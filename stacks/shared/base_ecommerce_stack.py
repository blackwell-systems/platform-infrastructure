"""
Base E-commerce Stack - Foundation for flexible e-commerce provider implementations

This base class enables the architectural transformation from hardcoded e-commerce/SSG
pairings to flexible client-choice architecture:

BEFORE (Hardcoded):
- ElevntySnipcartStack → Only Eleventy + Snipcart
- AstroFoxyStack → Only Astro + Foxy.io
- ShopifyBasicAWSStack → Only specific SSG + Shopify

AFTER (Flexible):
- SnipcartEcommerceStack → Hugo/Eleventy/Astro/Gatsby client choice
- FoxyEcommerceStack → Hugo/Eleventy/Astro/Gatsby client choice
- ShopifyBasicStack → Eleventy/Astro/Next.js/Nuxt client choice

Business Impact:
- Same monthly pricing serves multiple technical comfort levels
- Client choice based on technical preference, not arbitrary constraints
- 75% reduction in stack classes while exponentially increasing client options
"""

from typing import Dict, List, Any, Optional
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_ses as ses,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.ssg import StaticSiteConfig


class BaseEcommerceStack(BaseSSGStack):
    """
    Base class for e-commerce-enabled stacks with flexible SSG engine support.

    This class implements the e-commerce provider flexibility architecture,
    allowing clients to choose their e-commerce provider tier based on features
    and budget, then select their preferred SSG engine based on technical comfort.
    """

    # E-commerce Provider/SSG Engine Compatibility Matrix
    COMPATIBLE_SSG_ENGINES: Dict[str, List[str]] = {
        "snipcart": ["eleventy", "astro", "hugo", "gatsby"],
        "foxy": ["eleventy", "astro", "hugo", "gatsby"],
        "shopify_basic": ["eleventy", "astro", "nextjs", "nuxt"],
        "shopify_advanced": ["astro", "nextjs", "nuxt", "gatsby"],
        "shopify_headless": ["astro", "nextjs", "nuxt", "gatsby"]
    }

    # E-commerce Provider Features and Pricing
    PROVIDER_METADATA: Dict[str, Dict[str, Any]] = {
        "snipcart": {
            "name": "Snipcart",
            "monthly_cost_range": (29, 99),
            "transaction_fee": 0.02,  # 2%
            "setup_complexity": "low",
            "setup_hours": (3, 6),
            "best_for": ["simple_stores", "digital_products", "small_businesses"],
            "features": ["cart_management", "checkout", "order_management", "basic_analytics"]
        },
        "foxy": {
            "name": "Foxy.io",
            "monthly_cost_range": (75, 300),
            "transaction_fee": 0.015,  # 1.5%
            "setup_complexity": "high",
            "setup_hours": (6, 12),
            "best_for": ["advanced_features", "subscriptions", "complex_workflows"],
            "features": ["advanced_cart", "subscriptions", "custom_checkout", "advanced_analytics", "api_access"]
        },
        "shopify_basic": {
            "name": "Shopify Basic",
            "monthly_cost_range": (29, 79),
            "transaction_fee": 0.029,  # 2.9% + 30¢
            "setup_complexity": "medium",
            "setup_hours": (4, 8),
            "best_for": ["standard_ecommerce", "product_catalogs", "inventory_management"],
            "features": ["product_management", "inventory", "basic_analytics", "payment_processing"]
        },
        "shopify_advanced": {
            "name": "Shopify Advanced",
            "monthly_cost_range": (299, 399),
            "transaction_fee": 0.024,  # 2.4% + 30¢
            "setup_complexity": "high",
            "setup_hours": (8, 16),
            "best_for": ["enterprise_features", "advanced_reporting", "custom_apps"],
            "features": ["advanced_analytics", "custom_reporting", "flow_automation", "advanced_shipping"]
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        ecommerce_provider: str,
        ssg_engine: str = "eleventy",  # Default but client-configurable
        store_name: Optional[str] = None,
        currency: str = "USD",
        **kwargs
    ):
        # Validate e-commerce provider/SSG engine compatibility
        self._validate_ssg_ecommerce_compatibility(ssg_engine, ecommerce_provider)

        # Store e-commerce configuration
        self.ecommerce_provider = ecommerce_provider
        self.store_name = store_name or f"{client_id.title()} Store"
        self.currency = currency

        # Resolve template variant for (SSG, E-commerce) combination
        template_variant = self._resolve_ecommerce_template_variant(ssg_engine, ecommerce_provider)

        # Create flexible SSG configuration with e-commerce integration
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine=ssg_engine,  # Client choice within provider tier
            template_variant=template_variant,
            ecommerce_provider=ecommerce_provider,
            performance_tier="optimized"
        )

        super().__init__(scope, construct_id, ssg_config, **kwargs)

        # Add e-commerce-specific infrastructure
        self._setup_ecommerce_integration()

    def _validate_ssg_ecommerce_compatibility(self, ssg_engine: str, ecommerce_provider: str) -> None:
        """Validate that the selected SSG engine is compatible with the e-commerce provider"""
        compatible_engines = self.COMPATIBLE_SSG_ENGINES.get(ecommerce_provider, [])

        if ssg_engine not in compatible_engines:
            raise ValueError(
                f"SSG engine '{ssg_engine}' is not compatible with e-commerce provider '{ecommerce_provider}'. "
                f"Compatible engines: {compatible_engines}"
            )

    def _resolve_ecommerce_template_variant(self, ssg_engine: str, ecommerce_provider: str) -> str:
        """
        Map SSG + E-commerce combination to appropriate template variant.

        This enables the same e-commerce provider to work with different SSG engines
        using optimized templates for each combination.
        """
        template_mapping = {
            # Snipcart variants - optimized for each SSG engine
            ("eleventy", "snipcart"): "snipcart_ecommerce_simple",
            ("astro", "snipcart"): "snipcart_ecommerce_modern",
            ("hugo", "snipcart"): "snipcart_ecommerce_performance",
            ("gatsby", "snipcart"): "snipcart_ecommerce_react",

            # Foxy.io variants - advanced e-commerce features per SSG
            ("astro", "foxy"): "foxy_ecommerce_advanced",
            ("eleventy", "foxy"): "foxy_ecommerce_simple",
            ("hugo", "foxy"): "foxy_ecommerce_performance",
            ("gatsby", "foxy"): "foxy_ecommerce_react",

            # Shopify Basic variants - standard e-commerce per SSG
            ("eleventy", "shopify_basic"): "shopify_basic_simple",
            ("astro", "shopify_basic"): "shopify_basic_modern",
            ("nextjs", "shopify_basic"): "shopify_basic_react",
            ("nuxt", "shopify_basic"): "shopify_basic_vue",

            # Shopify Advanced variants - enterprise features per SSG
            ("astro", "shopify_advanced"): "shopify_advanced_headless",
            ("nextjs", "shopify_advanced"): "shopify_advanced_react",
            ("nuxt", "shopify_advanced"): "shopify_advanced_vue",
            ("gatsby", "shopify_advanced"): "shopify_advanced_graphql"
        }

        variant = template_mapping.get((ssg_engine, ecommerce_provider))
        if not variant:
            # Fallback to generic e-commerce template
            variant = f"{ecommerce_provider}_ecommerce_generic"

        return variant

    def _setup_ecommerce_integration(self) -> None:
        """Set up e-commerce provider integration infrastructure"""

        # Base e-commerce environment variables
        ecommerce_vars = {
            "ECOMMERCE_PROVIDER": self.ecommerce_provider,
            "STORE_NAME": self.store_name,
            "STORE_CURRENCY": self.currency,
            "SSG_ENGINE": self.ssg_config.ssg_engine
        }

        # Add SSG-specific e-commerce configuration
        ssg_specific_vars = self._get_ssg_specific_ecommerce_config()
        ecommerce_vars.update(ssg_specific_vars)

        self.add_environment_variables(ecommerce_vars)

        # Create e-commerce infrastructure components
        self._create_order_processing_infrastructure()
        self._create_webhook_infrastructure()
        self._create_notification_infrastructure()

    def _get_ssg_specific_ecommerce_config(self) -> Dict[str, str]:
        """
        Get SSG-specific e-commerce configuration.

        This allows the same e-commerce provider to integrate optimally
        with different SSG engines while maintaining provider consistency.
        """
        ssg_engine = self.ssg_config.ssg_engine

        # SSG-specific configuration patterns
        ssg_configs = {
            "eleventy": {
                "ECOMMERCE_TEMPLATES_PATH": "src/_includes/ecommerce",
                "PRODUCT_DATA_PATH": "src/_data/products.json",
                "BUILD_HOOK_PATH": "src/_data/store.json"
            },
            "astro": {
                "ECOMMERCE_COMPONENTS_PATH": "src/components/ecommerce",
                "PRODUCT_DATA_PATH": "src/data/products.json",
                "ASTRO_ECOMMERCE_ISLANDS": "true",
                "BUILD_HOOK_PATH": "src/data/store.json"
            },
            "hugo": {
                "ECOMMERCE_LAYOUTS_PATH": "layouts/ecommerce",
                "PRODUCT_DATA_PATH": "data/products.yaml",
                "BUILD_HOOK_PATH": "data/store.yaml"
            },
            "gatsby": {
                "ECOMMERCE_COMPONENTS_PATH": "src/components/ecommerce",
                "PRODUCT_GRAPHQL_TYPE": "Product",
                "GATSBY_ECOMMERCE_INTEGRATION": "true",
                "BUILD_HOOK_PATH": "src/data/store.json"
            },
            "nextjs": {
                "ECOMMERCE_COMPONENTS_PATH": "components/ecommerce",
                "PRODUCT_API_PATH": "pages/api/products",
                "NEXTJS_ECOMMERCE_INTEGRATION": "true"
            },
            "nuxt": {
                "ECOMMERCE_COMPONENTS_PATH": "components/ecommerce",
                "PRODUCT_API_PATH": "server/api/products",
                "NUXT_ECOMMERCE_INTEGRATION": "true"
            }
        }

        return ssg_configs.get(ssg_engine, {})

    def _create_order_processing_infrastructure(self) -> None:
        """Create infrastructure for order processing and management"""

        # Orders table for tracking e-commerce transactions
        self.orders_table = dynamodb.Table(
            self,
            "OrdersTable",
            table_name=f"{self.ssg_config.client_id}-{self.ecommerce_provider}-orders",
            partition_key=dynamodb.Attribute(
                name="order_id",
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

        # Add GSI for customer queries
        self.orders_table.add_global_secondary_index(
            index_name="customer-index",
            partition_key=dynamodb.Attribute(
                name="customer_email",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            )
        )

    def _create_webhook_infrastructure(self) -> None:
        """Create webhook infrastructure for e-commerce provider integration"""

        # Webhook processing Lambda function
        self.webhook_processor = lambda_.Function(
            self,
            "WebhookProcessor",
            function_name=f"{self.ssg_config.client_id}-{self.ecommerce_provider}-webhook",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="webhook.handler",
            code=lambda_.Code.from_asset("lambda/ecommerce-webhook"),
            environment={
                "ORDERS_TABLE": self.orders_table.table_name,
                "ECOMMERCE_PROVIDER": self.ecommerce_provider,
                "STORE_NAME": self.store_name,
                "SSG_ENGINE": self.ssg_config.ssg_engine
            }
        )

        # Grant permissions to webhook processor
        self.orders_table.grant_read_write_data(self.webhook_processor)

        # API Gateway for webhook endpoints
        self.webhook_api = apigateway.RestApi(
            self,
            "WebhookAPI",
            rest_api_name=f"{self.ssg_config.client_id}-{self.ecommerce_provider}-webhooks",
            description=f"Webhook API for {self.ecommerce_provider} e-commerce integration",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200
            )
        )

        # Webhook endpoint integration
        webhook_integration = apigateway.LambdaIntegration(
            self.webhook_processor,
            request_templates={
                "application/json": '{"statusCode": "200"}'
            }
        )

        # Add webhook resource and method
        webhook_resource = self.webhook_api.root.add_resource("webhook")
        webhook_resource.add_method("POST", webhook_integration)

    def _create_notification_infrastructure(self) -> None:
        """Create notification infrastructure for order updates"""

        # SES for order confirmation emails
        self.notification_processor = lambda_.Function(
            self,
            "NotificationProcessor",
            function_name=f"{self.ssg_config.client_id}-{self.ecommerce_provider}-notifications",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="notifications.handler",
            code=lambda_.Code.from_asset("lambda/ecommerce-notifications"),
            environment={
                "STORE_NAME": self.store_name,
                "ECOMMERCE_PROVIDER": self.ecommerce_provider,
                "FROM_EMAIL": f"orders@{self.ssg_config.domain}"
            }
        )

        # Grant SES permissions
        ses_policy = iam.PolicyStatement(
            actions=[
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            resources=[f"arn:aws:ses:*:*:identity/{self.ssg_config.domain}"]
        )
        self.notification_processor.add_to_role_policy(ses_policy)

    def get_ecommerce_provider_info(self) -> Dict[str, Any]:
        """Get detailed information about the selected e-commerce provider"""
        return self.PROVIDER_METADATA.get(self.ecommerce_provider, {})

    def get_compatible_ssg_engines(self) -> List[str]:
        """Get list of SSG engines compatible with this e-commerce provider"""
        return self.COMPATIBLE_SSG_ENGINES.get(self.ecommerce_provider, [])

    def estimate_setup_cost(self) -> Dict[str, int]:
        """Estimate setup cost based on provider complexity and SSG engine"""
        provider_info = self.get_ecommerce_provider_info()
        base_hours = provider_info.get("setup_hours", (4, 8))

        # SSG engine complexity multipliers
        ssg_multipliers = {
            "hugo": 0.8,      # Faster setup, technical users
            "eleventy": 1.0,  # Baseline
            "astro": 1.2,     # Modern features require more setup
            "gatsby": 1.4,    # Complex GraphQL integration
            "nextjs": 1.3,    # React ecosystem complexity
            "nuxt": 1.3       # Vue ecosystem complexity
        }

        multiplier = ssg_multipliers.get(self.ssg_config.ssg_engine, 1.0)
        hourly_rate = 120  # Professional rate

        min_cost = int(base_hours[0] * multiplier * hourly_rate)
        max_cost = int(base_hours[1] * multiplier * hourly_rate)

        return {
            "min_setup_cost": min_cost,
            "max_setup_cost": max_cost,
            "hourly_rate": hourly_rate,
            "estimated_hours": (base_hours[0] * multiplier, base_hours[1] * multiplier)
        }

    @property
    def ecommerce_outputs(self) -> Dict[str, Any]:
        """E-commerce specific outputs for client integration"""
        base_outputs = self.outputs

        ecommerce_outputs = {
            **base_outputs,
            "ecommerce_provider": self.ecommerce_provider,
            "store_name": self.store_name,
            "webhook_url": f"{self.webhook_api.url}webhook",
            "orders_table_name": self.orders_table.table_name,
            "compatible_ssg_engines": self.get_compatible_ssg_engines(),
            "provider_info": self.get_ecommerce_provider_info(),
            "setup_cost_estimate": self.estimate_setup_cost()
        }

        return ecommerce_outputs