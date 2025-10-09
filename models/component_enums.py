"""
Component Enums for Stack Configuration

Centralized enum definitions for all stack component names including SSG engines,
CMS providers, and e-commerce providers. These replace scattered literal types
throughout the configuration system to provide better type safety and validation.

Usage:
    from models.component_enums import SSGEngine, CMSProvider, EcommerceProvider

    # Type-safe provider selection
    cms_config = CMSProviderConfig(
        provider=CMSProvider.TINA,
        admin_users=["admin@example.com"]
    )

    # SSG engine selection with validation
    service_config = ServiceIntegrationConfig(
        ssg_engine=SSGEngine.ASTRO,
        service_type=ServiceType.CMS_TIER
    )
"""

from enum import Enum


class SSGEngine(str, Enum):
    """
    Static Site Generator engines supported by the platform.

    Each SSG engine has different characteristics in terms of build speed,
    complexity, and ecosystem compatibility.
    """

    # Performance-focused engines
    ELEVENTY = "eleventy"    # Node.js, very fast builds, flexible templating
    HUGO = "hugo"            # Go-based, fastest builds, technical users

    # Modern component-based engines
    ASTRO = "astro"          # Component islands, modern web standards

    # Traditional engines
    JEKYLL = "jekyll"        # Ruby-based, GitHub Pages compatible

    # React ecosystem
    NEXTJS = "nextjs"        # React framework, enterprise features
    GATSBY = "gatsby"        # React + GraphQL, rich plugin ecosystem

    # Vue ecosystem
    NUXT = "nuxt"            # Vue framework, SSR/SSG hybrid


class CMSProvider(str, Enum):
    """
    Content Management System providers supported by the platform.

    Each CMS provider offers different approaches to content management,
    from git-based workflows to API-first headless CMS solutions.
    """

    # Git-based CMS (free/low-cost)
    DECAP = "decap"          # Git-based, open source, self-hosted
    TINA = "tina"            # Git-based with visual editing, hybrid approach

    # API-based CMS (scalable)
    SANITY = "sanity"        # Structured content, real-time APIs, GROQ queries
    CONTENTFUL = "contentful" # Enterprise CMS, rich APIs, team collaboration


class EcommerceProvider(str, Enum):
    """
    E-commerce platform providers supported by the platform.

    Each provider offers different feature sets, pricing models, and integration
    complexity levels for e-commerce functionality.
    """

    # JAMstack-friendly providers
    SNIPCART = "snipcart"                # JavaScript-based, simple integration
    FOXY = "foxy"                        # Advanced features, subscriptions

    # Shopify variants
    SHOPIFY_BASIC = "shopify_basic"      # Standard Shopify plan
    SHOPIFY_ADVANCED = "shopify_advanced" # Advanced Shopify features
    SHOPIFY_HEADLESS = "shopify_headless" # Shopify Storefront API only

    # Other platforms
    WOOCOMMERCE = "woocommerce"          # WordPress-based e-commerce
    CUSTOM_API = "custom_api"            # Custom e-commerce backend

    # No e-commerce
    NONE = "none"                        # Content-only sites


class ProviderType(str, Enum):
    """
    High-level provider type classification for composition architecture.
    """
    CMS = "cms"
    ECOMMERCE = "ecommerce"


class Environment(str, Enum):
    """
    Deployment environment types supported by the platform.
    """
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


class IntegrationLevel(str, Enum):
    """
    Integration complexity levels for composed stacks.
    """
    MINIMAL = "minimal"      # Basic integration with minimal features
    STANDARD = "standard"    # Standard integration with common features
    FULL = "full"           # Full integration with all advanced features


class InventoryPolicy(str, Enum):
    """
    Inventory management policies for e-commerce products.
    """
    DENY = "deny"           # Deny sales when out of stock
    CONTINUE = "continue"   # Allow sales when out of stock


class HTTPMethod(str, Enum):
    """
    HTTP methods supported for webhook endpoints.
    """
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"


class EventType(str, Enum):
    """
    Content event types supported by the composition system.
    """
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    INVENTORY_UPDATED = "inventory.updated"
    COLLECTION_CREATED = "collection.created"
    COLLECTION_UPDATED = "collection.updated"


# Convenience mappings for backwards compatibility and easy access
SSG_ENGINES = {
    "eleventy": SSGEngine.ELEVENTY,
    "hugo": SSGEngine.HUGO,
    "astro": SSGEngine.ASTRO,
    "jekyll": SSGEngine.JEKYLL,
    "nextjs": SSGEngine.NEXTJS,
    "gatsby": SSGEngine.GATSBY,
    "nuxt": SSGEngine.NUXT,
}

CMS_PROVIDERS = {
    "decap": CMSProvider.DECAP,
    "tina": CMSProvider.TINA,
    "sanity": CMSProvider.SANITY,
    "contentful": CMSProvider.CONTENTFUL,
}

ECOMMERCE_PROVIDERS = {
    "snipcart": EcommerceProvider.SNIPCART,
    "foxy": EcommerceProvider.FOXY,
    "shopify_basic": EcommerceProvider.SHOPIFY_BASIC,
    "shopify_advanced": EcommerceProvider.SHOPIFY_ADVANCED,
    "shopify_headless": EcommerceProvider.SHOPIFY_HEADLESS,
    "woocommerce": EcommerceProvider.WOOCOMMERCE,
    "custom_api": EcommerceProvider.CUSTOM_API,
    "none": EcommerceProvider.NONE,
}


# Helper functions for validation and conversion
def get_ssg_engine(value: str) -> SSGEngine:
    """Convert string to SSGEngine enum with validation."""
    try:
        return SSGEngine(value)
    except ValueError:
        valid_engines = list(SSGEngine)
        raise ValueError(f"Invalid SSG engine '{value}'. Valid options: {valid_engines}")


def get_cms_provider(value: str) -> CMSProvider:
    """Convert string to CMSProvider enum with validation."""
    try:
        return CMSProvider(value)
    except ValueError:
        valid_providers = list(CMSProvider)
        raise ValueError(f"Invalid CMS provider '{value}'. Valid options: {valid_providers}")


def get_ecommerce_provider(value: str) -> EcommerceProvider:
    """Convert string to EcommerceProvider enum with validation."""
    try:
        return EcommerceProvider(value)
    except ValueError:
        valid_providers = list(EcommerceProvider)
        raise ValueError(f"Invalid e-commerce provider '{value}'. Valid options: {valid_providers}")


# Export all enums and utilities
__all__ = [
    "SSGEngine",
    "CMSProvider",
    "EcommerceProvider",
    "ProviderType",
    "Environment",
    "IntegrationLevel",
    "InventoryPolicy",
    "HTTPMethod",
    "EventType",
    "SSG_ENGINES",
    "CMS_PROVIDERS",
    "ECOMMERCE_PROVIDERS",
    "get_ssg_engine",
    "get_cms_provider",
    "get_ecommerce_provider",
]