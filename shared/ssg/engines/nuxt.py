"""
Nuxt.js SSG Engine Configuration

Defines the Nuxt.js static site generator engine with its specific
build commands, templates, and optimization features.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate


class NuxtConfig(SSGEngineConfig):
    """Nuxt.js SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "nuxt"

    @property
    def runtime_version(self) -> str:
        return "nodejs-20"

    @property
    def install_commands(self) -> List[str]:
        return ["npm ci", "npm install -g nuxt"]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="generate_static",
                command="npm run generate",
                environment_vars={
                    "NODE_ENV": "production",
                    "NITRO_PRESET": "static",
                    "NUXT_TELEMETRY_DISABLED": "1",
                },
            ),
            BuildCommand(
                name="optimize_build",
                command="npm run build:optimize",
                environment_vars={"NODE_ENV": "production"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "dist"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "vue_3_composition_api": True,
            "auto_imports": True,
            "server_side_rendering": True,
            "static_generation": True,
            "typescript_support": True,
            "universal_rendering": True,
            "nitro_engine": True,
            "build_performance": "fast",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="professional_headless_cms",
                description="Professional Nuxt 3 with headless CMS integration",
                use_cases=["vue_applications", "professional_sites", "spa_conversion"],
                repo_url="https://github.com/your-templates/nuxt-professional-headless-cms",
                customization_points=[
                    "cms_integration",
                    "vue_components",
                    "styling",
                    "ssr_config",
                ],
                demo_url="https://demo.yourservices.com/nuxt-professional",
                difficulty_level="intermediate",
            ),
            SSGTemplate(
                name="enterprise_applications",
                description=(
                    "Enterprise Nuxt applications with advanced Vue ecosystem "
                    "integration"
                ),
                use_cases=[
                    "enterprise_vue_apps",
                    "complex_spas",
                    "vue_ecosystem",
                    "pinia_state_management",
                ],
                repo_url="https://github.com/your-templates/nuxt-enterprise-applications",
                customization_points=[
                    "pinia_stores",
                    "vue_router",
                    "composables",
                    "middleware",
                    "plugins",
                ],
                demo_url="https://demo.yourservices.com/nuxt-enterprise",
                difficulty_level="advanced",
            ),
        ]