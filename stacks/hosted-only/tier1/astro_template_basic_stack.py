"""
Astro Template Basic Stack

High-performance Tier 1 service for modern interactive static sites.
Targets: Small businesses wanting modern performance and interactive features
Management: Developer-managed with optional CMS integration ($60-85/month)

Business Model:
- Setup Revenue: $1,200-2,400 (intermediate setup complexity)
- Monthly Revenue: $60-85 (hosting + performance optimization)
- Target Market: Small businesses, agencies, modern web applications
- Performance Focus: Sub-second loading with component islands

Technical Features:
- Astro SSG with component islands architecture
- Zero JavaScript by default with selective hydration
- Framework-agnostic (React, Vue, Svelte components)
- Built-in performance optimization and modern build tools
- Optional headless CMS integration (Decap, Tina)
- TypeScript support with excellent developer experience
"""

from typing import Dict, Any, Optional
from constructs import Construct

from shared.base.base_ssg_stack import BaseSSGStack
from shared.ssg import StaticSiteConfig


class AstroTemplateBasicStack(BaseSSGStack):
    """
    Modern interactive static sites using Astro SSG with component islands.

    Key Features:
    - Ultra-fast loading with Astro's component islands architecture
    - Zero JavaScript by default with selective hydration for interactivity
    - Framework-agnostic components (React, Vue, Svelte)
    - Built-in performance optimization and modern build tools
    - TypeScript support with excellent developer experience
    - Optional headless CMS integration for content management
    - Cost-optimized infrastructure for small businesses

    Performance Benefits:
    - Component islands: Only interactive components ship JavaScript
    - Partial hydration: Hydrate components only when needed
    - Modern build optimizations: Vite-powered build system
    - Automatic code splitting and bundle optimization
    - Built-in image optimization and lazy loading

    Target Use Cases:
    - Modern business websites requiring interactivity
    - Component showcases and design systems
    - Small applications with mixed static/dynamic content
    - Performance-critical sites with modern aesthetics
    - Sites requiring framework flexibility (React + Vue components)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        enable_cms: bool = False,
        cms_provider: str = "decap",
        **kwargs
    ):
        """
        Initialize Astro Template Basic stack.

        Args:
            scope: CDK app or stage for this stack
            construct_id: Unique identifier for this stack instance
            client_id: Client identifier (kebab-case, used for AWS resource naming)
            domain: Primary domain for the site (e.g., "business.example.com")
            enable_cms: Whether to enable headless CMS integration
            cms_provider: CMS provider ("decap", "tina", "contentful")
            **kwargs: Additional CDK stack parameters
        """
        # Create SSG configuration for Astro
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine="astro",
            template_variant="modern_interactive",
            performance_tier="optimized",  # Astro sites benefit from performance optimization
            environment_vars={
                "ASTRO_TELEMETRY_DISABLED": "1",  # Disable telemetry for privacy
                "NODE_ENV": "production",
                "SITE_TYPE": "interactive"
            }
        )

        # Initialize base SSG infrastructure
        super().__init__(scope, construct_id, ssg_config, **kwargs)

        # Store CMS configuration
        self.enable_cms = enable_cms
        self.cms_provider = cms_provider

        # Add Astro-specific configurations
        self._setup_astro_features()
        if enable_cms:
            self._setup_cms_integration()

    def _setup_astro_features(self) -> None:
        """Configure Astro-specific features and optimizations"""

        # Astro build optimization
        astro_vars = {
            # Core Astro configuration
            "ASTRO_TELEMETRY_DISABLED": "1",  # Privacy-focused
            "NODE_ENV": "production",
            "SITE_TYPE": "interactive",

            # Performance optimization
            "ASTRO_EXPERIMENTAL_ASSETS": "true",  # Enhanced asset handling
            "ASTRO_EXPERIMENTAL_VIEW_TRANSITIONS": "true",  # Smooth page transitions

            # Build optimization
            "VITE_BUILD_OPTIMIZE": "true",  # Vite build optimizations
            "ASTRO_PREFETCH": "true",  # Enable prefetching for faster navigation

            # Component framework configuration
            "ASTRO_REACT_ENABLED": "true",  # Enable React integration
            "ASTRO_VUE_ENABLED": "false",   # Disable Vue by default (can be enabled)
            "ASTRO_SVELTE_ENABLED": "false", # Disable Svelte by default

            # TypeScript support
            "ASTRO_TYPESCRIPT": "true",
            "TYPESCRIPT_STRICT": "true",

            # Performance monitoring
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "TRACK_COMPONENT_HYDRATION": "true",
            "BUNDLE_ANALYZER": "false"  # Can be enabled for analysis
        }

        self.add_environment_variables(astro_vars)

        # Add analytics and SEO setup
        self._setup_analytics_integration()

    def _setup_cms_integration(self) -> None:
        """Set up headless CMS integration if enabled"""

        if not self.enable_cms:
            return

        cms_configs = {
            "decap": {
                "CMS_PROVIDER": "decap",
                "DECAP_CMS_ENABLED": "true",
                "CMS_CONFIG_PATH": "src/cms/config.yml",
                "CMS_ADMIN_PATH": "/admin",
                "CMS_BACKEND": "git-gateway",  # Netlify Identity integration
                "CMS_MEDIA_FOLDER": "src/assets/images",
                "CMS_PUBLIC_FOLDER": "/images"
            },
            "tina": {
                "CMS_PROVIDER": "tina",
                "TINA_CMS_ENABLED": "true",
                "TINA_CLIENT_ID": "${TINA_CLIENT_ID}",  # CDK parameter
                "TINA_TOKEN": "${TINA_TOKEN}",  # CDK parameter
                "TINA_BRANCH": "main",
                "TINA_CONFIG_PATH": "tina/config.ts"
            },
            "contentful": {
                "CMS_PROVIDER": "contentful",
                "CONTENTFUL_SPACE_ID": "${CONTENTFUL_SPACE_ID}",  # CDK parameter
                "CONTENTFUL_ACCESS_TOKEN": "${CONTENTFUL_ACCESS_TOKEN}",  # CDK parameter
                "CONTENTFUL_PREVIEW_ACCESS_TOKEN": "${CONTENTFUL_PREVIEW_TOKEN}",  # CDK parameter
                "CONTENTFUL_ENVIRONMENT": "master"
            }
        }

        cms_vars = cms_configs.get(self.cms_provider, cms_configs["decap"])
        self.add_environment_variables(cms_vars)

    def _setup_analytics_integration(self) -> None:
        """Set up analytics and performance tracking"""

        analytics_vars = {
            # Analytics integration
            "GOOGLE_ANALYTICS_ID": "${GOOGLE_ANALYTICS_ID}",  # CDK parameter
            "GOOGLE_TAG_MANAGER_ID": "${GOOGLE_TAG_MANAGER_ID}",  # CDK parameter

            # Performance monitoring specific to Astro
            "ASTRO_PERFORMANCE_TRACKING": "true",  # Track component hydration performance
            "WEB_VITALS_TRACKING": "true",  # Core Web Vitals monitoring
            "COMPONENT_ISLAND_ANALYTICS": "true",  # Track island hydration patterns

            # SEO optimization
            "ASTRO_SEO_ENABLED": "true",
            "GENERATE_SITEMAP": "true",
            "ROBOTS_TXT_ENABLED": "true",

            # Social media optimization
            "FACEBOOK_PIXEL_ID": "${FACEBOOK_PIXEL_ID}",  # CDK parameter
            "TWITTER_SITE": "${TWITTER_HANDLE}",  # CDK parameter

            # Development and debugging (can be disabled in production)
            "ASTRO_DEV_TOOLBAR": "false",  # Disable dev toolbar in production
            "ASTRO_DEBUG": "false"
        }

        self.add_environment_variables(analytics_vars)

    def _setup_github_source(self) -> None:
        """Set up GitHub source integration for Astro template repository"""
        # TODO: Implement GitHub source integration
        # Repository: https://github.com/your-templates/astro-modern-interactive
        #
        # The template includes:
        # - Astro project with component islands architecture
        # - React components for interactive elements
        # - TypeScript configuration and strict type checking
        # - Tailwind CSS for modern styling
        # - Built-in SEO components and meta tag management
        # - Image optimization with Astro's asset pipeline
        # - Optional CMS integration (Decap/Tina/Contentful)
        # - Performance optimization configuration
        # - Modern development tooling (ESLint, Prettier, etc.)
        pass

    def get_astro_configuration(self) -> Dict[str, Any]:
        """
        Get Astro configuration details for client documentation.

        Returns comprehensive setup information that clients need to
        understand and customize their Astro deployment.
        """
        return {
            "ssg_engine": "astro",
            "template_variant": "modern_interactive",
            "framework": "astro",
            "component_frameworks": ["react"],  # Can be extended to Vue, Svelte
            "build_system": "vite",
            "typescript_support": True,

            # Performance characteristics
            "performance_features": [
                "component_islands",
                "partial_hydration",
                "zero_js_by_default",
                "automatic_code_splitting",
                "built_in_optimizations"
            ],

            # CMS integration
            "cms_enabled": self.enable_cms,
            "cms_provider": self.cms_provider if self.enable_cms else None,
            "cms_admin_path": "/admin" if self.enable_cms else None,

            # Development experience
            "development_features": [
                "hot_module_reloading",
                "typescript_support",
                "component_dev_server",
                "automatic_type_checking",
                "modern_tooling"
            ],

            # Business metrics
            "setup_complexity": "intermediate",
            "estimated_setup_hours": 4.0,
            "monthly_cost_estimate": "$60-85",
            "target_market": ["small_businesses", "modern_websites", "interactive_sites"],

            # Technical details
            "node_version": "20",
            "build_time": "fast",
            "bundle_size": "minimal",
            "seo_optimized": True,
            "performance_score": "excellent",

            # Documentation and resources
            "documentation_url": "https://docs.astro.build/",
            "template_repo": "https://github.com/your-templates/astro-modern-interactive",
            "demo_url": "https://demo.yourservices.com/astro-interactive",
            "community_support": "https://astro.build/chat"
        }

    def get_cms_setup_guide(self) -> Dict[str, Any]:
        """
        Get CMS setup guide if CMS integration is enabled.

        Returns step-by-step instructions for configuring
        the selected headless CMS with this Astro stack.
        """
        if not self.enable_cms:
            return {"cms_enabled": False, "message": "CMS integration not enabled for this stack"}

        cms_guides = {
            "decap": {
                "title": "Decap CMS Setup Guide",
                "steps": [
                    {
                        "step": 1,
                        "title": "Enable Netlify Identity",
                        "description": "Set up Netlify Identity for authentication",
                        "action": "Configure in Netlify dashboard > Identity"
                    },
                    {
                        "step": 2,
                        "title": "Configure CMS Config",
                        "description": "Customize src/cms/config.yml for your content structure",
                        "file": "src/cms/config.yml"
                    },
                    {
                        "step": 3,
                        "title": "Deploy and Test",
                        "description": "Deploy site and access admin at /admin",
                        "url": f"https://{self.ssg_config.domain}/admin"
                    }
                ],
                "cost": "$0 (included with Netlify Identity)",
                "management": "Visual interface for non-technical users"
            },
            "tina": {
                "title": "Tina CMS Setup Guide",
                "steps": [
                    {
                        "step": 1,
                        "title": "Create Tina Account",
                        "description": "Sign up at tina.io and create a project",
                        "action": "Get Client ID and Token"
                    },
                    {
                        "step": 2,
                        "title": "Configure CDK Parameters",
                        "description": "Set Tina credentials in CDK parameters",
                        "parameters": ["TINA_CLIENT_ID", "TINA_TOKEN"]
                    },
                    {
                        "step": 3,
                        "title": "Deploy and Access",
                        "description": "Access visual editor at /admin/index.html",
                        "url": f"https://{self.ssg_config.domain}/admin/index.html"
                    }
                ],
                "cost": "$29/month (Tina Cloud)",
                "management": "Visual editing with live preview"
            },
            "contentful": {
                "title": "Contentful CMS Setup Guide",
                "steps": [
                    {
                        "step": 1,
                        "title": "Create Contentful Space",
                        "description": "Set up content models in Contentful dashboard",
                        "action": "Get Space ID and Access Tokens"
                    },
                    {
                        "step": 2,
                        "title": "Configure CDK Parameters",
                        "description": "Set Contentful credentials",
                        "parameters": ["CONTENTFUL_SPACE_ID", "CONTENTFUL_ACCESS_TOKEN"]
                    },
                    {
                        "step": 3,
                        "title": "Content Sync",
                        "description": "Content updates trigger automatic rebuilds",
                        "webhook": "Configured automatically"
                    }
                ],
                "cost": "$300/month (Contentful Basic)",
                "management": "Professional content management interface"
            }
        }

        return cms_guides.get(self.cms_provider, {"error": f"Unknown CMS provider: {self.cms_provider}"})

    @property
    def outputs(self) -> Dict[str, Any]:
        """Enhanced outputs including Astro and CMS specific information"""
        base_outputs = super().outputs

        # Add Astro-specific outputs
        astro_outputs = {
            "ssg_engine": "astro",
            "template_variant": "modern_interactive",
            "component_frameworks": ["react"],
            "typescript_enabled": True,
            "cms_integration": self.enable_cms,
            "cms_provider": self.cms_provider if self.enable_cms else None,
            "cms_admin_url": f"https://{self.ssg_config.domain}/admin" if self.enable_cms else None,
            "performance_optimized": True,
            "build_system": "vite",
            "setup_complexity": "intermediate",
            "estimated_setup_hours": 4.0,
            "monthly_cost_estimate": "$60-85",
            "documentation_url": "https://docs.astro.build/",
            "template_repo": "https://github.com/your-templates/astro-modern-interactive"
        }

        return {**base_outputs, **astro_outputs}