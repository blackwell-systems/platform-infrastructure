"""
JSON Provider Registry

Lightweight provider discovery and metadata system using JSON files.
This provides fast provider discovery without loading heavy implementation classes,
complementing the existing ProviderAdapterRegistry which handles actual webhook processing.

Design:
- Metadata operations are fast (JSON loading only)
- Implementation loading is lazy (only when actually needed)
- Can be used for CLI tools, dashboards, and discovery systems
- Separates concerns: discovery vs. processing
"""

import json
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Union
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProviderMetadata:
    """Provider metadata loaded from JSON files"""
    provider_id: str
    provider_name: str
    category: str
    tier_name: str
    description: str
    features: List[str]
    supported_ssg_engines: List[str]
    integration_modes: List[str]
    complexity_level: str
    target_market: List[str]
    use_cases: List[str]
    cost_characteristics: Dict[str, Any]
    technical_requirements: Dict[str, Any]
    performance_characteristics: Dict[str, Any]
    implementation_class: str
    provider_class: Optional[str]
    documentation: Dict[str, str]
    compatibility: Dict[str, Any]
    metadata_version: str
    last_updated: str

    # Additional computed properties
    _raw_metadata: Dict[str, Any] = None

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'ProviderMetadata':
        """Create ProviderMetadata from JSON data"""
        return cls(
            provider_id=json_data["provider_id"],
            provider_name=json_data["provider_name"],
            category=json_data["category"],
            tier_name=json_data["tier_name"],
            description=json_data.get("description", ""),
            features=json_data["features"],
            supported_ssg_engines=json_data["supported_ssg_engines"],
            integration_modes=json_data["integration_modes"],
            complexity_level=json_data["complexity_level"],
            target_market=json_data.get("target_market", []),
            use_cases=json_data.get("use_cases", []),
            cost_characteristics=json_data.get("cost_characteristics", {}),
            technical_requirements=json_data.get("technical_requirements", {}),
            performance_characteristics=json_data.get("performance_characteristics", {}),
            implementation_class=json_data["implementation_class"],
            provider_class=json_data.get("provider_class"),
            documentation=json_data.get("documentation", {}),
            compatibility=json_data.get("compatibility", {}),
            metadata_version=json_data.get("metadata_version", "1.0.0"),
            last_updated=json_data.get("last_updated", ""),
            _raw_metadata=json_data
        )

    def supports_ssg_engine(self, ssg_engine: str) -> bool:
        """Check if provider supports specific SSG engine"""
        return ssg_engine in self.supported_ssg_engines

    def supports_integration_mode(self, mode: str) -> bool:
        """Check if provider supports specific integration mode"""
        return mode in self.integration_modes

    def has_feature(self, feature: str) -> bool:
        """Check if provider has specific feature"""
        return feature in self.features

    def get_ssg_compatibility_score(self, ssg_engine: str) -> Optional[int]:
        """Get compatibility score for specific SSG engine"""
        compat = self.compatibility.get("ssg_engine_compatibility", {})
        engine_compat = compat.get(ssg_engine, {})
        return engine_compat.get("compatibility_score")

    def get_ssg_setup_complexity(self, ssg_engine: str) -> Optional[str]:
        """Get setup complexity for specific SSG engine"""
        compat = self.compatibility.get("ssg_engine_compatibility", {})
        engine_compat = compat.get(ssg_engine, {})
        return engine_compat.get("setup_complexity")

    def get_estimated_monthly_cost_range(self) -> tuple[int, int]:
        """Get estimated monthly cost range"""
        cost_range = self.cost_characteristics.get("estimated_monthly_range", {})
        return cost_range.get("min", 0), cost_range.get("max", 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return self._raw_metadata if self._raw_metadata else {}


class JsonProviderRegistry:
    """
    Lightweight provider registry using JSON metadata files.

    Provides fast provider discovery and capability queries without
    loading heavy implementation classes.
    """

    def __init__(self, registry_root: Optional[Path] = None):
        """
        Initialize the JSON provider registry.

        Args:
            registry_root: Path to registry root directory.
                          Defaults to registry/ directory relative to this file.
        """
        if registry_root is None:
            registry_root = Path(__file__).parent

        self.registry_root = Path(registry_root)
        self.providers_path = self.registry_root / "providers"
        self.schema_path = self.registry_root / "schema" / "provider_metadata_schema.json"

        # Cache for loaded metadata
        self._metadata_cache: Dict[str, ProviderMetadata] = {}
        self._cache_loaded = False

    def _ensure_cache_loaded(self) -> None:
        """Ensure metadata cache is loaded"""
        if not self._cache_loaded:
            self._load_all_metadata()
            self._cache_loaded = True

    def _load_all_metadata(self) -> None:
        """Load all provider metadata files into cache"""
        if not self.providers_path.exists():
            logger.warning(f"Providers directory not found: {self.providers_path}")
            return

        # Find all JSON files in providers directory
        for json_file in self.providers_path.rglob("*.json"):
            try:
                with open(json_file) as f:
                    json_data = json.load(f)

                metadata = ProviderMetadata.from_json(json_data)
                self._metadata_cache[metadata.provider_id] = metadata

                logger.debug(f"Loaded metadata for provider: {metadata.provider_id}")

            except Exception as e:
                logger.error(f"Failed to load metadata from {json_file}: {e}")

        logger.info(f"Loaded metadata for {len(self._metadata_cache)} providers")

    def get_provider_metadata(self, provider_id: str) -> Optional[ProviderMetadata]:
        """
        Get metadata for a specific provider.

        Args:
            provider_id: Provider identifier

        Returns:
            ProviderMetadata object or None if not found
        """
        self._ensure_cache_loaded()
        return self._metadata_cache.get(provider_id)

    def list_providers(self,
                      category: Optional[str] = None,
                      feature: Optional[str] = None,
                      ssg_engine: Optional[str] = None,
                      integration_mode: Optional[str] = None) -> List[ProviderMetadata]:
        """
        List providers with optional filtering.

        Args:
            category: Filter by category (cms, ecommerce, etc.)
            feature: Filter by required feature
            ssg_engine: Filter by supported SSG engine
            integration_mode: Filter by supported integration mode

        Returns:
            List of matching ProviderMetadata objects
        """
        self._ensure_cache_loaded()

        providers = list(self._metadata_cache.values())

        # Apply filters
        if category:
            providers = [p for p in providers if p.category == category]

        if feature:
            providers = [p for p in providers if p.has_feature(feature)]

        if ssg_engine:
            providers = [p for p in providers if p.supports_ssg_engine(ssg_engine)]

        if integration_mode:
            providers = [p for p in providers if p.supports_integration_mode(integration_mode)]

        # Sort by provider name
        return sorted(providers, key=lambda p: p.provider_name)

    def list_provider_ids(self, **filters) -> List[str]:
        """List provider IDs with optional filtering"""
        providers = self.list_providers(**filters)
        return [p.provider_id for p in providers]

    def get_providers_by_category(self) -> Dict[str, List[ProviderMetadata]]:
        """Get providers grouped by category"""
        self._ensure_cache_loaded()

        by_category = {}
        for provider in self._metadata_cache.values():
            category = provider.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(provider)

        # Sort within each category
        for category in by_category:
            by_category[category].sort(key=lambda p: p.provider_name)

        return by_category

    def get_supported_features(self, category: Optional[str] = None) -> List[str]:
        """Get all supported features across providers"""
        self._ensure_cache_loaded()

        features = set()
        for provider in self._metadata_cache.values():
            if category is None or provider.category == category:
                features.update(provider.features)

        return sorted(list(features))

    def get_supported_ssg_engines(self, category: Optional[str] = None) -> List[str]:
        """Get all supported SSG engines across providers"""
        self._ensure_cache_loaded()

        engines = set()
        for provider in self._metadata_cache.values():
            if category is None or provider.category == category:
                engines.update(provider.supported_ssg_engines)

        return sorted(list(engines))

    def find_providers_for_requirements(self, requirements: Dict[str, Any]) -> List[ProviderMetadata]:
        """
        Find providers that match specific requirements.

        Args:
            requirements: Dictionary of requirements like:
                {
                    "category": "cms",
                    "features": ["visual_editing", "git_based"],
                    "ssg_engine": "astro",
                    "integration_mode": "event_driven",
                    "max_complexity": "intermediate",
                    "budget_max": 100
                }

        Returns:
            List of matching providers sorted by suitability
        """
        self._ensure_cache_loaded()

        candidates = []

        for provider in self._metadata_cache.values():
            score = 0
            matches = True

            # Required category
            if "category" in requirements:
                if provider.category != requirements["category"]:
                    continue

            # Required features
            required_features = requirements.get("features", [])
            if required_features:
                if not all(provider.has_feature(f) for f in required_features):
                    continue
                score += len(required_features) * 10

            # Required SSG engine
            if "ssg_engine" in requirements:
                if not provider.supports_ssg_engine(requirements["ssg_engine"]):
                    continue
                score += 20

            # Required integration mode
            if "integration_mode" in requirements:
                if not provider.supports_integration_mode(requirements["integration_mode"]):
                    continue
                score += 15

            # Complexity preference
            max_complexity = requirements.get("max_complexity")
            if max_complexity:
                complexity_scores = {"simple": 3, "intermediate": 2, "advanced": 1}
                provider_complexity = complexity_scores.get(provider.complexity_level, 0)
                max_allowed = complexity_scores.get(max_complexity, 0)

                if provider_complexity > max_allowed:
                    continue

                score += (4 - provider_complexity) * 5

            # Budget consideration
            budget_max = requirements.get("budget_max")
            if budget_max:
                min_cost, max_cost = provider.get_estimated_monthly_cost_range()
                if min_cost > budget_max:
                    continue
                if max_cost <= budget_max:
                    score += 10

            candidates.append((provider, score))

        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [provider for provider, score in candidates]

    def get_implementation_class(self, provider_id: str) -> Optional[Type]:
        """
        Dynamically load and return the implementation class for a provider.

        This is the "heavy" operation that loads actual CDK stack classes.

        Args:
            provider_id: Provider identifier

        Returns:
            Implementation class or None if not found/loadable
        """
        metadata = self.get_provider_metadata(provider_id)
        if not metadata or not metadata.implementation_class:
            return None

        try:
            module_path, class_name = metadata.implementation_class.rsplit('.', 1)
            module = importlib.import_module(module_path)
            implementation_class = getattr(module, class_name)

            logger.info(f"Loaded implementation class for {provider_id}: {metadata.implementation_class}")
            return implementation_class

        except Exception as e:
            logger.error(f"Failed to load implementation class for {provider_id}: {e}")
            return None

    def get_provider_class(self, provider_id: str) -> Optional[Type]:
        """
        Dynamically load and return the provider class for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Provider class or None if not found/loadable
        """
        metadata = self.get_provider_metadata(provider_id)
        if not metadata or not metadata.provider_class:
            return None

        try:
            module_path, class_name = metadata.provider_class.rsplit('.', 1)
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)

            logger.info(f"Loaded provider class for {provider_id}: {metadata.provider_class}")
            return provider_class

        except Exception as e:
            logger.error(f"Failed to load provider class for {provider_id}: {e}")
            return None

    def refresh_cache(self) -> None:
        """Refresh the metadata cache by reloading from files"""
        self._metadata_cache.clear()
        self._cache_loaded = False
        self._ensure_cache_loaded()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self._ensure_cache_loaded()

        return {
            "total_providers": len(self._metadata_cache),
            "providers_by_category": {
                category: len(providers)
                for category, providers in self.get_providers_by_category().items()
            },
            "cache_loaded": self._cache_loaded,
            "registry_root": str(self.registry_root)
        }


