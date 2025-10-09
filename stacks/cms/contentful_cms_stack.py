"""
Contentful CMS Tier Stack

Enterprise-grade CMS tier providing Contentful integration with flexible SSG engine support.
This stack represents the premium tier of the CMS service portfolio, offering advanced
content management, team collaboration, and enterprise workflows.

CONTENTFUL CMS TIER FEATURES:
- Enterprise-grade content management with advanced workflows
- Team collaboration with roles, permissions, and approval processes
- Multi-language content support with localization workflows
- Rich media management with asset optimization
- GraphQL and REST API access for flexible integrations
- Advanced content modeling with references and structured data
- Content versioning, scheduling, and publishing workflows

SUPPORTED SSG ENGINES:
- Gatsby: Perfect integration with GraphQL, optimal for content-heavy sites
- Astro: Modern component architecture with Contentful API integration
- Next.js: Full-stack React with Contentful JavaScript SDK
- Nuxt: Vue ecosystem with Contentful integration modules

BUSINESS POSITIONING:
- Target Market: Enterprise clients, large content teams, complex workflows
- Monthly Cost: $75-125/month (AWS hosting + Contentful subscription)
- Setup Cost: $2,100-4,800 (enterprise complexity and customization)
- ROI: Advanced features justify premium pricing for enterprise content needs

ENTERPRISE BENEFITS:
- Professional content workflows with approval processes
- Team collaboration with granular permissions
- Multi-environment content management (dev/staging/prod)
- Advanced analytics and content performance tracking
- Enterprise security and compliance features
- Dedicated support and SLA guarantees
"""

from typing import Dict, Any, Optional, List
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.providers.cms.contentful_provider import ContentfulProvider
from models.client_config import ClientConfig


