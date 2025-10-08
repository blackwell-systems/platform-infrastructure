"""
E-commerce Provider Factory

Factory class for creating e-commerce provider instances.
Follows the same pattern as SSGEngineFactory to maintain consistency
across the platform architecture.

Supported Providers:
- Snipcart: JavaScript-based e-commerce with minimal backend
- Foxy.io: Advanced e-commerce with subscription support (future)
- Shopify: Headless Shopify integration (future)

Usage:
    provider = EcommerceProviderFactory.create_provider("snipcart", config)
    provider.setup_infrastructure(stack)
"""

from typing import Dict, Any, List, Type, Optional
from .base_provider import EcommerceProvider
from .snipcart_provider import SnipcartProvider


class EcommerceProviderFactory:
    """
    Factory for creating e-commerce provider instances.

    Provides a consistent interface for instantiating different
    e-commerce providers based on provider name and configuration.
    """

    # Registry of available providers
    _providers: Dict[str, Type[EcommerceProvider]] = {
        "snipcart": SnipcartProvider,
        # Future providers will be added here:
        # "foxy": FoxyProvider,
        # "shopify_basic": ShopifyBasicProvider,
        # "shopify_advanced": ShopifyAdvancedProvider,
        # "shopify_headless": ShopifyHeadlessProvider,
        # "woocommerce": WooCommerceProvider,
        # "custom_api": CustomApiProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str, config: Dict[str, Any]) -> EcommerceProvider:
        """
        Create an e-commerce provider instance.

        Args:
            provider_name: Name of the e-commerce provider (e.g., "snipcart")
            config: Provider-specific configuration dictionary

        Returns:
            EcommerceProvider instance for the specified provider

        Raises:
            ValueError: If provider_name is not supported

        Example:
            config = {"store_name": "My Store", "currency": "USD"}
            provider = EcommerceProviderFactory.create_provider("snipcart", config)
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported e-commerce provider '{provider_name}'. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available e-commerce provider names.

        Returns:
            List of supported provider names
        """
        return list(cls._providers.keys())

    @classmethod
    def get_provider_metadata(cls, provider_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific provider without instantiating it.

        Args:
            provider_name: Name of the e-commerce provider

        Returns:
            Provider metadata dictionary

        Raises:
            ValueError: If provider_name is not supported
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported e-commerce provider '{provider_name}'. "
                f"Available providers: {available}"
            )

        # Create a temporary instance with minimal config to get metadata
        provider_class = cls._providers[provider_name]
        temp_provider = provider_class({})  # Most providers handle empty config for metadata
        return temp_provider.get_configuration_metadata()

    @classmethod
    def get_all_providers_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all available providers.

        Returns:
            Dictionary mapping provider names to their metadata

        Example:
            {
                "snipcart": {
                    "monthly_cost_range": [29, 99],
                    "transaction_fee_percent": 2.0,
                    "features": ["cart", "checkout", "inventory"]
                }
            }
        """
        metadata = {}
        for provider_name in cls._providers.keys():
            try:
                metadata[provider_name] = cls.get_provider_metadata(provider_name)
            except Exception as e:
                # Log error but continue with other providers
                print(f"Warning: Could not get metadata for {provider_name}: {e}")
                metadata[provider_name] = {"error": str(e)}

        return metadata

    @classmethod
    def get_providers_by_feature(cls, feature: str) -> List[str]:
        """
        Get providers that support a specific feature.

        Args:
            feature: Feature name to search for (e.g., "subscriptions", "digital_products")

        Returns:
            List of provider names that support the feature

        Example:
            subscription_providers = EcommerceProviderFactory.get_providers_by_feature("subscriptions")
            # Returns: ["snipcart", "foxy"]
        """
        supporting_providers = []

        for provider_name in cls._providers.keys():
            try:
                metadata = cls.get_provider_metadata(provider_name)
                features = metadata.get("features", [])
                if feature in features:
                    supporting_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return supporting_providers

    @classmethod
    def get_providers_by_cost_range(cls, max_monthly_cost: float) -> List[str]:
        """
        Get providers within a specific monthly cost range.

        Args:
            max_monthly_cost: Maximum acceptable monthly cost

        Returns:
            List of provider names within the cost range

        Example:
            budget_providers = EcommerceProviderFactory.get_providers_by_cost_range(50)
            # Returns providers with monthly costs under $50
        """
        affordable_providers = []

        for provider_name in cls._providers.keys():
            try:
                metadata = cls.get_provider_metadata(provider_name)
                cost_range = metadata.get("monthly_cost_range", [0, 0])
                min_cost = cost_range[0] if cost_range else 0

                if min_cost <= max_monthly_cost:
                    affordable_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return affordable_providers

    @classmethod
    def get_recommended_provider(
        cls,
        store_type: str = "simple",
        monthly_sales: float = 1000,
        required_features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get recommended provider based on store requirements.

        Args:
            store_type: Type of store ("simple", "advanced", "enterprise")
            monthly_sales: Expected monthly sales volume
            required_features: List of required features

        Returns:
            Dictionary with recommended provider and reasoning

        Example:
            recommendation = EcommerceProviderFactory.get_recommended_provider(
                store_type="simple",
                monthly_sales=2000,
                required_features=["subscriptions"]
            )
        """
        required_features = required_features or []

        # Get all provider metadata
        all_metadata = cls.get_all_providers_metadata()

        recommendations = []

        for provider_name, metadata in all_metadata.items():
            if "error" in metadata:
                continue

            # Check feature requirements
            features = metadata.get("features", [])
            if not all(feature in features for feature in required_features):
                continue

            # Calculate cost score (lower is better)
            cost_range = metadata.get("monthly_cost_range", [0, 0])
            transaction_fee = metadata.get("transaction_fee_percent", 0)
            monthly_cost = cost_range[0] + (monthly_sales * transaction_fee / 100)

            # Score based on store type and complexity
            complexity_score = cls._get_complexity_score(store_type, metadata)

            recommendations.append({
                "provider": provider_name,
                "monthly_cost_estimate": monthly_cost,
                "complexity_score": complexity_score,
                "features": features,
                "setup_hours": metadata.get("estimated_setup_hours", 0),
                "metadata": metadata
            })

        # Sort by complexity score (ascending) then by cost
        recommendations.sort(key=lambda x: (x["complexity_score"], x["monthly_cost_estimate"]))

        if recommendations:
            best = recommendations[0]
            return {
                "recommended_provider": best["provider"],
                "reason": cls._get_recommendation_reason(best, store_type, monthly_sales),
                "estimated_monthly_cost": best["monthly_cost_estimate"],
                "setup_time_hours": best["setup_hours"],
                "alternatives": [r["provider"] for r in recommendations[1:3]]  # Top 3 alternatives
            }
        else:
            return {
                "recommended_provider": None,
                "reason": "No providers match the specified requirements",
                "alternatives": list(cls._providers.keys())
            }

    @classmethod
    def _get_complexity_score(cls, store_type: str, metadata: Dict[str, Any]) -> int:
        """Get complexity score for store type matching"""
        setup_complexity = metadata.get("setup_complexity", "medium")

        complexity_scores = {
            "simple": {"low": 1, "medium": 2, "high": 3},
            "advanced": {"low": 2, "medium": 1, "high": 2},
            "enterprise": {"low": 3, "medium": 2, "high": 1}
        }

        return complexity_scores.get(store_type, {}).get(setup_complexity, 2)

    @classmethod
    def _get_recommendation_reason(cls, recommendation: Dict[str, Any], store_type: str, monthly_sales: float) -> str:
        """Generate human-readable recommendation reason"""
        provider = recommendation["provider"]
        cost = recommendation["monthly_cost_estimate"]
        hours = recommendation["setup_hours"]

        return (
            f"{provider.title()} is recommended for {store_type} stores because it offers "
            f"the best balance of features, cost (${cost:.0f}/month estimated), and "
            f"setup time ({hours} hours). It matches your store complexity requirements."
        )

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[EcommerceProvider]) -> None:
        """
        Register a new e-commerce provider.

        This method allows for dynamic provider registration,
        useful for plugins or custom integrations.

        Args:
            name: Provider name
            provider_class: Provider class that extends EcommerceProvider
        """
        if not issubclass(provider_class, EcommerceProvider):
            raise ValueError(f"Provider class must extend EcommerceProvider")

        cls._providers[name] = provider_class

    @classmethod
    def is_provider_supported(cls, provider_name: str) -> bool:
        """
        Check if a provider is supported.

        Args:
            provider_name: Name of the provider to check

        Returns:
            True if provider is supported
        """
        return provider_name in cls._providers