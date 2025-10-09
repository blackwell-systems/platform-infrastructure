"""
Decap CMS Dual-Mode Tier Stack

Updated Decap CMS implementation with dual-mode integration support:
- Direct Mode: Traditional git webhook → build pipeline (simple, familiar)
- Event-Driven Mode: Git events → SNS → unified content system (composition-ready)

Decap CMS (formerly Netlify CMS) Features:
- FREE CMS with no monthly fees - perfect for budget-conscious clients
- Git-based workflow with full version control
- GitHub OAuth authentication
- Supports Hugo, Eleventy, Astro, and Gatsby
- Markdown editing with live preview
- Zero vendor lock-in

Target Market:
- Budget-conscious clients ($50-75/month total)
- Technical teams comfortable with git workflow
- Clients wanting maximum control and zero vendor lock-in
- Small to medium content volumes (direct mode)
- Growing businesses planning composition (event-driven mode)
"""

from typing import Dict, Any, Optional, List
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
from models.service_config import ClientServiceConfig, IntegrationMode
from shared.composition.integration_layer import EventDrivenIntegrationLayer
from shared.providers.cms.factory import CMSProviderFactory


class DecapCMSTierStack(BaseSSGStack):
    """
    Decap CMS Tier Stack Implementation

    Supports both integration modes:
    - Direct: Git webhook → CodeBuild → S3/CloudFront (simple, familiar)
    - Event-Driven: Git events → SNS → unified content system (composition-ready)

    The FREE CMS option that works for both simple sites and complex compositions.
    """

    # Supported SSG engines for Decap CMS
    SUPPORTED_SSG_ENGINES = {
        "hugo": {
            "compatibility": "excellent",
            "setup_complexity": "easy",
            "features": ["fast_builds", "markdown_native", "powerful_templating"]
        },
        "eleventy": {
            "compatibility": "excellent",
            "setup_complexity": "easy",
            "features": ["flexible_templating", "fast_builds", "javascript_config"]
        },
        "astro": {
            "compatibility": "good",
            "setup_complexity": "intermediate",
            "features": ["component_islands", "modern_tooling", "partial_hydration"]
        },
        "gatsby": {
            "compatibility": "good",
            "setup_complexity": "advanced",
            "features": ["react_based", "graphql", "plugin_ecosystem"]
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientServiceConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, client_config, **kwargs)

        # Validate Decap CMS configuration
        self._validate_decap_cms_config()

        # Initialize providers and integration
        self.cms_provider = self._initialize_cms_provider()
        self.integration_mode = client_config.service_integration.integration_mode

        # Create infrastructure based on integration mode
        if self.integration_mode == IntegrationMode.DIRECT:
            self._create_direct_mode_infrastructure()
        else:
            self.integration_layer = EventDrivenIntegrationLayer(
                self, "IntegrationLayer", client_config
            )
            self._create_event_driven_infrastructure()

        # Create common infrastructure (both modes need these)
        self._create_common_infrastructure()

        # Output stack information
        self._create_stack_outputs()

    def _validate_decap_cms_config(self) -> None:
        """Validate Decap CMS configuration"""
        service_config = self.client_config.service_integration

        if not service_config.cms_config:
            raise ValueError("Decap CMS tier requires cms_config")

        if service_config.cms_config.provider != "decap":
            raise ValueError(f"Expected Decap CMS provider, got {service_config.cms_config.provider}")

        # Validate Decap-specific settings
        settings = service_config.cms_config.settings
        required = ["repository", "repository_owner"]
        for setting in required:
            if not settings.get(setting):
                raise ValueError(f"Decap CMS requires '{setting}' in settings")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"Decap CMS supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_cms_provider(self):
        """Initialize CMS provider instance"""
        cms_config = self.client_config.service_integration.cms_config
        return CMSProviderFactory.create_provider(
            cms_config.provider,
            cms_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Traditional Git webhook → CodeBuild pipeline
        self.github_webhook_handler = self._create_github_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # Decap CMS admin interface
        self._create_decap_admin_interface()

        # GitHub webhook integration
        self._create_github_webhook_integration()

        print(f"✅ Created Decap CMS direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Git events → Integration Layer → Unified Content
        self._create_event_driven_cms_integration()

        # Decap CMS admin interface (same as direct mode)
        self._create_decap_admin_interface()

        # Connect to event system
        self._connect_decap_to_event_system()

        print(f"✅ Created Decap CMS event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Create base SSG infrastructure (S3, CloudFront, etc.)
        bucket_name = f"{self.client_config.resource_prefix}-content"
        self.content_bucket = self.create_content_bucket(bucket_name)
        self.distribution = self.create_cloudfront_distribution(self.content_bucket)

        # Both modes need these components:
        self._create_content_storage()
        self._create_monitoring_and_logging()

        # Common outputs are handled in _create_stack_outputs()

    def _create_github_webhook_handler(self) -> lambda_.Function:
        """Create GitHub webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "GitHubWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="github_webhook.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import hmac
import hashlib
import os

def main(event, context):
    '''Handle GitHub webhook for Decap CMS in direct mode'''

    try:
        # Verify webhook signature
        signature = event['headers'].get('X-Hub-Signature-256', '')
        body = event['body']

        if not verify_signature(body, signature):
            return {'statusCode': 401, 'body': 'Unauthorized'}

        # Parse webhook payload
        payload = json.loads(body)

        # Only trigger build on push to main branch
        if payload.get('ref') == 'refs/heads/main':
            codebuild = boto3.client('codebuild')

            response = codebuild.start_build(
                projectName=os.environ['BUILD_PROJECT_NAME'],
                environmentVariablesOverride=[
                    {
                        'name': 'COMMIT_SHA',
                        'value': payload['head_commit']['id']
                    },
                    {
                        'name': 'COMMIT_MESSAGE',
                        'value': payload['head_commit']['message']
                    }
                ]
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Build triggered',
                    'buildId': response['build']['id']
                })
            }

        return {'statusCode': 200, 'body': 'No action needed'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def verify_signature(body, signature):
    '''Verify GitHub webhook signature'''
    secret = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
    if not secret:
        return True  # Skip verification if no secret set

    expected = 'sha256=' + hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-decap-build",
                "GITHUB_WEBHOOK_SECRET": "placeholder"  # Should use Secrets Manager
            },
            timeout=Duration.seconds(30)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        return codebuild.Project(
            self,
            "DecapDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-decap-build",
            source=codebuild.Source.git_hub(
                owner=self.client_config.service_integration.cms_config.settings["repository_owner"],
                repo=self.client_config.service_integration.cms_config.settings["repository"],
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH)
                ]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_cms_integration(self) -> None:
        """Create event-driven CMS integration"""

        # Git Event Processor - transforms Git events to unified content events
        self.git_event_processor = lambda_.Function(
            self,
            "GitEventProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="git_event_processor.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import os
import uuid
from datetime import datetime, timezone

def main(event, context):
    '''Process Git events and publish to unified content system'''

    sns = boto3.client('sns')

    try:
        # Parse GitHub webhook
        github_event = json.loads(event['body'])

        # Only process pushes to main branch
        if github_event.get('ref') != 'refs/heads/main':
            return {'statusCode': 200, 'body': 'Branch ignored'}

        # Extract content changes from commits
        commits = github_event.get('commits', [])

        for commit in commits:
            # Look for content file changes (markdown files)
            added_files = [f for f in commit.get('added', []) if f.endswith('.md')]
            modified_files = [f for f in commit.get('modified', []) if f.endswith('.md')]
            removed_files = [f for f in commit.get('removed', []) if f.endswith('.md')]

            # Process content changes
            for file_path in added_files + modified_files:
                unified_event = {
                    'event_type': 'content_updated',
                    'provider': 'decap',
                    'content_id': file_path.replace('.md', '').replace('/', '-'),
                    'content_type': determine_content_type(file_path),
                    'timestamp': commit['timestamp'],
                    'data': {
                        'file_path': file_path,
                        'commit_sha': commit['id'],
                        'commit_message': commit['message'],
                        'author': commit['author']['name'],
                        'action': 'added' if file_path in added_files else 'modified'
                    }
                }

                # Publish to content events topic
                sns.publish(
                    TopicArn=os.environ['CONTENT_EVENTS_TOPIC_ARN'],
                    Message=json.dumps(unified_event),
                    Subject=f"Decap Content Updated: {unified_event['content_id']}"
                )

            # Process deletions
            for file_path in removed_files:
                unified_event = {
                    'event_type': 'content_deleted',
                    'provider': 'decap',
                    'content_id': file_path.replace('.md', '').replace('/', '-'),
                    'content_type': determine_content_type(file_path),
                    'timestamp': commit['timestamp'],
                    'data': {
                        'file_path': file_path,
                        'commit_sha': commit['id'],
                        'commit_message': commit['message'],
                        'author': commit['author']['name'],
                        'action': 'deleted'
                    }
                }

                sns.publish(
                    TopicArn=os.environ['CONTENT_EVENTS_TOPIC_ARN'],
                    Message=json.dumps(unified_event),
                    Subject=f"Decap Content Deleted: {unified_event['content_id']}"
                )

        return {'statusCode': 200, 'body': f'Processed {len(commits)} commits'}

    except Exception as e:
        print(f"Error processing Git event: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def determine_content_type(file_path):
    '''Determine content type from file path'''
    if 'posts' in file_path or 'blog' in file_path:
        return 'article'
    elif 'pages' in file_path:
        return 'page'
    elif 'products' in file_path:
        return 'product'
    else:
        return 'page'  # Default
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn
            },
            timeout=Duration.seconds(30)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.git_event_processor)

    def _create_decap_admin_interface(self) -> None:
        """Create Decap CMS admin interface (same for both modes)"""

        # Create admin config for Decap CMS
        admin_config = self._generate_decap_admin_config()

        # Store admin config in S3 for serving via CloudFront
        # This would typically be done during deployment
        # The admin interface is served at /admin/ path

        pass  # Implementation would create S3 objects for admin interface

    def _create_github_webhook_integration(self) -> None:
        """Create GitHub webhook integration for direct mode"""

        # Create API Gateway for GitHub webhooks
        webhook_api = apigateway.RestApi(
            self,
            "GitHubWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-github-webhooks",
            description="GitHub webhook endpoint for Decap CMS"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.github_webhook_handler)
        )

    def _connect_decap_to_event_system(self) -> None:
        """Connect Decap CMS to event system for event-driven mode"""

        # Create API Gateway for GitHub webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "DecapEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-decap-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        decap_resource = event_resource.add_resource("decap")

        decap_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.git_event_processor)
        )

        # Output webhook URL for GitHub configuration
        CfnOutput(
            self,
            "DecapWebhookUrl",
            value=f"{webhook_api.url}events/decap",
            description="Webhook URL to configure in GitHub repository"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # Additional Decap-specific storage could be added here
        pass

    def _create_monitoring_and_logging(self) -> None:
        """Create monitoring and logging (both modes)"""
        # CloudWatch dashboards and alarms
        # Implementation would create monitoring resources
        pass

    def _generate_decap_admin_config(self) -> Dict[str, Any]:
        """Generate Decap CMS admin configuration"""

        cms_settings = self.client_config.service_integration.cms_config.settings
        ssg_engine = self.client_config.service_integration.ssg_engine

        # Base configuration for Decap CMS
        config = {
            "backend": {
                "name": "github",
                "repo": f"{cms_settings['repository_owner']}/{cms_settings['repository']}",
                "branch": cms_settings.get("branch", "main"),
                "auth_endpoint": "api/auth"
            },
            "media_folder": cms_settings.get("media_path", "static/images"),
            "public_folder": "/images",
            "collections": self._get_content_collections_config()
        }

        return config

    def _get_content_collections_config(self) -> List[Dict[str, Any]]:
        """Get content collections configuration for Decap CMS"""

        ssg_engine = self.client_config.service_integration.ssg_engine

        # Base collections that work with all SSG engines
        collections = [
            {
                "name": "posts",
                "label": "Blog Posts",
                "folder": "content/posts",
                "create": True,
                "slug": "{{year}}-{{month}}-{{day}}-{{slug}}",
                "fields": [
                    {"label": "Title", "name": "title", "widget": "string"},
                    {"label": "Date", "name": "date", "widget": "datetime"},
                    {"label": "Description", "name": "description", "widget": "text", "required": False},
                    {"label": "Body", "name": "body", "widget": "markdown"}
                ]
            },
            {
                "name": "pages",
                "label": "Pages",
                "folder": "content/pages",
                "create": True,
                "slug": "{{slug}}",
                "fields": [
                    {"label": "Title", "name": "title", "widget": "string"},
                    {"label": "Body", "name": "body", "widget": "markdown"}
                ]
            }
        ]

        # Add SSG-specific configurations
        if ssg_engine == "hugo":
            # Hugo-specific frontmatter
            for collection in collections:
                collection["fields"].insert(1, {
                    "label": "Draft", "name": "draft", "widget": "boolean", "default": False
                })

        elif ssg_engine == "gatsby":
            # Gatsby-specific configurations
            for collection in collections:
                collection["fields"].insert(-1, {
                    "label": "Tags", "name": "tags", "widget": "list", "required": False
                })

        return collections

    def _get_direct_mode_buildspec(self) -> codebuild.BuildSpec:
        """Get buildspec for direct mode builds"""

        ssg_engine = self.client_config.service_integration.ssg_engine

        if ssg_engine == "hugo":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"go": "1.19"},
                        "commands": [
                            "curl -L -o hugo.tar.gz https://github.com/gohugoio/hugo/releases/download/v0.111.0/hugo_extended_0.111.0_linux-amd64.tar.gz",
                            "tar -xzf hugo.tar.gz",
                            "chmod +x hugo",
                            "mv hugo /usr/local/bin/"
                        ]
                    },
                    "build": {
                        "commands": ["hugo --minify"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "public"
                }
            })

        elif ssg_engine == "eleventy":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": ["npx @11ty/eleventy"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "_site"
                }
            })

        elif ssg_engine == "astro":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": ["npm run build"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "dist"
                }
            })

        else:  # gatsby
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": ["gatsby build"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "public"
                }
            })

    def _create_stack_outputs(self) -> None:
        """Create CloudFormation outputs"""

        # Common outputs
        CfnOutput(
            self,
            "SiteUrl",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="Published site URL"
        )

        CfnOutput(
            self,
            "DecapAdminUrl",
            value=f"https://{self.distribution.distribution_domain_name}/admin",
            description="Decap CMS admin interface URL"
        )

        CfnOutput(
            self,
            "IntegrationMode",
            value=self.integration_mode.value,
            description="CMS integration mode (direct or event_driven)"
        )

        CfnOutput(
            self,
            "CMSProvider",
            value="decap",
            description="CMS provider"
        )

        CfnOutput(
            self,
            "SSGEngine",
            value=self.client_config.service_integration.ssg_engine,
            description="SSG engine"
        )

        # Mode-specific outputs
        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            CfnOutput(
                self,
                "ContentEventsTopicArn",
                value=self.integration_layer.content_events_topic.topic_arn,
                description="SNS topic for content events"
            )

            CfnOutput(
                self,
                "IntegrationApiUrl",
                value=self.integration_layer.integration_api.url,
                description="Integration API endpoint"
            )

            CfnOutput(
                self,
                "SupportsComposition",
                value="true",
                description="Supports composition with other providers"
            )
        else:
            CfnOutput(
                self,
                "SupportsComposition",
                value="false",
                description="Direct mode - no composition support"
            )

    def _create_custom_infrastructure(self) -> None:
        """Required implementation from BaseSSGStack"""
        # Infrastructure creation is handled by mode-specific methods
        pass

    def get_monthly_cost_estimate(self) -> Dict[str, Any]:
        """Get monthly cost estimate for Decap CMS tier"""

        base_costs = {
            "decap_cms": 0,  # FREE!
            "aws_hosting": 25,  # Base hosting costs
            "cloudfront": 15,  # CDN costs
            "codebuild": 10,  # Build minutes
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 5,  # Event messaging
                "lambda_executions": 5,  # Event processing
                "dynamodb": 10,  # Unified content storage
            })

        base_costs["total"] = sum(base_costs.values())

        return base_costs

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for Decap CMS tier"""

        score = 0
        reasons = []

        # Budget consciousness (major factor for Decap)
        if requirements.get("budget_conscious", False):
            score += 30
            reasons.append("FREE CMS - no monthly fees")

        # Technical comfort
        if requirements.get("technical_team", False):
            score += 25
            reasons.append("Git-based workflow perfect for technical teams")

        # Content volume (Decap works best with small-medium volumes)
        content_volume = requirements.get("content_volume", "medium")
        if content_volume in ["small", "medium"]:
            score += 20
            reasons.append("Optimal for small to medium content volumes")
        elif content_volume == "large":
            score -= 10
            reasons.append("May not scale well for large content volumes")

        # Control and ownership
        if requirements.get("vendor_independence", False):
            score += 15
            reasons.append("Zero vendor lock-in with git-based storage")

        # Integration mode preference
        if requirements.get("simple_workflow", False):
            score += 10
            reasons.append("Simple git-based workflow")

        # Determine suitability level
        if score >= 80:
            suitability = "excellent"
        elif score >= 60:
            suitability = "good"
        elif score >= 40:
            suitability = "fair"
        else:
            suitability = "poor"

        return {
            "suitability_score": min(100, max(0, score)),
            "suitability": suitability,
            "reasons": reasons,
            "integration_mode_recommendation": "direct" if requirements.get("simple_workflow") else "event_driven"
        }