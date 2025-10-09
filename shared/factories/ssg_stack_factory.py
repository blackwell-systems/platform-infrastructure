"""
SSG Stack Factory - Intelligent Static Site Generator Stack Selection

This factory implements intelligent SSG stack selection based on client requirements,
business use cases, and technical preferences. It complements the EcommerceStackFactory
to provide complete architectural consistency across the platform.

ARCHITECTURAL TRANSFORMATION:
- Before: Manual stack instantiation with hardcoded configurations
- After: Intelligent stack selection based on business use cases and client requirements

BUSINESS IMPACT:
- Automated stack recommendation based on client profile and requirements
- Consistent cost estimation and tier selection
- Simplified deployment process for different business use cases
- Clear separation between technical preferences and business requirements

SUPPORTED STACK TYPES:
- Marketing Stack: Cost-optimized for marketing sites and content-driven businesses
- Developer Stack: Technical workflow-focused with GitHub Pages compatibility
- Modern Performance Stack: High-performance with modern interactive features
- Enterprise Stack: High-scale with advanced features (future)

USAGE EXAMPLES:
- Content-focused business: Eleventy Marketing Stack (cost-optimized, fast builds)
- Technical team/documentation: Jekyll GitHub Stack (Git workflow, dual hosting)
- Performance-critical modern site: Astro Template Stack (component islands, interactive)
- Enterprise requirements: Enterprise Stack with advanced features (future)
"""

from typing import Dict, List, Any, Optional, Type
from constructs import Construct

# Dynamic imports to handle hyphenated directory names
import importlib.util
import sys
import os

