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

ARCHITECTURAL PATTERN:
✅ Uses abstract FoxyProvider for proper separation of concerns
✅ Eliminates code duplication through provider pattern
✅ Enables consistent provider behavior across SSG engines
"""

from typing import Dict, Optional, List, Any
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    CfnParameter,
    RemovalPolicy
)

from shared.base.base_ecommerce_stack import BaseEcommerceStack
from shared.providers.ecommerce.foxy_provider import FoxyProvider


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

        # ✅ REFACTORED: Use FoxyProvider pattern instead of hardcoded logic
        # Use the provided store_name parameter directly
        effective_store_name = store_name or f"{client_id.title()} Store"
        provider_config = {
            "store_name": effective_store_name,
            "currency": currency,
            "mode": "live",  # Foxy.io default mode
            "subscription_products": enable_subscriptions,
            "customer_accounts": True,  # Foxy advanced feature
            "multi_currency": False,  # Default, can be overridden
            "advanced_shipping": True,  # Foxy advanced feature
            "tax_calculation": False  # Default, can be overridden
        }

        self.foxy_provider = FoxyProvider(provider_config)

        # Setup provider-based infrastructure
        self._setup_provider_integration()
        self._create_foxy_parameters()

        if enable_subscriptions:
            self._setup_subscription_management()

    def _setup_provider_integration(self) -> None:
        """
        ✅ REFACTORED: Use FoxyProvider pattern for integration setup.

        This eliminates code duplication and uses the abstract provider interface
        for consistent behavior across all Foxy.io implementations.
        """

        # Get provider-specific environment variables (replaces hardcoded config)
        provider_vars = self.foxy_provider.get_environment_variables()
        self.add_environment_variables(provider_vars)

        # Setup provider-specific infrastructure (replaces manual webhook setup)
        self.foxy_provider.setup_infrastructure(self)

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

    def get_foxy_integration_guide(self) -> Dict[str, Any]:
        """
        ✅ REFACTORED: Get integration guide from FoxyProvider.

        This uses the provider's centralized integration guide instead of
        duplicating integration logic in the stack.
        """
        return self.foxy_provider.get_client_integration_guide()

    def get_foxy_advanced_features(self) -> List[str]:
        """
        ✅ REFACTORED: Get advanced features from FoxyProvider metadata.

        This uses the provider's feature list instead of hardcoding features
        in the stack.
        """
        provider_metadata = self.foxy_provider.get_configuration_metadata()
        return provider_metadata.get("features", [])

    @property
    def foxy_outputs(self) -> Dict[str, Any]:
        """
        ✅ REFACTORED: Foxy.io-specific outputs using provider metadata.

        This uses provider methods to get consistent output information
        instead of hardcoding stack-specific values.
        """
        base_outputs = self.ecommerce_outputs
        provider_metadata = self.foxy_provider.get_configuration_metadata()

        foxy_outputs = {
            **base_outputs,
            "foxy_subdomain": self.foxy_subdomain,
            "subscriptions_enabled": str(self.enable_subscriptions),
            "provider_metadata": provider_metadata,
            "integration_guide": self.get_foxy_integration_guide(),
            "advanced_features": self.get_foxy_advanced_features(),
            "webhook_endpoint": self.foxy_provider.get_webhook_endpoint_name(),
            "required_aws_services": self.foxy_provider.get_required_aws_services(),
            "template_variant": self.ssg_config.template_variant,
            "ssg_engine_choice": self.ssg_config.ssg_engine
        }

        if self.enable_subscriptions:
            foxy_outputs.update({
                "subscriptions_table_name": self.subscriptions_table.table_name,
                "subscription_manager_function": self.subscription_manager.function_name
            })

        return foxy_outputs