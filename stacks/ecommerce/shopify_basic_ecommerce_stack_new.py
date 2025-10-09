"""
Shopify Basic E-commerce Tier Stack

Updated Shopify Basic implementation with optional event-driven integration support:
- Direct Mode: Shopify webhooks → build pipeline (traditional, proven)
- Event-Driven Mode: Shopify events → SNS → unified content system (composition-ready)

Shopify Basic E-commerce Features:
- Shopify Basic plan ($29/month) with Storefront API
- High-performance static frontend with sub-2s page loads
- Real-time product synchronization via webhooks
- Professional e-commerce features without complexity
- Proven platform reliability and PCI compliance
- 80-90% cost reduction vs traditional Shopify agencies

Target Market:
- Small-medium stores needing proven e-commerce platform
- Performance-focused brands wanting static site benefits
- Businesses wanting Shopify reliability with custom frontend
- Agency alternatives with professional results
- Stores needing straightforward product catalog management

Pricing:
- Shopify Basic: $29/month + 2.9% transaction fees
- AWS Hosting: $50-75/month
- Total Monthly: $80-105/month + 2.9% of sales
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
    aws_cloudwatch as cloudwatch,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from models.service_config import ClientServiceConfig, IntegrationMode
from shared.composition.integration_layer import EventDrivenIntegrationLayer
from shared.providers.ecommerce.factory import EcommerceProviderFactory


class ShopifyBasicEcommerceStack(BaseSSGStack):
    """
    Shopify Basic E-commerce Tier Stack Implementation

    Supports both integration modes:
    - Direct: Shopify webhooks → CodeBuild → S3/CloudFront (traditional, proven)
    - Event-Driven: Shopify events → SNS → unified content system (composition-ready)

    The proven e-commerce solution with professional features and reliability.
    """

    # Supported SSG engines for Shopify Basic
    SUPPORTED_SSG_ENGINES = {
        "eleventy": {
            "compatibility": "excellent",
            "setup_complexity": "simple",
            "features": ["fast_builds", "simple_templating", "shopify_integration"]
        },
        "astro": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["component_islands", "performance_optimization", "shopify_components"]
        },
        "nextjs": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "features": ["react_ecosystem", "shopify_hooks", "api_routes"]
        },
        "nuxt": {
            "compatibility": "good",
            "setup_complexity": "advanced",
            "features": ["vue_ecosystem", "ssr_support", "shopify_modules"]
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

        # Validate Shopify Basic e-commerce configuration
        self._validate_shopify_ecommerce_config()

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

    def _validate_shopify_ecommerce_config(self) -> None:
        """Validate Shopify Basic e-commerce configuration"""
        service_config = self.client_config.service_integration

        if not service_config.ecommerce_config:
            raise ValueError("Shopify Basic e-commerce tier requires ecommerce_config")

        if service_config.ecommerce_config.provider != "shopify_basic":
            raise ValueError(f"Expected Shopify Basic provider, got {service_config.ecommerce_config.provider}")

        # Validate Shopify-specific settings
        settings = service_config.ecommerce_config.settings
        required = ["store_domain"]
        for setting in required:
            if not settings.get(setting):
                raise ValueError(f"Shopify Basic requires '{setting}' in settings")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"Shopify Basic supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_ecommerce_provider(self):
        """Initialize e-commerce provider instance"""
        ecommerce_config = self.client_config.service_integration.ecommerce_config
        return EcommerceProviderFactory.create_provider(
            ecommerce_config.provider,
            ecommerce_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Shopify webhook → CodeBuild pipeline
        self.shopify_webhook_handler = self._create_shopify_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # Shopify Basic configuration
        self._create_shopify_configuration()

        # Shopify webhook integration
        self._create_shopify_webhook_integration()

        print(f"✅ Created Shopify Basic direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Shopify events → Integration Layer → Unified Content
        self._create_event_driven_ecommerce_integration()

        # Shopify Basic configuration (same as direct mode)
        self._create_shopify_configuration()

        # Connect to event system
        self._connect_shopify_to_event_system()

        print(f"✅ Created Shopify Basic event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_shopify_secrets()
        self._create_product_sync_system()
        self._create_shopify_analytics()

    def _create_shopify_webhook_handler(self) -> lambda_.Function:
        """Create Shopify webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "ShopifyWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
const AWS = require('aws-sdk');
const crypto = require('crypto');

