"""
Composed Stack Examples - CMS + E-commerce Combinations

Demonstrates how different CMS and E-commerce providers can be composed together
using the event-driven integration architecture. Each example shows popular
combinations that serve different market segments and business needs.

KEY BENEFITS OF COMPOSITION:
- Choose best CMS for content needs + best e-commerce for business model
- Unified event system coordinates content and commerce updates
- Single infrastructure stack with multiple specialized providers
- Cost optimization through provider-specific strengths
- Avoid vendor lock-in by mixing providers strategically

ARCHITECTURE PATTERN:
Both CMS and E-commerce providers publish events to the unified content system:
- CMS Events: content_updated, content_deleted, content_published
- E-commerce Events: product_updated, order_created, inventory_changed
- Unified Processing: Cross-provider content synchronization and workflow automation
"""

from aws_cdk import App
from models.service_config import IntegrationMode
from models.client_templates import tier1_composed_client
from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack
from stacks.cms.contentful_cms_stack import ContentfulCMSStack
from stacks.cms.sanity_cms_tier_stack import SanityCMSTierStack
from stacks.ecommerce.snipcart_ecommerce_stack_new import SnipcartEcommerceStack
from stacks.ecommerce.shopify_basic_ecommerce_stack_new import ShopifyBasicEcommerceStack
from stacks.ecommerce.foxy_ecommerce_stack_new import FoxyEcommerceStack


def demo_budget_friendly_composition():
    """
    Example 1: Budget-Friendly Composition
    Decap CMS (FREE) + Snipcart E-commerce (2% transaction fees only)

    PERFECT FOR:
    - Startups and small businesses on tight budgets
    - Technical teams comfortable with git-based workflows
    - Low to medium transaction volumes
    - Maximum cost efficiency with professional results

    TOTAL MONTHLY COST: ~$65-90/month + 2% of sales
    - Decap CMS: $0/month (FREE)
    - Snipcart: 2% transaction fees (no monthly fees)
    - AWS Hosting + Integration: $65-90/month
    """

    print("💰 Budget-Friendly Composition: Decap CMS + Snipcart")
    print("=" * 60)

    app = App()

    # Create composed client configuration
    budget_composed_client = tier1_composed_client(
        client_id="budget-startup",
        company_name="Budget Startup Co",
        domain="budgetstartup.com",
        contact_email="admin@budgetstartup.com",
        cms_provider="decap",  # FREE CMS
        ecommerce_provider="snipcart",  # Cost-effective e-commerce
        ssg_engine="eleventy",  # Fast, simple builds
        integration_mode=IntegrationMode.EVENT_DRIVEN,  # Required for composition
        cms_settings={
            "repository": "budget-startup-site",
            "repository_owner": "budget-startup",
            "branch": "main"
        },
        ecommerce_settings={
            "public_api_key": "your-snipcart-public-api-key",
            "currency": "USD"
        }
    )

    print(f"Client: {budget_composed_client.company_name}")
    print(f"Stack Type: {budget_composed_client.stack_type}")
    print(f"CMS Provider: {budget_composed_client.service_integration.cms_config.provider} (FREE)")
    print(f"E-commerce Provider: {budget_composed_client.service_integration.ecommerce_config.provider}")
    print(f"Integration Mode: {budget_composed_client.service_integration.integration_mode.value}")
    print(f"SSG Engine: {budget_composed_client.service_integration.ssg_engine}")

    # Create CMS stack
    cms_stack = DecapCMSTierStack(
        app,
        f"{budget_composed_client.deployment_name}-CMS",
        client_config=budget_composed_client
    )

    # Create E-commerce stack (shares the same integration layer)
    ecommerce_stack = SnipcartEcommerceStack(
        app,
        f"{budget_composed_client.deployment_name}-Ecommerce",
        client_config=budget_composed_client
    )

    print("\n🎯 COMPOSITION BENEFITS:")
    print("  • FREE CMS eliminates monthly content management costs")
    print("  • Git-based workflow provides full version control")
    print("  • Snipcart handles payments without monthly fees")
    print("  • Event-driven sync keeps content and products aligned")
    print("  • Total monthly cost under $100 for most small businesses")

    return {
        "cms_stack": cms_stack,
        "ecommerce_stack": ecommerce_stack,
        "client_config": budget_composed_client
    }


