"""
Foxy.io E-commerce Tier Stack

Updated Foxy.io implementation with optional event-driven integration support:
- Direct Mode: Foxy.io webhooks → build pipeline (traditional, advanced features)
- Event-Driven Mode: Foxy.io events → SNS → unified content system (composition-ready)

Foxy.io E-commerce Features:
- Advanced e-commerce with 1.5% transaction fee + $20/month base
- Subscription management and recurring billing
- Advanced cart customization and rules
- Custom checkout flows and API access
- Comprehensive analytics and customer insights
- Multi-currency and international shipping

Target Market:
- Businesses needing advanced e-commerce features
- Subscription-based business models
- Custom checkout flow requirements
- Clients wanting sophisticated cart behavior
- Multi-currency and international operations

Pricing:
- Foxy.io: 1.5% transaction fee + $20/month base
- AWS Hosting: $75-100/month
- Total Monthly: $95-120/month + 1.5% of sales
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
from shared.providers.ecommerce.factory import EcommerceProviderFactory


class FoxyEcommerceStack(BaseSSGStack):
    """
    Foxy.io E-commerce Tier Stack Implementation

    Supports both integration modes:
    - Direct: Foxy.io webhooks → CodeBuild → S3/CloudFront (traditional, advanced features)
    - Event-Driven: Foxy.io events → SNS → unified content system (composition-ready)

    The advanced e-commerce solution with sophisticated customization capabilities.
    """

    # Supported SSG engines for Foxy.io
    SUPPORTED_SSG_ENGINES = {
        "hugo": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["fast_builds", "advanced_templating", "foxy_integration"]
        },
        "eleventy": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["flexible_templating", "foxy_helpers", "subscription_support"]
        },
        "astro": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "features": ["component_islands", "foxy_components", "modern_tooling"]
        },
        "gatsby": {
            "compatibility": "good",
            "setup_complexity": "advanced",
            "features": ["react_components", "graphql", "foxy_plugins"]
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

        # Validate Foxy.io e-commerce configuration
        self._validate_foxy_ecommerce_config()

        # Initialize providers and integration
        self.ecommerce_provider = self._initialize_ecommerce_provider()
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

    def _validate_foxy_ecommerce_config(self) -> None:
        """Validate Foxy.io e-commerce configuration"""
        service_config = self.client_config.service_integration

        if not service_config.ecommerce_config:
            raise ValueError("Foxy.io e-commerce tier requires ecommerce_config")

        if service_config.ecommerce_config.provider != "foxy":
            raise ValueError(f"Expected Foxy.io provider, got {service_config.ecommerce_config.provider}")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"Foxy.io supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_ecommerce_provider(self):
        """Initialize e-commerce provider instance"""
        ecommerce_config = self.client_config.service_integration.ecommerce_config
        return EcommerceProviderFactory.create_provider(
            ecommerce_config.provider,
            ecommerce_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Foxy.io webhook → CodeBuild pipeline
        self.foxy_webhook_handler = self._create_foxy_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # Foxy.io configuration
        self._create_foxy_configuration()

        # Foxy.io webhook integration
        self._create_foxy_webhook_integration()

        print(f"✅ Created Foxy.io direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Foxy.io events → Integration Layer → Unified Content
        self._create_event_driven_ecommerce_integration()

        # Foxy.io configuration (same as direct mode)
        self._create_foxy_configuration()

        # Connect to event system
        self._connect_foxy_to_event_system()

        print(f"✅ Created Foxy.io event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_foxy_secrets()
        self._create_subscription_management()
        self._create_advanced_analytics()

    def _create_foxy_webhook_handler(self) -> lambda_.Function:
        """Create Foxy.io webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "FoxyWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="foxy_webhook.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import hmac
import hashlib
import os

