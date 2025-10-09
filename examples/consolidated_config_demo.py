"""
Consolidated Configuration System Demonstration

Shows how the new unified service configuration system simplifies client setup
and eliminates the configuration sprawl from the previous system.

BEFORE: 979 lines of ClientConfig + 559 lines of CMS config + complex validation
AFTER: Clean, composable models with clear separation of concerns
"""

from models.service_config import (
    ClientServiceConfig,
    ServiceIntegrationConfig,
    CMSProviderConfig,
    EcommerceProviderConfig,
    ServiceType,
    ServiceTier,
    ManagementModel,
    IntegrationMode
)
from models.client_templates import (
    tier1_self_managed_client,
    tier1_ecommerce_client,
    tier1_composed_client,
    tier3_enterprise_client
)


def demo_configuration_consolidation():
    """Demonstrate the benefits of the consolidated configuration system"""

    print("🔧 Consolidated Configuration System Demo")
    print("=" * 60)

    # Example 1: Simple CMS client (direct mode)
    print("\n📝 Example 1: Simple CMS Client (Direct Mode)")
    print("-" * 50)

    simple_cms_client = tier1_self_managed_client(
        client_id="content-startup",
        company_name="Content Startup LLC",
        domain="contentstartup.com",
        contact_email="admin@contentstartup.com",
        cms_provider="tina",
        ssg_engine="astro",
        integration_mode=IntegrationMode.DIRECT,
        repository="content-site",
        repository_owner="contentstartup"
    )

    print(f"Client: {simple_cms_client.company_name}")
    print(f"Stack Type: {simple_cms_client.stack_type}")
    print(f"Deployment Name: {simple_cms_client.deployment_name}")
    print(f"Integration Mode: {simple_cms_client.service_integration.integration_mode.value}")
    print(f"CMS Provider: {simple_cms_client.service_integration.cms_config.provider}")
    print(f"SSG Engine: {simple_cms_client.service_integration.ssg_engine}")

    # Example 2: E-commerce client (direct mode)
    print("\n🛒 Example 2: E-commerce Client (Direct Mode)")
    print("-" * 50)

    ecommerce_client = tier1_ecommerce_client(
        client_id="tech-gadgets",
        company_name="Tech Gadgets Store",
        domain="techgadgets.com",
        contact_email="orders@techgadgets.com",
        ecommerce_provider="snipcart",
        ssg_engine="hugo",
        integration_mode=IntegrationMode.DIRECT
    )

    print(f"Client: {ecommerce_client.company_name}")
    print(f"Stack Type: {ecommerce_client.stack_type}")
    print(f"Has E-commerce: {ecommerce_client.has_ecommerce()}")
    print(f"E-commerce Provider: {ecommerce_client.service_integration.ecommerce_config.provider}")
    print(f"Integration Mode: {ecommerce_client.service_integration.integration_mode.value}")

    # Example 3: Composed stack (event-driven mode)
    print("\n🔀 Example 3: Composed Stack (Event-Driven Mode)")
    print("-" * 50)

    composed_client = tier1_composed_client(
        client_id="full-service-biz",
        company_name="Full Service Business",
        domain="fullservicebiz.com",
        contact_email="admin@fullservicebiz.com",
        cms_provider="tina",
        ecommerce_provider="snipcart",
        ssg_engine="astro",
        integration_mode=IntegrationMode.EVENT_DRIVEN
    )

    print(f"Client: {composed_client.company_name}")
    print(f"Stack Type: {composed_client.stack_type}")
    print(f"Is Composed Stack: {composed_client.is_composed_stack()}")
    print(f"Is Event-Driven: {composed_client.is_event_driven()}")
    print(f"CMS Provider: {composed_client.service_integration.cms_config.provider}")
    print(f"E-commerce Provider: {composed_client.service_integration.ecommerce_config.provider}")

    # Example 4: Enterprise client with full features
    print("\n🏢 Example 4: Enterprise Client (Event-Driven)")
    print("-" * 50)

    enterprise_client = tier3_enterprise_client(
        client_id="bigcorp",
        company_name="BigCorp Industries",
        domain="bigcorp.com",
        contact_email="devops@bigcorp.com",
        service_type=ServiceType.COMPOSED_STACK,
        integration_mode=IntegrationMode.EVENT_DRIVEN,
        cms_provider="contentful",
        ecommerce_provider="shopify_advanced",
        ssg_engine="nextjs"
    )

    print(f"Client: {enterprise_client.company_name}")
    print(f"Service Tier: {enterprise_client.service_tier.value}")
    print(f"Stack Type: {enterprise_client.stack_type}")
    print(f"Integration Mode: {enterprise_client.service_integration.integration_mode.value}")
    print(f"Deployment Name: {enterprise_client.deployment_name}")

    # Show integration configuration
    print("\n🔗 Integration Configuration:")
    integration_config = enterprise_client.get_integration_config()
    for key, value in integration_config.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")

    # Show AWS tags for cost allocation
    print("\n📊 AWS Tags (for cost allocation):")
    tags = enterprise_client.tags
    for key, value in tags.items():
        print(f"  {key}: {value}")


