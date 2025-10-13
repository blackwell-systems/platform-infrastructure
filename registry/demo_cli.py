#!/usr/bin/env python3
"""
Demo CLI for Provider Registry

Demonstrates the performance difference between metadata operations
and implementation loading, showcasing the benefits of the metadata/code split.

Usage:
    python demo_cli.py list                    # List all providers (fast)
    python demo_cli.py show tina              # Show provider details (fast)
    python demo_cli.py find --feature=visual_editing  # Find by feature (fast)
    python demo_cli.py load tina              # Load implementation (slower)
    python demo_cli.py benchmark              # Performance comparison
"""

import argparse
import time
import sys
from pathlib import Path

# Add registry to path
sys.path.insert(0, str(Path(__file__).parent))

from json_provider_registry import json_provider_registry


def cmd_list(args):
    """List all providers"""
    print("📋 Available Providers\n")

    start_time = time.time()

    by_category = json_provider_registry.get_providers_by_category()

    for category, providers in by_category.items():
        print(f"{category.upper()}:")
        for provider in providers:
            features = ", ".join(provider.features[:3])  # Show first 3 features
            if len(provider.features) > 3:
                features += f" (+{len(provider.features) - 3} more)"

            print(f"  • {provider.provider_name}")
            print(f"    └─ Features: {features}")
            print(f"    └─ SSG Engines: {', '.join(provider.supported_ssg_engines)}")
            print(f"    └─ Complexity: {provider.complexity_level}")
            print()

    elapsed = (time.time() - start_time) * 1000
    print(f"⏱️  Completed in {elapsed:.1f}ms")


def cmd_show(args):
    """Show detailed provider information"""
    provider_id = args.provider

    print(f"🔍 Provider Details: {provider_id}\n")

    start_time = time.time()

    metadata = json_provider_registry.get_provider_metadata(provider_id)

    if not metadata:
        print(f"❌ Provider '{provider_id}' not found")
        return

    print(f"📦 {metadata.provider_name}")
    print(f"    Category: {metadata.category}")
    print(f"    Tier: {metadata.tier_name}")
    print(f"    Description: {metadata.description}")
    print()

    print("🎯 Features:")
    for feature in metadata.features:
        print(f"    • {feature}")
    print()

    print("⚙️  SSG Engine Support:")
    for engine in metadata.supported_ssg_engines:
        score = metadata.get_ssg_compatibility_score(engine)
        complexity = metadata.get_ssg_setup_complexity(engine)
        print(f"    • {engine} - Score: {score}/10, Setup: {complexity}")
    print()

    print("🔧 Technical Requirements:")
    tech_req = metadata.technical_requirements
    for key, value in tech_req.items():
        print(f"    • {key.replace('_', ' ').title()}: {value}")
    print()

    min_cost, max_cost = metadata.get_estimated_monthly_cost_range()
    print(f"💰 Estimated Cost: ${min_cost}-${max_cost}/month")
    print()

    print("📖 Use Cases:")
    for use_case in metadata.use_cases:
        print(f"    • {use_case}")

    elapsed = (time.time() - start_time) * 1000
    print(f"\n⏱️  Completed in {elapsed:.1f}ms")


def cmd_find(args):
    """Find providers by criteria"""
    print("🔍 Finding Providers\n")

    start_time = time.time()

    filters = {}
    if args.category:
        filters["category"] = args.category
    if args.feature:
        filters["feature"] = args.feature
    if args.ssg_engine:
        filters["ssg_engine"] = args.ssg_engine
    if args.integration_mode:
        filters["integration_mode"] = args.integration_mode

    print(f"Filters: {filters}")
    print()

    providers = json_provider_registry.list_providers(**filters)

    if not providers:
        print("❌ No providers found matching criteria")
        return

    print(f"✅ Found {len(providers)} matching provider(s):")
    print()

    for provider in providers:
        print(f"📦 {provider.provider_name} ({provider.provider_id})")
        print(f"    └─ {provider.tier_name}")

        if args.feature:
            print(f"    └─ Has '{args.feature}': ✅")

        if args.ssg_engine:
            score = provider.get_ssg_compatibility_score(args.ssg_engine)
            print(f"    └─ {args.ssg_engine} compatibility: {score}/10")

        print()

    elapsed = (time.time() - start_time) * 1000
    print(f"⏱️  Completed in {elapsed:.1f}ms")


