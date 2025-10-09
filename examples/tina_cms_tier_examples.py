"""
Tina CMS Tier Client Configuration Examples

Demonstrates how to configure clients for the Tina CMS tier across
different SSG engine options and client scenarios.

These examples show the complete client configuration process including:
- Visual editing CMS configuration setup
- SSG engine selection (Next.js, Astro, Gatsby)
- Repository configuration with Tina Cloud integration
- Team collaboration and content creator workflows

Usage:
    python examples/tina_cms_tier_examples.py
"""

from models.cms_config import CMSIntegrationConfig, tina_cms_config
from clients._templates.client_config import (
    tier1_self_managed_client,
    create_client_config
)


def example_tina_nextjs_agency():
    """
    Example: Digital agency wanting visual editing for client sites.

    Client Profile:
    - Visual editing preference for content creators
    - Multiple team members creating content
    - React/Next.js technical stack preference
    - Moderate budget for enhanced CMS features
    """

    # Create CMS configuration for Tina + Next.js
    cms_config = CMSIntegrationConfig(
        cms=tina_cms_config(
            admin_users=["admin@digitalagency.co", "content@digitalagency.co", "designer@digitalagency.co"],
            repository="digitalagency-website",
            repository_owner="digital-agency-co",
            branch="main",
            content_path="content",
            media_path="public/images",
            tina_token="tina_xxxxxxxxxx",  # Tina Cloud token for collaboration
            client_id="agency-tina-client-id"
        ),
        ssg_engine="nextjs",  # Next.js for React-based development
        enable_incremental_builds=True,
        cache_content=True,
        enable_editorial_workflow=True,  # Multiple content creators
        enable_media_management=True
    )

    # Create client configuration
    client = create_client_config(
        client_id="digital-agency-co",
        company_name="Digital Agency Co",
        service_tier="tier1",
        stack_type="tina_cms_tier",
        domain="digitalagency.co",
        contact_email="admin@digitalagency.co",
        environment="prod",
        delivery_model="hosted",
        management_model="self_managed",
        ssg_engine="nextjs",
        cms_config=cms_config
    )

    return client


def example_tina_astro_content_creator():
    """
    Example: Content creator/blogger wanting modern features with visual editing.

    Client Profile:
    - Individual content creator or small team
    - Wants modern web features (component islands)
    - Prefers visual editing over markdown
    - Budget-conscious but values user experience
    """

    cms_config = CMSIntegrationConfig(
        cms=tina_cms_config(
            admin_users=["creator@modernblog.io"],
            repository="modernblog-site",
            repository_owner="content-creator-io",
            branch="main",
            content_path="src/content",  # Astro-style content organization
            media_path="public/assets/images"
            # No Tina Cloud integration - self-hosted for budget savings
        ),
        ssg_engine="astro",  # Modern features with component islands
        enable_incremental_builds=True,
        cache_content=True,
        # Content types for blog
        content_types=[
            {
                "name": "blog_posts",
                "label": "Blog Posts",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "date", "type": "datetime", "required": True},
                    {"name": "excerpt", "type": "rich-text"},
                    {"name": "featured_image", "type": "image"},
                    {"name": "tags", "type": "string", "list": True},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            }
        ]
    )

    client = create_client_config(
        client_id="content-creator-io",
        company_name="Modern Blog Creator",
        service_tier="tier1",
        stack_type="tina_cms_tier",
        domain="modernblog.io",
        contact_email="creator@modernblog.io",
        management_model="self_managed",
        ssg_engine="astro",
        cms_config=cms_config
    )

    return client


