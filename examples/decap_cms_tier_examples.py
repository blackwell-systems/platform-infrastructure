"""
Decap CMS Tier Client Configuration Examples

Demonstrates how to configure clients for the Decap CMS tier across
different SSG engine options and client scenarios.

These examples show the complete client configuration process including:
- CMS configuration setup
- SSG engine selection
- Repository configuration
- Admin user management

Usage:
    python examples/decap_cms_tier_examples.py
"""

from models.cms_config import CMSIntegrationConfig, decap_cms_config
from clients._templates.client_config import (
    tier1_self_managed_client,
    create_client_config
)


def example_decap_hugo_law_firm():
    """
    Example: Law firm with budget constraints wanting fast performance.

    Client Profile:
    - Budget-conscious (wants free CMS)
    - Technical comfort level: Medium (can handle git workflow)
    - Performance critical (law firm needs fast loading)
    - Small content team (1-2 people updating content)
    """

    # Create CMS configuration for Decap + Hugo
    cms_config = CMSIntegrationConfig(
        cms=decap_cms_config(
            admin_users=["admin@smithlaw.com", "paralegal@smithlaw.com"],
            repository="smithlaw-website",
            repository_owner="smith-law-firm",
            branch="main",
            content_path="content",
            media_path="static/images"
        ),
        ssg_engine="hugo",  # Hugo for maximum performance
        enable_incremental_builds=True,
        cache_content=True
    )

    # Create client configuration
    client = create_client_config(
        client_id="smith-law-firm",
        company_name="Smith Law Firm",
        service_tier="tier1",
        stack_type="decap_cms_tier",
        domain="smithlaw.com",
        contact_email="admin@smithlaw.com",
        environment="prod",
        delivery_model="hosted",
        management_model="self_managed",
        ssg_engine="hugo",
        cms_config=cms_config
    )

    return client


def example_decap_eleventy_marketing_agency():
    """
    Example: Marketing agency needing easy content management.

    Client Profile:
    - Budget-conscious but needs reliability
    - Medium technical comfort
    - Multiple clients/projects to manage
    - Need balance of simplicity and features
    """

    cms_config = CMSIntegrationConfig(
        cms=decap_cms_config(
            admin_users=["admin@creativemarketingco.com", "content@creativemarketingco.com"],
            repository="creativemarketingco-site",
            repository_owner="creative-marketing-co",
            branch="main",
            content_path="content",
            media_path="static/assets/images"
        ),
        ssg_engine="eleventy",  # Eleventy for balanced complexity
        enable_editorial_workflow=True,  # Multiple content creators
        enable_media_management=True
    )

    client = create_client_config(
        client_id="creative-marketing-co",
        company_name="Creative Marketing Co",
        service_tier="tier1",
        stack_type="decap_cms_tier",
        domain="creativemarketingco.com",
        contact_email="admin@creativemarketingco.com",
        management_model="self_managed",
        ssg_engine="eleventy",
        cms_config=cms_config
    )

    return client


def example_decap_astro_tech_startup():
    """
    Example: Tech startup wanting modern features with budget constraints.

    Client Profile:
    - Budget-conscious startup
    - High technical comfort
    - Want modern web features
    - Small but growing team
    """

    cms_config = CMSIntegrationConfig(
        cms=decap_cms_config(
            admin_users=["founder@techstartup.io", "dev@techstartup.io"],
            repository="techstartup-website",
            repository_owner="tech-startup-io",
            branch="main",
            content_path="src/content",  # Astro-style content organization
            media_path="public/images"
        ),
        ssg_engine="astro",  # Modern features with component islands
        enable_incremental_builds=True,
        cache_content=True
    )

    client = create_client_config(
        client_id="tech-startup-io",
        company_name="Tech Startup Inc",
        service_tier="tier1",
        stack_type="decap_cms_tier",
        domain="techstartup.io",
        contact_email="founder@techstartup.io",
        management_model="self_managed",
        ssg_engine="astro",
        cms_config=cms_config
    )

    return client


def example_decap_gatsby_content_business():
    """
    Example: Content-heavy business preferring React ecosystem.

    Client Profile:
    - Content-focused business (blog, resources)
    - React/GraphQL preference
    - Medium budget consciousness
    - Growing content team
    """

    cms_config = CMSIntegrationConfig(
        cms=decap_cms_config(
            admin_users=["editor@contentbusiness.com", "admin@contentbusiness.com"],
            repository="contentbusiness-site",
            repository_owner="content-business-llc",
            branch="main",
            content_path="content",
            media_path="static/images"
        ),
        ssg_engine="gatsby",  # React + GraphQL for content-heavy sites
        enable_editorial_workflow=True,
        enable_media_management=True,
        # Gatsby-specific content types
        content_types=[
            {
                "name": "blog_posts",
                "label": "Blog Posts",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "date", "type": "datetime", "required": True},
                    {"name": "category", "type": "select", "options": ["tech", "business", "marketing"]},
                    {"name": "featured", "type": "boolean", "default": False},
                    {"name": "excerpt", "type": "text"},
                    {"name": "body", "type": "markdown", "required": True}
                ]
            }
        ]
    )

    client = create_client_config(
        client_id="content-business-llc",
        company_name="Content Business LLC",
        service_tier="tier1",
        stack_type="decap_cms_tier",
        domain="contentbusiness.com",
        contact_email="admin@contentbusiness.com",
        management_model="self_managed",
        ssg_engine="gatsby",
        cms_config=cms_config
    )

    return client


