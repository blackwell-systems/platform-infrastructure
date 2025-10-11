"""
Gatsby Template Stack

Business Context:
- Serves React developers wanting familiar component-driven architecture
- Perfect for content-heavy sites with advanced data requirements
- Appeals to teams already invested in React ecosystem and modern JavaScript tooling

Key Differentiator: React-native development experience with GraphQL data layer and rich plugin ecosystem
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


class GatsbyTemplateStack(BaseSSGStack):
    """
    Gatsby template stack for React ecosystem developers.

    Key Features:
    - React-based development with familiar JSX components and patterns
    - GraphQL data layer for complex content relationships and queries
    - Rich plugin ecosystem for extended functionality and integrations
    - Component-driven architecture with modern React development workflow
    - Advanced image processing and performance optimizations

    Target Clients:
    - React developers and teams familiar with modern JavaScript
    - Content-heavy sites requiring complex data relationships
    - Teams wanting component reusability and modern development patterns
    - Businesses needing advanced SEO and performance optimizations
    - Organizations planning future React application development

    Business Value:
    - Leverages existing React team skills and development workflows
    - GraphQL provides powerful content querying and relationship management
    - Rich plugin ecosystem reduces custom development time and costs
    - Component architecture enables design system consistency
    - Strong SEO and performance foundation supports business growth
    """

    # Gatsby template variants optimized for React development patterns
    SUPPORTED_TEMPLATE_VARIANTS = {
        "react_business": {
            "gatsby_starter": "gatsby-starter-business",
            "description": "React-based business sites with component architecture",
            "features": [
                "react_components", "contact_forms", "seo_optimization",
                "analytics_integration", "responsive_design", "accessibility"
            ],
            "plugins": [
                "gatsby-plugin-react-helmet", "gatsby-plugin-sitemap",
                "gatsby-plugin-google-analytics", "gatsby-plugin-manifest"
            ],
            "target_audience": "React-familiar business teams",
            "ideal_for": "Business websites, marketing sites, professional services"
        },
        "content_blog": {
            "gatsby_starter": "gatsby-starter-blog",
            "description": "Content-focused blog sites with GraphQL data layer",
            "features": [
                "markdown_processing", "rss_feeds", "categories", "tags",
                "graphql_queries", "content_relationships", "search"
            ],
            "plugins": [
                "gatsby-transformer-remark", "gatsby-plugin-feed",
                "gatsby-plugin-typography", "gatsby-plugin-sharp"
            ],
            "target_audience": "Content creators with React preference",
            "ideal_for": "Technical blogs, content marketing, publishing platforms"
        },
        "portfolio_showcase": {
            "gatsby_starter": "gatsby-starter-portfolio",
            "description": "Creative portfolio sites with advanced image processing",
            "features": [
                "image_gallery", "project_pages", "contact_forms", "case_studies",
                "image_optimization", "lazy_loading", "lightbox"
            ],
            "plugins": [
                "gatsby-plugin-image", "gatsby-plugin-sharp", "gatsby-transformer-sharp",
                "gatsby-plugin-typography", "gatsby-plugin-styled-components"
            ],
            "target_audience": "Creative professionals with technical skills",
            "ideal_for": "Designer portfolios, agency showcases, creative professionals"
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        template_variant: str = "react_business",
        node_version: str = "20",
        gatsby_version: str = "5.13.0",
        enable_typescript: bool = True,
        theme_id: Optional[str] = None,
        theme_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize Gatsby Template Stack for React ecosystem developers.

        Args:
            scope: CDK construct scope
            construct_id: Unique identifier for this stack
            client_id: Client identifier for resource naming
            domain: Primary domain for the site
            template_variant: Gatsby template variant (react_business, content_blog, portfolio_showcase)
            node_version: Node.js version to use (default: 20 LTS)
            gatsby_version: Gatsby version to use (default: latest stable)
            enable_typescript: Whether to enable TypeScript support
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

        # Create Gatsby-optimized SSG configuration
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine="gatsby",  # React-based static site generator
            template_variant=template_variant,
            performance_tier="optimized",  # Gatsby provides good performance with React
            theme_id=theme_id,
            theme_config=theme_config or {}
        )

        # Initialize base SSG infrastructure (S3, CloudFront, Route53)
        super().__init__(scope, construct_id, ssg_config, **kwargs)

        # Store Gatsby-specific configuration
        self.template_variant = template_variant
        self.node_version = node_version
        self.gatsby_version = gatsby_version
        self.enable_typescript = enable_typescript

        # Set up Gatsby-specific features following comprehensive pattern
        self._setup_gatsby_environment()
        self._setup_react_ecosystem()
        self._setup_graphql_features()
        self._setup_plugin_ecosystem()
        self._setup_theme_integration()
        self._create_stack_parameters()
        self._create_stack_outputs()

    def _setup_gatsby_environment(self) -> None:
        """
        Configure Gatsby-specific build environment and variables.

        Sets up Node.js environment, Gatsby CLI, and React-specific
        configurations for optimal development experience.
        """

        # Get template variant configuration
        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # Core Gatsby environment variables
        gatsby_vars = {
            # Node.js and Gatsby configuration
            "NODE_VERSION": self.node_version,
            "GATSBY_VERSION": self.gatsby_version,
            "GATSBY_CLI_VERSION": "latest",
            "NODE_ENV": "production",

            # Gatsby build configuration
            "GATSBY_ACTIVE_ENV": "production",
            "GATSBY_CPU_COUNT": "2",  # Optimize for CodeBuild environment
            "GATSBY_TELEMETRY_DISABLED": "1",  # Disable telemetry in CI/CD

            # React and JavaScript configuration
            "ENABLE_TYPESCRIPT": str(self.enable_typescript).lower(),
            "REACT_APP_ENV": "production",

            # Performance and optimization
            "GATSBY_EXPERIMENTAL_PAGE_BUILD_ON_DATA_CHANGES": "true",
            "GATSBY_PARALLEL_SOURCING": "true",
            "GATSBY_EXPERIMENTAL_LAZY_IMAGES": "true",

            # Build optimization
            "GATSBY_BUILD_OPTIMIZATION": "production",
            "GATSBY_MINIFY": "true",
            "GATSBY_WEBPACK_PUBLICPATH": "/",

            # Site identification and metadata
            "SITE_TYPE": "react_business",
            "HOSTING_PLATFORM": "aws_s3_cloudfront",
            "BUILD_ENGINE": "gatsby_react",
            "FRAMEWORK": "react",
        }

        # Add template variant-specific environment variables
        gatsby_vars.update({
            "TEMPLATE_VARIANT": self.template_variant,
            "GATSBY_STARTER": variant_config["gatsby_starter"],
            "TEMPLATE_FEATURES": ",".join(variant_config["features"]),
            "TARGET_AUDIENCE": variant_config["target_audience"],
            "IDEAL_USE_CASE": variant_config["ideal_for"]
        })

        # Add plugin configuration
        plugin_list = ",".join(variant_config["plugins"])
        gatsby_vars["GATSBY_PLUGINS"] = plugin_list

        # Add theme-specific environment variables if theme is configured
        theme_info = self.ssg_config.get_theme_info()
        if theme_info:
            gatsby_vars.update(theme_info["theme_env_vars"])
            gatsby_vars.update({
                "THEME_ID": theme_info["theme"].id,
                "THEME_SOURCE": theme_info["source"],
                "THEME_GATSBY_COMPATIBLE": str(theme_info.get("gatsby_compatible", True)).lower()
            })

        self.add_environment_variables(gatsby_vars)

    def _setup_react_ecosystem(self) -> None:
        """
        Configure React ecosystem features and development tools.

        React developers expect modern tooling, component patterns,
        and development workflows familiar from React applications.
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # React ecosystem environment variables
        react_vars = {
            # React configuration
            "REACT_APP_SITE_NAME": f"{self.ssg_config.client_id}-site",
            "REACT_APP_SITE_DOMAIN": self.ssg_config.domain,
            "REACT_APP_BUILD_DATE": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",

            # Development tools
            "GENERATE_SOURCEMAP": "false",  # Disable in production builds
            "EXTEND_ESLINT": "true",  # Use project ESLint config
            "DISABLE_ESLINT_PLUGIN": "false",  # Keep ESLint for code quality

            # Component and styling systems
            "GATSBY_STYLED_COMPONENTS": "true",  # Enable styled-components
            "GATSBY_EMOTION": "false",  # Use styled-components instead
            "GATSBY_CSS_MODULES": "true",  # Enable CSS modules

            # Modern JavaScript features
            "GATSBY_BABEL_PRESET": "gatsby",  # Use Gatsby's Babel preset
            "GATSBY_WEBPACK_RESOLVE": "modern",  # Modern module resolution
            "GATSBY_POLYFILL_IO": "false",  # Don't include automatic polyfills

            # Performance monitoring
            "GATSBY_BUNDLE_ANALYZER": "false",  # Disable in production
            "GATSBY_PERF_MEASURING": "true",  # Enable performance measuring
        }

        # TypeScript configuration if enabled
        if self.enable_typescript:
            react_vars.update({
                "GATSBY_TYPESCRIPT": "true",
                "TYPESCRIPT_STRICT_MODE": "true",
                "GATSBY_TYPE_GEN": "true",  # Generate GraphQL types
            })

        # Add variant-specific React features
        if "accessibility" in variant_config["features"]:
            react_vars.update({
                "GATSBY_A11Y_TESTING": "true",
                "REACT_APP_A11Y_ENABLED": "true"
            })

        if "responsive_design" in variant_config["features"]:
            react_vars.update({
                "GATSBY_RESPONSIVE_IMAGES": "true",
                "GATSBY_BREAKPOINTS": "mobile,tablet,desktop"
            })

        self.add_environment_variables(react_vars)

    def _setup_graphql_features(self) -> None:
        """
        Configure GraphQL data layer and content querying features.

        GraphQL is one of Gatsby's key differentiators, providing
        powerful content querying and relationship management.
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # GraphQL configuration environment variables
        graphql_vars = {
            # Core GraphQL settings
            "GATSBY_GRAPHQL_IDE": "false",  # Disable GraphQL IDE in production
            "GATSBY_GRAPHQL_PLAYGROUND": "false",  # Disable playground in production
            "GATSBY_EXPERIMENTAL_GRAPHQL_TYPEGEN": "true",  # Enable type generation

            # Data layer configuration
            "GATSBY_DATA_SCHEMA": "auto_infer",  # Auto-infer GraphQL schema
            "GATSBY_SCHEMA_SNAPSHOT": "true",  # Enable schema snapshots
            "GATSBY_SCHEMA_CUSTOMIZATION": "enabled",  # Allow schema customization

            # Query optimization
            "GATSBY_QUERY_ON_DEMAND": "true",  # Enable on-demand query running
            "GATSBY_LAZY_IMAGES_QUERY": "true",  # Lazy load images via GraphQL
            "GATSBY_GRAPHQL_QUERY_CACHE": "true",  # Cache GraphQL queries

            # Content sourcing
            "GATSBY_CONTENT_SOURCING": "filesystem",  # Primary content source
            "GATSBY_MARKDOWN_SOURCING": "true",  # Enable markdown sourcing
            "GATSBY_IMAGE_SOURCING": "filesystem",  # Image sourcing method
        }

        # Add content-specific GraphQL features
        if "content_relationships" in variant_config["features"]:
            graphql_vars.update({
                "GATSBY_CONTENT_RELATIONSHIPS": "enabled",
                "GATSBY_FOREIGN_KEY_RESOLUTION": "true",
                "GATSBY_CONTENT_TAXONOMY": "enabled"
            })

        if "search" in variant_config["features"]:
            graphql_vars.update({
                "GATSBY_SEARCH_INDEX": "graphql",
                "GATSBY_SEARCH_FIELDS": "title,content,excerpt",
                "GATSBY_FLEXSEARCH": "enabled"
            })

        self.add_environment_variables(graphql_vars)

    def _setup_plugin_ecosystem(self) -> None:
        """
        Configure Gatsby plugin ecosystem and integrations.

        Gatsby's rich plugin ecosystem is a major advantage - configure
        plugins based on template variant and business requirements.
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        # Plugin ecosystem environment variables
        plugin_vars = {
            # Core plugin configuration
            "GATSBY_PLUGIN_MANAGEMENT": "auto",
            "GATSBY_PLUGIN_CACHE": "enabled",
            "GATSBY_PLUGIN_VALIDATION": "strict",

            # Image processing plugins
            "GATSBY_SHARP_PROCESSING": "true",
            "GATSBY_IMAGE_FORMATS": "webp,jpg,png",
            "GATSBY_IMAGE_QUALITY": "85",
            "GATSBY_IMAGE_PLACEHOLDER": "blurred",

            # SEO and analytics plugins
            "GATSBY_SEO_PLUGIN": "react-helmet",
            "GATSBY_SITEMAP_GENERATION": "automatic",
            "GATSBY_ROBOTS_TXT": "enabled",

            # Performance plugins
            "GATSBY_OFFLINE_PLUGIN": "false",  # Disable by default
            "GATSBY_MANIFEST_PLUGIN": "enabled",
            "GATSBY_CRITICAL_CSS": "enabled",

            # Development plugins
            "GATSBY_HOT_RELOAD": "enabled",
            "GATSBY_FAST_DEV": "true",
            "GATSBY_DEV_SSR": "false",  # Disable SSR in development
        }

        # Configure plugins based on template variant
        if self.template_variant == "content_blog":
            plugin_vars.update({
                "GATSBY_REMARK_PROCESSING": "enabled",
                "GATSBY_REMARK_PLUGINS": "prismjs,autolink-headers,responsive-iframe",
                "GATSBY_FEED_GENERATION": "enabled",
                "GATSBY_TYPOGRAPHY": "enabled"
            })

        elif self.template_variant == "portfolio_showcase":
            plugin_vars.update({
                "GATSBY_IMAGE_GALLERY": "enabled",
                "GATSBY_LIGHTBOX": "enabled",
                "GATSBY_LAZY_LOADING": "aggressive",
                "GATSBY_STYLED_COMPONENTS": "enabled"
            })

        elif self.template_variant == "react_business":
            plugin_vars.update({
                "GATSBY_GOOGLE_ANALYTICS": "enabled",
                "GATSBY_CONTACT_FORMS": "netlify",
                "GATSBY_MANIFEST_ICON": "auto_generate",
                "GATSBY_ACCESSIBILITY": "enabled"
            })

        self.add_environment_variables(plugin_vars)

        # Grant permissions for plugin functionality
        self._grant_plugin_permissions()

    def _grant_plugin_permissions(self) -> None:
        """
        Grant IAM permissions required for Gatsby plugin functionality.

        Some Gatsby plugins require AWS service access for advanced features
        like image processing, analytics, and deployment optimizations.
        """

        # CloudWatch access for analytics and monitoring plugins
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

        # S3 access for image processing and asset optimization
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

        # Parameter Store access for plugin configuration
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters"
                ],
                resources=[
                    f"arn:aws:ssm:*:*:parameter/{self.ssg_config.client_id}/*",
                    f"arn:aws:ssm:*:*:parameter/gatsby/*"
                ]
            )
        )

    def _setup_theme_integration(self) -> None:
        """
        Configure Gatsby theme integration and customization.

        Gatsby themes provide powerful customization capabilities
        while maintaining component-based architecture.
        """

        theme_info = self.ssg_config.get_theme_info()
        if not theme_info:
            return

        # Gatsby theme environment variables
        theme_vars = {
            "GATSBY_THEME_INSTALLATION": "npm_package",  # Gatsby's preferred method
            "GATSBY_THEME_CUSTOMIZATION": "component_shadowing",  # Gatsby's theme system
            "GATSBY_THEME_CONFIG": "gatsby-config.js",  # Configuration method
        }

        # Add theme customization variables
        if self.ssg_config.theme_config:
            for key, value in self.ssg_config.theme_config.items():
                theme_vars[f"GATSBY_THEME_{key.upper()}"] = str(value)

        self.add_environment_variables(theme_vars)

    def _create_stack_parameters(self) -> None:
        """
        Create CDK parameters for client-specific Gatsby configuration.

        React developers appreciate fine-grained control over their
        build environment and deployment configuration.
        """

        # Node.js version parameter
        self.node_version_parameter = CfnParameter(
            self,
            "NodeVersion",
            type="String",
            description="Node.js version for Gatsby builds",
            default=self.node_version,
            allowed_values=["18", "20", "21"]
        )

        # Gatsby version parameter
        self.gatsby_version_parameter = CfnParameter(
            self,
            "GatsbyVersion",
            type="String",
            description="Gatsby version to use",
            default=self.gatsby_version,
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
            description="Gatsby template variant to use",
            default=self.template_variant,
            allowed_values=list(self.SUPPORTED_TEMPLATE_VARIANTS.keys())
        )

        # Build optimization parameter
        self.build_optimization_parameter = CfnParameter(
            self,
            "BuildOptimization",
            type="String",
            description="Build optimization strategy",
            default="production",
            allowed_values=["development", "production", "performance"]
        )

    def _create_stack_outputs(self) -> None:
        """
        Create CDK outputs for client reference and React development integration.

        React developers need access to build information and AWS resources
        for local development and CI/CD integration.
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
            description="S3 bucket containing Gatsby-generated site content",
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

        # CodeBuild project for development integration
        CfnOutput(
            self,
            "BuildProjectName",
            value=self.build_project.project_name,
            description="CodeBuild project for Gatsby builds and React development",
            export_name=f"{self.stack_name}-BuildProject"
        )

        # Gatsby-specific outputs
        CfnOutput(
            self,
            "GatsbyVersion",
            value=self.gatsby_version,
            description="Gatsby version configured for this stack",
            export_name=f"{self.stack_name}-GatsbyVersion"
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
            "TypeScriptEnabled",
            value=str(self.enable_typescript).lower(),
            description="TypeScript support enabled",
            export_name=f"{self.stack_name}-TypeScript"
        )

        # GraphQL development endpoint (development only)
        CfnOutput(
            self,
            "GraphQLEndpoint",
            value="Available during 'gatsby develop' locally",
            description="GraphQL endpoint for development queries",
            export_name=f"{self.stack_name}-GraphQL"
        )

    def get_client_setup_instructions(self) -> Dict[str, Any]:
        """
        Generate comprehensive setup instructions for React developers.

        Gatsby users are React developers who appreciate detailed technical
        instructions and modern development workflow guidance.

        Returns:
            Dict containing complete Gatsby React development setup instructions
        """

        variant_config = self.SUPPORTED_TEMPLATE_VARIANTS[self.template_variant]

        instructions = {
            "stack_type": "Gatsby Template Stack",
            "management_model": "React Developer (⚛️)",
            "monthly_cost": "$85-110",
            "framework": "React + GraphQL",

            "gatsby_configuration": {
                "gatsby_version": self.gatsby_version,
                "node_version": self.node_version,
                "typescript_enabled": self.enable_typescript,
                "starter": variant_config["gatsby_starter"],
                "template_variant": self.template_variant,
                "plugins": variant_config["plugins"]
            },

            "local_development": {
                "prerequisites": [
                    f"Node.js {self.node_version} or later",
                    "npm or yarn package manager",
                    "Git for version control",
                    "Code editor with React/GraphQL support (VS Code recommended)"
                ],
                "quick_start": [
                    "# Install Gatsby CLI globally",
                    "npm install -g gatsby-cli",
                    "",
                    "# Create new Gatsby site",
                    f"gatsby new my-site {variant_config['gatsby_starter']}",
                    "cd my-site",
                    "",
                    "# Start development server",
                    "gatsby develop",
                    "# Site available at http://localhost:8000",
                    "# GraphQL explorer at http://localhost:8000/___graphql"
                ],
                "development_workflow": [
                    "gatsby develop --host 0.0.0.0  # Allow external connections",
                    "gatsby clean  # Clear cache if issues occur",
                    "gatsby build  # Production build for testing"
                ]
            },

            "react_development": {
                "component_structure": [
                    "src/components/  # Reusable React components",
                    "src/pages/       # Page components (auto-routed)",
                    "src/templates/   # Template components for dynamic pages",
                    "src/hooks/       # Custom React hooks"
                ],
                "styling_options": [
                    "CSS Modules (recommended for component isolation)",
                    "Styled Components (CSS-in-JS solution)",
                    "SCSS/Sass (with gatsby-plugin-sass)",
                    "Emotion (alternative CSS-in-JS)"
                ],
                "state_management": [
                    "React Context for global state",
                    "Local component state with useState/useReducer",
                    "GraphQL for data management (built-in)",
                    "Third-party: Redux, Zustand (if needed)"
                ]
            },

            "graphql_data_layer": {
                "query_examples": [
                    "# Page queries (in page components)",
                    "export const query = graphql`",
                    "  query HomePage {",
                    "    site { siteMetadata { title } }",
                    "  }",
                    "`",
                    "",
                    "# Static queries (in components)",
                    "const data = useStaticQuery(graphql`",
                    "  query HeaderQuery {",
                    "    site { siteMetadata { title } }",
                    "  }",
                    "`)"
                ],
                "data_sources": [
                    "Markdown files (gatsby-transformer-remark)",
                    "JSON/YAML data files",
                    "Images (gatsby-plugin-sharp)",
                    "External APIs (source plugins)",
                    "Headless CMS integration (available)"
                ],
                "development_tools": [
                    "GraphQL explorer: http://localhost:8000/___graphql",
                    "GraphQL type generation (if TypeScript enabled)",
                    "Query debugging and performance analysis"
                ]
            },

            "plugin_ecosystem": {
                "essential_plugins": variant_config["plugins"],
                "additional_plugins": [
                    "gatsby-plugin-google-analytics - Analytics integration",
                    "gatsby-plugin-sitemap - SEO sitemap generation",
                    "gatsby-plugin-robots-txt - Search engine directives",
                    "gatsby-plugin-pwa - Progressive Web App features",
                    "gatsby-plugin-netlify - Netlify deployment optimization"
                ],
                "plugin_management": [
                    "Install: npm install gatsby-plugin-name",
                    "Configure: Add to gatsby-config.js plugins array",
                    "Documentation: https://www.gatsbyjs.com/plugins/"
                ]
            },

            "deployment_workflow": {
                "automatic": "Push to main branch triggers automatic Gatsby build and deployment",
                "manual": f"Trigger build manually via AWS CodeBuild: {self.build_project.project_name}",
                "local_preview": "Use 'gatsby build && gatsby serve' for production preview",
                "build_time": "5-15 minutes depending on content volume and plugins",
                "cache_strategy": "Gatsby's built-in caching optimizes rebuild times"
            },

            "performance_optimization": {
                "image_optimization": "gatsby-plugin-image provides automatic WebP conversion and lazy loading",
                "code_splitting": "Automatic route-based code splitting for optimal loading",
                "prefetching": "Gatsby prefetches resources for faster navigation",
                "critical_css": "Inline critical CSS for improved first paint",
                "bundle_analysis": "gatsby-plugin-webpack-bundle-analyser-v2 for bundle optimization"
            },

            "template_features": {
                "included_features": variant_config["features"],
                "target_audience": variant_config["target_audience"],
                "ideal_for": variant_config["ideal_for"],
                "customization": "Full React component customization and styling flexibility"
            },

            "typescript_support": {
                "enabled": self.enable_typescript,
                "configuration": "Automatic TypeScript support with zero configuration" if self.enable_typescript else "Enable TypeScript with gatsby-plugin-typescript",
                "graphql_types": "Automatic GraphQL type generation for type-safe queries" if self.enable_typescript else "Available when TypeScript is enabled",
                "component_types": "Full React component type checking and IntelliSense"
            },

            "aws_integration": {
                "content_bucket": self.content_bucket.bucket_name,
                "distribution_id": self.distribution.distribution_id,
                "build_project": self.build_project.project_name,
                "primary_domain": self.ssg_config.domain,
                "cache_invalidation": "Automatic cache invalidation after each successful build"
            },

            "development_tools": {
                "hot_reload": "Fast Refresh for instant component updates during development",
                "error_overlay": "Detailed error messages with stack traces in development",
                "graphql_explorer": "Built-in GraphQL query explorer and documentation",
                "build_analysis": "Build performance metrics and bundle size analysis",
                "debugging": "React DevTools and Gatsby development tools support"
            }
        }

        return instructions

    @property
    def stack_cost_breakdown(self) -> Dict[str, str]:
        """
        Provide detailed cost breakdown for React developers.

        Gatsby builds are more resource-intensive than simple SSGs but
        provide significant value through React ecosystem integration.

        Returns:
            Dict with detailed AWS cost breakdown and React-specific value analysis
        """

        return {
            "setup_cost": "$1,200-2,400 (one-time setup with React ecosystem configuration)",
            "monthly_breakdown": {
                "s3_storage": "$2-12/month (React build artifacts require more storage)",
                "cloudfront": "$3-20/month (optimized for React SPA performance)",
                "route53": "$0.50/month (hosted zone for custom domain)",
                "codebuild": "$5-15/month (React builds require more compute time)",
                "certificate_manager": "$0/month (free SSL certificates)",
                "monitoring": "$2-5/month (CloudWatch metrics and build logs)"
            },
            "total_monthly": "$85-110/month (includes professional React development support)",

            "react_development_value": {
                "familiar_workflow": "Leverage existing React team skills and development patterns",
                "component_reusability": "Build design systems and reusable component libraries",
                "graphql_benefits": "Powerful data layer reduces custom API development time",
                "plugin_ecosystem": "Rich plugin ecosystem reduces custom development costs",
                "typescript_support": "Optional TypeScript for enterprise-grade type safety"
            },

            "cost_optimization_strategies": {
                "build_optimization": "Gatsby's incremental builds reduce CodeBuild costs over time",
                "image_optimization": "Built-in image processing reduces manual optimization work",
                "plugin_efficiency": "Use established plugins vs custom development (60-80% time savings)",
                "graphql_caching": "Intelligent GraphQL caching reduces build times and costs",
                "component_caching": "React component caching improves build performance"
            },

            "business_impact_analysis": {
                "development_velocity": "React familiarity increases team productivity by 40-60%",
                "maintenance_efficiency": "Component architecture reduces long-term maintenance costs",
                "scalability_foundation": "Gatsby provides foundation for future React application growth",
                "seo_performance": "Built-in SEO optimizations improve search visibility and conversion",
                "user_experience": "React SPA experience improves engagement and retention"
            },

            "comparison_with_alternatives": {
                "vs_create_react_app": "Static generation provides better SEO and performance",
                "vs_next_js": "Simpler deployment model with better static optimization",
                "vs_pure_ssg": "React ecosystem benefits justify 20-30% higher costs",
                "vs_custom_react": "50-70% lower development time with Gatsby framework"
            },

            "scaling_economics": {
                "small_business_sites": "$85/month for React business sites with professional support",
                "content_heavy_sites": "$95/month for blogs and content platforms with GraphQL",
                "portfolio_showcases": "$110/month for creative portfolios with advanced image processing",
                "enterprise_foundation": "Gatsby provides foundation for future React application growth"
            },

            "upgrade_pathways": {
                "headless_cms_integration": "Add headless CMS for $180-220/month total",
                "ecommerce_integration": "Add React-based e-commerce for $200-300/month total",
                "full_stack_react": "Migrate to Next.js for server-side features ($150-250/month)",
                "custom_react_app": "Graduate to full React application development ($500+/month)"
            },

            "roi_justification": {
                "react_skill_leverage": "Utilize existing React team investment and expertise",
                "development_speed": "30-50% faster development vs learning new SSG",
                "future_proofing": "Foundation for React application growth and scaling",
                "ecosystem_benefits": "Access to entire React ecosystem and community resources"
            }
        }

    def get_react_best_practices(self) -> Dict[str, Any]:
        """
        Provide React and Gatsby-specific best practices and optimization guidelines.

        Returns:
            Dict containing React development patterns and Gatsby optimization strategies
        """

        return {
            "component_architecture": {
                "component_organization": "Organize components by feature or domain, not technical layers",
                "component_composition": "Favor composition over inheritance for flexible component design",
                "prop_types_validation": "Use TypeScript or PropTypes for component interface validation",
                "component_testing": "Write unit tests for components using React Testing Library"
            },

            "graphql_optimization": {
                "query_optimization": "Use GraphQL fragments to avoid query duplication",
                "static_vs_page_queries": "Use page queries for page-level data, static queries for components",
                "query_performance": "Optimize GraphQL queries for minimal data fetching",
                "schema_customization": "Customize GraphQL schema for better type safety and performance"
            },

            "performance_optimization": {
                "image_optimization": "Use gatsby-plugin-image for automatic image optimization",
                "code_splitting": "Leverage Gatsby's automatic code splitting and lazy loading",
                "prefetching_strategy": "Configure link prefetching for optimal navigation performance",
                "bundle_optimization": "Analyze and optimize JavaScript bundle size regularly"
            },

            "development_workflow": {
                "hot_reload_usage": "Take advantage of Fast Refresh for efficient development",
                "graphql_explorer": "Use GraphQL explorer for query development and debugging",
                "build_optimization": "Use gatsby clean when experiencing cache-related issues",
                "development_vs_production": "Test production builds locally before deployment"
            },

            "seo_and_accessibility": {
                "react_helmet_usage": "Use React Helmet for dynamic meta tag management",
                "accessibility_testing": "Implement accessibility testing in your React components",
                "semantic_html": "Use semantic HTML elements in your React components",
                "structured_data": "Implement JSON-LD structured data for better SEO"
            }
        }