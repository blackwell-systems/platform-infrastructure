"""
Decap CMS Tier Stack

Factory-powered CMS tier implementation for Decap CMS (formerly Netlify CMS).
Provides git-based content management with GitHub integration across multiple
SSG engine options (Hugo, Eleventy, Astro, Gatsby).

Key Features:
- FREE CMS with no monthly fees
- Git-based workflow with version control
- GitHub OAuth authentication
- Supports Hugo, Eleventy, Astro, and Gatsby
- Markdown editing with live preview
- Media management with git-lfs support

Target Market:
- Budget-conscious clients ($50-75/month total)
- Technical teams comfortable with git workflow
- Small to medium content volumes
- Clients wanting maximum control and zero vendor lock-in

Architecture:
- Static site generation with chosen SSG engine
- S3 + CloudFront for global distribution
- Decap CMS admin interface served statically
- GitHub webhooks for automated builds
- CodeBuild for SSG compilation and deployment
"""

from typing import Dict, Any, Optional
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.factories.ssg_stack_factory import SSGStackFactory
from shared.providers.cms.factory import CMSProviderFactory
from shared.providers.cms.integration_patterns import CMSIntegrationManager


class DecapCMSTierStack(BaseSSGStack):
    """
    Decap CMS Tier Stack Implementation

    Factory-powered implementation that combines:
    - Client's chosen SSG engine (Hugo, Eleventy, Astro, Gatsby)
    - Decap CMS for git-based content management
    - Automated build pipeline triggered by content changes
    - Global CloudFront distribution

    Pricing: $50-75/month (no CMS fees, only hosting costs)
    Setup: $960-2,640 depending on SSG engine complexity
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config,
        **kwargs
    ):
        super().__init__(scope, construct_id, client_config, **kwargs)

        # Validate Decap CMS configuration
        self._validate_decap_config()

        # Get SSG configuration from factory
        self.ssg_config = self._get_ssg_configuration()

        # Get CMS provider instance
        self.cms_provider = self._get_cms_provider()

        # Get CMS integration pattern
        self.cms_integration = self._get_cms_integration_pattern()

        # Create infrastructure
        self._create_decap_infrastructure()

    def _validate_decap_config(self) -> None:
        """Validate Decap CMS specific configuration"""
        if not self.client_config.has_cms():
            raise ValueError("Decap CMS tier requires cms_config to be specified")

        cms_config = self.client_config.cms_config
        if cms_config.cms.provider != "decap":
            raise ValueError(f"Expected Decap CMS provider, got {cms_config.cms.provider}")

        # Validate required Decap settings
        required_settings = ["repository", "repository_owner"]
        content_settings = cms_config.cms.content_settings

        for setting in required_settings:
            if not content_settings.get(setting):
                raise ValueError(f"Decap CMS requires '{setting}' in content_settings")

        # Validate SSG engine compatibility
        supported_engines = ["hugo", "eleventy", "astro", "gatsby"]
        if self.client_config.ssg_engine not in supported_engines:
            raise ValueError(
                f"SSG engine '{self.client_config.ssg_engine}' not supported for Decap CMS. "
                f"Supported engines: {supported_engines}"
            )

    def _get_ssg_configuration(self) -> Dict[str, Any]:
        """Get SSG configuration from factory"""
        return SSGStackFactory.get_stack_recommendation(
            ssg_engine=self.client_config.ssg_engine,
            cms_provider="decap",
            content_volume="medium",
            service_tier=self.client_config.service_tier
        )

    def _get_cms_provider(self):
        """Get configured Decap CMS provider instance"""
        return CMSProviderFactory.create_provider(
            "decap",
            self.client_config.cms_config.cms.get_provider_config()
        )

    def _get_cms_integration_pattern(self):
        """Get CMS integration pattern for Decap (git-based)"""
        integration_manager = CMSIntegrationManager({
            "client_config": self.client_config.to_dict(),
            "cms_config": self.client_config.cms_config.model_dump() if self.client_config.cms_config else {}
        })
        return integration_manager.get_integration_pattern()

    def _create_decap_infrastructure(self) -> None:
        """Create complete Decap CMS infrastructure"""

        # 1. Base SSG infrastructure (S3, CloudFront, etc.)
        self._create_base_ssg_infrastructure()

        # 2. Decap CMS admin interface
        self._create_decap_admin_interface()

        # 3. Build pipeline with GitHub webhook integration
        self._create_build_pipeline()

        # 4. GitHub webhook handler
        self._create_github_webhook_handler()

        # 5. CMS-specific environment variables
        self._add_cms_environment_variables()

    def _create_base_ssg_infrastructure(self) -> None:
        """Create base SSG infrastructure using factory configuration"""

        # Content bucket for static site
        self.content_bucket = s3.Bucket(
            self, "ContentBucket",
            bucket_name=f"{self.client_config.resource_prefix}-content",
            website_index_document="index.html",
            website_error_document="404.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # CloudFront distribution for global delivery
        self.distribution = cloudfront.CloudFrontWebDistribution(
            self, "ContentDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=self.content_bucket
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                            allowed_methods=cloudfront.CloudFrontAllowedMethods.GET_HEAD_OPTIONS,
                            cached_methods=cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD_OPTIONS,
                            compress=True,
                            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                            default_ttl=Duration.hours(24),
                            max_ttl=Duration.days(365)
                        )
                    ]
                )
            ],
            comment=f"Decap CMS distribution for {self.client_config.client_id}",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Cost optimization
            enabled=True
        )

    def _create_decap_admin_interface(self) -> None:
        """Create Decap CMS admin interface configuration"""

        # Get admin configuration from CMS provider
        admin_config = self.cms_provider.get_admin_config()

        # Store admin configuration for deployment
        self.admin_interface_config = {
            **admin_config,
            "cms_type": "git_based",
            "admin_path": "/admin",
            "backend": {
                "name": "github",
                "repo": f"{self.client_config.cms_config.cms.content_settings['repository_owner']}/{self.client_config.cms_config.cms.content_settings['repository']}",
                "branch": self.client_config.cms_config.cms.content_settings.get("branch", "main")
            },
            "media_folder": self.client_config.cms_config.cms.content_settings.get("media_path", "static/images"),
            "public_folder": "/images",
            "collections": self._get_decap_collections()
        }

    def _get_decap_collections(self) -> list:
        """Get Decap CMS collection configuration based on SSG engine"""

        # Base collections that work with all SSG engines
        base_collections = [
            {
                "name": "posts",
                "label": "Blog Posts",
                "folder": f"{self.client_config.cms_config.cms.content_settings.get('content_path', 'content')}/posts",
                "create": True,
                "slug": "{{year}}-{{month}}-{{day}}-{{slug}}",
                "fields": [
                    {"label": "Title", "name": "title", "widget": "string"},
                    {"label": "Date", "name": "date", "widget": "datetime"},
                    {"label": "Description", "name": "description", "widget": "text", "required": False},
                    {"label": "Featured Image", "name": "image", "widget": "image", "required": False},
                    {"label": "Tags", "name": "tags", "widget": "list", "required": False},
                    {"label": "Body", "name": "body", "widget": "markdown"}
                ]
            },
            {
                "name": "pages",
                "label": "Pages",
                "folder": f"{self.client_config.cms_config.cms.content_settings.get('content_path', 'content')}/pages",
                "create": True,
                "slug": "{{slug}}",
                "fields": [
                    {"label": "Title", "name": "title", "widget": "string"},
                    {"label": "Permalink", "name": "permalink", "widget": "string", "required": False},
                    {"label": "Description", "name": "description", "widget": "text", "required": False},
                    {"label": "Body", "name": "body", "widget": "markdown"}
                ]
            }
        ]

        # SSG-specific optimizations
        if self.client_config.ssg_engine == "hugo":
            # Hugo-specific front matter
            for collection in base_collections:
                collection["fields"].insert(1, {"label": "Draft", "name": "draft", "widget": "boolean", "default": False})

        elif self.client_config.ssg_engine == "gatsby":
            # Gatsby-specific fields for GraphQL optimization
            for collection in base_collections:
                if collection["name"] == "posts":
                    collection["fields"].extend([
                        {"label": "Category", "name": "category", "widget": "string", "required": False},
                        {"label": "Featured", "name": "featured", "widget": "boolean", "default": False}
                    ])

        return base_collections

    def _create_build_pipeline(self) -> None:
        """Create CodeBuild project for SSG compilation and deployment"""

        # Build role with necessary permissions
        build_role = iam.Role(
            self, "BuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
            ]
        )

        # Grant S3 permissions
        self.content_bucket.grant_read_write(build_role)

        # Grant CloudFront invalidation permissions
        build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["cloudfront:CreateInvalidation"],
                resources=[f"arn:aws:cloudfront::{self.account}:distribution/{self.distribution.distribution_id}"]
            )
        )

        # Get SSG-specific build commands
        build_commands = self._get_ssg_build_commands()

        # CodeBuild project
        self.build_project = codebuild.Project(
            self, "SSGBuildProject",
            project_name=f"{self.client_config.resource_prefix}-decap-build",
            role=build_role,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables=self._get_build_environment_variables()
            ),
            source=codebuild.Source.git_hub(
                owner=self.client_config.cms_config.cms.content_settings["repository_owner"],
                repo=self.client_config.cms_config.cms.content_settings["repository"],
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(
                        codebuild.EventAction.PUSH
                    ).and_branch_is(
                        self.client_config.cms_config.cms.content_settings.get("branch", "main")
                    )
                ]
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "nodejs": "18"
                        },
                        "commands": build_commands["install"]
                    },
                    "pre_build": {
                        "commands": build_commands["pre_build"]
                    },
                    "build": {
                        "commands": build_commands["build"]
                    },
                    "post_build": {
                        "commands": build_commands["post_build"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": build_commands["output_dir"]
                }
            })
        )

    def _get_ssg_build_commands(self) -> Dict[str, Any]:
        """Get SSG-specific build commands based on engine"""

        ssg_engine = self.client_config.ssg_engine

        if ssg_engine == "hugo":
            return {
                "install": [
                    "apt-get update",
                    "apt-get install -y wget",
                    "wget https://github.com/gohugoio/hugo/releases/download/v0.120.4/hugo_extended_0.120.4_linux-amd64.deb",
                    "dpkg -i hugo_extended_0.120.4_linux-amd64.deb"
                ],
                "pre_build": [
                    "echo Hugo version:",
                    "hugo version"
                ],
                "build": [
                    "hugo --minify --gc"
                ],
                "post_build": [
                    f"aws s3 sync public/ s3://{self.content_bucket.bucket_name} --delete",
                    f"aws cloudfront create-invalidation --distribution-id {self.distribution.distribution_id} --paths '/*'"
                ],
                "output_dir": "public"
            }

        elif ssg_engine == "eleventy":
            return {
                "install": [
                    "npm install -g @11ty/eleventy"
                ],
                "pre_build": [
                    "npm install"
                ],
                "build": [
                    "npx @11ty/eleventy"
                ],
                "post_build": [
                    f"aws s3 sync _site/ s3://{self.content_bucket.bucket_name} --delete",
                    f"aws cloudfront create-invalidation --distribution-id {self.distribution.distribution_id} --paths '/*'"
                ],
                "output_dir": "_site"
            }

        elif ssg_engine == "astro":
            return {
                "install": [],
                "pre_build": [
                    "npm install"
                ],
                "build": [
                    "npm run build"
                ],
                "post_build": [
                    f"aws s3 sync dist/ s3://{self.content_bucket.bucket_name} --delete",
                    f"aws cloudfront create-invalidation --distribution-id {self.distribution.distribution_id} --paths '/*'"
                ],
                "output_dir": "dist"
            }

        elif ssg_engine == "gatsby":
            return {
                "install": [],
                "pre_build": [
                    "npm install"
                ],
                "build": [
                    "npm run build"
                ],
                "post_build": [
                    f"aws s3 sync public/ s3://{self.content_bucket.bucket_name} --delete",
                    f"aws cloudfront create-invalidation --distribution-id {self.distribution.distribution_id} --paths '/*'"
                ],
                "output_dir": "public"
            }

        else:
            raise ValueError(f"Unsupported SSG engine for Decap CMS: {ssg_engine}")

    def _get_build_environment_variables(self) -> Dict[str, codebuild.BuildEnvironmentVariable]:
        """Get build environment variables"""

        # Get CMS environment variables
        cms_env_vars = self.cms_provider.get_environment_variables()

        # Convert to CodeBuild format
        build_env_vars = {}
        for key, value in cms_env_vars.items():
            build_env_vars[key] = codebuild.BuildEnvironmentVariable(value=value)

        # Add stack-specific variables
        build_env_vars.update({
            "BUCKET_NAME": codebuild.BuildEnvironmentVariable(value=self.content_bucket.bucket_name),
            "DISTRIBUTION_ID": codebuild.BuildEnvironmentVariable(value=self.distribution.distribution_id),
            "SSG_ENGINE": codebuild.BuildEnvironmentVariable(value=self.client_config.ssg_engine),
            "CMS_PROVIDER": codebuild.BuildEnvironmentVariable(value="decap")
        })

        return build_env_vars

    def _create_github_webhook_handler(self) -> None:
        """Create GitHub webhook handler for manual build triggers"""

        # Lambda function to handle GitHub webhooks
        webhook_handler = lambda_.Function(
            self, "GitHubWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline(f"""
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