class ContentfulCMSStack(BaseSSGStack):
    """
    Enterprise Contentful CMS tier with flexible SSG engine support.

    ARCHITECTURE:
    - API-based CMS with REST and GraphQL endpoints
    - Webhook-driven content synchronization
    - Enterprise security with API key management
    - Advanced monitoring and analytics
    - Multi-environment content delivery

    FLEXIBLE SSG ENGINE SUPPORT:
    - Client chooses CMS tier (Contentful) for enterprise features
    - Client chooses SSG engine (Gatsby/Astro/Next.js/Nuxt) for technical preference
    - Same monthly cost serves different technical comfort levels

    ENTERPRISE FEATURES:
    - Content workflows with approval processes
    - Team collaboration and permissions
    - Multi-language and localization support
    - Advanced content modeling and relationships
    - Content scheduling and versioning
    - Enterprise analytics and reporting
    """

    # SSG engine compatibility for Contentful CMS tier
    SUPPORTED_SSG_ENGINES = {
        "gatsby": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "build_time": "medium",
            "features": ["graphql", "content_sourcing", "image_optimization"],
            "cost_multiplier": 1.2
        },
        "astro": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "build_time": "fast",
            "features": ["component_islands", "performance", "api_integration"],
            "cost_multiplier": 1.0
        },
        "nextjs": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "build_time": "medium",
            "features": ["react_ecosystem", "api_routes", "enterprise_features"],
            "cost_multiplier": 1.3
        },
        "nuxt": {
            "compatibility": "excellent",
            "setup_complexity": "advanced",
            "build_time": "medium",
            "features": ["vue_ecosystem", "ssr", "enterprise_features"],
            "cost_multiplier": 1.3
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientConfig,
        ssg_engine: str,
        contentful_space_id: str,
        contentful_environment: str = "master",
        enable_preview: bool = True,
        enable_webhooks: bool = True,
        **kwargs
    ):
        # Validate SSG engine compatibility
        if ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            raise ValueError(
                f"SSG engine '{ssg_engine}' not supported by Contentful CMS tier. "
                f"Supported engines: {list(self.SUPPORTED_SSG_ENGINES.keys())}"
            )

        super().__init__(scope, construct_id, client_config, **kwargs)

        self.ssg_engine = ssg_engine
        self.contentful_space_id = contentful_space_id
        self.contentful_environment = contentful_environment
        self.enable_preview = enable_preview
        self.enable_webhooks = enable_webhooks

        # Create Contentful provider instance
        self.contentful_provider = ContentfulProvider(
            space_id=contentful_space_id,
            environment=contentful_environment,
            ssg_engine=ssg_engine
        )

        # Create enterprise-grade infrastructure
        self._create_enterprise_infrastructure()

    def _create_enterprise_infrastructure(self) -> None:
        """Create enterprise-grade infrastructure for Contentful CMS"""

        # 1. Create base SSG infrastructure (S3, CloudFront, etc.)
        self.create_content_bucket()
        self.create_cloudfront_distribution(
            origin_bucket=self.content_bucket,
            custom_domain=self.client_config.domain,
            enable_enterprise_features=True
        )

        # 2. Create Contentful API key management
        self._create_api_key_management()

        # 3. Create webhook handling infrastructure
        if self.enable_webhooks:
            self._create_webhook_infrastructure()

        # 4. Create content synchronization system
        self._create_content_sync_system()

        # 5. Create enterprise monitoring and analytics
        self._create_enterprise_monitoring()

        # 6. Create build pipeline with Contentful integration
        self._create_contentful_build_pipeline()

        # 7. Create outputs
        self.create_standard_outputs()
        self._create_contentful_outputs()

    def _create_api_key_management(self) -> None:
        """Create secure API key management for Contentful"""

        # Create Secrets Manager for Contentful API keys
        self.contentful_secrets = secretsmanager.Secret(
            self, "ContentfulSecrets",
            secret_name=f"{self.client_config.resource_prefix}-contentful-secrets",
            description="Contentful API keys and configuration",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"space_id": "' + self.contentful_space_id + '"}',
                generate_string_key="delivery_token",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"",
                password_length=64
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create separate secret for preview API (if enabled)
        if self.enable_preview:
            self.contentful_preview_secrets = secretsmanager.Secret(
                self, "ContentfulPreviewSecrets",
                secret_name=f"{self.client_config.resource_prefix}-contentful-preview-secrets",
                description="Contentful Preview API keys",
                removal_policy=RemovalPolicy.DESTROY
            )

    def _create_webhook_infrastructure(self) -> None:
        """Create Contentful webhook handling infrastructure"""

        # Create webhook handler Lambda
        self.webhook_handler = lambda_.Function(
            self, "ContentfulWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_webhook_handler_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "SSG_ENGINE": self.ssg_engine,
                "CONTENTFUL_SPACE_ID": self.contentful_space_id,
                "CONTENTFUL_ENVIRONMENT": self.contentful_environment,
                "SECRETS_ARN": self.contentful_secrets.secret_arn
            }
        )

        # Grant permissions to access secrets
        self.contentful_secrets.grant_read(self.webhook_handler)
        if self.enable_preview:
            self.contentful_preview_secrets.grant_read(self.webhook_handler)

        # Create API Gateway for webhooks
        self.webhook_api = apigateway.RestApi(
            self, "ContentfulWebhookAPI",
            rest_api_name=f"{self.client_config.client_id}-contentful-webhooks",
            description="Contentful webhook endpoints for content synchronization"
        )

        # Add webhook endpoint
        webhook_integration = apigateway.LambdaIntegration(self.webhook_handler)
        webhook_resource = self.webhook_api.root.add_resource("contentful")
        webhook_resource.add_method("POST", webhook_integration)

        # Add CORS for Contentful webhook requirements
        webhook_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Contentful-Topic"]
        )

    def _create_content_sync_system(self) -> None:
        """Create Contentful content synchronization system"""

        # Create content cache table for Contentful data
        self.contentful_cache = dynamodb.Table(
            self, "ContentfulCache",
            table_name=f"{self.client_config.resource_prefix}-contentful-cache",
            partition_key=dynamodb.Attribute(
                name="entry_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="locale",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            # Enterprise features
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            time_to_live_attribute="ttl"
        )

        # Create content synchronization Lambda
        self.content_sync = lambda_.Function(
            self, "ContentfulSync",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_content_sync_code()),
            timeout=Duration.seconds(300),  # 5 minutes for large content sync
            memory_size=512,  # Higher memory for enterprise content processing
            environment={
                **self.get_standard_environment_variables(),
                "SSG_ENGINE": self.ssg_engine,
                "CONTENTFUL_CACHE_TABLE": self.contentful_cache.table_name,
                "CONTENTFUL_SPACE_ID": self.contentful_space_id,
                "CONTENTFUL_ENVIRONMENT": self.contentful_environment,
                "SECRETS_ARN": self.contentful_secrets.secret_arn
            }
        )

        # Grant permissions
        self.contentful_cache.grant_read_write_data(self.content_sync)
        self.contentful_secrets.grant_read(self.content_sync)
        if self.enable_preview:
            self.contentful_preview_secrets.grant_read(self.content_sync)

    def _create_enterprise_monitoring(self) -> None:
        """Create enterprise-grade monitoring and analytics"""

        # Create CloudWatch dashboard for Contentful CMS metrics
        self.cms_dashboard = cloudwatch.Dashboard(
            self, "ContentfulCMSDashboard",
            dashboard_name=f"{self.client_config.client_id}-contentful-cms"
        )

        # Add metrics widgets
        self.cms_dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Contentful API Calls",
                left=[
                    self.content_sync.metric_invocations(),
                    self.webhook_handler.metric_invocations()
                ]
            ),
            cloudwatch.GraphWidget(
                title="Content Cache Performance",
                left=[
                    self.contentful_cache.metric_consumed_read_capacity_units(),
                    self.contentful_cache.metric_consumed_write_capacity_units()
                ]
            )
        )

        # Create alarms for enterprise monitoring
        cloudwatch.Alarm(
            self, "ContentfulSyncErrors",
            metric=self.content_sync.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="High error rate in Contentful content sync"
        )

        cloudwatch.Alarm(
            self, "ContentfulWebhookErrors",
            metric=self.webhook_handler.metric_errors(),
            threshold=10,
            evaluation_periods=2,
            alarm_description="High error rate in Contentful webhook processing"
        )

    def _create_contentful_build_pipeline(self) -> None:
        """Create build pipeline with Contentful integration"""

        # Create build role with Contentful-specific permissions
        additional_policies = [
            # DynamoDB permissions for Contentful cache
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[self.contentful_cache.table_arn]
            ),
            # Secrets Manager permissions for API keys
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    self.contentful_secrets.secret_arn,
                    *([self.contentful_preview_secrets.secret_arn] if self.enable_preview else [])
                ]
            )
        ]

        self.create_build_role(additional_policies=additional_policies)

        # Create build project with Contentful-specific buildspec
        buildspec = self._get_contentful_buildspec()
        self.create_build_project(buildspec=buildspec)

    def _create_contentful_outputs(self) -> None:
        """Create Contentful CMS-specific outputs"""

        from aws_cdk import CfnOutput

        # CMS configuration outputs
        CfnOutput(
            self, "ContentfulSpaceID",
            value=self.contentful_space_id,
            description="Contentful Space ID"
        )

        CfnOutput(
            self, "ContentfulEnvironment",
            value=self.contentful_environment,
            description="Contentful Environment"
        )

        CfnOutput(
            self, "SSGEngine",
            value=self.ssg_engine,
            description="Selected SSG Engine"
        )

        # Webhook configuration
        if self.enable_webhooks:
            CfnOutput(
                self, "ContentfulWebhookURL",
                value=f"{self.webhook_api.url}contentful",
                description="Contentful webhook URL for content synchronization"
            )

        # Enterprise features
        CfnOutput(
            self, "CMSDashboardURL",
            value=f"https://console.aws.amazon.com/cloudwatch/home#dashboards:name={self.cms_dashboard.dashboard_name}",
            description="CloudWatch dashboard for CMS monitoring"
        )

        # Service tier and pricing information
        CfnOutput(
            self, "ServiceTier",
            value="contentful_cms_tier",
            description="CMS service tier"
        )

        engine_config = self.SUPPORTED_SSG_ENGINES[self.ssg_engine]
        CfnOutput(
            self, "EstimatedMonthlyCost",
            value=f"${75 * engine_config['cost_multiplier']:.0f}-${125 * engine_config['cost_multiplier']:.0f}",
            description="Estimated monthly cost range"
        )

    def _get_webhook_handler_code(self) -> str:
        """Get Lambda code for Contentful webhook handling"""
        return """
        const AWS = require('aws-sdk');
        const https = require('https');

        const secretsManager = new AWS.SecretsManager();
        const codebuild = new AWS.CodeBuild();

        exports.handler = async (event) => {
            console.log('Contentful webhook received:', JSON.stringify(event));

            try {
                const body = JSON.parse(event.body || '{}');
                const headers = event.headers || {};

                // Validate Contentful webhook
                const contentfulTopic = headers['X-Contentful-Topic'] || headers['x-contentful-topic'];
                if (!contentfulTopic) {
                    console.warn('Missing Contentful topic header');
                    return { statusCode: 400, body: 'Invalid webhook' };
                }

                console.log('Contentful topic:', contentfulTopic);

                // Handle different content events
                if (contentfulTopic.includes('Entry.') || contentfulTopic.includes('Asset.')) {
                    await handleContentChange(body, contentfulTopic);
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

        async function handleContentChange(webhookData, topic) {
            console.log('Processing content change:', topic);

            // Trigger content synchronization
            await triggerContentSync();

            // Trigger site rebuild if content is published
            if (topic.includes('publish') || topic.includes('unpublish')) {
                await triggerSiteRebuild(webhookData);
            }
        }

        async function triggerContentSync() {
            // In production, this would trigger the content sync Lambda
            console.log('Content sync triggered');
        }

        async function triggerSiteRebuild(contentData) {
            try {
                const buildParams = {
                    projectName: process.env.BUILD_PROJECT_NAME,
                    environmentVariablesOverride: [
                        {
                            name: 'CONTENT_CHANGED',
                            value: 'true',
                            type: 'PLAINTEXT'
                        },
                        {
                            name: 'CONTENTFUL_SPACE_ID',
                            value: process.env.CONTENTFUL_SPACE_ID,
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

    def _get_content_sync_code(self) -> str:
        """Get Lambda code for Contentful content synchronization"""
        return """
        const AWS = require('aws-sdk');
        const https = require('https');

        const dynamodb = new AWS.DynamoDB.DocumentClient();
        const secretsManager = new AWS.SecretsManager();

        exports.handler = async (event) => {
            console.log('Contentful sync triggered:', JSON.stringify(event));

            try {
                // Get Contentful API credentials
                const secrets = await getContentfulSecrets();

                // Sync content from Contentful
                await syncContentfulContent(secrets);

                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'Content synchronized successfully',
                        timestamp: new Date().toISOString()
                    })
                };

            } catch (error) {
                console.error('Content sync error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ error: error.message })
                };
            }
        };

        async function getContentfulSecrets() {
            const secretValue = await secretsManager.getSecretValue({
                SecretId: process.env.SECRETS_ARN
            }).promise();

            return JSON.parse(secretValue.SecretString);
        }

        async function syncContentfulContent(secrets) {
            console.log('Syncing Contentful content...');

            // In production, this would:
            // 1. Fetch content from Contentful Delivery API
            // 2. Process and normalize content for the chosen SSG engine
            // 3. Store in DynamoDB cache for build process
            // 4. Handle localization and content relationships

            const sampleContent = {
                entry_id: 'sample-' + Date.now(),
                locale: 'en-US',
                content_type: 'article',
                title: 'Sample Content',
                body: 'This is sample content from Contentful',
                ssg_engine: process.env.SSG_ENGINE,
                synced_at: new Date().toISOString(),
                ttl: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hour TTL
            };

            await dynamodb.put({
                TableName: process.env.CONTENTFUL_CACHE_TABLE,
                Item: sampleContent
            }).promise();

            console.log('Content cached successfully');
        }
        """

    def _get_contentful_buildspec(self) -> Dict[str, Any]:
        """Get CodeBuild buildspec for Contentful CMS integration"""

        base_buildspec = {
            "version": "0.2",
            "env": {
                "variables": {
                    "SSG_ENGINE": self.ssg_engine,
                    "CONTENTFUL_SPACE_ID": self.contentful_space_id,
                    "CONTENTFUL_ENVIRONMENT": self.contentful_environment
                },
                "secrets-manager": {
                    "CONTENTFUL_DELIVERY_TOKEN": f"{self.contentful_secrets.secret_arn}:delivery_token",
                    "CONTENTFUL_PREVIEW_TOKEN": (
                        f"{self.contentful_preview_secrets.secret_arn}:preview_token"
                        if self.enable_preview else ""
                    )
                }
            },
            "phases": {
                "install": {
                    "runtime-versions": {
                        "nodejs": 18
                    },
                    "commands": [
                        "echo Installing dependencies for $SSG_ENGINE with Contentful CMS",
                        "npm install -g contentful-cli"
                    ]
                },
                "pre_build": {
                    "commands": [
                        "echo Fetching content from Contentful...",
                        "echo Space ID: $CONTENTFUL_SPACE_ID",
                        "echo Environment: $CONTENTFUL_ENVIRONMENT"
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
            "gatsby": [
                "npm install",
                "npm install gatsby-source-contentful",
                "CONTENTFUL_SPACE_ID=$CONTENTFUL_SPACE_ID CONTENTFUL_ACCESS_TOKEN=$CONTENTFUL_DELIVERY_TOKEN gatsby build"
            ],
            "astro": [
                "npm install",
                "npm install @astrojs/contentful",
                "CONTENTFUL_SPACE_ID=$CONTENTFUL_SPACE_ID CONTENTFUL_ACCESS_TOKEN=$CONTENTFUL_DELIVERY_TOKEN npm run build"
            ],
            "nextjs": [
                "npm install",
                "npm install contentful",
                "CONTENTFUL_SPACE_ID=$CONTENTFUL_SPACE_ID CONTENTFUL_ACCESS_TOKEN=$CONTENTFUL_DELIVERY_TOKEN npm run build && npm run export"
            ],
            "nuxt": [
                "npm install",
                "npm install @nuxtjs/contentful",
                "CONTENTFUL_SPACE_ID=$CONTENTFUL_SPACE_ID CONTENTFUL_ACCESS_TOKEN=$CONTENTFUL_DELIVERY_TOKEN npm run generate"
            ]
        }

        base_buildspec["phases"]["build"]["commands"] = ssg_commands.get(
            self.ssg_engine,
            ["echo Unsupported SSG engine: $SSG_ENGINE"]
        )

        return base_buildspec

    def get_monthly_cost_estimate(self) -> Dict[str, float]:
        """Get monthly cost estimate for Contentful CMS tier"""

        # Get base SSG costs
        base_costs = super().estimate_monthly_cost()

        # Contentful CMS costs (enterprise tier)
        contentful_cost = 300  # Contentful Team plan starting cost

        # Enterprise AWS overhead
        engine_config = self.SUPPORTED_SSG_ENGINES[self.ssg_engine]
        aws_overhead = 25 * engine_config["cost_multiplier"]  # Higher due to enterprise features

        # Enterprise features overhead
        enterprise_overhead = 15  # Enhanced monitoring, security, etc.

        total_cms_cost = contentful_cost + aws_overhead + enterprise_overhead

        return {
            **base_costs,
            "contentful_subscription": contentful_cost,
            "enterprise_aws_overhead": aws_overhead,
            "enterprise_features": enterprise_overhead,
            "total_cms_cost": total_cms_cost,
            "total": base_costs.get("total", 0) + total_cms_cost
        }

    @classmethod
    def get_client_suitability_score(
        cls,
        client_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get suitability score for Contentful CMS tier based on client requirements"""

        score = 0
        reasons = []

        # Enterprise features boost score
        if client_requirements.get("team_size", 1) > 5:
            score += 30
            reasons.append("Large team benefits from collaboration features")

        if client_requirements.get("content_localization", False):
            score += 25
            reasons.append("Multi-language content support")

        if client_requirements.get("content_workflows", False):
            score += 20
            reasons.append("Advanced content workflows and approval processes")

        if client_requirements.get("budget_range", "small") == "enterprise":
            score += 20
            reasons.append("Enterprise budget supports premium CMS features")

        if client_requirements.get("technical_complexity", "simple") == "advanced":
            score += 15
            reasons.append("Advanced technical requirements match enterprise tier")

        # Penalties for misalignment
        if client_requirements.get("budget_range", "small") == "tight":
            score -= 40
            reasons.append("Budget constraints limit enterprise CMS viability")

        if client_requirements.get("team_size", 1) <= 2:
            score -= 20
            reasons.append("Small team may not need enterprise collaboration features")

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
            "estimated_monthly_cost": "$375-$500+ (including Contentful subscription)"
        }