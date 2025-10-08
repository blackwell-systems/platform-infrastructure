"""
Gatsby SSG Engine Configuration

Defines the Gatsby static site generator engine with its specific
build commands, templates, and optimization features.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate


class GatsbyConfig(SSGEngineConfig):
    """Gatsby SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "gatsby"

    @property
    def runtime_version(self) -> str:
        return "nodejs-20"

    @property
    def install_commands(self) -> List[str]:
        return ["npm ci", "npm install -g gatsby-cli"]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npm run build",
                environment_vars={
                    "NODE_ENV": "production",
                    "GATSBY_TELEMETRY_DISABLED": "1",
                    "CI": "true",
                },
            ),
            BuildCommand(
                name="optimize_images",
                command="npm run build:optimize",
                environment_vars={"NODE_ENV": "production"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "public"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "graphql_data_layer": True,
            "automatic_code_splitting": True,
            "progressive_web_app": True,
            "image_optimization": True,
            "prefetching": True,
            "react_hydration": True,
            "plugin_ecosystem": True,
            "build_performance": "moderate",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="contentful_integration",
                description="Gatsby with Contentful CMS integration and GraphQL",
                use_cases=["content_sites", "blogs", "marketing_sites"],
                repo_url="https://github.com/your-templates/gatsby-contentful",
                customization_points=[
                    "contentful_schema",
                    "page_templates",
                    "graphql_queries",
                    "styling",
                ],
                demo_url="https://demo.yourservices.com/gatsby-contentful",
                difficulty_level="intermediate",
            ),
            SSGTemplate(
                name="headless_cms_stack",
                description=(
                    "Advanced Gatsby with multiple headless CMS options and GraphQL "
                    "optimization"
                ),
                use_cases=[
                    "headless_cms_sites",
                    "content_management",
                    "editorial_workflows",
                    "multi_source_content",
                ],
                repo_url="https://github.com/your-templates/gatsby-headless-cms",
                customization_points=[
                    "cms_selection",
                    "graphql_optimization",
                    "content_sourcing",
                    "build_optimization",
                ],
                demo_url="https://demo.yourservices.com/gatsby-headless",
                difficulty_level="advanced",
            ),
        ]