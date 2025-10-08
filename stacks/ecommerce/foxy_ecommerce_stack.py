"""
Foxy.io E-commerce Stack - Advanced E-commerce with SSG Flexibility

This stack demonstrates advanced e-commerce provider flexibility:

TRANSFORMATION ACHIEVED:
- Before: Only Astro + Foxy.io (hardcoded pairing)
- After: Hugo/Eleventy/Astro/Gatsby + Foxy.io (client choice within provider tier)

BUSINESS BENEFITS:
- Same monthly cost ($100-150) serves multiple technical comfort levels
- Client chooses Foxy tier for advanced features, then SSG for technical preference
- Higher complexity providers support sophisticated client technical requirements

CLIENT CHOICE EXAMPLES:
- Performance-focused: Hugo + Foxy (fastest builds, advanced e-commerce)
- Balanced complexity: Eleventy + Foxy (simple builds, advanced features)
- Modern features: Astro + Foxy (component islands, advanced e-commerce)
- React ecosystem: Gatsby + Foxy (GraphQL, React components, advanced features)

ADVANCED FEATURES:
- Subscription management
- Advanced cart customization
- Custom checkout flows
- API access for integrations
- Advanced analytics and reporting
"""

from typing import Dict, Optional, List
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    CfnParameter,
    RemovalPolicy
)

from stacks.shared.base_ecommerce_stack import BaseEcommerceStack


