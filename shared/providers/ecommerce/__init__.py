"""
E-commerce Provider System

Public API for the e-commerce provider abstraction system.
Provides consistent interfaces for integrating various e-commerce
platforms (Snipcart, Foxy.io, Shopify, etc.) with SSG stacks.

Usage:
    from shared.providers.ecommerce import EcommerceProviderFactory, EcommerceProvider

    # Create a provider instance
    provider = EcommerceProviderFactory.create_provider("snipcart", config)

    # Use in CDK stack
    provider.setup_infrastructure(stack)
    env_vars = provider.get_environment_variables()
"""

from .base_provider import EcommerceProvider, EcommerceProviderConfig
from .factory import EcommerceProviderFactory
from .snipcart_provider import SnipcartProvider

# Public API exports
__all__ = [
    # Core abstractions
    "EcommerceProvider",
    "EcommerceProviderConfig",
    "EcommerceProviderFactory",

    # Concrete providers
    "SnipcartProvider",
]

# Version information
__version__ = "1.0.0"