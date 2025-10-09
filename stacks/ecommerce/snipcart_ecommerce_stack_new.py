"""
Snipcart E-commerce Tier Stack

Updated Snipcart implementation with optional event-driven integration support:
- Direct Mode: Snipcart webhooks → build pipeline (simple, familiar)
- Event-Driven Mode: Snipcart events → SNS → unified content system (composition-ready)

Snipcart E-commerce Features:
- Simple setup with HTML data attributes
- No monthly fees - 2% transaction fee only
- Built-in payment processing (Stripe, PayPal, etc.)
- Inventory management and customer portal
- Discount codes and tax calculations
- Perfect for small to medium stores

Target Market:
- Small businesses wanting simple e-commerce
- Developers preferring lightweight solutions
- Budget-conscious clients (no monthly fees)
- Stores with low to medium transaction volumes
- Sites wanting to add e-commerce to existing content

Pricing:
- Snipcart: 2% transaction fee (no monthly cost!)
- AWS Hosting: $50-75/month
- Total Monthly: $50-75/month + 2% of sales
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
    aws_ssm as ssm,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from models.service_config import ClientServiceConfig, IntegrationMode
from shared.composition.integration_layer import EventDrivenIntegrationLayer
from shared.providers.ecommerce.factory import EcommerceProviderFactory


class SnipcartEcommerceStack(BaseSSGStack):
    """
    Snipcart E-commerce Tier Stack Implementation

    Supports both integration modes:
    - Direct: Snipcart webhooks → CodeBuild → S3/CloudFront (simple, budget-friendly)
    - Event-Driven: Snipcart events → SNS → unified content system (composition-ready)

    The most cost-effective e-commerce solution with no monthly fees!
    """

    # Supported SSG engines for Snipcart
    SUPPORTED_SSG_ENGINES = {
        "hugo": {
            "compatibility": "excellent",
            "setup_complexity": "easy",
            "features": ["fast_builds", "simple_integration", "snipcart_partials"]
        },
        "eleventy": {
            "compatibility": "excellent",
            "setup_complexity": "easy",
            "features": ["flexible_templating", "snipcart_filters", "javascript_config"]
        },
        "astro": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["component_islands", "snipcart_components", "modern_tooling"]
        },
        "gatsby": {
            "compatibility": "good",
            "setup_complexity": "advanced",
            "features": ["react_components", "graphql", "snipcart_plugins"]
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

        # Validate Snipcart e-commerce configuration
        self._validate_snipcart_ecommerce_config()

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

    def _validate_snipcart_ecommerce_config(self) -> None:
        """Validate Snipcart e-commerce configuration"""
        service_config = self.client_config.service_integration

        if not service_config.ecommerce_config:
            raise ValueError("Snipcart e-commerce tier requires ecommerce_config")

        if service_config.ecommerce_config.provider != "snipcart":
            raise ValueError(f"Expected Snipcart provider, got {service_config.ecommerce_config.provider}")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"Snipcart supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_ecommerce_provider(self):
        """Initialize e-commerce provider instance"""
        ecommerce_config = self.client_config.service_integration.ecommerce_config
        return EcommerceProviderFactory.create_provider(
            ecommerce_config.provider,
            ecommerce_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Snipcart webhook → CodeBuild pipeline
        self.snipcart_webhook_handler = self._create_snipcart_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # Snipcart configuration
        self._create_snipcart_configuration()

        # Snipcart webhook integration
        self._create_snipcart_webhook_integration()

        print(f"✅ Created Snipcart direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Snipcart events → Integration Layer → Unified Content
        self._create_event_driven_ecommerce_integration()

        # Snipcart configuration (same as direct mode)
        self._create_snipcart_configuration()

        # Connect to event system
        self._connect_snipcart_to_event_system()

        print(f"✅ Created Snipcart event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_snipcart_secrets()
        self._create_product_catalog_storage()

    def _create_snipcart_webhook_handler(self) -> lambda_.Function:
        """Create Snipcart webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "SnipcartWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="snipcart_webhook.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import hmac
import hashlib
import os