def main(event, context):
    '''Handle Foxy.io webhook for direct mode'''

    try:
        # Verify webhook signature
        if not verify_foxy_signature(event):
            return {'statusCode': 401, 'body': 'Unauthorized'}

        # Parse webhook payload
        body = json.loads(event['body'])

        # Get event type from Foxy.io
        resource_type = body.get('_embedded', {}).keys()
        if not resource_type:
            return {'statusCode': 200, 'body': 'No embedded resources'}

        resource_type = list(resource_type)[0]

        # Trigger build for relevant events (transactions, subscriptions, etc.)
        if resource_type in ['fx:transactions', 'fx:subscriptions', 'fx:items']:
            codebuild = boto3.client('codebuild')

            transaction_id = ''
            if resource_type == 'fx:transactions':
                transaction_data = body.get('_embedded', {}).get('fx:transactions', [{}])[0]
                transaction_id = transaction_data.get('id', '')

            response = codebuild.start_build(
                projectName=os.environ['BUILD_PROJECT_NAME'],
                environmentVariablesOverride=[
                    {
                        'name': 'FOXY_EVENT_TYPE',
                        'value': resource_type
                    },
                    {
                        'name': 'FOXY_TRANSACTION_ID',
                        'value': str(transaction_id)
                    }
                ]
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Build triggered',
                    'buildId': response['build']['id'],
                    'eventType': resource_type,
                    'transactionId': transaction_id
                })
            }

        return {'statusCode': 200, 'body': f'Event {resource_type} processed'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def verify_foxy_signature(event):
    '''Verify Foxy.io webhook signature'''
    webhook_secret = os.environ.get('FOXY_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return True  # Skip verification if no secret set

    signature = event['headers'].get('foxy-webhook-signature', '')
    body = event['body']

    # Foxy.io uses custom signature format
    expected = hmac.new(
        webhook_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-foxy-build",
                "FOXY_WEBHOOK_SECRET": "placeholder"  # Should use Secrets Manager
            },
            timeout=Duration.seconds(30)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        # Get Foxy.io settings for environment variables
        foxy_settings = self.ecommerce_provider.settings

        return codebuild.Project(
            self,
            "FoxyDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-foxy-build",
            source=codebuild.Source.no_source(),  # Foxy.io works with existing content
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    "FOXY_SUBDOMAIN": codebuild.BuildEnvironmentVariable(
                        value=foxy_settings.get("subdomain", f"{self.client_config.client_id}-foxy")
                    ),
                    "FOXY_CURRENCY": codebuild.BuildEnvironmentVariable(
                        value=foxy_settings.get("currency", "USD")
                    )
                }
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_ecommerce_integration(self) -> None:
        """Create event-driven e-commerce integration"""

        # Foxy.io Event Processor - transforms Foxy.io webhooks to unified content events
        self.foxy_event_processor = lambda_.Function(
            self,
            "FoxyEventProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="foxy_event_processor.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import os
import uuid
from datetime import datetime, timezone

def main(event, context):
    '''Process Foxy.io events and publish to unified content system'''

    sns = boto3.client('sns')

    try:
        # Parse Foxy.io webhook
        foxy_event = json.loads(event['body'])

        # Get resource type from embedded data
        embedded_resources = foxy_event.get('_embedded', {})
        if not embedded_resources:
            return {'statusCode': 200, 'body': 'No embedded resources'}

        resource_type = list(embedded_resources.keys())[0]

        # Transform different Foxy.io events to unified format
        if resource_type == 'fx:transactions':
            transaction_data = embedded_resources['fx:transactions'][0]

            unified_event = {
                'event_type': 'ecommerce_order_updated',
                'provider': 'foxy',
                'content_id': str(transaction_data.get('id', str(uuid.uuid4()))),
                'content_type': 'order',
                'timestamp': transaction_data.get('transaction_date', datetime.now(timezone.utc).isoformat()),
                'data': {
                    'foxy_transaction': transaction_data,
                    'transaction_total': transaction_data.get('total_order', 0),
                    'currency': transaction_data.get('currency_code', 'USD'),
                    'customer_email': transaction_data.get('customer_email'),
                    'status': transaction_data.get('status'),
                    'items_count': len(transaction_data.get('_embedded', {}).get('fx:items', []))
                }
            }

            # Publish to e-commerce events topic
            topic_arn = os.environ['ECOMMERCE_EVENTS_TOPIC_ARN']

        elif resource_type == 'fx:subscriptions':
            subscription_data = embedded_resources['fx:subscriptions'][0]

            unified_event = {
                'event_type': 'ecommerce_subscription_updated',
                'provider': 'foxy',
                'content_id': str(subscription_data.get('id', str(uuid.uuid4()))),
                'content_type': 'subscription',
                'timestamp': subscription_data.get('date_created', datetime.now(timezone.utc).isoformat()),
                'data': {
                    'foxy_subscription': subscription_data,
                    'frequency': subscription_data.get('frequency'),
                    'next_transaction_date': subscription_data.get('next_transaction_date'),
                    'status': subscription_data.get('is_active'),
                    'customer_email': subscription_data.get('customer_email')
                }
            }

            # Use content events topic for subscription changes
            topic_arn = os.environ['CONTENT_EVENTS_TOPIC_ARN']

        else:
            return {'statusCode': 200, 'body': f'Event type {resource_type} not processed'}

        # Publish unified event
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(unified_event),
            Subject=f"Foxy.io {unified_event['content_type'].title()} Updated: {unified_event['content_id']}"
        )

        return {'statusCode': 200, 'body': f'Processed {resource_type}'}

    except Exception as e:
        print(f"Error processing Foxy.io event: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn,
                "ECOMMERCE_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn  # Use same topic for now
            },
            timeout=Duration.seconds(30)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.foxy_event_processor)

    def _create_foxy_configuration(self) -> None:
        """Create Foxy.io configuration for the client"""

        # Generate Foxy.io configuration for SSG integration
        foxy_config = self._generate_foxy_config()

        # Store configuration in Parameter Store for easy access
        from aws_cdk import aws_ssm as ssm
        self.foxy_config_param = ssm.StringParameter(
            self,
            "FoxyConfig",
            parameter_name=f"/{self.client_config.resource_prefix}/foxy/config",
            string_value=json.dumps(foxy_config),
            description="Foxy.io configuration for SSG integration"
        )

    def _create_foxy_webhook_integration(self) -> None:
        """Create Foxy.io webhook integration for direct mode"""

        # Create API Gateway for Foxy.io webhooks
        webhook_api = apigateway.RestApi(
            self,
            "FoxyWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-foxy-webhooks",
            description="Foxy.io webhook endpoint"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.foxy_webhook_handler)
        )

        # Output webhook URL
        CfnOutput(
            self,
            "FoxyWebhookUrl",
            value=f"{webhook_api.url}webhook",
            description="Webhook URL to configure in Foxy.io admin"
        )

    def _connect_foxy_to_event_system(self) -> None:
        """Connect Foxy.io to event system for event-driven mode"""

        # Create API Gateway for Foxy.io webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "FoxyEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-foxy-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        foxy_resource = event_resource.add_resource("foxy")

        foxy_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.foxy_event_processor)
        )

        # Output webhook URL for Foxy.io configuration
        CfnOutput(
            self,
            "FoxyEventWebhookUrl",
            value=f"{webhook_api.url}events/foxy",
            description="Event webhook URL to configure in Foxy.io admin"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # Additional Foxy.io-specific storage could be added here
        pass

    def _create_foxy_secrets(self) -> None:
        """Create secrets for Foxy.io API credentials"""

        # Foxy.io API credentials
        self.foxy_client_secret = secrets.Secret(
            self,
            "FoxyClientSecret",
            secret_name=f"{self.client_config.resource_prefix}-foxy-client-secret",
            description="Foxy.io OAuth client secret"
        )

        # Foxy.io API key
        self.foxy_api_key_secret = secrets.Secret(
            self,
            "FoxyApiKeySecret",
            secret_name=f"{self.client_config.resource_prefix}-foxy-api-key",
            description="Foxy.io API key for advanced features"
        )

        # Webhook secret
        self.webhook_secret = secrets.Secret(
            self,
            "FoxyWebhookSecret",
            secret_name=f"{self.client_config.resource_prefix}-foxy-webhook-secret",
            description="Secret for Foxy.io webhook signature verification"
        )

    def _create_subscription_management(self) -> None:
        """Create subscription management infrastructure (Foxy.io advanced feature)"""

        # Subscriptions table for managing recurring billing
        self.subscriptions_table = dynamodb.Table(
            self,
            "FoxySubscriptionsTable",
            table_name=f"{self.client_config.resource_prefix}-foxy-subscriptions",
            partition_key=dynamodb.Attribute(
                name="subscription_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )

        # GSI for customer subscription queries
        self.subscriptions_table.add_global_secondary_index(
            index_name="customer-subscriptions",
            partition_key=dynamodb.Attribute(
                name="customer_email",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="subscription_status",
                type=dynamodb.AttributeType.STRING
            )
        )

    def _create_advanced_analytics(self) -> None:
        """Create advanced analytics for Foxy.io integration"""

        # Analytics table for e-commerce insights
        self.analytics_table = dynamodb.Table(
            self,
            "FoxyAnalyticsTable",
            table_name=f"{self.client_config.resource_prefix}-foxy-analytics",
            partition_key=dynamodb.Attribute(
                name="transaction_id",
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

    def _generate_foxy_config(self) -> Dict[str, Any]:
        """Generate Foxy.io configuration for SSG integration"""

        ssg_engine = self.client_config.service_integration.ssg_engine
        ecommerce_settings = self.ecommerce_provider.settings

        # Base Foxy.io configuration
        config = {
            "subdomain": ecommerce_settings.get("subdomain", f"{self.client_config.client_id}-foxy"),
            "currency": ecommerce_settings.get("currency", "USD"),
            "locale": ecommerce_settings.get("locale", "US"),
            "checkoutType": "default_account"
        }

        # Add SSG-specific configurations
        if ssg_engine == "hugo":
            config.update({
                "integration": "hugo",
                "dataFormat": "yaml",
                "templatesPath": "layouts/foxy"
            })
        elif ssg_engine == "eleventy":
            config.update({
                "integration": "eleventy",
                "dataFormat": "json",
                "templatesPath": "_includes/foxy"
            })
        elif ssg_engine == "astro":
            config.update({
                "integration": "astro",
                "componentFormat": "Foxy{Component}",
                "componentsPath": "src/components/foxy"
            })
        elif ssg_engine == "gatsby":
            config.update({
                "integration": "gatsby",
                "componentFormat": "Foxy{Component}",
                "componentsPath": "src/components/foxy"
            })

        return config

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
            "IntegrationMode",
            value=self.integration_mode.value,
            description="E-commerce integration mode (direct or event_driven)"
        )

        CfnOutput(
            self,
            "EcommerceProvider",
            value="foxy",
            description="E-commerce provider"
        )

        CfnOutput(
            self,
            "SSGEngine",
            value=self.client_config.service_integration.ssg_engine,
            description="SSG engine"
        )

    def _create_custom_infrastructure(self) -> None:
        """Required implementation from BaseSSGStack"""
        # Infrastructure creation is handled by mode-specific methods
        pass

    def get_monthly_cost_estimate(self) -> Dict[str, Any]:
        """Get monthly cost estimate for Foxy.io e-commerce tier"""

        base_costs = {
            "foxy_base_fee": 20,  # Base monthly fee
            "foxy_transaction_fees": "1.5% of sales",  # Transaction fees
            "aws_hosting": 75,  # Base hosting costs
            "cloudfront": 20,  # CDN costs
            "codebuild": 15,  # Build minutes
            "advanced_features": 10,  # Subscription management, analytics
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 10,  # Event messaging
                "lambda_executions": 10,  # Event processing
                "dynamodb": 15,  # Subscription and analytics storage
            })

        monthly_total = sum(v for v in base_costs.values() if isinstance(v, (int, float)))

        return {
            "monthly_fixed_costs": monthly_total,
            "transaction_fees": "1.5% of sales",
            "total_description": f"${monthly_total}/month + 1.5% of sales",
            "break_even_comparison": f"Better than Shopify Plus above ${monthly_total * 20} monthly sales",
            "competitive_advantage": "Advanced customization with lower transaction fees than Shopify"
        }

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for Foxy.io e-commerce tier"""

        score = 0
        reasons = []

        # Advanced e-commerce needs (major factor for Foxy.io)
        if requirements.get("advanced_ecommerce", False):
            score += 35
            reasons.append("Advanced e-commerce features and customization")

        # Subscription business model
        if requirements.get("subscription_business", False):
            score += 30
            reasons.append("Excellent subscription management capabilities")

        # Custom checkout requirements
        if requirements.get("custom_checkout", False):
            score += 25
            reasons.append("Sophisticated checkout flow customization")

        # International/multi-currency
        if requirements.get("multi_currency", False):
            score += 20
            reasons.append("Multi-currency and international shipping support")

        # Transaction volume considerations
        expected_monthly_sales = requirements.get("expected_monthly_sales", 5000)
        if expected_monthly_sales >= 10000:  # $150+ in fees vs higher-tier alternatives
            score += 15
            reasons.append("Cost-effective for high-volume sales")
        elif expected_monthly_sales >= 5000:
            score += 10
            reasons.append("Good value for medium-volume sales")

        # Technical sophistication
        if requirements.get("technical_team", False):
            score += 15
            reasons.append("Developer-friendly with extensive customization options")

        # Budget considerations
        budget = requirements.get("monthly_budget", 100)
        if budget >= 150:
            score += 10
            reasons.append("Budget supports advanced e-commerce features")
        elif budget >= 100:
            score += 5
            reasons.append("Budget covers basic Foxy.io implementation")
        else:
            score -= 10
            reasons.append("Budget may be tight for Foxy.io features")

        # Simple e-commerce penalty
        if requirements.get("simple_ecommerce", False):
            score -= 15
            reasons.append("May be overkill for simple e-commerce needs")

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
            "integration_mode_recommendation": "event_driven" if requirements.get("complex_business_logic") else "direct"
        }