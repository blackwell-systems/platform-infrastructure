"""
PlatformStackFactory - Unified Stack Creation and Management System

This unified factory consolidates SSG, CMS, and E-commerce stack creation into a single
intelligent interface, resolving the composed stack ownership crisis and providing
complete business model coverage.

ARCHITECTURAL TRANSFORMATION:
- Before: Separate factories (SSGStackFactory, CMSStackFactory, EcommerceStackFactory)
- After: Single unified factory with intelligent cross-domain orchestration

BUSINESS IMPACT:
- Complete business model coverage (42/42 stack combinations)
- Unified API surface reduces development complexity

SUPPORTED STACK TYPES:
- SSG Template Business Services: Hugo, Gatsby, Next.js, Nuxt template stacks
- Foundation SSG Stacks: Marketing, Developer, Modern Performance stacks
- CMS Tier Services: Decap, Tina, Sanity, Contentful with flexible SSG choice
- E-commerce Tier Services: Snipcart, Foxy, Shopify with flexible SSG choice
- Composed Stacks: CMS + E-commerce + SSG orchestration (SOLVES OWNERSHIP CRISIS)

USAGE EXAMPLES:
- Simple business service: create_stack("hugo_template", ...)
- CMS tier service: create_stack("sanity_cms_tier", ssg_engine="astro", ...)
- E-commerce service: create_stack("snipcart_ecommerce", ssg_engine="hugo", ...)
- Composed service: create_composed_stack("sanity", "snipcart", "astro", ...)
"""

from typing import Dict, List, Any, Optional, Type, Union, Callable
from constructs import Construct
import importlib.util
import sys
import os
from pathlib import Path
import logging

# Import centralized enums for type safety
from models.component_enums import SSGEngine, CMSProvider, EcommerceProvider

# Import S3 Provider Registry from blackwell-core
try:
    from blackwell_core.registry import default_registry
    REGISTRY_AVAILABLE = True
except ImportError as e:
    default_registry = None
    REGISTRY_AVAILABLE = False

# Establish base directory for portable imports
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Internal logging hook for CLI integration
_LOGGER: Optional[logging.Logger] = None

def set_logger(logger: logging.Logger) -> None:
    """Set the internal logger for CLI integration and debugging."""
    global _LOGGER
    _LOGGER = logger

def _log(level: str, message: str, **kwargs) -> None:
    """Internal logging with fallback to print for CLI integration."""
    if _LOGGER:
        getattr(_LOGGER, level.lower())(message, **kwargs)
    elif level.upper() == 'ERROR':
        print(f"ERROR: {message}", file=sys.stderr)