# Global registry instance
json_provider_registry = JsonProviderRegistry()


# CLI-friendly functions
def list_cms_providers() -> List[str]:
    """List all CMS provider IDs"""
    return json_provider_registry.list_provider_ids(category="cms")


def list_ecommerce_providers() -> List[str]:
    """List all e-commerce provider IDs"""
    return json_provider_registry.list_provider_ids(category="ecommerce")


def get_provider_info(provider_id: str) -> Optional[Dict[str, Any]]:
    """Get provider information as dictionary"""
    metadata = json_provider_registry.get_provider_metadata(provider_id)
    return metadata.to_dict() if metadata else None


def find_providers_with_feature(feature: str) -> List[str]:
    """Find all providers that support a specific feature"""
    return json_provider_registry.list_provider_ids(feature=feature)


def find_providers_for_ssg(ssg_engine: str) -> List[str]:
    """Find all providers that support a specific SSG engine"""
    return json_provider_registry.list_provider_ids(ssg_engine=ssg_engine)


# Example usage
if __name__ == "__main__":
    # Demo the registry
    registry = JsonProviderRegistry()

    print("📋 Available Providers:")
    for category, providers in registry.get_providers_by_category().items():
        print(f"\n{category.upper()}:")
        for provider in providers:
            print(f"  • {provider.provider_name} ({provider.provider_id})")

    print(f"\n🔍 CMS providers supporting visual editing: {find_providers_with_feature('visual_editing')}")
    print(f"⚡ Providers supporting Astro: {find_providers_for_ssg('astro')}")

    # Find providers for specific requirements
    requirements = {
        "category": "cms",
        "features": ["visual_editing"],
        "ssg_engine": "astro",
        "max_complexity": "intermediate"
    }

    matches = registry.find_providers_for_requirements(requirements)
    print(f"\n🎯 Providers matching requirements: {[p.provider_id for p in matches]}")