def example_tina_gatsby_ecommerce_blog():
    """
    Example: E-commerce business with content marketing blog.

    Client Profile:
    - E-commerce business with content marketing needs
    - GraphQL preference for complex data relationships
    - Team of writers and marketers
    - Need structured content for product integration
    """

    cms_config = CMSIntegrationConfig(
        cms=tina_cms_config(
            admin_users=["marketing@ecommercebiz.com", "writer@ecommercebiz.com"],
            repository="ecommercebiz-blog",
            repository_owner="ecommerce-biz-llc",
            branch="main",
            content_path="content",
            media_path="static/images",
            tina_token="tina_yyyyyyyyyy",  # Tina Cloud for team collaboration
            client_id="ecommerce-tina-client"
        ),
        ssg_engine="gatsby",  # GraphQL for complex content relationships
        enable_editorial_workflow=True,
        enable_media_management=True,
        # E-commerce focused content types
        content_types=[
            {
                "name": "blog_posts",
                "label": "Blog Posts",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "date", "type": "datetime", "required": True},
                    {"name": "category", "type": "select", "options": ["product_guide", "industry_news", "how_to"]},
                    {"name": "related_products", "type": "reference", "collection": "products"},
                    {"name": "seo_title", "type": "string"},
                    {"name": "meta_description", "type": "string"},
                    {"name": "featured_image", "type": "image"},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            },
            {
                "name": "product_guides",
                "label": "Product Guides",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "product_category", "type": "string", "required": True},
                    {"name": "difficulty_level", "type": "select", "options": ["beginner", "intermediate", "advanced"]},
                    {"name": "estimated_time", "type": "string"},
                    {"name": "materials_needed", "type": "rich-text"},
                    {"name": "steps", "type": "object", "list": True, "fields": [
                        {"name": "step_title", "type": "string"},
                        {"name": "description", "type": "rich-text"},
                        {"name": "image", "type": "image"}
                    ]},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            }
        ]
    )

    client = create_client_config(
        client_id="ecommerce-biz-llc",
        company_name="E-commerce Business LLC",
        service_tier="tier1",
        stack_type="tina_cms_tier",
        domain="ecommercebiz.com",
        contact_email="marketing@ecommercebiz.com",
        management_model="self_managed",
        ssg_engine="gatsby",
        cms_config=cms_config
    )

    return client


def example_tina_nextjs_saas_company():
    """
    Example: SaaS company with content marketing and documentation needs.

    Client Profile:
    - B2B SaaS company
    - Technical documentation + marketing content
    - Large team with different content roles
    - Need for advanced collaboration features
    """

    cms_config = CMSIntegrationConfig(
        cms=tina_cms_config(
            admin_users=[
                "marketing@saascompany.com",
                "docs@saascompany.com",
                "content@saascompany.com",
                "developer@saascompany.com"
            ],
            repository="saascompany-website",
            repository_owner="saas-company-inc",
            branch="main",
            content_path="content",
            media_path="public/assets",
            tina_token="tina_zzzzzzzzzz",  # Tina Cloud for enterprise collaboration
            client_id="saas-company-tina-client"
        ),
        ssg_engine="nextjs",  # Next.js for SaaS application integration
        enable_editorial_workflow=True,
        enable_media_management=True,
        enable_incremental_builds=True,
        # SaaS-focused content types
        content_types=[
            {
                "name": "blog_posts",
                "label": "Blog Posts",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "date", "type": "datetime", "required": True},
                    {"name": "author", "type": "reference", "collection": "authors"},
                    {"name": "category", "type": "select", "options": ["product_updates", "industry_insights", "customer_stories"]},
                    {"name": "target_audience", "type": "select", "options": ["developers", "business_owners", "general"]},
                    {"name": "cta_type", "type": "select", "options": ["trial", "demo", "newsletter", "none"]},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            },
            {
                "name": "documentation",
                "label": "Documentation",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "category", "type": "select", "options": ["api", "getting_started", "tutorials", "reference"]},
                    {"name": "order", "type": "number"},
                    {"name": "code_examples", "type": "object", "list": True, "fields": [
                        {"name": "language", "type": "string"},
                        {"name": "code", "type": "string", "ui": {"component": "textarea"}}
                    ]},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            },
            {
                "name": "case_studies",
                "label": "Case Studies",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "client_name", "type": "string", "required": True},
                    {"name": "industry", "type": "string"},
                    {"name": "challenge", "type": "rich-text"},
                    {"name": "solution", "type": "rich-text"},
                    {"name": "results", "type": "rich-text"},
                    {"name": "metrics", "type": "object", "list": True, "fields": [
                        {"name": "metric_name", "type": "string"},
                        {"name": "before_value", "type": "string"},
                        {"name": "after_value", "type": "string"},
                        {"name": "improvement", "type": "string"}
                    ]},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            }
        ]
    )

    client = create_client_config(
        client_id="saas-company-inc",
        company_name="SaaS Company Inc",
        service_tier="tier1",
        stack_type="tina_cms_tier",
        domain="saascompany.com",
        contact_email="marketing@saascompany.com",
        management_model="self_managed",
        ssg_engine="nextjs",
        cms_config=cms_config
    )

    return client


