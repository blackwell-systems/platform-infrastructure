"""
Static Site Generator (SSG) Engine System

Provides a clean, browsable interface to the SSG configuration system.
This package organizes SSG engines, templates, and configurations into
focused, maintainable modules.
"""

# Public API - everything users need to import
from .static_site_config import StaticSiteConfig
from .factory import SSGEngineFactory
from .core_models import (
    BuildCommand, 
    ECommerceIntegration, 
    SSGTemplate,
    SSGEngineType,
    ECommerceProvider,
    HostingPattern
)
from .base_engine import SSGEngineConfig

# Re-export for convenience
__all__ = [
    # Main client integration
    "StaticSiteConfig",
    
    # Factory for creating engine configs
    "SSGEngineFactory", 
    
    # Core models
    "BuildCommand",
    "ECommerceIntegration", 
    "SSGTemplate",
    "SSGEngineConfig",
    
    # Type definitions
    "HostingPattern",
    "SSGEngineType", 
    "ECommerceProvider"
]