codebuild = boto3.client('codebuild')

def handler(event, context):
    try:
        # Parse GitHub webhook payload
        if event.get('httpMethod') == 'POST':
            payload = json.loads(event['body'])

            # Check if this is a push to the main branch
            ref = payload.get('ref', '')
            target_branch = 'refs/heads/{self.client_config.cms_config.cms.content_settings.get("branch", "main")}'

            if ref == target_branch:
                logger.info(f"Triggering build for push to {{ref}}")

                # Start CodeBuild project
                response = codebuild.start_build(
                    projectName='{self.build_project.project_name}'
                )

                return {{
                    'statusCode': 200,
                    'body': json.dumps({{
                        'message': 'Build triggered successfully',
                        'buildId': response['build']['id']
                    }})
                }}
            else:
                logger.info(f"Ignoring push to {{ref}} (not target branch)")
                return {{
                    'statusCode': 200,
                    'body': json.dumps({{'message': 'Branch ignored'}})
                }}

        return {{
            'statusCode': 400,
            'body': json.dumps({{'message': 'Invalid request'}})
        }}

    except Exception as e:
        logger.error(f"Error processing webhook: {{str(e)}}")
        return {{
            'statusCode': 500,
            'body': json.dumps({{'message': 'Internal server error'}})
        }}
            """),
            environment={
                "BUILD_PROJECT_NAME": self.build_project.project_name
            }
        )

        # Grant Lambda permission to start builds
        webhook_handler.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codebuild:StartBuild"],
                resources=[self.build_project.project_arn]
            )
        )

        # API Gateway for webhook endpoint
        webhook_api = apigateway.RestApi(
            self, "WebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-decap-webhook",
            description="GitHub webhook handler for Decap CMS builds"
        )

        webhook_integration = apigateway.LambdaIntegration(webhook_handler)
        webhook_api.root.add_method("POST", webhook_integration)

        # Store webhook URL for GitHub configuration
        self.webhook_url = webhook_api.url

    def _add_cms_environment_variables(self) -> None:
        """Add CMS-specific environment variables to outputs"""

        cms_env_vars = self.cms_provider.get_environment_variables()

        for key, value in cms_env_vars.items():
            CfnOutput(
                self, f"EnvVar{key}",
                value=value,
                description=f"Environment variable {key} for CMS integration"
            )

    def _create_stack_outputs(self) -> None:
        """Create CloudFormation outputs for client reference"""

        # Website URL
        CfnOutput(
            self, "WebsiteURL",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="Website URL"
        )

        # Admin URL
        CfnOutput(
            self, "AdminURL",
            value=f"https://{self.distribution.distribution_domain_name}/admin",
            description="Decap CMS Admin Interface URL"
        )

        # Webhook URL for GitHub configuration
        CfnOutput(
            self, "WebhookURL",
            value=self.webhook_url,
            description="GitHub webhook URL for automated builds"
        )

        # Repository information
        CfnOutput(
            self, "Repository",
            value=f"https://github.com/{self.client_config.cms_config.cms.content_settings['repository_owner']}/{self.client_config.cms_config.cms.content_settings['repository']}",
            description="GitHub repository for content management"
        )

        # SSG engine information
        CfnOutput(
            self, "SSGEngine",
            value=self.client_config.ssg_engine,
            description="Static Site Generator engine used"
        )

        # Cost information
        estimated_monthly_cost = self.cms_provider.estimate_monthly_cost("medium")
        CfnOutput(
            self, "EstimatedMonthlyCost",
            value=f"${estimated_monthly_cost['total_estimated']:.2f}",
            description="Estimated monthly cost (CMS + hosting)"
        )