"""
Shopify Basic E-commerce Stack

Standard Shopify integration with flexible SSG engine support for enhanced performance,
cost optimization, and superior customer experience. This stack provides enterprise-level
performance at small business prices through static site generation with Shopify backend.

SHOPIFY BASIC STACK FEATURES:
- Shopify Basic plan integration with Storefront API
- High-performance static frontend with sub-2s page loads
- Real-time product synchronization via webhooks
- Flexible SSG engine choice (Eleventy, Astro, Next.js, Nuxt)
- Automated build triggers on product/inventory changes
- Professional e-commerce features without enterprise complexity
- 80-90% cost reduction vs traditional Shopify agencies

SUPPORTED SSG ENGINES:
- Eleventy: Simple, fast builds ideal for straightforward product catalogs
- Astro: Modern component architecture with optimal performance for brands
- Next.js: React ecosystem with advanced Shopify SDK integration
- Nuxt: Vue ecosystem with comprehensive e-commerce modules

BUSINESS POSITIONING:
- Target Market: Small-medium stores, performance-focused brands, agency alternatives
- Monthly Cost: $75-125/month (Shopify Basic + AWS + integration)
- Setup Cost: $1,600-3,200 (80-90% less than traditional agencies)
- Value Proposition: Enterprise performance at small business prices

ARCHITECTURAL BENEFITS:
- Shopify handles complex e-commerce logic (cart, checkout, payments, PCI compliance)
- Static frontend provides superior performance, SEO, and mobile optimization
- Automated infrastructure eliminates ongoing agency dependencies
- Flexible SSG choice serves different technical comfort levels
"""

from typing import Dict, Any, Optional, List
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.providers.ecommerce.shopify_basic_provider import ShopifyBasicProvider
from models.client_config import ClientConfig