def demo_configuration_benefits():
    """Demonstrate benefits of consolidated configuration"""

    print("\n\n✨ Configuration Consolidation Benefits")
    print("=" * 60)

    print("\n📊 Before vs After:")
    print("-" * 30)
    print("BEFORE (sprawling configuration):")
    print("  • ClientConfig: 979 lines with mixed concerns")
    print("  • CMSIntegrationConfig: 559 lines")
    print("  • Template functions scattered throughout")
    print("  • Complex validation logic spread across files")
    print("  • Difficult to add new integration modes")

    print("\nAFTER (consolidated configuration):")
    print("  • ClientServiceConfig: Clean, focused model")
    print("  • ServiceIntegrationConfig: Composable service configs")
    print("  • Template functions: Simple, clear functions")
    print("  • Integration modes: Built-in support for direct/event-driven")
    print("  • Easy to extend with new providers and modes")

    print("\n🎯 Key Improvements:")
    print("-" * 30)
    print("1. ✅ Separation of Concerns")
    print("   - Client identity separate from service configuration")
    print("   - Provider configs focused on provider-specific settings")
    print("   - Integration mode drives architecture decisions")

    print("\n2. ✅ Composability")
    print("   - Mix and match CMS + E-commerce providers")
    print("   - Choose integration mode per client needs")
    print("   - SSG engine choice within provider tiers")

    print("\n3. ✅ Extensibility")
    print("   - Easy to add new providers")
    print("   - Easy to add new integration modes")
    print("   - Clear patterns for validation and configuration")

    print("\n4. ✅ Developer Experience")
    print("   - Type safety with Pydantic models")
    print("   - Clear examples in model schemas")
    print("   - Computed fields for common derived values")
    print("   - Template functions for common configurations")


def demo_integration_modes():
    """Demonstrate integration mode differences"""

    print("\n\n🔄 Integration Mode Comparison")
    print("=" * 60)

    print("\n📞 DIRECT MODE:")
    print("-" * 20)
    print("✅ Use when:")
    print("  • Single service (CMS only or E-commerce only)")
    print("  • Simple requirements")
    print("  • Lower complexity preferred")
    print("  • Direct provider APIs sufficient")

    print("\n🏗️  Architecture:")
    print("  • CMS/E-commerce → Webhook → Lambda → CodeBuild")
    print("  • Direct provider API calls")
    print("  • Simple build triggers")

    print("\n⚡ EVENT-DRIVEN MODE:")
    print("-" * 25)
    print("✅ Use when:")
    print("  • Composed stacks (CMS + E-commerce)")
    print("  • Cross-provider content sync needed")
    print("  • Enterprise scalability requirements")
    print("  • Complex workflows and automation")

    print("\n🏗️  Architecture:")
    print("  • Providers → SNS Topics → Lambda Processors → DynamoDB")
    print("  • Unified content API")
    print("  • Event-based workflows")
    print("  • Cross-provider normalization")

    # Show configuration examples
    print("\n📝 Configuration Examples:")
    print("-" * 30)

    # Direct mode example
    direct_config = ServiceIntegrationConfig(
        service_type=ServiceType.CMS_TIER,
        integration_mode=IntegrationMode.DIRECT,
        ssg_engine="astro",
        cms_config=CMSProviderConfig(
            provider="tina",
            admin_users=["admin@example.com"],
            settings={"repository": "site-repo"}
        )
    )

    print(f"\nDirect Mode Config:")
    print(f"  Service Type: {direct_config.service_type.value}")
    print(f"  Integration Mode: {direct_config.integration_mode.value}")
    print(f"  CMS Provider: {direct_config.cms_config.provider}")

    # Event-driven mode example
    event_driven_config = ServiceIntegrationConfig(
        service_type=ServiceType.COMPOSED_STACK,
        integration_mode=IntegrationMode.EVENT_DRIVEN,
        ssg_engine="nextjs",
        cms_config=CMSProviderConfig(
            provider="contentful",
            admin_users=["admin@example.com"],
            settings={"space_id": "abc123"}
        ),
        ecommerce_config=EcommerceProviderConfig(
            provider="shopify_basic",
            settings={"store_domain": "example-store.myshopify.com"}
        )
    )

    print(f"\nEvent-Driven Config:")
    print(f"  Service Type: {event_driven_config.service_type.value}")
    print(f"  Integration Mode: {event_driven_config.integration_mode.value}")
    print(f"  CMS Provider: {event_driven_config.cms_config.provider}")
    print(f"  E-commerce Provider: {event_driven_config.ecommerce_config.provider}")
    print(f"  Event Config: {event_driven_config.event_config}")


if __name__ == "__main__":
    # Run all demonstrations
    demo_configuration_consolidation()
    demo_configuration_benefits()
    demo_integration_modes()

    print("\n" + "=" * 60)
    print("🎉 Configuration consolidation complete!")
    print("📚 Ready to implement optional event-layer integration in existing stacks.")
    print("=" * 60)