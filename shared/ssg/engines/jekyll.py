"""
Jekyll SSG Engine Configuration

Defines the Jekyll static site generator engine with its specific
build commands, templates, and optimization features. Optimized for GitHub Pages.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate


class JekyllConfig(SSGEngineConfig):
    """Jekyll SSG engine configuration (for GitHub Pages)"""

    @property
    def engine_name(self) -> str:
        return "jekyll"

    @property
    def runtime_version(self) -> str:
        return "ruby-3.1"

    @property
    def install_commands(self) -> List[str]:
        return ["gem install bundler", "bundle install"]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="bundle exec jekyll build",
                environment_vars={"JEKYLL_ENV": "production"},
            )
        ]

    @property
    def output_directory(self) -> str:
        return "_site"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "github_pages_compatible": True,
            "liquid_templating": True,
            "markdown_processing": True,
            "sass_support": True,
            "plugin_ecosystem": True,
            "free_hosting": True,  # GitHub Pages
            "build_performance": "moderate",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="nonprofit_charity",
                description=(
                    "Charity/nonprofit focused with donation integration and "
                    "volunteer signup"
                ),
                use_cases=["nonprofits", "charities", "community_organizations"],
                repo_url="https://github.com/your-templates/jekyll-nonprofit",
                customization_points=[
                    "cause_focus",
                    "donation_integration",
                    "volunteer_forms",
                    "impact_metrics",
                ],
                demo_url="https://demo.yourservices.com/jekyll-nonprofit",
            ),
            SSGTemplate(
                name="simple_blog",
                description="Clean, simple blog with GitHub Pages compatibility",
                use_cases=["personal_blogs", "content_creators", "documentation"],
                repo_url="https://github.com/your-templates/jekyll-simple-blog",
                customization_points=[
                    "theme_colors",
                    "layout_style",
                    "social_integration",
                    "comments_system",
                ],
                demo_url="https://demo.yourservices.com/jekyll-blog",
            ),
        ]