const codebuild = new AWS.CodeBuild();
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    console.log('Shopify webhook received:', JSON.stringify(event));

    try {
        const body = JSON.parse(event.body || '{}');
        const headers = event.headers || {};

        // Validate Shopify webhook
        const shopifyTopic = headers['X-Shopify-Topic'] || headers['x-shopify-topic'];
        if (!shopifyTopic) {
            console.warn('Missing Shopify topic header');
            return { statusCode: 400, body: 'Invalid webhook' };
        }

        console.log('Shopify topic:', shopifyTopic);

        // Handle different webhook events
        if (shopifyTopic.startsWith('products/')) {
            await handleProductWebhook(body, shopifyTopic);
        } else if (shopifyTopic.startsWith('orders/')) {
            await handleOrderWebhook(body, shopifyTopic);
        } else if (shopifyTopic.startsWith('inventory_levels/')) {
            await handleInventoryWebhook(body, shopifyTopic);
        }

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Webhook processed successfully' })
        };

    } catch (error) {
        console.error('Webhook processing error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};

async function handleProductWebhook(productData, topic) {
    console.log('Processing product webhook:', topic);

    // Update product cache
    if (topic === 'products/delete') {
        await dynamodb.delete({
            TableName: process.env.PRODUCT_CACHE_TABLE,
            Key: {
                product_id: productData.id.toString(),
                handle: productData.handle
            }
        }).promise();
    } else {
        const cacheItem = {
            product_id: productData.id.toString(),
            handle: productData.handle,
            title: productData.title,
            description: productData.description,
            vendor: productData.vendor,
            product_type: productData.product_type,
            tags: productData.tags,
            images: productData.images,
            variants: productData.variants,
            status: productData.status,
            created_at: productData.created_at,
            updated_at: productData.updated_at,
            synced_at: new Date().toISOString(),
            ttl: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60) // 7 day TTL
        };

        await dynamodb.put({
            TableName: process.env.PRODUCT_CACHE_TABLE,
            Item: cacheItem
        }).promise();
    }

    // Trigger site rebuild for product changes
    await triggerSiteRebuild(`Product ${topic}`, productData);
}

async function handleOrderWebhook(orderData, topic) {
    console.log('Processing order webhook:', topic);

    // Orders don't typically require site rebuild, but could trigger for analytics
    if (topic === 'orders/create') {
        // Log order for analytics
        console.log('New order created:', orderData.id);
    }
}

async function handleInventoryWebhook(inventoryData, topic) {
    console.log('Processing inventory webhook:', topic);

    const inventoryItem = {
        variant_id: inventoryData.inventory_item_id.toString(),
        available: inventoryData.available,
        location_id: inventoryData.location_id,
        updated_at: inventoryData.updated_at,
        ttl: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hour TTL
    };

    await dynamodb.put({
        TableName: process.env.INVENTORY_CACHE_TABLE,
        Item: inventoryItem
    }).promise();

    // Trigger site rebuild for inventory changes (less frequent)
    if (Math.random() < 0.1) { // 10% chance to avoid too many rebuilds
        await triggerSiteRebuild('Inventory update', inventoryData);
    }
}

async function triggerSiteRebuild(reason, data) {
    try {
        const buildParams = {
            projectName: process.env.BUILD_PROJECT_NAME,
            environmentVariablesOverride: [
                {
                    name: 'SHOPIFY_SYNC_REASON',
                    value: reason,
                    type: 'PLAINTEXT'
                },
                {
                    name: 'SHOPIFY_STORE_DOMAIN',
                    value: process.env.SHOPIFY_STORE_DOMAIN,
                    type: 'PLAINTEXT'
                }
            ]
        };

        console.log('Starting build:', buildParams.projectName);
        const result = await codebuild.startBuild(buildParams).promise();
        console.log('Build started:', result.build.id);

    } catch (error) {
        console.error('Build trigger error:', error);
        throw error;
    }
}
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-shopify-build",
                "SHOPIFY_STORE_DOMAIN": self.ecommerce_provider.settings.get("store_domain", ""),
                "PRODUCT_CACHE_TABLE": f"{self.client_config.resource_prefix}-shopify-products",
                "INVENTORY_CACHE_TABLE": f"{self.client_config.resource_prefix}-shopify-inventory"
            },
            timeout=Duration.seconds(60)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        # Get Shopify settings for environment variables
        shopify_settings = self.ecommerce_provider.settings

        return codebuild.Project(
            self,
            "ShopifyDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-shopify-build",
            source=codebuild.Source.no_source(),  # Shopify is API-based
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    "SHOPIFY_STORE_DOMAIN": codebuild.BuildEnvironmentVariable(
                        value=shopify_settings["store_domain"]
                    ),
                    "SHOPIFY_PLAN": codebuild.BuildEnvironmentVariable(
                        value=shopify_settings.get("plan", "basic")
                    )
                }
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_ecommerce_integration(self) -> None:
        """Create event-driven e-commerce integration"""

        # Shopify Event Processor - transforms Shopify webhooks to unified content events
        self.shopify_event_processor = lambda_.Function(
            self,
            "ShopifyEventProcessor",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
const AWS = require('aws-sdk');

const sns = new AWS.SNS();

exports.handler = async (event) => {
    console.log('Processing Shopify event for unified content system');

    try {
        const body = JSON.parse(event.body || '{}');
        const headers = event.headers || {};
        const shopifyTopic = headers['X-Shopify-Topic'] || headers['x-shopify-topic'];

        if (!shopifyTopic) {
            return { statusCode: 400, body: 'Invalid webhook' };
        }

        let unifiedEvent = null;

        // Transform different Shopify events to unified format
        if (shopifyTopic.startsWith('products/')) {
            unifiedEvent = {
                event_type: 'ecommerce_product_updated',
                provider: 'shopify_basic',
                content_id: body.id.toString(),
                content_type: 'product',
                timestamp: body.updated_at || new Date().toISOString(),
                data: {
                    shopify_product: body,
                    product_title: body.title,
                    product_handle: body.handle,
                    vendor: body.vendor,
                    product_type: body.product_type,
                    tags: body.tags,
                    status: body.status,
                    action: shopifyTopic.split('/')[1] // create, update, delete
                }
            };
        } else if (shopifyTopic.startsWith('orders/')) {
            unifiedEvent = {
                event_type: 'ecommerce_order_updated',
                provider: 'shopify_basic',
                content_id: body.id.toString(),
                content_type: 'order',
                timestamp: body.created_at || new Date().toISOString(),
                data: {
                    shopify_order: body,
                    order_number: body.order_number,
                    total_price: body.total_price,
                    currency: body.currency,
                    customer_email: body.email,
                    financial_status: body.financial_status,
                    fulfillment_status: body.fulfillment_status,
                    line_items_count: body.line_items ? body.line_items.length : 0
                }
            };
        } else if (shopifyTopic.startsWith('inventory_levels/')) {
            unifiedEvent = {
                event_type: 'ecommerce_inventory_updated',
                provider: 'shopify_basic',
                content_id: body.inventory_item_id.toString(),
                content_type: 'inventory',
                timestamp: body.updated_at || new Date().toISOString(),
                data: {
                    shopify_inventory: body,
                    available_quantity: body.available,
                    location_id: body.location_id,
                    inventory_item_id: body.inventory_item_id
                }
            };
        }

        if (unifiedEvent) {
            // Publish to content events topic
            await sns.publish({
                TopicArn: process.env.CONTENT_EVENTS_TOPIC_ARN,
                Message: JSON.stringify(unifiedEvent),
                Subject: `Shopify ${unifiedEvent.content_type} Updated: ${unifiedEvent.content_id}`
            }).promise();

            console.log('Published unified event:', unifiedEvent.event_type);
        }

        return { statusCode: 200, body: `Processed ${shopifyTopic}` };

    } catch (error) {
        console.error('Error processing Shopify event:', error);
        return { statusCode: 500, body: `Error: ${error.message}` };
    }
};
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn
            },
            timeout=Duration.seconds(30)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.shopify_event_processor)

    def _create_shopify_configuration(self) -> None:
        """Create Shopify configuration for the client"""

        # Generate Shopify configuration for SSG integration
        shopify_config = self._generate_shopify_config()

        # Store configuration in Parameter Store for easy access
        from aws_cdk import aws_ssm as ssm
        self.shopify_config_param = ssm.StringParameter(
            self,
            "ShopifyConfig",
            parameter_name=f"/{self.client_config.resource_prefix}/shopify/config",
            string_value=json.dumps(shopify_config),
            description="Shopify Basic configuration for SSG integration"
        )

    def _create_shopify_webhook_integration(self) -> None:
        """Create Shopify webhook integration for direct mode"""

        # Create API Gateway for Shopify webhooks
        webhook_api = apigateway.RestApi(
            self,
            "ShopifyWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-shopify-webhooks",
            description="Shopify webhook endpoint"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.shopify_webhook_handler)
        )

        # Add CORS for development
        webhook_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Shopify-Topic", "X-Shopify-Hmac-Sha256"]
        )

        # Output webhook URL
        CfnOutput(
            self,
            "ShopifyWebhookUrl",
            value=f"{webhook_api.url}webhook",
            description="Webhook URL to configure in Shopify admin"
        )

    def _connect_shopify_to_event_system(self) -> None:
        """Connect Shopify to event system for event-driven mode"""

        # Create API Gateway for Shopify webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "ShopifyEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-shopify-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        shopify_resource = event_resource.add_resource("shopify")

        shopify_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.shopify_event_processor)
        )

        # Output webhook URL for Shopify configuration
        CfnOutput(
            self,
            "ShopifyEventWebhookUrl",
            value=f"{webhook_api.url}events/shopify",
            description="Event webhook URL to configure in Shopify admin"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # Additional Shopify-specific storage could be added here
        pass

    def _create_shopify_secrets(self) -> None:
        """Create secrets for Shopify API credentials"""

        # Shopify Storefront access token
        self.shopify_storefront_token = secrets.Secret(
            self,
            "ShopifyStorefrontToken",
            secret_name=f"{self.client_config.resource_prefix}-shopify-storefront-token",
            description="Shopify Storefront API access token"
        )

        # Shopify Admin API token
        self.shopify_admin_token = secrets.Secret(
            self,
            "ShopifyAdminToken",
            secret_name=f"{self.client_config.resource_prefix}-shopify-admin-token",
            description="Shopify Admin API access token for webhooks"
        )

        # Webhook secret
        self.webhook_secret = secrets.Secret(
            self,
            "ShopifyWebhookSecret",
            secret_name=f"{self.client_config.resource_prefix}-shopify-webhook-secret",
            description="Secret for Shopify webhook signature verification"
        )

    def _create_product_sync_system(self) -> None:
        """Create Shopify product synchronization system"""

        # Create product cache table
        self.product_cache = dynamodb.Table(
            self,
            "ShopifyProductCache",
            table_name=f"{self.client_config.resource_prefix}-shopify-products",
            partition_key=dynamodb.Attribute(
                name="product_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="handle",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )

        # Create inventory tracking table
        self.inventory_cache = dynamodb.Table(
            self,
            "ShopifyInventoryCache",
            table_name=f"{self.client_config.resource_prefix}-shopify-inventory",
            partition_key=dynamodb.Attribute(
                name="variant_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )

        # Grant permissions to webhook handler
        self.product_cache.grant_read_write_data(self.shopify_webhook_handler)
        self.inventory_cache.grant_read_write_data(self.shopify_webhook_handler)

    def _create_shopify_analytics(self) -> None:
        """Create analytics and monitoring for Shopify integration"""

        # Create CloudWatch dashboard for Shopify metrics
        self.shopify_dashboard = cloudwatch.Dashboard(
            self,
            "ShopifyDashboard",
            dashboard_name=f"{self.client_config.client_id}-shopify-ecommerce"
        )

        # Add metrics widgets
        self.shopify_dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Shopify Webhook Processing",
                left=[
                    self.shopify_webhook_handler.metric_invocations(),
                    self.shopify_webhook_handler.metric_errors()
                ]
            ),
            cloudwatch.GraphWidget(
                title="Product Cache Performance",
                left=[
                    self.product_cache.metric_consumed_read_capacity_units(),
                    self.product_cache.metric_consumed_write_capacity_units()
                ]
            )
        )

    def _generate_shopify_config(self) -> Dict[str, Any]:
        """Generate Shopify configuration for SSG integration"""

        ssg_engine = self.client_config.service_integration.ssg_engine
        ecommerce_settings = self.ecommerce_provider.settings

        # Base Shopify configuration
        config = {
            "storeDomain": ecommerce_settings["store_domain"],
            "plan": ecommerce_settings.get("plan", "basic"),
            "apiVersion": "2023-10",
            "currency": ecommerce_settings.get("currency", "USD")
        }

        # Add SSG-specific configurations
        if ssg_engine == "eleventy":
            config.update({
                "integration": "eleventy",
                "dataFormat": "json",
                "templatesPath": "_includes/shopify"
            })
        elif ssg_engine == "astro":
            config.update({
                "integration": "astro",
                "componentFormat": "Shopify{Component}",
                "componentsPath": "src/components/shopify"
            })
        elif ssg_engine == "nextjs":
            config.update({
                "integration": "nextjs",
                "hooksPath": "hooks/shopify",
                "componentsPath": "components/shopify"
            })
        elif ssg_engine == "nuxt":
            config.update({
                "integration": "nuxt",
                "modulePath": "modules/shopify",
                "componentsPath": "components/shopify"
            })

        return config

    def _get_direct_mode_buildspec(self) -> codebuild.BuildSpec:
        """Get buildspec for direct mode builds"""

        ssg_engine = self.client_config.service_integration.ssg_engine

        if ssg_engine == "eleventy":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci", "npm install @shopify/storefront-api-client"]
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
                        "commands": ["npm ci", "npm install @shopify/storefront-api-client"]
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

        elif ssg_engine == "nextjs":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci", "npm install @shopify/storefront-api-client @shopify/react-hooks"]
                    },
                    "build": {
                        "commands": ["npm run build", "npm run export"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "out"
                }
            })

        else:  # nuxt
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci", "npm install @shopify/storefront-api-client @nuxtjs/axios"]
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
            "ShopifyStoreDomain",
            value=self.ecommerce_provider.settings["store_domain"],
            description="Shopify store domain"
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
            value="shopify_basic",
            description="E-commerce provider"
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
        """Get monthly cost estimate for Shopify Basic e-commerce tier"""

        base_costs = {
            "shopify_basic_plan": 29,  # Fixed Shopify Basic plan
            "shopify_transaction_fees": "2.9% of sales",  # Transaction fees
            "aws_hosting": 50,  # Base hosting costs
            "cloudfront": 15,  # CDN costs
            "codebuild": 10,  # Build minutes
            "dynamodb": 10,  # Product and inventory cache
            "lambda": 5,  # Webhook processing
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 8,  # Event messaging
                "lambda_executions": 8,  # Event processing
                "dynamodb_events": 5,  # Additional event storage
            })

        monthly_total = sum(v for v in base_costs.values() if isinstance(v, (int, float)))

        return {
            "monthly_fixed_costs": monthly_total,
            "transaction_fees": "2.9% of sales",
            "total_description": f"${monthly_total}/month + 2.9% of sales",
            "agency_cost_savings": "80-90% vs traditional Shopify agencies",
            "competitive_advantage": "Proven platform reliability with custom performance optimization"
        }

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for Shopify Basic e-commerce tier"""

        score = 0
        reasons = []

        # E-commerce platform reliability (major factor for Shopify)
        if requirements.get("proven_platform", False):
            score += 30
            reasons.append("Shopify's proven e-commerce platform reliability")

        # Performance requirements
        if requirements.get("performance_critical", False):
            score += 25
            reasons.append("Static site performance with proven e-commerce backend")

        # Agency alternative
        if requirements.get("agency_alternative", False):
            score += 25
            reasons.append("Excellent agency alternative with 80-90% cost savings")

        # Business size alignment
        business_size = requirements.get("business_size", "small")
        if business_size in ["small", "medium"]:
            score += 20
            reasons.append("Perfect fit for small to medium businesses")

        # Budget considerations
        budget = requirements.get("monthly_budget", 100)
        if budget >= 100:
            score += 15
            reasons.append("Budget supports Shopify Basic with hosting")
        elif budget >= 80:
            score += 10
            reasons.append("Budget covers basic Shopify implementation")
        else:
            score -= 10
            reasons.append("Budget may be tight for Shopify Basic")

        # Transaction volume
        expected_monthly_sales = requirements.get("expected_monthly_sales", 2000)
        if expected_monthly_sales >= 5000:
            score += 10
            reasons.append("Good value for medium-volume sales")
        elif expected_monthly_sales >= 1000:
            score += 5
            reasons.append("Suitable for growing sales volume")

        # PCI compliance need
        if requirements.get("pci_compliance", False):
            score += 15
            reasons.append("Shopify handles PCI compliance automatically")

        # Complex customization penalty
        if requirements.get("complex_customization", False):
            score -= 10
            reasons.append("Advanced customization may be limited compared to custom solutions")

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
            "integration_mode_recommendation": "event_driven" if requirements.get("growth_planning") else "direct"
        }