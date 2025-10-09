"""
Contentful CMS Tier Stack

Updated Contentful CMS implementation with optional event-driven integration support:
- Direct Mode: Contentful webhooks → build pipeline (traditional, enterprise-proven)
- Event-Driven Mode: Contentful events → SNS → unified content system (composition-ready)

Contentful CMS Features:
- Enterprise-grade content management with advanced workflows
- Team collaboration with roles, permissions, and approval processes
- Multi-language content support with localization workflows
- Rich media management with asset optimization and CDN
- GraphQL and REST API access for flexible integrations
- Advanced content modeling with references and structured data
- Content versioning, scheduling, and publishing workflows

Target Market:
- Enterprise clients with complex content needs
- Large content teams requiring collaboration tools
- Multi-brand organizations needing content governance
- Global companies requiring localization workflows
- Organizations needing enterprise security and compliance

Pricing:
- Contentful CMS: $300-2000+/month (Team to Enterprise plans)
- AWS Hosting: $50-100/month
- Total: $350-2,100+/month depending on usage and plan
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
    aws_dynamodb as dynamodb,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from models.service_config import ClientServiceConfig, IntegrationMode
from shared.composition.integration_layer import EventDrivenIntegrationLayer
from shared.providers.cms.factory import CMSProviderFactory


class ContentfulCMSStack(BaseSSGStack):
    """
    Contentful CMS Tier Stack Implementation

    Supports both integration modes:
    - Direct: Contentful webhooks → CodeBuild → S3/CloudFront (enterprise-proven)
    - Event-Driven: Contentful events → SNS → unified content system (composition-ready)

    The enterprise CMS solution for sophisticated content management needs.
    """

    # Supported SSG engines for Contentful CMS
    SUPPORTED_SSG_ENGINES = {
        "gatsby": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "features": ["graphql", "contentful_source_plugin", "image_optimization"]
        },
        "astro": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["contentful_integration", "component_islands", "fast_builds"]
        },
        "nextjs": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["contentful_sdk", "isr", "preview_mode"]
        },
        "nuxt": {
            "compatibility": "good",
            "setup_complexity": "intermediate",
            "features": ["contentful_module", "ssr_support", "vue_components"]
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

        # Validate Contentful CMS configuration
        self._validate_contentful_cms_config()

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

    def _validate_contentful_cms_config(self) -> None:
        """Validate Contentful CMS configuration"""
        service_config = self.client_config.service_integration

        if not service_config.cms_config:
            raise ValueError("Contentful CMS tier requires cms_config")

        if service_config.cms_config.provider != "contentful":
            raise ValueError(f"Expected Contentful CMS provider, got {service_config.cms_config.provider}")

        # Validate Contentful-specific settings
        settings = service_config.cms_config.settings
        required = ["space_id"]
        for setting in required:
            if not settings.get(setting):
                raise ValueError(f"Contentful CMS requires '{setting}' in settings")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"Contentful CMS supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_cms_provider(self):
        """Initialize CMS provider instance"""
        cms_config = self.client_config.service_integration.cms_config
        return CMSProviderFactory.create_provider(
            cms_config.provider,
            cms_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Contentful webhook → CodeBuild pipeline
        self.contentful_webhook_handler = self._create_contentful_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # Enterprise monitoring and logging
        self._create_enterprise_monitoring()

        # Contentful webhook integration
        self._create_contentful_webhook_integration()

        print(f"✅ Created Contentful CMS direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Contentful events → Integration Layer → Unified Content
        self._create_event_driven_cms_integration()

        # Enterprise monitoring (same as direct mode)
        self._create_enterprise_monitoring()

        # Connect to event system
        self._connect_contentful_to_event_system()

        print(f"✅ Created Contentful CMS event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_contentful_secrets()
        self._create_preview_environment()

    def _create_contentful_webhook_handler(self) -> lambda_.Function:
        """Create Contentful webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "ContentfulWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="contentful_webhook.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import hmac
import hashlib
import os

