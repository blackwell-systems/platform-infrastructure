"""
Minimal Mistakes Theme Integration

Simple theme integration for the minimal-mistakes Jekyll theme.
Provides theme discovery and validation for the requested theme.
"""

from typing import Optional

from .theme_models import Theme, ThemeInstallMethod
from .jekyll_themes import get_minimal_mistakes_theme


class ThemeRegistry:
    """
    Theme integration for minimal-mistakes Jekyll theme.
    
    Provides simple theme discovery and validation for the specific
    minimal-mistakes theme as requested.
    """
    
    @classmethod
    def get_theme(cls, theme_id: str) -> Optional[Theme]:
        """
        Get the minimal-mistakes theme if requested.
        
        Args:
            theme_id: Theme identifier
            
        Returns:
            Theme object if minimal-mistakes is requested, None otherwise
        """
        if theme_id == "minimal-mistakes":
            return get_minimal_mistakes_theme()
        return None
    
    @classmethod
    def get_themes(cls, engine: str) -> list[Theme]:
        """
        Get available themes for Jekyll engine.
        
        Args:
            engine: SSG engine name
            
        Returns:
            List containing minimal-mistakes theme if engine is jekyll
        """
        if engine == "jekyll":
            return [get_minimal_mistakes_theme()]
        return []
    
    @classmethod
    def validate_theme_compatibility(cls, theme_id: str, engine: str) -> bool:
        """
        Validate that minimal-mistakes is compatible with Jekyll engine.
        
        Args:
            theme_id: Theme identifier
            engine: SSG engine name
            
        Returns:
            True if minimal-mistakes + jekyll, False otherwise
        """
        return theme_id == "minimal-mistakes" and engine == "jekyll"
    
    @classmethod
    def get_github_pages_compatible_themes(cls, engine: str) -> list[Theme]:
        """
        Get GitHub Pages compatible themes.
        
        Args:
            engine: SSG engine name
            
        Returns:
            List containing minimal-mistakes if engine is jekyll
        """
        if engine == "jekyll":
            return [get_minimal_mistakes_theme()]
        return []


# Export main classes and types for easy importing
__all__ = [
    "ThemeRegistry",
    "Theme", 
    "ThemeInstallMethod",
    "get_minimal_mistakes_theme"
]