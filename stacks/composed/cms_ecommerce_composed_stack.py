"""
CMS + E-commerce Composed Stack

Event-driven compositional architecture enabling both content management and e-commerce
capabilities in a single deployment using decoupled integration patterns.

ARCHITECTURAL PATTERN (Event-Driven):
- Event-driven communication via SNS/SQS (no tight coupling)
- Shared state managed through S3/DynamoDB cache with unified schema
- Pluggable component protocol for CMS and E-commerce providers
- Integration layer acts as translation hub between systems
- Independent provider evolution with stable interfaces

INTEGRATION FLOW:
1. CMS webhook → Integration Layer → Normalize to UnifiedContent → S3 Cache
2. E-commerce webhook → Integration Layer → Merge product data → S3 Cache
3. Integration Layer → SNS "content.changed" → CodeBuild rebuild
4. SSG fetches unified content during build → Compile static site

BUSINESS USE CASES:
- Content + Commerce: Fashion brands with blogs + online stores
- Service + Product: Consulting firms selling courses and products
- Media + Merchandise: Content creators monetizing content and products
- B2B Resources: SaaS companies with content marketing + product sales

ARCHITECTURAL BENEFITS:
- Loose coupling: Systems communicate only through events
- Independent scaling: Each component can be updated separately
- Fault tolerance: Failures in one system don't cascade
- Pluggable providers: New CMS/E-commerce providers via protocol implementation

UNIFIED CONTENT SCHEMA:
class UnifiedContent(BaseModel):
    id: str
    title: str
    description: str
    image: str
    price: float | None          # E-commerce specific
    inventory: int | None        # E-commerce specific
    content_type: Literal["product", "article", "page"]

COST STRUCTURE:
- Base hosting: $50-75/month (same as individual stacks)
- CMS provider fees: $0-200/month (varies by provider)
- E-commerce provider fees: $29-300/month (varies by provider and volume)
- Integration overhead: $15-25/month (Lambda executions, API calls, monitoring)
- Setup cost: $2,400-4,800 (event-driven integration complexity)
"""

from typing import Dict, Any, Optional, List, Protocol
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct
from pydantic import BaseModel, Field
from enum import Enum

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.providers.cms.factory import CMSProviderFactory
from shared.providers.ecommerce.factory import EcommerceProviderFactory
from models.cms_config import CMSIntegrationConfig
from models.ecommerce_config import EcommerceIntegrationConfig


class ContentType(str, Enum):
    """Content types in the unified schema"""
    PRODUCT = "product"
    ARTICLE = "article"
    PAGE = "page"


class UnifiedContent(BaseModel):
    """Unified content schema for CMS + E-commerce composition"""
    model_config = {"str_strip_whitespace": True, "validate_assignment": True}

    id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description")
    image: Optional[str] = Field(None, description="Primary image URL")
    price: Optional[float] = Field(None, description="Product price (e-commerce only)")
    inventory: Optional[int] = Field(None, description="Inventory count (e-commerce only)")
    content_type: ContentType = Field(..., description="Type of content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific metadata")


class ComposableComponent(Protocol):
    """Protocol that all CMS and E-commerce components must implement"""

    def register_webhooks(self, integration_api_url: str) -> None:
        """Register webhooks with the integration layer"""
        ...

    def get_content_feed(self) -> List[UnifiedContent]:
        """Get content in unified schema format"""
        ...

    def normalize_content(self, raw_data: Dict[str, Any]) -> UnifiedContent:
        """Convert provider-specific data to unified schema"""
        ...


