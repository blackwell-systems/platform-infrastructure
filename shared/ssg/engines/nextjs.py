"""
Next.js SSG Engine Configuration

Defines the Next.js static site generator engine with its specific
build commands, templates, and optimization features.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate


class NextJSConfig(SSGEngineConfig):
    """Next.js SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "nextjs"

    @property
    def runtime_version(self) -> str:
        return "nodejs-20"

    @property
    def install_commands(self) -> List[str]:
        return ["npm ci", "npm install -g next"]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npm run build",
                environment_vars={
                    "NODE_ENV": "production",
                    "NEXT_TELEMETRY_DISABLED": "1",
                },
            ),
            BuildCommand(
                name="export_static",
                command="npm run export",
                environment_vars={"NODE_ENV": "production"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "out"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "automatic_static_optimization": True,
            "image_optimization": True,
            "code_splitting": True,
            "prefetching": True,
            "typescript_support": True,
            "app_router": True,
            "react_server_components": True,
            "build_performance": "fast",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="professional_headless_cms",
                description=(
                    "Professional headless CMS integration with Contentful/Strapi"
                ),
                use_cases=["professional_sites", "headless_cms", "content_heavy"],
                repo_url="https://github.com/your-templates/nextjs-professional-headless-cms",
                customization_points=[
                    "cms_integration",
                    "page_layouts",
                    "styling_system",
                    "seo_config",
                ],
                demo_url="https://demo.yourservices.com/nextjs-professional",
                difficulty_level="intermediate",
            ),
            SSGTemplate(
                name="enterprise_applications",
                description=(
                    "Enterprise-grade applications with advanced features and "
                    "integrations"
                ),
                use_cases=[
                    "enterprise_apps",
                    "complex_applications",
                    "multi_tenant",
                    "advanced_routing",
                ],
                repo_url="https://github.com/your-templates/nextjs-enterprise-applications",
                customization_points=[
                    "authentication",
                    "authorization",
                    "database_integration",
                    "api_routes",
                    "middleware",
                ],
                demo_url="https://demo.yourservices.com/nextjs-enterprise",
                difficulty_level="advanced",
            ),
        ]