"""
CMS + E-commerce Composed Stack

Compositional architecture enabling both content management and e-commerce
capabilities in a single deployment. This stack addresses real-world scenarios
where clients need both content publishing and product sales functionality.

ARCHITECTURAL PATTERN:
- Composition over inheritance for flexible feature combination
- Single infrastructure base (S3, CloudFront, builds) shared by both systems
- Independent CMS and e-commerce provider selection
- Unified authentication and user management

BUSINESS USE CASES:
- Content + Commerce: Fashion brands with blogs + online stores
- Service + Product: Consulting firms selling courses and products
- Media + Merchandise: Content creators monetizing content and products
- B2B Resources: SaaS companies with content marketing + product sales

SUPPORTED COMBINATIONS:
- Any CMS provider (Decap, Tina, Sanity, Contentful) + Any E-commerce provider (Snipcart, Foxy, Shopify)
- SSG engine must be compatible with both chosen providers
- Unified build process compiling both content and product catalogs

COST STRUCTURE:
- Base hosting: $50-75/month (same as individual stacks)
- CMS provider fees: $0-200/month (varies by provider)
- E-commerce provider fees: $29-300/month (varies by provider and volume)
- Setup cost: $2,400-4,800 (complexity of integrating both systems)
"""

from typing import Dict, Any, Optional, List
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.providers.cms.factory import CMSProviderFactory
from shared.providers.ecommerce.factory import EcommerceProviderFactory
from models.cms_config import CMSIntegrationConfig
from models.ecommerce_config import EcommerceIntegrationConfig


