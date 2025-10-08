"""
E-commerce Stack Factory - Flexible E-commerce Provider and SSG Engine Selection

This factory implements the e-commerce provider flexibility architecture,
enabling clients to choose their e-commerce provider tier based on features
and budget, then select their preferred SSG engine based on technical comfort.

ARCHITECTURAL TRANSFORMATION:
- Before: Hardcoded e-commerce/SSG pairings (ElevntySnipcartStack, AstroFoxyStack)
- After: Flexible client choice within provider tiers (12+ combinations from 4 provider classes)

BUSINESS IMPACT:
- Same monthly pricing serves multiple technical comfort levels
- Client choice eliminates arbitrary technology constraints
- Revenue optimization through appropriate complexity alignment
- 75% reduction in stack classes while exponentially increasing client options

USAGE EXAMPLES:
- Budget-conscious technical client: Hugo + Snipcart (fast builds, simple e-commerce)
- Modern business: Astro + Snipcart (component islands, simple e-commerce)
- Advanced features needed: Gatsby + Foxy (React ecosystem, advanced e-commerce)
- Enterprise requirements: Next.js + Shopify Advanced (React, enterprise features)
"""

from typing import Dict, List, Any, Optional, Type
from constructs import Construct

from stacks.ecommerce.snipcart_ecommerce_stack import SnipcartEcommerceStack
from stacks.ecommerce.foxy_ecommerce_stack import FoxyEcommerceStack
from shared.base.base_ecommerce_stack import BaseEcommerceStack


