"""
Abstract Base E-commerce Provider

Defines the interface that all e-commerce providers must implement.
This abstraction allows SSG stacks to support multiple e-commerce platforms
(Snipcart, Foxy.io, Shopify, etc.) without duplicating integration logic.

Design Principles:
- Provider-agnostic infrastructure setup
- Consistent environment variable management
- Standardized configuration metadata
- Clean separation between SSG logic and e-commerce logic
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EcommerceProvider(ABC):
    """
    Abstract base class for all e-commerce provider integrations.

    Each e-commerce provider (Snipcart, Foxy.io, Shopify, etc.) implements
    this interface to provide consistent integration across all SSG stacks.

    The provider is responsible for:
    - Environment variables specific to the e-commerce platform
    - AWS infrastructure setup (Lambda functions, SES, etc.)
    - Configuration metadata for client documentation
    - Cost calculations and business model information
    """

    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """
        Initialize the e-commerce provider.

        Args:
            provider_name: Identifier for this provider (e.g., "snipcart", "foxy")
            config: Provider-specific configuration from StaticSiteConfig.ecommerce_config
        """
        self.provider_name = provider_name
        self.config = config

    @abstractmethod
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get environment variables required by this e-commerce provider.

        Returns variables needed for:
        - Provider API keys and configuration
        - Build-time integration settings
        - Runtime behavior configuration

        Returns:
            Dict of environment variable names to values.
            Values starting with "${...}" are CDK parameters.

        Example:
            {
                "SNIPCART_API_KEY": "${SNIPCART_API_KEY}",
                "STORE_CURRENCY": "USD",
                "PROVIDER_MODE": "live"
            }
        """
        pass

    @abstractmethod
    def setup_infrastructure(self, stack) -> None:
        """
        Set up AWS infrastructure specific to this e-commerce provider.

        This method is called by the SSG stack to create provider-specific
        AWS resources such as:
        - Lambda functions for webhook processing
        - SES configuration for order notifications
        - API Gateway endpoints for provider callbacks
        - DynamoDB tables for order tracking

        Args:
            stack: The CDK stack instance where resources should be created
        """
        pass

    @abstractmethod
    def get_configuration_metadata(self) -> Dict[str, Any]:
        """
        Get provider configuration metadata for client documentation.

        Returns comprehensive information about:
        - Cost structure (monthly fees, transaction fees)
        - Required configuration steps
        - Supported features and payment methods
        - Integration complexity and setup time
        - Documentation links and resources

        Returns:
            Dictionary with standardized provider information

        Example:
            {
                "provider": "snipcart",
                "monthly_cost_range": [29, 99],
                "transaction_fee_percent": 2.0,
                "setup_complexity": "low",
                "features": ["cart", "checkout", "inventory"]
            }
        """
        pass

    @abstractmethod
    def get_required_aws_services(self) -> List[str]:
        """
        Get list of additional AWS services required by this provider.

        Beyond the base SSG infrastructure (S3, CloudFront, Route53),
        e-commerce providers may need additional services.

        Returns:
            List of AWS service names

        Example:
            ["Lambda", "SES", "API Gateway", "DynamoDB"]
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """
        Validate that the provider configuration is complete and correct.

        Checks that required configuration parameters are present
        and have valid values for this provider.

        Returns:
            True if configuration is valid, raises ValueError otherwise

        Raises:
            ValueError: If configuration is invalid with descriptive message
        """
        pass

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return self.provider_name

    def get_config(self) -> Dict[str, Any]:
        """Get the provider configuration"""
        return self.config

    def get_webhook_endpoint_name(self) -> str:
        """
        Get the webhook endpoint name for this provider.

        Default implementation uses provider name, but can be overridden
        for providers that need custom endpoint naming.
        """
        return f"{self.provider_name}-webhook"

    def supports_feature(self, feature: str) -> bool:
        """
        Check if this provider supports a specific feature.

        Args:
            feature: Feature name to check (e.g., "subscriptions", "digital_products")

        Returns:
            True if feature is supported
        """
        metadata = self.get_configuration_metadata()
        supported_features = metadata.get("features", [])
        return feature in supported_features

    def estimate_monthly_cost(self, monthly_sales: float = 0) -> Dict[str, Any]:
        """
        Estimate monthly costs for this provider based on sales volume.

        Args:
            monthly_sales: Expected monthly sales volume in USD

        Returns:
            Cost breakdown dictionary

        Example:
            {
                "base_monthly_fee": 29,
                "transaction_fees": 60,  # 2% of $3000 sales
                "aws_infrastructure": 15,
                "total_estimated": 104
            }
        """
        metadata = self.get_configuration_metadata()
        monthly_range = metadata.get("monthly_cost_range", [0, 0])
        base_fee = monthly_range[0]  # Use minimum base fee for estimation

        transaction_fee_percent = metadata.get("transaction_fee_percent", 0)
        transaction_fees = (monthly_sales * transaction_fee_percent) / 100

        aws_costs = 15  # Estimated AWS costs for Lambda + SES + misc

        return {
            "base_monthly_fee": base_fee,
            "transaction_fees": round(transaction_fees, 2),
            "aws_infrastructure": aws_costs,
            "total_estimated": round(base_fee + transaction_fees + aws_costs, 2),
            "sales_volume": monthly_sales
        }


class EcommerceProviderConfig(BaseModel):
    """
    Configuration model for e-commerce provider validation.

    This model can be used by concrete providers to validate their
    specific configuration requirements using Pydantic.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow"  # Allow provider-specific fields
    )

    provider: str = Field(..., description="E-commerce provider name")
    store_name: Optional[str] = Field(None, description="Display name for the store")
    currency: str = Field(default="USD", description="Store currency code")
    mode: str = Field(default="live", description="Provider mode (live/test/sandbox)")