def example_decap_developer_managed():
    """
    Example: Developer-managed Decap CMS tier for non-technical client.

    Client Profile:
    - Non-technical business owner
    - Wants content management but doesn't want to learn git
    - Willing to pay developer to manage content updates
    - Budget-conscious on monthly costs
    """

    cms_config = CMSIntegrationConfig(
        cms=decap_cms_config(
            admin_users=["developer@webdev-agency.com"],  # Only developer has admin access
            repository="local-restaurant-site",
            repository_owner="webdev-agency",  # Agency owns the repo
            branch="main",
            content_path="content",
            media_path="static/images"
        ),
        ssg_engine="eleventy",  # Simple and reliable
        enable_editorial_workflow=False,  # Developer manages all updates
        enable_media_management=True
    )

    client = create_client_config(
        client_id="local-restaurant",
        company_name="Local Restaurant",
        service_tier="tier1",
        stack_type="decap_cms_tier",
        domain="localrestaurant.com",
        contact_email="owner@localrestaurant.com",
        management_model="developer_managed",  # Developer manages content
        ssg_engine="eleventy",
        cms_config=cms_config
    )

    return client


def demonstrate_decap_cms_tier_flexibility():
    """
    Demonstrate the flexibility of Decap CMS tier across different scenarios.
    """

    examples = [
        ("Law Firm - Hugo", example_decap_hugo_law_firm()),
        ("Marketing Agency - Eleventy", example_decap_eleventy_marketing_agency()),
        ("Tech Startup - Astro", example_decap_astro_tech_startup()),
        ("Content Business - Gatsby", example_decap_gatsby_content_business()),
        ("Developer Managed - Eleventy", example_decap_developer_managed())
    ]

    print("🎯 Decap CMS Tier - Client Configuration Examples")
    print("=" * 60)
    print()

    for name, client in examples:
        print(f"📋 {name}")
        print(f"   Client ID: {client.client_id}")
        print(f"   Company: {client.company_name}")
        print(f"   SSG Engine: {client.ssg_engine}")
        print(f"   Management: {client.management_model}")
        print(f"   CMS Provider: {client.cms_config.cms.provider}")
        print(f"   Repository: {client.cms_config.cms.content_settings.get('repository')}")
        print(f"   Monthly Cost: $50-75 (free CMS + hosting)")
        print(f"   Setup Cost: $960-2,640 (varies by SSG complexity)")
        print()

        # Validate configuration
        try:
            client.validate_cms_compatibility()
            print("   ✅ Configuration Valid")
        except Exception as e:
            print(f"   ❌ Configuration Error: {e}")

        print("-" * 40)
        print()


def get_decap_cms_tier_cost_analysis():
    """
    Analyze costs across different Decap CMS tier configurations.
    """

    configurations = [
        ("Hugo", "Performance-focused", 960, 1800, 50, 65),
        ("Eleventy", "Balanced complexity", 1200, 2160, 55, 70),
        ("Astro", "Modern features", 1440, 2400, 60, 75),
        ("Gatsby", "React ecosystem", 1800, 2640, 65, 75)
    ]

    print("💰 Decap CMS Tier - Cost Analysis")
    print("=" * 50)
    print()
    print(f"{'SSG Engine':<12} {'Profile':<20} {'Setup Range':<15} {'Monthly Range':<15}")
    print("-" * 62)

    for ssg, profile, setup_min, setup_max, monthly_min, monthly_max in configurations:
        print(f"{ssg:<12} {profile:<20} ${setup_min}-{setup_max}    ${monthly_min}-{monthly_max}")

    print()
    print("Key Benefits:")
    print("• FREE CMS (Decap CMS costs $0/month)")
    print("• Client chooses SSG engine based on technical preference")
    print("• Same monthly hosting cost serves different complexity levels")
    print("• Setup cost reflects SSG complexity, not CMS complexity")
    print("• No vendor lock-in - content stored in client's git repository")


if __name__ == "__main__":
    demonstrate_decap_cms_tier_flexibility()
    print()
    get_decap_cms_tier_cost_analysis()