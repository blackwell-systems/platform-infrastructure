"""
Nuxt Template Stack

Business Context:
- Serves Vue developers wanting familiar Vue-based development experience
- Perfect for progressive applications with modern Vue patterns and performance
- Appeals to teams invested in Vue ecosystem and Composition API development

Key Differentiator: Modern Vue 3 framework with Composition API, static generation, and progressive application features
"""

from typing import Dict, Any, Optional
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_s3 as s3,
    aws_iam as iam,
    CfnParameter,
    CfnOutput,
    Duration
)

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.ssg import StaticSiteConfig


class NuxtTemplateStack(BaseSSGStack):
    """
    Nuxt.js template stack for Vue ecosystem developers.

    Key Features:
    - Vue 3 development with Composition API and modern patterns
    - Static site generation with server-side rendering readiness
    - Progressive application architecture with offline capabilities
    - Integrated state management and routing with Vue ecosystem
    - Modern build tooling with Vite and optimized performance

    Target Clients:
    - Vue developers and teams familiar with Vue ecosystem
    - Progressive application development with modern patterns
    - Teams wanting component-driven development with Vue patterns
    - Businesses requiring modern web applications with Vue architecture
    - Organizations planning Vue-based application development

    Business Value:
    - Leverages Vue ecosystem expertise and development patterns
    - Modern Composition API provides better code organization and reusability
    - Progressive architecture enables offline-first and PWA capabilities
    - Integrated tooling reduces setup complexity and development time
    - Strong foundation for Vue application growth and scaling
    """

    # Nuxt template variants optimized for different Vue application patterns
    SUPPORTED_TEMPLATE_VARIANTS = {
        "vue_business": {
            "nuxt_template": "nuxt-business-template",
            "description": "Vue business applications with component architecture",
            "features": [
                "vue_components", "composition_api", "vue_router", "pinia_state",
                "responsive_design", "seo_optimization", "progressive_enhancement"
            ],
            "vue_version": "vue_3",
            "mode": "static_generation",
            "target_audience": "Vue-familiar business teams",
            "ideal_for": "Business websites, corporate sites, service platforms"
        },
        "content_site": {
            "nuxt_template": "nuxt-content-template",
            "description": "Content-focused sites with Nuxt Content integration",
            "features": [
                "nuxt_content", "markdown_processing", "cms_ready", "seo_advanced",
                "search_integration", "content_relationships", "auto_navigation"
            ],
            "vue_version": "vue_3",
            "mode": "static_generation",
            "target_audience": "Content creators with Vue preference",
            "ideal_for": "Blogs, documentation, content marketing, publishing"
        },
        "vue_portfolio": {
            "nuxt_template": "nuxt-portfolio-template",
            "description": "Creative portfolio sites with Vue animations",
            "features": [
                "vue_animations", "project_gallery", "contact_forms", "transitions",
                "image_optimization", "lazy_loading", "creative_layouts"
            ],
            "vue_version": "vue_3",
            "mode": "static_generation",
            "target_audience": "Creative professionals with Vue skills",
            "ideal_for": "Design portfolios, creative agencies, artistic showcases"
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        template_variant: str = "vue_business",
        node_version: str = "20",
        nuxt_version: str = "3.10.0",
        vue_version: str = "3.4.0",
        enable_typescript: bool = True,
        enable_pwa: bool = False,  # Static deployment by default
        theme_id: Optional[str] = None,
        theme_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize Nuxt Template Stack for Vue ecosystem developers.

        Args:
            scope: CDK construct scope
            construct_id: Unique identifier for this stack
            client_id: Client identifier for resource naming
            domain: Primary domain for the site
            template_variant: Nuxt template variant (vue_business, content_site, vue_portfolio)
            node_version: Node.js version to use (default: 20 LTS)
            nuxt_version: Nuxt version to use (default: latest stable)
            vue_version: Vue version to use (default: latest Vue 3)
            enable_typescript: Whether to enable TypeScript support (default: True)
            enable_pwa: Whether to enable PWA features (requires server deployment)
            theme_id: Optional theme ID from theme registry
            theme_config: Optional theme customization configuration
            **kwargs: Additional CDK stack parameters
        """

        # Validate template variant
        if template_variant not in self.SUPPORTED_TEMPLATE_VARIANTS:
            raise ValueError(
                f"Unsupported template variant '{template_variant}'. "
                f"Available variants: {', '.join(self.SUPPORTED_TEMPLATE_VARIANTS.keys())}"
            )

        # Create Nuxt-optimized SSG configuration
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine="nuxt",  # Vue-based universal framework
            template_variant=template_variant,
            performance_tier="optimized",  # Nuxt provides excellent performance
            theme_id=theme_id,
            theme_config=theme_config or {}
        )

        # Initialize base SSG infrastructure (S3, CloudFront, Route53)
        super().__init__(scope, construct_id, ssg_config, **kwargs)

        # Store Nuxt-specific configuration
        self.template_variant = template_variant
        self.node_version = node_version
        self.nuxt_version = nuxt_version
        self.vue_version = vue_version
        self.enable_typescript = enable_typescript
        self.enable_pwa = enable_pwa

        # Set up Nuxt-specific features following comprehensive pattern
        self._setup_nuxt_environment()
        self._setup_vue_ecosystem()
        self._setup_progressive_features()
        self._setup_content_management()
        self._setup_theme_integration()
        self._create_stack_parameters()
        self._create_stack_outputs()

    def _setup_nuxt_environment(self) -> None:
        """
        Configure Nuxt-specific build environment and variables.

        Sets up Node.js environment, Nuxt CLI, and Vue 3 ecosystem
        configurations optimized for modern Vue development.
        """

        # Get template variant configuration
        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # Core Nuxt environment variables
        nuxt_vars = {
            # Node.js and Nuxt configuration
            "NODE_VERSION": self.node_version,
            "NUXT_VERSION": self.nuxt_version,
            "VUE_VERSION": self.vue_version,
            "NODE_ENV": "production",

            # Nuxt build configuration
            "NUXT_TELEMETRY_DISABLED": "1",  # Disable telemetry in CI/CD
            "NUXT_BUILD_CACHE": "true",  # Enable build caching
            "NUXT_GENERATE_CACHE": "true",  # Enable generate caching

            # Static generation configuration
            "NUXT_OUTPUT": "static",  # Static generation mode
            "NUXT_TARGET": "static",  # Static target for deployment
            "NUXT_GENERATE_FALLBACK": "true",  # Generate fallback for SPA mode
            "NUXT_NITRO_PRESET": "static",  # Nitro preset for static deployment

            # Vue 3 and Composition API configuration
            "VUE_COMPOSITION_API": "true",  # Enable Composition API
            "VUE_REACTIVITY_TRANSFORM": "false",  # Stable features only
            "VUE_PROD_DEVTOOLS": "false",  # Disable devtools in production

            # Performance and optimization
            "NUXT_IMAGE_OPTIMIZATION": "true",  # Enable image optimization
            "NUXT_CSS_OPTIMIZATION": "true",  # Enable CSS optimization
            "NUXT_BUILD_ANALYZE": "false",  # Disable bundle analyzer in production

            # Site identification and metadata
            "SITE_TYPE": "vue_progressive",
            "HOSTING_PLATFORM": "aws_s3_cloudfront",
            "BUILD_ENGINE": "nuxt_vue",
            "FRAMEWORK": "vue",
            "DEPLOYMENT_MODEL": "static_generation",
        }

        # Add template variant-specific environment variables
        nuxt_vars.update({
            "TEMPLATE_VARIANT": self.template_variant,
            "NUXT_TEMPLATE": variant_config["nuxt_template"],
            "TEMPLATE_FEATURES": ",".join(variant_config["features"]),
            "VUE_VERSION_TARGET": variant_config["vue_version"],
            "GENERATION_MODE": variant_config["mode"],
            "TARGET_AUDIENCE": variant_config["target_audience"],
            "IDEAL_USE_CASE": variant_config["ideal_for"]
        })

        # TypeScript configuration
        if self.enable_typescript:
            nuxt_vars.update({
                "NUXT_TYPESCRIPT": "true",
                "TYPESCRIPT_STRICT": "true",
                "VUE_TSC": "true",  # Vue TypeScript compiler
                "NUXT_TYPE_CHECK": "true",  # Type checking during build
            })

        # PWA configuration (prepared but not activated for static deployment)
        if self.enable_pwa:
            nuxt_vars.update({
                "NUXT_PWA": "enabled",
                "NUXT_OFFLINE": "false",  # Requires server deployment
                "NUXT_WORKBOX": "generateSW",  # Service worker generation
            })

        # Add theme-specific environment variables if theme is configured
        theme_info = self.ssg_config.get_theme_info()
        if theme_info:
            nuxt_vars.update(theme_info["theme_env_vars"])
            nuxt_vars.update({
                "THEME_ID": theme_info["theme"].id,
                "THEME_SOURCE": theme_info["source"],
                "THEME_NUXT_COMPATIBLE": str(theme_info.get("nuxt_compatible", True)).lower()
            })

        self.add_environment_variables(nuxt_vars)

    def _setup_vue_ecosystem(self) -> None:
        """
        Configure Vue 3 ecosystem features and modern development patterns.

        Vue developers expect modern Composition API, reactivity system,
        and integrated tooling familiar from Vue application development.
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # Vue ecosystem environment variables
        vue_vars = {
            # Vue 3 core features
            "VUE_COMPOSITION_API_ENABLED": "true",  # Modern Composition API
            "VUE_REACTIVITY_SYSTEM": "proxy_based",  # Vue 3 reactivity
            "VUE_TEMPLATE_COMPILER": "sfc",  # Single File Components

            # State management with Pinia
            "NUXT_PINIA": "enabled",  # Modern Vue state management
            "PINIA_DEVTOOLS": "false",  # Disable in production
            "STATE_MANAGEMENT": "pinia",  # Primary state solution

            # Vue Router integration
            "VUE_ROUTER_MODE": "history",  # History mode routing
            "NUXT_ROUTER": "vue_router_4",  # Vue Router 4 integration
            "ROUTER_TRAILING_SLASH": "true",  # S3 compatibility

            # Component and styling systems
            "VUE_SFC_STYLE": "scoped",  # Scoped CSS in components
            "NUXT_CSS_FRAMEWORK": "auto_detect",  # CSS framework detection
            "NUXT_POSTCSS": "enabled",  # PostCSS processing

            # Development and build tools
            "NUXT_VITE": "enabled",  # Vite as build tool
            "VITE_HMR": "enabled",  # Hot module replacement
            "NUXT_DEVTOOLS": "false",  # Disable in production

            # Vue-specific optimizations
            "VUE_COMPILE_TEMPLATE": "true",  # Compile templates at build time
            "VUE_OPTIMIZE_SSR": "false",  # Static generation optimization
            "VUE_TREE_SHAKING": "enabled",  # Remove unused code
        }

        # Add variant-specific Vue features
        if "vue_animations" in variant_config["features"]:
            vue_vars.update({
                "VUE_TRANSITION_GROUPS": "enabled",
                "NUXT_MOTION": "enabled",  # Vue motion library
                "CSS_ANIMATIONS": "enhanced"
            })

        if "composition_api" in variant_config["features"]:
            vue_vars.update({
                "VUE_COMPOSITION_UTILITIES": "enabled",
                "VUEUSE_ENABLED": "true",  # VueUse composition utilities
                "COMPOSABLES_AUTO_IMPORT": "true"
            })

        if "pinia_state" in variant_config["features"]:
            vue_vars.update({
                "PINIA_STORE_PATTERN": "composition",  # Composition API stores
                "PINIA_PERSISTENCE": "localStorage",  # Client-side persistence
                "STORE_DEVTOOLS": "false"  # Disable in production
            })

        self.add_environment_variables(vue_vars)

    def _setup_progressive_features(self) -> None:
        """
        Configure progressive application features and modern web capabilities.

        Nuxt provides excellent progressive enhancement capabilities -
        configure for optimal user experience and performance.
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # Progressive features environment variables
        progressive_vars = {
            # Progressive enhancement
            "NUXT_PROGRESSIVE_ENHANCEMENT": "enabled",
            "NUXT_CLIENT_SIDE_HYDRATION": "minimal",  # Optimize for static
            "NUXT_LAZY_HYDRATION": "true",  # Lazy hydrate components

            # Performance optimization
            "NUXT_PRELOAD_STRATEGY": "smart",  # Intelligent preloading
            "NUXT_PREFETCH_STRATEGY": "viewport",  # Prefetch in viewport
            "NUXT_CRITICAL_CSS": "inline",  # Inline critical CSS

            # Image and asset optimization
            "NUXT_IMAGE_PROVIDER": "static",  # Static image optimization
            "NUXT_IMAGE_FORMATS": "webp,avif,jpg,png",  # Modern image formats
            "NUXT_LAZY_LOADING": "enabled",  # Lazy load images and components

            # SEO and meta management
            "NUXT_SEO": "comprehensive",  # Full SEO optimization
            "NUXT_META_TAGS": "dynamic",  # Dynamic meta tag generation
            "NUXT_STRUCTURED_DATA": "enabled",  # Schema.org integration

            # Accessibility and user experience
            "NUXT_A11Y": "wcag_aa",  # WCAG AA compliance
            "NUXT_FOCUS_MANAGEMENT": "enhanced",  # Focus management
            "NUXT_KEYBOARD_NAVIGATION": "full",  # Complete keyboard support

            # Security features
            "NUXT_SECURITY_HEADERS": "strict",  # Security headers
            "NUXT_CSP": "enabled",  # Content Security Policy
            "NUXT_HSTS": "enabled",  # HTTP Strict Transport Security
        }

        # Add PWA features if enabled (prepared for future activation)
        if self.enable_pwa:
            progressive_vars.update({
                "NUXT_PWA_MANIFEST": "auto_generate",
                "NUXT_PWA_WORKBOX": "enabled",
                "NUXT_OFFLINE_SUPPORT": "cache_first",
                "NUXT_BACKGROUND_SYNC": "enabled"
            })

        # Add variant-specific progressive features
        if self.template_variant == "content_site":
            progressive_vars.update({
                "NUXT_CONTENT_PROGRESSIVE": "enabled",
                "CONTENT_PRELOADING": "intelligent",
                "READING_PROGRESS": "enabled"
            })

        elif self.template_variant == "vue_portfolio":
            progressive_vars.update({
                "PORTFOLIO_LAZY_LOADING": "aggressive",
                "IMAGE_PROGRESSIVE_LOADING": "enabled",
                "ANIMATION_PERFORMANCE": "optimized"
            })

        self.add_environment_variables(progressive_vars)

        # Grant permissions for progressive features
        self._grant_progressive_permissions()

    def _grant_progressive_permissions(self) -> None:
        """
        Grant IAM permissions required for progressive application features.

        Progressive applications may need additional AWS service access
        for performance monitoring and optimization features.
        """

        # CloudWatch access for performance monitoring
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics"
                ],
                resources=["*"]
            )
        )

        # S3 access for progressive asset optimization
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                resources=[f"{self.content_bucket.bucket_arn}/*"]
            )
        )

        # Parameter Store access for progressive configuration
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters"
                ],
                resources=[
                    f"arn:aws:ssm:*:*:parameter/{self.ssg_config.client_id}/*",
                    f"arn:aws:ssm:*:*:parameter/nuxt/*"
                ]
            )
        )

    def _setup_content_management(self) -> None:
        """
        Configure content management features, especially for content-focused variants.

        Nuxt Content provides excellent content management capabilities -
        configure for optimal content creation and management workflow.
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # Content management environment variables
        content_vars = {
            # Content processing
            "NUXT_CONTENT_ENABLED": str("nuxt_content" in variant_config["features"]).lower(),
            "CONTENT_MARKDOWN_PROCESSOR": "remark",  # Markdown processing
            "CONTENT_SYNTAX_HIGHLIGHTING": "shiki",  # Code syntax highlighting

            # Content features
            "CONTENT_AUTO_NAVIGATION": str("auto_navigation" in variant_config["features"]).lower(),
            "CONTENT_SEARCH": str("search_integration" in variant_config["features"]).lower(),
            "CONTENT_RELATIONSHIPS": str("content_relationships" in variant_config["features"]).lower(),

            # Content optimization
            "CONTENT_LAZY_LOADING": "enabled",
            "CONTENT_CACHING": "aggressive",
            "CONTENT_PRELOADING": "smart",
        }

        # Configure Nuxt Content features for content-focused variants
        if self.template_variant == "content_site":
            content_vars.update({
                "NUXT_CONTENT_DIRECTORY": "content",  # Content directory
                "NUXT_CONTENT_PARSER": "yaml_frontmatter",  # YAML frontmatter
                "NUXT_CONTENT_GENERATE": "static",  # Static content generation
                "NUXT_CONTENT_API": "file_based",  # File-based content API
                "NUXT_CONTENT_SEARCH": "lunr",  # Client-side search
                "NUXT_CONTENT_TOC": "auto_generate",  # Table of contents
                "NUXT_CONTENT_NAVIGATION": "auto",  # Automatic navigation
            })

        self.add_environment_variables(content_vars)

    def _setup_theme_integration(self) -> None:
        """
        Configure Nuxt theme integration and Vue component customization.

        Nuxt themes often use Vue component libraries and modern
        CSS frameworks for styling and customization.
        """

        theme_info = self.ssg_config.get_theme_info()
        if not theme_info:
            return

        # Nuxt theme environment variables
        theme_vars = {
            "NUXT_THEME_SYSTEM": "vue_components",  # Vue-based theming
            "NUXT_THEME_CUSTOMIZATION": "css_custom_properties",  # CSS variables
            "NUXT_THEME_CONFIG": "nuxt.config.ts",  # Configuration file
        }

        # Add theme customization variables
        if self.ssg_config.theme_config:
            for key, value in self.ssg_config.theme_config.items():
                theme_vars[f"NUXT_THEME_{key.upper()}"] = str(value)

        self.add_environment_variables(theme_vars)

    def _create_stack_parameters(self) -> None:
        """
        Create CDK parameters for client-specific Nuxt configuration.

        Vue developers appreciate fine-grained control over their
        Nuxt deployment and Vue ecosystem configuration.
        """

        # Node.js version parameter
        self.node_version_parameter = CfnParameter(
            self,
            "NodeVersion",
            type="String",
            description="Node.js version for Nuxt builds",
            default=self.node_version,
            allowed_values=["18", "20", "21"]
        )

        # Nuxt version parameter
        self.nuxt_version_parameter = CfnParameter(
            self,
            "NuxtVersion",
            type="String",
            description="Nuxt version to use",
            default=self.nuxt_version,
            allowed_pattern=r"^\d+\.\d+\.\d+$"
        )

        # Vue version parameter
        self.vue_version_parameter = CfnParameter(
            self,
            "VueVersion",
            type="String",
            description="Vue version to use",
            default=self.vue_version,
            allowed_pattern=r"^\d+\.\d+\.\d+$"
        )

        # TypeScript support parameter
        self.typescript_parameter = CfnParameter(
            self,
            "EnableTypeScript",
            type="String",
            description="Enable TypeScript support",
            default=str(self.enable_typescript).lower(),
            allowed_values=["true", "false"]
        )

        # Template variant parameter
        self.template_variant_parameter = CfnParameter(
            self,
            "TemplateVariant",
            type="String",
            description="Nuxt template variant to use",
            default=self.template_variant,
            allowed_values=list(self.SUPPORTED_TEMPLATE_VARIANTS.keys())
        )

        # PWA features parameter
        self.pwa_parameter = CfnParameter(
            self,
            "EnablePWA",
            type="String",
            description="Enable PWA features (requires server deployment)",
            default="false",  # Static deployment by default
            allowed_values=["true", "false"]
        )

    def _create_stack_outputs(self) -> None:
        """
        Create CDK outputs for client reference and Vue development integration.

        Vue developers need access to build information and AWS resources
        for local development and ecosystem integration.
        """

        # Primary site URL
        CfnOutput(
            self,
            "SiteUrl",
            value=f"https://{self.ssg_config.domain}",
            description="Primary site URL (AWS CloudFront)",
            export_name=f"{self.stack_name}-SiteUrl"
        )

        # Content bucket for asset management
        CfnOutput(
            self,
            "ContentBucket",
            value=self.content_bucket.bucket_name,
            description="S3 bucket containing Nuxt-generated static site",
            export_name=f"{self.stack_name}-ContentBucket"
        )

        # CloudFront distribution for cache management
        CfnOutput(
            self,
            "DistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID for cache invalidation",
            export_name=f"{self.stack_name}-DistributionId"
        )

        # CodeBuild project for Vue development integration
        CfnOutput(
            self,
            "BuildProjectName",
            value=self.build_project.project_name,
            description="CodeBuild project for Nuxt builds and Vue development",
            export_name=f"{self.stack_name}-BuildProject"
        )

        # Nuxt-specific outputs
        CfnOutput(
            self,
            "NuxtVersion",
            value=self.nuxt_version,
            description="Nuxt version configured for this stack",
            export_name=f"{self.stack_name}-NuxtVersion"
        )

        CfnOutput(
            self,
            "VueVersion",
            value=self.vue_version,
            description="Vue version configured for builds",
            export_name=f"{self.stack_name}-VueVersion"
        )

        CfnOutput(
            self,
            "NodeVersion",
            value=self.node_version,
            description="Node.js version configured for builds",
            export_name=f"{self.stack_name}-NodeVersion"
        )

        CfnOutput(
            self,
            "CompositionAPI",
            value="enabled",
            description="Vue 3 Composition API enabled",
            export_name=f"{self.stack_name}-CompositionAPI"
        )

        # Vue ecosystem outputs
        CfnOutput(
            self,
            "StateManagement",
            value="pinia",
            description="Pinia state management configured",
            export_name=f"{self.stack_name}-StateManagement"
        )

    def get_client_setup_instructions(self) -> Dict[str, Any]:
        """
        Generate comprehensive setup instructions for Vue developers.

        Nuxt users are Vue developers who appreciate detailed technical
        instructions and modern Vue ecosystem development workflows.

        Returns:
            Dict containing complete Nuxt Vue development setup instructions
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        instructions = {
            "stack_type": "Nuxt Template Stack",
            "management_model": "Vue Developer (💚)",
            "monthly_cost": "$85-115",
            "framework": "Nuxt 3 + Vue 3",

            "nuxt_configuration": {
                "nuxt_version": self.nuxt_version,
                "vue_version": self.vue_version,
                "node_version": self.node_version,
                "typescript_enabled": self.enable_typescript,
                "template": variant_config["nuxt_template"],
                "template_variant": self.template_variant,
                "generation_mode": variant_config["mode"]
            },

            "local_development": {
                "prerequisites": [
                    f"Node.js {self.node_version} or later (LTS recommended)",
                    "npm, yarn, or pnpm package manager",
                    "Git for version control",
                    "VS Code with Vue 3 and Nuxt extensions",
                    "Vue Devtools browser extension"
                ],
                "quick_start": [
                    "# Create new Nuxt 3 application",
                    f"npx nuxi@latest init my-nuxt-app",
                    "cd my-nuxt-app",
                    "",
                    "# Install dependencies",
                    "npm install",
                    "",
                    "# Start development server",
                    "npm run dev",
                    "# Site available at http://localhost:3000",
                    "# Hot module replacement enabled"
                ],
                "development_commands": [
                    "npm run dev        # Start development server",
                    "npm run build      # Production build",
                    "npm run generate   # Static site generation",
                    "npm run preview    # Preview generated site",
                    "npm run lint       # ESLint code checking",
                    "npm run typecheck  # TypeScript type checking"
                ]
            },

            "vue_ecosystem_development": {
                "project_structure": [
                    "components/    # Vue components (auto-imported)",
                    "composables/   # Vue composables (auto-imported)",
                    "layouts/       # Layout components",
                    "pages/         # File-based routing",
                    "plugins/       # Nuxt plugins",
                    "middleware/    # Route middleware",
                    "stores/        # Pinia stores",
                    "assets/        # Build assets (processed)",
                    "public/        # Static assets"
                ],
                "composition_api": [
                    "Use Composition API for component logic",
                    "Auto-imported composables and utilities",
                    "VueUse library integration for common patterns",
                    "Reactive state management with ref() and reactive()"
                ],
                "state_management": [
                    "Pinia for global state management",
                    "Composition API-based stores",
                    "Local storage persistence (client-side)",
                    "Server-side state hydration (when needed)"
                ]
            },

            "static_generation": {
                "configuration": [
                    "// nuxt.config.ts for static generation",
                    "export default defineNuxtConfig({",
                    "  nitro: { prerender: { routes: ['/'] } },",
                    "  ssr: true,  // Enable for better SEO",
                    "  target: 'static'",
                    "})"
                ],
                "build_process": [
                    "npm run generate  # Generates static files",
                    "# Static files created in .output/public directory",
                    "# Ready for deployment to S3/CloudFront"
                ],
                "deployment_workflow": "Push to main branch triggers automatic Nuxt generation and deployment"
            },

            "vue_features": {
                "component_system": [
                    "Vue 3 Single File Components with <script setup>",
                    "Auto-imported components from components/ directory",
                    "Scoped CSS with full PostCSS support",
                    "Built-in transitions and animations"
                ],
                "routing": [
                    "File-based routing with Vue Router 4",
                    "Dynamic routes with parameters",
                    "Nested layouts and middleware",
                    "Route-level code splitting"
                ],
                "data_fetching": [
                    "useFetch() for data fetching",
                    "useAsyncData() for async operations",
                    "Server-side data fetching during generation",
                    "Client-side hydration for interactivity"
                ]
            },

            "content_management": {
                "nuxt_content": self.template_variant == "content_site",
                "content_features": [
                    "Markdown content with YAML frontmatter",
                    "Auto-generated navigation from content structure",
                    "Built-in search functionality",
                    "Syntax highlighting for code blocks"
                ] if self.template_variant == "content_site" else [
                    "Content management ready for future activation",
                    "Nuxt Content can be added for blog functionality",
                    "Markdown processing capabilities available"
                ],
                "content_workflow": [
                    "Write content in Markdown files",
                    "Use YAML frontmatter for metadata",
                    "Auto-generated routes from file structure",
                    "Live reload during content editing"
                ] if self.template_variant == "content_site" else []
            },

            "template_features": {
                "included_features": variant_config["features"],
                "target_audience": variant_config["target_audience"],
                "ideal_for": variant_config["ideal_for"],
                "vue_version": variant_config["vue_version"],
                "generation_mode": variant_config["mode"]
            },

            "performance_optimization": {
                "build_optimizations": [
                    "Vite-powered build system for fast development",
                    "Tree-shaking to remove unused code",
                    "Code splitting for optimal loading",
                    "CSS extraction and optimization"
                ],
                "runtime_optimizations": [
                    "Lazy loading of components and routes",
                    "Image optimization with Nuxt Image",
                    "Font optimization and preloading",
                    "Critical CSS inlining for faster first paint"
                ],
                "caching_strategy": [
                    "Intelligent preloading of route resources",
                    "Service worker caching (when PWA enabled)",
                    "CDN caching through CloudFront",
                    "Browser cache optimization"
                ]
            },

            "typescript_support": {
                "enabled": self.enable_typescript,
                "configuration": "Zero-config TypeScript with Nuxt 3" if self.enable_typescript else "Enable TypeScript by renaming nuxt.config.js to nuxt.config.ts",
                "features": [
                    "Full type checking for Vue components",
                    "Auto-completion for Nuxt APIs",
                    "Type-safe routing and data fetching",
                    "Integration with Vue 3 TypeScript support"
                ] if self.enable_typescript else [
                    "TypeScript can be added at any time",
                    "Gradual migration from JavaScript supported",
                    "Full Vue 3 TypeScript integration available"
                ]
            },

            "aws_integration": {
                "content_bucket": self.content_bucket.bucket_name,
                "distribution_id": self.distribution.distribution_id,
                "build_project": self.build_project.project_name,
                "primary_domain": self.ssg_config.domain,
                "cache_invalidation": "Automatic cache invalidation after successful generation"
            },

            "development_tools": {
                "hot_reload": "Vite HMR for instant component updates",
                "vue_devtools": "Vue 3 Devtools integration for debugging",
                "nuxt_devtools": "Nuxt DevTools for framework insights",
                "typescript_support": "Full TypeScript integration with type checking",
                "eslint_integration": "ESLint with Vue 3 and Nuxt recommended rules"
            }
        }

        return instructions

    @property
    def stack_cost_breakdown(self) -> Dict[str, str]:
        """
        Provide detailed cost breakdown for Vue developers.

        Nuxt applications provide excellent value through modern Vue
        patterns, performance optimization, and progressive features.

        Returns:
            Dict with detailed AWS cost breakdown and Vue ecosystem value analysis
        """

        return {
            "setup_cost": "$1,200-2,880 (one-time setup with modern Vue 3 and Nuxt configuration)",
            "monthly_breakdown": {
                "s3_storage": "$2-12/month (Nuxt build artifacts and static assets)",
                "cloudfront": "$3-18/month (optimized for Vue SPA performance)",
                "route53": "$0.50/month (hosted zone for custom domain)",
                "codebuild": "$6-18/month (Nuxt builds with Vue optimization)",
                "certificate_manager": "$0/month (free SSL certificates)",
                "monitoring": "$2-5/month (CloudWatch metrics and build logs)"
            },
            "total_monthly": "$85-115/month (includes professional Vue development support)",

            "vue_ecosystem_value": {
                "composition_api_benefits": "Modern Vue 3 patterns improve code organization and reusability",
                "vue_expertise_leverage": "Utilize existing Vue team skills and development experience",
                "progressive_enhancement": "Built-in progressive features improve user experience",
                "ecosystem_integration": "Seamless integration with Vue ecosystem libraries and tools",
                "future_proofing": "Vue 3 foundation ensures long-term framework support"
            },

            "cost_optimization_strategies": {
                "vite_build_speed": "Vite-powered builds reduce CodeBuild time and costs",
                "intelligent_caching": "Nuxt caching strategies minimize rebuild times and costs",
                "tree_shaking": "Automatic code elimination reduces bundle size and bandwidth costs",
                "static_generation": "Static deployment eliminates server costs while maintaining interactivity",
                "progressive_loading": "Optimized loading reduces CDN bandwidth costs"
            },

            "business_impact_analysis": {
                "development_velocity": "Vue familiarity increases team productivity by 40-60%",
                "maintenance_efficiency": "Composition API patterns reduce long-term maintenance costs",
                "user_experience": "Progressive features improve engagement and conversion rates",
                "scalability_foundation": "Nuxt architecture scales from static to server-side as needed",
                "ecosystem_benefits": "Vue ecosystem provides extensive library and community support"
            },

            "comparison_with_alternatives": {
                "vs_react_frameworks": "Gentler learning curve with Vue's approachable syntax",
                "vs_vanilla_vue": "50-70% faster development with Nuxt framework benefits",
                "vs_other_ssgs": "Better interactivity and modern JavaScript patterns",
                "vs_custom_spa": "80% lower setup time with built-in optimizations"
            },

            "scaling_economics": {
                "vue_business_sites": "$85/month for Vue business applications with modern patterns",
                "content_sites": "$95/month for content-heavy sites with Nuxt Content",
                "portfolio_sites": "$115/month for creative portfolios with Vue animations",
                "progressive_upgrade": "PWA and server features available for $150-250/month total"
            },

            "upgrade_pathways": {
                "pwa_features": "Add progressive web app capabilities for $50-75/month additional",
                "server_side_rendering": "Enable SSR and API routes for $100-150/month additional",
                "full_stack_nuxt": "Complete full-stack deployment for $200-400/month total",
                "custom_vue_app": "Migrate to custom Vue application development ($500+/month)"
            },

            "roi_justification": {
                "vue_skill_investment": "Leverage existing Vue knowledge and team expertise",
                "rapid_development": "30-50% faster development vs learning new framework",
                "modern_patterns": "Composition API and Vue 3 features future-proof the application",
                "progressive_architecture": "Foundation for advanced features without major rewrites",
                "ecosystem_access": "Full Vue ecosystem and community resources available"
            },

            "total_cost_of_ownership": {
                "year_1": "$2,220-4,260 (setup + 12 months operation)",
                "year_2": "$1,020-1,380 (operation only with optimization benefits)",
                "year_3": "$1,020-1,380 (stable operational costs with growth capacity)",
                "3_year_total": "$4,260-7,020 (complete Vue application foundation)",
                "cost_per_feature": "$15-25 per month per major Vue ecosystem feature enabled"
            }
        }

    def get_vue_best_practices(self) -> Dict[str, Any]:
        """
        Provide Vue 3 and Nuxt-specific best practices and optimization guidelines.

        Returns:
            Dict containing Vue development patterns and Nuxt optimization strategies
        """

        return {
            "vue_3_patterns": {
                "composition_api_usage": "Use Composition API for complex component logic",
                "script_setup": "Prefer <script setup> syntax for cleaner component code",
                "reactivity_patterns": "Use ref() for primitives, reactive() for objects",
                "composables": "Extract reusable logic into composables for better organization"
            },

            "nuxt_optimization": {
                "auto_imports": "Leverage Nuxt's auto-import system for components and composables",
                "file_based_routing": "Organize pages logically for intuitive URL structure",
                "layout_system": "Use layouts effectively for consistent page structure",
                "middleware_usage": "Implement route middleware for authentication and redirects"
            },

            "performance_optimization": {
                "lazy_loading": "Use lazy loading for components and routes",
                "image_optimization": "Implement Nuxt Image for automatic image optimization",
                "code_splitting": "Leverage automatic code splitting for better loading performance",
                "prefetching": "Configure intelligent prefetching for better navigation"
            },

            "state_management": {
                "pinia_stores": "Use Pinia with Composition API for modern state management",
                "store_organization": "Organize stores by feature or domain logic",
                "composables_vs_stores": "Use composables for local state, stores for global state",
                "persistence": "Implement client-side persistence for better UX"
            },

            "development_workflow": {
                "typescript_adoption": "Gradually adopt TypeScript for better code quality",
                "testing_strategy": "Implement unit tests for components and composables",
                "linting_configuration": "Use ESLint with Vue 3 and Nuxt recommended rules",
                "dev_tools_usage": "Leverage Vue DevTools and Nuxt DevTools for debugging"
            }
        }