def demo_enterprise_composition():
    """
    Example 2: Enterprise Composition
    Contentful CMS (Enterprise features) + Shopify Basic (Proven reliability)

    PERFECT FOR:
    - Large content teams needing advanced workflows
    - Businesses requiring enterprise CMS features
    - Organizations wanting proven e-commerce reliability
    - Multi-brand companies with complex content governance

    TOTAL MONTHLY COST: ~$430-580/month + 2.9% of sales
    - Contentful: $300-500/month (Team to Business plans)
    - Shopify Basic: $29/month + 2.9% transaction fees
    - AWS Hosting + Integration: $100-150/month
    """

    print("\n\n🏢 Enterprise Composition: Contentful CMS + Shopify Basic")
    print("=" * 65)

    app = App()

    # Create enterprise composed client configuration
    enterprise_composed_client = tier1_composed_client(
        client_id="enterprise-corp",
        company_name="Enterprise Corp",
        domain="enterprisecorp.com",
        contact_email="admin@enterprisecorp.com",
        cms_provider="contentful",  # Enterprise CMS
        ecommerce_provider="shopify_basic",  # Proven e-commerce
        ssg_engine="gatsby",  # Advanced React ecosystem
        integration_mode=IntegrationMode.EVENT_DRIVEN,  # Required for composition
        cms_settings={
            "space_id": "your-contentful-space-id",
            "environment": "master"
        },
        ecommerce_settings={
            "store_domain": "enterprisecorp.myshopify.com",
            "plan": "basic"
        }
    )

    print(f"Client: {enterprise_composed_client.company_name}")
    print(f"CMS Provider: {enterprise_composed_client.service_integration.cms_config.provider} (Enterprise)")
    print(f"E-commerce Provider: {enterprise_composed_client.service_integration.ecommerce_config.provider} (Proven)")
    print(f"SSG Engine: {enterprise_composed_client.service_integration.ssg_engine} (Advanced)")

    # Create CMS stack
    cms_stack = ContentfulCMSStack(
        app,
        f"{enterprise_composed_client.deployment_name}-CMS",
        client_config=enterprise_composed_client
    )

    # Create E-commerce stack
    ecommerce_stack = ShopifyBasicEcommerceStack(
        app,
        f"{enterprise_composed_client.deployment_name}-Ecommerce",
        client_config=enterprise_composed_client
    )

    print("\n🎯 COMPOSITION BENEFITS:")
    print("  • Contentful provides enterprise-grade content management")
    print("  • Advanced workflows, roles, and approval processes")
    print("  • Shopify handles proven e-commerce with PCI compliance")
    print("  • Static site performance with enterprise backend reliability")
    print("  • Unified events coordinate complex content and commerce workflows")

    return {
        "cms_stack": cms_stack,
        "ecommerce_stack": ecommerce_stack,
        "client_config": enterprise_composed_client
    }


