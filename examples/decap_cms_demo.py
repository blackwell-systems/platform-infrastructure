"""
Decap CMS Dual-Mode Stack Demonstration

Shows how to use the new DecapCMSDualModeStack with both integration modes
and demonstrates the benefits of the consolidated configuration system.

Decap CMS is the FREE option that works for both simple sites and complex compositions!
"""

from aws_cdk import App
from models.service_config import IntegrationMode
from models.client_templates import tier1_self_managed_client, tier1_composed_client
from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack


def demo_decap_cms_dual_mode():
    """Demonstrate Decap CMS dual-mode capabilities"""

    print("🆓 Decap CMS Dual-Mode Stack Demo")
    print("=" * 50)
    print("The FREE CMS that works for simple sites AND complex compositions!")

    app = App()

    # Example 1: Budget-conscious developer (Direct Mode)
    print("\n💰 Example 1: Budget-Conscious Developer (Direct Mode)")
    print("-" * 55)

    budget_client = tier1_self_managed_client(
        client_id="budget-dev",
        company_name="Budget Developer",
        domain="budgetdev.com",
        contact_email="dev@budgetdev.com",
        cms_provider="decap",
        ssg_engine="hugo",  # Fastest builds
        integration_mode=IntegrationMode.DIRECT,
        repository="budget-site",
        repository_owner="budget-dev"
    )

    print(f"Client: {budget_client.company_name}")
    print(f"Stack Type: {budget_client.stack_type}")
    print(f"Integration Mode: {budget_client.service_integration.integration_mode.value}")
    print(f"CMS Cost: $0/month (FREE!)")
    print(f"Total Monthly Cost: ~$50-75/month (hosting only)")

    # Create stack
    budget_stack = DecapCMSTierStack(
        app,
        budget_client.deployment_name,
        client_config=budget_client
    )

    # Show suitability scoring
    budget_requirements = {
        "budget_conscious": True,
        "technical_team": True,
        "content_volume": "small",
        "simple_workflow": True,
        "vendor_independence": True
    }

    suitability = DecapCMSTierStack.get_client_suitability_score(budget_requirements)
    print(f"Suitability Score: {suitability['suitability_score']}/100 ({suitability['suitability']})")
    print(f"Recommended Integration Mode: {suitability['integration_mode_recommendation']}")

    # Example 2: Growing tech startup (Event-Driven Mode)
    print("\n🚀 Example 2: Growing Tech Startup (Event-Driven Mode)")
    print("-" * 55)

    startup_client = tier1_self_managed_client(
        client_id="tech-startup",
        company_name="Tech Startup Co",
        domain="techstartup.com",
        contact_email="admin@techstartup.com",
        cms_provider="decap",
        ssg_engine="astro",  # Modern features
        integration_mode=IntegrationMode.EVENT_DRIVEN,
        repository="startup-site",
        repository_owner="tech-startup"
    )

    print(f"Client: {startup_client.company_name}")
    print(f"Integration Mode: {startup_client.service_integration.integration_mode.value}")
    print(f"Benefits: Event-driven architecture, composition-ready")
    print(f"Total Monthly Cost: ~$65-90/month (hosting + events)")

    # Create stack
    startup_stack = DecapCMSTierStack(
        app,
        startup_client.deployment_name,
        client_config=startup_client
    )

    # Show startup requirements
    startup_requirements = {
        "budget_conscious": True,
        "technical_team": True,
        "content_volume": "medium",
        "growth_planning": True,
        "composition_future": True  # Planning to add e-commerce later
    }

    startup_suitability = DecapCMSTierStack.get_client_suitability_score(startup_requirements)
    print(f"Suitability Score: {startup_suitability['suitability_score']}/100")

    # Example 3: Future composition planning
    print("\n🔀 Example 3: Composition Planning (Decap + E-commerce)")
    print("-" * 55)

    # This shows how event-driven mode enables future composition
    composed_client = tier1_composed_client(
        client_id="future-store",
        company_name="Future Store Co",
        domain="futurestore.com",
        contact_email="admin@futurestore.com",
        cms_provider="decap",  # FREE CMS
        ecommerce_provider="snipcart",  # Budget-friendly e-commerce
        ssg_engine="eleventy",
        integration_mode=IntegrationMode.EVENT_DRIVEN,  # Required for composition
        cms_settings={
            "repository": "future-store-site",
            "repository_owner": "future-store",
            "branch": "main"
        },
        ecommerce_settings={
            "store_currency": "USD"
        }
    )

    print(f"Client: {composed_client.company_name}")
    print(f"Stack Type: {composed_client.stack_type}")
    print(f"CMS Provider: {composed_client.service_integration.cms_config.provider} (FREE)")
    print(f"E-commerce Provider: {composed_client.service_integration.ecommerce_config.provider}")
    print(f"Integration Mode: {composed_client.service_integration.integration_mode.value}")

    # Note: Composed stack would use different stack class, but Decap is part of the composition

    return {
        "budget_stack": budget_stack,
        "startup_stack": startup_stack,
        "composed_config": composed_client
    }


