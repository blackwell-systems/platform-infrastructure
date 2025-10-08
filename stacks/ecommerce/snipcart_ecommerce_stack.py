"""
Snipcart E-commerce Stack - Flexible SSG Engine Support

This stack demonstrates the e-commerce provider flexibility architecture:

TRANSFORMATION ACHIEVED:
- Before: Only Eleventy + Snipcart (hardcoded pairing)
- After: Hugo/Eleventy/Astro/Gatsby + Snipcart (client choice within provider tier)

BUSINESS BENEFITS:
- Same monthly cost ($85-125) serves multiple technical comfort levels
- Client chooses Snipcart tier for features/budget, then SSG for technical preference
- Revenue optimization through appropriate complexity alignment

CLIENT CHOICE EXAMPLES:
- Technical client: Hugo + Snipcart (fast builds, performance)
- Intermediate client: Eleventy + Snipcart (balanced complexity)
- Modern client: Astro + Snipcart (component islands, modern features)
- Advanced client: Gatsby + Snipcart (React ecosystem, GraphQL)

ARCHITECTURAL PATTERN:
✅ Uses abstract SnipcartProvider for proper separation of concerns
✅ Eliminates code duplication through provider pattern
✅ Enables consistent provider behavior across SSG engines
"""

from typing import Dict, Optional, Any
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ssm as ssm,
    CfnParameter
)

from shared.base.base_ecommerce_stack import BaseEcommerceStack
from shared.providers.ecommerce.snipcart_provider import SnipcartProvider


class SnipcartEcommerceStack(BaseEcommerceStack):
    """
    Snipcart e-commerce stack supporting multiple SSG engines.

    Compatible SSG Engines: Hugo, Eleventy, Astro, Gatsby
    E-commerce Features: Simple setup, 2% transaction fee, $29-99/month
    Monthly Cost: $85-125 (hosting + e-commerce)
    Setup Cost: $960-2,640 (varies by SSG complexity)

    This stack enables clients to:
    1. Choose Snipcart tier for budget-friendly e-commerce features
    2. Select their preferred SSG engine based on technical comfort
    3. Get optimized templates for their specific SSG/Snipcart combination
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        ssg_engine: str = "eleventy",  # Client configurable - not hardcoded!
        store_name: Optional[str] = None,
        currency: str = "USD",
        snipcart_mode: str = "live",  # "test" or "live"
        **kwargs
    ):
        # Validate that selected SSG engine is compatible with Snipcart
        # This validation is handled by BaseEcommerceStack

        super().__init__(
            scope, construct_id, client_id, domain,
            ecommerce_provider="snipcart",
            ssg_engine=ssg_engine,  # Pass through client choice
            store_name=store_name,
            currency=currency,
            **kwargs
        )

        self.snipcart_mode = snipcart_mode

        # ✅ REFACTORED: Use SnipcartProvider pattern instead of hardcoded logic
        # Use the provided store_name parameter directly
        effective_store_name = store_name or f"{client_id.title()} Store"
        provider_config = {
            "store_name": effective_store_name,
            "currency": currency,
            "mode": snipcart_mode
        }

        self.snipcart_provider = SnipcartProvider(provider_config)

        # Setup provider-based infrastructure
        self._setup_provider_integration()
        self._create_snipcart_parameters()

    def _setup_provider_integration(self) -> None:
        """
        ✅ REFACTORED: Use SnipcartProvider pattern for integration setup.

        This eliminates code duplication and uses the abstract provider interface
        for consistent behavior across all Snipcart implementations.
        """

        # Get provider-specific environment variables (replaces hardcoded config)
        provider_vars = self.snipcart_provider.get_environment_variables()
        self.add_environment_variables(provider_vars)

        # Setup provider-specific infrastructure (replaces manual webhook setup)
        self.snipcart_provider.setup_infrastructure(self)

    def _create_snipcart_parameters(self) -> None:
        """Create CDK parameters for Snipcart configuration"""

        # Snipcart API keys (stored in Parameter Store)
        self.snipcart_api_key_param = CfnParameter(
            self,
            "SnipcartApiKey",
            type="String",
            description="Snipcart API key for live mode",
            no_echo=True,
            default=f"/snipcart/{self.ssg_config.client_id}/api-key"
        )

        self.snipcart_test_api_key_param = CfnParameter(
            self,
            "SnipcartTestApiKey",
            type="String",
            description="Snipcart API key for test mode",
            no_echo=True,
            default=f"/snipcart/{self.ssg_config.client_id}/test-api-key"
        )

        self.snipcart_webhook_secret_param = CfnParameter(
            self,
            "SnipcartWebhookSecret",
            type="String",
            description="Snipcart webhook secret for validation",
            no_echo=True,
            default=f"/snipcart/{self.ssg_config.client_id}/webhook-secret"
        )

        # Add parameter references to environment variables
        additional_vars = {
            "SNIPCART_API_KEY": self.snipcart_api_key_param.value_as_string,
            "SNIPCART_TEST_API_KEY": self.snipcart_test_api_key_param.value_as_string,
            "SNIPCART_WEBHOOK_SECRET": self.snipcart_webhook_secret_param.value_as_string
        }

        self.add_environment_variables(additional_vars)

    def get_snipcart_integration_guide(self) -> Dict[str, Any]:
        """
        ✅ REFACTORED: Get integration guide from SnipcartProvider.

        This uses the provider's centralized integration guide instead of
        duplicating integration logic in the stack.
        """
        return self.snipcart_provider.get_client_integration_guide()

    @property
    def snipcart_outputs(self) -> Dict[str, Any]:
        """
        ✅ REFACTORED: Snipcart-specific outputs using provider metadata.

        This uses provider methods to get consistent output information
        instead of hardcoding stack-specific values.
        """
        base_outputs = self.ecommerce_outputs
        provider_metadata = self.snipcart_provider.get_configuration_metadata()

        snipcart_outputs = {
            **base_outputs,
            "snipcart_mode": self.snipcart_mode,
            "provider_metadata": provider_metadata,
            "integration_guide": self.get_snipcart_integration_guide(),
            "webhook_endpoint": self.snipcart_provider.get_webhook_endpoint_name(),
            "required_aws_services": self.snipcart_provider.get_required_aws_services(),
            "template_variant": self.ssg_config.template_variant,
            "ssg_engine_choice": self.ssg_config.ssg_engine
        }

        return snipcart_outputs