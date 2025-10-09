"""
Client Configuration Compatibility Adapter

This module provides compatibility between the new ClientServiceConfig model
and the existing EventDrivenIntegrationLayer that expects the legacy ClientConfig.

This adapter ensures seamless integration without breaking existing functionality
while enabling the new dual-mode architecture.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, computed_field

from models.service_config import ClientServiceConfig


class LegacyClientConfig(BaseModel):
    """
    Legacy ClientConfig compatibility model for EventDrivenIntegrationLayer.

    This model provides the interface expected by the existing EventDrivenIntegrationLayer
    while being populated from the new ClientServiceConfig.
    """

    client_id: str = Field(..., description="Unique client identifier")
    company_name: str = Field(..., description="Client company name")
    domain: str = Field(..., description="Primary domain for the client")
    contact_email: str = Field(..., description="Primary contact email")

    @computed_field
    @property
    def resource_prefix(self) -> str:
        """Generate resource prefix for AWS resources"""
        return f"webservices-{self.client_id.lower().replace('_', '-')}"


class ClientConfigAdapter:
    """
    Adapter class to convert between ClientServiceConfig and legacy ClientConfig.

    This adapter enables the new dual-mode stacks to work with the existing
    EventDrivenIntegrationLayer without requiring changes to the integration layer.
    """

    @staticmethod
    def to_legacy_config(client_service_config: ClientServiceConfig) -> LegacyClientConfig:
        """
        Convert ClientServiceConfig to legacy ClientConfig format.

        Args:
            client_service_config: New configuration model

        Returns:
            LegacyClientConfig compatible with EventDrivenIntegrationLayer
        """

        return LegacyClientConfig(
            client_id=client_service_config.client_id,
            company_name=client_service_config.company_name,
            domain=client_service_config.domain,
            contact_email=client_service_config.contact_email
        )

    @staticmethod
    def create_integration_layer_compatible_config(
        client_service_config: ClientServiceConfig
    ) -> Dict[str, Any]:
        """
        Create a configuration dictionary that's compatible with EventDrivenIntegrationLayer.

        This method extracts the necessary information from ClientServiceConfig
        and formats it for use with the existing integration layer.
        """

        legacy_config = ClientConfigAdapter.to_legacy_config(client_service_config)

        return {
            "client_config": legacy_config,
            "integration_mode": client_service_config.service_integration.integration_mode,
            "providers": {
                "cms": {
                    "provider": client_service_config.service_integration.cms_config.provider if client_service_config.service_integration.cms_config else None,
                    "settings": client_service_config.service_integration.cms_config.settings if client_service_config.service_integration.cms_config else {}
                },
                "ecommerce": {
                    "provider": client_service_config.service_integration.ecommerce_config.provider if client_service_config.service_integration.ecommerce_config else None,
                    "settings": client_service_config.service_integration.ecommerce_config.settings if client_service_config.service_integration.ecommerce_config else {}
                }
            },
            "ssg_engine": client_service_config.service_integration.ssg_engine
        }

    @staticmethod
    def get_webhook_endpoints_mapping(client_service_config: ClientServiceConfig) -> Dict[str, str]:
        """
        Generate webhook endpoint mappings for the configured providers.

        This method creates the webhook URL mappings that providers need
        for configuring their webhook endpoints.
        """

        base_url = f"https://api.{client_service_config.domain}"

        endpoints = {
            "base_url": base_url,
            "health_check": f"{base_url}/health"
        }

        # Add CMS webhook endpoints
        if client_service_config.service_integration.cms_config:
            cms_provider = client_service_config.service_integration.cms_config.provider
            endpoints[f"{cms_provider}_webhook"] = f"{base_url}/webhooks/{cms_provider}"

        # Add E-commerce webhook endpoints
        if client_service_config.service_integration.ecommerce_config:
            ecommerce_provider = client_service_config.service_integration.ecommerce_config.provider
            endpoints[f"{ecommerce_provider}_webhook"] = f"{base_url}/webhooks/{ecommerce_provider}"

        return endpoints

    @staticmethod
    def validate_integration_layer_compatibility(
        client_service_config: ClientServiceConfig
    ) -> Dict[str, Any]:
        """
        Validate that the ClientServiceConfig is compatible with EventDrivenIntegrationLayer.

        Returns validation results and any compatibility issues found.
        """

        issues = []
        warnings = []

        # Check required fields
        if not client_service_config.client_id:
            issues.append("client_id is required for integration layer")

        if not client_service_config.domain:
            issues.append("domain is required for webhook configuration")

        # Check integration mode
        from models.service_config import IntegrationMode
        if client_service_config.service_integration.integration_mode == IntegrationMode.DIRECT:
            warnings.append("Direct mode does not use EventDrivenIntegrationLayer")

        # Check provider configuration
        has_cms = client_service_config.service_integration.cms_config is not None
        has_ecommerce = client_service_config.service_integration.ecommerce_config is not None

        if not has_cms and not has_ecommerce:
            issues.append("At least one provider (CMS or E-commerce) must be configured")

        # Check supported providers
        supported_cms = ["decap", "tina", "sanity", "contentful"]
        supported_ecommerce = ["snipcart", "foxy", "shopify_basic"]

        if has_cms:
            cms_provider = client_service_config.service_integration.cms_config.provider
            if cms_provider not in supported_cms:
                issues.append(f"CMS provider '{cms_provider}' not supported by integration layer")

        if has_ecommerce:
            ecommerce_provider = client_service_config.service_integration.ecommerce_config.provider
            if ecommerce_provider not in supported_ecommerce:
                issues.append(f"E-commerce provider '{ecommerce_provider}' not supported by integration layer")

        return {
            "is_compatible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "supported_cms_providers": supported_cms,
            "supported_ecommerce_providers": supported_ecommerce
        }


def create_compatible_integration_layer(
    scope,
    client_service_config: ClientServiceConfig,
    **kwargs
):
    """
    Factory function to create EventDrivenIntegrationLayer with ClientServiceConfig.

    This function handles the compatibility conversion and creates the integration
    layer using the legacy interface while accepting the new configuration model.
    """

    from shared.composition.integration_layer import EventDrivenIntegrationLayer

    # Convert to legacy format
    legacy_config = ClientConfigAdapter.to_legacy_config(client_service_config)

    # Create integration layer with compatible config
    integration_layer = EventDrivenIntegrationLayer(
        scope=scope,
        construct_id=f"{client_service_config.client_id}-integration-layer",
        client_config=legacy_config,
        **kwargs
    )

    return integration_layer


# Export the main classes and functions
__all__ = [
    "LegacyClientConfig",
    "ClientConfigAdapter",
    "create_compatible_integration_layer"
]