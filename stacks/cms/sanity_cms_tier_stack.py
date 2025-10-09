"""
Sanity CMS Tier Stack

Updated Sanity CMS implementation with optional event-driven integration support:
- Direct Mode: Sanity webhooks → build pipeline (traditional, fast)
- Event-Driven Mode: Sanity events → SNS → unified content system (composition-ready)

Sanity CMS Features:
- Structured content platform with real-time APIs
- GROQ query language for flexible content access
- Advanced content modeling and relationships
- Real-time collaboration with live editing
- Powerful media management with transformations
- Excellent developer experience with Studio

Target Market:
- Content-heavy sites requiring structured data
- Teams needing advanced content modeling
- Projects requiring real-time collaboration
- Enterprises needing scalable content architecture
- Sites with complex content relationships

Pricing:
- Sanity CMS: $0-199/month (Free tier to Business plan)
- AWS Hosting: $45-80/month
- Total: $65-280/month depending on usage and plan
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


class SanityCMSTierStack(BaseSSGStack):
    """
    Sanity CMS Tier Stack Implementation

    Supports both integration modes:
    - Direct: Sanity webhooks → CodeBuild → S3/CloudFront (traditional, fast)
    - Event-Driven: Sanity events → SNS → unified content system (composition-ready)

    Perfect for structured content and enterprise content management needs.
    """

    # Supported SSG engines for Sanity CMS
    SUPPORTED_SSG_ENGINES = {
        "astro": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["component_islands", "sanity_integration", "fast_builds"]
        },
        "gatsby": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "features": ["graphql", "sanity_source_plugin", "rich_ecosystem"]
        },
        "nextjs": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["isr", "preview_mode", "sanity_studio_embed"]
        },
        "nuxt": {
            "compatibility": "good",
            "setup_complexity": "intermediate",
            "features": ["vue_components", "sanity_module", "ssr_support"]
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

        # Validate Sanity CMS configuration
        self._validate_sanity_cms_config()

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

    def _validate_sanity_cms_config(self) -> None:
        """Validate Sanity CMS configuration"""
        service_config = self.client_config.service_integration

        if not service_config.cms_config:
            raise ValueError("Sanity CMS tier requires cms_config")

        if service_config.cms_config.provider != "sanity":
            raise ValueError(f"Expected Sanity CMS provider, got {service_config.cms_config.provider}")

        # Validate Sanity-specific settings
        settings = service_config.cms_config.settings
        required = ["project_id"]
        for setting in required:
            if not settings.get(setting):
                raise ValueError(f"Sanity CMS requires '{setting}' in settings")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"Sanity CMS supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_cms_provider(self):
        """Initialize CMS provider instance"""
        cms_config = self.client_config.service_integration.cms_config
        return CMSProviderFactory.create_provider(
            cms_config.provider,
            cms_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Sanity webhook → CodeBuild pipeline
        self.sanity_webhook_handler = self._create_sanity_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # Sanity Studio configuration
        self._create_sanity_studio_config()

        # Sanity webhook integration
        self._create_sanity_webhook_integration()

        print(f"✅ Created Sanity CMS direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Sanity events → Integration Layer → Unified Content
        self._create_event_driven_cms_integration()

        # Sanity Studio configuration (same as direct mode)
        self._create_sanity_studio_config()

        # Connect to event system
        self._connect_sanity_to_event_system()

        print(f"✅ Created Sanity CMS event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_sanity_secrets()
        self._create_monitoring_and_logging()

    def _create_sanity_webhook_handler(self) -> lambda_.Function:
        """Create Sanity webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "SanityWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="sanity_webhook.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import hmac
import hashlib
import os

