#!/usr/bin/env python3
"""
Extract current STACK_METADATA and convert to JSON registry format

This script reads the PlatformStackFactory.STACK_METADATA and converts it
to the structured JSON format for the S3-based Provider Metadata Registry.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Set
import importlib.util

# Add the project root to Python path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.factories.platform_stack_factory import PlatformStackFactory
    FACTORY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import PlatformStackFactory: {e}")
    FACTORY_AVAILABLE = False

# Output directory structure
OUTPUT_DIR = Path(__file__).parent / "output"
PROVIDERS_DIR = OUTPUT_DIR / "providers"
STACKS_DIR = OUTPUT_DIR / "stacks"

class MetadataExtractor:
    """Extract and convert STACK_METADATA to JSON registry format"""

    def __init__(self):
        self.current_time = datetime.now(timezone.utc).isoformat()
        self.schema_version = "1.0.0"

        # Create output directories
        for dir_path in [OUTPUT_DIR, PROVIDERS_DIR, STACKS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create provider and stack category directories
        (PROVIDERS_DIR / "cms").mkdir(exist_ok=True)
        (PROVIDERS_DIR / "ecommerce").mkdir(exist_ok=True)
        (PROVIDERS_DIR / "ssg").mkdir(exist_ok=True)

        (STACKS_DIR / "templates").mkdir(exist_ok=True)
        (STACKS_DIR / "foundation").mkdir(exist_ok=True)
        (STACKS_DIR / "cms-tiers").mkdir(exist_ok=True)
        (STACKS_DIR / "ecommerce-tiers").mkdir(exist_ok=True)
        (STACKS_DIR / "composed").mkdir(exist_ok=True)

    def extract_all_metadata(self) -> Dict[str, Any]:
        """Extract all metadata and generate JSON files"""

        if not FACTORY_AVAILABLE:
            print("❌ PlatformStackFactory not available. Cannot extract metadata.")
            return {}

        print("🔍 Extracting metadata from PlatformStackFactory...")

        # Get the current STACK_METADATA
        stack_metadata = PlatformStackFactory.STACK_METADATA
        print(f"✅ Found {len(stack_metadata)} stack entries")

        # Process each entry
        providers_found = {
            "cms": set(),
            "ecommerce": set(),
            "ssg": set()
        }

        stacks_found = {
            "templates": [],
            "foundation": [],
            "cms-tiers": [],
            "ecommerce-tiers": [],
            "composed": []
        }

        for stack_type, metadata in stack_metadata.items():
            print(f"\n📋 Processing: {stack_type}")

            # Convert stack metadata
            stack_json = self._convert_stack_metadata(stack_type, metadata)

            # Determine output category and file
            category = self._get_stack_category(metadata.get("category", ""))
            stack_file = STACKS_DIR / category / f"{stack_type}.json"

            # Write stack JSON
            with open(stack_file, 'w') as f:
                json.dump(stack_json, f, indent=2, sort_keys=True)

            stacks_found[category].append(stack_type)
            print(f"  ✅ Generated: {stack_file}")

            # Extract provider information
            self._extract_providers_from_stack(metadata, providers_found)

        # Generate provider JSON files
        self._generate_provider_files(providers_found)

        # Generate manifest
        manifest = self._generate_manifest(providers_found, stacks_found)

        return {
            "providers": dict(providers_found),
            "stacks": stacks_found,
            "manifest": manifest
        }

    def _map_complexity_level(self, original_complexity: str) -> str:
        """Map original complexity levels to schema-compliant values"""
        complexity_mapping = {
            "low": "low_to_medium",
            "medium": "medium_to_high",
            "high": "high",
            "enterprise": "enterprise",
            # Handle existing schema-compliant values
            "low_to_medium": "low_to_medium",
            "medium_to_high": "medium_to_high"
        }
        return complexity_mapping.get(original_complexity, "medium_to_high")

    def _convert_stack_metadata(self, stack_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert single stack metadata to JSON schema format"""

        base_fields = {
            "stack_type": stack_type,
            "tier_name": metadata.get("tier_name", ""),
            "category": metadata.get("category", ""),
            "monthly_cost_range": metadata.get("monthly_cost_range", [0, 0]),
            "setup_cost_range": metadata.get("setup_cost_range", [0, 0]),
            "target_market": metadata.get("target_market", []),
            "best_for": metadata.get("best_for", ""),
            "complexity_level": self._map_complexity_level(metadata.get("complexity_level", "medium_to_high")),
            "key_features": metadata.get("key_features", []),
            "hosting_pattern": metadata.get("hosting_pattern", "aws_optimized"),
            "performance_tier": metadata.get("performance_tier", "optimized"),
            "last_updated": self.current_time,
            "schema_version": self.schema_version
        }

        # Add optional fields if present
        optional_fields = [
            "ssg_engine", "ssg_engine_options", "cms_provider", "ecommerce_provider",
            "cms_type", "template_variants", "provider_combinations"
        ]

        for field in optional_fields:
            if field in metadata:
                base_fields[field] = metadata[field]

        # Convert provider_type to ecommerce_type if present
        if "provider_type" in metadata and metadata["category"] == "ecommerce_tier_service":
            base_fields["ecommerce_type"] = metadata["provider_type"]

        return base_fields

    def _get_stack_category(self, category: str) -> str:
        """Map metadata category to output directory"""
        category_mapping = {
            "ssg_template_business_service": "templates",
            "foundation_ssg_service": "foundation",
            "cms_tier_service": "cms-tiers",
            "ecommerce_tier_service": "ecommerce-tiers",
            "composed_service": "composed"
        }
        return category_mapping.get(category, "templates")

    def _extract_providers_from_stack(self, metadata: Dict[str, Any], providers_found: Dict[str, Set]):
        """Extract provider information from stack metadata"""

        # Extract CMS providers
        if "cms_provider" in metadata:
            providers_found["cms"].add(metadata["cms_provider"])

        # Extract E-commerce providers
        if "ecommerce_provider" in metadata:
            providers_found["ecommerce"].add(metadata["ecommerce_provider"])

        # Extract SSG engines
        if "ssg_engine" in metadata:
            providers_found["ssg"].add(metadata["ssg_engine"])

        if "ssg_engine_options" in metadata:
            for engine in metadata["ssg_engine_options"]:
                providers_found["ssg"].add(engine)

    def _generate_provider_files(self, providers_found: Dict[str, Set]):
        """Generate individual provider JSON files"""

        print("\n🏗️  Generating provider files...")

        # CMS Providers
        cms_providers = {
            "decap": {
                "display_name": "Decap CMS",
                "cms_type": "git_based",
                "tier_name": "Decap CMS - Free Git-Based Content Management",
                "best_for": "Budget-friendly content management with full git workflow control",
                "key_features": ["free_cms", "git_workflow", "markdown_editing", "github_oauth", "version_control", "no_vendor_lock_in"]
            },
            "sanity": {
                "display_name": "Sanity CMS",
                "cms_type": "api_based",
                "tier_name": "Sanity CMS - Structured Content with Real-Time APIs",
                "best_for": "Professional structured content management with real-time APIs and advanced querying",
                "key_features": ["structured_content", "groq_querying", "real_time_apis", "content_validation", "advanced_media", "webhook_automation"]
            },
            "tina": {
                "display_name": "Tina CMS",
                "cms_type": "hybrid",
                "tier_name": "Tina CMS - Visual Editing with Git Workflow",
                "best_for": "Visual content editing with git-based storage and real-time collaboration",
                "key_features": ["visual_editing", "real_time_preview", "git_workflow", "react_based", "graphql_api", "collaboration"]
            },
            "contentful": {
                "display_name": "Contentful CMS",
                "cms_type": "api_based",
                "tier_name": "Contentful CMS - Enterprise Content Management with Advanced Workflows",
                "best_for": "Enterprise-grade content management with advanced workflows, team collaboration, and multi-language support",
                "key_features": ["enterprise_workflows", "team_collaboration", "multi_language_support", "content_versioning", "scheduled_publishing", "advanced_permissions"]
            }
        }

        for provider_name in providers_found["cms"]:
            if provider_name in cms_providers:
                provider_data = self._create_provider_json(
                    provider_name, "cms", cms_providers[provider_name]
                )

                provider_file = PROVIDERS_DIR / "cms" / f"{provider_name}.json"
                with open(provider_file, 'w') as f:
                    json.dump(provider_data, f, indent=2, sort_keys=True)
                print(f"  ✅ Generated: {provider_file}")

        # E-commerce Providers
        ecommerce_providers = {
            "snipcart": {
                "display_name": "Snipcart",
                "ecommerce_type": "simple_integration",
                "tier_name": "Snipcart E-commerce - Simple E-commerce Integration",
                "best_for": "Budget-friendly e-commerce with fast setup",
                "key_features": ["simple_integration", "secure_checkout", "inventory_management", "basic_analytics"]
            },
            "foxy": {
                "display_name": "Foxy",
                "ecommerce_type": "advanced_platform",
                "tier_name": "Foxy E-commerce - Advanced E-commerce Features",
                "best_for": "Advanced features, subscriptions, complex workflows",
                "key_features": ["subscription_management", "advanced_checkout", "webhook_automation", "complex_pricing"]
            },
            "shopify_basic": {
                "display_name": "Shopify Basic",
                "ecommerce_type": "hosted_platform",
                "tier_name": "Shopify Basic - Performance E-commerce with Flexible SSG",
                "best_for": "Enterprise performance at small business prices - 80-90% cost reduction vs agencies",
                "key_features": ["shopify_storefront_api", "real_time_sync", "webhook_automation", "performance_optimization"]
            }
        }

        for provider_name in providers_found["ecommerce"]:
            if provider_name in ecommerce_providers:
                provider_data = self._create_provider_json(
                    provider_name, "ecommerce", ecommerce_providers[provider_name]
                )

                provider_file = PROVIDERS_DIR / "ecommerce" / f"{provider_name}.json"
                with open(provider_file, 'w') as f:
                    json.dump(provider_data, f, indent=2, sort_keys=True)
                print(f"  ✅ Generated: {provider_file}")

        # SSG Engines
        ssg_engines = {
            "hugo": {
                "display_name": "Hugo",
                "tier_name": "Hugo - Ultra-Fast Static Site Generator",
                "best_for": "Ultra-fast static sites with complex content relationships and technical documentation",
                "language": "go",
                "ecosystem": "go_templates",
                "build_speed": "fastest",
                "key_features": ["ultra_fast_builds", "technical_documentation", "multi_language", "complex_taxonomies", "performance_optimization"]
            },
            "gatsby": {
                "display_name": "Gatsby",
                "tier_name": "Gatsby - React Ecosystem with GraphQL",
                "best_for": "React-based static sites with GraphQL data layer and component architecture",
                "language": "javascript",
                "ecosystem": "react",
                "build_speed": "medium",
                "key_features": ["react_components", "graphql_data_layer", "plugin_ecosystem", "image_optimization", "component_reusability"]
            },
            "nextjs": {
                "display_name": "Next.js",
                "tier_name": "Next.js - Enterprise Full-Stack React Foundation",
                "best_for": "Enterprise-ready React applications with static export and full-stack growth path",
                "language": "javascript",
                "ecosystem": "react",
                "build_speed": "medium",
                "key_features": ["enterprise_patterns", "typescript_first", "api_routes_ready", "static_export", "full_stack_growth"]
            },
            "nuxt": {
                "display_name": "Nuxt.js",
                "tier_name": "Nuxt - Vue Ecosystem with Modern Patterns",
                "best_for": "Modern Vue 3 applications with Composition API and progressive enhancement features",
                "language": "javascript",
                "ecosystem": "vue",
                "build_speed": "medium",
                "key_features": ["vue_3_composition_api", "progressive_enhancement", "pinia_state_management", "modern_patterns", "vue_ecosystem"]
            },
            "eleventy": {
                "display_name": "Eleventy",
                "tier_name": "Eleventy - Simple and Flexible Static Site Generator",
                "best_for": "Simple, flexible static sites with minimal configuration",
                "language": "javascript",
                "ecosystem": "javascript",
                "build_speed": "fast",
                "key_features": ["simple_setup", "flexible_templating", "minimal_config", "fast_builds", "framework_agnostic"]
            },
            "astro": {
                "display_name": "Astro",
                "tier_name": "Astro - Modern High-Performance Framework",
                "best_for": "Modern sites requiring interactive features with optimal performance",
                "language": "javascript",
                "ecosystem": "multi_framework",
                "build_speed": "fast",
                "key_features": ["component_islands", "partial_hydration", "framework_agnostic", "performance_optimized"]
            },
            "jekyll": {
                "display_name": "Jekyll",
                "tier_name": "Jekyll - GitHub Pages Compatible Static Site Generator",
                "best_for": "Technical sites with Git-based workflows and GitHub Pages compatibility",
                "language": "ruby",
                "ecosystem": "ruby",
                "build_speed": "medium",
                "key_features": ["github_pages_compatible", "git_workflow", "theme_system", "dual_hosting"]
            }
        }

        for provider_name in providers_found["ssg"]:
            if provider_name in ssg_engines:
                provider_data = self._create_ssg_provider_json(
                    provider_name, ssg_engines[provider_name]
                )

                provider_file = PROVIDERS_DIR / "ssg" / f"{provider_name}.json"
                with open(provider_file, 'w') as f:
                    json.dump(provider_data, f, indent=2, sort_keys=True)
                print(f"  ✅ Generated: {provider_file}")

    def _create_provider_json(self, name: str, provider_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create provider JSON with all required fields"""

        # Base cost estimates (simplified for extraction)
        cost_estimates = {
            "decap": ([50, 75], [960, 2640]),
            "sanity": ([65, 280], [1440, 3360]),
            "tina": ([60, 125], [1200, 2880]),
            "contentful": ([75, 500], [2100, 4800]),
            "snipcart": ([85, 125], [960, 2640]),
            "foxy": ([100, 150], [1200, 3000]),
            "shopify_basic": ([75, 125], [1600, 3200])
        }

        monthly_cost, setup_cost = cost_estimates.get(name, ([50, 100], [1000, 2000]))

        return {
            "provider_name": name,
            "provider_type": provider_type,
            "display_name": details["display_name"],
            "tier_name": details.get("tier_name", details["display_name"]),
            "category": f"{provider_type}_tier_service",
            "monthly_cost_range": monthly_cost,
            "setup_cost_range": setup_cost,
            "target_market": ["small_businesses", "agencies", "developers"],
            "best_for": details["best_for"],
            "complexity_level": "medium_to_high",
            "key_features": details["key_features"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "last_updated": self.current_time,
            "schema_version": self.schema_version,
            f"{provider_type}_type": details.get(f"{provider_type}_type", "api_based")
        }

    def _create_ssg_provider_json(self, name: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create SSG provider JSON with SSG-specific fields"""

        return {
            "provider_name": name,
            "provider_type": "ssg",
            "display_name": details["display_name"],
            "tier_name": details.get("tier_name", details["display_name"]),
            "category": "ssg_template_business_service",
            "monthly_cost_range": [75, 115],
            "setup_cost_range": [1000, 2500],
            "target_market": ["developers", "technical_teams", "agencies"],
            "best_for": details["best_for"],
            "complexity_level": "medium_to_high",
            "key_features": details["key_features"],
            "hosting_pattern": "aws_optimized",
            "performance_tier": "optimized",
            "last_updated": self.current_time,
            "schema_version": self.schema_version,
            "ssg_engine": name,
            "language": details["language"],
            "ecosystem": details["ecosystem"],
            "build_speed": details["build_speed"]
        }

    def _generate_manifest(self, providers_found: Dict[str, Set], stacks_found: Dict[str, List]) -> Dict[str, Any]:
        """Generate the registry manifest"""

        # Convert sets to sorted lists
        providers_lists = {
            category: sorted(list(providers))
            for category, providers in providers_found.items()
        }

        manifest = {
            "schema_version": self.schema_version,
            "last_updated": self.current_time,
            "providers": providers_lists,
            "stacks": stacks_found,
            "cdn_urls": {
                "base": "https://registry.blackwell.dev",
                "manifest": "https://registry.blackwell.dev/manifest.json"
            },
            "metadata": {
                "total_providers": sum(len(providers) for providers in providers_lists.values()),
                "total_stacks": sum(len(stacks) for stacks in stacks_found.values()),
                "registry_version": "1.0.0"
            }
        }

        # Write manifest file
        manifest_file = OUTPUT_DIR / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        print(f"\n📄 Generated manifest: {manifest_file}")
        return manifest


def main():
    """Main extraction function"""
    print("🚀 Starting Provider Metadata Registry extraction...")
    print("=" * 60)

    extractor = MetadataExtractor()

    try:
        results = extractor.extract_all_metadata()

        print("\n" + "=" * 60)
        print("✅ Extraction completed successfully!")
        print(f"📊 Summary:")
        print(f"   • CMS providers: {len(results['providers']['cms'])}")
        print(f"   • E-commerce providers: {len(results['providers']['ecommerce'])}")
        print(f"   • SSG engines: {len(results['providers']['ssg'])}")
        print(f"   • Total stacks: {sum(len(stacks) for stacks in results['stacks'].values())}")
        print(f"\n📁 Output directory: {OUTPUT_DIR}")
        print(f"📄 Next steps:")
        print(f"   1. Review generated JSON files")
        print(f"   2. Run validation: python validate_registry.py")
        print(f"   3. Upload to S3: python deploy_registry.py")

    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()