def demo_decap_cost_comparison():
    """Demonstrate Decap CMS cost advantages"""

    print("\n\n💰 Decap CMS Cost Comparison")
    print("=" * 40)

    print("🆓 DECAP CMS (Our Implementation):")
    print("  • CMS Cost: $0/month (FREE)")
    print("  • Hosting: $50-75/month")
    print("  • Setup: $960-2,640 (one-time)")
    print("  • Total Year 1: $1,560-3,540")

    print("\n💸 TRADITIONAL ALTERNATIVES:")
    print("  • Contentful: $300+/month + hosting")
    print("  • WordPress Managed: $100-500/month")
    print("  • Custom CMS Agency: $5,000-50,000 setup")
    print("  • Traditional Agency: $10,000-100,000+")

    print("\n📊 SAVINGS WITH DECAP:")
    print("  • vs Contentful: Save $3,600+/year")
    print("  • vs WordPress Managed: Save $600-5,400/year")
    print("  • vs Agency Solution: Save $10,000-95,000+")

    print("\n✅ DECAP ADVANTAGES:")
    print("  • 100% FREE CMS with no usage limits")
    print("  • Zero vendor lock-in (git-based)")
    print("  • Developer-friendly workflow")
    print("  • Perfect for technical teams")
    print("  • Works with ANY SSG engine")
    print("  • Can evolve to event-driven composition")


def demo_integration_mode_selection():
    """Demonstrate how to choose integration mode"""

    print("\n\n🔄 Integration Mode Selection Guide")
    print("=" * 45)

    print("📞 CHOOSE DIRECT MODE WHEN:")
    print("  ✅ You want the simplest possible setup")
    print("  ✅ You have a single content source (CMS only)")
    print("  ✅ You prefer traditional webhook patterns")
    print("  ✅ You want the lowest possible costs")
    print("  ✅ Your team is comfortable with Git workflows")

    print("\n⚡ CHOOSE EVENT-DRIVEN MODE WHEN:")
    print("  ✅ You plan to add e-commerce in the future")
    print("  ✅ You want cutting-edge architecture")
    print("  ✅ You need cross-provider content sync")
    print("  ✅ You value scalability and extensibility")
    print("  ✅ You want to future-proof your infrastructure")

    print("\n🎯 DECAP-SPECIFIC RECOMMENDATIONS:")

    scenarios = [
        {
            "title": "Solo Developer / Small Blog",
            "mode": "DIRECT",
            "reason": "Simplest setup, lowest costs, git workflow"
        },
        {
            "title": "Growing Business / Documentation Site",
            "mode": "DIRECT",
            "reason": "Proven pattern, cost-effective, easy maintenance"
        },
        {
            "title": "Startup Planning E-commerce",
            "mode": "EVENT-DRIVEN",
            "reason": "Future composition capability, scalable architecture"
        },
        {
            "title": "Agency Managing Multiple Sites",
            "mode": "EVENT-DRIVEN",
            "reason": "Standardized architecture, better monitoring"
        },
        {
            "title": "Enterprise Content + Commerce",
            "mode": "EVENT-DRIVEN",
            "reason": "Required for composition, enterprise features"
        }
    ]

    for scenario in scenarios:
        print(f"\n{scenario['title']}:")
        print(f"  Recommended: {scenario['mode']} mode")
        print(f"  Reason: {scenario['reason']}")


def demo_ssg_engine_selection():
    """Demonstrate SSG engine selection for Decap CMS"""

    print("\n\n⚙️  SSG Engine Selection for Decap CMS")
    print("=" * 45)

    engines = DecapCMSTierStack.SUPPORTED_SSG_ENGINES

    for engine, info in engines.items():
        print(f"\n{engine.upper()}:")
        print(f"  Compatibility: {info['compatibility']}")
        print(f"  Setup Complexity: {info['setup_complexity']}")
        print(f"  Features: {', '.join(info['features'])}")

        # Recommendations
        if engine == "hugo":
            print("  Best for: Technical teams, fastest builds, Go templating")
        elif engine == "eleventy":
            print("  Best for: JavaScript developers, flexible templating")
        elif engine == "astro":
            print("  Best for: Modern features, component islands, growing sites")
        elif engine == "gatsby":
            print("  Best for: React developers, GraphQL lovers, rich ecosystems")

    print("\n🎯 SELECTION GUIDE:")
    print("  • Technical team + speed → Hugo")
    print("  • JavaScript developers → Eleventy")
    print("  • Modern features + growth → Astro")
    print("  • React ecosystem → Gatsby")


if __name__ == "__main__":
    # Run all demonstrations
    demo_decap_cms_dual_mode()
    demo_decap_cost_comparison()
    demo_integration_mode_selection()
    demo_ssg_engine_selection()

    print("\n" + "=" * 50)
    print("🎉 Decap CMS Dual-Mode Demo Complete!")
    print("💡 Key Takeaway: FREE CMS that scales from simple to complex!")
    print("=" * 50)