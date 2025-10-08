"""
CMS Provider System

Provides a clean, browsable interface to the CMS provider system.
This package organizes CMS providers and configurations into focused,
maintainable modules following the same patterns as the e-commerce provider system.

Key Components:
- CMSProvider: Abstract base class for all CMS integrations
- CMSProviderFactory: Factory for creating and managing CMS provider instances
- Concrete providers: Decap, Tina, Sanity, Contentful implementations

Usage:
    from shared.providers.cms import CMSProviderFactory

    # Get CMS recommendations
    recommendations = CMSProviderFactory.get_cms_recommendations(
        ssg_engine="astro",
        content_volume="medium",
        required_features=["visual_editor"]
    )

    # Create CMS provider
    provider = CMSProviderFactory.create_provider("sanity", config)
    provider.setup_infrastructure(stack)
"""

# Public API - everything users need to import
from .base_provider import (
    CMSProvider,
    CMSProviderConfig,
    CMSType,
    CMSAuthMethod,
    CMSFeatures
)
from .factory import CMSProviderFactory

# Re-export for convenience
__all__ = [
    # Core CMS provider system
    "CMSProvider",
    "CMSProviderConfig",
    "CMSProviderFactory",

    # Type definitions and enums
    "CMSType",
    "CMSAuthMethod",
    "CMSFeatures"
]