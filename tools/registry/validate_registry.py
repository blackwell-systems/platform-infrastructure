#!/usr/bin/env python3
"""
Validate Provider Registry JSON files against schemas

This script validates all generated JSON files against their corresponding
JSON schemas to ensure data integrity and compliance before deployment.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import jsonschema
from jsonschema import Draft7Validator

# Paths
TOOL_DIR = Path(__file__).parent
SCHEMAS_DIR = TOOL_DIR / "schemas"
OUTPUT_DIR = TOOL_DIR / "output"

class RegistryValidator:
    """Validate provider registry JSON files against schemas"""

    def __init__(self):
        self.schemas = self.load_schemas()
        self.errors = []
        self.warnings = []

    def load_schemas(self) -> Dict[str, Any]:
        """Load all JSON schemas"""
        schemas = {}

        schema_files = {
            "manifest": SCHEMAS_DIR / "manifest.schema.json",
            "provider": SCHEMAS_DIR / "provider.schema.json",
            "stack": SCHEMAS_DIR / "stack.schema.json"
        }

        for name, path in schema_files.items():
            if path.exists():
                with open(path, 'r') as f:
                    schemas[name] = json.load(f)
                print(f"✅ Loaded schema: {name}")
            else:
                print(f"❌ Schema not found: {path}")
                sys.exit(1)

        return schemas

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Validate all registry files"""
        print("\n🔍 Starting registry validation...")
        print("=" * 50)

        success = True

        # Validate manifest
        if not self.validate_manifest():
            success = False

        # Validate providers
        if not self.validate_providers():
            success = False

        # Validate stacks
        if not self.validate_stacks():
            success = False

        # Cross-reference validation
        if not self.validate_cross_references():
            success = False

        return success, self.errors, self.warnings

    def validate_manifest(self) -> bool:
        """Validate manifest.json"""
        print("\n📄 Validating manifest.json...")

        manifest_file = OUTPUT_DIR / "manifest.json"
        if not manifest_file.exists():
            self.errors.append("manifest.json not found")
            return False

        try:
            with open(manifest_file, 'r') as f:
                manifest_data = json.load(f)

            # Validate against schema
            validator = Draft7Validator(self.schemas["manifest"])
            errors = list(validator.iter_errors(manifest_data))

            if errors:
                for error in errors:
                    self.errors.append(f"Manifest schema error: {error.message} at {error.json_path}")
                return False

            print("  ✅ Manifest schema validation passed")

            # Additional manifest validations
            self._validate_manifest_completeness(manifest_data)

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"Manifest JSON parse error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Manifest validation error: {e}")
            return False

    def validate_providers(self) -> bool:
        """Validate all provider JSON files"""
        print("\n👥 Validating provider files...")

        success = True
        providers_dir = OUTPUT_DIR / "providers"

        if not providers_dir.exists():
            self.errors.append("Providers directory not found")
            return False

        provider_categories = ["cms", "ecommerce", "ssg"]
        for category in provider_categories:
            category_dir = providers_dir / category
            if not category_dir.exists():
                self.warnings.append(f"Provider category directory not found: {category}")
                continue

            provider_files = list(category_dir.glob("*.json"))
            print(f"  📂 Validating {len(provider_files)} {category} providers...")

            for provider_file in provider_files:
                if not self._validate_provider_file(provider_file, category):
                    success = False

        return success

    def validate_stacks(self) -> bool:
        """Validate all stack JSON files"""
        print("\n🏗️  Validating stack files...")

        success = True
        stacks_dir = OUTPUT_DIR / "stacks"

        if not stacks_dir.exists():
            self.errors.append("Stacks directory not found")
            return False

        stack_categories = ["templates", "foundation", "cms-tiers", "ecommerce-tiers", "composed"]
        for category in stack_categories:
            category_dir = stacks_dir / category
            if not category_dir.exists():
                self.warnings.append(f"Stack category directory not found: {category}")
                continue

            stack_files = list(category_dir.glob("*.json"))
            print(f"  📂 Validating {len(stack_files)} {category} stacks...")

            for stack_file in stack_files:
                if not self._validate_stack_file(stack_file, category):
                    success = False

        return success

    def _validate_provider_file(self, provider_file: Path, category: str) -> bool:
        """Validate individual provider file"""
        try:
            with open(provider_file, 'r') as f:
                provider_data = json.load(f)

            # Schema validation
            validator = Draft7Validator(self.schemas["provider"])
            errors = list(validator.iter_errors(provider_data))

            if errors:
                for error in errors:
                    self.errors.append(f"Provider {provider_file.stem} schema error: {error.message}")
                return False

            # Business logic validations
            if not self._validate_provider_business_rules(provider_data, provider_file.stem):
                return False

            print(f"    ✅ {provider_file.stem}")
            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"Provider {provider_file.stem} JSON parse error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Provider {provider_file.stem} validation error: {e}")
            return False

    def _validate_stack_file(self, stack_file: Path, category: str) -> bool:
        """Validate individual stack file"""
        try:
            with open(stack_file, 'r') as f:
                stack_data = json.load(f)

            # Schema validation
            validator = Draft7Validator(self.schemas["stack"])
            errors = list(validator.iter_errors(stack_data))

            if errors:
                for error in errors:
                    self.errors.append(f"Stack {stack_file.stem} schema error: {error.message}")
                return False

            # Business logic validations
            if not self._validate_stack_business_rules(stack_data, stack_file.stem):
                return False

            print(f"    ✅ {stack_file.stem}")
            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"Stack {stack_file.stem} JSON parse error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Stack {stack_file.stem} validation error: {e}")
            return False

    def _validate_manifest_completeness(self, manifest_data: Dict[str, Any]):
        """Validate manifest completeness against actual files"""

        # Check if all listed providers have corresponding files
        for category, providers in manifest_data["providers"].items():
            for provider in providers:
                provider_file = OUTPUT_DIR / "providers" / category / f"{provider}.json"
                if not provider_file.exists():
                    self.errors.append(f"Provider file missing: {provider_file}")

        # Check if all listed stacks have corresponding files
        for category, stacks in manifest_data["stacks"].items():
            for stack in stacks:
                stack_file = OUTPUT_DIR / "stacks" / category / f"{stack}.json"
                if not stack_file.exists():
                    self.errors.append(f"Stack file missing: {stack_file}")

    def _validate_provider_business_rules(self, provider_data: Dict[str, Any], provider_name: str) -> bool:
        """Validate provider business logic rules"""

        success = True

        # Cost range validation
        monthly_range = provider_data.get("monthly_cost_range", [])
        setup_range = provider_data.get("setup_cost_range", [])

        if len(monthly_range) == 2 and monthly_range[0] > monthly_range[1]:
            self.errors.append(f"Provider {provider_name}: Monthly cost min > max")
            success = False

        if len(setup_range) == 2 and setup_range[0] > setup_range[1]:
            self.errors.append(f"Provider {provider_name}: Setup cost min > max")
            success = False

        # Provider type consistency
        provider_type = provider_data.get("provider_type")
        category = provider_data.get("category")

        expected_category = f"{provider_type}_tier_service"
        if provider_type in ["cms", "ecommerce"] and category != expected_category:
            self.warnings.append(f"Provider {provider_name}: Category '{category}' doesn't match type '{provider_type}'")

        # Required type-specific fields
        if provider_type == "cms" and "cms_type" not in provider_data:
            self.errors.append(f"CMS provider {provider_name}: Missing cms_type")
            success = False

        if provider_type == "ecommerce" and "ecommerce_type" not in provider_data:
            self.errors.append(f"E-commerce provider {provider_name}: Missing ecommerce_type")
            success = False

        if provider_type == "ssg":
            required_ssg_fields = ["ssg_engine", "language", "ecosystem", "build_speed"]
            for field in required_ssg_fields:
                if field not in provider_data:
                    self.errors.append(f"SSG provider {provider_name}: Missing {field}")
                    success = False

        return success

    def _validate_stack_business_rules(self, stack_data: Dict[str, Any], stack_name: str) -> bool:
        """Validate stack business logic rules"""

        success = True

        # Cost range validation
        monthly_range = stack_data.get("monthly_cost_range", [])
        setup_range = stack_data.get("setup_cost_range", [])

        if len(monthly_range) == 2 and monthly_range[0] > monthly_range[1]:
            self.errors.append(f"Stack {stack_name}: Monthly cost min > max")
            success = False

        if len(setup_range) == 2 and setup_range[0] > setup_range[1]:
            self.errors.append(f"Stack {stack_name}: Setup cost min > max")
            success = False

        # Category-specific validations
        category = stack_data.get("category")

        if category in ["ssg_template_business_service", "foundation_ssg_service"]:
            if "ssg_engine" not in stack_data:
                self.errors.append(f"Template/Foundation stack {stack_name}: Missing ssg_engine")
                success = False

        elif category in ["cms_tier_service", "ecommerce_tier_service"]:
            if "ssg_engine_options" not in stack_data:
                self.errors.append(f"Tier stack {stack_name}: Missing ssg_engine_options")
                success = False

        elif category == "composed_service":
            required_composed_fields = ["ssg_engine_options", "provider_combinations"]
            for field in required_composed_fields:
                if field not in stack_data:
                    self.errors.append(f"Composed stack {stack_name}: Missing {field}")
                    success = False

        return success

    def validate_cross_references(self) -> bool:
        """Validate cross-references between files"""
        print("\n🔗 Validating cross-references...")

        success = True

        try:
            # Load manifest for reference lists
            with open(OUTPUT_DIR / "manifest.json", 'r') as f:
                manifest = json.load(f)

            # Validate stack SSG engine references
            success = self._validate_ssg_references(manifest) and success

            # Validate composed stack provider references
            success = self._validate_provider_references(manifest) and success

            if success:
                print("  ✅ Cross-reference validation passed")

        except Exception as e:
            self.errors.append(f"Cross-reference validation error: {e}")
            success = False

        return success

    def _validate_ssg_references(self, manifest: Dict[str, Any]) -> bool:
        """Validate SSG engine references in stacks"""

        success = True
        available_ssg_engines = set(manifest["providers"]["ssg"])

        # Check all stack files for valid SSG engine references
        stacks_dir = OUTPUT_DIR / "stacks"
        for stack_file in stacks_dir.rglob("*.json"):
            try:
                with open(stack_file, 'r') as f:
                    stack_data = json.load(f)

                # Check fixed SSG engine
                if "ssg_engine" in stack_data:
                    engine = stack_data["ssg_engine"]
                    if engine not in available_ssg_engines:
                        self.warnings.append(f"Stack {stack_file.stem}: References unknown SSG engine '{engine}'")

                # Check SSG engine options
                if "ssg_engine_options" in stack_data:
                    for engine in stack_data["ssg_engine_options"]:
                        if engine not in available_ssg_engines:
                            self.warnings.append(f"Stack {stack_file.stem}: References unknown SSG engine '{engine}' in options")

            except Exception as e:
                self.errors.append(f"Error validating SSG references in {stack_file.stem}: {e}")
                success = False

        return success

    def _validate_provider_references(self, manifest: Dict[str, Any]) -> bool:
        """Validate provider references in composed stacks"""

        success = True
        available_cms = set(manifest["providers"]["cms"])
        available_ecommerce = set(manifest["providers"]["ecommerce"])

        # Check composed stacks for valid provider references
        composed_dir = OUTPUT_DIR / "stacks" / "composed"
        if composed_dir.exists():
            for stack_file in composed_dir.glob("*.json"):
                try:
                    with open(stack_file, 'r') as f:
                        stack_data = json.load(f)

                    # Check CMS provider reference
                    if "cms_provider" in stack_data:
                        provider = stack_data["cms_provider"]
                        if provider not in available_cms:
                            self.warnings.append(f"Composed stack {stack_file.stem}: References unknown CMS provider '{provider}'")

                    # Check e-commerce provider reference
                    if "ecommerce_provider" in stack_data:
                        provider = stack_data["ecommerce_provider"]
                        if provider not in available_ecommerce:
                            self.warnings.append(f"Composed stack {stack_file.stem}: References unknown e-commerce provider '{provider}'")

                except Exception as e:
                    self.errors.append(f"Error validating provider references in {stack_file.stem}: {e}")
                    success = False

        return success


def main():
    """Main validation function"""
    print("🔍 Starting Provider Registry validation...")
    print("=" * 60)

    if not OUTPUT_DIR.exists():
        print(f"❌ Output directory not found: {OUTPUT_DIR}")
        print("Please run extract_metadata.py first to generate registry files.")
        sys.exit(1)

    validator = RegistryValidator()

    try:
        success, errors, warnings = validator.validate_all()

        print("\n" + "=" * 60)

        if warnings:
            print(f"⚠️  {len(warnings)} warnings:")
            for warning in warnings:
                print(f"   • {warning}")
            print()

        if errors:
            print(f"❌ {len(errors)} errors found:")
            for error in errors:
                print(f"   • {error}")
            print(f"\n❌ Validation failed!")
            sys.exit(1)
        else:
            print(f"✅ Validation passed successfully!")
            print(f"📊 Summary:")
            print(f"   • All JSON files are valid")
            print(f"   • Schema compliance verified")
            print(f"   • Cross-references validated")
            print(f"   • Business rules enforced")

            if warnings:
                print(f"   • {len(warnings)} warnings to review")

            print(f"\n📁 Registry ready for deployment!")
            print(f"📄 Next step: python deploy_registry.py")

    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        raise


if __name__ == "__main__":
    main()