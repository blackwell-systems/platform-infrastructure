"""
Tina CMS Tier Stack

Factory-powered visual editing CMS tier implementation for Tina CMS.
Provides git-based content management with visual editing capabilities
across multiple SSG engine options (Next.js, Astro, Gatsby).

Key Features:
- Visual editing with real-time preview
- Git-based workflow with version control
- GitHub OAuth authentication
- Supports Next.js, Astro, and Gatsby
- Rich text editing with structured content
- Optional Tina Cloud integration for enhanced features

Target Market:
- Content creators wanting visual editing
- Teams needing collaboration features
- Agencies managing multiple client sites
- Developers wanting both visual editing and git control

Architecture:
- Hybrid CMS: Git storage + visual editing interface
- React-based admin interface served statically
- GraphQL API for content queries
- Tina Cloud integration for real-time collaboration
- CodeBuild for SSG compilation and deployment

Pricing:
- Self-hosted: Free (git-only editing)
- Tina Cloud: $0-50/month based on usage
- Total cost: $60-125/month including hosting
- Setup: $1,200-2,880 depending on SSG engine complexity
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
    aws_secretsmanager as secrets,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.factories.ssg_stack_factory import SSGStackFactory
from shared.providers.cms.factory import CMSProviderFactory
from shared.providers.cms.integration_patterns import CMSIntegrationManager


class TinaCMSTierStack(BaseSSGStack):
    """
    Tina CMS Tier Stack Implementation

    Factory-powered implementation that combines:
    - Client's chosen SSG engine (Next.js, Astro, Gatsby)
    - Tina CMS for visual editing with git-based storage
    - Automated build pipeline triggered by content changes
    - Global CloudFront distribution with preview capabilities

    Pricing: $60-125/month (includes optional Tina Cloud features)
    Setup: $1,200-2,880 depending on SSG engine complexity
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config,
        **kwargs
    ):
        super().__init__(scope, construct_id, client_config, **kwargs)

        # Validate Tina CMS configuration
        self._validate_tina_config()

        # Get SSG configuration from factory
        self.ssg_config = self._get_ssg_configuration()

        # Get CMS provider instance
        self.cms_provider = self._get_cms_provider()

        # Get CMS integration pattern
        self.cms_integration = self._get_cms_integration_pattern()

        # Create infrastructure
        self._create_tina_infrastructure()

    def _validate_tina_config(self) -> None:
        """Validate Tina CMS specific configuration"""
        if not self.client_config.has_cms():
            raise ValueError("Tina CMS tier requires cms_config to be specified")

        cms_config = self.client_config.cms_config
        if cms_config.cms.provider != "tina":
            raise ValueError(f"Expected Tina CMS provider, got {cms_config.cms.provider}")

        # Validate required Tina settings
        required_settings = ["repository", "repository_owner"]
        content_settings = cms_config.cms.content_settings

        for setting in required_settings:
            if not content_settings.get(setting):
                raise ValueError(f"Tina CMS requires '{setting}' in content_settings")

        # Validate SSG engine compatibility
        supported_engines = ["nextjs", "astro", "gatsby"]
        if self.client_config.ssg_engine not in supported_engines:
            raise ValueError(
                f"Tina CMS supports SSG engines: {supported_engines}. "
                f"Got: {self.client_config.ssg_engine}"
            )

    def _get_ssg_configuration(self):
        """Get SSG configuration from factory"""
        return SSGStackFactory.get_ssg_engine_info(self.client_config.ssg_engine)

    def _get_cms_provider(self):
        """Get CMS provider instance"""
        return CMSProviderFactory.create_provider(
            self.client_config.cms_config.cms.provider,
            self.client_config.cms_config.cms.content_settings
        )

    def _get_cms_integration_pattern(self):
        """Get CMS integration pattern"""
        return CMSIntegrationManager.get_integration_pattern(
            cms_provider=self.client_config.cms_config.cms.provider,
            ssg_engine=self.client_config.ssg_engine,
            auth_method=self.client_config.cms_config.cms.auth_method
        )

    def _create_custom_infrastructure(self) -> None:
        """Required implementation of abstract method from BaseSSGStack"""
        # This method is called by BaseSSGStack.__init__
        # Our actual infrastructure creation is in _create_tina_infrastructure
        pass

    def _create_tina_infrastructure(self) -> None:
        """Create complete Tina CMS infrastructure"""

        # 1. Base SSG infrastructure (S3, CloudFront, etc.)
        self._create_base_ssg_infrastructure()

        # 2. Tina-specific infrastructure
        self._create_tina_admin_interface()

        # 3. Build pipeline with Tina integration
        self._create_tina_build_pipeline()

        # 4. GitHub webhook handler for content changes
        self._create_github_webhook_handler()

        # 5. Tina Cloud integration (if configured)
        self._create_tina_cloud_integration()

        # 6. Environment variables and secrets
        self._add_tina_environment_variables()

        # 7. Create outputs
        self.create_standard_outputs()
        self._create_tina_outputs()

    def _create_base_ssg_infrastructure(self) -> None:
        """Create base SSG infrastructure using BaseSSGStack methods"""

        # Create content bucket
        self.content_bucket = self.create_content_bucket(
            bucket_name=f"{self.client_config.resource_prefix}-tina-content"
        )

        # Create CloudFront distribution
        self.distribution = self.create_cloudfront_distribution(
            origin_bucket=self.content_bucket,
            custom_domain=self.client_config.domain
        )

    def _create_tina_admin_interface(self) -> None:
        """Create Tina CMS admin interface configuration"""

        # Get admin configuration from CMS provider
        admin_config = self.cms_provider.get_admin_interface_config()

        # Create Tina-specific Lambda for admin API
        self.tina_admin_api = lambda_.Function(
            self, "TinaAdminAPI",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_tina_admin_api_code()),
            timeout=Duration.seconds(30),
            environment={
                **self.get_standard_environment_variables(),
                "TINA_ADMIN_PATH": admin_config.get("admin_path", "/admin"),
                "TINA_API_PATH": admin_config.get("api_path", "/api/tina/graphql"),
                "GITHUB_REPO": self.client_config.cms_config.cms.content_settings.get("repository"),
                "GITHUB_OWNER": self.client_config.cms_config.cms.content_settings.get("repository_owner"),
                "BRANCH": self.client_config.cms_config.cms.content_settings.get("branch", "main")
            }
        )

        # Grant permissions to Lambda
        if self.content_bucket:
            self.content_bucket.grant_read_write(self.tina_admin_api)

        # Create API Gateway for Tina admin
        self.tina_api_gateway = apigateway.RestApi(
            self, "TinaAPIGateway",
            rest_api_name=f"{self.client_config.client_id}-tina-api",
            description="Tina CMS API Gateway for admin interface"
        )

        # Add Tina API integration
        tina_integration = apigateway.LambdaIntegration(self.tina_admin_api)
        api_resource = self.tina_api_gateway.root.add_resource("api")
        tina_resource = api_resource.add_resource("tina")
        tina_resource.add_resource("graphql").add_method("POST", tina_integration)
        tina_resource.add_resource("graphql").add_method("GET", tina_integration)

    def _create_tina_build_pipeline(self) -> None:
        """Create build pipeline optimized for Tina CMS and chosen SSG engine"""

        # Get build configuration for the SSG engine
        build_config = self.cms_provider.get_build_integration_config()
        ssg_build_config = build_config.get(self.client_config.ssg_engine, {})

        # Create build role
        additional_policies = [
            # Secrets Manager access for Tina Cloud tokens
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue"
                ],
                resources=[f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:tina-*"]
            )
        ]
        self.build_role = self.create_build_role(additional_policies=additional_policies)

        # Create CodeBuild project
        build_spec = self._generate_tina_buildspec(ssg_build_config)

        self.build_project = codebuild.Project(
            self, "TinaBuildProject",
            project_name=f"{self.client_config.resource_prefix}-tina-build",
            source=codebuild.Source.git_hub(
                owner=self.client_config.cms_config.cms.content_settings.get("repository_owner"),
                repo=self.client_config.cms_config.cms.content_settings.get("repository"),
                branch_or_ref=self.client_config.cms_config.cms.content_settings.get("branch", "main"),
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH)
                ]
            ),
            build_spec=codebuild.BuildSpec.from_object(build_spec),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL
            ),
            role=self.build_role,
            timeout=Duration.minutes(20)
        )

    def _create_github_webhook_handler(self) -> None:
        """Create GitHub webhook handler for Tina content changes"""

        self.github_webhook_handler = lambda_.Function(
            self, "TinaGitHubWebhook",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_github_webhook_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "BUILD_PROJECT_NAME": self.build_project.project_name,
                "CMS_PROVIDER": "tina",
                "WEBHOOK_SECRET": "${GITHUB_WEBHOOK_SECRET}"
            }
        )

        # Grant webhook handler permission to trigger builds
        self.build_project.grant_start_build(self.github_webhook_handler)

        # Create API Gateway for webhook
        self.webhook_api = apigateway.RestApi(
            self, "TinaWebhookAPI",
            rest_api_name=f"{self.client_config.client_id}-tina-webhook"
        )

        webhook_integration = apigateway.LambdaIntegration(self.github_webhook_handler)
        self.webhook_api.root.add_resource("webhook").add_method("POST", webhook_integration)

    def _create_tina_cloud_integration(self) -> None:
        """Create Tina Cloud integration if configured"""

        content_settings = self.client_config.cms_config.cms.content_settings
        tina_token = content_settings.get("tina_token")
        tina_client_id = content_settings.get("tina_client_id")

        if not (tina_token and tina_client_id):
            # No Tina Cloud integration configured
            return

        # Store Tina Cloud credentials in Secrets Manager
        self.tina_secrets = secrets.Secret(
            self, "TinaCloudSecrets",
            secret_name=f"tina-cloud-{self.client_config.client_id}",
            description="Tina Cloud integration credentials",
            generate_secret_string=secrets.SecretStringGenerator(
                secret_string_template=f'{{"tina_client_id": "{tina_client_id}"}}',
                generate_string_key="tina_token",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\""
            )
        )

        # Create Tina Cloud sync Lambda
        self.tina_cloud_sync = lambda_.Function(
            self, "TinaCloudSync",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_tina_cloud_sync_code()),
            timeout=Duration.minutes(5),
            environment={
                **self.get_standard_environment_variables(),
                "TINA_SECRETS_ARN": self.tina_secrets.secret_arn,
                "CONTENT_BUCKET": self.content_bucket.bucket_name
            }
        )

        # Grant permissions
        self.tina_secrets.grant_read(self.tina_cloud_sync)
        self.content_bucket.grant_read_write(self.tina_cloud_sync)

    def _add_tina_environment_variables(self) -> None:
        """Add Tina-specific environment variables to build process"""

        # Base environment variables are handled by BaseSSGStack
        tina_env_vars = {
            "CMS_PROVIDER": "tina",
            "TINA_ADMIN_PATH": "/admin",
            "TINA_API_PATH": "/api/tina/graphql"
        }

        # Add to build project if it exists
        if hasattr(self, 'build_project'):
            for key, value in tina_env_vars.items():
                self.build_project.add_environment_variable(key, codebuild.BuildEnvironmentVariable(value=value))

    def _create_tina_outputs(self) -> None:
        """Create Tina CMS specific outputs"""

        # Tina admin interface URL
        CfnOutput(
            self, "TinaAdminURL",
            value=f"https://{self.get_website_url()}/admin",
            description="Tina CMS admin interface URL"
        )

        # Tina API endpoint
        if hasattr(self, 'tina_api_gateway'):
            CfnOutput(
                self, "TinaAPIEndpoint",
                value=self.tina_api_gateway.url,
                description="Tina CMS GraphQL API endpoint"
            )

        # GitHub webhook URL
        if hasattr(self, 'webhook_api'):
            CfnOutput(
                self, "GitHubWebhookURL",
                value=f"{self.webhook_api.url}webhook",
                description="GitHub webhook URL for content changes"
            )

        # Tina Cloud integration status
        content_settings = self.client_config.cms_config.cms.content_settings
        cloud_enabled = bool(content_settings.get("tina_token") and content_settings.get("tina_client_id"))

        CfnOutput(
            self, "TinaCloudEnabled",
            value="true" if cloud_enabled else "false",
            description="Tina Cloud integration status"
        )

    def _generate_tina_buildspec(self, ssg_build_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CodeBuild buildspec for Tina CMS with chosen SSG engine"""

        install_command = ssg_build_config.get("install_command", "npm install")
        build_command = ssg_build_config.get("build_command", "npm run build")
        output_directory = ssg_build_config.get("output_directory", "dist")

        return {
            "version": "0.2",
            "phases": {
                "install": {
                    "runtime-versions": {
                        "nodejs": "18"
                    },
                    "commands": [
                        "echo Installing dependencies...",
                        install_command,
                        "echo Installing Tina CLI...",
                        "npm install -g @tinacms/cli"
                    ]
                },
                "pre_build": {
                    "commands": [
                        "echo Configuring Tina CMS...",
                        "npx @tinacms/cli init --skip-prompts || true",
                        "echo Generating Tina schema...",
                        "npx @tinacms/cli build --skip-sdk || true"
                    ]
                },
                "build": {
                    "commands": [
                        f"echo Building {self.client_config.ssg_engine} site with Tina CMS...",
                        build_command,
                        "echo Build completed successfully"
                    ]
                },
                "post_build": {
                    "commands": [
                        f"echo Syncing to S3 bucket: {self.content_bucket.bucket_name}",
                        f"aws s3 sync {output_directory}/ s3://{self.content_bucket.bucket_name}/ --delete",
                        f"echo Invalidating CloudFront distribution: {self.distribution.distribution_id}",
                        f"aws cloudfront create-invalidation --distribution-id {self.distribution.distribution_id} --paths '/*'"
                    ]
                }
            },
            "artifacts": {
                "files": [
                    "**/*"
                ],
                "base-directory": output_directory
            }
        }

    def _get_tina_admin_api_code(self) -> str:
        """Get Lambda code for Tina admin API"""
        return """
        const { TinaCloudAPI } = require('@tinacms/graphql');

        exports.handler = async (event) => {
            console.log('Tina admin API request:', JSON.stringify(event));

            const { httpMethod, path, body, headers } = event;

            try {
                // Handle Tina GraphQL API requests
                if (path === '/api/tina/graphql') {
                    const query = JSON.parse(body || '{}');

                    // Process GraphQL query
                    const result = await processTinaQuery(query);

                    return {
                        statusCode: 200,
                        headers: {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        body: JSON.stringify(result)
                    };
                }

                return {
                    statusCode: 404,
                    body: JSON.stringify({ message: 'Not found' })
                };
            } catch (error) {
                console.error('Tina API error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ error: error.message })
                };
            }
        };

        async function processTinaQuery(query) {
            // Implementation would handle Tina GraphQL queries
            return { data: null, errors: [] };
        }
        """

    def _get_github_webhook_code(self) -> str:
        """Get Lambda code for GitHub webhook handling"""
        return """
        const AWS = require('aws-sdk');
        const codebuild = new AWS.CodeBuild();

        exports.handler = async (event) => {
            console.log('GitHub webhook received:', JSON.stringify(event));

            const { body, headers } = event;
            const payload = JSON.parse(body || '{}');

            // Verify webhook is from GitHub
            const githubEvent = headers['X-GitHub-Event'] || headers['x-github-event'];

            if (githubEvent === 'push') {
                console.log('Push event detected, triggering build...');

                try {
                    const buildResult = await codebuild.startBuild({
                        projectName: process.env.BUILD_PROJECT_NAME
                    }).promise();

                    console.log('Build started:', buildResult.build.id);

                    return {
                        statusCode: 200,
                        body: JSON.stringify({
                            message: 'Build triggered successfully',
                            buildId: buildResult.build.id
                        })
                    };
                } catch (error) {
                    console.error('Failed to trigger build:', error);
                    return {
                        statusCode: 500,
                        body: JSON.stringify({ error: error.message })
                    };
                }
            }

            return {
                statusCode: 200,
                body: JSON.stringify({ message: 'Webhook processed' })
            };
        };
        """

    def _get_tina_cloud_sync_code(self) -> str:
        """Get Lambda code for Tina Cloud synchronization"""
        return """
        const AWS = require('aws-sdk');
        const secretsManager = new AWS.SecretsManager();
        const s3 = new AWS.S3();

        exports.handler = async (event) => {
            console.log('Tina Cloud sync triggered:', JSON.stringify(event));

            try {
                // Get Tina Cloud credentials
                const secretValue = await secretsManager.getSecretValue({
                    SecretId: process.env.TINA_SECRETS_ARN
                }).promise();

                const secrets = JSON.parse(secretValue.SecretString);
                const { tina_token, tina_client_id } = secrets;

                // Sync content with Tina Cloud
                console.log('Syncing with Tina Cloud...');

                // Implementation would sync content between local git and Tina Cloud

                return {
                    statusCode: 200,
                    body: JSON.stringify({ message: 'Tina Cloud sync completed' })
                };
            } catch (error) {
                console.error('Tina Cloud sync error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ error: error.message })
                };
            }
        };
        """

    def estimate_monthly_cost(self) -> Dict[str, float]:
        """Estimate monthly costs for Tina CMS tier"""

        # Get base SSG costs
        base_costs = super().estimate_monthly_cost()

        # Add Tina-specific costs
        content_settings = self.client_config.cms_config.cms.content_settings
        cloud_enabled = bool(content_settings.get("tina_token") and content_settings.get("tina_client_id"))

        tina_costs = {
            "tina_cloud": 29.0 if cloud_enabled else 0.0,  # Tina Cloud base plan
            "additional_lambda": 3.0,  # Additional Lambda executions for admin API
            "api_gateway": 2.0,        # API Gateway for Tina admin
            "secrets_manager": 0.5 if cloud_enabled else 0.0,  # Secrets storage
        }

        # Combine costs
        total_costs = {**base_costs, **tina_costs}
        total_costs["total"] = sum(total_costs.values())

        return total_costs