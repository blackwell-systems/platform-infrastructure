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
            "monthly_cost_range": (80, 105),
            "setup_cost_range": (960, 2160),
            "target_market": ["technical_teams", "performance_critical_sites", "documentation_sites", "enterprise_technical"],
            "best_for": "Ultra-fast static sites with complex content relationships and technical documentation",
            "complexity_level": "medium_to_high",
            "ssg_engine": "hugo",
            "template_variants": ["documentation", "performance_blog", "technical_portfolio"],
            "key_features": ["ultra_fast_builds", "technical_documentation", "multi_language", "complex_taxonomies", "performance_optimization"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "maximum"
        },
        "gatsby_template": {
            "tier_name": "Gatsby Template - React Ecosystem with GraphQL",
            "category": "ssg_template_business_service",
            "monthly_cost_range": (85, 110),
            "setup_cost_range": (1200, 2400),
            "target_market": ["react_developers", "component_driven_teams", "content_heavy_sites", "javascript_teams"],
            "best_for": "React-based static sites with GraphQL data layer and component architecture",
            "complexity_level": "medium_to_high",
            "ssg_engine": "gatsby",
            "template_variants": ["react_business", "content_blog", "portfolio_showcase"],
            "key_features": ["react_components", "graphql_data_layer", "plugin_ecosystem", "image_optimization", "component_reusability"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized"
        },
        "nextjs_template": {
            "tier_name": "Next.js Template - Enterprise Full-Stack React Foundation",
            "category": "ssg_template_business_service",
            "monthly_cost_range": (85, 115),
            "setup_cost_range": (1440, 3360),
            "target_market": ["fullstack_developers", "enterprise_teams", "business_applications", "scalable_architecture"],
            "best_for": "Enterprise-ready React applications with static export and full-stack growth path",
            "complexity_level": "high",
            "ssg_engine": "nextjs",
            "template_variants": ["business_app", "marketing_site", "saas_landing"],
            "key_features": ["enterprise_patterns", "typescript_first", "api_routes_ready", "static_export", "full_stack_growth"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "enterprise"
        },
        "nuxt_template": {
            "tier_name": "Nuxt Template - Vue Ecosystem with Modern Patterns",
            "category": "ssg_template_business_service",
            "monthly_cost_range": (85, 115),
            "setup_cost_range": (1200, 2880),
            "target_market": ["vue_developers", "composition_api_teams", "progressive_applications", "vue_ecosystem"],
            "best_for": "Modern Vue 3 applications with Composition API and progressive enhancement features",
            "complexity_level": "medium",
            "ssg_engine": "nuxt",
            "template_variants": ["vue_business", "content_site", "vue_portfolio"],
            "key_features": ["vue_3_composition_api", "progressive_enhancement", "pinia_state_management", "modern_patterns", "vue_ecosystem"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized"
        },

        # === FOUNDATION SSG STACK METADATA ===
        "marketing": {
            "tier_name": "Marketing-Optimized Static Sites",
            "category": "foundation_ssg_service",
            "monthly_cost_range": (75, 100),
            "setup_cost_range": (1200, 2400),
            "target_market": ["small_businesses", "marketing_agencies", "content_creators", "professionals"],
            "best_for": "Content-driven marketing sites with fast loading and SEO optimization",
            "complexity_level": "low_to_medium",
            "ssg_engine": "eleventy",
            "template_variants": ["business_modern", "corporate_clean", "marketing_focused"],
            "key_features": ["fast_builds", "seo_optimized", "cost_effective", "developer_managed"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized"
        },
        "developer": {
            "tier_name": "Developer-Focused Git Workflow",
            "category": "foundation_ssg_service",
            "monthly_cost_range": (0, 25),  # Can use GitHub Pages for $0
            "setup_cost_range": (800, 1800),
            "target_market": ["developers", "technical_writers", "open_source_projects", "documentation_sites"],
            "best_for": "Technical sites with Git-based workflows and GitHub Pages compatibility",
            "complexity_level": "medium",
            "ssg_engine": "jekyll",
            "template_variants": ["technical_blog", "documentation", "simple_blog"],
            "key_features": ["github_pages_compatible", "git_workflow", "theme_system", "dual_hosting"],
            "hosting_pattern": "github_compatible",
            "performance_tier": "basic"
        },
        "modern_performance": {
            "tier_name": "Modern High-Performance Interactive",
            "category": "foundation_ssg_service",
            "monthly_cost_range": (60, 85),
            "setup_cost_range": (1200, 2400),
            "target_market": ["modern_businesses", "agencies", "performance_critical_sites", "interactive_applications"],
            "best_for": "Modern sites requiring interactive features with optimal performance",
            "complexity_level": "medium_to_high",
            "ssg_engine": "astro",
            "template_variants": ["modern_interactive", "component_islands", "performance_optimized"],
            "key_features": ["component_islands", "partial_hydration", "framework_agnostic", "performance_optimized"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium"
        },

        # === CMS TIER METADATA ===
        "decap_cms_tier": {
            "tier_name": "Decap CMS - Free Git-Based Content Management",
            "category": "cms_tier_service",
            "monthly_cost_range": (50, 75),  # No CMS fees, only hosting
            "setup_cost_range": (960, 2640),  # Varies by SSG engine choice
            "target_market": ["budget_conscious_businesses", "technical_teams", "small_to_medium_content", "git_workflow_users"],
            "best_for": "Budget-friendly content management with full git workflow control",
            "complexity_level": "low_to_medium",
            "cms_provider": "decap",
            "cms_type": "git_based",
            "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
            "template_variants": ["git_cms_basic", "markdown_focused", "developer_friendly"],
            "key_features": ["free_cms", "git_workflow", "markdown_editing", "github_oauth", "version_control", "no_vendor_lock_in"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized"
        },
        "tina_cms_tier": {
            "tier_name": "Tina CMS - Visual Editing with Git Workflow",
            "category": "cms_tier_service",
            "monthly_cost_range": (60, 125),  # Includes optional Tina Cloud features
            "setup_cost_range": (1200, 2880),  # Higher complexity due to visual editor integration
            "target_market": ["content_creators", "agencies", "visual_editing_preference", "collaboration_teams"],
            "best_for": "Visual content editing with git-based storage and real-time collaboration",
            "complexity_level": "medium",
            "cms_provider": "tina",
            "cms_type": "hybrid",
            "ssg_engine_options": ["nextjs", "astro", "gatsby"],
            "template_variants": ["visual_editor", "react_based", "collaboration_focused"],
            "key_features": ["visual_editing", "real_time_preview", "git_workflow", "react_based", "graphql_api", "collaboration"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized"
        },
        "sanity_cms_tier": {
            "tier_name": "Sanity CMS - Structured Content with Real-Time APIs",
            "category": "cms_tier_service",
            "monthly_cost_range": (65, 280),  # Hosting + Sanity CMS plans (Free to Business)
            "setup_cost_range": (1440, 3360),  # High complexity due to API integration and structured content
            "target_market": ["professional_content_teams", "api_first_developers", "structured_content_needs", "enterprise_ready"],
            "best_for": "Professional structured content management with real-time APIs and advanced querying",
            "complexity_level": "medium_to_high",
            "cms_provider": "sanity",
            "cms_type": "api_based",
            "ssg_engine_options": ["nextjs", "astro", "gatsby", "eleventy"],
            "template_variants": ["structured_content", "api_driven", "professional_editorial"],
            "key_features": ["structured_content", "groq_querying", "real_time_apis", "content_validation", "advanced_media", "webhook_automation"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium"
        },
        "contentful_cms_tier": {
            "tier_name": "Contentful CMS - Enterprise Content Management with Advanced Workflows",
            "category": "cms_tier_service",
            "monthly_cost_range": (75, 500),  # AWS hosting + Contentful subscription (Team to Business plans)
            "setup_cost_range": (2100, 4800),  # Enterprise complexity and customization requirements
            "target_market": ["enterprise_content_teams", "large_organizations", "complex_workflows", "multi_brand_companies", "international_businesses"],
            "best_for": "Enterprise-grade content management with advanced workflows, team collaboration, and multi-language support",
            "complexity_level": "high",
            "cms_provider": "contentful",
            "cms_type": "api_based",
            "ssg_engine_options": ["gatsby", "astro", "nextjs", "nuxt"],
            "template_variants": ["enterprise_workflows", "multi_language", "team_collaboration"],
            "key_features": ["enterprise_workflows", "team_collaboration", "multi_language_support", "content_versioning", "scheduled_publishing", "advanced_permissions"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "enterprise"
        },

        # === E-COMMERCE TIER METADATA ===
        "snipcart_ecommerce": {
            "tier_name": "Snipcart E-commerce - Simple E-commerce Integration",
            "category": "ecommerce_tier_service",
            "monthly_cost_range": (85, 125),
            "setup_cost_range": (960, 2640),
            "target_market": ["individuals", "small_businesses", "simple_stores"],
            "best_for": "Budget-friendly e-commerce with fast setup",
            "complexity_level": "low_to_medium",
            "ecommerce_provider": "snipcart",
            "provider_type": "simple_integration",
            "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
            "template_variants": ["simple_store", "digital_products", "catalog_basic"],
            "key_features": ["simple_integration", "secure_checkout", "inventory_management", "basic_analytics"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized"
        },
        "foxy_ecommerce": {
            "tier_name": "Foxy E-commerce - Advanced E-commerce Features",
            "category": "ecommerce_tier_service",
            "monthly_cost_range": (100, 150),
            "setup_cost_range": (1200, 3000),
            "target_market": ["small_businesses", "growing_companies", "subscription_services"],
            "best_for": "Advanced features, subscriptions, complex workflows",
            "complexity_level": "medium_to_high",
            "ecommerce_provider": "foxy",
            "provider_type": "advanced_platform",
            "ssg_engine_options": ["eleventy", "astro", "gatsby"],
            "template_variants": ["subscription_store", "advanced_catalog", "custom_checkout"],
            "key_features": ["subscription_management", "advanced_checkout", "webhook_automation", "complex_pricing"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium"
        },
        "shopify_basic_ecommerce": {
            "tier_name": "Shopify Basic - Performance E-commerce with Flexible SSG",
            "category": "ecommerce_tier_service",
            "monthly_cost_range": (75, 125),
            "setup_cost_range": (1600, 3200),
            "target_market": ["small_medium_stores", "performance_focused_brands", "agency_alternatives", "shopify_theme_upgrades"],
            "best_for": "Enterprise performance at small business prices - 80-90% cost reduction vs agencies",
            "complexity_level": "medium",
            "ecommerce_provider": "shopify_basic",
            "provider_type": "hosted_platform",
            "ssg_engine_options": ["eleventy", "astro", "nextjs", "nuxt"],
            "template_variants": ["performance_optimized", "static_site_ecommerce", "agency_alternative"],
            "key_features": ["shopify_storefront_api", "real_time_sync", "webhook_automation", "performance_optimization"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "premium"
        },

        # === COMPOSED STACK METADATA (SOLVES OWNERSHIP CRISIS) ===
        "cms_ecommerce_composed": {
            "tier_name": "Composed CMS + E-commerce Stack",
            "category": "composed_service",
            "monthly_cost_range": (140, 405),  # Combined range based on provider choices
            "setup_cost_range": (2160, 5760),  # Combined setup complexity
            "target_market": ["content_driven_stores", "editorial_ecommerce", "complex_business_models"],
            "best_for": "Sites requiring both professional content management and e-commerce capabilities",
            "complexity_level": "high",
            "provider_combinations": "flexible", # CMS + E-commerce provider choice
            "ssg_engine_options": ["astro", "gatsby", "nextjs"],  # SSGs supporting both integrations
            "template_variants": ["content_store", "editorial_commerce", "magazine_shop"],
            "key_features": ["unified_content_commerce", "cross_domain_events", "shared_user_management", "integrated_analytics"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "enterprise"
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
        Get intelligent stack recommendations across all service tiers.

        This unified recommendation engine analyzes client requirements and
        suggests optimal stack configurations from all available options.

        Args:
            requirements: Dictionary of client requirements and preferences

        Returns:
            List of recommended stacks sorted by suitability

        Example:
            requirements = {
                'budget_conscious': True,
                'technical_team': True,
                'performance_critical': True,
                'content_management': True
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

            recommendations.append({
                "stack_type": "hugo_template",
                "category": "ssg_template_business_service",
                "ssg_engine": "hugo",
                "monthly_cost": "$80-105",
                "setup_cost": "$960-2,160",
                "reason": "Ultra-fast builds (1000+ pages/second) ideal for performance-critical technical sites",
                "best_for": "Technical documentation, performance-critical sites, large content volumes",
                "complexity": "Medium to High",
                "key_benefits": [
                    "Ultra-fast build performance",
                    "Excellent for technical documentation",
                    "Multi-language support",
                    "Complex taxonomy management"
                ]
            })

        # Gatsby Template (React ecosystem)
        if (requirements.get("react_preferred", False) or
            requirements.get("component_architecture", False) or
            requirements.get("graphql_preferred", False)):

            recommendations.append({
                "stack_type": "gatsby_template",
                "category": "ssg_template_business_service",
                "ssg_engine": "gatsby",
                "monthly_cost": "$85-110",
                "setup_cost": "$1,200-2,400",
                "reason": "React ecosystem with GraphQL data layer and rich plugin ecosystem",
                "best_for": "React teams, component-driven development, content-heavy sites",
                "complexity": "Medium to High",
                "key_benefits": [
                    "React component architecture",
                    "Powerful GraphQL data layer",
                    "Rich plugin ecosystem",
                    "Advanced image optimization"
                ]
            })

        # Next.js Template (Full-stack React)
        if (requirements.get("react_preferred", False) or
            requirements.get("full_stack", False) or
            requirements.get("enterprise_features", False) or
            requirements.get("typescript_preferred", False)):

            recommendations.append({
                "stack_type": "nextjs_template",
                "category": "ssg_template_business_service",
                "ssg_engine": "nextjs",
                "monthly_cost": "$85-115",
                "setup_cost": "$1,440-3,360",
                "reason": "Enterprise-ready React framework with static export and full-stack growth path",
                "best_for": "Enterprise teams, business applications, full-stack React development",
                "complexity": "High",
                "key_benefits": [
                    "Enterprise-grade patterns",
                    "TypeScript-first development",
                    "API routes ready for activation",
                    "Full-stack architecture foundation"
                ]
            })

        # Nuxt Template (Vue ecosystem)
        if (requirements.get("vue_preferred", False) or
            requirements.get("composition_api", False) or
            requirements.get("progressive_applications", False)):

            recommendations.append({
                "stack_type": "nuxt_template",
                "category": "ssg_template_business_service",
                "ssg_engine": "nuxt",
                "monthly_cost": "$85-115",
                "setup_cost": "$1,200-2,880",
                "reason": "Modern Vue 3 framework with Composition API and progressive enhancement",
                "best_for": "Vue teams, modern component patterns, progressive applications",
                "complexity": "Medium",
                "key_benefits": [
                    "Vue 3 Composition API patterns",
                    "Progressive enhancement features",
                    "Pinia state management",
                    "Modern Vue ecosystem integration"
                ]
            })

        # === CMS TIER RECOMMENDATIONS ===

        if requirements.get("content_management", False) or requirements.get("cms_needed", False):

            # Budget-conscious CMS: Decap CMS
            if requirements.get("budget_conscious", False):
                recommended_ssg = cls._recommend_ssg_engine("decap_cms_tier", requirements)
                recommendations.append({
                    "stack_type": "decap_cms_tier",
                    "category": "cms_tier_service",
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
                    "monthly_cost": "$50-75",
                    "setup_cost": "$960-2,640",
                    "reason": "Free git-based CMS with full content management capabilities",
                    "best_for": "Budget-conscious sites, technical teams, git workflow",
                    "complexity": "Low to Medium",
                    "key_benefits": [
                        "Completely free CMS",
                        "Git-based workflow",
                        "Choose your SSG engine",
                        "No vendor lock-in"
                    ]
                })

            # Visual editing preference: Tina CMS
            if requirements.get("visual_editing", False):
                recommended_ssg = cls._recommend_ssg_engine("tina_cms_tier", requirements)
                recommendations.append({
                    "stack_type": "tina_cms_tier",
                    "category": "cms_tier_service",
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": ["nextjs", "astro", "gatsby"],
                    "monthly_cost": "$60-125",
                    "setup_cost": "$1,200-2,880",
                    "reason": "Visual editing CMS with git-based storage and real-time collaboration",
                    "best_for": "Content creators, agencies, visual editing preference",
                    "complexity": "Medium",
                    "key_benefits": [
                        "Visual editing interface",
                        "Real-time preview",
                        "Git-based storage",
                        "React-based admin"
                    ]
                })

        # === E-COMMERCE TIER RECOMMENDATIONS ===

        if requirements.get("ecommerce_needed", False) or requirements.get("online_store", False):

            # Simple e-commerce: Snipcart
            if requirements.get("budget_conscious", False) or requirements.get("simple_store", False):
                recommended_ssg = cls._recommend_ssg_engine("snipcart_ecommerce", requirements)
                recommendations.append({
                    "stack_type": "snipcart_ecommerce",
                    "category": "ecommerce_tier_service",
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
                    "monthly_cost": "$85-125",
                    "setup_cost": "$960-2,640",
                    "reason": "Budget-friendly e-commerce with fast setup and flexible SSG choice",
                    "best_for": "Small stores, digital products, simple catalogs",
                    "complexity": "Low to Medium"
                })

        # === COMPOSED STACK RECOMMENDATIONS ===

        if (requirements.get("content_management", False) and
            requirements.get("ecommerce_needed", False)):

            recommendations.append({
                "stack_type": "cms_ecommerce_composed",
                "category": "composed_service",
                "cms_provider": "flexible_choice",
                "ecommerce_provider": "flexible_choice",
                "ssg_engine_options": ["astro", "gatsby", "nextjs"],
                "monthly_cost": "$140-405",
                "setup_cost": "$2,160-5,760",
                "reason": "Combined content management and e-commerce capabilities with unified orchestration",
                "best_for": "Content-driven stores, editorial e-commerce, complex business models",
                "complexity": "High",
                "key_benefits": [
                    "Unified content and commerce",
                    "Cross-domain event integration",
                    "Shared user management",
                    "Integrated analytics"
                ]
            })

        # Sort recommendations by suitability score
        for rec in recommendations:
            rec["suitability_score"] = cls._calculate_suitability_score(rec, requirements)

        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)

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
    def _calculate_suitability_score(cls, recommendation: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """Calculate suitability score for recommendation sorting."""
        score = 5.0  # Base score

        # Budget alignment
        if requirements.get("budget_conscious", False):
            monthly_cost = recommendation.get("monthly_cost", "$100")
            min_cost = int(monthly_cost.split("-")[0].replace("$", ""))
            if min_cost <= 75:
                score += 2.0
            elif min_cost <= 100:
                score += 1.0

        # Technical team alignment
        if requirements.get("technical_team", False):
            complexity = recommendation.get("complexity", "Medium")
            if "High" in complexity:
                score += 1.5
            elif "Medium" in complexity:
                score += 1.0

        # Framework preferences
        ssg_engine = recommendation.get("ssg_engine", "")
        if requirements.get("react_preferred", False) and ssg_engine in ["gatsby", "nextjs"]:
            score += 2.0
        elif requirements.get("vue_preferred", False) and ssg_engine == "nuxt":
            score += 2.0
        elif requirements.get("performance_critical", False) and ssg_engine == "hugo":
            score += 2.0

        return score

    @classmethod
    def get_stack_metadata(cls, stack_type: str) -> Dict[str, Any]:
        """Get detailed metadata for a specific stack type."""
        return cls.STACK_METADATA.get(stack_type, {})

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
    def estimate_total_cost(
        cls,
        stack_type: str,
        ssg_engine: Optional[str] = None,
        client_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate total cost for any stack type configuration.

        Args:
            stack_type: Platform stack type name
            ssg_engine: Optional SSG engine for flexible stacks
            client_requirements: Optional client requirements for accurate estimation

        Returns:
            Cost breakdown including setup, monthly, and feature costs
        """
        metadata = cls.get_stack_metadata(stack_type)
        if not metadata:
            raise ValueError(f"Unknown stack type: {stack_type}")

        # Base cost ranges
        setup_range = metadata["setup_cost_range"]
        monthly_range = metadata["monthly_cost_range"]

        # SSG engine complexity adjustments
        ssg_multipliers = {
            "hugo": 0.9,        # Faster setup for technical users
            "eleventy": 1.0,    # Baseline
            "astro": 1.1,       # Modern tooling complexity
            "gatsby": 1.2,      # React ecosystem complexity
            "nextjs": 1.2,      # Full-stack complexity
            "nuxt": 1.2         # Vue ecosystem complexity
        }

        multiplier = 1.0
        if ssg_engine:
            multiplier = ssg_multipliers.get(ssg_engine, 1.0)

        adjusted_setup_cost = (
            int(setup_range[0] * multiplier),
            int(setup_range[1] * multiplier)
        )

        return {
            "stack_type": stack_type,
            "ssg_engine": ssg_engine,
            "setup_cost_range": adjusted_setup_cost,
            "monthly_cost_range": monthly_range,
            "ssg_complexity_multiplier": multiplier,
            "total_first_year_estimate": {
                "min": adjusted_setup_cost[0] + (monthly_range[0] * 12),
                "max": adjusted_setup_cost[1] + (monthly_range[1] * 12)
            },
            "tier_name": metadata["tier_name"],
            "complexity_level": metadata["complexity_level"],
            "category": metadata["category"]
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