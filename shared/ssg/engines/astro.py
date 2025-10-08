"""
Astro SSG Engine Configuration

Defines the Astro static site generator engine with its specific
build commands, templates, and optimization features.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate, ECommerceIntegration


class AstroConfig(SSGEngineConfig):
    """Astro SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "astro"

    @property
    def runtime_version(self) -> str:
        return "nodejs-20"

    @property
    def install_commands(self) -> List[str]:
        return ["npm ci", "npm install -g astro"]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npm run build",
                environment_vars={"NODE_ENV": "production"},
            ),
            BuildCommand(
                name="optimize_components",
                command="npm run build:optimize",
                environment_vars={"ASTRO_TELEMETRY_DISABLED": "1"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "dist"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "component_islands": True,
            "partial_hydration": True,
            "framework_agnostic": True,
            "zero_js_by_default": True,
            "built_in_optimizations": True,
            "modern_build_tools": True,
            "typescript_support": True,
            "build_performance": "fast",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="modern_interactive",
                description=(
                    "Interactive components with React/Vue islands for dynamic features"
                ),
                use_cases=["interactive_sites", "component_showcases", "modern_apps"],
                repo_url="https://github.com/your-templates/astro-modern-interactive",
                customization_points=[
                    "component_framework",
                    "interactive_elements",
                    "styling_system",
                    "integrations",
                ],
                demo_url="https://demo.yourservices.com/astro-interactive",
                supports_ecommerce=False,
            ),
            SSGTemplate(
                name="performance_focused",
                description=(
                    "Ultra-fast loading with component islands and minimal JavaScript"
                ),
                use_cases=[
                    "performance_critical",
                    "mobile_first",
                    "conversion_optimization",
                ],
                repo_url="https://github.com/your-templates/astro-performance",
                customization_points=[
                    "performance_budgets",
                    "critical_css",
                    "lazy_loading",
                    "optimization_settings",
                ],
                demo_url="https://demo.yourservices.com/astro-performance",
                supports_ecommerce=False,
            ),
            SSGTemplate(
                name="foxy_ecommerce",
                description=(
                    "Advanced e-commerce with Foxy.io integration and React islands"
                ),
                use_cases=[
                    "advanced_ecommerce",
                    "scalable_stores",
                    "subscription_products",
                    "complex_catalogs"
                ],
                repo_url="https://github.com/your-templates/astro-foxy-store",
                customization_points=[
                    "product_pages",
                    "cart_components",
                    "checkout_flow",
                    "subscription_management",
                    "inventory_display",
                    "customer_accounts",
                ],
                demo_url="https://demo.yourservices.com/astro-foxy",
                difficulty_level="advanced",
                estimated_setup_hours=6.0,
                supports_ecommerce=True,
                ecommerce_integration=ECommerceIntegration(
                    provider="foxy",
                    features=[
                        "cart", "checkout", "inventory", "subscriptions", 
                        "customer_portal", "advanced_shipping", "tax_calculation"
                    ],
                    setup_complexity="high",
                    monthly_cost_range=[75, 300],
                    transaction_fee_percent=1.5,
                    integration_method="api_integration",
                    required_environment_vars=["FOXY_STORE_DOMAIN", "FOXY_API_KEY"],
                    build_dependencies=["@astrojs/react", "@foxy.io/sdk"],
                    aws_services_needed=["Lambda", "API Gateway", "DynamoDB", "SES"]
                ),
            ),
        ]