def cmd_load(args):
    """Load actual implementation class (heavy operation)"""
    provider_id = args.provider

    print(f"🏗️  Loading Implementation: {provider_id}\n")

    # First, show metadata load time
    start_time = time.time()
    metadata = json_provider_registry.get_provider_metadata(provider_id)
    metadata_time = (time.time() - start_time) * 1000

    if not metadata:
        print(f"❌ Provider '{provider_id}' not found")
        return

    print(f"📋 Metadata loaded in {metadata_time:.1f}ms")
    print(f"    Implementation class: {metadata.implementation_class}")
    print()

    # Now load the actual implementation
    print("⏳ Loading implementation class...")
    start_time = time.time()

    implementation_class = json_provider_registry.get_implementation_class(provider_id)

    impl_time = (time.time() - start_time) * 1000

    if implementation_class:
        print(f"✅ Implementation class loaded in {impl_time:.1f}ms")
        print(f"    Class: {implementation_class.__name__}")
        print(f"    Module: {implementation_class.__module__}")

        # Show some attributes if available
        if hasattr(implementation_class, 'SUPPORTED_SSG_ENGINES'):
            engines = list(implementation_class.SUPPORTED_SSG_ENGINES.keys())
            print(f"    Supported SSG engines: {engines}")

            # Verify metadata accuracy
            metadata_engines = set(metadata.supported_ssg_engines)
            impl_engines = set(engines)

            if metadata_engines == impl_engines:
                print("    ✅ Metadata matches implementation")
            else:
                print("    ⚠️  Metadata/implementation mismatch:")
                print(f"        Metadata: {metadata_engines}")
                print(f"        Implementation: {impl_engines}")

    else:
        print(f"❌ Failed to load implementation class")

    print()
    print(f"📊 Performance comparison:")
    print(f"    Metadata: {metadata_time:.1f}ms")
    print(f"    Implementation: {impl_time:.1f}ms")
    print(f"    Slowdown: {impl_time/metadata_time:.1f}x")


def cmd_benchmark(args):
    """Benchmark metadata operations vs implementation loading"""
    print("🏃 Performance Benchmark\n")

    all_providers = json_provider_registry.list_provider_ids()
    print(f"Testing with {len(all_providers)} providers: {all_providers}")
    print()

    # Benchmark metadata operations
    print("📋 Testing metadata operations...")
    iterations = 100

    start_time = time.time()
    for _ in range(iterations):
        for provider_id in all_providers:
            metadata = json_provider_registry.get_provider_metadata(provider_id)
            _ = metadata.features if metadata else []
    metadata_total = (time.time() - start_time) * 1000

    print(f"    {iterations * len(all_providers)} metadata operations: {metadata_total:.1f}ms")
    print(f"    Average per operation: {metadata_total / (iterations * len(all_providers)):.2f}ms")
    print()

    # Benchmark implementation loading
    print("🏗️  Testing implementation loading...")
    impl_times = []

    for provider_id in all_providers:
        start_time = time.time()
        impl_class = json_provider_registry.get_implementation_class(provider_id)
        impl_time = (time.time() - start_time) * 1000
        impl_times.append(impl_time)

        result = "✅" if impl_class else "❌"
        print(f"    {provider_id}: {impl_time:.1f}ms {result}")

    if impl_times:
        avg_impl_time = sum(impl_times) / len(impl_times)
        avg_metadata_time = metadata_total / (iterations * len(all_providers))

        print()
        print("📊 Summary:")
        print(f"    Average metadata operation: {avg_metadata_time:.2f}ms")
        print(f"    Average implementation load: {avg_impl_time:.1f}ms")
        print(f"    Implementation loading is {avg_impl_time/avg_metadata_time:.0f}x slower")
        print()
        print("💡 This demonstrates why metadata operations are ideal for:")
        print("    • CLI discovery commands")
        print("    • Provider listing and filtering")
        print("    • Capability queries")
        print("    • Configuration validation")
        print()
        print("🏗️  While implementation loading is only needed for:")
        print("    • Actual deployment")
        print("    • CDK stack instantiation")
        print("    • Provider-specific operations")


def main():
    parser = argparse.ArgumentParser(description="Provider Registry Demo CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List all providers")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show provider details")
    show_parser.add_argument("provider", help="Provider ID")

    # Find command
    find_parser = subparsers.add_parser("find", help="Find providers by criteria")
    find_parser.add_argument("--category", help="Filter by category")
    find_parser.add_argument("--feature", help="Filter by feature")
    find_parser.add_argument("--ssg-engine", help="Filter by SSG engine")
    find_parser.add_argument("--integration-mode", help="Filter by integration mode")

    # Load command
    load_parser = subparsers.add_parser("load", help="Load implementation class")
    load_parser.add_argument("provider", help="Provider ID")

    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Performance benchmark")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "list":
        cmd_list(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "find":
        cmd_find(args)
    elif args.command == "load":
        cmd_load(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)


if __name__ == "__main__":
    main()