# SSG Engine Configuration System
# Foundation for all static site stacks

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional

from aws_cdk import aws_codebuild as codebuild
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SSGEngineType = Literal[
    "eleventy", "hugo", "astro", "jekyll", "nextjs", "nuxt", "gatsby"
]

ECommerceProvider = Literal[
    "snipcart", "foxy", "shopify_basic", "shopify_advanced", "shopify_headless", 
    "woocommerce", "custom_api", "none"
]

HostingPattern = Literal[
    "aws",           # Full AWS hosting (S3 + CloudFront + Route53)
    "github",        # GitHub Pages hosting only
    "hybrid",        # AWS primary + GitHub Pages fallback
    "aws_minimal"    # AWS hosting with minimal features (cost-optimized)
]


class BuildCommand(BaseModel):
    """Represents a build step for SSG compilation"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "build_site",
                    "command": "npm run build",
                    "environment_vars": {"NODE_ENV": "production"},
                    "timeout_minutes": 10,
                }
            ]
        },
    )

    name: str = Field(..., description="Name of the build step")
    command: str = Field(..., description="Shell command to execute")
    environment_vars: Dict[str, str] = Field(
        default_factory=dict, description="Environment variables for this command"
    )
    timeout_minutes: int = Field(
        default=10, ge=1, le=60, description="Timeout for this build step"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Build command name must be alphanumeric with underscores/hyphens"
            )
        return v

    @field_validator("command")
    @classmethod
    def validate_command(cls, v):
        if not v.strip():
            raise ValueError("Build command cannot be empty")
        return v.strip()


class ECommerceIntegration(BaseModel):
    """E-commerce platform integration configuration"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "provider": "snipcart",
                    "features": ["cart", "checkout", "inventory"],
                    "setup_complexity": "low",
                    "monthly_cost_range": [29, 99],
                    "transaction_fee_percent": 2.0,
                    "integration_method": "javascript_snippet"
                }
            ]
        },
    )

    provider: ECommerceProvider = Field(..., description="E-commerce platform provider")
    features: List[str] = Field(..., description="Available e-commerce features")
    setup_complexity: Literal["low", "medium", "high"] = Field(default="medium")
    monthly_cost_range: List[int] = Field(description="Monthly cost range [min, max]")
    transaction_fee_percent: Optional[float] = Field(None, description="Transaction fee percentage")
    integration_method: Literal[
        "javascript_snippet", "api_integration", "headless_api", "plugin_based", "custom_backend"
    ] = Field(description="How the e-commerce platform integrates")
    required_environment_vars: List[str] = Field(
        default_factory=list, description="Required environment variables"
    )
    build_dependencies: List[str] = Field(
        default_factory=list, description="Additional build dependencies needed"
    )
    aws_services_needed: List[str] = Field(
        default_factory=list, description="Additional AWS services required"
    )