def main(event, context):
    '''Handle Sanity webhook for direct mode'''

    try:
        # Verify webhook signature if secret is configured
        if not verify_sanity_signature(event):
            return {'statusCode': 401, 'body': 'Unauthorized'}

        # Parse webhook payload
        body = json.loads(event['body'])

        # Only trigger build for published documents
        if body.get('_id') and not body.get('_id').startswith('drafts.'):
            codebuild = boto3.client('codebuild')

            response = codebuild.start_build(
                projectName=os.environ['BUILD_PROJECT_NAME'],
                environmentVariablesOverride=[
                    {
                        'name': 'SANITY_DOCUMENT_ID',
                        'value': body.get('_id', '')
                    },
                    {
                        'name': 'SANITY_DOCUMENT_TYPE',
                        'value': body.get('_type', '')
                    }
                ]
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Build triggered',
                    'buildId': response['build']['id'],
                    'documentId': body.get('_id')
                })
            }

        return {'statusCode': 200, 'body': 'No action needed'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def verify_sanity_signature(event):
    '''Verify Sanity webhook signature'''
    sanity_secret = os.environ.get('SANITY_WEBHOOK_SECRET', '')
    if not sanity_secret:
        return True  # Skip verification if no secret set

    signature = event['headers'].get('sanity-webhook-signature', '')
    body = event['body']

    # Sanity uses sha256 signature format
    expected = hashlib.sha256((body + sanity_secret).encode()).hexdigest()

    return hmac.compare_digest(signature, expected)
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-sanity-build",
                "SANITY_WEBHOOK_SECRET": "placeholder"  # Should use Secrets Manager
            },
            timeout=Duration.seconds(30)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        # Get Sanity settings for environment variables
        sanity_settings = self.cms_provider.settings

        return codebuild.Project(
            self,
            "SanityDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-sanity-build",
            source=codebuild.Source.no_source(),  # Sanity is API-based, not git-based
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    "SANITY_PROJECT_ID": codebuild.BuildEnvironmentVariable(
                        value=sanity_settings["project_id"]
                    ),
                    "SANITY_DATASET": codebuild.BuildEnvironmentVariable(
                        value=sanity_settings.get("dataset", "production")
                    ),
                    "SANITY_API_VERSION": codebuild.BuildEnvironmentVariable(
                        value=sanity_settings.get("api_version", "2023-05-03")
                    )
                }
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_cms_integration(self) -> None:
        """Create event-driven CMS integration"""

        # Sanity Event Processor - transforms Sanity webhooks to unified content events
        self.sanity_event_processor = lambda_.Function(
            self,
            "SanityEventProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="sanity_event_processor.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import os
import uuid
from datetime import datetime, timezone

def main(event, context):
    '''Process Sanity events and publish to unified content system'''

    sns = boto3.client('sns')

    try:
        # Parse Sanity webhook
        sanity_event = json.loads(event['body'])

        # Skip draft documents
        document_id = sanity_event.get('_id', '')
        if document_id.startswith('drafts.'):
            return {'statusCode': 200, 'body': 'Draft document ignored'}

        # Transform to unified content event
        unified_event = {
            'event_type': 'content_updated',
            'provider': 'sanity',
            'content_id': document_id,
            'content_type': determine_content_type(sanity_event.get('_type', '')),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'sanity_document': sanity_event,
                'document_type': sanity_event.get('_type'),
                'revision': sanity_event.get('_rev'),
                'created_at': sanity_event.get('_createdAt'),
                'updated_at': sanity_event.get('_updatedAt')
            }
        }

        # Publish to content events topic
        sns.publish(
            TopicArn=os.environ['CONTENT_EVENTS_TOPIC_ARN'],
            Message=json.dumps(unified_event),
            Subject=f"Sanity Content Updated: {unified_event['content_id']}"
        )

        return {'statusCode': 200, 'body': f'Processed document: {document_id}'}

    except Exception as e:
        print(f"Error processing Sanity event: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def determine_content_type(sanity_type):
    '''Map Sanity document types to unified content types'''
    type_mapping = {
        'post': 'article',
        'article': 'article',
        'blog': 'article',
        'page': 'page',
        'product': 'product',
        'category': 'collection',
        'collection': 'collection'
    }
    return type_mapping.get(sanity_type, 'page')
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn
            },
            timeout=Duration.seconds(30)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.sanity_event_processor)

    def _create_sanity_studio_config(self) -> None:
        """Create Sanity Studio configuration"""

        # Generate Studio configuration for the client
        studio_config = self._generate_sanity_studio_config()

        # Store configuration in S3 for deployment
        # This would typically be done during deployment process
        pass

    def _create_sanity_webhook_integration(self) -> None:
        """Create Sanity webhook integration for direct mode"""

        # Create API Gateway for Sanity webhooks
        webhook_api = apigateway.RestApi(
            self,
            "SanityWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-sanity-webhooks",
            description="Sanity webhook endpoint"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.sanity_webhook_handler)
        )

        # Output webhook URL
        CfnOutput(
            self,
            "SanityWebhookUrl",
            value=f"{webhook_api.url}webhook",
            description="Webhook URL to configure in Sanity Studio"
        )

    def _connect_sanity_to_event_system(self) -> None:
        """Connect Sanity CMS to event system for event-driven mode"""

        # Create API Gateway for Sanity webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "SanityEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-sanity-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        sanity_resource = event_resource.add_resource("sanity")

        sanity_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.sanity_event_processor)
        )

        # Output webhook URL for Sanity configuration
        CfnOutput(
            self,
            "SanityEventWebhookUrl",
            value=f"{webhook_api.url}events/sanity",
            description="Event webhook URL to configure in Sanity Studio"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # Additional Sanity-specific storage could be added here
        pass

    def _create_sanity_secrets(self) -> None:
        """Create secrets for Sanity API credentials"""

        # Sanity API token secret
        self.sanity_token_secret = secrets.Secret(
            self,
            "SanityTokenSecret",
            secret_name=f"{self.client_config.resource_prefix}-sanity-token",
            description="Sanity API token for content fetching"
        )

        # Optional webhook secret
        self.webhook_secret = secrets.Secret(
            self,
            "SanityWebhookSecret",
            secret_name=f"{self.client_config.resource_prefix}-sanity-webhook-secret",
            description="Secret for Sanity webhook signature verification"
        )

    def _create_monitoring_and_logging(self) -> None:
        """Create monitoring and logging (both modes)"""
        # CloudWatch dashboards and alarms for Sanity integration
        pass

    def _generate_sanity_studio_config(self) -> Dict[str, Any]:
        """Generate Sanity Studio configuration"""

        cms_settings = self.cms_provider.settings
        ssg_engine = self.client_config.service_integration.ssg_engine

        # Base Studio configuration
        config = {
            "projectId": cms_settings["project_id"],
            "dataset": cms_settings.get("dataset", "production"),
            "plugins": [
                "@sanity/vision"  # GROQ query tool
            ],
            "schema": {
                "types": self._get_sanity_schema_types()
            }
        }

        # Add SSG-specific configurations
        if ssg_engine == "nextjs":
            config["plugins"].append("@sanity/nextjs-loader")
        elif ssg_engine == "gatsby":
            config["plugins"].append("gatsby-source-sanity")

        return config

    def _get_sanity_schema_types(self) -> List[Dict[str, Any]]:
        """Get Sanity schema types configuration"""

        # Basic schema types that work with all SSG engines
        schema_types = [
            {
                "name": "post",
                "type": "document",
                "title": "Blog Post",
                "fields": [
                    {"name": "title", "type": "string", "title": "Title"},
                    {"name": "slug", "type": "slug", "title": "Slug", "options": {"source": "title"}},
                    {"name": "publishedAt", "type": "datetime", "title": "Published At"},
                    {"name": "excerpt", "type": "text", "title": "Excerpt"},
                    {"name": "body", "type": "array", "title": "Body", "of": [{"type": "block"}]},
                    {"name": "featuredImage", "type": "image", "title": "Featured Image"},
                    {"name": "tags", "type": "array", "title": "Tags", "of": [{"type": "string"}]}
                ]
            },
            {
                "name": "page",
                "type": "document",
                "title": "Page",
                "fields": [
                    {"name": "title", "type": "string", "title": "Title"},
                    {"name": "slug", "type": "slug", "title": "Slug", "options": {"source": "title"}},
                    {"name": "body", "type": "array", "title": "Body", "of": [{"type": "block"}]},
                    {"name": "seo", "type": "seo", "title": "SEO"}
                ]
            },
            {
                "name": "seo",
                "type": "object",
                "title": "SEO",
                "fields": [
                    {"name": "title", "type": "string", "title": "SEO Title"},
                    {"name": "description", "type": "text", "title": "SEO Description"},
                    {"name": "image", "type": "image", "title": "Social Image"}
                ]
            }
        ]

        return schema_types

    def _get_direct_mode_buildspec(self) -> codebuild.BuildSpec:
        """Get buildspec for direct mode builds"""

        ssg_engine = self.client_config.service_integration.ssg_engine

        if ssg_engine == "nextjs":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": [
                            "npm run build",
                            "npm run export"
                        ]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "out"
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

        elif ssg_engine == "gatsby":
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

        else:  # nuxt
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": ["npm run generate"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "dist"
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
            "SanityStudioUrl",
            value=f"https://{self.cms_provider.settings['project_id']}.sanity.studio",
            description="Sanity Studio URL for content management"
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
            value="sanity",
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
        """Get monthly cost estimate for Sanity CMS tier"""

        base_costs = {
            "sanity_cms_free": 0,  # Free tier: 3 users, 500K API requests
            "sanity_cms_team": 99,  # Team plan: 5 users, 1M API requests
            "sanity_cms_business": 199,  # Business plan: 15 users, 10M API requests
            "aws_hosting": 60,  # Base hosting costs (higher due to API calls)
            "cloudfront": 20,  # CDN costs
            "codebuild": 15,  # Build minutes
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 10,  # Event messaging
                "lambda_executions": 10,  # Event processing
                "dynamodb": 15,  # Unified content storage
            })

        # Calculate total for different Sanity plans
        return {
            "sanity_free_tier": base_costs["sanity_cms_free"] + base_costs["aws_hosting"] + base_costs["cloudfront"] + base_costs["codebuild"] + base_costs.get("sns_messages", 0) + base_costs.get("lambda_executions", 0) + base_costs.get("dynamodb", 0),
            "sanity_team_plan": base_costs["sanity_cms_team"] + base_costs["aws_hosting"] + base_costs["cloudfront"] + base_costs["codebuild"] + base_costs.get("sns_messages", 0) + base_costs.get("lambda_executions", 0) + base_costs.get("dynamodb", 0),
            "sanity_business_plan": base_costs["sanity_cms_business"] + base_costs["aws_hosting"] + base_costs["cloudfront"] + base_costs["codebuild"] + base_costs.get("sns_messages", 0) + base_costs.get("lambda_executions", 0) + base_costs.get("dynamodb", 0),
            "recommended_plan": "team" if self.integration_mode == IntegrationMode.EVENT_DRIVEN else "free"
        }

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for Sanity CMS tier"""

        score = 0
        reasons = []

        # Structured content need (major factor for Sanity)
        if requirements.get("structured_content", False):
            score += 30
            reasons.append("Excellent structured content modeling")

        # Content team size
        team_size = requirements.get("team_size", 1)
        if team_size >= 5:
            score += 25
            reasons.append("Great for collaborative content teams")
        elif team_size >= 3:
            score += 15
            reasons.append("Good for small content teams")

        # Technical sophistication
        if requirements.get("technical_team", False):
            score += 20
            reasons.append("Developer-friendly with GROQ query language")

        # Real-time features
        if requirements.get("real_time_editing", False):
            score += 15
            reasons.append("Real-time collaboration and live preview")

        # Content complexity
        content_complexity = requirements.get("content_complexity", "simple")
        if content_complexity == "complex":
            score += 20
            reasons.append("Handles complex content relationships")
        elif content_complexity == "medium":
            score += 10

        # Budget considerations
        budget = requirements.get("monthly_budget", 100)
        if budget >= 200:
            score += 10
            reasons.append("Budget supports Business plan features")
        elif budget >= 100:
            score += 5
            reasons.append("Budget supports Team plan")
        else:
            score -= 5
            reasons.append("May exceed budget on paid plans")

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
            "integration_mode_recommendation": "event_driven" if team_size >= 5 else "direct"
        }