class CMSEcommerceComposedStack(BaseSSGStack):
    """
    Event-driven composed stack providing both CMS and E-commerce capabilities.

    ARCHITECTURE:
    - Event-driven communication: CMS/E-commerce → Integration Layer → SSG rebuild
    - Shared content cache: S3/DynamoDB stores unified content schema
    - Pluggable components: CMS and E-commerce providers implement standard protocol
    - Loose coupling: Systems communicate only through events and shared cache

    INTEGRATION FLOW:
    1. Webhook → Integration Layer → Normalize content → Update cache
    2. Cache change → SNS event → CodeBuild trigger → SSG rebuild
    3. Build process fetches unified content from cache → Generate static site

    BENEFITS:
    - No direct system coupling (fault tolerance)
    - Independent provider updates (maintainability)
    - Standardized content schema (SSG simplicity)
    - Event-driven scaling (performance)

    This approach eliminates the complexity of direct system integration while
    providing seamless client experience with both content management and
    e-commerce functionality.
    """

    # Provider compatibility matrix for composed stacks
    COMPOSITION_COMPATIBILITY: Dict[str, Dict[str, List[str]]] = {
        "cms_providers": {
            "decap": ["hugo", "eleventy", "astro", "gatsby"],
            "tina": ["nextjs", "astro", "gatsby"],
            "sanity": ["nextjs", "astro", "gatsby", "eleventy"],
            "contentful": ["nextjs", "astro", "gatsby", "eleventy"]
        },
        "ecommerce_providers": {
            "snipcart": ["eleventy", "astro", "hugo", "gatsby"],
            "foxy": ["eleventy", "astro", "hugo", "gatsby"],
            "shopify_basic": ["eleventy", "astro", "nextjs", "nuxt"],
            "shopify_advanced": ["astro", "nextjs", "nuxt", "gatsby"]
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config,
        cms_config: CMSIntegrationConfig,
        ecommerce_config: EcommerceIntegrationConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, client_config, **kwargs)

        self.cms_config = cms_config
        self.ecommerce_config = ecommerce_config

        # Validate provider compatibility with chosen SSG engine
        self._validate_composition_compatibility()

        # Create composed infrastructure
        self._create_custom_infrastructure()

    def _validate_composition_compatibility(self) -> None:
        """Validate that CMS provider, E-commerce provider, and SSG engine are all compatible"""
        ssg_engine = self.client_config.ssg_engine
        cms_provider = self.cms_config.cms.provider
        ecommerce_provider = self.ecommerce_config.provider

        # Check CMS + SSG compatibility
        cms_compatible_ssgs = self.COMPOSITION_COMPATIBILITY["cms_providers"].get(cms_provider, [])
        if ssg_engine not in cms_compatible_ssgs:
            raise ValueError(
                f"SSG engine '{ssg_engine}' is not compatible with CMS provider '{cms_provider}'. "
                f"Compatible engines: {cms_compatible_ssgs}"
            )

        # Check E-commerce + SSG compatibility
        ecommerce_compatible_ssgs = self.COMPOSITION_COMPATIBILITY["ecommerce_providers"].get(ecommerce_provider, [])
        if ssg_engine not in ecommerce_compatible_ssgs:
            raise ValueError(
                f"SSG engine '{ssg_engine}' is not compatible with E-commerce provider '{ecommerce_provider}'. "
                f"Compatible engines: {ecommerce_compatible_ssgs}"
            )

    def _create_custom_infrastructure(self) -> None:
        """Create event-driven composed CMS + E-commerce infrastructure"""

        # 1. Create base SSG infrastructure (S3, CloudFront, etc.)
        self.create_content_bucket()
        self.create_cloudfront_distribution(
            origin_bucket=self.content_bucket,
            custom_domain=self.client_config.domain
        )

        # 2. Create integration layer (event bus and content cache)
        self._create_integration_layer()

        # 3. Create CMS component with webhook registration
        self._create_cms_component()

        # 4. Create E-commerce component with webhook registration
        self._create_ecommerce_component()

        # 5. Create event-driven build pipeline
        self._create_event_driven_build_pipeline()

        # 6. Wire components to integration layer
        self._wire_component_events()

        # 7. Create standard outputs
        self.create_standard_outputs()
        self._create_composition_outputs()

    def _create_integration_layer(self) -> None:
        """Create event-driven integration layer infrastructure"""

        # Create SNS topic for content change events
        self.content_events_topic = sns.Topic(
            self, "ContentEventsTopic",
            topic_name=f"{self.client_config.resource_prefix}-content-events",
            display_name="Content Change Events"
        )

        # Create SQS queue for event processing
        self.event_processing_queue = sqs.Queue(
            self, "EventProcessingQueue",
            queue_name=f"{self.client_config.resource_prefix}-event-processing",
            visibility_timeout=Duration.seconds(300)
        )

        # Create unified content cache (DynamoDB)
        self.unified_content_cache = dynamodb.Table(
            self, "UnifiedContentCache",
            table_name=f"{self.client_config.resource_prefix}-unified-content",
            partition_key=dynamodb.Attribute(
                name="content_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="content_type",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create content cache bucket for larger objects
        self.content_cache_bucket = s3.Bucket(
            self, "ContentCacheBucket",
            bucket_name=f"{self.client_config.resource_prefix}-content-cache",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create integration API for webhook handling
        self.integration_api = apigateway.RestApi(
            self, "IntegrationAPI",
            rest_api_name=f"{self.client_config.client_id}-integration-api",
            description="Integration API for webhook handling and content normalization"
        )

        # Create integration Lambda function
        self.integration_handler = lambda_.Function(
            self, "IntegrationHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_integration_handler_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "CONTENT_CACHE_TABLE": self.unified_content_cache.table_name,
                "CONTENT_CACHE_BUCKET": self.content_cache_bucket.bucket_name,
                "CONTENT_EVENTS_TOPIC": self.content_events_topic.topic_arn,
                "CMS_PROVIDER": self.cms_config.cms.provider,
                "ECOMMERCE_PROVIDER": self.ecommerce_config.provider
            }
        )

        # Grant permissions to integration handler
        self.unified_content_cache.grant_read_write_data(self.integration_handler)
        self.content_cache_bucket.grant_read_write(self.integration_handler)
        self.content_events_topic.grant_publish(self.integration_handler)

        # Add webhook endpoints to integration API
        webhook_integration = apigateway.LambdaIntegration(self.integration_handler)
        self.integration_api.root.add_resource("webhooks").add_resource("cms").add_method("POST", webhook_integration)
        self.integration_api.root.add_resource("webhooks").add_resource("ecommerce").add_method("POST", webhook_integration)
        self.integration_api.root.add_resource("content").add_method("GET", webhook_integration)  # For SSG builds

    def _create_cms_component(self) -> None:
        """Create CMS component that implements ComposableComponent protocol"""

        # Create CMS webhook handler specific to provider type
        self.cms_webhook_handler = lambda_.Function(
            self, "CMSWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_cms_webhook_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "CMS_PROVIDER": self.cms_config.cms.provider,
                "INTEGRATION_API_URL": self.integration_api.url,
                "GITHUB_REPO": self.cms_config.cms.content_settings.get("repository", ""),
                "GITHUB_OWNER": self.cms_config.cms.content_settings.get("repository_owner", "")
            }
        )

    def _create_ecommerce_component(self) -> None:
        """Create E-commerce component that implements ComposableComponent protocol"""

        # Create E-commerce webhook handler specific to provider type
        self.ecommerce_webhook_handler = lambda_.Function(
            self, "EcommerceWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_ecommerce_webhook_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "ECOMMERCE_PROVIDER": self.ecommerce_config.provider,
                "INTEGRATION_API_URL": self.integration_api.url
            }
        )

    def _create_git_based_cms_resources(self) -> None:
        """Create resources for git-based CMS providers (Decap, Tina)"""

        # Create GitHub webhook handler
        self.cms_webhook_handler = lambda_.Function(
            self, "CMSWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_cms_webhook_code()),
            timeout=Duration.seconds(60),
            environment={
                **self.get_standard_environment_variables(),
                "CMS_PROVIDER": self.cms_config.cms.provider,
                "GITHUB_REPO": self.cms_config.cms.content_settings.get("repository", ""),
                "GITHUB_OWNER": self.cms_config.cms.content_settings.get("repository_owner", "")
            }
        )

        # Grant webhook handler permissions to trigger builds
        if self.content_bucket:
            self.content_bucket.grant_read_write(self.cms_webhook_handler)

    def _create_api_based_cms_resources(self) -> None:
        """Create resources for API-based CMS providers (Sanity, Contentful)"""

        # Create content synchronization Lambda
        self.content_sync = lambda_.Function(
            self, "ContentSync",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_content_sync_code()),
            timeout=Duration.seconds(300),  # 5 minutes for large content sync
            environment={
                **self.get_standard_environment_variables(),
                "CMS_PROVIDER": self.cms_config.cms.provider,
                "CMS_PROJECT_ID": self.cms_config.cms.content_settings.get("project_id", ""),
                "CMS_DATASET": self.cms_config.cms.content_settings.get("dataset", "production")
            }
        )

    def _create_hybrid_cms_resources(self) -> None:
        """Create resources for hybrid CMS providers"""
        # Create both git-based and API-based resources
        self._create_git_based_cms_resources()
        self._create_api_based_cms_resources()

    def _create_event_driven_build_pipeline(self) -> None:
        """Create event-driven build pipeline triggered by content changes"""

        # Create build trigger Lambda that responds to SNS events
        self.build_trigger = lambda_.Function(
            self, "BuildTrigger",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_build_trigger_code()),
            timeout=Duration.seconds(30),
            environment={
                **self.get_standard_environment_variables(),
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-build",
                "CONTENT_CACHE_TABLE": self.unified_content_cache.table_name,
                "CONTENT_CACHE_BUCKET": self.content_cache_bucket.bucket_name
            }
        )

        # Subscribe build trigger to content events
        self.content_events_topic.add_subscription(
            sns.subscriptions.LambdaSubscription(self.build_trigger)
        )

        # Create build role with permissions for unified content access
        additional_policies = [
            # DynamoDB permissions for unified content cache access during build
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    self.unified_content_cache.table_arn
                ]
            ),
            # S3 permissions for content cache bucket
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                resources=[
                    self.content_cache_bucket.bucket_arn,
                    f"{self.content_cache_bucket.bucket_arn}/*"
                ]
            )
        ]

        self.create_build_role(additional_policies=additional_policies)

        # Grant build trigger permission to start builds
        self.build_trigger.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codebuild:StartBuild"],
                resources=[f"arn:aws:codebuild:*:*:project/{self.client_config.resource_prefix}-build"]
            )
        )

        # Grant access to content cache
        self.unified_content_cache.grant_read_data(self.build_trigger)
        self.content_cache_bucket.grant_read(self.build_trigger)

    def _wire_component_events(self) -> None:
        """Wire CMS and E-commerce components to integration layer events"""

        # The integration layer handles all webhook processing and content normalization
        # Components register their webhooks to point to the integration API endpoints

        # CMS webhook URLs: {integration_api}/webhooks/cms
        # E-commerce webhook URLs: {integration_api}/webhooks/ecommerce
        #
        # Integration flow:
        # 1. External webhook → Integration API → Normalize content → Update cache
        # 2. Cache update → SNS publish → Build trigger → CodeBuild start
        # 3. Build process → Fetch from integration API /content → Generate site

        pass  # Wiring is handled through environment variables and API endpoints

    def _create_composition_outputs(self) -> None:
        """Create outputs specific to composed CMS + E-commerce stack"""

        from aws_cdk import CfnOutput

        # CMS-related outputs
        CfnOutput(
            self, "CMSProvider",
            value=self.cms_config.cms.provider,
            description="CMS provider"
        )

        CfnOutput(
            self, "CMSAdminURL",
            value=f"https://{self.get_website_url()}/admin",
            description="CMS admin interface URL"
        )

        # E-commerce-related outputs
        CfnOutput(
            self, "EcommerceProvider",
            value=self.ecommerce_config.provider,
            description="E-commerce provider"
        )

        CfnOutput(
            self, "EcommerceAPIEndpoint",
            value=self.ecommerce_api.url,
            description="E-commerce API endpoint"
        )

        # Composed stack outputs
        CfnOutput(
            self, "CompositionType",
            value="cms_ecommerce_composed",
            description="Stack composition type"
        )

        CfnOutput(
            self, "SupportedFeatures",
            value=f"CMS({self.cms_config.cms.provider}) + E-commerce({self.ecommerce_config.provider}) + SSG({self.client_config.ssg_engine})",
            description="Supported feature composition"
        )

    def _get_integration_handler_code(self) -> str:
        """Get Lambda code for integration layer (webhook processing and content normalization)"""
        return """
        const AWS = require('aws-sdk');
        const dynamodb = new AWS.DynamoDB.DocumentClient();
        const s3 = new AWS.S3();
        const sns = new AWS.SNS();

        exports.handler = async (event) => {
            const { httpMethod, path, body } = event;

            console.log('Integration layer request:', { httpMethod, path });

            try {
                if (httpMethod === 'POST' && path.includes('/webhooks/cms')) {
                    return await handleCMSWebhook(JSON.parse(body || '{}'));
                } else if (httpMethod === 'POST' && path.includes('/webhooks/ecommerce')) {
                    return await handleEcommerceWebhook(JSON.parse(body || '{}'));
                } else if (httpMethod === 'GET' && path.includes('/content')) {
                    return await getUnifiedContent();
                }

                return {
                    statusCode: 404,
                    body: JSON.stringify({ message: 'Endpoint not found' })
                };
            } catch (error) {
                console.error('Integration handler error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ message: 'Internal server error', error: error.message })
                };
            }
        };

        async function handleCMSWebhook(webhookData) {
            console.log('Processing CMS webhook:', webhookData);

            // Normalize CMS content to unified schema
            const unifiedContent = normalizeCMSContent(webhookData);

            // Store in content cache
            await storeUnifiedContent(unifiedContent);

            // Trigger content change event
            await publishContentChangeEvent('cms', unifiedContent.id);

            return {
                statusCode: 200,
                body: JSON.stringify({ message: 'CMS webhook processed', contentId: unifiedContent.id })
            };
        }

        async function handleEcommerceWebhook(webhookData) {
            console.log('Processing E-commerce webhook:', webhookData);

            // Normalize e-commerce data to unified schema
            const unifiedContent = normalizeEcommerceContent(webhookData);

            // Store in content cache
            await storeUnifiedContent(unifiedContent);

            // Trigger content change event
            await publishContentChangeEvent('ecommerce', unifiedContent.id);

            return {
                statusCode: 200,
                body: JSON.stringify({ message: 'E-commerce webhook processed', contentId: unifiedContent.id })
            };
        }

        async function getUnifiedContent() {
            // Fetch all unified content for SSG build process
            const params = {
                TableName: process.env.CONTENT_CACHE_TABLE
            };

            const result = await dynamodb.scan(params).promise();

            return {
                statusCode: 200,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: result.Items,
                    lastUpdated: new Date().toISOString()
                })
            };
        }

        function normalizeCMSContent(cmsData) {
            // Convert CMS-specific data to UnifiedContent schema
            return {
                id: cmsData.id || generateId(),
                title: cmsData.title || cmsData.name || 'Untitled',
                description: cmsData.description || cmsData.summary || '',
                image: cmsData.image || cmsData.featured_image,
                price: null, // CMS content doesn't have price
                inventory: null, // CMS content doesn't have inventory
                content_type: 'article', // Default for CMS content
                metadata: {
                    source: 'cms',
                    provider: process.env.CMS_PROVIDER,
                    originalData: cmsData
                }
            };
        }

        function normalizeEcommerceContent(ecommerceData) {
            // Convert E-commerce-specific data to UnifiedContent schema
            return {
                id: ecommerceData.id || ecommerceData.product_id || generateId(),
                title: ecommerceData.name || ecommerceData.title || 'Untitled Product',
                description: ecommerceData.description || ecommerceData.summary || '',
                image: ecommerceData.image || ecommerceData.featured_image,
                price: parseFloat(ecommerceData.price || 0),
                inventory: parseInt(ecommerceData.inventory || ecommerceData.stock || 0),
                content_type: 'product',
                metadata: {
                    source: 'ecommerce',
                    provider: process.env.ECOMMERCE_PROVIDER,
                    originalData: ecommerceData
                }
            };
        }

        async function storeUnifiedContent(unifiedContent) {
            const params = {
                TableName: process.env.CONTENT_CACHE_TABLE,
                Item: {
                    content_id: unifiedContent.id,
                    content_type: unifiedContent.content_type,
                    ...unifiedContent,
                    updatedAt: new Date().toISOString()
                }
            };

            await dynamodb.put(params).promise();
        }

        async function publishContentChangeEvent(source, contentId) {
            const params = {
                TopicArn: process.env.CONTENT_EVENTS_TOPIC,
                Message: JSON.stringify({
                    eventType: 'content.changed',
                    source: source,
                    contentId: contentId,
                    timestamp: new Date().toISOString()
                })
            };

            await sns.publish(params).promise();
        }

        function generateId() {
            return Date.now().toString() + '-' + Math.random().toString(36).substr(2, 9);
        }
        """

    def _get_build_trigger_code(self) -> str:
        """Get Lambda code for build trigger (responds to SNS events)"""
        return """
        const AWS = require('aws-sdk');
        const codebuild = new AWS.CodeBuild();

        exports.handler = async (event) => {
            console.log('Build trigger event:', JSON.stringify(event));

            try {
                // Parse SNS message
                const records = event.Records || [];

                for (const record of records) {
                    if (record.Sns) {
                        const message = JSON.parse(record.Sns.Message);
                        console.log('Content change event:', message);

                        if (message.eventType === 'content.changed') {
                            await triggerBuild(message);
                        }
                    }
                }

                return {
                    statusCode: 200,
                    body: JSON.stringify({ message: 'Build triggers processed' })
                };
            } catch (error) {
                console.error('Build trigger error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ message: 'Build trigger failed', error: error.message })
                };
            }
        };

        async function triggerBuild(contentChangeEvent) {
            const params = {
                projectName: process.env.BUILD_PROJECT_NAME,
                environmentVariablesOverride: [
                    {
                        name: 'CONTENT_CHANGE_SOURCE',
                        value: contentChangeEvent.source,
                        type: 'PLAINTEXT'
                    },
                    {
                        name: 'CONTENT_CHANGE_ID',
                        value: contentChangeEvent.contentId,
                        type: 'PLAINTEXT'
                    },
                    {
                        name: 'INTEGRATION_CONTENT_URL',
                        value: `${process.env.INTEGRATION_API_URL}/content`,
                        type: 'PLAINTEXT'
                    }
                ]
            };

            console.log('Starting build with params:', params);
            const result = await codebuild.startBuild(params).promise();
            console.log('Build started:', result.build.id);

            return result;
        }
        """

    def _get_cms_webhook_code(self) -> str:
        """Get Lambda code for CMS-specific webhook handling (forwards to integration layer)"""
        return """
        const https = require('https');
        const url = require('url');

        exports.handler = async (event) => {
            console.log('CMS component webhook received:', JSON.stringify(event));

            try {
                // Forward webhook to integration layer
                const integrationUrl = process.env.INTEGRATION_API_URL + '/webhooks/cms';

                // CMS providers have different webhook formats, normalize here if needed
                const normalizedData = normalizeCMSWebhook(event, process.env.CMS_PROVIDER);

                const response = await forwardWebhook(integrationUrl, normalizedData);

                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'CMS webhook forwarded to integration layer',
                        integrationResponse: response
                    })
                };
            } catch (error) {
                console.error('CMS webhook forward error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ message: 'CMS webhook forward failed', error: error.message })
                };
            }
        };

        function normalizeCMSWebhook(event, provider) {
            // Normalize different CMS provider webhook formats
            switch (provider) {
                case 'decap':
                    return event.body ? JSON.parse(event.body) : event;
                case 'tina':
                    return event.body ? JSON.parse(event.body) : event;
                case 'sanity':
                    return event.body ? JSON.parse(event.body) : event;
                case 'contentful':
                    return event.body ? JSON.parse(event.body) : event;
                default:
                    return event.body ? JSON.parse(event.body) : event;
            }
        }

        async function forwardWebhook(targetUrl, data) {
            return new Promise((resolve, reject) => {
                const parsedUrl = url.parse(targetUrl);
                const postData = JSON.stringify(data);

                const options = {
                    hostname: parsedUrl.hostname,
                    port: parsedUrl.port || 443,
                    path: parsedUrl.path,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Content-Length': Buffer.byteLength(postData)
                    }
                };

                const req = https.request(options, (res) => {
                    let responseData = '';
                    res.on('data', (chunk) => responseData += chunk);
                    res.on('end', () => resolve(responseData));
                });

                req.on('error', reject);
                req.write(postData);
                req.end();
            });
        }
        """

    def _get_ecommerce_webhook_code(self) -> str:
        """Get Lambda code for E-commerce-specific webhook handling (forwards to integration layer)"""
        return """
        const https = require('https');
        const url = require('url');

        exports.handler = async (event) => {
            console.log('E-commerce component webhook received:', JSON.stringify(event));

            try {
                // Forward webhook to integration layer
                const integrationUrl = process.env.INTEGRATION_API_URL + '/webhooks/ecommerce';

                // E-commerce providers have different webhook formats, normalize here if needed
                const normalizedData = normalizeEcommerceWebhook(event, process.env.ECOMMERCE_PROVIDER);

                const response = await forwardWebhook(integrationUrl, normalizedData);

                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'E-commerce webhook forwarded to integration layer',
                        integrationResponse: response
                    })
                };
            } catch (error) {
                console.error('E-commerce webhook forward error:', error);
                return {
                    statusCode: 500,
                    body: JSON.stringify({ message: 'E-commerce webhook forward failed', error: error.message })
                };
            }
        };

        function normalizeEcommerceWebhook(event, provider) {
            // Normalize different E-commerce provider webhook formats
            switch (provider) {
                case 'snipcart':
                    return event.body ? JSON.parse(event.body) : event;
                case 'foxy':
                    return event.body ? JSON.parse(event.body) : event;
                case 'shopify_basic':
                case 'shopify_advanced':
                    return event.body ? JSON.parse(event.body) : event;
                default:
                    return event.body ? JSON.parse(event.body) : event;
            }
        }

        async function forwardWebhook(targetUrl, data) {
            return new Promise((resolve, reject) => {
                const parsedUrl = url.parse(targetUrl);
                const postData = JSON.stringify(data);

                const options = {
                    hostname: parsedUrl.hostname,
                    port: parsedUrl.port || 443,
                    path: parsedUrl.path,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Content-Length': Buffer.byteLength(postData)
                    }
                };

                const req = https.request(options, (res) => {
                    let responseData = '';
                    res.on('data', (chunk) => responseData += chunk);
                    res.on('end', () => resolve(responseData));
                });

                req.on('error', reject);
                req.write(postData);
                req.end();
            });
        }
        """

    def _get_ecommerce_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for e-commerce components"""
        env_vars = self.get_standard_environment_variables()
        env_vars.update({
            "ECOMMERCE_PROVIDER": self.ecommerce_config.provider,
            "PRODUCT_CATALOG_TABLE": self.product_catalog.table_name,
            "INVENTORY_TABLE": self.inventory_table.table_name
        })
        return env_vars

    @classmethod
    def get_compatible_ssg_engines(
        cls,
        cms_provider: str,
        ecommerce_provider: str
    ) -> List[str]:
        """Get SSG engines compatible with both CMS and E-commerce providers"""

        cms_compatible = cls.COMPOSITION_COMPATIBILITY["cms_providers"].get(cms_provider, [])
        ecommerce_compatible = cls.COMPOSITION_COMPATIBILITY["ecommerce_providers"].get(ecommerce_provider, [])

        # Return intersection of both compatibility lists
        return list(set(cms_compatible) & set(ecommerce_compatible))

    def estimate_monthly_cost(self) -> Dict[str, float]:
        """Estimate monthly costs for event-driven composed CMS + E-commerce stack"""

        # Get base SSG costs
        base_costs = super().estimate_monthly_cost()

        # Add CMS provider costs (would be calculated based on CMS provider and usage)
        cms_cost = 0  # Provider-specific costs (Contentful $300+, others free-$99)

        # Add E-commerce provider costs (would be calculated based on E-commerce provider)
        ecommerce_cost = 50  # Base e-commerce provider cost (Snipcart $29+, Foxy $75+, Shopify $29+)

        # Event-driven integration overhead breakdown
        lambda_executions = 8    # Integration handler, webhook handlers, build trigger
        dynamodb_usage = 3       # Unified content cache
        sns_usage = 1           # Content change events
        api_gateway_usage = 2   # Integration API calls
        additional_storage = 1   # Content cache S3 bucket

        integration_overhead = lambda_executions + dynamodb_usage + sns_usage + api_gateway_usage + additional_storage

        composed_costs = {
            **base_costs,
            "cms_provider": cms_cost,
            "ecommerce_provider": ecommerce_cost,
            "integration_overhead": integration_overhead,
            "lambda_executions": lambda_executions,
            "event_bus_usage": sns_usage,
            "content_cache": dynamodb_usage + additional_storage,
        }

        composed_costs["total"] = sum(composed_costs.values())
        return composed_costs