class CMSEcommerceComposedStack(BaseSSGStack):
    """
    Composed stack providing both CMS and E-commerce capabilities.

    This stack implements compositional architecture to combine any supported
    CMS provider with any supported E-commerce provider, sharing common
    infrastructure while maintaining provider independence.
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
        """Create composed CMS + E-commerce infrastructure"""

        # 1. Create base SSG infrastructure (S3, CloudFront, etc.)
        self.create_content_bucket()
        self.create_cloudfront_distribution(
            origin_bucket=self.content_bucket,
            custom_domain=self.client_config.domain
        )

        # 2. Create CMS infrastructure components
        self._create_cms_infrastructure()

        # 3. Create E-commerce infrastructure components
        self._create_ecommerce_infrastructure()

        # 4. Create unified build pipeline
        self._create_composed_build_pipeline()

        # 5. Create shared authentication and user management
        self._create_unified_auth_system()

        # 6. Create standard outputs
        self.create_standard_outputs()
        self._create_composition_outputs()

    def _create_cms_infrastructure(self) -> None:
        """Create CMS-specific infrastructure components"""

        # Get CMS provider instance
        cms_provider = CMSProviderFactory.create_provider(
            self.cms_config.cms.provider,
            self.cms_config.cms.content_settings
        )

        # Create CMS-specific resources based on provider type
        if cms_provider.get_cms_type().value == "git_based":
            self._create_git_based_cms_resources()
        elif cms_provider.get_cms_type().value == "api_based":
            self._create_api_based_cms_resources()
        elif cms_provider.get_cms_type().value == "hybrid":
            self._create_hybrid_cms_resources()

    def _create_ecommerce_infrastructure(self) -> None:
        """Create E-commerce-specific infrastructure components"""

        # Create order processing Lambda
        self.order_processor = lambda_.Function(
            self, "OrderProcessor",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_order_processor_code()),
            timeout=Duration.seconds(30),
            environment=self._get_ecommerce_environment_variables()
        )

        # Create product catalog DynamoDB table
        self.product_catalog = dynamodb.Table(
            self, "ProductCatalog",
            table_name=f"{self.client_config.resource_prefix}-products",
            partition_key=dynamodb.Attribute(
                name="product_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create inventory management table
        self.inventory_table = dynamodb.Table(
            self, "InventoryManagement",
            table_name=f"{self.client_config.resource_prefix}-inventory",
            partition_key=dynamodb.Attribute(
                name="sku",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Grant Lambda permissions to DynamoDB tables
        self.product_catalog.grant_read_write_data(self.order_processor)
        self.inventory_table.grant_read_write_data(self.order_processor)

        # Create API Gateway for e-commerce endpoints
        self.ecommerce_api = apigateway.RestApi(
            self, "EcommerceAPI",
            rest_api_name=f"{self.client_config.client_id}-ecommerce-api",
            description="E-commerce API for order processing and product management"
        )

        # Add Lambda integration
        order_integration = apigateway.LambdaIntegration(self.order_processor)
        self.ecommerce_api.root.add_resource("orders").add_method("POST", order_integration)
        self.ecommerce_api.root.add_resource("products").add_method("GET", order_integration)

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

    def _create_composed_build_pipeline(self) -> None:
        """Create unified build pipeline for both CMS content and E-commerce data"""

        # Create build role with permissions for both CMS and E-commerce
        additional_policies = [
            # DynamoDB permissions for product catalog access during build
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    self.product_catalog.table_arn,
                    self.inventory_table.table_arn
                ]
            )
        ]

        self.create_build_role(additional_policies=additional_policies)

    def _create_unified_auth_system(self) -> None:
        """Create unified authentication system for both CMS and E-commerce access"""

        # Create user management table
        self.user_management = dynamodb.Table(
            self, "UserManagement",
            table_name=f"{self.client_config.resource_prefix}-users",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create authentication Lambda
        self.auth_handler = lambda_.Function(
            self, "AuthHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_auth_handler_code()),
            timeout=Duration.seconds(30),
            environment={
                **self.get_standard_environment_variables(),
                "USER_TABLE": self.user_management.table_name,
                "CMS_PROVIDER": self.cms_config.cms.provider,
                "ECOMMERCE_PROVIDER": self.ecommerce_config.provider
            }
        )

        # Grant permissions
        self.user_management.grant_read_write_data(self.auth_handler)

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

    def _get_order_processor_code(self) -> str:
        """Get Lambda code for order processing"""
        return """
        const AWS = require('aws-sdk');
        const dynamodb = new AWS.DynamoDB.DocumentClient();

        exports.handler = async (event) => {
            const { httpMethod, path, body } = event;

            if (httpMethod === 'POST' && path === '/orders') {
                return await processOrder(JSON.parse(body));
            } else if (httpMethod === 'GET' && path === '/products') {
                return await getProducts();
            }

            return {
                statusCode: 404,
                body: JSON.stringify({ message: 'Not found' })
            };
        };

        async function processOrder(orderData) {
            // Process order logic here
            return {
                statusCode: 200,
                body: JSON.stringify({ orderId: 'generated-id', status: 'processed' })
            };
        }

        async function getProducts() {
            // Get products logic here
            return {
                statusCode: 200,
                body: JSON.stringify({ products: [] })
            };
        }
        """

    def _get_cms_webhook_code(self) -> str:
        """Get Lambda code for CMS webhook handling"""
        return """
        exports.handler = async (event) => {
            console.log('CMS webhook received:', JSON.stringify(event));

            // Trigger build process when content changes
            // Implementation depends on CMS provider

            return {
                statusCode: 200,
                body: JSON.stringify({ message: 'Webhook processed' })
            };
        };
        """

    def _get_content_sync_code(self) -> str:
        """Get Lambda code for content synchronization"""
        return """
        exports.handler = async (event) => {
            console.log('Content sync triggered:', JSON.stringify(event));

            // Sync content from API-based CMS
            // Implementation depends on CMS provider

            return {
                statusCode: 200,
                body: JSON.stringify({ message: 'Content synced' })
            };
        };
        """

    def _get_auth_handler_code(self) -> str:
        """Get Lambda code for unified authentication"""
        return """
        const AWS = require('aws-sdk');
        const dynamodb = new AWS.DynamoDB.DocumentClient();

        exports.handler = async (event) => {
            console.log('Auth request:', JSON.stringify(event));

            // Handle authentication for both CMS and E-commerce access
            // Implementation depends on chosen providers

            return {
                statusCode: 200,
                body: JSON.stringify({ authenticated: true })
            };
        };
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
        """Estimate monthly costs for composed CMS + E-commerce stack"""

        # Get base SSG costs
        base_costs = super().estimate_monthly_cost()

        # Add CMS provider costs (implementation would query CMS provider)
        cms_cost = 0  # Would be calculated based on CMS provider and usage

        # Add E-commerce provider costs (implementation would query E-commerce provider)
        ecommerce_cost = 50  # Base e-commerce provider cost

        # Add composition overhead (additional Lambda executions, DynamoDB usage)
        composition_overhead = 15

        composed_costs = {
            **base_costs,
            "cms_provider": cms_cost,
            "ecommerce_provider": ecommerce_cost,
            "composition_overhead": composition_overhead,
        }

        composed_costs["total"] = sum(composed_costs.values())
        return composed_costs