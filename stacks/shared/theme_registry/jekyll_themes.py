"""
Jekyll Minimal Mistakes Theme Integration

Integration for the minimal-mistakes Jekyll theme as requested.
Uses remote_theme method for GitHub Pages compatibility.
"""

from typing import List
from .theme_models import Theme, ThemeInstallMethod


# Minimal Mistakes theme integration (as specifically requested)
JEKYLL_THEMES: List[Theme] = [
    Theme(
        id="minimal-mistakes",
        name="Minimal Mistakes",
        description="Professional Jekyll theme from mmistakes/minimal-mistakes repository with clean design and extensive customization options.",
        engine="jekyll",
        installation_method=ThemeInstallMethod.REMOTE_THEME,
        source="mmistakes/minimal-mistakes@4.27.3",
        required_plugins=[
            "jekyll-include-cache",
            "jekyll-paginate", 
            "jekyll-sitemap",
            "jekyll-gist",
            "jekyll-feed"
        ],
        minimum_engine_version="4.0.0",
        github_pages_compatible=True,
        repo_url="https://github.com/mmistakes/minimal-mistakes",
        demo_url="https://mmistakes.github.io/minimal-mistakes/",
        documentation_url="https://mmistakes.github.io/minimal-mistakes/docs/quick-start-guide/",
        categories=["business", "professional", "portfolio"],
        tags=["responsive", "clean", "modern", "seo"],
        customization_options={
            "skins": ["default", "dark", "dirt", "mint", "plum", "sunrise"],
            "layouts": ["single", "splash", "archive", "search", "home"],
            "author_profile": True,
            "navigation": True,
            "sidebar": True,
            "search": True
        },
        verified=True,
        maintenance_status="active",
        license_type="MIT",
        author_name="Michael Rose"
    )
]


def get_minimal_mistakes_theme() -> Theme:
    """
    Get the minimal-mistakes theme configuration.
    
    Returns:
        Theme object for minimal-mistakes
    """
    return JEKYLL_THEMES[0]


def get_github_pages_themes() -> List[Theme]:
    """
    Get all Jekyll themes compatible with GitHub Pages.
    
    Returns:
        List of GitHub Pages compatible themes (currently just minimal-mistakes)
    """
    return [theme for theme in JEKYLL_THEMES if theme.github_pages_compatible]