"""
CMS Provider Implementations

Concrete implementations of CMS providers that extend the base CMSProvider class.
Each provider implements the abstract methods to provide CMS-specific functionality
while maintaining a consistent interface across all providers.

Available Providers:
- DecapCMSProvider: Git-based CMS with GitHub integration
- SanityCMSProvider: API-based CMS with real-time collaboration
- ContentfulProvider: Enterprise API-based CMS
- TinaCMSProvider: Hybrid git+API CMS with visual editing

Usage:
    from shared.providers.cms.providers import DecapCMSProvider

    provider = DecapCMSProvider({
        "admin_users": ["admin@example.com"],
        "content_path": "content",
        "branch": "main"
    })
"""

# Import concrete provider implementations
# These will be implemented as we build out the provider system

__all__ = [
    # Git-based CMS providers
    "DecapCMSProvider",

    # API-based CMS providers
    # "SanityCMSProvider",
    # "ContentfulProvider",

    # Hybrid CMS providers
    # "TinaCMSProvider",
]