def _import_from_hyphenated_path(module_path: str, class_name: str):
    """Import class from module path that may contain hyphens"""
    # Convert module path to file path
    file_path = module_path.replace('.', '/') + '.py'

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location(class_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
    else:
        raise ImportError(f"Could not import {class_name} from {module_path}")

# Import stack classes using dynamic loading
EleventyMarketingStack = _import_from_hyphenated_path("stacks/hosted-only/tier1/eleventy_marketing_stack", "EleventyMarketingStack")
JekyllGitHubStack = _import_from_hyphenated_path("stacks/hosted-only/tier1/jekyll_github_stack", "JekyllGitHubStack")
AstroTemplateBasicStack = _import_from_hyphenated_path("stacks/hosted-only/tier1/astro_template_basic_stack", "AstroTemplateBasicStack")
from shared.base.base_ssg_stack import BaseSSGStack
from shared.ssg import StaticSiteConfig


class SSGStackFactory:
    """
    Factory for creating SSG stacks based on business use cases and client requirements.

    This factory provides intelligent stack selection, cost estimation, and recommendation
    engine to match clients with optimal SSG stack configurations.
    """

    # SSG stack class registry organized by use case
    SSG_STACK_CLASSES: Dict[str, Type[BaseSSGStack]] = {
        "marketing": EleventyMarketingStack,
        "developer": JekyllGitHubStack,
        "modern_performance": AstroTemplateBasicStack,
        # Future stacks would be added here:
        # "enterprise": EnterpriseSSGStack,
        # "ecommerce_optimized": EcommerceOptimizedSSGStack,
        # "cms_integrated": CMSIntegratedSSGStack,
    }

    # Business tier information for each stack type
    STACK_TIERS: Dict[str, Dict[str, Any]] = {
        "marketing": {
            "tier_name": "Marketing-Optimized Static Sites",
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
        "decap_cms_tier": {
            "tier_name": "Decap CMS - Free Git-Based Content Management",
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
            "performance_tier": "optimized",
            "cms_features": ["admin_interface", "media_management", "editorial_workflow", "github_integration"],
            "ideal_client_profile": {
                "budget": "cost_conscious",
                "technical_comfort": "medium_to_high",
                "content_volume": "small_to_medium",
                "team_size": "1-5_people",
                "workflow_preference": "git_based"
            }
        },
        "tina_cms_tier": {
            "tier_name": "Tina CMS - Visual Editing with Git Workflow",
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
            "performance_tier": "optimized",
            "cms_features": ["visual_editor", "real_time_collaboration", "media_management", "structured_content", "preview_mode"],
            "ideal_client_profile": {
                "budget": "moderate",
                "technical_comfort": "medium",
                "content_volume": "small_to_large",
                "team_size": "2-10_people",
                "workflow_preference": "visual_editing"
            },
            "tina_cloud_features": ["real_time_sync", "team_collaboration", "advanced_media", "analytics_dashboard"]
        }
    }

    # SSG Engine capabilities matrix
    SSG_ENGINE_CAPABILITIES: Dict[str, Dict[str, Any]] = {
        "eleventy": {
            "build_speed": "very_fast",
            "learning_curve": "low",
            "ecosystem": "javascript",
            "best_for": ["marketing_sites", "blogs", "small_business_sites"],
            "template_engines": ["liquid", "nunjucks", "handlebars", "mustache"],
            "setup_complexity": "low"
        },
        "jekyll": {
            "build_speed": "medium",
            "learning_curve": "medium",
            "ecosystem": "ruby",
            "best_for": ["technical_blogs", "documentation", "github_pages"],
            "template_engines": ["liquid"],
            "setup_complexity": "medium",
            "github_pages_native": True
        },
        "astro": {
            "build_speed": "fast",
            "learning_curve": "medium_high",
            "ecosystem": "javascript",
            "best_for": ["modern_sites", "interactive_applications", "performance_critical"],
            "template_engines": ["astro", "jsx", "vue", "svelte"],
            "setup_complexity": "high",
            "component_islands": True
        },
        "hugo": {
            "build_speed": "fastest",
            "learning_curve": "high",
            "ecosystem": "go",
            "best_for": ["large_sites", "technical_users", "performance_critical"],
            "template_engines": ["go_templates"],
            "setup_complexity": "high"
        },
        "gatsby": {
            "build_speed": "slow",
            "learning_curve": "high",
            "ecosystem": "react",
            "best_for": ["react_applications", "complex_data_sites", "spa_like_sites"],
            "template_engines": ["jsx"],
            "setup_complexity": "high",
            "graphql_native": True
        },
        "nextjs": {
            "build_speed": "medium",
            "learning_curve": "high",
            "ecosystem": "react",
            "best_for": ["react_applications", "hybrid_rendering", "api_integration"],
            "template_engines": ["jsx"],
            "setup_complexity": "high",
            "hybrid_rendering": True
        },
        "nuxt": {
            "build_speed": "medium",
            "learning_curve": "high",
            "ecosystem": "vue",
            "best_for": ["vue_applications", "hybrid_rendering", "spa_like_sites"],
            "template_engines": ["vue"],
            "setup_complexity": "high",
            "hybrid_rendering": True
        }
    }

    @classmethod
    def create_ssg_stack(
        cls,
        scope: Construct,
        client_id: str,
        domain: str,
        stack_type: str,
        **kwargs
    ) -> BaseSSGStack:
        """
        Create SSG stack based on business use case and requirements.

        This method enables intelligent stack selection:
        1. Client specifies use case (marketing, developer, modern_performance)
        2. Factory creates optimized stack for the chosen use case
        3. Stack includes appropriate SSG engine, templates, and configurations

        Args:
            scope: CDK scope for stack creation
            client_id: Unique client identifier
            domain: Client domain name
            stack_type: Business use case (marketing, developer, modern_performance)
            **kwargs: Additional stack-specific arguments

        Returns:
            Configured SSG stack instance

        Raises:
            ValueError: If stack_type is invalid
        """

        # Validate stack type
        stack_class = cls.SSG_STACK_CLASSES.get(stack_type)
        if not stack_class:
            available_types = list(cls.SSG_STACK_CLASSES.keys())
            raise ValueError(
                f"Unsupported SSG stack type '{stack_type}'. "
                f"Available types: {available_types}"
            )

        # Generate construct ID
        construct_id = f"{client_id.title()}-{stack_type.title().replace('_', '')}-SSG-Stack"

        # Create and return stack instance
        return stack_class(
            scope=scope,
            construct_id=construct_id,
            client_id=client_id,
            domain=domain,
            **kwargs
        )

    @classmethod
    def get_ssg_recommendations(
        cls,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get SSG stack recommendations based on client requirements.

        This recommendation engine helps clients choose the optimal SSG stack
        based on their business needs, technical capabilities, and budget.

        Args:
            requirements: Dictionary of client requirements and preferences

        Returns:
            List of recommended stack types with explanations and cost estimates
        """
        recommendations = []

        # Marketing/Content-focused recommendations
        if (requirements.get("content_focused", False) or
            requirements.get("marketing_site", False) or
            requirements.get("budget_conscious", False)):

            recommendations.append({
                "stack_type": "marketing",
                "ssg_engine": "eleventy",
                "monthly_cost": "$75-100",
                "setup_cost": "$1,200-2,400",
                "reason": "Optimized for content-driven marketing sites with fast builds and cost efficiency",
                "best_for": "Marketing sites, small business sites, content creators",
                "complexity": "Low to Medium",
                "build_time": "Very Fast",
                "key_benefits": ["Cost effective", "Fast builds", "SEO optimized", "Easy content management"]
            })

        # Developer/Technical recommendations
        if (requirements.get("technical_team", False) or
            requirements.get("git_workflow", False) or
            requirements.get("documentation_site", False) or
            requirements.get("github_pages", False)):

            recommendations.append({
                "stack_type": "developer",
                "ssg_engine": "jekyll",
                "monthly_cost": "$0-25",
                "setup_cost": "$800-1,800",
                "reason": "Perfect for technical teams preferring Git workflows with GitHub Pages compatibility",
                "best_for": "Documentation, technical blogs, open source projects",
                "complexity": "Medium",
                "build_time": "Medium",
                "key_benefits": ["GitHub Pages compatible", "Git-based workflow", "Theme system", "Zero-cost hosting option"]
            })

        # Modern/Performance recommendations
        if (requirements.get("modern_features", False) or
            requirements.get("interactive_features", False) or
            requirements.get("performance_critical", False) or
            requirements.get("component_architecture", False)):

            recommendations.append({
                "stack_type": "modern_performance",
                "ssg_engine": "astro",
                "monthly_cost": "$60-85",
                "setup_cost": "$1,200-2,400",
                "reason": "Modern architecture with component islands for optimal performance and interactivity",
                "best_for": "Modern businesses, performance-critical sites, interactive applications",
                "complexity": "Medium to High",
                "build_time": "Fast",
                "key_benefits": ["Component islands", "Framework agnostic", "Optimal performance", "Modern developer experience"]
            })

        # CMS recommendations - Decap CMS tier (Budget-focused)
        if (requirements.get("content_management", False) or
            requirements.get("cms_needed", False) or
            requirements.get("git_based_cms", False) or
            requirements.get("budget_conscious", False) and requirements.get("content_management", False)):

            # Determine best SSG engine for Decap CMS based on requirements
            recommended_ssg = "eleventy"  # Default
            if requirements.get("performance_critical", False):
                recommended_ssg = "hugo"
            elif requirements.get("modern_features", False):
                recommended_ssg = "astro"
            elif requirements.get("react_preferred", False):
                recommended_ssg = "gatsby"

            recommendations.append({
                "stack_type": "decap_cms_tier",
                "ssg_engine": recommended_ssg,
                "ssg_engine_options": ["hugo", "eleventy", "astro", "gatsby"],
                "monthly_cost": "$50-75",
                "setup_cost": "$960-2,640",
                "reason": "Free git-based CMS with full content management capabilities and SSG flexibility",
                "best_for": "Budget-conscious sites needing content management, technical teams, small-medium content volume",
                "complexity": "Low to Medium",
                "build_time": "Fast",
                "cms_provider": "decap",
                "cms_cost": "$0/month",
                "key_benefits": [
                    "Completely free CMS",
                    "Git-based workflow",
                    "Choose your SSG engine",
                    "No vendor lock-in",
                    "Version controlled content",
                    "GitHub OAuth integration"
                ],
                "ideal_for": {
                    "budget": "Cost-conscious (free CMS)",
                    "team_size": "1-5 people",
                    "content_volume": "Small to medium",
                    "technical_comfort": "Medium (git workflow)"
                }
            })

        # CMS recommendations - Tina CMS tier (Visual editing focused)
        if (requirements.get("content_management", False) or
            requirements.get("cms_needed", False) or
            requirements.get("visual_editing", False) or
            requirements.get("collaboration", False) or
            requirements.get("content_creators", False)):

            # Determine best SSG engine for Tina CMS based on requirements
            recommended_ssg = "nextjs"  # Default for Tina (React-based)
            if requirements.get("modern_features", False) and not requirements.get("react_preferred", False):
                recommended_ssg = "astro"
            elif requirements.get("react_preferred", False) or requirements.get("graphql_preferred", False):
                recommended_ssg = "gatsby"

            recommendations.append({
                "stack_type": "tina_cms_tier",
                "ssg_engine": recommended_ssg,
                "ssg_engine_options": ["nextjs", "astro", "gatsby"],
                "monthly_cost": "$60-125",
                "setup_cost": "$1,200-2,880",
                "reason": "Visual editing CMS with git-based storage and real-time collaboration capabilities",
                "best_for": "Content creators, agencies, teams needing visual editing with git workflow control",
                "complexity": "Medium",
                "build_time": "Fast",
                "cms_provider": "tina",
                "cms_cost": "$0-50/month",
                "key_benefits": [
                    "Visual editing interface",
                    "Real-time preview",
                    "Git-based storage",
                    "React-based admin",
                    "GraphQL API",
                    "Optional cloud collaboration"
                ],
                "ideal_for": {
                    "budget": "Moderate ($60-125/month)",
                    "team_size": "2-10 people",
                    "content_volume": "Small to large",
                    "technical_comfort": "Medium (visual editing preference)"
                },
                "tina_cloud_features": ["real_time_sync", "team_collaboration", "advanced_media", "analytics"]
            })

        # Enterprise/Advanced recommendations (future)
        if requirements.get("enterprise_features", False) or requirements.get("high_scale", False):
            recommendations.append({
                "stack_type": "enterprise",
                "ssg_engine": "nextjs",  # Future implementation
                "monthly_cost": "$150-300",
                "setup_cost": "$3,000-6,000",
                "reason": "Enterprise-grade features with advanced customization and scale",
                "best_for": "Large organizations, complex requirements, high-scale sites",
                "complexity": "High",
                "build_time": "Medium",
                "key_benefits": ["Enterprise features", "Advanced customization", "High scale", "Professional support"],
                "status": "Coming Soon"
            })

        # Sort by cost if budget is a concern
        if requirements.get("budget_conscious", False):
            recommendations.sort(key=lambda x: cls._extract_min_cost(x["monthly_cost"]))
        else:
            # Sort by complexity match
            target_complexity = cls._determine_target_complexity(requirements)
            recommendations.sort(key=lambda x: cls._complexity_match_score(x["complexity"], target_complexity))

        return recommendations

    @classmethod
    def _extract_min_cost(cls, cost_range: str) -> int:
        """Extract minimum cost from cost range string"""
        try:
            return int(cost_range.split('-')[0].replace('$', ''))
        except:
            return 0

    @classmethod
    def _determine_target_complexity(cls, requirements: Dict[str, Any]) -> str:
        """Determine target complexity based on requirements"""
        if requirements.get("technical_team", False) and requirements.get("modern_features", False):
            return "High"
        elif requirements.get("technical_team", False) or requirements.get("interactive_features", False):
            return "Medium"
        else:
            return "Low"

    @classmethod
    def _complexity_match_score(cls, stack_complexity: str, target_complexity: str) -> int:
        """Calculate complexity match score (lower is better)"""
        complexity_levels = {"Low": 1, "Medium": 2, "High": 3}
        stack_level = complexity_levels.get(stack_complexity.split()[0], 2)
        target_level = complexity_levels.get(target_complexity, 2)
        return abs(stack_level - target_level)

    @classmethod
    def get_available_stack_types(cls) -> List[str]:
        """Get list of available SSG stack types"""
        return list(cls.SSG_STACK_CLASSES.keys())

    @classmethod
    def get_stack_tier_info(cls, stack_type: str) -> Dict[str, Any]:
        """
        Get detailed information about an SSG stack tier.

        Args:
            stack_type: SSG stack type name

        Returns:
            Stack tier information including costs, features, and target market
        """
        return cls.STACK_TIERS.get(stack_type, {})

    @classmethod
    def get_ssg_engine_info(cls, engine: str) -> Dict[str, Any]:
        """
        Get detailed information about an SSG engine.

        Args:
            engine: SSG engine name

        Returns:
            Engine capabilities and characteristics
        """
        return cls.SSG_ENGINE_CAPABILITIES.get(engine, {})

    @classmethod
    def estimate_total_cost(
        cls,
        stack_type: str,
        client_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate total cost for SSG stack type.

        Args:
            stack_type: SSG stack type name
            client_requirements: Optional client requirements for more accurate estimation

        Returns:
            Cost breakdown including setup, monthly, and feature costs
        """
        stack_info = cls.get_stack_tier_info(stack_type)
        if not stack_info:
            raise ValueError(f"Unknown SSG stack type: {stack_type}")

        # Base cost ranges
        setup_range = stack_info["setup_cost_range"]
        monthly_range = stack_info["monthly_cost_range"]

        # Complexity adjustments
        complexity_multipliers = {
            "low": 0.8,
            "low_to_medium": 1.0,
            "medium": 1.1,
            "medium_to_high": 1.3,
            "high": 1.5
        }

        complexity = stack_info.get("complexity_level", "medium")
        multiplier = complexity_multipliers.get(complexity, 1.0)

        adjusted_setup_cost = (
            int(setup_range[0] * multiplier),
            int(setup_range[1] * multiplier)
        )

        return {
            "setup_cost_range": adjusted_setup_cost,
            "monthly_cost_range": monthly_range,
            "complexity_multiplier": multiplier,
            "total_first_year_estimate": {
                "min": adjusted_setup_cost[0] + (monthly_range[0] * 12),
                "max": adjusted_setup_cost[1] + (monthly_range[1] * 12)
            },
            "stack_tier": stack_info["tier_name"],
            "complexity_level": complexity,
            "ssg_engine": stack_info["ssg_engine"],
            "hosting_pattern": stack_info.get("hosting_pattern", "aws_standard"),
            "performance_tier": stack_info.get("performance_tier", "standard")
        }

    @classmethod
    def get_client_decision_framework(cls) -> Dict[str, Any]:
        """
        Get structured decision framework to help clients choose optimal SSG stack.

        Returns:
            Decision framework with step-by-step guidance
        """
        return {
            "step_1_identify_use_case": {
                "description": "Identify primary business use case and requirements",
                "decision_points": {
                    "marketing_focused": "Choose Marketing stack for content-driven marketing sites",
                    "technical_team": "Choose Developer stack for Git workflows and technical control",
                    "modern_interactive": "Choose Modern Performance stack for interactive features",
                    "enterprise_scale": "Choose Enterprise stack for complex requirements (coming soon)"
                }
            },
            "step_2_assess_technical_capabilities": {
                "description": "Assess team technical capabilities and preferences",
                "decision_points": {
                    "low_technical": "Marketing stack offers simplest management",
                    "medium_technical": "Developer or Modern Performance based on use case",
                    "high_technical": "Any stack based on business requirements",
                    "framework_preference": "Consider SSG engine ecosystem alignment"
                }
            },
            "step_3_evaluate_budget": {
                "description": "Evaluate budget constraints and cost priorities",
                "budget_tiers": {
                    "minimal_budget": "Developer stack ($0-25/month with GitHub Pages)",
                    "small_business": "Marketing or Modern Performance stack ($60-100/month)",
                    "growing_business": "Any stack based on feature requirements",
                    "enterprise_budget": "Enterprise stack for maximum features (coming soon)"
                }
            },
            "step_4_validate_choice": {
                "description": "Ensure chosen stack meets all requirements",
                "validation_points": [
                    "Stack type supports required business use case",
                    "SSG engine matches team technical capabilities",
                    "Budget aligns with total cost estimate",
                    "Performance requirements are met",
                    "Hosting pattern matches preferences"
                ]
            }
        }

    @classmethod
    def validate_stack_type(cls, stack_type: str) -> bool:
        """
        Validate that a stack type is supported.

        Args:
            stack_type: SSG stack type name

        Returns:
            True if stack type is valid, False otherwise
        """
        return stack_type in cls.SSG_STACK_CLASSES

    @classmethod
    def get_recommended_stack_for_budget(cls, max_monthly_budget: float) -> List[str]:
        """
        Get stack types within a specific monthly budget.

        Args:
            max_monthly_budget: Maximum acceptable monthly cost

        Returns:
            List of stack types within the budget range
        """
        affordable_stacks = []

        for stack_type, info in cls.STACK_TIERS.items():
            min_cost = info["monthly_cost_range"][0]
            if min_cost <= max_monthly_budget:
                affordable_stacks.append(stack_type)

        return affordable_stacks

    @classmethod
    def get_stacks_by_ssg_engine(cls, ssg_engine: str) -> List[str]:
        """
        Get stack types that use a specific SSG engine.

        Args:
            ssg_engine: SSG engine name

        Returns:
            List of stack types using the specified engine
        """
        matching_stacks = []

        for stack_type, info in cls.STACK_TIERS.items():
            if info.get("ssg_engine") == ssg_engine:
                matching_stacks.append(stack_type)

        return matching_stacks


# Convenience functions for common use cases
def create_marketing_site(
    scope: Construct,
    client_id: str,
    domain: str
) -> EleventyMarketingStack:
    """Create a marketing-optimized static site with Eleventy"""
    return SSGStackFactory.create_ssg_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type="marketing"
    )


def create_developer_site(
    scope: Construct,
    client_id: str,
    domain: str,
    github_repo: Optional[str] = None,
    enable_github_pages_fallback: bool = True
) -> JekyllGitHubStack:
    """Create a developer-focused site with Jekyll and GitHub Pages compatibility"""
    return SSGStackFactory.create_ssg_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type="developer",
        github_repo=github_repo,
        enable_github_pages_fallback=enable_github_pages_fallback
    )


def create_modern_performance_site(
    scope: Construct,
    client_id: str,
    domain: str
) -> AstroTemplateBasicStack:
    """Create a modern high-performance site with Astro and component islands"""
    return SSGStackFactory.create_ssg_stack(
        scope=scope,
        client_id=client_id,
        domain=domain,
        stack_type="modern_performance"
    )