def demo_creative_composition():
    """
    Example 3: Creative/Advanced Composition
    Sanity CMS (Structured content) + Foxy.io (Advanced customization)

    PERFECT FOR:
    - Creative agencies and design-focused businesses
    - Complex content modeling requirements
    - Advanced e-commerce customization needs
    - Subscription-based or complex business models

    TOTAL MONTHLY COST: ~$180-300/month + 1.5% of sales
    - Sanity: $0-199/month (Free to Business plans)
    - Foxy.io: $20/month + 1.5% transaction fees
    - AWS Hosting + Integration: $120-180/month
    """

    print("\n\n🎨 Creative/Advanced Composition: Sanity CMS + Foxy.io")
    print("=" * 60)

    app = App()

    # Create creative composed client configuration
    creative_composed_client = tier1_composed_client(
        client_id="creative-agency",
        company_name="Creative Agency Co",
        domain="creativeagency.com",
        contact_email="admin@creativeagency.com",
        cms_provider="sanity",  # Structured content CMS
        ecommerce_provider="foxy",  # Advanced customization
        ssg_engine="astro",  # Modern architecture
        integration_mode=IntegrationMode.EVENT_DRIVEN,  # Required for composition
        cms_settings={
            "project_id": "your-sanity-project-id",
            "dataset": "production"
        },
        ecommerce_settings={
            "subdomain": "creative-agency-foxy",
            "currency": "USD"
        }
    )

    print(f"Client: {creative_composed_client.company_name}")
    print(f"CMS Provider: {creative_composed_client.service_integration.cms_config.provider} (Structured)")
    print(f"E-commerce Provider: {creative_composed_client.service_integration.ecommerce_config.provider} (Advanced)")
    print(f"SSG Engine: {creative_composed_client.service_integration.ssg_engine} (Modern)")

    # Create CMS stack
    cms_stack = SanityCMSTierStack(
        app,
        f"{creative_composed_client.deployment_name}-CMS",
        client_config=creative_composed_client
    )

    # Create E-commerce stack
    ecommerce_stack = FoxyEcommerceStack(
        app,
        f"{creative_composed_client.deployment_name}-Ecommerce",
        client_config=creative_composed_client
    )

    print("\n🎯 COMPOSITION BENEFITS:")
    print("  • Sanity's structured content perfect for complex designs")
    print("  • Real-time collaboration and advanced content modeling")
    print("  • Foxy.io enables sophisticated cart and checkout customization")
    print("  • Lower transaction fees (1.5%) for higher-volume businesses")
    print("  • Event-driven architecture supports complex business logic")

    return {
        "cms_stack": cms_stack,
        "ecommerce_stack": ecommerce_stack,
        "client_config": creative_composed_client
    }


def demo_composition_architecture_benefits():
    """Demonstrate the architectural benefits of composed stacks"""

    print("\n\n🏗️  Composition Architecture Benefits")
    print("=" * 50)

    print("\n🔄 EVENT-DRIVEN COORDINATION:")
    print("  • CMS content updates trigger product page rebuilds")
    print("  • E-commerce inventory changes update content displays")
    print("  • Cross-provider analytics and monitoring")
    print("  • Unified search indexing across content and products")

    print("\n⚡ PERFORMANCE BENEFITS:")
    print("  • Static site delivery (0.8-1.5s page loads)")
    print("  • CDN optimization for global performance")
    print("  • Incremental builds based on change detection")
    print("  • Edge caching for both content and product data")

    print("\n💰 COST OPTIMIZATION:")
    print("  • Choose providers based on specific needs, not full suite")
    print("  • Pay only for features you actually use")
    print("  • Avoid enterprise pricing for unnecessary features")
    print("  • Scale different components independently")

    print("\n🔓 VENDOR FREEDOM:")
    print("  • No single-vendor lock-in")
    print("  • Migrate CMS or e-commerce independently")
    print("  • Mix best-of-breed solutions")
    print("  • Future-proof architecture")

    print("\n🎯 TECHNICAL ADVANTAGES:")
    print("  • Unified content schema across providers")
    print("  • Consistent deployment and monitoring")
    print("  • Shared caching and CDN infrastructure")
    print("  • Single AWS account and billing")