class SSGTemplate(BaseModel):
    """Template configuration for SSG engines"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "business_modern",
                    "description": "Modern business website with hero, services, "
                    "testimonials",
                    "use_cases": [
                        "business_sites",
                        "professional_services",
                        "consulting",
                    ],
                    "repo_url": "https://github.com/your-templates/eleventy-business-modern",
                    "customization_points": [
                        "colors",
                        "fonts",
                        "hero_content",
                        "services_grid",
                    ],
                    "demo_url": "https://demo.yourservices.com/business-modern",
                    "difficulty_level": "intermediate",
                    "estimated_setup_hours": 2.0,
                    "ecommerce_integration": None
                }
            ]
        },
    )

    name: str = Field(..., description="Template identifier")
    description: str = Field(..., description="Human-readable description")
    use_cases: List[str] = Field(..., description="List of appropriate use cases")
    repo_url: str = Field(..., description="Git repository URL for template")
    customization_points: List[str] = Field(
        ..., description="List of customizable aspects"
    )
    demo_url: Optional[str] = Field(None, description="URL of live demo")
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(
        default="intermediate"
    )
    estimated_setup_hours: float = Field(
        default=2.0, ge=0.5, le=40.0, description="Estimated setup time in hours"
    )
    ecommerce_integration: Optional[ECommerceIntegration] = Field(
        None, description="E-commerce platform integration if applicable"
    )
    supports_ecommerce: bool = Field(
        default=False, description="Whether this template supports e-commerce features"
    )

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        if not (
            v.startswith("https://github.com/") or v.startswith("https://gitlab.com/")
        ):
            raise ValueError("Repository URL must be from GitHub or GitLab")
        return v

    @field_validator("use_cases")
    @classmethod
    def validate_use_cases(cls, v):
        if not v:
            raise ValueError("At least one use case must be specified")
        return v


class SSGEngineConfig(ABC):
    """Abstract base class for SSG engine configurations"""

    def __init__(self, template_variant: str = "default"):
        self.template_variant = template_variant

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of the SSG engine"""
        pass

    @property
    @abstractmethod
    def runtime_version(self) -> str:
        """Node.js or other runtime version"""
        pass

    @property
    @abstractmethod
    def install_commands(self) -> List[str]:
        """Commands to install dependencies"""
        pass

    @property
    @abstractmethod
    def build_commands(self) -> List[BuildCommand]:
        """Commands to build the site"""
        pass

    @property
    @abstractmethod
    def output_directory(self) -> str:
        """Directory containing built site files"""
        pass

    @property
    @abstractmethod
    def optimization_features(self) -> Dict[str, Any]:
        """Engine-specific optimization settings"""
        pass

    @property
    @abstractmethod
    def available_templates(self) -> List[SSGTemplate]:
        """Templates available for this engine"""
        pass

    def get_codebuild_environment(self) -> codebuild.BuildEnvironment:
        """Generate CodeBuild environment for this engine"""
        return codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
            environment_variables={
                "SSG_ENGINE": codebuild.BuildEnvironmentVariable(
                    value=self.engine_name
                ),
                "TEMPLATE_VARIANT": codebuild.BuildEnvironmentVariable(
                    value=self.template_variant
                ),
                "OUTPUT_DIR": codebuild.BuildEnvironmentVariable(
                    value=self.output_directory
                ),
            },
        )

    def get_buildspec(self) -> Dict[str, Any]:
        """Generate CodeBuild buildspec for this engine"""
        # Handle different runtime types
        runtime_versions = {}
        if self.runtime_version.startswith("nodejs-"):
            runtime_versions["nodejs"] = self.runtime_version.split("nodejs-")[1]
        elif self.runtime_version.startswith("golang-"):
            runtime_versions["golang"] = self.runtime_version.split("golang-")[1]
        elif self.runtime_version.startswith("ruby-"):
            runtime_versions["ruby"] = self.runtime_version.split("ruby-")[1]

        install_phase = {
            "runtime-versions": runtime_versions,
            "commands": self.install_commands,
        }

        build_phase = {"commands": [cmd.command for cmd in self.build_commands]}

        return {
            "version": "0.2",
            "phases": {"install": install_phase, "build": build_phase},
            "artifacts": {"files": ["**/*"], "base-directory": self.output_directory},
        }


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