def main(event, context):
    '''Handle Snipcart webhook for direct mode'''

    try:
        # Verify webhook signature
        if not verify_snipcart_signature(event):
            return {'statusCode': 401, 'body': 'Unauthorized'}

        # Parse webhook payload
        body = json.loads(event['body'])

        # Get event type from Snipcart
        event_type = body.get('eventName', '')

        # Trigger build for relevant events (order completed, product updated, etc.)
        if event_type in ['order.completed', 'order.status.changed']:
            codebuild = boto3.client('codebuild')

            order_token = body.get('content', {}).get('token', '')
            order_total = body.get('content', {}).get('finalGrandTotal', 0)

            response = codebuild.start_build(
                projectName=os.environ['BUILD_PROJECT_NAME'],
                environmentVariablesOverride=[
                    {
                        'name': 'SNIPCART_EVENT_TYPE',
                        'value': event_type
                    },
                    {
                        'name': 'SNIPCART_ORDER_TOKEN',
                        'value': order_token
                    }
                ]
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Build triggered',
                    'buildId': response['build']['id'],
                    'eventType': event_type,
                    'orderToken': order_token
                })
            }

        return {'statusCode': 200, 'body': f'Event {event_type} processed'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def verify_snipcart_signature(event):
    '''Verify Snipcart webhook signature'''
    webhook_secret = os.environ.get('SNIPCART_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return True  # Skip verification if no secret set

    signature = event['headers'].get('x-snipcart-requesttoken', '')
    body = event['body']

    # Snipcart uses custom signature format
    expected = hmac.new(
        webhook_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-snipcart-build",
                "SNIPCART_WEBHOOK_SECRET": "placeholder"  # Should use Secrets Manager
            },
            timeout=Duration.seconds(30)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        # Get Snipcart settings for environment variables
        snipcart_settings = self.ecommerce_provider.settings

        return codebuild.Project(
            self,
            "SnipcartDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-snipcart-build",
            source=codebuild.Source.no_source(),  # Snipcart works with existing content
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    "SNIPCART_PUBLIC_API_KEY": codebuild.BuildEnvironmentVariable(
                        value=snipcart_settings.get("public_api_key", "placeholder")
                    ),
                    "SNIPCART_CURRENCY": codebuild.BuildEnvironmentVariable(
                        value=snipcart_settings.get("currency", "USD")
                    )
                }
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_ecommerce_integration(self) -> None:
        """Create event-driven e-commerce integration"""

        # Snipcart Event Processor - transforms Snipcart webhooks to unified content events
        self.snipcart_event_processor = lambda_.Function(
            self,
            "SnipcartEventProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="snipcart_event_processor.main",
            code=lambda_.Code.from_inline("""
import json
import boto3
import os
import uuid
from datetime import datetime, timezone

def main(event, context):
    '''Process Snipcart events and publish to unified content system'''

    sns = boto3.client('sns')

    try:
        # Parse Snipcart webhook
        snipcart_event = json.loads(event['body'])
        event_type = snipcart_event.get('eventName', '')

        # Transform different Snipcart events to unified format
        if event_type in ['order.completed', 'order.status.changed']:
            order_data = snipcart_event.get('content', {})

            unified_event = {
                'event_type': 'ecommerce_order_updated',
                'provider': 'snipcart',
                'content_id': order_data.get('token', str(uuid.uuid4())),
                'content_type': 'order',
                'timestamp': order_data.get('creationDate', datetime.now(timezone.utc).isoformat()),
                'data': {
                    'snipcart_order': order_data,
                    'order_status': order_data.get('status'),
                    'total_amount': order_data.get('finalGrandTotal', 0),
                    'currency': order_data.get('currency', 'USD'),
                    'customer_email': order_data.get('email'),
                    'items_count': len(order_data.get('items', []))
                }
            }

            # Publish to e-commerce events topic
            topic_arn = os.environ['ECOMMERCE_EVENTS_TOPIC_ARN']

        elif event_type in ['product.created', 'product.updated']:
            # Handle product events (if Snipcart adds this feature)
            product_data = snipcart_event.get('content', {})

            unified_event = {
                'event_type': 'ecommerce_product_updated',
                'provider': 'snipcart',
                'content_id': product_data.get('id', str(uuid.uuid4())),
                'content_type': 'product',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'snipcart_product': product_data,
                    'product_name': product_data.get('name'),
                    'price': product_data.get('price', 0),
                    'inventory': product_data.get('stock', 0)
                }
            }

            # Use content events topic for product changes
            topic_arn = os.environ['CONTENT_EVENTS_TOPIC_ARN']

        else:
            return {'statusCode': 200, 'body': f'Event type {event_type} not processed'}

        # Publish unified event
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(unified_event),
            Subject=f"Snipcart {unified_event['content_type'].title()} Updated: {unified_event['content_id']}"
        )

        return {'statusCode': 200, 'body': f'Processed {event_type}'}

    except Exception as e:
        print(f"Error processing Snipcart event: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn,
                "ECOMMERCE_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn  # Use same topic for now
            },
            timeout=Duration.seconds(30)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.snipcart_event_processor)

    def _create_snipcart_configuration(self) -> None:
        """Create Snipcart configuration for the client"""

        # Generate Snipcart configuration for SSG integration
        snipcart_config = self._generate_snipcart_config()

        # Store configuration in Parameter Store for easy access
        self.snipcart_config_param = ssm.StringParameter(
            self,
            "SnipcartConfig",
            parameter_name=f"/{self.client_config.resource_prefix}/snipcart/config",
            string_value=json.dumps(snipcart_config),
            description="Snipcart configuration for SSG integration"
        )

    def _create_snipcart_webhook_integration(self) -> None:
        """Create Snipcart webhook integration for direct mode"""

        # Create API Gateway for Snipcart webhooks
        webhook_api = apigateway.RestApi(
            self,
            "SnipcartWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-snipcart-webhooks",
            description="Snipcart webhook endpoint"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.snipcart_webhook_handler)
        )

        # Output webhook URL
        CfnOutput(
            self,
            "SnipcartWebhookUrl",
            value=f"{webhook_api.url}webhook",
            description="Webhook URL to configure in Snipcart dashboard"
        )

    def _connect_snipcart_to_event_system(self) -> None:
        """Connect Snipcart to event system for event-driven mode"""

        # Create API Gateway for Snipcart webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "SnipcartEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-snipcart-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        snipcart_resource = event_resource.add_resource("snipcart")

        snipcart_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.snipcart_event_processor)
        )

        # Output webhook URL for Snipcart configuration
        CfnOutput(
            self,
            "SnipcartEventWebhookUrl",
            value=f"{webhook_api.url}events/snipcart",
            description="Event webhook URL to configure in Snipcart dashboard"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # Additional Snipcart-specific storage could be added here
        pass

    def _create_snipcart_secrets(self) -> None:
        """Create secrets for Snipcart API credentials"""

        # Snipcart public API key (can be exposed in frontend)
        self.public_api_key_param = ssm.StringParameter(
            self,
            "SnipcartPublicApiKey",
            parameter_name=f"/{self.client_config.resource_prefix}/snipcart/public-api-key",
            string_value="your-snipcart-public-api-key-here",
            description="Snipcart public API key (safe for frontend use)"
        )

        # Snipcart secret API key (server-side only)
        self.secret_api_key_secret = secrets.Secret(
            self,
            "SnipcartSecretApiKey",
            secret_name=f"{self.client_config.resource_prefix}-snipcart-secret-api-key",
            description="Snipcart secret API key for server-side operations"
        )

        # Webhook secret
        self.webhook_secret = secrets.Secret(
            self,
            "SnipcartWebhookSecret",
            secret_name=f"{self.client_config.resource_prefix}-snipcart-webhook-secret",
            description="Secret for Snipcart webhook signature verification"
        )

    def _create_product_catalog_storage(self) -> None:
        """Create storage for product catalog (if using dynamic products)"""

        # Optional DynamoDB table for product catalog
        # (Snipcart can work with static HTML or dynamic API)
        self.product_catalog_table = dynamodb.Table(
            self,
            "SnipcartProductCatalog",
            table_name=f"{self.client_config.resource_prefix}-snipcart-products",
            partition_key=dynamodb.Attribute(
                name="product_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

    def _generate_snipcart_config(self) -> Dict[str, Any]:
        """Generate Snipcart configuration for SSG integration"""

        ssg_engine = self.client_config.service_integration.ssg_engine
        ecommerce_settings = self.ecommerce_provider.settings

        # Base Snipcart configuration
        config = {
            "publicApiKey": ecommerce_settings.get("public_api_key", "your-public-api-key"),
            "currency": ecommerce_settings.get("currency", "USD"),
            "templatesUrl": f"https://{self.client_config.domain}/snipcart-templates"
        }

        # Add SSG-specific configurations
        if ssg_engine == "hugo":
            config.update({
                "integration": "hugo",
                "productAttributeFormat": "data-item-{attribute}",
                "templatesPath": "layouts/snipcart"
            })
        elif ssg_engine == "eleventy":
            config.update({
                "integration": "eleventy",
                "productAttributeFormat": "data-item-{attribute}",
                "templatesPath": "_includes/snipcart"
            })
        elif ssg_engine == "astro":
            config.update({
                "integration": "astro",
                "componentFormat": "Snipcart{Component}",
                "componentsPath": "src/components/snipcart"
            })
        elif ssg_engine == "gatsby":
            config.update({
                "integration": "gatsby",
                "componentFormat": "Snipcart{Component}",
                "componentsPath": "src/components/snipcart"
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
            value="snipcart",
            description="E-commerce provider"
        )

        CfnOutput(
            self,
            "SSGEngine",
            value=self.client_config.service_integration.ssg_engine,
            description="SSG engine"
        )

        CfnOutput(
            self,
            "SnipcartPublicApiKeyParam",
            value=self.public_api_key_param.parameter_name,
            description="Parameter Store path for Snipcart public API key"
        )

        # Mode-specific outputs
        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            CfnOutput(
                self,
                "ContentEventsTopicArn",
                value=self.integration_layer.content_events_topic.topic_arn,
                description="SNS topic for content/e-commerce events"
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
                description="Supports composition with CMS providers"
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
        """Get monthly cost estimate for Snipcart e-commerce tier"""

        base_costs = {
            "snipcart_transaction_fees": "2% of sales",  # No monthly fees!
            "aws_hosting": 50,  # Base hosting costs
            "cloudfront": 15,  # CDN costs
            "codebuild": 10,  # Build minutes
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 5,  # Event messaging
                "lambda_executions": 5,  # Event processing
                "dynamodb": 10,  # Product catalog storage
            })

        monthly_total = sum(v for v in base_costs.values() if isinstance(v, (int, float)))

        return {
            "monthly_fixed_costs": monthly_total,
            "transaction_fees": "2% of sales",
            "total_description": f"${monthly_total}/month + 2% of sales",
            "break_even_sales": f"${monthly_total * 50} monthly sales to equal $20/month CMS",
            "competitive_advantage": "No monthly fees - only pay when you sell!"
        }

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for Snipcart e-commerce tier"""

        score = 0
        reasons = []

        # Budget consciousness (major factor for Snipcart)
        if requirements.get("budget_conscious", False):
            score += 35
            reasons.append("No monthly fees - only 2% per transaction")

        # Simple e-commerce needs
        if requirements.get("simple_ecommerce", False):
            score += 25
            reasons.append("Perfect for straightforward product sales")

        # Low to medium sales volume
        expected_monthly_sales = requirements.get("expected_monthly_sales", 1000)
        if expected_monthly_sales <= 2500:  # $50 in fees vs $20-50 monthly CMS
            score += 20
            reasons.append("Cost-effective for sales under $2,500/month")
        elif expected_monthly_sales <= 5000:
            score += 10
            reasons.append("Competitive for sales under $5,000/month")
        else:
            score -= 5
            reasons.append("Transaction fees may exceed flat-rate alternatives at high volume")

        # Technical comfort (Snipcart is developer-friendly)
        if requirements.get("technical_team", False):
            score += 15
            reasons.append("Developer-friendly with simple HTML integration")

        # Existing static site
        if requirements.get("has_existing_site", False):
            score += 15
            reasons.append("Easy to add to existing static sites")

        # Complex e-commerce features
        if requirements.get("advanced_ecommerce", False):
            score -= 10
            reasons.append("May need more advanced e-commerce platform")

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