class EcommerceStackFactory:
    """
    Factory for creating e-commerce stacks with flexible SSG engine support.

    This factory enables the architectural transformation from hardcoded
    e-commerce/SSG pairings to flexible client choice within provider tiers.
    """

    # E-commerce stack class registry
    ECOMMERCE_STACK_CLASSES: Dict[str, Type[BaseEcommerceStack]] = {
        "snipcart": SnipcartEcommerceStack,
        "foxy": FoxyEcommerceStack,
        # Note: ShopifyBasicStack and ShopifyAdvancedStack would be added here
    }

    # E-commerce provider tier information
    PROVIDER_TIERS: Dict[str, Dict[str, Any]] = {
        "snipcart": {
            "tier_name": "Simple E-commerce",
            "monthly_cost_range": (85, 125),
            "setup_cost_range": (960, 2640),
            "target_market": ["individuals", "small_businesses", "simple_stores"],
            "best_for": "Budget-friendly e-commerce with fast setup",
            "complexity_level": "low_to_medium"
        },
        "foxy": {
            "tier_name": "Advanced E-commerce",
            "monthly_cost_range": (100, 150),
            "setup_cost_range": (1200, 3000),
            "target_market": ["small_businesses", "growing_companies", "subscription_services"],
            "best_for": "Advanced features, subscriptions, complex workflows",
            "complexity_level": "medium_to_high"
        },
        "shopify_basic": {
            "tier_name": "Standard E-commerce",
            "monthly_cost_range": (75, 125),
            "setup_cost_range": (1800, 3600),
            "target_market": ["small_businesses", "product_retailers", "inventory_focused"],
            "best_for": "Standard e-commerce with inventory management",
            "complexity_level": "medium"
        },
        "shopify_advanced": {
            "tier_name": "Enterprise E-commerce",
            "monthly_cost_range": (150, 300),
            "setup_cost_range": (3600, 6000),
            "target_market": ["enterprises", "high_volume_retailers", "custom_requirements"],
            "best_for": "Enterprise features, custom experiences, high volume",
            "complexity_level": "high"
        }
    }

    @classmethod
    def create_ecommerce_stack(
        cls,
        scope: Construct,
        client_id: str,
        domain: str,
        ecommerce_provider: str,
        ssg_engine: str = "eleventy",
        **kwargs
    ) -> BaseEcommerceStack:
        """
        Create e-commerce stack with specified provider and SSG engine.

        This method enables flexible client choice:
        1. Client chooses e-commerce provider tier (snipcart/foxy/shopify) based on features/budget
        2. Client chooses SSG engine based on technical comfort and requirements
        3. Factory creates optimized stack for the chosen combination

        Args:
            scope: CDK scope for stack creation
            client_id: Unique client identifier
            domain: Client domain name
            ecommerce_provider: E-commerce provider (snipcart, foxy, shopify_basic, shopify_advanced)
            ssg_engine: SSG engine choice (hugo, eleventy, astro, gatsby, nextjs, nuxt)
            **kwargs: Additional provider-specific arguments

        Returns:
            Configured e-commerce stack instance

        Raises:
            ValueError: If provider/engine combination is invalid
        """

        # Validate e-commerce provider
        stack_class = cls.ECOMMERCE_STACK_CLASSES.get(ecommerce_provider)
        if not stack_class:
            available_providers = list(cls.ECOMMERCE_STACK_CLASSES.keys())
            raise ValueError(
                f"Unsupported e-commerce provider '{ecommerce_provider}'. "
                f"Available providers: {available_providers}"
            )

        # Validate SSG engine compatibility
        compatible_engines = BaseEcommerceStack.COMPATIBLE_SSG_ENGINES.get(ecommerce_provider, [])
        if ssg_engine not in compatible_engines:
            raise ValueError(
                f"SSG engine '{ssg_engine}' is not compatible with e-commerce provider '{ecommerce_provider}'. "
                f"Compatible engines: {compatible_engines}"
            )

        # Generate construct ID
        construct_id = f"{client_id.title()}-{ecommerce_provider.title()}-{ssg_engine.title()}-Stack"

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
    def get_ecommerce_recommendations(
        cls,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get e-commerce provider and SSG engine recommendations based on client requirements.

        This recommendation engine helps clients choose the optimal combination
        of e-commerce provider tier and SSG engine based on their specific needs.

        Args:
            requirements: Dictionary of client requirements and preferences

        Returns:
            List of recommended provider/engine combinations with explanations
        """
        recommendations = []

        # Budget-conscious recommendations
        if requirements.get("budget_conscious", False):
            ssg_options = ["eleventy", "hugo"] if requirements.get("technical_team", False) else ["eleventy"]
            recommendations.append({
                "ecommerce_provider": "snipcart",
                "ssg_options": ssg_options,
                "monthly_cost": "$85-125",
                "setup_cost": "$960-1,800" if "hugo" in ssg_options else "$1,200-2,160",
                "reason": "Budget-friendly e-commerce with efficient SSG engines",
                "best_for": "Small stores, digital products, simple catalogs",
                "complexity": "Low to Medium",
                "recommended_ssg": "hugo" if requirements.get("technical_team") else "eleventy"
            })

        # Advanced features needed
        if requirements.get("advanced_ecommerce", False) or requirements.get("subscriptions", False):
            ssg_options = []
            if requirements.get("prefer_react", False):
                ssg_options = ["gatsby", "astro"]
            elif requirements.get("modern_features", False):
                ssg_options = ["astro", "gatsby"]
            else:
                ssg_options = ["astro", "eleventy", "gatsby"]

            recommendations.append({
                "ecommerce_provider": "foxy",
                "ssg_options": ssg_options,
                "monthly_cost": "$100-150",
                "setup_cost": "$1,440-3,000",
                "reason": "Advanced e-commerce features with flexible SSG integration",
                "best_for": "Subscription products, complex workflows, advanced analytics",
                "complexity": "Medium to High",
                "recommended_ssg": cls._recommend_ssg_for_foxy(requirements)
            })

        # Enterprise/Shopify requirements
        if requirements.get("shopify_integration", False) or requirements.get("enterprise_ecommerce", False):
            ssg_options = []
            if requirements.get("prefer_react", False):
                ssg_options = ["nextjs", "gatsby"]
            elif requirements.get("prefer_vue", False):
                ssg_options = ["nuxt"]
            elif requirements.get("modern_features", False):
                ssg_options = ["astro", "nextjs"]
            else:
                ssg_options = ["astro", "nextjs", "nuxt"]

            tier = "shopify_advanced" if requirements.get("enterprise_ecommerce") else "shopify_basic"
            cost_info = cls.PROVIDER_TIERS[tier]

            recommendations.append({
                "ecommerce_provider": tier,
                "ssg_options": ssg_options,
                "monthly_cost": f"${cost_info['monthly_cost_range'][0]}-{cost_info['monthly_cost_range'][1]}",
                "setup_cost": f"${cost_info['setup_cost_range'][0]}-{cost_info['setup_cost_range'][1]}",
                "reason": f"{cost_info['best_for']} with headless architecture",
                "best_for": "Large catalogs, custom experiences, enterprise workflows",
                "complexity": cost_info['complexity_level'].title(),
                "recommended_ssg": cls._recommend_ssg_for_shopify(requirements, tier)
            })

        # Performance-focused recommendations
        if requirements.get("performance_critical", False):
            recommendations.append({
                "ecommerce_provider": "snipcart",
                "ssg_options": ["hugo", "astro"],
                "monthly_cost": "$85-125",
                "setup_cost": "$960-2,400",
                "reason": "Fastest SSG engines with lightweight e-commerce integration",
                "best_for": "High-traffic sites, fast loading, technical teams",
                "complexity": "Medium",
                "recommended_ssg": "hugo"
            })

        return recommendations

    @classmethod
    def _recommend_ssg_for_foxy(cls, requirements: Dict[str, Any]) -> str:
        """Recommend optimal SSG engine for Foxy.io based on requirements"""
        if requirements.get("prefer_react", False):
            return "gatsby"
        elif requirements.get("modern_features", False):
            return "astro"
        elif requirements.get("technical_team", False):
            return "astro"  # Foxy works well with Astro's islands
        else:
            return "eleventy"

    @classmethod
    def _recommend_ssg_for_shopify(cls, requirements: Dict[str, Any], tier: str) -> str:
        """Recommend optimal SSG engine for Shopify based on requirements and tier"""
        if requirements.get("prefer_react", False):
            return "nextjs"
        elif requirements.get("prefer_vue", False):
            return "nuxt"
        elif requirements.get("modern_features", False):
            return "astro"
        elif tier == "shopify_advanced":
            return "nextjs"  # Enterprise features work well with Next.js
        else:
            return "astro"

    @classmethod
    def get_all_valid_combinations(cls) -> Dict[str, List[str]]:
        """
        Get all valid e-commerce provider and SSG engine combinations.

        Returns:
            Dictionary mapping each provider to its compatible SSG engines
        """
        return BaseEcommerceStack.COMPATIBLE_SSG_ENGINES.copy()

    @classmethod
    def get_provider_tier_info(cls, provider: str) -> Dict[str, Any]:
        """
        Get detailed information about an e-commerce provider tier.

        Args:
            provider: E-commerce provider name

        Returns:
            Provider tier information including costs, features, and target market
        """
        return cls.PROVIDER_TIERS.get(provider, {})

    @classmethod
    def estimate_total_cost(
        cls,
        ecommerce_provider: str,
        ssg_engine: str,
        client_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate total cost for e-commerce provider and SSG engine combination.

        Args:
            ecommerce_provider: E-commerce provider name
            ssg_engine: SSG engine name
            client_requirements: Optional client requirements for more accurate estimation

        Returns:
            Cost breakdown including setup, monthly, and provider fees
        """
        provider_info = cls.get_provider_tier_info(ecommerce_provider)
        if not provider_info:
            raise ValueError(f"Unknown e-commerce provider: {ecommerce_provider}")

        # SSG engine complexity multipliers for setup cost
        ssg_multipliers = {
            "hugo": 0.8,      # Fastest setup, technical users
            "eleventy": 1.0,  # Baseline complexity
            "astro": 1.2,     # Modern features require more setup
            "gatsby": 1.4,    # Complex GraphQL integration
            "nextjs": 1.3,    # React ecosystem complexity
            "nuxt": 1.3       # Vue ecosystem complexity
        }

        multiplier = ssg_multipliers.get(ssg_engine, 1.0)
        base_setup_range = provider_info["setup_cost_range"]

        adjusted_setup_cost = (
            int(base_setup_range[0] * multiplier),
            int(base_setup_range[1] * multiplier)
        )

        # Provider-specific transaction fees
        provider_metadata = BaseEcommerceStack.PROVIDER_METADATA.get(ecommerce_provider, {})
        transaction_fee = provider_metadata.get("transaction_fee", 0.025)

        return {
            "setup_cost_range": adjusted_setup_cost,
            "monthly_cost_range": provider_info["monthly_cost_range"],
            "transaction_fee_percent": transaction_fee * 100,
            "ssg_complexity_multiplier": multiplier,
            "total_first_year_estimate": {
                "min": adjusted_setup_cost[0] + (provider_info["monthly_cost_range"][0] * 12),
                "max": adjusted_setup_cost[1] + (provider_info["monthly_cost_range"][1] * 12)
            },
            "provider_tier": provider_info["tier_name"],
            "complexity_level": provider_info["complexity_level"]
        }

    @classmethod
    def validate_combination(cls, ecommerce_provider: str, ssg_engine: str) -> bool:
        """
        Validate that an e-commerce provider and SSG engine combination is supported.

        Args:
            ecommerce_provider: E-commerce provider name
            ssg_engine: SSG engine name

        Returns:
            True if combination is valid, False otherwise
        """
        compatible_engines = BaseEcommerceStack.COMPATIBLE_SSG_ENGINES.get(ecommerce_provider, [])
        return ssg_engine in compatible_engines

    @classmethod
    def get_client_decision_framework(cls) -> Dict[str, Any]:
        """
        Get structured decision framework to help clients choose optimal combination.

        Returns:
            Decision framework with step-by-step guidance
        """
        return {
            "step_1_choose_provider_tier": {
                "description": "Choose e-commerce provider tier based on features and budget",
                "decision_points": {
                    "budget_conscious": "Choose Snipcart for simple, cost-effective e-commerce",
                    "advanced_features": "Choose Foxy for subscriptions and advanced functionality",
                    "shopify_ecosystem": "Choose Shopify Basic for standard e-commerce with inventory",
                    "enterprise_needs": "Choose Shopify Advanced for enterprise features and scale"
                }
            },
            "step_2_choose_ssg_engine": {
                "description": "Choose SSG engine based on technical comfort and requirements",
                "decision_points": {
                    "technical_team": "Hugo for fastest builds and technical control",
                    "balanced_approach": "Eleventy for simplicity and flexibility",
                    "modern_features": "Astro for component islands and modern architecture",
                    "react_ecosystem": "Gatsby or Next.js for React-based development",
                    "vue_ecosystem": "Nuxt for Vue-based development"
                }
            },
            "step_3_validate_choice": {
                "description": "Ensure chosen combination meets all requirements",
                "validation_points": [
                    "Provider tier supports required e-commerce features",
                    "SSG engine matches team technical capabilities",
                    "Budget aligns with total cost estimate",
                    "Combination is validated as compatible"
                ]
            }
        }


# Convenience functions for common use cases
def create_simple_ecommerce_store(
    scope: Construct,
    client_id: str,
    domain: str,
    ssg_engine: str = "eleventy"
) -> SnipcartEcommerceStack:
    """Create a simple e-commerce store with Snipcart and flexible SSG choice"""
    return EcommerceStackFactory.create_ecommerce_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        ecommerce_provider="snipcart",
        ssg_engine=ssg_engine
    )


def create_advanced_ecommerce_store(
    scope: Construct,
    client_id: str,
    domain: str,
    ssg_engine: str = "astro",
    enable_subscriptions: bool = True
) -> FoxyEcommerceStack:
    """Create an advanced e-commerce store with Foxy and flexible SSG choice"""
    return EcommerceStackFactory.create_ecommerce_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        ecommerce_provider="foxy",
        ssg_engine=ssg_engine,
        enable_subscriptions=enable_subscriptions
    )