def _import_from_hyphenated_path(module_path: str, class_name: str):
    """Import class from module path that may contain hyphens with portable BASE_DIR handling."""
    try:
        # Convert module path to absolute file path using BASE_DIR
        file_path = BASE_DIR / f"{module_path.replace('.', '/')}.py"

        # Validate file exists
        if not file_path.exists():
            raise ImportError(f"Module file not found: {file_path}")

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(class_name, str(file_path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name)
        else:
            raise ImportError(f"Could not load spec for {class_name} from {file_path}")
    except Exception as e:
        _log('error', f"Failed to import {class_name} from {module_path}: {e}")
        raise ImportError(f"Could not import {class_name} from {module_path}: {e}")

# Lazy loading registry for performance optimization
_STACK_CLASS_CACHE: Dict[str, Type] = {}

def _lazy_import_stack_class(stack_type: str, import_config: Dict[str, Any]) -> Type:
    """Lazy import stack class with caching for CLI performance optimization."""
    if stack_type in _STACK_CLASS_CACHE:
        return _STACK_CLASS_CACHE[stack_type]

    try:
        _log('debug', f"Lazy loading stack class: {stack_type}")

        if import_config["import_type"] == "hyphenated":
            stack_class = _import_from_hyphenated_path(
                import_config["module_path"],
                import_config["class_name"]
            )
        else:  # standard import
            module = importlib.import_module(import_config["module_path"])
            stack_class = getattr(module, import_config["class_name"])

        _STACK_CLASS_CACHE[stack_type] = stack_class
        _log('debug', f"Successfully loaded stack class: {stack_type}")
        return stack_class

    except Exception as e:
        _log('error', f"Failed to lazy load {stack_type}: {e}")
        raise ImportError(f"Could not lazy load {stack_type}: {e}")

# Import base classes and static site config (these are needed immediately)
from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.ssg import StaticSiteConfig


class PlatformStackFactory:
    """
    Unified factory for creating all platform stack types.

    This factory resolves the composed stack ownership crisis and provides
    intelligent stack selection, cost estimation, and recommendation engine
    to match clients with optimal configurations across all service tiers.
    """

    # LAZY LOADING STACK IMPORT CONFIGURATION - Defers imports until needed
    _STACK_IMPORT_CONFIG: Dict[str, Dict[str, Any]] = {
        # === SSG TEMPLATE BUSINESS SERVICE STACKS (DEVELOPER ECOSYSTEM COVERAGE) ===
        "hugo_template": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/hugo_template_stack",
            "class_name": "HugoTemplateStack"
        },
        "gatsby_template": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/gatsby_template_stack",
            "class_name": "GatsbyTemplateStack"
        },
        "nextjs_template": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/nextjs_template_stack",
            "class_name": "NextJSTemplateStack"
        },
        "nuxt_template": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/nuxt_template_stack",
            "class_name": "NuxtTemplateStack"
        },

        # === FOUNDATION SSG STACKS (PROVEN BUSINESS SERVICES) ===
        "marketing": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/eleventy_marketing_stack",
            "class_name": "EleventyMarketingStack"
        },
        "developer": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/jekyll_github_stack",
            "class_name": "JekyllGitHubStack"
        },
        "modern_performance": {
            "import_type": "hyphenated",
            "module_path": "stacks/hosted-only/tier1/astro_template_basic_stack",
            "class_name": "AstroTemplateBasicStack"
        },

        # === CMS TIER STACKS (CONTENT MANAGEMENT WITH SSG FLEXIBILITY) ===
        "decap_cms_tier": {
            "import_type": "standard",
            "module_path": "stacks.cms.decap_cms_tier_stack",
            "class_name": "DecapCMSTierStack"
        },
        "tina_cms_tier": {
            "import_type": "standard",
            "module_path": "stacks.cms.tina_cms_tier_stack",
            "class_name": "TinaCMSTierStack"
        },
        "sanity_cms_tier": {
            "import_type": "standard",
            "module_path": "stacks.cms.sanity_cms_tier_stack",
            "class_name": "SanityCMSTierStack"
        },
        "contentful_cms_tier": {
            "import_type": "standard",
            "module_path": "stacks.cms.contentful_cms_stack",
            "class_name": "ContentfulCMSStack"
        },

        # === E-COMMERCE TIER STACKS (E-COMMERCE WITH SSG FLEXIBILITY) ===
        "snipcart_ecommerce": {
            "import_type": "standard",
            "module_path": "stacks.ecommerce.snipcart_ecommerce_stack",
            "class_name": "SnipcartEcommerceStack"
        },
        "foxy_ecommerce": {
            "import_type": "standard",
            "module_path": "stacks.ecommerce.foxy_ecommerce_stack",
            "class_name": "FoxyEcommerceStack"
        },
        "shopify_basic_ecommerce": {
            "import_type": "standard",
            "module_path": "stacks.ecommerce.shopify_basic_ecommerce_stack",
            "class_name": "ShopifyBasicEcommerceStack"
        },

        # === COMPOSED STACKS (CROSS-DOMAIN ORCHESTRATION - SOLVES OWNERSHIP CRISIS) ===
        "cms_ecommerce_composed": {
            "import_type": "standard",
            "module_path": "stacks.composed.cms_ecommerce_composed_stack",
            "class_name": "CMSEcommerceComposedStack"
        },
    }

    @classmethod
    def get_stack_class(cls, stack_type: str) -> Type[BaseSSGStack]:
        """
        Get stack class with lazy loading for CLI performance optimization.

        This method loads stack classes on-demand, improving startup time for
        CLI operations that only need metadata access.

        Args:
            stack_type: The stack type to load

        Returns:
            The stack class for the given type

        Raises:
            ValueError: If stack_type is not supported
        """
        if stack_type not in cls._STACK_IMPORT_CONFIG:
            available_types = list(cls._STACK_IMPORT_CONFIG.keys())
            raise ValueError(
                f"Unsupported stack type '{stack_type}'. "
                f"Available types: {available_types}"
            )

        import_config = cls._STACK_IMPORT_CONFIG[stack_type]
        return _lazy_import_stack_class(stack_type, import_config)

    @classmethod
    def get_available_stack_types(cls) -> List[str]:
        """Get list of all available stack types from import configuration."""
        return list(cls._STACK_IMPORT_CONFIG.keys())

    # UNIFIED STACK METADATA - Complete business tier information
    STACK_METADATA: Dict[str, Dict[str, Any]] = {
        # === SSG TEMPLATE BUSINESS SERVICE METADATA ===
        "hugo_template": {
            "tier_name": "Hugo Template - Performance-Critical Technical Teams",
            "category": "ssg_template_business_service",
            "target_audience": ["technical_teams", "performance_critical_sites", "documentation_sites", "enterprise_technical"],
            "best_for": "Ultra-fast static sites with complex content relationships and technical documentation",
            "complexity_level": "medium_to_high",
            "technical_requirements": ["go_templating", "markdown_expertise", "build_pipeline_knowledge"],
            "ssg_engine": "hugo",
            "template_variants": ["documentation", "performance_blog", "technical_portfolio"],
            "key_features": ["ultra_fast_builds", "technical_documentation", "multi_language", "complex_taxonomies", "performance_optimization"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "maximum",
            "use_cases": ["high_traffic_sites", "documentation_portals", "technical_blogs", "enterprise_websites"]
        },
        "gatsby_template": {
            "tier_name": "Gatsby Template - React Ecosystem with GraphQL",
            "category": "ssg_template_business_service",
            "target_audience": ["react_developers", "component_driven_teams", "content_heavy_sites", "javascript_teams"],
            "best_for": "React-based static sites with GraphQL data layer and component architecture",
            "complexity_level": "medium_to_high",
            "technical_requirements": ["react_knowledge", "graphql_understanding", "javascript_es6", "component_architecture"],
            "ssg_engine": "gatsby",
            "template_variants": ["react_business", "content_blog", "portfolio_showcase"],
            "key_features": ["react_components", "graphql_data_layer", "plugin_ecosystem", "image_optimization", "component_reusability"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "use_cases": ["content_heavy_websites", "portfolio_sites", "business_blogs", "component_showcases"]
        },
        "nextjs_template": {
            "tier_name": "Next.js Template - Enterprise Full-Stack React Foundation",
            "category": "ssg_template_business_service",
            "target_audience": ["fullstack_developers", "enterprise_teams", "business_applications", "scalable_architecture"],
            "best_for": "Enterprise-ready React applications with static export and full-stack growth path",
            "complexity_level": "high",
            "technical_requirements": ["react_advanced", "typescript_proficiency", "next_js_concepts", "full_stack_architecture"],
            "ssg_engine": "nextjs",
            "template_variants": ["business_app", "marketing_site", "saas_landing"],
            "key_features": ["enterprise_patterns", "typescript_first", "api_routes_ready", "static_export", "full_stack_growth"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "enterprise",
            "use_cases": ["enterprise_applications", "saas_platforms", "business_websites", "scalable_web_apps"]
        },
        "nuxt_template": {
            "tier_name": "Nuxt Template - Vue Ecosystem with Modern Patterns",
            "category": "ssg_template_business_service",
            "target_audience": ["vue_developers", "composition_api_teams", "progressive_applications", "vue_ecosystem"],
            "best_for": "Modern Vue 3 applications with Composition API and progressive enhancement features",
            "complexity_level": "medium",
            "technical_requirements": ["vue_3_knowledge", "composition_api", "nuxt_framework", "modern_javascript"],
            "ssg_engine": "nuxt",
            "template_variants": ["vue_business", "content_site", "vue_portfolio"],
            "key_features": ["vue_3_composition_api", "progressive_enhancement", "pinia_state_management", "modern_patterns", "vue_ecosystem"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "use_cases": ["progressive_web_apps", "vue_business_sites", "modern_portfolios", "spa_websites"]
        },

        # === FOUNDATION SSG STACK METADATA ===
        "marketing": {
            "tier_name": "Marketing-Optimized Static Sites",
            "category": "foundation_ssg_service",
            "target_audience": ["small_businesses", "marketing_agencies", "content_creators", "professionals"],
            "best_for": "Content-driven marketing sites with fast loading and SEO optimization",
            "complexity_level": "low_to_medium",
            "technical_requirements": ["basic_html_css", "content_management", "seo_understanding"],
            "ssg_engine": "eleventy",
            "template_variants": ["business_modern", "corporate_clean", "marketing_focused"],
            "key_features": ["fast_builds", "seo_optimized", "content_focused", "developer_managed"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "use_cases": ["business_websites", "marketing_campaigns", "corporate_sites", "professional_portfolios"]
        },
        "developer": {
            "tier_name": "Developer-Focused Git Workflow",
            "category": "foundation_ssg_service",
            "target_audience": ["developers", "technical_writers", "open_source_projects", "documentation_sites"],
            "best_for": "Technical sites with Git-based workflows and GitHub Pages compatibility",
            "complexity_level": "medium",
            "technical_requirements": ["git_proficiency", "ruby_basics", "liquid_templating", "github_workflow"],
            "ssg_engine": "jekyll",
            "template_variants": ["technical_blog", "documentation", "simple_blog"],
            "key_features": ["github_pages_compatible", "git_workflow", "theme_system", "dual_hosting"],
            "hosting_pattern": "github_compatible",
            "performance_tier": "basic",
            "use_cases": ["technical_blogs", "project_documentation", "personal_sites", "open_source_projects"]
        },
        "modern_performance": {
            "tier_name": "Modern High-Performance Interactive",
            "category": "foundation_ssg_service",
            "target_audience": ["modern_businesses", "agencies", "performance_critical_sites", "interactive_applications"],
            "best_for": "Modern sites requiring interactive features with optimal performance",
            "complexity_level": "medium_to_high",
            "technical_requirements": ["modern_javascript", "component_architecture", "build_tools", "performance_optimization"],
            "ssg_engine": "astro",
            "template_variants": ["modern_interactive", "component_islands", "performance_optimized"],
            "key_features": ["component_islands", "partial_hydration", "framework_agnostic", "performance_optimized"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium",
            "use_cases": ["interactive_websites", "modern_web_apps", "performance_critical_sites", "component_showcases"]
        },

        # === CMS TIER METADATA ===
        "decap_cms_tier": {
            "tier_name": "Decap CMS - Free Git-Based Content Management",
            "category": "cms_tier_service",
            "target_audience": ["technical_teams", "developer_focused_teams", "small_to_medium_content", "git_workflow_users"],
            "best_for": "Git-based content management with developer-friendly workflow and version control",
            "complexity_level": "low_to_medium",
            "technical_requirements": ["git_proficiency", "markdown_knowledge", "basic_yaml", "github_workflow"],
            "cms_provider": "decap",
            "cms_type": "git_based",
            "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
            "template_variants": ["git_cms_basic", "markdown_focused", "developer_friendly"],
            "key_features": ["free_cms", "git_workflow", "markdown_editing", "github_oauth", "version_control", "no_vendor_lock_in"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "use_cases": ["developer_blogs", "technical_documentation", "small_business_sites", "version_controlled_content"]
        },
        "tina_cms_tier": {
            "tier_name": "Tina CMS - Visual Editing with Git Workflow",
            "category": "cms_tier_service",
            "target_audience": ["content_creators", "agencies", "visual_editing_preference", "collaboration_teams"],
            "best_for": "Visual content editing with git-based storage and real-time collaboration",
            "complexity_level": "medium",
            "technical_requirements": ["react_familiarity", "git_basics", "graphql_understanding", "modern_javascript"],
            "cms_provider": "tina",
            "cms_type": "hybrid",
            "ssg_engine_options": ["nextjs", "astro", "gatsby"],
            "template_variants": ["visual_editor", "react_based", "collaboration_focused"],
            "key_features": ["visual_editing", "real_time_preview", "git_workflow", "react_based", "graphql_api", "collaboration"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "use_cases": ["content_marketing", "agency_projects", "collaborative_editing", "visual_content_creation"]
        },
        "sanity_cms_tier": {
            "tier_name": "Sanity CMS - Structured Content with Real-Time APIs",
            "category": "cms_tier_service",
            "target_audience": ["professional_content_teams", "api_first_developers", "structured_content_needs", "enterprise_ready"],
            "best_for": "Professional structured content management with real-time APIs and advanced querying",
            "complexity_level": "medium_to_high",
            "technical_requirements": ["api_integration", "structured_content_modeling", "groq_query_language", "webhook_setup"],
            "cms_provider": "sanity",
            "cms_type": "api_based",
            "ssg_engine_options": ["nextjs", "astro", "gatsby", "eleventy"],
            "template_variants": ["structured_content", "api_driven", "professional_editorial"],
            "key_features": ["structured_content", "groq_querying", "real_time_apis", "content_validation", "advanced_media", "webhook_automation"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium",
            "use_cases": ["professional_publishing", "api_driven_sites", "structured_data_management", "real_time_content_sync"]
        },
        "contentful_cms_tier": {
            "tier_name": "Contentful CMS - Enterprise Content Management with Advanced Workflows",
            "category": "cms_tier_service",
            "target_audience": ["enterprise_content_teams", "large_organizations", "complex_workflows", "multi_brand_companies", "international_businesses"],
            "best_for": "Enterprise-grade content management with advanced workflows, team collaboration, and multi-language support",
            "complexity_level": "high",
            "technical_requirements": ["enterprise_api_integration", "workflow_management", "multi_language_setup", "advanced_permissions"],
            "cms_provider": "contentful",
            "cms_type": "api_based",
            "ssg_engine_options": ["gatsby", "astro", "nextjs", "nuxt"],
            "template_variants": ["enterprise_workflows", "multi_language", "team_collaboration"],
            "key_features": ["enterprise_workflows", "team_collaboration", "multi_language_support", "content_versioning", "scheduled_publishing", "advanced_permissions"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "enterprise",
            "use_cases": ["enterprise_publishing", "multi_brand_management", "international_content", "complex_editorial_workflows"]
        },

        # === E-COMMERCE TIER METADATA ===
        "snipcart_ecommerce": {
            "tier_name": "Snipcart E-commerce - Simple E-commerce Integration",
            "category": "ecommerce_tier_service",
            "target_audience": ["individuals", "small_businesses", "simple_stores", "quick_setup_needs"],
            "best_for": "Simple e-commerce integration with fast setup and minimal technical complexity",
            "complexity_level": "low_to_medium",
            "technical_requirements": ["basic_html_css", "javascript_basics", "payment_setup", "product_management"],
            "ecommerce_provider": "snipcart",
            "provider_type": "simple_integration",
            "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
            "template_variants": ["simple_store", "digital_products", "catalog_basic"],
            "key_features": ["simple_integration", "secure_checkout", "inventory_management", "basic_analytics"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "use_cases": ["small_online_stores", "digital_product_sales", "simple_catalogs", "quick_e_commerce_setup"]
        },
        "foxy_ecommerce": {
            "tier_name": "Foxy E-commerce - Advanced E-commerce Features",
            "category": "ecommerce_tier_service",
            "target_audience": ["small_businesses", "growing_companies", "subscription_services", "advanced_features_needs"],
            "best_for": "Advanced e-commerce features including subscriptions and complex pricing workflows",
            "complexity_level": "medium_to_high",
            "technical_requirements": ["api_integration", "webhook_setup", "subscription_management", "advanced_configuration"],
            "ecommerce_provider": "foxy",
            "provider_type": "advanced_platform",
            "ssg_engine_options": ["eleventy", "astro", "gatsby"],
            "template_variants": ["subscription_store", "advanced_catalog", "custom_checkout"],
            "key_features": ["subscription_management", "advanced_checkout", "webhook_automation", "complex_pricing"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium",
            "use_cases": ["subscription_businesses", "complex_product_catalogs", "advanced_checkout_flows", "recurring_billing"]
        },
        "shopify_basic_ecommerce": {
            "tier_name": "Shopify Basic - Performance E-commerce with Flexible SSG",
            "category": "ecommerce_tier_service",
            "target_audience": ["small_medium_stores", "performance_focused_brands", "agency_alternatives", "shopify_theme_upgrades"],
            "best_for": "High-performance e-commerce leveraging Shopify's platform with custom frontend flexibility",
            "complexity_level": "medium",
            "technical_requirements": ["shopify_storefront_api", "graphql_queries", "webhook_integration", "performance_optimization"],
            "ecommerce_provider": "shopify_basic",
            "provider_type": "hosted_platform",
            "ssg_engine_options": ["eleventy", "astro", "nextjs", "nuxt"],
            "template_variants": ["performance_optimized", "static_site_ecommerce", "agency_alternative"],
            "key_features": ["shopify_storefront_api", "real_time_sync", "webhook_automation", "performance_optimization"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium",
            "use_cases": ["performance_focused_stores", "custom_shopify_frontends", "headless_e_commerce", "high_traffic_stores"]
        },

        # === COMPOSED STACK METADATA (SOLVES OWNERSHIP CRISIS) ===
        "cms_ecommerce_composed": {
            "tier_name": "Composed CMS + E-commerce Stack",
            "category": "composed_service",
            "target_audience": ["content_driven_stores", "editorial_ecommerce", "complex_business_models", "integrated_publishing"],
            "best_for": "Sites requiring both professional content management and e-commerce capabilities with unified orchestration",
            "complexity_level": "high",
            "technical_requirements": ["multi_provider_integration", "event_driven_architecture", "cross_domain_orchestration", "unified_user_management"],
            "provider_combinations": "flexible", # CMS + E-commerce provider choice
            "ssg_engine_options": ["astro", "gatsby", "nextjs"],  # SSGs supporting both integrations
            "template_variants": ["content_store", "editorial_commerce", "magazine_shop"],
            "key_features": ["unified_content_commerce", "cross_domain_events", "shared_user_management", "integrated_analytics"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "enterprise",
            "use_cases": ["content_driven_e_commerce", "editorial_shopping", "magazine_stores", "integrated_publishing_platforms"]
        }
    }

    @classmethod
    def create_stack(
        cls,
        scope: Construct,
        client_id: str,
        domain: str,
        stack_type: str,
        ssg_engine: Optional[str] = None,
        **kwargs
    ) -> BaseSSGStack:
        """
        Create any platform stack type with unified API.

        This method provides single interface for all stack creation:
        1. Validates stack type exists in unified registry
        2. Handles SSG engine selection for flexible stacks
        3. Creates optimized stack configuration
        4. Returns configured stack instance

        Args:
            scope: CDK scope for stack creation
            client_id: Unique client identifier
            domain: Client domain name
            stack_type: Platform stack type (from STACK_REGISTRY)
            ssg_engine: Optional SSG engine for flexible stacks
            **kwargs: Additional stack-specific arguments

        Returns:
            Configured platform stack instance

        Raises:
            ValueError: If stack_type is invalid or SSG engine incompatible

        Examples:
            # SSG template business service
            hugo_stack = create_stack(scope, "client", "domain.com", "hugo_template")

            # CMS tier with SSG choice
            cms_stack = create_stack(scope, "client", "domain.com", "sanity_cms_tier", ssg_engine="astro")

            # E-commerce tier with SSG choice
            ecommerce_stack = create_stack(scope, "client", "domain.com", "snipcart_ecommerce", ssg_engine="hugo")
        """

        # Validate and get stack class with lazy loading
        _log('debug', f"Creating stack: {stack_type}")
        stack_class = cls.get_stack_class(stack_type)

        # Get stack metadata
        stack_metadata = cls.STACK_METADATA.get(stack_type, {})
        stack_category = stack_metadata.get("category", "unknown")

        # Handle SSG engine selection based on stack category
        if stack_category in ["cms_tier_service", "ecommerce_tier_service"]:
            # Flexible stacks require/support SSG engine choice
            if not ssg_engine:
                ssg_engine = cls._recommend_ssg_engine(stack_type, kwargs)

            # Validate SSG engine compatibility
            supported_engines = stack_metadata.get("ssg_engine_options", [])
            if supported_engines and ssg_engine not in supported_engines:
                raise ValueError(
                    f"SSG engine '{ssg_engine}' not supported by {stack_type}. "
                    f"Supported engines: {', '.join(supported_engines)}"
                )

        elif stack_category in ["ssg_template_business_service", "foundation_ssg_service"]:
            # Fixed stacks have predetermined SSG engine
            ssg_engine = stack_metadata.get("ssg_engine")

        # Generate construct ID
        construct_id = f"{client_id.title().replace('-', '')}-{stack_type.title().replace('_', '')}-Stack"

        # Set default template variant if not provided
        if 'template_variant' not in kwargs and 'template_variants' in stack_metadata:
            kwargs['template_variant'] = stack_metadata['template_variants'][0]

        # Create and return stack instance
        return stack_class(
            scope=scope,
            construct_id=construct_id,
            client_id=client_id,
            domain=domain,
            ssg_engine=ssg_engine,
            **kwargs
        )

    @classmethod
    def create_composed_stack(
        cls,
        scope: Construct,
        client_id: str,
        domain: str,
        cms_provider: str,
        ecommerce_provider: str,
        ssg_engine: str,
        **kwargs
    ) -> BaseSSGStack:
        """
        Create composed CMS + E-commerce stack with unified orchestration.

        SOLVES OWNERSHIP CRISIS: This method provides the natural home for
        cross-domain stacks that combine CMS and E-commerce capabilities.

        Args:
            scope: CDK scope for stack creation
            client_id: Unique client identifier
            domain: Client domain name
            cms_provider: CMS provider choice (decap, tina, sanity, contentful)
            ecommerce_provider: E-commerce provider choice (snipcart, foxy, shopify_basic)
            ssg_engine: SSG engine choice (must support both integrations)
            **kwargs: Additional configuration options

        Returns:
            Configured composed stack instance

        Raises:
            ValueError: If provider combination or SSG engine is incompatible

        Example:
            composed_stack = create_composed_stack(
                scope=app,
                client_id="editorial-store",
                domain="editorialstore.com",
                cms_provider="sanity",
                ecommerce_provider="snipcart",
                ssg_engine="astro"
            )
        """

        # Validate CMS provider with lazy loading
        cms_stack_type = f"{cms_provider}_cms_tier"
        available_types = cls.get_available_stack_types()
        if cms_stack_type not in available_types:
            available_cms = [k.replace("_cms_tier", "") for k in available_types if k.endswith("_cms_tier")]
            raise ValueError(
                f"Unsupported CMS provider '{cms_provider}'. "
                f"Available providers: {', '.join(available_cms)}"
            )

        # Validate E-commerce provider with lazy loading
        ecommerce_stack_type = f"{ecommerce_provider}_ecommerce"
        if ecommerce_stack_type not in available_types:
            available_ecommerce = [k.replace("_ecommerce", "") for k in available_types if k.endswith("_ecommerce")]
            raise ValueError(
                f"Unsupported e-commerce provider '{ecommerce_provider}'. "
                f"Available providers: {', '.join(available_ecommerce)}"
            )

        # Validate SSG engine supports both integrations
        cms_metadata = cls.STACK_METADATA.get(cms_stack_type, {})
        ecommerce_metadata = cls.STACK_METADATA.get(ecommerce_stack_type, {})

        cms_engines = set(cms_metadata.get("ssg_engine_options", []))
        ecommerce_engines = set(ecommerce_metadata.get("ssg_engine_options", []))
        compatible_engines = cms_engines.intersection(ecommerce_engines)

        if ssg_engine not in compatible_engines:
            raise ValueError(
                f"SSG engine '{ssg_engine}' not compatible with both {cms_provider} and {ecommerce_provider}. "
                f"Compatible engines: {', '.join(sorted(compatible_engines))}"
            )

        # Generate construct ID
        construct_id = f"{client_id.title().replace('-', '')}-{cms_provider.title()}{ecommerce_provider.title()}Composed-Stack"

        # Get composed stack class with lazy loading
        composed_stack_class = cls.get_stack_class("cms_ecommerce_composed")

        # Create and return composed stack instance
        return composed_stack_class(
            scope=scope,
            construct_id=construct_id,
            client_id=client_id,
            domain=domain,
            cms_provider=cms_provider,
            ecommerce_provider=ecommerce_provider,
            ssg_engine=ssg_engine,
            **kwargs
        )

    @classmethod
    def get_recommendations(
        cls,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get intelligent stack recommendations based on technical capabilities and use cases.

        This unified recommendation engine analyzes client requirements and
        suggests optimal stack configurations based on technical fit and capabilities.

        Args:
            requirements: Dictionary of client requirements and technical preferences

        Returns:
            List of recommended stacks sorted by capability match score

        Example:
            requirements = {
                'project_type': 'business_site',
                'technical_level': 'intermediate',
                'performance_critical': True,
                'content_management': True,
                'framework_preference': 'react'
            }
            recommendations = get_recommendations(requirements)
        """
        recommendations = []

        # === SSG TEMPLATE BUSINESS SERVICE RECOMMENDATIONS ===

        # Hugo Template (Performance-critical technical teams)
        if (requirements.get("performance_critical", False) or
            requirements.get("technical_team", False) or
            requirements.get("documentation_site", False) or
            requirements.get("build_speed", False)):

            stack_metadata = cls.get_stack_metadata("hugo_template")
            recommendations.append({
                "stack_type": "hugo_template",
                "category": stack_metadata.get("category", "ssg_template_business_service"),
                "ssg_engine": "hugo",
                "tier_name": stack_metadata.get("tier_name", "Hugo Template"),
                "complexity_level": stack_metadata.get("complexity_level", "medium_to_high"),
                "reason": "Ultra-fast builds (1000+ pages/second) ideal for performance-critical technical sites",
                "best_for": stack_metadata.get("best_for", "Technical documentation, performance-critical sites"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "maximum"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # Gatsby Template (React ecosystem)
        if (requirements.get("react_preferred", False) or
            requirements.get("component_architecture", False) or
            requirements.get("graphql_preferred", False)):

            stack_metadata = cls.get_stack_metadata("gatsby_template")
            recommendations.append({
                "stack_type": "gatsby_template",
                "category": stack_metadata.get("category", "ssg_template_business_service"),
                "ssg_engine": "gatsby",
                "tier_name": stack_metadata.get("tier_name", "Gatsby Template"),
                "complexity_level": stack_metadata.get("complexity_level", "medium_to_high"),
                "reason": "React ecosystem with GraphQL data layer and rich plugin ecosystem",
                "best_for": stack_metadata.get("best_for", "React teams, component-driven development"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "optimized"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # Next.js Template (Full-stack React)
        if (requirements.get("react_preferred", False) or
            requirements.get("full_stack", False) or
            requirements.get("enterprise_features", False) or
            requirements.get("typescript_preferred", False)):

            stack_metadata = cls.get_stack_metadata("nextjs_template")
            recommendations.append({
                "stack_type": "nextjs_template",
                "category": stack_metadata.get("category", "ssg_template_business_service"),
                "ssg_engine": "nextjs",
                "tier_name": stack_metadata.get("tier_name", "Next.js Template"),
                "complexity_level": stack_metadata.get("complexity_level", "high"),
                "reason": "Enterprise-ready React framework with static export and full-stack growth path",
                "best_for": stack_metadata.get("best_for", "Enterprise teams, business applications"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "enterprise"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # Nuxt Template (Vue ecosystem)
        if (requirements.get("vue_preferred", False) or
            requirements.get("composition_api", False) or
            requirements.get("progressive_applications", False)):

            stack_metadata = cls.get_stack_metadata("nuxt_template")
            recommendations.append({
                "stack_type": "nuxt_template",
                "category": stack_metadata.get("category", "ssg_template_business_service"),
                "ssg_engine": "nuxt",
                "tier_name": stack_metadata.get("tier_name", "Nuxt Template"),
                "complexity_level": stack_metadata.get("complexity_level", "medium"),
                "reason": "Modern Vue 3 framework with Composition API and progressive enhancement",
                "best_for": stack_metadata.get("best_for", "Vue teams, modern component patterns"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "optimized"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # === FOUNDATION SSG RECOMMENDATIONS ===

        # Marketing-focused sites
        if (requirements.get("marketing_site", False) or
            requirements.get("seo_focused", False) or
            requirements.get("small_business", False)):

            stack_metadata = cls.get_stack_metadata("marketing")
            recommendations.append({
                "stack_type": "marketing",
                "category": stack_metadata.get("category", "foundation_ssg_service"),
                "ssg_engine": "eleventy",
                "tier_name": stack_metadata.get("tier_name", "Marketing-Optimized Static Sites"),
                "complexity_level": stack_metadata.get("complexity_level", "low_to_medium"),
                "reason": "Content-driven marketing sites optimized for SEO and fast loading",
                "best_for": stack_metadata.get("best_for", "Content-driven marketing sites"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "optimized"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # Developer-focused sites
        if (requirements.get("developer_site", False) or
            requirements.get("git_workflow", False) or
            requirements.get("github_pages", False)):

            stack_metadata = cls.get_stack_metadata("developer")
            recommendations.append({
                "stack_type": "developer",
                "category": stack_metadata.get("category", "foundation_ssg_service"),
                "ssg_engine": "jekyll",
                "tier_name": stack_metadata.get("tier_name", "Developer-Focused Git Workflow"),
                "complexity_level": stack_metadata.get("complexity_level", "medium"),
                "reason": "Technical sites with Git-based workflows and GitHub Pages compatibility",
                "best_for": stack_metadata.get("best_for", "Technical sites with Git workflows"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "basic"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # Modern performance sites
        if (requirements.get("interactive_features", False) or
            requirements.get("component_islands", False) or
            requirements.get("modern_tooling", False)):

            stack_metadata = cls.get_stack_metadata("modern_performance")
            recommendations.append({
                "stack_type": "modern_performance",
                "category": stack_metadata.get("category", "foundation_ssg_service"),
                "ssg_engine": "astro",
                "tier_name": stack_metadata.get("tier_name", "Modern High-Performance Interactive"),
                "complexity_level": stack_metadata.get("complexity_level", "medium_to_high"),
                "reason": "Modern sites requiring interactive features with optimal performance",
                "best_for": stack_metadata.get("best_for", "Modern sites with interactive features"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "premium"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # === CMS TIER RECOMMENDATIONS ===

        if requirements.get("content_management", False) or requirements.get("cms_needed", False):

            # Git-based CMS for technical teams
            if (requirements.get("technical_team", False) or
                requirements.get("git_workflow", False) or
                requirements.get("simple_cms", False)):

                recommended_ssg = cls._recommend_ssg_engine("decap_cms_tier", requirements)
                stack_metadata = cls.get_stack_metadata("decap_cms_tier")
                recommendations.append({
                    "stack_type": "decap_cms_tier",
                    "category": stack_metadata.get("category", "cms_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Decap CMS"),
                    "complexity_level": stack_metadata.get("complexity_level", "low_to_medium"),
                    "reason": "Git-based CMS with developer-friendly workflow and version control",
                    "best_for": stack_metadata.get("best_for", "Technical teams, git workflow"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "optimized"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

            # Visual editing CMS
            if (requirements.get("visual_editing", False) or
                requirements.get("content_creators", False) or
                requirements.get("real_time_preview", False)):

                recommended_ssg = cls._recommend_ssg_engine("tina_cms_tier", requirements)
                stack_metadata = cls.get_stack_metadata("tina_cms_tier")
                recommendations.append({
                    "stack_type": "tina_cms_tier",
                    "category": stack_metadata.get("category", "cms_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Tina CMS"),
                    "complexity_level": stack_metadata.get("complexity_level", "medium"),
                    "reason": "Visual content editing with git-based storage and real-time collaboration",
                    "best_for": stack_metadata.get("best_for", "Content creators, visual editing"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "optimized"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

            # Professional structured CMS
            if (requirements.get("structured_content", False) or
                requirements.get("professional_publishing", False) or
                requirements.get("api_first", False)):

                recommended_ssg = cls._recommend_ssg_engine("sanity_cms_tier", requirements)
                stack_metadata = cls.get_stack_metadata("sanity_cms_tier")
                recommendations.append({
                    "stack_type": "sanity_cms_tier",
                    "category": stack_metadata.get("category", "cms_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Sanity CMS"),
                    "complexity_level": stack_metadata.get("complexity_level", "medium_to_high"),
                    "reason": "Professional structured content management with real-time APIs",
                    "best_for": stack_metadata.get("best_for", "Professional content teams, structured content"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "premium"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

            # Enterprise CMS
            if (requirements.get("enterprise_features", False) or
                requirements.get("team_collaboration", False) or
                requirements.get("multi_language", False)):

                recommended_ssg = cls._recommend_ssg_engine("contentful_cms_tier", requirements)
                stack_metadata = cls.get_stack_metadata("contentful_cms_tier")
                recommendations.append({
                    "stack_type": "contentful_cms_tier",
                    "category": stack_metadata.get("category", "cms_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Contentful CMS"),
                    "complexity_level": stack_metadata.get("complexity_level", "high"),
                    "reason": "Enterprise-grade content management with advanced workflows",
                    "best_for": stack_metadata.get("best_for", "Enterprise teams, complex workflows"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "enterprise"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

        # === E-COMMERCE TIER RECOMMENDATIONS ===

        if requirements.get("ecommerce_needed", False) or requirements.get("online_store", False):

            # Simple e-commerce
            if (requirements.get("simple_store", False) or
                requirements.get("digital_products", False) or
                requirements.get("quick_setup", False)):

                recommended_ssg = cls._recommend_ssg_engine("snipcart_ecommerce", requirements)
                stack_metadata = cls.get_stack_metadata("snipcart_ecommerce")
                recommendations.append({
                    "stack_type": "snipcart_ecommerce",
                    "category": stack_metadata.get("category", "ecommerce_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Snipcart E-commerce"),
                    "complexity_level": stack_metadata.get("complexity_level", "low_to_medium"),
                    "reason": "Simple e-commerce integration with fast setup and minimal complexity",
                    "best_for": stack_metadata.get("best_for", "Simple stores, digital products"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "optimized"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

            # Advanced e-commerce features
            if (requirements.get("subscription_services", False) or
                requirements.get("advanced_checkout", False) or
                requirements.get("recurring_billing", False)):

                recommended_ssg = cls._recommend_ssg_engine("foxy_ecommerce", requirements)
                stack_metadata = cls.get_stack_metadata("foxy_ecommerce")
                recommendations.append({
                    "stack_type": "foxy_ecommerce",
                    "category": stack_metadata.get("category", "ecommerce_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Foxy E-commerce"),
                    "complexity_level": stack_metadata.get("complexity_level", "medium_to_high"),
                    "reason": "Advanced e-commerce features including subscriptions and complex pricing",
                    "best_for": stack_metadata.get("best_for", "Subscription services, advanced features"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "premium"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

            # Performance-focused e-commerce
            if (requirements.get("performance_critical", False) or
                requirements.get("high_traffic", False) or
                requirements.get("custom_frontend", False)):

                recommended_ssg = cls._recommend_ssg_engine("shopify_basic_ecommerce", requirements)
                stack_metadata = cls.get_stack_metadata("shopify_basic_ecommerce")
                recommendations.append({
                    "stack_type": "shopify_basic_ecommerce",
                    "category": stack_metadata.get("category", "ecommerce_tier_service"),
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": stack_metadata.get("ssg_engine_options", []),
                    "tier_name": stack_metadata.get("tier_name", "Shopify Basic"),
                    "complexity_level": stack_metadata.get("complexity_level", "medium"),
                    "reason": "High-performance e-commerce with Shopify platform and custom frontend flexibility",
                    "best_for": stack_metadata.get("best_for", "Performance-focused stores, custom frontends"),
                    "technical_requirements": stack_metadata.get("technical_requirements", []),
                    "key_features": stack_metadata.get("key_features", []),
                    "use_cases": stack_metadata.get("use_cases", []),
                    "performance_tier": stack_metadata.get("performance_tier", "premium"),
                    "target_audience": stack_metadata.get("target_audience", [])
                })

        # === COMPOSED STACK RECOMMENDATIONS ===

        if (requirements.get("content_management", False) and
            requirements.get("ecommerce_needed", False)):

            stack_metadata = cls.get_stack_metadata("cms_ecommerce_composed")
            recommendations.append({
                "stack_type": "cms_ecommerce_composed",
                "category": stack_metadata.get("category", "composed_service"),
                "provider_combinations": "flexible",
                "ssg_engine_options": stack_metadata.get("ssg_engine_options", ["astro", "gatsby", "nextjs"]),
                "tier_name": stack_metadata.get("tier_name", "Composed CMS + E-commerce Stack"),
                "complexity_level": stack_metadata.get("complexity_level", "high"),
                "reason": "Combined content management and e-commerce capabilities with unified orchestration",
                "best_for": stack_metadata.get("best_for", "Content-driven stores, editorial e-commerce"),
                "technical_requirements": stack_metadata.get("technical_requirements", []),
                "key_features": stack_metadata.get("key_features", []),
                "use_cases": stack_metadata.get("use_cases", []),
                "performance_tier": stack_metadata.get("performance_tier", "enterprise"),
                "target_audience": stack_metadata.get("target_audience", [])
            })

        # Sort recommendations by capability match score
        for rec in recommendations:
            rec["capability_match_score"] = cls._calculate_capability_match_score(rec, requirements)

        recommendations.sort(key=lambda x: x["capability_match_score"], reverse=True)

        return recommendations

    @classmethod
    def _recommend_ssg_engine(cls, stack_type: str, requirements: Dict[str, Any]) -> str:
        """Recommend optimal SSG engine for flexible stack based on requirements."""
        metadata = cls.STACK_METADATA.get(stack_type, {})
        supported_engines = metadata.get("ssg_engine_options", [])

        if not supported_engines:
            return "eleventy"  # Safe default

        # Performance critical
        if requirements.get("performance_critical", False):
            performance_order = ["hugo", "eleventy", "astro", "gatsby", "nextjs", "nuxt"]
            for engine in performance_order:
                if engine in supported_engines:
                    return engine

        # React preference
        if requirements.get("react_preferred", False):
            react_engines = ["gatsby", "nextjs", "astro"]
            for engine in react_engines:
                if engine in supported_engines:
                    return engine

        # Vue preference
        if requirements.get("vue_preferred", False):
            if "nuxt" in supported_engines:
                return "nuxt"

        # Technical team
        if requirements.get("technical_team", False):
            if "hugo" in supported_engines:
                return "hugo"

        # Default to first supported engine
        return supported_engines[0]

    @classmethod
    def _calculate_capability_match_score(cls, recommendation: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """Calculate capability match score for recommendation sorting based on technical alignment."""
        score = 10.0  # Base score

        # Technical complexity alignment
        rec_complexity = recommendation.get("complexity_level", "medium")
        req_complexity = requirements.get("technical_level", "intermediate")

        complexity_mapping = {
            "low": 1, "low_to_medium": 2, "medium": 3,
            "medium_to_high": 4, "high": 5,
            "beginner": 1, "intermediate": 3, "advanced": 5
        }

        rec_complexity_score = complexity_mapping.get(rec_complexity, 3)
        req_complexity_score = complexity_mapping.get(req_complexity, 3)

        # Perfect match gets bonus, close match gets partial bonus
        complexity_diff = abs(rec_complexity_score - req_complexity_score)
        if complexity_diff == 0:
            score += 20.0  # Perfect complexity match
        elif complexity_diff == 1:
            score += 10.0  # Close complexity match
        elif complexity_diff == 2:
            score += 5.0   # Moderate complexity match

        # Framework/SSG engine preferences
        ssg_engine = recommendation.get("ssg_engine", "")
        if requirements.get("react_preferred", False) and ssg_engine in ["gatsby", "nextjs"]:
            score += 25.0  # Strong framework alignment
        elif requirements.get("vue_preferred", False) and ssg_engine == "nuxt":
            score += 25.0  # Strong framework alignment
        elif requirements.get("performance_critical", False) and ssg_engine == "hugo":
            score += 25.0  # Performance requirement alignment

        # Project type alignment
        project_type = requirements.get("project_type", "")
        use_cases = recommendation.get("use_cases", [])
        target_audience = recommendation.get("target_audience", [])

        if project_type == "business_site" and any("business" in case for case in use_cases):
            score += 15.0
        elif project_type == "documentation" and any("documentation" in case for case in use_cases):
            score += 15.0
        elif project_type == "ecommerce" and any("commerce" in case or "store" in case for case in use_cases):
            score += 15.0

        # Performance tier alignment
        if requirements.get("performance_critical", False):
            performance_tier = recommendation.get("performance_tier", "standard")
            if performance_tier in ["maximum", "premium", "enterprise"]:
                score += 15.0
            elif performance_tier == "optimized":
                score += 10.0

        # Feature-specific alignments
        key_features = recommendation.get("key_features", [])

        # Visual editing preference
        if requirements.get("visual_editing", False) and any("visual" in feature for feature in key_features):
            score += 12.0

        # Git workflow preference
        if requirements.get("git_workflow", False) and any("git" in feature for feature in key_features):
            score += 12.0

        # API-first preference
        if requirements.get("api_first", False) and any("api" in feature for feature in key_features):
            score += 12.0

        # Enterprise features preference
        if requirements.get("enterprise_features", False) and any("enterprise" in feature for feature in key_features):
            score += 12.0

        # Technical team alignment with target audience
        if requirements.get("technical_team", False):
            if any("technical" in audience or "developer" in audience for audience in target_audience):
                score += 10.0

        # Content management alignment
        if requirements.get("content_management", False) and recommendation.get("category") == "cms_tier_service":
            score += 15.0

        # E-commerce alignment
        if requirements.get("ecommerce_needed", False) and recommendation.get("category") == "ecommerce_tier_service":
            score += 15.0

        # Composed stack bonus for complex requirements
        if (requirements.get("content_management", False) and
            requirements.get("ecommerce_needed", False) and
            recommendation.get("category") == "composed_service"):
            score += 20.0  # Bonus for matching complex architectural needs

        return score

    @classmethod
    def get_stack_metadata(cls, stack_type: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific stack type with registry integration.

        Uses multi-tier fallback system:
        1. S3 Provider Registry (distributed, globally cached)
        2. Embedded STACK_METADATA (local fallback)
        3. Empty dict (graceful degradation)

        Args:
            stack_type: Stack type identifier

        Returns:
            Stack metadata dictionary
        """

        # Primary: Try S3 Provider Registry
        if REGISTRY_AVAILABLE and default_registry:
            try:
                _log('debug', f"Fetching {stack_type} metadata from S3 Provider Registry")
                registry_data = default_registry.get_stack_metadata_sync(stack_type)
                if registry_data:
                    _log('debug', f"✅ Retrieved {stack_type} from registry")
                    return registry_data
            except Exception as e:
                _log('warning', f"Registry fetch failed for {stack_type}: {e}, using embedded data")

        # Secondary: Use embedded STACK_METADATA
        embedded_data = cls.STACK_METADATA.get(stack_type, {})
        if embedded_data:
            _log('debug', f"Using embedded metadata for {stack_type}")
            return embedded_data

        # Tertiary: Graceful degradation
        _log('warning', f"No metadata available for stack type: {stack_type}")
        return {}

    @classmethod
    def validate_stack_type(cls, stack_type: str) -> bool:
        """Validate that a stack type is supported with lazy loading optimization."""
        return stack_type in cls._STACK_IMPORT_CONFIG

    @classmethod
    def get_compatible_ssg_engines(cls, stack_type: str) -> List[str]:
        """Get SSG engines compatible with a specific stack type."""
        metadata = cls.STACK_METADATA.get(stack_type, {})
        return metadata.get("ssg_engine_options", [metadata.get("ssg_engine")] if metadata.get("ssg_engine") else [])

    @classmethod
    def get_stack_capabilities(
        cls,
        stack_type: str,
        ssg_engine: Optional[str] = None,
        client_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed capabilities and technical information for any stack type configuration.

        Args:
            stack_type: Platform stack type name
            ssg_engine: Optional SSG engine for flexible stacks
            client_requirements: Optional client requirements for capability matching

        Returns:
            Capability breakdown including technical requirements, features, and use cases
        """
        metadata = cls.get_stack_metadata(stack_type)
        if not metadata:
            raise ValueError(f"Unknown stack type: {stack_type}")

        # SSG engine complexity levels for technical requirements
        ssg_complexity_levels = {
            "hugo": "high_performance",     # Fast builds, technical setup
            "eleventy": "balanced",         # Good balance of features and complexity
            "astro": "modern",             # Modern tooling, component islands
            "gatsby": "react_ecosystem",    # React knowledge required
            "nextjs": "full_stack",        # Full-stack capabilities
            "nuxt": "vue_ecosystem"        # Vue knowledge required
        }

        complexity_description = "standard"
        if ssg_engine:
            complexity_description = ssg_complexity_levels.get(ssg_engine, "standard")

        return {
            "stack_type": stack_type,
            "ssg_engine": ssg_engine,
            "ssg_complexity_level": complexity_description,
            "technical_requirements": metadata.get("technical_requirements", []),
            "key_features": metadata.get("key_features", []),
            "use_cases": metadata.get("use_cases", []),
            "tier_name": metadata["tier_name"],
            "complexity_level": metadata["complexity_level"],
            "category": metadata["category"],
            "target_audience": metadata.get("target_audience", []),
            "performance_tier": metadata.get("performance_tier", "standard")
        }

    @classmethod
    def get_registry_status(cls) -> Dict[str, Any]:
        """
        Get S3 Provider Registry status for operational monitoring.

        Returns:
            Registry status dictionary with health information
        """
        if not REGISTRY_AVAILABLE or not default_registry:
            return {
                "available": False,
                "reason": "Registry not imported or initialized",
                "health": "unavailable",
                "metadata_source": "embedded"
            }

        try:
            health_status = default_registry.get_health_status()
            cache_stats = default_registry.get_cache_stats()

            return {
                "available": True,
                "health": health_status["status"],
                "uptime_score": health_status["uptime_score"],
                "base_url": health_status["base_url"],
                "cache_hit_ratio": health_status["cache_hit_ratio"],
                "consecutive_failures": health_status["consecutive_failures"],
                "cache_entries": cache_stats["cache_entries"],
                "fresh_entries": cache_stats["fresh_entries"],
                "http_client": health_status["http_client"],
                "fallback_available": health_status["fallback_available"],
                "metadata_source": "registry" if health_status["status"] == "healthy" else "embedded"
            }

        except Exception as e:
            return {
                "available": True,
                "health": "error",
                "error": str(e),
                "metadata_source": "embedded"
            }


# ===== CONVENIENCE FUNCTIONS FOR COMMON USE CASES =====

def create_hugo_performance_site(
    scope: Construct,
    client_id: str,
    domain: str
) -> BaseSSGStack:
    """Create performance-critical site with Hugo template stack"""
    return PlatformStackFactory.create_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type="hugo_template"
    )

def create_react_business_site(
    scope: Construct,
    client_id: str,
    domain: str,
    framework: str = "gatsby"  # gatsby or nextjs
) -> BaseSSGStack:
    """Create React-based business site with template stack choice"""
    stack_type = f"{framework}_template"
    return PlatformStackFactory.create_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type=stack_type
    )

def create_vue_application_site(
    scope: Construct,
    client_id: str,
    domain: str
) -> BaseSSGStack:
    """Create Vue 3 application with Nuxt template stack"""
    return PlatformStackFactory.create_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type="nuxt_template"
    )

def create_cms_site(
    scope: Construct,
    client_id: str,
    domain: str,
    cms_provider: str,
    ssg_engine: str = "astro"
) -> BaseSSGStack:
    """Create CMS-enabled site with flexible provider and SSG choice"""
    return PlatformStackFactory.create_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type=f"{cms_provider}_cms_tier",
        ssg_engine=ssg_engine
    )

def create_ecommerce_site(
    scope: Construct,
    client_id: str,
    domain: str,
    ecommerce_provider: str,
    ssg_engine: str = "eleventy"
) -> BaseSSGStack:
    """Create e-commerce site with flexible provider and SSG choice"""
    return PlatformStackFactory.create_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type=f"{ecommerce_provider}_ecommerce",
        ssg_engine=ssg_engine
    )

def create_content_commerce_site(
    scope: Construct,
    client_id: str,
    domain: str,
    cms_provider: str,
    ecommerce_provider: str,
    ssg_engine: str = "astro"
) -> BaseSSGStack:
    """Create combined content management + e-commerce site (SOLVES OWNERSHIP CRISIS)"""
    return PlatformStackFactory.create_composed_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        cms_provider=cms_provider,
        ecommerce_provider=ecommerce_provider,
        ssg_engine=ssg_engine
    )