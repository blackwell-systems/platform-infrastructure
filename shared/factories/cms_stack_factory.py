"""
CMS Stack Factory

Factory class for creating CMS tier stacks with flexible SSG engine support.
Decoupled from SSGStackFactory to maintain clear architectural boundaries.

This factory handles complete CMS tier infrastructure stacks that combine:
- CMS providers (Decap, Tina, Sanity, Contentful)
- SSG engines (Hugo, Eleventy, Astro, Gatsby, Next.js, Nuxt)
- AWS infrastructure (S3, CloudFront, Route53, etc.)

Architecture Pattern:
- Provider-level: CMSProviderFactory creates individual CMS provider instances
- Stack-level: CMSStackFactory creates complete AWS infrastructure with CMS integration

Usage:
    cms_stack = CMSStackFactory.create_cms_stack(
        scope=app,
        client_id="example-client",
        domain="example.com",
        cms_provider="sanity",
        ssg_engine="astro"
    )
"""

from typing import Dict, Any, List, Type, Optional, Tuple
from constructs import Construct

# Import CMS tier stack implementations
from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack
from stacks.cms.tina_cms_tier_stack import TinaCMSTierStack
from stacks.cms.sanity_cms_tier_stack import SanityCMSTierStack
from stacks.cms.contentful_cms_stack import ContentfulCMSStack
from shared.base.base_ssg_stack import BaseSSGStack


