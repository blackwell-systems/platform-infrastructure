"""
CMS Provider Factory

Factory class for creating CMS provider instances.
Follows the same pattern as EcommerceProviderFactory to maintain consistency
across the platform architecture.

Supported CMS Providers:
- Decap CMS: Git-based CMS with GitHub integration (free)
- Tina CMS: Hybrid CMS with visual editing ($60-85/month)
- Sanity: API-based CMS with real-time collaboration ($65-90/month)
- Contentful: Enterprise API-based CMS ($75-125/month)

Usage:
    provider = CMSProviderFactory.create_provider("decap", config)
    provider.setup_infrastructure(stack)
"""

from typing import Dict, Any, List, Type, Optional
from .base_provider import CMSProvider, CMSType, CMSAuthMethod


class CMSProviderFactory:
    """
    Factory for creating CMS provider instances.

    Provides a consistent interface for instantiating different
    CMS providers based on provider name and configuration.
    """

    # Registry of available providers
    _providers: Dict[str, Type[CMSProvider]] = {
        # Git-based CMS providers
        "decap": None,  # Lazy loaded to avoid circular imports
        # "forestry": ForestryProvider,  # Legacy, being phased out

        # Hybrid CMS providers
        "tina": None,   # Lazy loaded to avoid circular imports

        # API-based CMS providers
        # "sanity": SanityCMSProvider,
        # "contentful": ContentfulProvider,
        # "strapi": StrapiProvider,
        # "ghost": GhostProvider,

        # Self-hosted options
        # "directus": DirectusProvider,
        # "payload": PayloadCMSProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str, config: Dict[str, Any]) -> CMSProvider:
        """
        Create a CMS provider instance.

        Args:
            provider_name: Name of the CMS provider (e.g., "decap", "sanity")
            config: Provider-specific configuration dictionary

        Returns:
            CMSProvider instance for the specified provider

        Raises:
            ValueError: If provider_name is not supported

        Example:
            config = {"admin_users": ["admin@example.com"], "content_path": "content"}
            provider = CMSProviderFactory.create_provider("decap", config)
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            available_msg = f"Available providers: {available}" if available else "No providers currently registered"
            raise ValueError(
                f"Unsupported CMS provider '{provider_name}'. "
                f"{available_msg}"
            )

        # Lazy load providers to avoid circular imports
        provider_class = cls._providers[provider_name]
        if provider_class is None:
            provider_class = cls._load_provider_class(provider_name)
            cls._providers[provider_name] = provider_class

        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available CMS provider names.

        Returns:
            List of supported provider names
        """
        return list(cls._providers.keys())

    @classmethod
    def get_provider_metadata(cls, provider_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific CMS provider without instantiating it.

        Args:
            provider_name: Name of the CMS provider

        Returns:
            Provider metadata dictionary

        Raises:
            ValueError: If provider_name is not supported
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            available_msg = f"Available providers: {available}" if available else "No providers currently registered"
            raise ValueError(
                f"Unsupported CMS provider '{provider_name}'. "
                f"{available_msg}"
            )

        # Create a temporary instance with minimal config to get metadata
        provider_class = cls._providers[provider_name]
        temp_provider = provider_class({})  # Most providers handle empty config for metadata
        return temp_provider.get_configuration_metadata()

    @classmethod
    def get_all_providers_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all available CMS providers.

        Returns:
            Dictionary mapping provider names to their metadata

        Example:
            {
                "decap": {
                    "cms_type": "git_based",
                    "monthly_cost_range": [0, 0],
                    "setup_complexity": "low",
                    "features": ["markdown_editor", "git_workflow"]
                },
                "sanity": {
                    "cms_type": "api_based",
                    "monthly_cost_range": [0, 99],
                    "setup_complexity": "medium",
                    "features": ["visual_editor", "real_time_collaboration"]
                }
            }
        """
        metadata = {}
        for provider_name in cls._providers.keys():
            try:
                metadata[provider_name] = cls.get_provider_metadata(provider_name)
            except Exception as e:
                # Log error but continue with other providers
                print(f"Warning: Could not get metadata for {provider_name}: {e}")
                metadata[provider_name] = {"error": str(e)}

        return metadata

    @classmethod
    def get_providers_by_cms_type(cls, cms_type: CMSType) -> List[str]:
        """
        Get CMS providers that match a specific architecture type.

        Args:
            cms_type: CMS architecture type (git_based, api_based, hybrid)

        Returns:
            List of provider names matching the CMS type

        Example:
            git_providers = CMSProviderFactory.get_providers_by_cms_type(CMSType.GIT_BASED)
            # Returns: ["decap", "forestry"]
        """
        matching_providers = []

        for provider_name in cls._providers.keys():
            try:
                provider_class = cls._providers[provider_name]
                temp_provider = provider_class({})
                if temp_provider.get_cms_type() == cms_type:
                    matching_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return matching_providers

    @classmethod
    def get_providers_by_feature(cls, feature: str) -> List[str]:
        """
        Get CMS providers that support a specific feature.

        Args:
            feature: Feature name to search for (e.g., "visual_editor", "real_time_collaboration")

        Returns:
            List of provider names that support the feature

        Example:
            visual_editors = CMSProviderFactory.get_providers_by_feature("visual_editor")
            # Returns: ["tina", "sanity", "contentful"]
        """
        supporting_providers = []

        for provider_name in cls._providers.keys():
            try:
                metadata = cls.get_provider_metadata(provider_name)
                features = metadata.get("features", [])
                if feature in features:
                    supporting_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return supporting_providers

    @classmethod
    def get_providers_by_cost_range(cls, max_monthly_cost: float) -> List[str]:
        """
        Get CMS providers within a specific monthly cost range.

        Args:
            max_monthly_cost: Maximum acceptable monthly cost

        Returns:
            List of provider names within the cost range

        Example:
            budget_cms = CMSProviderFactory.get_providers_by_cost_range(50)
            # Returns providers with monthly costs under $50
        """
        affordable_providers = []

        for provider_name in cls._providers.keys():
            try:
                metadata = cls.get_provider_metadata(provider_name)
                cost_range = metadata.get("monthly_cost_range", [0, 0])
                min_cost = cost_range[0] if cost_range else 0

                if min_cost <= max_monthly_cost:
                    affordable_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return affordable_providers

    @classmethod
    def get_providers_by_auth_method(cls, auth_method: CMSAuthMethod) -> List[str]:
        """
        Get CMS providers that use a specific authentication method.

        Args:
            auth_method: Authentication method (github_oauth, api_key, etc.)

        Returns:
            List of provider names using the auth method

        Example:
            github_cms = CMSProviderFactory.get_providers_by_auth_method(CMSAuthMethod.GITHUB_OAUTH)
            # Returns: ["decap", "forestry"]
        """
        matching_providers = []

        for provider_name in cls._providers.keys():
            try:
                provider_class = cls._providers[provider_name]
                temp_provider = provider_class({})
                if temp_provider.get_auth_method() == auth_method:
                    matching_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return matching_providers

    @classmethod
    def get_providers_compatible_with_ssg(cls, ssg_engine: str) -> List[str]:
        """
        Get CMS providers compatible with a specific SSG engine.

        Args:
            ssg_engine: SSG engine name (e.g., "eleventy", "astro", "gatsby")

        Returns:
            List of compatible CMS provider names

        Example:
            astro_cms = CMSProviderFactory.get_providers_compatible_with_ssg("astro")
            # Returns CMS providers that work well with Astro
        """
        compatible_providers = []

        for provider_name in cls._providers.keys():
            try:
                provider_class = cls._providers[provider_name]
                temp_provider = provider_class({})
                compatible_ssgs = temp_provider.get_ssg_compatibility()
                if ssg_engine in compatible_ssgs:
                    compatible_providers.append(provider_name)
            except Exception:
                # Skip providers that can't provide metadata
                continue

        return compatible_providers

    @classmethod
    def get_cms_recommendations(
        cls,
        ssg_engine: str,
        content_volume: str = "medium",
        budget_limit: Optional[float] = None,
        required_features: Optional[List[str]] = None,
        technical_skill: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Get recommended CMS providers based on requirements.

        Args:
            ssg_engine: Target SSG engine
            content_volume: Expected content volume ("small", "medium", "large")
            budget_limit: Maximum monthly budget (None for no limit)
            required_features: List of required features
            technical_skill: Technical skill level ("low", "medium", "high")

        Returns:
            List of recommendations sorted by suitability

        Example:
            recommendations = CMSProviderFactory.get_cms_recommendations(
                ssg_engine="astro",
                content_volume="medium",
                budget_limit=75,
                required_features=["visual_editor"],
                technical_skill="low"
            )
        """
        required_features = required_features or []
        all_metadata = cls.get_all_providers_metadata()
        recommendations = []

        for provider_name, metadata in all_metadata.items():
            if "error" in metadata:
                continue

            # Check SSG compatibility
            try:
                provider_class = cls._providers[provider_name]
                temp_provider = provider_class({})
                compatible_ssgs = temp_provider.get_ssg_compatibility()
                if ssg_engine not in compatible_ssgs:
                    continue
            except Exception:
                continue

            # Check feature requirements
            features = metadata.get("features", [])
            if not all(feature in features for feature in required_features):
                continue

            # Check budget constraint
            if budget_limit is not None:
                cost_range = metadata.get("monthly_cost_range", [0, 0])
                min_cost = cost_range[0] if cost_range else 0
                if min_cost > budget_limit:
                    continue

            # Calculate suitability score based on requirements
            score = cls._calculate_cms_suitability_score(
                metadata, content_volume, technical_skill, required_features
            )

            # Estimate monthly cost based on content volume
            try:
                temp_provider = provider_class({})
                cost_estimate = temp_provider.estimate_monthly_cost(content_volume)
                estimated_cost = cost_estimate["total_estimated"]
            except Exception:
                estimated_cost = metadata.get("monthly_cost_range", [0, 0])[0]

            recommendations.append({
                "provider": provider_name,
                "suitability_score": score,
                "estimated_monthly_cost": estimated_cost,
                "cms_type": metadata.get("cms_type", "unknown"),
                "setup_complexity": metadata.get("setup_complexity", "medium"),
                "features": features,
                "metadata": metadata
            })

        # Sort by suitability score (descending) then by cost (ascending)
        recommendations.sort(key=lambda x: (-x["suitability_score"], x["estimated_monthly_cost"]))

        # Add recommendation reasoning
        for i, rec in enumerate(recommendations):
            rec["ranking"] = i + 1
            rec["reason"] = cls._get_cms_recommendation_reason(
                rec, ssg_engine, content_volume, technical_skill
            )

        return recommendations

    @classmethod
    def _calculate_cms_suitability_score(
        cls,
        metadata: Dict[str, Any],
        content_volume: str,
        technical_skill: str,
        required_features: List[str]
    ) -> float:
        """Calculate suitability score for CMS recommendation"""
        score = 0.0

        # Base score for setup complexity vs technical skill
        complexity = metadata.get("setup_complexity", "medium")
        complexity_scores = {
            ("low", "low"): 3.0,      # Easy CMS for non-technical users
            ("low", "medium"): 2.5,   # Easy CMS for medium users
            ("low", "high"): 2.0,     # Easy CMS for technical users (less optimal)
            ("medium", "low"): 1.0,   # Medium CMS for non-technical (challenging)
            ("medium", "medium"): 3.0, # Medium CMS for medium users (perfect match)
            ("medium", "high"): 2.5,  # Medium CMS for technical users
            ("high", "low"): 0.5,     # Complex CMS for non-technical (poor match)
            ("high", "medium"): 2.0,  # Complex CMS for medium users
            ("high", "high"): 3.0     # Complex CMS for technical users (perfect match)
        }
        score += complexity_scores.get((complexity, technical_skill), 1.5)

        # Bonus for matching content volume needs
        features = metadata.get("features", [])
        if content_volume == "large" and "api_access" in features:
            score += 1.0
        if content_volume == "small" and "git_based" in str(metadata.get("cms_type", "")):
            score += 0.5

        # Feature match bonus
        feature_match_ratio = len([f for f in required_features if f in features]) / max(len(required_features), 1)
        score += feature_match_ratio * 2.0

        # Cost efficiency bonus (free/low-cost solutions get points)
        cost_range = metadata.get("monthly_cost_range", [0, 0])
        if cost_range[0] == 0:  # Free tier available
            score += 1.0
        elif cost_range[0] < 30:  # Low cost
            score += 0.5

        return round(score, 2)

    @classmethod
    def _get_cms_recommendation_reason(
        cls,
        recommendation: Dict[str, Any],
        ssg_engine: str,
        content_volume: str,
        technical_skill: str
    ) -> str:
        """Generate human-readable recommendation reason"""
        provider = recommendation["provider"]
        cms_type = recommendation["cms_type"]
        complexity = recommendation["setup_complexity"]
        cost = recommendation["estimated_monthly_cost"]

        reasons = []

        # Cost reasoning
        if cost == 0:
            reasons.append("free to use")
        elif cost < 50:
            reasons.append(f"cost-effective at ${cost}/month")
        else:
            reasons.append(f"feature-rich at ${cost}/month")

        # Technical skill matching
        skill_match = {
            ("low", "low"): "beginner-friendly setup",
            ("medium", "medium"): "balanced complexity for your skill level",
            ("high", "high"): "advanced features for technical users"
        }
        if (complexity, technical_skill) in skill_match:
            reasons.append(skill_match[(complexity, technical_skill)])

        # CMS type benefits
        cms_benefits = {
            "git_based": "git-based workflow you can control",
            "api_based": "powerful API and scalability",
            "hybrid": "best of both git and API approaches"
        }
        if cms_type in cms_benefits:
            reasons.append(cms_benefits[cms_type])

        reason_text = f"{provider.title()} is recommended because it offers " + ", ".join(reasons)
        return f"{reason_text}, making it ideal for {ssg_engine} sites with {content_volume} content volume."

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[CMSProvider]) -> None:
        """
        Register a new CMS provider.

        This method allows for dynamic provider registration,
        useful for plugins or custom integrations.

        Args:
            name: Provider name
            provider_class: Provider class that extends CMSProvider
        """
        if not issubclass(provider_class, CMSProvider):
            raise ValueError(f"Provider class must extend CMSProvider")

        cls._providers[name] = provider_class

    @classmethod
    def is_provider_supported(cls, provider_name: str) -> bool:
        """
        Check if a CMS provider is supported.

        Args:
            provider_name: Name of the provider to check

        Returns:
            True if provider is supported
        """
        return provider_name in cls._providers

    @classmethod
    def get_provider_integration_complexity(cls, provider_name: str, ssg_engine: str) -> Dict[str, Any]:
        """
        Get integration complexity information for a specific provider/SSG combination.

        Args:
            provider_name: CMS provider name
            ssg_engine: SSG engine name

        Returns:
            Dictionary with complexity information

        Example:
            complexity = CMSProviderFactory.get_provider_integration_complexity("sanity", "astro")
            # Returns: {"estimated_hours": 4, "complexity": "medium", "dependencies": [...]}
        """
        if not cls.is_provider_supported(provider_name):
            raise ValueError(f"Unsupported CMS provider: {provider_name}")

        try:
            provider_class = cls._providers[provider_name]
            temp_provider = provider_class({})

            # Get base complexity
            metadata = temp_provider.get_configuration_metadata()
            base_complexity = metadata.get("setup_complexity", "medium")

            # Get SSG-specific dependencies
            dependencies = temp_provider.get_required_dependencies(ssg_engine)

            # Estimate hours based on complexity and dependencies
            complexity_hours = {
                "low": 2,
                "medium": 4,
                "high": 8
            }

            base_hours = complexity_hours.get(base_complexity, 4)
            dependency_hours = len(dependencies) * 0.5  # 30 minutes per dependency

            return {
                "provider": provider_name,
                "ssg_engine": ssg_engine,
                "estimated_hours": base_hours + dependency_hours,
                "complexity": base_complexity,
                "dependencies": dependencies,
                "cms_type": temp_provider.get_cms_type(),
                "auth_method": temp_provider.get_auth_method()
            }

        except Exception as e:
            return {
                "provider": provider_name,
                "ssg_engine": ssg_engine,
                "error": f"Could not determine complexity: {str(e)}"
            }

    @classmethod
    def compare_providers(cls, provider_names: List[str], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare multiple CMS providers across different criteria.

        Args:
            provider_names: List of provider names to compare
            criteria: Comparison criteria (cost, features, complexity, etc.)

        Returns:
            Comparison matrix with scores and recommendations

        Example:
            comparison = CMSProviderFactory.compare_providers(
                ["decap", "sanity", "contentful"],
                {"max_cost": 100, "required_features": ["visual_editor"]}
            )
        """
        comparison = {
            "providers": {},
            "summary": {},
            "recommendation": None
        }

        for provider_name in provider_names:
            if not cls.is_provider_supported(provider_name):
                comparison["providers"][provider_name] = {"error": "Provider not supported"}
                continue

            try:
                metadata = cls.get_provider_metadata(provider_name)
                provider_class = cls._providers[provider_name]
                temp_provider = provider_class({})

                # Calculate scores based on criteria
                scores = {}

                # Cost score (lower cost = higher score)
                max_cost = criteria.get("max_cost", 1000)
                provider_cost = metadata.get("monthly_cost_range", [0, 0])[1]
                scores["cost"] = max(0, (max_cost - provider_cost) / max_cost * 10)

                # Feature score
                required_features = criteria.get("required_features", [])
                provider_features = metadata.get("features", [])
                feature_match = len([f for f in required_features if f in provider_features])
                scores["features"] = (feature_match / max(len(required_features), 1)) * 10

                # Complexity score (matches user skill level)
                user_skill = criteria.get("technical_skill", "medium")
                complexity = metadata.get("setup_complexity", "medium")
                complexity_match = {
                    ("low", "low"): 10,
                    ("medium", "medium"): 10,
                    ("high", "high"): 10,
                    ("low", "medium"): 8,
                    ("medium", "high"): 8,
                    ("high", "medium"): 6,
                    ("low", "high"): 5,
                    ("medium", "low"): 4,
                    ("high", "low"): 2
                }
                scores["complexity"] = complexity_match.get((complexity, user_skill), 5)

                # Overall score
                scores["overall"] = sum(scores.values()) / len(scores)

                comparison["providers"][provider_name] = {
                    "metadata": metadata,
                    "scores": scores,
                    "cms_type": temp_provider.get_cms_type(),
                    "auth_method": temp_provider.get_auth_method()
                }

            except Exception as e:
                comparison["providers"][provider_name] = {"error": str(e)}

        # Determine best recommendation
        valid_providers = {k: v for k, v in comparison["providers"].items() if "error" not in v}
        if valid_providers:
            best_provider = max(valid_providers.items(), key=lambda x: x[1]["scores"]["overall"])
            comparison["recommendation"] = {
                "provider": best_provider[0],
                "score": best_provider[1]["scores"]["overall"],
                "reason": f"Best overall match with {best_provider[1]['scores']['overall']:.1f}/10 score"
            }

        return comparison

    @classmethod
    def _load_provider_class(cls, provider_name: str) -> Type[CMSProvider]:
        """Lazy load provider class to avoid circular imports"""
        if provider_name == "decap":
            from .providers.decap_cms import DecapCMSProvider
            return DecapCMSProvider
        elif provider_name == "tina":
            from .providers.tina_cms import TinaCMSProvider
            return TinaCMSProvider
        else:
            raise ValueError(f"Provider '{provider_name}' not implemented yet")