def main(event, context):
    '''Handle Contentful webhook for direct mode'''

    try:
        # Verify webhook signature
        if not verify_contentful_signature(event):
            return {'statusCode': 401, 'body': 'Unauthorized'}

        # Parse webhook payload
        body = json.loads(event['body'])

        # Get webhook topic from headers
        topic = event['headers'].get('X-Contentful-Topic', '')

        # Only trigger build for published entries
        if topic in ['ContentManagement.Entry.publish', 'ContentManagement.Asset.publish']:
            codebuild = boto3.client('codebuild')

            entry_id = body.get('sys', {}).get('id', '')
            content_type = body.get('sys', {}).get('contentType', {}).get('sys', {}).get('id', '')

            response = codebuild.start_build(
                projectName=os.environ['BUILD_PROJECT_NAME'],
                environmentVariablesOverride=[
                    {
                        'name': 'CONTENTFUL_ENTRY_ID',
                        'value': entry_id
                    },
                    {
                        'name': 'CONTENTFUL_CONTENT_TYPE',
                        'value': content_type
                    },
                    {
                        'name': 'WEBHOOK_TOPIC',
                        'value': topic
                    }
                ]
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Build triggered',
                    'buildId': response['build']['id'],
                    'entryId': entry_id,
                    'contentType': content_type
                })
            }

        return {'statusCode': 200, 'body': f'Topic {topic} ignored'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def verify_contentful_signature(event):
    '''Verify Contentful webhook signature'''
    webhook_secret = os.environ.get('CONTENTFUL_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return True  # Skip verification if no secret set

    signature = event['headers'].get('X-Contentful-Webhook-Signature', '')
    body = event['body']

    # Contentful uses HMAC-SHA256
    expected = hmac.new(
        webhook_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-contentful-build",
                "CONTENTFUL_WEBHOOK_SECRET": "placeholder"  # Should use Secrets Manager
            },
            timeout=Duration.seconds(30)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        # Get Contentful settings for environment variables
        contentful_settings = self.cms_provider.settings

        return codebuild.Project(
            self,
            "ContentfulDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-contentful-build",
            source=codebuild.Source.no_source(),  # Contentful is API-based
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.MEDIUM,  # Medium for enterprise builds
                environment_variables={
                    "CONTENTFUL_SPACE_ID": codebuild.BuildEnvironmentVariable(
                        value=contentful_settings["space_id"]
                    ),
                    "CONTENTFUL_ENVIRONMENT": codebuild.BuildEnvironmentVariable(
                        value=contentful_settings.get("environment", "master")
                    ),
                    "CONTENTFUL_HOST": codebuild.BuildEnvironmentVariable(
                        value=contentful_settings.get("host", "cdn.contentful.com")
                    )
                }
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_cms_integration(self) -> None:
        """Create event-driven CMS integration"""

        # Contentful Event Processor - transforms Contentful webhooks to unified content events
        self.contentful_event_processor = lambda_.Function(
            self,
            "ContentfulEventProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="contentful_event_processor.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import os
import uuid
from datetime import datetime, timezone

def main(event, context):
    '''Process Contentful events and publish to unified content system'''

    sns = boto3.client('sns')

    try:
        # Parse Contentful webhook
        contentful_event = json.loads(event['body'])
        topic = event['headers'].get('X-Contentful-Topic', '')

        # Only process published content
        if 'publish' not in topic:
            return {'statusCode': 200, 'body': 'Non-publish event ignored'}

        # Extract entry information
        entry_id = contentful_event.get('sys', {}).get('id', '')
        content_type_id = contentful_event.get('sys', {}).get('contentType', {}).get('sys', {}).get('id', '')

        # Transform to unified content event
        unified_event = {
            'event_type': 'content_updated',
            'provider': 'contentful',
            'content_id': entry_id,
            'content_type': map_contentful_type(content_type_id),
            'timestamp': contentful_event.get('sys', {}).get('updatedAt', datetime.now(timezone.utc).isoformat()),
            'data': {
                'contentful_entry': contentful_event,
                'content_type_id': content_type_id,
                'space_id': contentful_event.get('sys', {}).get('space', {}).get('sys', {}).get('id', ''),
                'environment_id': contentful_event.get('sys', {}).get('environment', {}).get('sys', {}).get('id', ''),
                'revision': contentful_event.get('sys', {}).get('revision', 0),
                'webhook_topic': topic
            }
        }

        # Publish to content events topic
        sns.publish(
            TopicArn=os.environ['CONTENT_EVENTS_TOPIC_ARN'],
            Message=json.dumps(unified_event),
            Subject=f"Contentful Content Updated: {unified_event['content_id']}"
        )

        return {'statusCode': 200, 'body': f'Processed entry: {entry_id}'}

    except Exception as e:
        print(f"Error processing Contentful event: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def map_contentful_type(content_type_id):
    '''Map Contentful content types to unified content types'''
    type_mapping = {
        'blogPost': 'article',
        'post': 'article',
        'article': 'article',
        'page': 'page',
        'landingPage': 'page',
        'product': 'product',
        'category': 'collection',
        'collection': 'collection'
    }
    return type_mapping.get(content_type_id, 'page')
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn
            },
            timeout=Duration.seconds(30)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.contentful_event_processor)

    def _create_enterprise_monitoring(self) -> None:
        """Create enterprise-grade monitoring and logging"""

        # Content analytics table for enterprise insights
        self.analytics_table = dynamodb.Table(
            self,
            "ContentfulAnalyticsTable",
            table_name=f"{self.client_config.resource_prefix}-contentful-analytics",
            partition_key=dynamodb.Attribute(
                name="entry_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"  # Auto-cleanup old analytics
        )

        # Performance monitoring Lambda
        self.monitoring_function = lambda_.Function(
            self,
            "ContentfulMonitoring",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="contentful_monitoring.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import os
from datetime import datetime, timezone

def main(event, context):
    '''Monitor Contentful performance and log analytics'''

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['ANALYTICS_TABLE_NAME'])

    # Log content update analytics
    for record in event.get('Records', []):
        if record.get('eventName') in ['INSERT', 'MODIFY']:
            # Extract content information
            content_data = record.get('dynamodb', {}).get('NewImage', {})

            # Store analytics
            table.put_item(Item={
                'entry_id': content_data.get('content_id', {}).get('S', ''),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'event_type': record.get('eventName'),
                'content_type': content_data.get('content_type', {}).get('S', ''),
                'ttl': int((datetime.now(timezone.utc).timestamp() + 2592000))  # 30 days TTL
            })

    return {'statusCode': 200, 'processed': len(event.get('Records', []))}
            """),
            environment={
                "ANALYTICS_TABLE_NAME": self.analytics_table.table_name
            },
            timeout=Duration.seconds(60)
        )

        # Grant DynamoDB write permissions
        self.analytics_table.grant_write_data(self.monitoring_function)

    def _create_contentful_webhook_integration(self) -> None:
        """Create Contentful webhook integration for direct mode"""

        # Create API Gateway for Contentful webhooks
        webhook_api = apigateway.RestApi(
            self,
            "ContentfulWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-contentful-webhooks",
            description="Contentful webhook endpoint"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.contentful_webhook_handler)
        )

        # Output webhook URL
        CfnOutput(
            self,
            "ContentfulWebhookUrl",
            value=f"{webhook_api.url}webhook",
            description="Webhook URL to configure in Contentful space"
        )

    def _connect_contentful_to_event_system(self) -> None:
        """Connect Contentful CMS to event system for event-driven mode"""

        # Create API Gateway for Contentful webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "ContentfulEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-contentful-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        contentful_resource = event_resource.add_resource("contentful")

        contentful_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.contentful_event_processor)
        )

        # Output webhook URL for Contentful configuration
        CfnOutput(
            self,
            "ContentfulEventWebhookUrl",
            value=f"{webhook_api.url}events/contentful",
            description="Event webhook URL to configure in Contentful space"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # Additional Contentful-specific storage could be added here
        pass

    def _create_contentful_secrets(self) -> None:
        """Create secrets for Contentful API credentials"""

        # Contentful delivery API token
        self.delivery_token_secret = secrets.Secret(
            self,
            "ContentfulDeliveryTokenSecret",
            secret_name=f"{self.client_config.resource_prefix}-contentful-delivery-token",
            description="Contentful Delivery API token for content fetching"
        )

        # Contentful preview API token
        self.preview_token_secret = secrets.Secret(
            self,
            "ContentfulPreviewTokenSecret",
            secret_name=f"{self.client_config.resource_prefix}-contentful-preview-token",
            description="Contentful Preview API token for draft content"
        )

        # Webhook secret
        self.webhook_secret = secrets.Secret(
            self,
            "ContentfulWebhookSecret",
            secret_name=f"{self.client_config.resource_prefix}-contentful-webhook-secret",
            description="Secret for Contentful webhook signature verification"
        )

    def _create_preview_environment(self) -> None:
        """Create preview environment for content editing"""

        # Preview Lambda for draft content
        self.preview_function = lambda_.Function(
            self,
            "ContentfulPreviewFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="contentful_preview.main",
            code=lambda_.Code.from_inline("""
import json
import os

def main(event, context):
    '''Handle preview requests for draft content'''

    try:
        # Get preview parameters
        query_params = event.get('queryStringParameters', {}) or {}
        entry_id = query_params.get('entry_id', '')

        if not entry_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'entry_id parameter required'})
            }

        # Generate preview URL
        preview_url = f"https://{os.environ['SITE_DOMAIN']}/preview/{entry_id}"

        return {
            'statusCode': 302,
            'headers': {
                'Location': preview_url
            },
            'body': ''
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
            """),
            environment={
                "SITE_DOMAIN": self.client_config.domain
            },
            timeout=Duration.seconds(10)
        )

    def _get_direct_mode_buildspec(self) -> codebuild.BuildSpec:
        """Get buildspec for direct mode builds"""

        ssg_engine = self.client_config.service_integration.ssg_engine

        if ssg_engine == "gatsby":
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

        elif ssg_engine == "nextjs":
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

        space_id = self.cms_provider.settings["space_id"]
        CfnOutput(
            self,
            "ContentfulSpaceUrl",
            value=f"https://app.contentful.com/spaces/{space_id}",
            description="Contentful space management URL"
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
            value="contentful",
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
        """Get monthly cost estimate for Contentful CMS tier"""

        base_costs = {
            "contentful_team": 300,  # Team plan: 5 users, 1M API requests
            "contentful_business": 879,  # Business plan: 15 users, 10M API requests
            "contentful_enterprise": 2000,  # Enterprise plan: custom pricing
            "aws_hosting": 75,  # Base hosting costs (higher for enterprise)
            "cloudfront": 25,  # CDN costs
            "codebuild": 20,  # Build minutes
            "monitoring": 15,  # Enterprise monitoring
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 15,  # Event messaging
                "lambda_executions": 15,  # Event processing
                "dynamodb": 20,  # Unified content storage
                "analytics": 10,  # Enterprise analytics
            })

        # Calculate total for different Contentful plans
        base_hosting = base_costs["aws_hosting"] + base_costs["cloudfront"] + base_costs["codebuild"] + base_costs["monitoring"]
        event_costs = base_costs.get("sns_messages", 0) + base_costs.get("lambda_executions", 0) + base_costs.get("dynamodb", 0) + base_costs.get("analytics", 0)

        return {
            "contentful_team_total": base_costs["contentful_team"] + base_hosting + event_costs,
            "contentful_business_total": base_costs["contentful_business"] + base_hosting + event_costs,
            "contentful_enterprise_total": base_costs["contentful_enterprise"] + base_hosting + event_costs,
            "recommended_plan": "business" if self.integration_mode == IntegrationMode.EVENT_DRIVEN else "team"
        }

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for Contentful CMS tier"""

        score = 0
        reasons = []

        # Enterprise features need (major factor for Contentful)
        if requirements.get("enterprise_cms", False):
            score += 35
            reasons.append("Enterprise-grade features and workflows")

        # Content team size (Contentful excels with large teams)
        team_size = requirements.get("team_size", 1)
        if team_size >= 15:
            score += 25
            reasons.append("Excellent for large content teams")
        elif team_size >= 5:
            score += 15
            reasons.append("Good for medium content teams")
        else:
            score -= 10
            reasons.append("May be overkill for small teams")

        # Multi-language/localization
        if requirements.get("multi_language", False):
            score += 20
            reasons.append("Advanced localization workflows")

        # Advanced content modeling
        if requirements.get("complex_content_modeling", False):
            score += 15
            reasons.append("Sophisticated content modeling capabilities")

        # Budget considerations (Contentful is premium)
        budget = requirements.get("monthly_budget", 100)
        if budget >= 1000:
            score += 15
            reasons.append("Budget supports enterprise features")
        elif budget >= 500:
            score += 10
            reasons.append("Budget supports business plan")
        elif budget >= 350:
            score += 5
            reasons.append("Budget supports team plan")
        else:
            score -= 20
            reasons.append("Budget may be insufficient for Contentful")

        # API usage and traffic
        if requirements.get("high_traffic", False):
            score += 10
            reasons.append("Scales well for high-traffic sites")

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
            "integration_mode_recommendation": "event_driven" if team_size >= 10 else "direct"
        }