class CMSStackFactory:
    """
    Factory for creating CMS tier stacks with flexible SSG engine support.

    Provides intelligent CMS stack creation, recommendations, and cost estimation
    based on client requirements and technical preferences.
    """

    # Registry of available CMS tier stacks
    CMS_STACK_CLASSES: Dict[str, Type[BaseSSGStack]] = {
        "decap_cms_tier": DecapCMSTierStack,
        "tina_cms_tier": TinaCMSTierStack,
        "sanity_cms_tier": SanityCMSTierStack,
        "contentful_cms_tier": ContentfulCMSStack,
    }

    # CMS tier metadata and cost information
    CMS_TIER_METADATA = {
        "decap_cms_tier": {
            "tier_name": "Decap CMS - Free Git-Based Content Management",
            "cms_provider": "decap",
            "cms_type": "git_based",
            "monthly_cost_range": (50, 75),  # No CMS fees, only hosting
            "setup_cost_range": (960, 2640),  # Varies by SSG engine choice
            "supported_ssg_engines": ["hugo", "eleventy", "astro", "gatsby"],
            "features": [
                "git_workflow", "markdown_editor", "version_control",
                "free_cms", "github_integration", "netlify_cms_compatible"
            ],
            "setup_complexity": "low",
            "technical_skill_required": "medium",
            "best_for": ["Budget-conscious sites", "Git-familiar teams", "Simple content needs"],
            "description": "Free Git-based CMS with GitHub workflow. Perfect for budget-conscious clients who want version control and simple content management.",
            "business_value": "Zero CMS licensing costs, full version control, developer-friendly workflow"
        },
        "tina_cms_tier": {
            "tier_name": "Tina CMS - Visual Editing with Git Workflow",
            "cms_provider": "tina",
            "cms_type": "hybrid",
            "monthly_cost_range": (60, 125),  # Includes optional Tina Cloud features
            "setup_cost_range": (1200, 2880),  # Higher complexity due to visual editor integration
            "supported_ssg_engines": ["nextjs", "astro", "gatsby", "eleventy"],
            "features": [
                "visual_editing", "live_preview", "git_workflow",
                "markdown_support", "media_management", "branch_based_editing"
            ],
            "setup_complexity": "medium",
            "technical_skill_required": "low",
            "best_for": ["Content creators", "Marketing teams", "Visual editing preference"],
            "description": "Modern visual editing experience with Git-based storage. Ideal for content creators who want WYSIWYG editing without sacrificing developer workflow.",
            "business_value": "Improved content creator experience, faster content updates, maintains developer workflow"
        },
        "sanity_cms_tier": {
            "tier_name": "Sanity CMS - Structured Content with Real-Time APIs",
            "cms_provider": "sanity",
            "cms_type": "api_based",
            "monthly_cost_range": (65, 280),  # Hosting + Sanity CMS plans (Free to Business)
            "setup_cost_range": (1440, 3360),  # High complexity due to API integration and structured content
            "supported_ssg_engines": ["nextjs", "astro", "gatsby", "eleventy"],
            "features": [
                "structured_content", "real_time_collaboration", "api_first",
                "custom_schemas", "image_processing", "webhooks",
                "multi_environment", "content_lake"
            ],
            "setup_complexity": "high",
            "technical_skill_required": "high",
            "best_for": ["Complex content models", "Multi-channel publishing", "Developer teams"],
            "description": "Powerful structured content CMS with real-time APIs. Perfect for complex content needs and multi-channel publishing.",
            "business_value": "Scalable content architecture, real-time collaboration, future-proof API-first approach"
        },
        "contentful_cms_tier": {
            "tier_name": "Contentful CMS - Enterprise Content Management with Advanced Workflows",
            "cms_provider": "contentful",
            "cms_type": "api_based",
            "monthly_cost_range": (75, 500),  # AWS hosting + Contentful subscription (Team to Business plans)
            "setup_cost_range": (2100, 4800),  # Enterprise complexity and customization requirements
            "supported_ssg_engines": ["gatsby", "astro", "nextjs", "nuxt"],
            "features": [
                "enterprise_workflows", "content_modeling", "multi_language",
                "user_roles_permissions", "content_scheduling", "webhooks",
                "cdn_integration", "enterprise_sla", "advanced_analytics"
            ],
            "setup_complexity": "high",
            "technical_skill_required": "medium",
            "best_for": ["Enterprise content teams", "Multi-language sites", "Complex workflows"],
            "description": "Enterprise-grade content management with advanced workflows and team collaboration features.",
            "business_value": "Enterprise scalability, advanced team workflows, proven content platform"
        }
    }

    @classmethod
    def create_cms_stack(
        cls,
        scope: Construct,
        client_id: str,
        domain: str,
        cms_provider: str,
        ssg_engine: str = None,
        template_variant: str = "default",
        **kwargs
    ) -> BaseSSGStack:
        """
        Create a CMS tier stack with specified provider and SSG engine.

        Args:
            scope: CDK construct scope
            client_id: Unique client identifier
            domain: Client domain name
            cms_provider: CMS provider name (decap, tina, sanity, contentful)
            ssg_engine: SSG engine choice (optional - will auto-select if not provided)
            template_variant: Template variant within the CMS tier
            **kwargs: Additional configuration options

        Returns:
            Configured CMS tier stack instance

        Raises:
            ValueError: If cms_provider is not supported or SSG engine incompatible

        Example:
            cms_stack = CMSStackFactory.create_cms_stack(
                scope=app,
                client_id="creative-agency",
                domain="creativeagency.com",
                cms_provider="sanity",
                ssg_engine="astro"
            )
        """
        # Validate CMS provider
        stack_type = f"{cms_provider}_cms_tier"
        if stack_type not in cls.CMS_STACK_CLASSES:
            available_providers = [k.replace("_cms_tier", "") for k in cls.CMS_STACK_CLASSES.keys()]
            raise ValueError(
                f"Unsupported CMS provider '{cms_provider}'. "
                f"Available providers: {', '.join(available_providers)}"
            )

        # Get stack class and metadata
        stack_class = cls.CMS_STACK_CLASSES[stack_type]
        tier_metadata = cls.CMS_TIER_METADATA[stack_type]

        # Auto-select SSG engine if not provided
        if not ssg_engine:
            ssg_engine = cls._recommend_ssg_engine_for_cms(cms_provider, kwargs)

        # Validate SSG engine compatibility
        supported_engines = tier_metadata["supported_ssg_engines"]
        if ssg_engine not in supported_engines:
            raise ValueError(
                f"SSG engine '{ssg_engine}' not supported by {cms_provider} CMS tier. "
                f"Supported engines: {', '.join(supported_engines)}"
            )

        # Generate construct ID
        construct_id = f"{client_id.title().replace('-', '')}-{cms_provider.title()}CMS-Stack"

        # Create client configuration
        from models.client import ClientConfig, ServiceIntegrationConfig, CMSProviderConfig
        from shared.ssg.ssg_engines import ServiceType, IntegrationMode

        client_config = ClientConfig(
            client_id=client_id,
            company_name=kwargs.get("company_name", f"{client_id.title()} Company"),
            domain=domain,
            contact_email=kwargs.get("contact_email", f"admin@{domain}"),
            service_integration=ServiceIntegrationConfig(
                service_type=ServiceType.CMS_TIER,
                integration_mode=kwargs.get("integration_mode", IntegrationMode.DIRECT),
                ssg_engine=ssg_engine,
                cms_config=CMSProviderConfig(
                    provider=cms_provider,
                    settings=kwargs.get("cms_settings", {})
                )
            )
        )

        # Create and return stack instance
        return stack_class(
            scope=scope,
            construct_id=construct_id,
            client_config=client_config,
            template_variant=template_variant,
            **kwargs
        )

    @classmethod
    def get_cms_recommendations(
        cls,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get CMS tier recommendations based on client requirements.

        Args:
            requirements: Dictionary of client requirements and preferences

        Returns:
            List of CMS recommendations sorted by suitability

        Example:
            requirements = {
                'budget_conscious': True,
                'visual_editing_preferred': False,
                'technical_team': True,
                'content_volume': 'medium',
                'multi_language': False
            }

            recommendations = CMSStackFactory.get_cms_recommendations(requirements)
        """
        recommendations = []

        for stack_type, metadata in cls.CMS_TIER_METADATA.items():
            suitability_score = cls._calculate_cms_suitability_score(metadata, requirements)

            if suitability_score["score"] >= 6.0:  # Only recommend suitable options
                # Get optimal SSG engine for this CMS + requirements
                cms_provider = metadata["cms_provider"]
                recommended_ssg = cls._recommend_ssg_engine_for_cms(cms_provider, requirements)

                recommendations.append({
                    "stack_type": stack_type,
                    "cms_provider": cms_provider,
                    "ssg_engine": recommended_ssg,
                    "ssg_engine_options": metadata["supported_ssg_engines"],
                    "suitability": suitability_score,
                    "monthly_cost_range": f"${metadata['monthly_cost_range'][0]}-{metadata['monthly_cost_range'][1]}",
                    "setup_cost_range": f"${metadata['setup_cost_range'][0]}-{metadata['setup_cost_range'][1]}",
                    "tier_name": metadata["tier_name"],
                    "business_value": metadata["business_value"],
                    "best_for": metadata["best_for"],
                    "setup_complexity": metadata["setup_complexity"]
                })

        # Sort by suitability score (descending)
        recommendations.sort(key=lambda x: x["suitability"]["score"], reverse=True)

        return recommendations

    @classmethod
    def get_cms_provider_comparison(
        cls,
        cms_providers: List[str],
        ssg_engine: str = None
    ) -> Dict[str, Any]:
        """
        Compare multiple CMS providers across key criteria.

        Args:
            cms_providers: List of CMS provider names to compare
            ssg_engine: Optional SSG engine to check compatibility

        Returns:
            Comparison matrix with provider details and recommendations

        Example:
            comparison = CMSStackFactory.get_cms_provider_comparison(
                ["decap", "sanity", "contentful"],
                ssg_engine="astro"
            )
        """
        comparison = {
            "providers": {},
            "summary": {
                "most_cost_effective": None,
                "most_feature_rich": None,
                "easiest_setup": None,
                "best_for_developers": None
            }
        }

        cost_scores = {}
        feature_scores = {}
        complexity_scores = {}
        developer_scores = {}

        for provider in cms_providers:
            stack_type = f"{provider}_cms_tier"

            if stack_type not in cls.CMS_TIER_METADATA:
                comparison["providers"][provider] = {"error": "Provider not supported"}
                continue

            metadata = cls.CMS_TIER_METADATA[stack_type]

            # Check SSG engine compatibility if specified
            ssg_compatible = True
            if ssg_engine:
                ssg_compatible = ssg_engine in metadata["supported_ssg_engines"]

            # Calculate comparison scores
            min_cost = metadata["monthly_cost_range"][0]
            max_cost = metadata["monthly_cost_range"][1]
            avg_cost = (min_cost + max_cost) / 2

            cost_scores[provider] = 1000 / avg_cost  # Lower cost = higher score
            feature_scores[provider] = len(metadata["features"])
            complexity_scores[provider] = {"low": 3, "medium": 2, "high": 1}[metadata["setup_complexity"]]
            developer_scores[provider] = {
                "git_based": 3, "hybrid": 2, "api_based": 1
            }.get(metadata["cms_type"], 1)

            comparison["providers"][provider] = {
                "tier_name": metadata["tier_name"],
                "cms_type": metadata["cms_type"],
                "monthly_cost_range": metadata["monthly_cost_range"],
                "setup_cost_range": metadata["setup_cost_range"],
                "supported_ssg_engines": metadata["supported_ssg_engines"],
                "ssg_engine_compatible": ssg_compatible,
                "features": metadata["features"],
                "feature_count": len(metadata["features"]),
                "setup_complexity": metadata["setup_complexity"],
                "technical_skill_required": metadata["technical_skill_required"],
                "best_for": metadata["best_for"],
                "business_value": metadata["business_value"],
                "scores": {
                    "cost_effectiveness": cost_scores[provider],
                    "feature_richness": feature_scores[provider],
                    "ease_of_setup": complexity_scores[provider],
                    "developer_friendliness": developer_scores[provider]
                }
            }

        # Determine best in each category
        if cost_scores:
            comparison["summary"]["most_cost_effective"] = max(cost_scores, key=cost_scores.get)
        if feature_scores:
            comparison["summary"]["most_feature_rich"] = max(feature_scores, key=feature_scores.get)
        if complexity_scores:
            comparison["summary"]["easiest_setup"] = max(complexity_scores, key=complexity_scores.get)
        if developer_scores:
            comparison["summary"]["best_for_developers"] = max(developer_scores, key=developer_scores.get)

        return comparison

    @classmethod
    def estimate_cms_costs(
        cls,
        cms_provider: str,
        ssg_engine: str,
        content_volume: str = "medium",
        team_size: int = 1
    ) -> Dict[str, Any]:
        """
        Estimate total costs for a CMS tier stack configuration.

        Args:
            cms_provider: CMS provider name
            ssg_engine: SSG engine choice
            content_volume: Expected content volume (small, medium, large)
            team_size: Number of team members using the CMS

        Returns:
            Detailed cost breakdown and estimates

        Example:
            costs = CMSStackFactory.estimate_cms_costs(
                cms_provider="sanity",
                ssg_engine="astro",
                content_volume="large",
                team_size=5
            )
        """
        stack_type = f"{cms_provider}_cms_tier"

        if stack_type not in cls.CMS_TIER_METADATA:
            raise ValueError(f"Unsupported CMS provider: {cms_provider}")

        metadata = cls.CMS_TIER_METADATA[stack_type]

        # Base costs from metadata
        base_monthly_min, base_monthly_max = metadata["monthly_cost_range"]
        setup_min, setup_max = metadata["setup_cost_range"]

        # Volume multipliers
        volume_multipliers = {
            "small": 0.8,   # Simpler setup, lower hosting costs
            "medium": 1.0,  # Base pricing
            "large": 1.3    # More complex setup, higher hosting costs
        }

        # Team size adjustments (mainly affects CMS provider costs)
        team_multipliers = {
            1: 1.0,         # Single user
            2: 1.1,         # Small team
            5: 1.3,         # Medium team
            10: 1.6         # Large team
        }

        # Find closest team size multiplier
        team_sizes = sorted(team_multipliers.keys())
        closest_team_size = min(team_sizes, key=lambda x: abs(x - team_size))
        team_multiplier = team_multipliers[closest_team_size]

        volume_multiplier = volume_multipliers.get(content_volume, 1.0)

        # Calculate adjusted costs
        adjusted_monthly_min = base_monthly_min * volume_multiplier * team_multiplier
        adjusted_monthly_max = base_monthly_max * volume_multiplier * team_multiplier
        adjusted_setup_min = setup_min * volume_multiplier
        adjusted_setup_max = setup_max * volume_multiplier

        # SSG engine complexity adjustment
        ssg_complexity_multipliers = {
            "hugo": 0.9,        # Faster builds, simpler setup
            "eleventy": 1.0,    # Baseline
            "astro": 1.1,       # Modern tooling complexity
            "gatsby": 1.2,      # React complexity
            "nextjs": 1.2,      # Full-stack complexity
            "nuxt": 1.2         # Vue complexity
        }

        ssg_multiplier = ssg_complexity_multipliers.get(ssg_engine, 1.0)
        final_setup_min = adjusted_setup_min * ssg_multiplier
        final_setup_max = adjusted_setup_max * ssg_multiplier

        return {
            "cms_provider": cms_provider,
            "ssg_engine": ssg_engine,
            "content_volume": content_volume,
            "team_size": team_size,
            "cost_breakdown": {
                "setup_cost_range": (int(final_setup_min), int(final_setup_max)),
                "monthly_cost_range": (int(adjusted_monthly_min), int(adjusted_monthly_max)),
                "cms_provider_cost": cls._estimate_cms_provider_cost(cms_provider, team_size),
                "aws_hosting_cost": cls._estimate_aws_hosting_cost(content_volume),
                "maintenance_cost": cls._estimate_maintenance_cost(metadata["setup_complexity"])
            },
            "multipliers_applied": {
                "volume_multiplier": volume_multiplier,
                "team_multiplier": team_multiplier,
                "ssg_complexity_multiplier": ssg_multiplier
            },
            "cost_factors": {
                "base_monthly_range": metadata["monthly_cost_range"],
                "base_setup_range": metadata["setup_cost_range"],
                "cms_type": metadata["cms_type"],
                "setup_complexity": metadata["setup_complexity"]
            }
        }

    @classmethod
    def get_available_cms_providers(cls) -> List[str]:
        """Get list of available CMS providers."""
        return [k.replace("_cms_tier", "") for k in cls.CMS_STACK_CLASSES.keys()]

    @classmethod
    def get_supported_ssg_engines(cls, cms_provider: str) -> List[str]:
        """Get SSG engines supported by a specific CMS provider."""
        stack_type = f"{cms_provider}_cms_tier"
        if stack_type not in cls.CMS_TIER_METADATA:
            raise ValueError(f"Unsupported CMS provider: {cms_provider}")

        return cls.CMS_TIER_METADATA[stack_type]["supported_ssg_engines"]

    @classmethod
    def validate_cms_ssg_combination(cls, cms_provider: str, ssg_engine: str) -> bool:
        """Validate if CMS provider supports the specified SSG engine."""
        try:
            supported_engines = cls.get_supported_ssg_engines(cms_provider)
            return ssg_engine in supported_engines
        except ValueError:
            return False

    @classmethod
    def _calculate_cms_suitability_score(
        cls,
        metadata: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate suitability score for CMS recommendation."""
        score = 0.0
        reasons = []

        # Budget alignment
        budget_conscious = requirements.get("budget_conscious", False)
        monthly_cost_avg = sum(metadata["monthly_cost_range"]) / 2

        if budget_conscious and monthly_cost_avg <= 75:
            score += 3.0
            reasons.append("cost-effective for budget-conscious projects")
        elif not budget_conscious and monthly_cost_avg > 100:
            score += 2.0
            reasons.append("feature-rich solution")
        elif not budget_conscious:
            score += 1.5

        # Visual editing preference
        visual_editing_preferred = requirements.get("visual_editing_preferred", False)
        has_visual_editing = "visual_editing" in metadata["features"]

        if visual_editing_preferred and has_visual_editing:
            score += 2.5
            reasons.append("provides visual editing capabilities")
        elif visual_editing_preferred and not has_visual_editing:
            score -= 1.0

        # Technical team alignment
        technical_team = requirements.get("technical_team", False)
        setup_complexity = metadata["setup_complexity"]

        if technical_team and setup_complexity == "high":
            score += 2.0
            reasons.append("advanced features for technical teams")
        elif not technical_team and setup_complexity == "low":
            score += 2.0
            reasons.append("easy setup for non-technical teams")
        elif technical_team and setup_complexity == "medium":
            score += 1.5

        # Content volume requirements
        content_volume = requirements.get("content_volume", "medium")
        cms_type = metadata["cms_type"]

        if content_volume == "large" and cms_type == "api_based":
            score += 1.5
            reasons.append("API-based architecture scales well")
        elif content_volume == "small" and cms_type == "git_based":
            score += 1.0
            reasons.append("Git-based workflow ideal for simple content")

        # Multi-language requirements
        multi_language = requirements.get("multi_language", False)
        has_multi_language = "multi_language" in metadata["features"]

        if multi_language and has_multi_language:
            score += 1.5
            reasons.append("supports multi-language content")
        elif multi_language and not has_multi_language:
            score -= 1.5

        # Real-time collaboration needs
        collaboration_needed = requirements.get("real_time_collaboration", False)
        has_collaboration = "real_time_collaboration" in metadata["features"]

        if collaboration_needed and has_collaboration:
            score += 1.0
            reasons.append("enables real-time team collaboration")

        return {
            "score": round(score, 1),
            "suitability": "excellent" if score >= 8 else "good" if score >= 6 else "limited",
            "reasons": reasons,
            "cms_type": cms_type,
            "setup_complexity": setup_complexity,
            "monthly_cost_range": metadata["monthly_cost_range"]
        }

    @classmethod
    def _recommend_ssg_engine_for_cms(cls, cms_provider: str, requirements: Dict[str, Any] = None) -> str:
        """Recommend optimal SSG engine for CMS provider based on requirements."""
        if requirements is None:
            requirements = {}

        stack_type = f"{cms_provider}_cms_tier"
        metadata = cls.CMS_TIER_METADATA.get(stack_type, {})
        supported_engines = metadata.get("supported_ssg_engines", [])

        if not supported_engines:
            return "eleventy"  # Safe default

        # Technical team preferences
        if requirements.get("technical_team", False):
            if "hugo" in supported_engines:
                return "hugo"  # Fastest for technical users

        # Performance critical requirements
        if requirements.get("performance_critical", False):
            performance_order = ["hugo", "eleventy", "astro", "gatsby", "nextjs", "nuxt"]
            for engine in performance_order:
                if engine in supported_engines:
                    return engine

        # React ecosystem preference
        if requirements.get("react_preferred", False):
            react_engines = ["gatsby", "nextjs", "astro"]
            for engine in react_engines:
                if engine in supported_engines:
                    return engine

        # Vue ecosystem preference
        if requirements.get("vue_preferred", False):
            if "nuxt" in supported_engines:
                return "nuxt"

        # Default recommendations by CMS provider
        cms_defaults = {
            "decap": "eleventy",    # Good balance for Git-based workflow
            "tina": "astro",        # Modern performance with visual editing
            "sanity": "nextjs",     # API integration works well with Next.js
            "contentful": "gatsby"  # Strong GraphQL integration
        }

        default_engine = cms_defaults.get(cms_provider, "eleventy")
        return default_engine if default_engine in supported_engines else supported_engines[0]

    @classmethod
    def _estimate_cms_provider_cost(cls, cms_provider: str, team_size: int) -> Dict[str, Any]:
        """Estimate CMS provider-specific costs."""
        # Provider cost structures
        provider_costs = {
            "decap": {"base": 0, "per_user": 0, "description": "Free open-source CMS"},
            "tina": {"base": 0, "per_user": 5, "description": "Free tier available, $5/user for advanced features"},
            "sanity": {"base": 0, "per_user": 20, "description": "Free tier for small teams, scales with usage"},
            "contentful": {"base": 300, "per_user": 0, "description": "Team plan starts at $300/month"}
        }

        cost_info = provider_costs.get(cms_provider, {"base": 0, "per_user": 0, "description": "Unknown provider"})

        monthly_cost = cost_info["base"] + (cost_info["per_user"] * team_size)

        return {
            "monthly_cost": monthly_cost,
            "breakdown": {
                "base_cost": cost_info["base"],
                "per_user_cost": cost_info["per_user"],
                "team_size": team_size
            },
            "description": cost_info["description"]
        }

    @classmethod
    def _estimate_aws_hosting_cost(cls, content_volume: str) -> Dict[str, Any]:
        """Estimate AWS hosting costs based on content volume."""
        volume_costs = {
            "small": {"monthly": 15, "description": "Basic S3 + CloudFront for simple sites"},
            "medium": {"monthly": 35, "description": "Standard hosting with moderate traffic"},
            "large": {"monthly": 75, "description": "Higher traffic with advanced caching"}
        }

        cost_info = volume_costs.get(content_volume, volume_costs["medium"])

        return {
            "monthly_cost": cost_info["monthly"],
            "description": cost_info["description"],
            "services": ["S3", "CloudFront", "Route53", "Certificate Manager"]
        }

    @classmethod
    def _estimate_maintenance_cost(cls, setup_complexity: str) -> Dict[str, Any]:
        """Estimate maintenance costs based on setup complexity."""
        maintenance_costs = {
            "low": {"monthly": 25, "description": "Basic monitoring and updates"},
            "medium": {"monthly": 50, "description": "Regular maintenance and optimization"},
            "high": {"monthly": 100, "description": "Advanced monitoring and custom maintenance"}
        }

        cost_info = maintenance_costs.get(setup_complexity, maintenance_costs["medium"])

        return {
            "monthly_cost": cost_info["monthly"],
            "description": cost_info["description"],
            "includes": ["Security updates", "Performance monitoring", "Backup management"]
        }

    @classmethod
    def register_cms_stack(cls, cms_provider: str, stack_class: Type[BaseSSGStack]) -> None:
        """
        Register a new CMS tier stack.

        Args:
            cms_provider: CMS provider name
            stack_class: Stack class extending BaseSSGStack
        """
        stack_type = f"{cms_provider}_cms_tier"
        cls.CMS_STACK_CLASSES[stack_type] = stack_class

    @classmethod
    def is_cms_provider_supported(cls, cms_provider: str) -> bool:
        """Check if CMS provider is supported."""
        stack_type = f"{cms_provider}_cms_tier"
        return stack_type in cls.CMS_STACK_CLASSES