class FoxyEcommerceStack(BaseEcommerceStack):
    """
    Foxy.io e-commerce stack supporting multiple SSG engines.

    Compatible SSG Engines: Hugo, Eleventy, Astro, Gatsby
    E-commerce Features: Advanced features, 1.5% transaction fee, $75-300/month
    Monthly Cost: $100-150 (hosting + e-commerce)
    Setup Cost: $1,200-3,000 (varies by SSG complexity)

    Advanced Features:
    - Subscription and recurring billing management
    - Advanced cart customization and rules
    - Custom checkout flow configuration
    - Comprehensive API access for integrations
    - Advanced analytics and customer insights
    - Multi-currency and international shipping
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        ssg_engine: str = "astro",  # Astro default for Foxy advanced features
        store_name: Optional[str] = None,
        currency: str = "USD",
        foxy_subdomain: Optional[str] = None,
        enable_subscriptions: bool = True,
        **kwargs
    ):
        super().__init__(
            scope, construct_id, client_id, domain,
            ecommerce_provider="foxy",
            ssg_engine=ssg_engine,  # Client choice within Foxy tier
            store_name=store_name,
            currency=currency,
            **kwargs
        )

        self.foxy_subdomain = foxy_subdomain or f"{client_id}-store"
        self.enable_subscriptions = enable_subscriptions

        # Add Foxy-specific infrastructure
        self._setup_foxy_integration()
        self._setup_foxy_advanced_features()
        self._create_foxy_parameters()

        if enable_subscriptions:
            self._setup_subscription_management()

    def _setup_foxy_integration(self) -> None:
        """Set up Foxy.io specific infrastructure and configuration"""

        # Base Foxy configuration
        foxy_vars = {
            "FOXY_ENABLED": "true",
            "FOXY_VERSION": "2.0",
            "FOXY_SUBDOMAIN": self.foxy_subdomain,
            "FOXY_CURRENCY": self.currency,
            "FOXY_STORE_NAME": self.store_name,
            "FOXY_SUBSCRIPTIONS_ENABLED": str(self.enable_subscriptions).lower()
        }

        # SSG-specific Foxy configuration
        ssg_specific_vars = self._get_ssg_specific_foxy_config()
        foxy_vars.update(ssg_specific_vars)

        self.add_environment_variables(foxy_vars)

    def _get_ssg_specific_foxy_config(self) -> Dict[str, str]:
        """
        Get SSG-specific Foxy.io configuration.

        Foxy.io's advanced features require more sophisticated integration
        patterns that vary by SSG engine capabilities.
        """
        ssg_engine = self.ssg_config.ssg_engine

        ssg_configs = {
            "eleventy": {
                "FOXY_TEMPLATES_PATH": "src/_includes/foxy",
                "PRODUCT_DATA_PATH": "src/_data/products.json",
                "SUBSCRIPTION_DATA_PATH": "src/_data/subscriptions.json",
                "ELEVENTY_FOXY_INTEGRATION": "true",
                "FOXY_CART_TYPE": "eleventy_data_driven"
            },
            "astro": {
                "FOXY_COMPONENTS_PATH": "src/components/foxy",
                "PRODUCT_DATA_PATH": "src/data/products.json",
                "SUBSCRIPTION_DATA_PATH": "src/data/subscriptions.json",
                "ASTRO_FOXY_INTEGRATION": "true",
                "ASTRO_FOXY_ISLANDS": "true",
                "FOXY_CART_TYPE": "astro_component_islands"
            },
            "hugo": {
                "FOXY_LAYOUTS_PATH": "layouts/foxy",
                "PRODUCT_DATA_PATH": "data/products.yaml",
                "SUBSCRIPTION_DATA_PATH": "data/subscriptions.yaml",
                "HUGO_FOXY_INTEGRATION": "true",
                "FOXY_CART_TYPE": "hugo_shortcodes"
            },
            "gatsby": {
                "FOXY_COMPONENTS_PATH": "src/components/foxy",
                "PRODUCT_GRAPHQL_TYPE": "FoxyProduct",
                "SUBSCRIPTION_GRAPHQL_TYPE": "FoxySubscription",
                "GATSBY_FOXY_INTEGRATION": "true",
                "FOXY_CART_TYPE": "gatsby_graphql_react"
            }
        }

        return ssg_configs.get(ssg_engine, {})

    def _setup_foxy_advanced_features(self) -> None:
        """Set up Foxy.io advanced features infrastructure"""

        # Advanced webhook processing for Foxy events
        self.foxy_webhook_processor = lambda_.Function(
            self,
            "FoxyWebhookProcessor",
            function_name=f"{self.ssg_config.client_id}-foxy-webhook-processor",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="foxy_webhook.handler",
            code=lambda_.Code.from_asset("lambda/foxy-webhook"),
            environment={
                "ORDERS_TABLE": self.orders_table.table_name,
                "FOXY_SUBDOMAIN": self.foxy_subdomain,
                "STORE_NAME": self.store_name,
                "SSG_ENGINE": self.ssg_config.ssg_engine,
                "SUBSCRIPTIONS_ENABLED": str(self.enable_subscriptions).lower(),
                "NOTIFICATION_FUNCTION": self.notification_processor.function_name
            }
        )

        # Grant permissions
        self.orders_table.grant_read_write_data(self.foxy_webhook_processor)
        self.notification_processor.grant_invoke(self.foxy_webhook_processor)

        # Add Foxy webhook endpoints to API Gateway
        foxy_resource = self.webhook_api.root.add_resource("foxy")

        # Foxy webhook integration
        foxy_integration = apigateway.LambdaIntegration(
            self.foxy_webhook_processor,
            request_templates={
                "application/json": '{"statusCode": "200"}'
            }
        )

        # Foxy specific webhook endpoints
        foxy_resource.add_method("POST", foxy_integration)

        # Advanced Foxy event endpoints
        transaction_events = foxy_resource.add_resource("transaction")
        transaction_events.add_method("POST", foxy_integration)

        subscription_events = foxy_resource.add_resource("subscription")
        subscription_events.add_method("POST", foxy_integration)

        customer_events = foxy_resource.add_resource("customer")
        customer_events.add_method("POST", foxy_integration)

        # Cart abandonment webhook
        cart_events = foxy_resource.add_resource("cart")
        cart_events.add_method("POST", foxy_integration)

    def _setup_subscription_management(self) -> None:
        """Set up subscription management infrastructure (Foxy advanced feature)"""

        # Subscriptions table for managing recurring billing
        self.subscriptions_table = dynamodb.Table(
            self,
            "SubscriptionsTable",
            table_name=f"{self.ssg_config.client_id}-foxy-subscriptions",
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

        # GSI for subscription status tracking
        self.subscriptions_table.add_global_secondary_index(
            index_name="status-expiry",
            partition_key=dynamodb.Attribute(
                name="subscription_status",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="next_billing_date",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Subscription management Lambda
        self.subscription_manager = lambda_.Function(
            self,
            "SubscriptionManager",
            function_name=f"{self.ssg_config.client_id}-foxy-subscription-manager",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="subscription_manager.handler",
            code=lambda_.Code.from_asset("lambda/foxy-subscriptions"),
            environment={
                "SUBSCRIPTIONS_TABLE": self.subscriptions_table.table_name,
                "ORDERS_TABLE": self.orders_table.table_name,
                "FOXY_SUBDOMAIN": self.foxy_subdomain,
                "SSG_ENGINE": self.ssg_config.ssg_engine
            }
        )

        # Grant permissions
        self.subscriptions_table.grant_read_write_data(self.subscription_manager)
        self.orders_table.grant_read_write_data(self.subscription_manager)

        # Update webhook processor environment
        self.foxy_webhook_processor.add_environment(
            "SUBSCRIPTIONS_TABLE", self.subscriptions_table.table_name
        )
        self.subscriptions_table.grant_read_write_data(self.foxy_webhook_processor)

    def _create_foxy_parameters(self) -> None:
        """Create CDK parameters for Foxy.io configuration"""

        # Foxy API credentials
        self.foxy_client_id_param = CfnParameter(
            self,
            "FoxyClientId",
            type="String",
            description="Foxy.io OAuth client ID",
            no_echo=True,
            default=f"/foxy/{self.ssg_config.client_id}/client-id"
        )

        self.foxy_client_secret_param = CfnParameter(
            self,
            "FoxyClientSecret",
            type="String",
            description="Foxy.io OAuth client secret",
            no_echo=True,
            default=f"/foxy/{self.ssg_config.client_id}/client-secret"
        )

        self.foxy_webhook_key_param = CfnParameter(
            self,
            "FoxyWebhookKey",
            type="String",
            description="Foxy.io webhook encryption key",
            no_echo=True,
            default=f"/foxy/{self.ssg_config.client_id}/webhook-key"
        )

        self.foxy_api_key_param = CfnParameter(
            self,
            "FoxyApiKey",
            type="String",
            description="Foxy.io API key for advanced features",
            no_echo=True,
            default=f"/foxy/{self.ssg_config.client_id}/api-key"
        )

        # Add parameter references to environment variables
        additional_vars = {
            "FOXY_CLIENT_ID": self.foxy_client_id_param.value_as_string,
            "FOXY_CLIENT_SECRET": self.foxy_client_secret_param.value_as_string,
            "FOXY_WEBHOOK_KEY": self.foxy_webhook_key_param.value_as_string,
            "FOXY_API_KEY": self.foxy_api_key_param.value_as_string
        }

        self.add_environment_variables(additional_vars)

    def get_foxy_integration_guide(self) -> Dict[str, str]:
        """
        Get SSG-specific integration guide for Foxy.io advanced features.

        Foxy.io's advanced capabilities require more sophisticated integration
        patterns that vary significantly by SSG engine.
        """
        ssg_engine = self.ssg_config.ssg_engine

        integration_guides = {
            "eleventy": {
                "setup_instructions": "Configure Foxy cart with Eleventy data cascade, advanced templating",
                "template_location": "src/_includes/foxy/",
                "data_format": "JSON with subscription schemas",
                "build_integration": "Eleventy computed data with Foxy API integration",
                "advanced_features": "Subscription templates, cart abandonment, customer portals",
                "example_product": """
                {
                  "id": "subscription-1",
                  "name": "Monthly Subscription",
                  "price": 29.99,
                  "frequency": "1m",
                  "subscription_frequency": "monthly",
                  "foxy_product_code": "SUB001"
                }
                """
            },
            "astro": {
                "setup_instructions": "Use Astro islands for advanced Foxy features, subscription management",
                "template_location": "src/components/foxy/",
                "data_format": "JSON with TypeScript interfaces",
                "build_integration": "Astro component islands with Foxy advanced cart functionality",
                "advanced_features": "Subscription islands, customer portal components, cart abandonment",
                "example_product": """
                <FoxySubscriptionProduct
                  id="subscription-1"
                  name="Monthly Subscription"
                  price={29.99}
                  frequency="1m"
                  client:load
                />
                """
            },
            "hugo": {
                "setup_instructions": "Hugo shortcodes and partials for Foxy advanced integration",
                "template_location": "layouts/foxy/",
                "data_format": "YAML with subscription schemas",
                "build_integration": "Hugo data templates with Foxy API calls during build",
                "advanced_features": "Subscription shortcodes, customer portal partials",
                "example_product": """
                - id: subscription-1
                  name: Monthly Subscription
                  price: 29.99
                  frequency: 1m
                  subscription_frequency: monthly
                  foxy_product_code: SUB001
                """
            },
            "gatsby": {
                "setup_instructions": "GraphQL schema extensions for Foxy advanced features with React",
                "template_location": "src/components/foxy/",
                "data_format": "GraphQL with subscription types",
                "build_integration": "Gatsby GraphQL with Foxy API source plugin, React components",
                "advanced_features": "Subscription GraphQL queries, customer portal pages, cart state management",
                "example_product": """
                query FoxySubscriptions {
                  allFoxySubscription {
                    nodes {
                      id
                      name
                      price
                      frequency
                      subscriptionFrequency
                      foxyProductCode
                      customerPortalUrl
                    }
                  }
                }
                """
            }
        }

        return integration_guides.get(ssg_engine, {})

    def get_foxy_advanced_features(self) -> List[Dict[str, str]]:
        """Get list of Foxy.io advanced features available with this stack"""
        return [
            {
                "name": "Subscription Management",
                "description": "Recurring billing and subscription lifecycle management",
                "ssg_integration": f"Integrated with {self.ssg_config.ssg_engine} templates and data"
            },
            {
                "name": "Advanced Cart Rules",
                "description": "Complex pricing rules, discounts, and cart behavior customization",
                "ssg_integration": f"Template-driven cart configuration for {self.ssg_config.ssg_engine}"
            },
            {
                "name": "Customer Portal",
                "description": "Self-service customer account management and subscription control",
                "ssg_integration": f"Embedded in {self.ssg_config.ssg_engine} site with SSO integration"
            },
            {
                "name": "Advanced Analytics",
                "description": "Detailed customer behavior tracking and business intelligence",
                "ssg_integration": f"Data integration with {self.ssg_config.ssg_engine} build process"
            },
            {
                "name": "API Access",
                "description": "Full REST API access for custom integrations and automation",
                "ssg_integration": f"Build-time API integration with {self.ssg_config.ssg_engine}"
            },
            {
                "name": "Multi-Currency Support",
                "description": "International commerce with automatic currency conversion",
                "ssg_integration": f"Locale-aware templates in {self.ssg_config.ssg_engine}"
            }
        ]

    @property
    def foxy_outputs(self) -> Dict[str, str]:
        """Foxy.io-specific outputs for client integration"""
        base_outputs = self.ecommerce_outputs

        foxy_outputs = {
            **base_outputs,
            "foxy_subdomain": self.foxy_subdomain,
            "foxy_store_url": f"https://{self.foxy_subdomain}.foxycart.com",
            "foxy_webhook_url": f"{self.webhook_api.url}foxy",
            "foxy_transaction_webhook_url": f"{self.webhook_api.url}foxy/transaction",
            "foxy_subscription_webhook_url": f"{self.webhook_api.url}foxy/subscription",
            "foxy_customer_webhook_url": f"{self.webhook_api.url}foxy/customer",
            "subscriptions_enabled": str(self.enable_subscriptions),
            "integration_guide": str(self.get_foxy_integration_guide()),
            "advanced_features": str(self.get_foxy_advanced_features()),
            "template_variant": self.ssg_config.template_variant,
            "ssg_engine_choice": self.ssg_config.ssg_engine
        }

        if self.enable_subscriptions:
            foxy_outputs.update({
                "subscriptions_table_name": self.subscriptions_table.table_name,
                "subscription_manager_function": self.subscription_manager.function_name
            })

        return foxy_outputs