def demo_composition_selection_guide():
    """Guide for selecting composition combinations"""

    print("\n\n📊 Composition Selection Guide")
    print("=" * 40)

    compositions = [
        {
            "name": "Budget Startup",
            "cms": "Decap (FREE)",
            "ecommerce": "Snipcart (2% fees)",
            "monthly_cost": "$65-90 + 2% sales",
            "best_for": "Technical teams, low budgets, simple products",
            "example_client": "Solo developer, small agency, startup"
        },
        {
            "name": "Growing Business",
            "cms": "Sanity ($99/month)",
            "ecommerce": "Snipcart (2% fees)",
            "monthly_cost": "$180-220 + 2% sales",
            "best_for": "Structured content, growing sales, design focus",
            "example_client": "Creative agency, medium business, content-heavy"
        },
        {
            "name": "Professional Standard",
            "cms": "Contentful ($300/month)",
            "ecommerce": "Shopify Basic ($29 + 2.9%)",
            "monthly_cost": "$430-480 + 2.9% sales",
            "best_for": "Team collaboration, proven reliability, scale",
            "example_client": "Established business, content teams, high volume"
        },
        {
            "name": "Advanced Customization",
            "cms": "Sanity ($199/month)",
            "ecommerce": "Foxy.io ($20 + 1.5%)",
            "monthly_cost": "$300-350 + 1.5% sales",
            "best_for": "Complex content, custom checkout, subscriptions",
            "example_client": "SaaS company, subscription business, complex products"
        }
    ]

    for comp in compositions:
        print(f"\n{comp['name']}:")
        print(f"  CMS: {comp['cms']}")
        print(f"  E-commerce: {comp['ecommerce']}")
        print(f"  Monthly Cost: {comp['monthly_cost']}")
        print(f"  Best For: {comp['best_for']}")
        print(f"  Example Client: {comp['example_client']}")

    print("\n🎯 SELECTION CRITERIA:")
    print("  • Budget < $150/month: Decap + Snipcart")
    print("  • Need enterprise CMS: Contentful + any e-commerce")
    print("  • Complex content modeling: Sanity + any e-commerce")
    print("  • Proven e-commerce reliability: Any CMS + Shopify")
    print("  • Advanced customization: Any CMS + Foxy.io")
    print("  • Maximum cost efficiency: Decap + Snipcart")


def demo_integration_requirements():
    """Demonstrate integration requirements for composed stacks"""

    print("\n\n⚙️  Integration Requirements")
    print("=" * 35)

    print("\n📋 MANDATORY REQUIREMENTS:")
    print("  ✅ Integration Mode: EVENT_DRIVEN (required for composition)")
    print("  ✅ Shared EventDrivenIntegrationLayer")
    print("  ✅ Unified content events topic (SNS)")
    print("  ✅ Cross-provider event processing")

    print("\n🔧 AUTOMATIC INFRASTRUCTURE:")
    print("  • Shared integration API for cross-provider coordination")
    print("  • Unified content schema and event format")
    print("  • Cross-provider analytics and monitoring")
    print("  • Consistent deployment and build coordination")

    print("\n⚠️  IMPORTANT NOTES:")
    print("  • Direct mode does NOT support composition")
    print("  • Both providers must support event-driven integration")
    print("  • Additional AWS costs for event messaging (~$15-25/month)")
    print("  • Slightly more complex setup than single-provider stacks")

    print("\n✨ COMPOSITION VALUE:")
    print("  • Provider flexibility outweighs small additional costs")
    print("  • Best-of-breed solutions vs single-vendor compromises")
    print("  • Future-proof architecture enables easy provider migration")
    print("  • Unified management despite multiple providers")


if __name__ == "__main__":
    # Run all composition demonstrations
    print("🎨 Composed Stack Examples - CMS + E-commerce Combinations")
    print("=" * 70)
    print("Demonstrating how different providers work together with event-driven integration")

    # Run composition examples
    budget_example = demo_budget_friendly_composition()
    enterprise_example = demo_enterprise_composition()
    creative_example = demo_creative_composition()

    # Educational content
    demo_composition_architecture_benefits()
    demo_composition_selection_guide()
    demo_integration_requirements()

    print("\n" + "=" * 70)
    print("🎉 Composed Stack Examples Complete!")
    print("💡 Key Takeaway: Mix and match providers for optimal cost and features!")
    print("=" * 70)

    # Return examples for potential testing
    return {
        "budget_example": budget_example,
        "enterprise_example": enterprise_example,
        "creative_example": creative_example
    }