def example_tina_developer_managed():
    """
    Example: Developer-managed Tina CMS for non-technical client.

    Client Profile:
    - Non-technical business owner
    - Wants visual editing but needs developer support
    - Developer manages technical aspects
    - Client focuses on content creation only
    """

    cms_config = CMSIntegrationConfig(
        cms=tina_cms_config(
            admin_users=["developer@webstudio.agency"],  # Only developer has admin access
            repository="local-business-site",
            repository_owner="webstudio-agency",  # Agency owns the repo
            branch="main",
            content_path="content",
            media_path="public/images",
            # Self-hosted for cost savings, developer manages everything
        ),
        ssg_engine="nextjs",  # Developer preference
        enable_editorial_workflow=False,  # Simple workflow for single user
        enable_media_management=True,
        # Simple content types for local business
        content_types=[
            {
                "name": "pages",
                "label": "Pages",
                "fields": [
                    {"name": "title", "type": "string", "required": True},
                    {"name": "slug", "type": "string", "required": True},
                    {"name": "hero_image", "type": "image"},
                    {"name": "body", "type": "rich-text", "isBody": True}
                ]
            },
            {
                "name": "services",
                "label": "Services",
                "fields": [
                    {"name": "name", "type": "string", "required": True},
                    {"name": "description", "type": "rich-text"},
                    {"name": "price", "type": "string"},
                    {"name": "image", "type": "image"},
                    {"name": "featured", "type": "boolean", "default": False}
                ]
            }
        ]
    )

    client = create_client_config(
        client_id="local-business",
        company_name="Local Business",
        service_tier="tier1",
        stack_type="tina_cms_tier",
        domain="localbusiness.com",
        contact_email="owner@localbusiness.com",
        management_model="developer_managed",  # Developer manages everything
        ssg_engine="nextjs",
        cms_config=cms_config
    )

    return client


def demonstrate_tina_cms_tier_flexibility():
    """
    Demonstrate the flexibility of Tina CMS tier across different scenarios.
    """

    examples = [
        ("Digital Agency - Next.js", example_tina_nextjs_agency()),
        ("Content Creator - Astro", example_tina_astro_content_creator()),
        ("E-commerce Blog - Gatsby", example_tina_gatsby_ecommerce_blog()),
        ("SaaS Company - Next.js", example_tina_nextjs_saas_company()),
        ("Developer Managed - Next.js", example_tina_developer_managed())
    ]

    print("🎨 Tina CMS Tier - Client Configuration Examples")
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

        # Check if Tina Cloud is enabled
        tina_token = client.cms_config.cms.content_settings.get('tina_token')
        cloud_status = "Enabled" if tina_token else "Self-hosted"
        print(f"   Tina Cloud: {cloud_status}")

        print(f"   Monthly Cost: $60-125 (includes CMS + hosting)")
        print(f"   Setup Cost: $1,200-2,880 (varies by complexity)")
        print()

        # Validate configuration
        try:
            client.validate_cms_compatibility()
            print("   ✅ Configuration Valid")
        except Exception as e:
            print(f"   ❌ Configuration Error: {e}")

        print("-" * 40)
        print()


def get_tina_cms_tier_cost_analysis():
    """
    Analyze costs across different Tina CMS tier configurations.
    """

    configurations = [
        ("Next.js", "React ecosystem", 1200, 2400, 60, 85, "Self-hosted"),
        ("Next.js + Cloud", "React + collaboration", 1440, 2640, 90, 125, "Tina Cloud"),
        ("Astro", "Modern features", 1440, 2640, 65, 90, "Self-hosted"),
        ("Astro + Cloud", "Modern + collaboration", 1680, 2880, 95, 125, "Tina Cloud"),
        ("Gatsby", "GraphQL ecosystem", 1800, 2880, 70, 100, "Self-hosted"),
        ("Gatsby + Cloud", "GraphQL + collaboration", 2040, 2880, 100, 125, "Tina Cloud")
    ]

    print("💰 Tina CMS Tier - Cost Analysis")
    print("=" * 70)
    print()
    print(f"{'Configuration':<20} {'Profile':<20} {'Setup Range':<15} {'Monthly Range':<15} {'Cloud':<12}")
    print("-" * 82)

    for config, profile, setup_min, setup_max, monthly_min, monthly_max, cloud in configurations:
        print(f"{config:<20} {profile:<20} ${setup_min}-{setup_max}   ${monthly_min}-{monthly_max}     {cloud:<12}")

    print()
    print("Key Benefits:")
    print("• Visual editing interface with real-time preview")
    print("• Git-based storage maintains version control")
    print("• React-based admin interface for modern UX")
    print("• GraphQL API for flexible content queries")
    print("• Optional Tina Cloud for team collaboration")
    print("• Support for structured content and rich media")
    print()
    print("Tina Cloud Features (additional $29-50/month):")
    print("• Real-time collaborative editing")
    print("• Advanced media management")
    print("• Team user management")
    print("• Analytics and usage insights")
    print("• Priority support")


if __name__ == "__main__":
    demonstrate_tina_cms_tier_flexibility()
    print()
    get_tina_cms_tier_cost_analysis()