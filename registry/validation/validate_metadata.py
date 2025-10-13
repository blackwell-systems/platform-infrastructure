#!/usr/bin/env python3
"""
Provider Metadata Validation Tool

Validates provider metadata files against the JSON schema and verifies
implementation class references and capability accuracy.

Usage:
    python validate_metadata.py                 # Validate all providers
    python validate_metadata.py --provider=tina # Validate specific provider
    python validate_metadata.py --schema-only   # Schema validation only
"""

import argparse
import json
import sys
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)


class MetadataValidator:
    """Validates provider metadata files for accuracy and completeness"""

    def __init__(self, registry_root: Path):
        self.registry_root = registry_root
        self.schema_path = registry_root / "schema" / "provider_metadata_schema.json"
        self.providers_path = registry_root / "providers"

        # Load JSON schema
        with open(self.schema_path) as f:
            self.schema = json.load(f)

        self.errors = []
        self.warnings = []

    def validate_all_providers(self) -> bool:
        """Validate all provider metadata files"""
        success = True

        print("🔍 Validating all provider metadata files...")
        print(f"📂 Registry root: {self.registry_root}")
        print(f"📋 Schema: {self.schema_path}")
        print()

        # Find all JSON files in providers directory
        provider_files = list(self.providers_path.rglob("*.json"))

        if not provider_files:
            print("❌ No provider metadata files found")
            return False

        for provider_file in provider_files:
            provider_success = self.validate_provider_file(provider_file)
            if not provider_success:
                success = False

        self._print_summary()
        return success

    def validate_provider(self, provider_id: str) -> bool:
        """Validate a specific provider by ID"""
        print(f"🔍 Validating provider: {provider_id}")

        # Find provider file
        provider_file = None
        for category_dir in self.providers_path.iterdir():
            if category_dir.is_dir():
                candidate = category_dir / f"{provider_id}.json"
                if candidate.exists():
                    provider_file = candidate
                    break

        if not provider_file:
            print(f"❌ Provider file not found: {provider_id}")
            return False

        success = self.validate_provider_file(provider_file)
        self._print_summary()
        return success

    def validate_provider_file(self, provider_file: Path) -> bool:
        """Validate a single provider metadata file"""
        provider_id = provider_file.stem
        category = provider_file.parent.name

        print(f"📄 {category}/{provider_id}.json")

        try:
            with open(provider_file) as f:
                metadata = json.load(f)
        except json.JSONDecodeError as e:
            self._add_error(provider_id, f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self._add_error(provider_id, f"Error reading file: {e}")
            return False

        success = True

        # 1. Schema validation
        if not self._validate_schema(provider_id, metadata):
            success = False

        # 2. Implementation class validation
        if not self._validate_implementation_class(provider_id, metadata):
            success = False

        # 3. Provider class validation
        if not self._validate_provider_class(provider_id, metadata):
            success = False

        # 4. SSG engine compatibility validation
        if not self._validate_ssg_compatibility(provider_id, metadata):
            success = False

        # 5. Cross-reference validation
        if not self._validate_cross_references(provider_id, metadata, category):
            success = False

        if success:
            print(f"  ✅ Valid")
        else:
            print(f"  ❌ Validation failed")

        print()
        return success

    def _validate_schema(self, provider_id: str, metadata: Dict) -> bool:
        """Validate metadata against JSON schema"""
        try:
            jsonschema.validate(metadata, self.schema)
            print(f"  ✅ Schema validation passed")
            return True
        except jsonschema.ValidationError as e:
            self._add_error(provider_id, f"Schema validation failed: {e.message}")
            return False

    def _validate_implementation_class(self, provider_id: str, metadata: Dict) -> bool:
        """Validate that implementation class exists and can be imported"""
        class_path = metadata.get("implementation_class")
        if not class_path:
            return True  # Optional field

        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            implementation_class = getattr(module, class_name)

            print(f"  ✅ Implementation class found: {class_path}")

            # Check if it has expected methods/attributes
            if hasattr(implementation_class, 'SUPPORTED_SSG_ENGINES'):
                supported_ssg = metadata.get("supported_ssg_engines", [])
                actual_ssg = list(implementation_class.SUPPORTED_SSG_ENGINES.keys())

                missing = set(supported_ssg) - set(actual_ssg)
                extra = set(actual_ssg) - set(supported_ssg)

                if missing:
                    self._add_warning(provider_id, f"Metadata claims SSG engines not in implementation: {missing}")
                if extra:
                    self._add_warning(provider_id, f"Implementation supports SSG engines not in metadata: {extra}")

            return True

        except ImportError as e:
            self._add_error(provider_id, f"Cannot import implementation class '{class_path}': {e}")
            return False
        except AttributeError as e:
            self._add_error(provider_id, f"Implementation class not found '{class_path}': {e}")
            return False
        except Exception as e:
            self._add_error(provider_id, f"Error validating implementation class: {e}")
            return False

    def _validate_provider_class(self, provider_id: str, metadata: Dict) -> bool:
        """Validate that provider class exists and can be imported"""
        class_path = metadata.get("provider_class")
        if not class_path:
            return True  # Optional field

        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            provider_class = getattr(module, class_name)

            print(f"  ✅ Provider class found: {class_path}")
            return True

        except ImportError as e:
            self._add_error(provider_id, f"Cannot import provider class '{class_path}': {e}")
            return False
        except AttributeError as e:
            self._add_error(provider_id, f"Provider class not found '{class_path}': {e}")
            return False
        except Exception as e:
            self._add_error(provider_id, f"Error validating provider class: {e}")
            return False

    def _validate_ssg_compatibility(self, provider_id: str, metadata: Dict) -> bool:
        """Validate SSG engine compatibility information"""
        supported_engines = metadata.get("supported_ssg_engines", [])
        compatibility = metadata.get("compatibility", {}).get("ssg_engine_compatibility", {})

        # Check that all supported engines have compatibility info
        missing_compat = set(supported_engines) - set(compatibility.keys())
        if missing_compat:
            self._add_warning(provider_id, f"Missing compatibility info for SSG engines: {missing_compat}")

        # Check that compatibility info doesn't reference unsupported engines
        extra_compat = set(compatibility.keys()) - set(supported_engines)
        if extra_compat:
            self._add_warning(provider_id, f"Compatibility info for unsupported SSG engines: {extra_compat}")

        print(f"  ✅ SSG compatibility validation passed")
        return True

    def _validate_cross_references(self, provider_id: str, metadata: Dict, category: str) -> bool:
        """Validate cross-references and consistency"""

        # Check provider_id matches filename
        if metadata.get("provider_id") != provider_id:
            self._add_error(provider_id, f"provider_id '{metadata.get('provider_id')}' doesn't match filename '{provider_id}'")
            return False

        # Check category matches directory
        if metadata.get("category") != category:
            self._add_error(provider_id, f"category '{metadata.get('category')}' doesn't match directory '{category}'")
            return False

        print(f"  ✅ Cross-reference validation passed")
        return True

    def _add_error(self, provider_id: str, message: str):
        """Add an error message"""
        self.errors.append(f"❌ {provider_id}: {message}")
        print(f"    ❌ {message}")

    def _add_warning(self, provider_id: str, message: str):
        """Add a warning message"""
        self.warnings.append(f"⚠️  {provider_id}: {message}")
        print(f"    ⚠️  {message}")

    def _print_summary(self):
        """Print validation summary"""
        print("=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed successfully!")
        elif not self.errors:
            print(f"\n✅ Validation passed with {len(self.warnings)} warning(s)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s) and {len(self.warnings)} warning(s)")


def main():
    parser = argparse.ArgumentParser(description="Validate provider metadata files")
    parser.add_argument("--provider", help="Validate specific provider by ID")
    parser.add_argument("--schema-only", action="store_true", help="Only validate JSON schema compliance")
    parser.add_argument("--registry-root",
                        default=Path(__file__).parent.parent,
                        type=Path,
                        help="Path to registry root directory")

    args = parser.parse_args()

    # Verify registry structure
    if not args.registry_root.exists():
        print(f"❌ Registry root not found: {args.registry_root}")
        sys.exit(1)

    if not (args.registry_root / "schema" / "provider_metadata_schema.json").exists():
        print(f"❌ Schema file not found: {args.registry_root / 'schema' / 'provider_metadata_schema.json'}")
        sys.exit(1)

    # Create validator
    validator = MetadataValidator(args.registry_root)

    # Run validation
    if args.provider:
        success = validator.validate_provider(args.provider)
    else:
        success = validator.validate_all_providers()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()