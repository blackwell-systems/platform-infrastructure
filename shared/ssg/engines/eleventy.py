"""
Eleventy SSG Engine Configuration

Defines the Eleventy (11ty) static site generator engine with its specific
build commands, templates, and optimization features.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate, ECommerceIntegration


class EleventyConfig(SSGEngineConfig):
    """Eleventy (11ty) SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "eleventy"

    @property
    def runtime_version(self) -> str:
        return "nodejs-20"

    @property
    def install_commands(self) -> List[str]:
        return [
            "npm ci",  # Clean install from package-lock.json
            "npm install -g @11ty/eleventy",  # Global install for CLI
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npx @11ty/eleventy",
                environment_vars={"ELEVENTY_PRODUCTION": "true"},
            ),
            BuildCommand(
                name="optimize_assets",
                command="npm run optimize",  # Custom optimization script
                environment_vars={"NODE_ENV": "production"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "_site"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "incremental_builds": True,
            "template_caching": True,
            "asset_optimization": True,
            "html_minification": True,
            "css_minification": True,
            "js_minification": True,
            "image_optimization": True,
            "build_performance": "fast",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="business_modern",
                description="Modern business website with hero, services, testimonials",
                use_cases=["business_sites", "professional_services", "consulting"],
                repo_url="https://github.com/your-templates/eleventy-business-modern",
                customization_points=[
                    "colors",
                    "fonts",
                    "hero_content",
                    "services_grid",
                    "contact_info",
                ],
                demo_url="https://demo.yourservices.com/business-modern",
                supports_ecommerce=False,
            ),
            SSGTemplate(
                name="snipcart_ecommerce",
                description="Simple e-commerce site with Snipcart integration for small stores",
                use_cases=["simple_ecommerce", "small_stores", "product_catalogs", "digital_products"],
                repo_url="https://github.com/your-templates/eleventy-snipcart-store",
                customization_points=[
                    "product_catalog",
                    "cart_styling",
                    "payment_methods",
                    "shipping_options",
                    "tax_configuration",
                ],
                demo_url="https://demo.yourservices.com/eleventy-snipcart",
                difficulty_level="intermediate",
                estimated_setup_hours=3.0,
                supports_ecommerce=True,
                ecommerce_integration=ECommerceIntegration(
                    provider="snipcart",
                    features=["cart", "checkout", "inventory", "digital_products", "subscriptions"],
                    setup_complexity="low",
                    monthly_cost_range=[29, 99],
                    transaction_fee_percent=2.0,
                    integration_method="javascript_snippet",
                    required_environment_vars=["SNIPCART_API_KEY"],
                    build_dependencies=[],
                    aws_services_needed=["Lambda", "SES"]  # For order notifications
                ),
            ),
            SSGTemplate(
                name="service_provider",
                description=(
                    "Service-focused layout with pricing, FAQ, booking integration"
                ),
                use_cases=["service_businesses", "freelancers", "agencies"],
                repo_url="https://github.com/your-templates/eleventy-service-provider",
                customization_points=[
                    "service_categories",
                    "pricing_tiers",
                    "booking_system",
                    "testimonials",
                ],
                demo_url="https://demo.yourservices.com/service-provider",
            ),
            SSGTemplate(
                name="marketing_landing",
                description=(
                    "High-conversion landing page with clear CTA and social proof"
                ),
                use_cases=["product_launches", "lead_generation", "campaigns"],
                repo_url="https://github.com/your-templates/eleventy-marketing-landing",
                customization_points=[
                    "hero_cta",
                    "feature_highlights",
                    "social_proof",
                    "conversion_forms",
                ],
                demo_url="https://demo.yourservices.com/marketing-landing",
                supports_ecommerce=False,
            ),
        ]