class ShopifyBasicEcommerceStack(BaseSSGStack):
    """
    Shopify Basic e-commerce tier with flexible SSG engine support and performance optimization.

    ARCHITECTURE:
    - Shopify backend handles all e-commerce functionality (proven, secure, PCI-compliant)
    - Custom static frontend provides superior performance and SEO optimization
    - Real-time synchronization between Shopify data and static site via webhooks
    - AWS-hosted frontend with CDN optimization and global delivery
    - Automated build triggers ensure content stays synchronized

    PERFORMANCE BENEFITS:
    - Static site delivery: 0.8-1.5s page loads vs 3-6s typical Shopify themes
    - CDN optimization: Global content delivery with edge caching
    - SEO excellence: Static HTML with perfect search engine optimization
    - Mobile performance: Optimized responsive design and asset delivery

    FLEXIBLE SSG ENGINE SUPPORT:
    - Client chooses e-commerce tier (Shopify Basic) for proven platform reliability
    - Client chooses SSG engine (Eleventy/Astro/Next.js/Nuxt) for technical preference
    - Same monthly cost serves different technical comfort levels and team expertise
    - Shopify handles complex e-commerce while frontend optimized for performance

    BUSINESS VALUE:
    - 80-90% cost reduction vs traditional Shopify agencies ($1,600-3,200 vs $8,000-25,000)
    - Superior performance drives better conversion rates and customer satisfaction
    - Automated infrastructure eliminates ongoing agency maintenance dependencies
    - Professional e-commerce features without enterprise complexity or cost
    """

    # SSG engine compatibility for Shopify Basic tier
    SUPPORTED_SSG_ENGINES = {
        "eleventy": {
            "compatibility": "excellent",
            "setup_complexity": "simple",
            "build_time": "very_fast",
            "features": ["fast_builds", "simple_templating", "shopify_integration"],
            "cost_multiplier": 1.0
        },
        "astro": {
            "compatibility": "perfect",
            "setup_complexity": "intermediate",
            "build_time": "fast",
            "features": ["component_islands", "performance_optimization", "modern_architecture"],
            "cost_multiplier": 1.1
        },
        "nextjs": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "build_time": "medium",
            "features": ["react_ecosystem", "shopify_hooks", "api_routes"],
            "cost_multiplier": 1.2
        },
        "nuxt": {
            "compatibility": "good",
            "setup_complexity": "advanced",
            "build_time": "medium",
            "features": ["vue_ecosystem", "ssr_support", "shopify_modules"],
            "cost_multiplier": 1.2
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientConfig,
        ssg_engine: str,
        shopify_store_domain: str,
        shopify_plan: str = "basic",
        enable_webhooks: bool = True,
        enable_analytics: bool = True,
        **kwargs
    ):
        # Validate SSG engine compatibility
        if ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            raise ValueError(
                f"SSG engine '{ssg_engine}' not supported by Shopify Basic tier. "
                f"Supported engines: {list(self.SUPPORTED_SSG_ENGINES.keys())}"
            )

        super().__init__(scope, construct_id, client_config, **kwargs)

        self.ssg_engine = ssg_engine
        self.shopify_store_domain = shopify_store_domain
        self.shopify_plan = shopify_plan
        self.enable_webhooks = enable_webhooks
        self.enable_analytics = enable_analytics

        # Create Shopify provider instance
        self.shopify_provider = ShopifyBasicProvider(
            store_domain=shopify_store_domain,
            shopify_plan=shopify_plan,
            ssg_engine=ssg_engine
        )

        # Create Shopify Basic infrastructure
        self._create_shopify_infrastructure()

    def _create_shopify_infrastructure(self) -> None:
        """Create Shopify Basic e-commerce infrastructure"""

        # 1. Create base SSG infrastructure (S3, CloudFront, etc.)
        self.create_content_bucket()
        self.create_cloudfront_distribution(
            origin_bucket=self.content_bucket,
            custom_domain=self.client_config.domain,
            enable_performance_optimization=True
        )

        # 2. Create Shopify API credentials management
        self._create_shopify_credentials()

        # 3. Create product synchronization infrastructure
        self._create_product_sync_system()

        # 4. Create webhook handling infrastructure
        if self.enable_webhooks:
            self._create_webhook_infrastructure()

        # 5. Create build pipeline with Shopify integration
        self._create_shopify_build_pipeline()

        # 6. Create analytics and monitoring
        if self.enable_analytics:
            self._create_shopify_analytics()

        # 7. Create standard outputs
        self.create_standard_outputs()
        self._create_shopify_outputs()

    def _create_shopify_credentials(self) -> None:
        """Create secure Shopify API credentials management"""

        # Create Secrets Manager for Shopify API tokens
        self.shopify_secrets = secretsmanager.Secret(
            self, "ShopifySecrets",
            secret_name=f"{self.client_config.resource_prefix}-shopify-secrets",
            description="Shopify API tokens and configuration",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=f'{{"store_domain": "{self.shopify_store_domain}"}}',
                generate_string_key="storefront_access_token",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"",
                password_length=32
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create additional secret for admin API token (for webhooks and management)
        self.shopify_admin_secrets = secretsmanager.Secret(
            self, "ShopifyAdminSecrets",
            secret_name=f"{self.client_config.resource_prefix}-shopify-admin-secrets",
            description="Shopify Admin API tokens for webhook management",
            removal_policy=RemovalPolicy.DESTROY
        )

    def _create_product_sync_system(self) -> None:
        """Create Shopify product synchronization system"""

        # Create product cache table
        self.product_cache = dynamodb.Table(
            self, "ShopifyProductCache",
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
            # Performance optimization
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            time_to_live_attribute="ttl"
        )

        # Create inventory tracking table
        self.inventory_cache = dynamodb.Table(
            self, "ShopifyInventoryCache",
            table_name=f"{self.client_config.resource_prefix}-shopify-inventory",
            partition_key=dynamodb.Attribute(
                name="variant_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )

        # Create product synchronization Lambda
        self.product_sync = lambda_.Function(
            self, "ShopifyProductSync",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_product_sync_code()),
            timeout=Duration.seconds(300),  # 5 minutes for large product catalogs
            memory_size=512,  # Higher memory for product processing
            environment={
                **self.get_standard_environment_variables(),
                "SSG_ENGINE": self.ssg_engine,
                "SHOPIFY_STORE_DOMAIN": self.shopify_store_domain,
                "PRODUCT_CACHE_TABLE": self.product_cache.table_name,
                "INVENTORY_CACHE_TABLE": self.inventory_cache.table_name,
                "SECRETS_ARN": self.shopify_secrets.secret_arn
            }
        )

        # Grant permissions
        self.product_cache.grant_read_write_data(self.product_sync)
        self.inventory_cache.grant_read_write_data(self.product_sync)
        self.shopify_secrets.grant_read(self.product_sync)

    def _create_webhook_infrastructure(self) -> None:
        """Create Shopify webhook handling infrastructure"""

        # Create webhook handler Lambda
        self.webhook_handler = lambda_.Function(
            self, "ShopifyWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_webhook_handler_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "SSG_ENGINE": self.ssg_engine,
                "SHOPIFY_STORE_DOMAIN": self.shopify_store_domain,
                "PRODUCT_CACHE_TABLE": self.product_cache.table_name,
                "INVENTORY_CACHE_TABLE": self.inventory_cache.table_name,
                "SECRETS_ARN": self.shopify_secrets.secret_arn
            }
        )

        # Grant permissions to access resources
        self.product_cache.grant_read_write_data(self.webhook_handler)
        self.inventory_cache.grant_read_write_data(self.webhook_handler)
        self.shopify_secrets.grant_read(self.webhook_handler)

        # Create API Gateway for webhooks
        self.webhook_api = apigateway.RestApi(
            self, "ShopifyWebhookAPI",
            rest_api_name=f"{self.client_config.client_id}-shopify-webhooks",
            description="Shopify webhook endpoints for product synchronization"
        )

        # Add webhook endpoint
        webhook_integration = apigateway.LambdaIntegration(self.webhook_handler)
        webhook_resource = self.webhook_api.root.add_resource("shopify")
        webhook_resource.add_method("POST", webhook_integration)

        # Add CORS for development and admin access
        webhook_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Shopify-Topic", "X-Shopify-Hmac-Sha256"]
        )

    def _create_shopify_build_pipeline(self) -> None:
        """Create build pipeline with Shopify integration"""

        # Create build role with Shopify-specific permissions
        additional_policies = [
            # DynamoDB permissions for product and inventory cache
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    self.product_cache.table_arn,
                    self.inventory_cache.table_arn
                ]
            ),
            # Secrets Manager permissions for Shopify API tokens
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    self.shopify_secrets.secret_arn,
                    self.shopify_admin_secrets.secret_arn
                ]
            )
        ]

        self.create_build_role(additional_policies=additional_policies)

        # Create build project with Shopify-specific buildspec
        buildspec = self._get_shopify_buildspec()
        self.create_build_project(buildspec=buildspec)

    def _create_shopify_analytics(self) -> None:
        """Create analytics and monitoring for Shopify integration"""

        # Create CloudWatch dashboard for Shopify metrics
        self.shopify_dashboard = cloudwatch.Dashboard(
            self, "ShopifyDashboard",
            dashboard_name=f"{self.client_config.client_id}-shopify-ecommerce"
        )

        # Add metrics widgets
        self.shopify_dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Shopify API Calls",
                left=[
                    self.product_sync.metric_invocations(),
                    self.webhook_handler.metric_invocations()
                ]
            ),
            cloudwatch.GraphWidget(
                title="Product Cache Performance",
                left=[
                    self.product_cache.metric_consumed_read_capacity_units(),
                    self.product_cache.metric_consumed_write_capacity_units()
                ]
            ),
            cloudwatch.GraphWidget(
                title="Build Performance",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/CodeBuild",
                        metric_name="Builds",
                        dimensions_map={
                            "ProjectName": f"{self.client_config.resource_prefix}-build"
                        }
                    )
                ]
            )
        )

        # Create alarms for critical issues
        cloudwatch.Alarm(
            self, "ShopifyProductSyncErrors",
            metric=self.product_sync.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="High error rate in Shopify product sync"
        )

        cloudwatch.Alarm(
            self, "ShopifyWebhookErrors",
            metric=self.webhook_handler.metric_errors(),
            threshold=10,
            evaluation_periods=2,
            alarm_description="High error rate in Shopify webhook processing"
        )

    def _create_shopify_outputs(self) -> None:
        """Create Shopify-specific outputs"""

        from aws_cdk import CfnOutput

        # E-commerce configuration outputs
        CfnOutput(
            self, "ShopifyStoreDomain",
            value=self.shopify_store_domain,
            description="Shopify store domain"
        )

        CfnOutput(
            self, "ShopifyPlan",
            value=self.shopify_plan,
            description="Shopify plan tier"
        )

        CfnOutput(
            self, "SSGEngine",
            value=self.ssg_engine,
            description="Selected SSG Engine"
        )

        # Webhook configuration
        if self.enable_webhooks:
            CfnOutput(
                self, "ShopifyWebhookURL",
                value=f"{self.webhook_api.url}shopify",
                description="Shopify webhook URL for real-time synchronization"
            )

        # Analytics dashboard
        if self.enable_analytics:
            CfnOutput(
                self, "ShopifyDashboardURL",
                value=f"https://console.aws.amazon.com/cloudwatch/home#dashboards:name={self.shopify_dashboard.dashboard_name}",
                description="CloudWatch dashboard for Shopify e-commerce metrics"
            )

        # Service tier and pricing information
        CfnOutput(
            self, "EcommerceProvider",
            value="shopify_basic",
            description="E-commerce provider tier"
        )

        engine_config = self.SUPPORTED_SSG_ENGINES[self.ssg_engine]
        CfnOutput(
            self, "EstimatedMonthlyCost",
            value=f"${75 * engine_config['cost_multiplier']:.0f}-${125 * engine_config['cost_multiplier']:.0f}",
            description="Estimated monthly cost range"
        )

    def _get_webhook_handler_code(self) -> str:
        """Get Lambda code for Shopify webhook handling"""
        return """
        const AWS = require('aws-sdk');
        const crypto = require('crypto');

        const dynamodb = new AWS.DynamoDB.DocumentClient();
        const codebuild = new AWS.CodeBuild();
        const secretsManager = new AWS.SecretsManager();

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
                } else if (shopifyTopic.startsWith('inventory_levels/')) {
                    await handleInventoryWebhook(body, shopifyTopic);
                } else if (shopifyTopic.startsWith('collections/')) {
                    await handleCollectionWebhook(body, shopifyTopic);
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

            if (topic === 'products/delete') {
                // Remove product from cache
                await dynamodb.delete({
                    TableName: process.env.PRODUCT_CACHE_TABLE,
                    Key: {
                        product_id: productData.id.toString(),
                        handle: productData.handle
                    }
                }).promise();
            } else {
                // Update or create product in cache
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
                    ssg_engine: process.env.SSG_ENGINE,
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

        async function handleCollectionWebhook(collectionData, topic) {
            console.log('Processing collection webhook:', topic);

            // Trigger site rebuild for collection changes
            await triggerSiteRebuild(`Collection ${topic}`, collectionData);
        }

        async function triggerSiteRebuild(reason, data) {
            try {
                const buildParams = {
                    projectName: process.env.BUILD_PROJECT_NAME || `${process.env.CLIENT_ID}-build`,
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
        """

    def _get_product_sync_code(self) -> str:
        """Get Lambda code for Shopify product synchronization"""
        return """
        const AWS = require('aws-sdk');
        const https = require('https');

        const dynamodb = new AWS.DynamoDB.DocumentClient();
        const secretsManager = new AWS.SecretsManager();

        exports.handler = async (event) => {
            console.log('Shopify product sync triggered:', JSON.stringify(event));

            try {
                // Get Shopify API credentials
                const secrets = await getShopifySecrets();

                // Sync products from Shopify Storefront API
                await syncShopifyProducts(secrets);

                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'Products synchronized successfully',
                        timestamp: new Date().toISOString()
                    })
                };

            } catch (error) {
                console.error('Product sync error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ error: error.message })
                };
            }
        };

        async function getShopifySecrets() {
            const secretValue = await secretsManager.getSecretValue({
                SecretId: process.env.SECRETS_ARN
            }).promise();

            return JSON.parse(secretValue.SecretString);
        }

        async function syncShopifyProducts(secrets) {
            console.log('Syncing Shopify products...');

            const storeDomain = process.env.SHOPIFY_STORE_DOMAIN;
            const storefrontToken = secrets.storefront_access_token;

            const query = `
                query getProducts($first: Int!) {
                    products(first: $first) {
                        edges {
                            node {
                                id
                                title
                                handle
                                description
                                vendor
                                productType
                                tags
                                createdAt
                                updatedAt
                                images(first: 10) {
                                    edges {
                                        node {
                                            id
                                            url
                                            altText
                                            width
                                            height
                                        }
                                    }
                                }
                                variants(first: 10) {
                                    edges {
                                        node {
                                            id
                                            title
                                            price {
                                                amount
                                                currencyCode
                                            }
                                            compareAtPrice {
                                                amount
                                                currencyCode
                                            }
                                            availableForSale
                                            quantityAvailable
                                        }
                                    }
                                }
                                priceRange {
                                    minVariantPrice {
                                        amount
                                        currencyCode
                                    }
                                    maxVariantPrice {
                                        amount
                                        currencyCode
                                    }
                                }
                            }
                        }
                    }
                }
            `;

            const response = await makeGraphQLRequest(storeDomain, storefrontToken, query, { first: 50 });
            const products = response.data.products.edges;

            console.log(`Found ${products.length} products to sync`);

            for (const { node: product } of products) {
                const cacheItem = {
                    product_id: product.id,
                    handle: product.handle,
                    title: product.title,
                    description: product.description,
                    vendor: product.vendor,
                    product_type: product.productType,
                    tags: product.tags,
                    images: product.images.edges.map(edge => edge.node),
                    variants: product.variants.edges.map(edge => edge.node),
                    price_range: product.priceRange,
                    created_at: product.createdAt,
                    updated_at: product.updatedAt,
                    ssg_engine: process.env.SSG_ENGINE,
                    synced_at: new Date().toISOString(),
                    ttl: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60) // 7 day TTL
                };

                await dynamodb.put({
                    TableName: process.env.PRODUCT_CACHE_TABLE,
                    Item: cacheItem
                }).promise();
            }

            console.log('Product sync completed successfully');
        }

        async function makeGraphQLRequest(storeDomain, accessToken, query, variables) {
            return new Promise((resolve, reject) => {
                const data = JSON.stringify({ query, variables });

                const options = {
                    hostname: storeDomain.replace('https://', '').replace('http://', ''),
                    path: '/api/2023-10/graphql.json',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Content-Length': Buffer.byteLength(data),
                        'X-Shopify-Storefront-Access-Token': accessToken
                    }
                };

                const req = https.request(options, (res) => {
                    let responseData = '';
                    res.on('data', (chunk) => responseData += chunk);
                    res.on('end', () => {
                        try {
                            resolve(JSON.parse(responseData));
                        } catch (error) {
                            reject(error);
                        }
                    });
                });

                req.on('error', reject);
                req.write(data);
                req.end();
            });
        }
        """

    def _get_shopify_buildspec(self) -> Dict[str, Any]:
        """Get CodeBuild buildspec for Shopify integration"""

        base_buildspec = {
            "version": "0.2",
            "env": {
                "variables": {
                    "SSG_ENGINE": self.ssg_engine,
                    "SHOPIFY_STORE_DOMAIN": self.shopify_store_domain,
                    "SHOPIFY_PLAN": self.shopify_plan
                },
                "secrets-manager": {
                    "SHOPIFY_STOREFRONT_ACCESS_TOKEN": f"{self.shopify_secrets.secret_arn}:storefront_access_token",
                    "SHOPIFY_ADMIN_ACCESS_TOKEN": f"{self.shopify_admin_secrets.secret_arn}:admin_access_token"
                }
            },
            "phases": {
                "install": {
                    "runtime-versions": {
                        "nodejs": 18
                    },
                    "commands": [
                        "echo Installing dependencies for $SSG_ENGINE with Shopify Basic",
                        "npm install -g @shopify/cli @shopify/theme"
                    ]
                },
                "pre_build": {
                    "commands": [
                        "echo Fetching products from Shopify Storefront API...",
                        "echo Store Domain: $SHOPIFY_STORE_DOMAIN",
                        "echo SSG Engine: $SSG_ENGINE"
                    ]
                },
                "build": {
                    "commands": []
                },
                "post_build": {
                    "commands": [
                        f"aws s3 sync ./dist s3://{self.content_bucket.bucket_name}/ --delete",
                        f"aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths '/*'"
                    ]
                }
            }
        }

        # Add SSG-specific build commands
        ssg_commands = {
            "eleventy": [
                "npm install",
                "npm install @shopify/storefront-api-client graphql",
                "SHOPIFY_STORE_DOMAIN=$SHOPIFY_STORE_DOMAIN SHOPIFY_STOREFRONT_ACCESS_TOKEN=$SHOPIFY_STOREFRONT_ACCESS_TOKEN npx @11ty/eleventy"
            ],
            "astro": [
                "npm install",
                "npm install @shopify/storefront-api-client @astrojs/node graphql",
                "SHOPIFY_STORE_DOMAIN=$SHOPIFY_STORE_DOMAIN SHOPIFY_STOREFRONT_ACCESS_TOKEN=$SHOPIFY_STOREFRONT_ACCESS_TOKEN npm run build"
            ],
            "nextjs": [
                "npm install",
                "npm install @shopify/storefront-api-client @shopify/react-hooks graphql",
                "NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN=$SHOPIFY_STORE_DOMAIN NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN=$SHOPIFY_STOREFRONT_ACCESS_TOKEN npm run build && npm run export"
            ],
            "nuxt": [
                "npm install",
                "npm install @shopify/storefront-api-client @nuxtjs/axios graphql",
                "NUXT_PUBLIC_SHOPIFY_STORE_DOMAIN=$SHOPIFY_STORE_DOMAIN NUXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN=$SHOPIFY_STOREFRONT_ACCESS_TOKEN npm run generate"
            ]
        }

        base_buildspec["phases"]["build"]["commands"] = ssg_commands.get(
            self.ssg_engine,
            ["echo Unsupported SSG engine: $SSG_ENGINE"]
        )

        return base_buildspec

    def get_monthly_cost_estimate(self) -> Dict[str, float]:
        """Get monthly cost estimate for Shopify Basic tier"""

        # Get base SSG costs
        base_costs = super().estimate_monthly_cost()

        # Shopify Basic plan cost
        shopify_basic = 29  # Fixed Shopify Basic plan

        # AWS overhead for e-commerce features
        engine_config = self.SUPPORTED_SSG_ENGINES[self.ssg_engine]
        aws_overhead = 20 * engine_config["cost_multiplier"]  # DynamoDB, Lambda, API Gateway

        # Integration and maintenance
        integration_maintenance = 15  # Automated sync and webhook handling
        performance_optimization = 8   # CDN and build optimization

        total_ecommerce_cost = shopify_basic + aws_overhead + integration_maintenance + performance_optimization

        return {
            **base_costs,
            "shopify_basic_plan": shopify_basic,
            "ecommerce_aws_overhead": aws_overhead,
            "integration_maintenance": integration_maintenance,
            "performance_optimization": performance_optimization,
            "total_ecommerce_cost": total_ecommerce_cost,
            "total": base_costs.get("total", 0) + total_ecommerce_cost
        }

    @classmethod
    def get_client_suitability_score(
        cls,
        client_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get suitability score for Shopify Basic tier based on client requirements"""

        score = 0
        reasons = []

        # E-commerce requirements boost score
        if client_requirements.get("ecommerce_needed", False):
            score += 30
            reasons.append("E-commerce functionality required")

        if client_requirements.get("product_catalog", False):
            score += 25
            reasons.append("Product catalog management needed")

        if client_requirements.get("performance_critical", False):
            score += 20
            reasons.append("Performance-critical requirements benefit from static site delivery")

        # Budget considerations
        budget = client_requirements.get("monthly_budget", 0)
        if 75 <= budget <= 200:
            score += 20
            reasons.append("Budget range ideal for Shopify Basic tier")
        elif budget < 75:
            score -= 15
            reasons.append("Budget may be tight for Shopify Basic tier")

        # Business size alignment
        business_size = client_requirements.get("business_size", "small")
        if business_size in ["small", "medium"]:
            score += 15
            reasons.append("Business size fits Shopify Basic tier perfectly")

        # Technical requirements
        if client_requirements.get("agency_alternative", False):
            score += 25
            reasons.append("Excellent agency alternative with 80-90% cost savings")

        # Penalties for misalignment
        if client_requirements.get("enterprise_features", False):
            score -= 20
            reasons.append("Enterprise features may require Shopify Advanced tier")

        if business_size == "enterprise":
            score -= 15
            reasons.append("Enterprise size might need advanced e-commerce features")

        suitability = "poor"
        if score >= 70:
            suitability = "excellent"
        elif score >= 50:
            suitability = "good"
        elif score >= 30:
            suitability = "fair"

        return {
            "suitability_score": max(0, min(100, score)),
            "suitability": suitability,
            "reasons": reasons,
            "recommended_ssg_engines": list(cls.SUPPORTED_SSG_ENGINES.keys()),
            "estimated_monthly_cost": "$75-125",
            "setup_cost_estimate": "$1,600-3,200"
        }