class HugoConfig(SSGEngineConfig):
    """Hugo SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "hugo"

    @property
    def runtime_version(self) -> str:
        return "golang-1.21"  # Hugo is Go-based

    @property
    def install_commands(self) -> List[str]:
        return [
            "wget https://github.com/gohugoio/hugo/releases/download/v0.121.0/hugo_extended_0.121.0_Linux-64bit.tar.gz",
            "tar -xzf hugo_extended_0.121.0_Linux-64bit.tar.gz",
            "chmod +x hugo",
            "sudo mv hugo /usr/local/bin/",
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="hugo --minify --gc",
                environment_vars={"HUGO_ENV": "production"},
            ),
            BuildCommand(
                name="optimize_images",
                command="hugo --minify --gc --enableGitInfo",
                environment_vars={"HUGO_ENV": "production"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "public"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "extremely_fast_builds": True,
            "built_in_minification": True,
            "image_processing": True,
            "asset_bundling": True,
            "template_caching": True,
            "incremental_builds": False,  # Hugo rebuilds everything but very fast
            "build_performance": "extremely_fast",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="corporate_clean",
                description="Clean corporate design with powerful content management",
                use_cases=["corporate_sites", "large_content_sites", "multi_language"],
                repo_url="https://github.com/your-templates/hugo-corporate-clean",
                customization_points=[
                    "theme_colors",
                    "layout_options",
                    "content_sections",
                    "navigation",
                ],
                demo_url="https://demo.yourservices.com/hugo-corporate",
            ),
            SSGTemplate(
                name="content_publisher",
                description=(
                    "Content-heavy site with blog, resources, and knowledge base"
                ),
                use_cases=[
                    "content_sites",
                    "blogs",
                    "documentation",
                    "knowledge_bases",
                ],
                repo_url="https://github.com/your-templates/hugo-content-publisher",
                customization_points=[
                    "content_taxonomy",
                    "search_functionality",
                    "author_profiles",
                    "content_types",
                ],
                demo_url="https://demo.yourservices.com/hugo-content",
            ),
        ]


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
            SSGTemplate(
                name="tina_cms_portfolio",
                description=(
                    "Portfolio template with Tina CMS for easy content management"
                ),
                use_cases=["portfolios", "creative_agencies", "freelancers", "showcases"],
                repo_url="https://github.com/your-templates/astro-tina-portfolio",
                customization_points=[
                    "project_layouts",
                    "gallery_styles",
                    "contact_forms",
                    "cms_schemas",
                ],
                demo_url="https://demo.yourservices.com/astro-tina",
                difficulty_level="intermediate",
                estimated_setup_hours=4.0,
                supports_ecommerce=False,
            ),
            SSGTemplate(
                name="sanity_cms_business",
                description=(
                    "Business site with Sanity CMS for structured content management"
                ),
                use_cases=["business_sites", "content_heavy", "multi_author", "editorial"],
                repo_url="https://github.com/your-templates/astro-sanity-business",
                customization_points=[
                    "content_schemas",
                    "page_layouts",
                    "author_profiles",
                    "content_workflows",
                ],
                demo_url="https://demo.yourservices.com/astro-sanity",
                difficulty_level="intermediate",
                estimated_setup_hours=5.0,
                supports_ecommerce=False,
            ),
        ]


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


class SSGEngineFactory:
    """Factory for creating SSG engine configurations"""

    _engines = {
        "eleventy": EleventyConfig,
        "hugo": HugoConfig,
        "astro": AstroConfig,
        "jekyll": JekyllConfig,
        "nextjs": NextJSConfig,
        "nuxt": NuxtConfig,
        "gatsby": GatsbyConfig,
    }

    @classmethod
    def create_engine(
        cls, engine_type: SSGEngineType, template_variant: str = "default"
    ) -> SSGEngineConfig:
        """Create an SSG engine configuration"""
        if engine_type not in cls._engines:
            raise ValueError(f"Unsupported SSG engine: {engine_type}")

        return cls._engines[engine_type](template_variant)

    @classmethod
    def get_available_engines(cls) -> List[str]:
        """Get list of available SSG engines"""
        return list(cls._engines.keys())

    @classmethod
    def get_engine_templates(cls, engine_type: SSGEngineType) -> List[SSGTemplate]:
        """Get available templates for an engine"""
        engine = cls.create_engine(engine_type)
        return engine.available_templates
    
    @classmethod
    def get_ecommerce_templates(cls) -> Dict[str, List[SSGTemplate]]:
        """Get all e-commerce templates across all engines"""
        ecommerce_templates = {}
        
        for engine_type in cls._engines.keys():
            engine = cls.create_engine(engine_type)
            templates = [t for t in engine.available_templates if t.supports_ecommerce]
            if templates:
                ecommerce_templates[engine_type] = templates
                
        return ecommerce_templates
    
    @classmethod
    def get_templates_by_provider(cls, provider: ECommerceProvider) -> Dict[str, List[SSGTemplate]]:
        """Get templates that support a specific e-commerce provider"""
        provider_templates = {}
        
        for engine_type in cls._engines.keys():
            engine = cls.create_engine(engine_type)
            templates = [
                t for t in engine.available_templates 
                if (t.supports_ecommerce and 
                    t.ecommerce_integration and 
                    t.ecommerce_integration.provider == provider)
            ]
            if templates:
                provider_templates[engine_type] = templates
                
        return provider_templates
    
    @classmethod
    def get_recommended_stack_for_ecommerce(
        cls, 
        provider: ECommerceProvider, 
        complexity: Literal["simple", "advanced", "enterprise"] = "simple"
    ) -> List[Dict[str, Any]]:
        """Get recommended SSG engine and template combinations for e-commerce"""
        recommendations = []
        
        complexity_mapping = {
            "simple": "low",
            "advanced": "high", 
            "enterprise": "high"  # Map enterprise to high for now
        }
        
        target_complexity = complexity_mapping.get(complexity, "low")
        provider_templates = cls.get_templates_by_provider(provider)
        
        for engine_type, templates in provider_templates.items():
            for template in templates:
                if (template.ecommerce_integration and 
                    template.ecommerce_integration.setup_complexity == target_complexity):
                    recommendations.append({
                        "engine": engine_type,
                        "template": template.name,
                        "provider": provider,
                        "complexity": complexity,
                        "estimated_hours": template.estimated_setup_hours,
                        "monthly_cost_range": template.ecommerce_integration.monthly_cost_range
                    })
        
        return sorted(recommendations, key=lambda x: x["estimated_hours"])


# Client Configuration Integration
class StaticSiteConfig(BaseModel):
    """Configuration for static site deployment with e-commerce support"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "client_id": "demo-client",
                    "domain": "demo-client.com",
                    "ssg_engine": "eleventy",
                    "template_variant": "snipcart_ecommerce",
                    "performance_tier": "optimized",
                    "cdn_caching_strategy": "moderate",
                    "ecommerce_provider": "snipcart",
                    "ecommerce_config": {
                        "store_name": "Demo Store",
                        "currency": "USD",
                        "tax_included": False
                    }
                }
            ]
        },
    )

    client_id: str = Field(
        ..., description="Unique client identifier", pattern=r"^[a-z0-9-]+$"
    )
    domain: str = Field(..., description="Primary domain for the site")
    ssg_engine: SSGEngineType = Field(
        default="eleventy", description="Static site generator to use"
    )
    template_variant: str = Field(
        default="business_modern", description="Template variant to use"
    )
    custom_build_commands: Optional[List[str]] = Field(
        None, description="Custom build commands if needed"
    )
    environment_vars: Dict[str, str] = Field(
        default_factory=dict, description="Custom environment variables"
    )
    performance_tier: Literal["basic", "optimized", "premium"] = Field(
        default="optimized", description="Performance optimization level"
    )
    
    # Hosting pattern configuration - key business decision per client
    hosting_pattern: Optional[HostingPattern] = Field(
        default=None,
        description="Hosting pattern: 'aws' (full), 'github' (pages only), 'hybrid' (AWS+GitHub), 'aws_minimal' (cost-optimized). Auto-selected based on tier if not specified."
    )
    
    cdn_caching_strategy: Literal["aggressive", "moderate", "minimal"] = Field(
        default="moderate", description="CDN caching strategy"
    )
    
    # E-commerce specific configurations
    ecommerce_provider: Optional[ECommerceProvider] = Field(
        None, description="E-commerce platform provider if applicable"
    )
    ecommerce_config: Dict[str, Any] = Field(
        default_factory=dict, description="E-commerce platform specific configuration"
    )
    
    # Theme system configuration
    theme_id: Optional[str] = Field(
        None,
        description="Theme identifier from theme registry (e.g., 'minimal-mistakes-business'). If not specified, uses SSG engine default.",
        pattern=r"^[a-z0-9-]+$"
    )
    theme_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Theme-specific customization options (colors, layouts, features, etc.)"
    )
    requires_backend_api: bool = Field(
        default=False, description="Whether this configuration requires backend API services"
    )
    webhook_endpoints: List[str] = Field(
        default_factory=list, description="Required webhook endpoints for e-commerce integrations"
    )

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        # Basic domain validation
        import re

        domain_pattern = (
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?)*$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError("Invalid domain format")
        return v.lower()

    @field_validator("client_id")
    @classmethod
    def validate_client_id(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Client ID must be between 3 and 50 characters")
        return v

    @model_validator(mode="after")
    def validate_theme_compatibility(self):
        """Validate theme compatibility with SSG engine and hosting pattern"""
        if self.theme_id:
            theme_info = self.get_theme_info()
            if not theme_info:
                raise ValueError(f"Theme '{self.theme_id}' not found in theme registry")
                
            theme = theme_info["theme"]
            
            # Check hosting pattern compatibility
            if self.hosting_pattern and not theme.is_compatible_with_hosting(self.hosting_pattern):
                raise ValueError(
                    f"Theme '{self.theme_id}' is not compatible with hosting pattern '{self.hosting_pattern}'"
                )
        
        return self
    
    @model_validator(mode="after")
    def validate_template_engine_compatibility(self):
        """Ensure template variant is compatible with selected engine and validate e-commerce config"""
        ssg_engine = self.ssg_engine
        template_variant = self.template_variant

        if ssg_engine and template_variant:
            # Get engine configuration - let errors propagate for validation
            engine_config = SSGEngineFactory.create_engine(ssg_engine, template_variant)
            
            # Check if template exists for this engine
            available_templates = [t.name for t in engine_config.available_templates]
            if template_variant not in available_templates:
                available = ", ".join(available_templates)
                raise ValueError(
                    f'Template "{template_variant}" not available for '
                    f'{ssg_engine}. Available: {available}'
                )
            
            # Get the specific template object for e-commerce validation
            template_obj = next(
                (t for t in engine_config.available_templates if t.name == template_variant), 
                None
            )
            
            if template_obj:
                # Check if e-commerce template requires provider
                if template_obj.supports_ecommerce and not self.ecommerce_provider:
                    provider_hint = (
                        template_obj.ecommerce_integration.provider 
                        if template_obj.ecommerce_integration 
                        else "unknown"
                    )
                    raise ValueError(
                        f'Template "{template_variant}" is an e-commerce template but no '
                        f'ecommerce_provider specified. Required provider: {provider_hint}'
                    )
                
                # Check if non-ecommerce template has provider specified
                if not template_obj.supports_ecommerce and self.ecommerce_provider:
                    ecommerce_templates = [
                        t.name for t in engine_config.available_templates 
                        if t.supports_ecommerce
                    ]
                    suggestion = (
                        f" Try: {', '.join(ecommerce_templates)}" 
                        if ecommerce_templates 
                        else ""
                    )
                    raise ValueError(
                        f'Template "{template_variant}" does not support e-commerce but '
                        f'ecommerce_provider "{self.ecommerce_provider}" was specified.{suggestion}'
                    )
                
                # Validate provider matches template integration
                if (template_obj.supports_ecommerce and 
                    template_obj.ecommerce_integration and 
                    self.ecommerce_provider and 
                    template_obj.ecommerce_integration.provider != self.ecommerce_provider):
                    raise ValueError(
                        f'Template "{template_variant}" is configured for '
                        f'{template_obj.ecommerce_integration.provider} but '
                        f'{self.ecommerce_provider} was specified'
                    )

        return self

    @model_validator(mode="after") 
    def set_hosting_pattern_defaults(self):
        """Auto-select hosting pattern based on business tier and client requirements"""
        
        # If hosting pattern is explicitly set, respect the client choice
        if self.hosting_pattern is not None:
            return self
        
        # Matrix-based hosting pattern selection aligned with business strategy
        # Based on tech-stack-product-matrix.md service tier positioning
        
        # Technical tier: Jekyll + GitHub Pages users prefer GitHub/hybrid
        if self.ssg_engine == "jekyll" and self.performance_tier == "basic":
            # Technical users often want GitHub Pages option for cost/control
            self.hosting_pattern = "hybrid"  # AWS primary + GitHub fallback
            
        # Individual/small business tier: Cost-optimized patterns
        elif self.performance_tier == "basic":
            # Basic tier focuses on cost optimization
            if self.ecommerce_provider in ["snipcart", "foxy"]:
                # E-commerce needs AWS for proper integration
                self.hosting_pattern = "aws_minimal"  # Cost-optimized AWS
            else:
                # Static sites can use GitHub for ultra-low cost
                self.hosting_pattern = "github"
                
        # Professional tier: Full AWS with performance optimization
        elif self.performance_tier == "optimized":
            # Professional small business tier needs reliable AWS
            self.hosting_pattern = "aws"  # Full AWS hosting
            
        # Premium/Enterprise tier: Hybrid for maximum flexibility
        elif self.performance_tier == "premium":
            # Premium clients want options and redundancy
            self.hosting_pattern = "hybrid"  # AWS + GitHub fallback
            
        # Default fallback to AWS for undefined cases
        else:
            self.hosting_pattern = "aws"
        
        return self

    def get_hosting_pattern_config(self) -> Dict[str, Any]:
        """Get detailed hosting pattern configuration and costs"""
        
        pattern = self.hosting_pattern or "aws"  # Default fallback
        
        # Hosting pattern configurations aligned with business matrix
        configs = {
            "aws": {
                "name": "Full AWS Hosting",
                "description": "Complete AWS hosting with S3, CloudFront, and Route53",
                "services": ["S3", "CloudFront", "Route53", "Certificate Manager", "CodeBuild"],
                "monthly_cost_range": "$5-50",
                "setup_complexity": "Medium",
                "best_for": ["Professional sites", "Business tier", "Custom domains"],
                "features": ["Global CDN", "SSL certificates", "Custom domains", "Performance optimization"]
            },
            "github": {
                "name": "GitHub Pages Only",
                "description": "GitHub Pages hosting with optional custom domain",
                "services": ["GitHub Pages"],
                "monthly_cost_range": "$0",
                "setup_complexity": "Low",
                "best_for": ["Technical users", "Documentation", "Personal sites"],
                "features": ["Free hosting", "Git-based workflow", "Built-in CI/CD", "Jekyll support"]
            },
            "hybrid": {
                "name": "AWS + GitHub Fallback",
                "description": "Primary AWS hosting with GitHub Pages as backup option",
                "services": ["S3", "CloudFront", "Route53", "GitHub Pages"],
                "monthly_cost_range": "$5-50 (AWS) + $0 (GitHub)",
                "setup_complexity": "High",
                "best_for": ["Technical users", "Enterprise clients", "Maximum flexibility"],
                "features": ["Redundancy", "Cost flexibility", "Multiple deployment options", "Technical control"]
            },
            "aws_minimal": {
                "name": "Cost-Optimized AWS",
                "description": "AWS hosting with minimal features for cost optimization",
                "services": ["S3", "CloudFront (basic)", "Route53"],
                "monthly_cost_range": "$1-15",
                "setup_complexity": "Low",
                "best_for": ["Budget-conscious clients", "Simple sites", "Basic e-commerce"],
                "features": ["Low cost", "Essential CDN", "Basic SSL", "Simplified setup"]
            }
        }
        
        return configs.get(pattern, configs["aws"])

    def get_ssg_config(self) -> SSGEngineConfig:
        """Get the SSG engine configuration"""
        return SSGEngineFactory.create_engine(self.ssg_engine, self.template_variant)

    def get_available_templates(self) -> List[SSGTemplate]:
        """Get available templates for selected engine"""
        return SSGEngineFactory.get_engine_templates(self.ssg_engine)

    def get_ecommerce_integration(self) -> Optional[ECommerceIntegration]:
        """Get the e-commerce integration configuration for the selected template"""
        if not self.ecommerce_provider:
            return None
            
        try:
            engine_config = self.get_ssg_config()
            template_obj = next(
                (t for t in engine_config.available_templates if t.name == self.template_variant),
                None
            )
            return template_obj.ecommerce_integration if template_obj else None
        except Exception:
            return None
    
    def get_required_aws_services(self) -> List[str]:
        """Get list of AWS services required for this configuration"""
        base_services = ["S3", "CloudFront", "Route53", "Certificate Manager"]
        
        ecommerce_integration = self.get_ecommerce_integration()
        if ecommerce_integration:
            base_services.extend(ecommerce_integration.aws_services_needed)
            
        return list(set(base_services))  # Remove duplicates
    
    def get_theme_info(self) -> Optional[Dict[str, Any]]:
        """Get theme information from theme registry"""
        if not self.theme_id:
            return None
            
        # Import here to avoid circular imports
        try:
            from stacks.shared.theme_registry import ThemeRegistry
            theme = ThemeRegistry.get_theme(self.theme_id)
            if not theme:
                return None
                
            # Validate theme compatibility with engine
            if theme.engine != self.ssg_engine:
                raise ValueError(
                    f"Theme '{self.theme_id}' is for {theme.engine} but engine is {self.ssg_engine}"
                )
                
            return {
                "theme": theme,
                "installation_method": theme.installation_method,
                "source": theme.source,
                "required_plugins": theme.required_plugins,
                "github_pages_compatible": theme.github_pages_compatible,
                "customization_options": theme.customization_options,
                "installation_commands": theme.get_installation_commands(),
                "theme_env_vars": theme.get_customization_env_vars(self.theme_config)
            }
        except ImportError:
            # Theme registry not available
            return None
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables including e-commerce and theme specific ones"""
        env_vars = self.environment_vars.copy()
        
        # Add e-commerce environment variables
        ecommerce_integration = self.get_ecommerce_integration()
        if ecommerce_integration:
            for var in ecommerce_integration.required_environment_vars:
                if var not in env_vars:
                    env_vars[var] = f"${{{var}}}"  # Placeholder for CDK parameter
        
        # Add theme environment variables
        theme_info = self.get_theme_info()
        if theme_info and "theme_env_vars" in theme_info:
            env_vars.update(theme_info["theme_env_vars"])
        
        return env_vars

    def to_aws_tags(self) -> Dict[str, str]:
        """Convert configuration to AWS resource tags"""
        tags = {
            "Client": self.client_id,
            "SSGEngine": self.ssg_engine,
            "Template": self.template_variant,
            "PerformanceTier": self.performance_tier,
            "Environment": "production",  # Can be parameterized later
            "HostingPattern": self.hosting_pattern or "aws"
        }
        
        if self.theme_id:
            tags["ThemeId"] = self.theme_id
            tags["HasTheme"] = "true"
        else:
            tags["HasTheme"] = "false"
        
        if self.ecommerce_provider:
            tags["ECommerceProvider"] = self.ecommerce_provider
            tags["HasECommerce"] = "true"
        else:
            tags["HasECommerce"] = "false"
            
        return tags


# Usage Examples and Testing
if __name__ == "__main__":
    # Example: Create different engine configurations
    eleventy = SSGEngineFactory.create_engine("eleventy", "business_modern")
    hugo = SSGEngineFactory.create_engine("hugo", "corporate_clean")
    astro = SSGEngineFactory.create_engine("astro", "modern_interactive")

    print(f"Eleventy templates: {len(eleventy.available_templates)}")
    print(f"Hugo build performance: {hugo.optimization_features['build_performance']}")
    print(
        f"Astro supports component islands: "
        f"{astro.optimization_features['component_islands']}"
    )

    # Example: Client configuration
    client_config = StaticSiteConfig(
        client_id="demo-client",
        domain="demo-client.yourservices.com",
        ssg_engine="eleventy",
        template_variant="business_modern",
    )

    ssg_config = client_config.get_ssg_config()
    buildspec = ssg_config.get_buildspec()
    print(f"Generated buildspec for {ssg_config.engine_name}")
