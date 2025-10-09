"""
Sanity CMS Tier Client Configuration Examples

Real-world client scenarios demonstrating the Sanity CMS tier implementation
for structured content management with different SSG engines and API-based workflows.

This module showcases practical configurations for various client types,
from professional content teams to enterprise-ready solutions with
advanced content modeling and real-time collaboration.

Client Scenarios:
1. Professional Content Agency (Next.js + Sanity Studio)
2. API-First SaaS Company (Astro + Structured Content)
3. E-commerce Editorial Team (Gatsby + Product Content)
4. Publishing House (Eleventy + Content Lake)
5. Enterprise Marketing Team (Next.js + Advanced Features)

Cost Analysis:
- Setup: $1,440-3,360 depending on complexity and SSG choice
- Monthly: $65-280 including hosting and Sanity plans
- Sanity CMS: $0-199/month (Free tier to Business plan)
- AWS Hosting: $45-80/month (optimized for API-based content)
"""

from datetime import datetime
from typing import Dict, Any, List

from models.client import ClientConfig
from models.cms_config import CMSIntegrationConfig, sanity_cms_config
from clients._templates.client_config import create_client_config


def professional_content_agency_nextjs() -> ClientConfig:
    """
    Professional content agency using Sanity CMS with Next.js.

    Client Profile:
    - Digital content agency managing multiple client projects
    - 8-person content team with structured workflows
    - Need for advanced content modeling and real-time collaboration
    - Budget: $150-200/month including premium Sanity features

    Technical Requirements:
    - Sanity Studio for content editors
    - Next.js with ISR for performance
    - Preview mode for content review
    - Webhook automation for instant updates
    - Advanced media management with transformations

    Business Value:
    - Professional content management workflows
    - Real-time collaboration between editors and clients
    - Structured content with validation and relationships
    - Scalable architecture for growing content volume
    """

    cms_config = CMSIntegrationConfig(
        cms=sanity_cms_config(
            admin_users=["editor@contentpro.agency", "manager@contentpro.agency"],
            project_id="cp7x8y9z",
            dataset="production",
            api_version="2023-05-03",
            api_token="skn123professional456token789",
            webhook_secret="content_webhook_secret_2024",
            use_cdn=True
        ),
        ssg_engine="nextjs",
        build_command="npm run build && npm run export",
        output_directory=".next",
        enable_incremental_builds=True,
        cache_content=True
    )

    return create_client_config(
        client_id="contentpro-agency",
        company_name="ContentPro Agency",
        service_tier="tier2",
        stack_type="sanity_cms_tier",
        domain="contentpro.agency",
        contact_email="tech@contentpro.agency",
        management_model="professionally_managed",
        ssg_engine="nextjs",
        cms_config=cms_config,
        performance_tier="premium",
        monthly_budget=200,
        setup_budget=2800,
        priority_features=[
            "structured_content",
            "real_time_collaboration",
            "preview_mode",
            "advanced_media",
            "webhook_automation"
        ],
        business_requirements={
            "content_team_size": 8,
            "client_projects": 12,
            "content_volume": "large",
            "collaboration_needs": "high",
            "workflow_complexity": "professional"
        }
    )


def api_first_saas_astro() -> ClientConfig:
    """
    API-first SaaS company using Sanity CMS with Astro.

    Client Profile:
    - Software company with API-first development approach
    - 5-person development team with strong technical skills
    - Marketing site with product documentation and blog
    - Budget: $120-150/month with emphasis on API capabilities

    Technical Requirements:
    - GROQ queries for flexible content access
    - Astro with component islands for performance
    - Structured content schemas for consistency
    - API-based content delivery for headless architecture
    - Content validation and schema enforcement

    Business Value:
    - API-first content architecture matching company values
    - Developer-friendly GROQ query language
    - High-performance site with structured content
    - Scalable content infrastructure
    """

    cms_config = CMSIntegrationConfig(
        cms=sanity_cms_config(
            admin_users=["dev@apiflow.com", "content@apiflow.com"],
            project_id="af9a8b7c",
            dataset="production",
            api_version="2023-05-03",
            api_token="skn456api789first012content345",
            use_cdn=True
        ),
        ssg_engine="astro",
        build_command="npm run build",
        output_directory="dist",
        enable_incremental_builds=True,
        cache_content=True
    )

    return create_client_config(
        client_id="apiflow-saas",
        company_name="ApiFlow SaaS Solutions",
        service_tier="tier2",
        stack_type="sanity_cms_tier",
        domain="apiflow.com",
        contact_email="engineering@apiflow.com",
        management_model="self_managed",
        ssg_engine="astro",
        cms_config=cms_config,
        performance_tier="premium",
        monthly_budget=150,
        setup_budget=2200,
        priority_features=[
            "api_first_architecture",
            "groq_querying",
            "structured_content",
            "content_validation",
            "developer_api"
        ],
        business_requirements={
            "development_team_size": 5,
            "api_integration_needs": "high",
            "content_volume": "medium",
            "technical_complexity": "high",
            "performance_requirements": "critical"
        }
    )


def ecommerce_editorial_gatsby() -> ClientConfig:
    """
    E-commerce company using Sanity CMS with Gatsby for editorial content.

    Client Profile:
    - E-commerce company with extensive product catalog
    - 6-person editorial team managing product content and blog
    - Need for content relationships and structured product data
    - Budget: $180-220/month with growth plan features

    Technical Requirements:
    - Gatsby with GraphQL for content queries
    - Structured product content with relationships
    - Advanced media management for product images
    - Content scheduling for marketing campaigns
    - Integration with e-commerce platform APIs

    Business Value:
    - Structured product content management
    - Editorial workflow for marketing content
    - Content relationships for cross-selling
    - Professional media management
    """

    cms_config = CMSIntegrationConfig(
        cms=sanity_cms_config(
            admin_users=["editor@shopcraft.com", "marketing@shopcraft.com"],
            project_id="sc6d7e8f",
            dataset="production",
            api_version="2023-05-03",
            api_token="skn789ecommerce012editorial345content678",
            webhook_secret="editorial_webhook_secret_2024",
            use_cdn=True
        ),
        ssg_engine="gatsby",
        build_command="npm run build",
        output_directory="public",
        enable_incremental_builds=True,
        cache_content=True
    )

    return create_client_config(
        client_id="shopcraft-editorial",
        company_name="ShopCraft E-commerce",
        service_tier="tier2",
        stack_type="sanity_cms_tier",
        domain="blog.shopcraft.com",
        contact_email="tech@shopcraft.com",
        management_model="professionally_managed",
        ssg_engine="gatsby",
        cms_config=cms_config,
        performance_tier="premium",
        monthly_budget=220,
        setup_budget=2600,
        priority_features=[
            "structured_content",
            "content_relationships",
            "advanced_media",
            "content_scheduling",
            "graphql_integration"
        ],
        business_requirements={
            "editorial_team_size": 6,
            "product_catalog_size": "large",
            "content_volume": "high",
            "marketing_campaigns": "frequent",
            "ecommerce_integration": "required"
        }
    )


def publishing_house_eleventy() -> ClientConfig:
    """
    Publishing house using Sanity CMS with Eleventy for content lake approach.

    Client Profile:
    - Traditional publishing house transitioning to digital
    - 10-person editorial team with varied technical skills
    - Large archive of content requiring structured organization
    - Budget: $160-200/month with business plan features

    Technical Requirements:
    - Eleventy for simple, fast builds
    - Content Lake approach for large content volumes
    - Portable Text for rich editorial content
    - Content modeling for books, articles, and authors
    - Advanced search and content organization

    Business Value:
    - Digital transformation of traditional publishing
    - Structured content organization at scale
    - Editorial workflows for publishing teams
    - Content archive digitization and management
    """

    cms_config = CMSIntegrationConfig(
        cms=sanity_cms_config(
            admin_users=[
                "editor@meridianpublishing.com",
                "digital@meridianpublishing.com",
                "archive@meridianpublishing.com"
            ],
            project_id="mp4e5f6g",
            dataset="production",
            api_version="2023-05-03",
            api_token="skn012publishing345house678content901",
            webhook_secret="publishing_webhook_secret_2024",
            use_cdn=True
        ),
        ssg_engine="eleventy",
        build_command="npm run build",
        output_directory="_site",
        enable_incremental_builds=True,
        cache_content=True
    )

    return create_client_config(
        client_id="meridian-publishing",
        company_name="Meridian Publishing House",
        service_tier="tier2",
        stack_type="sanity_cms_tier",
        domain="meridianpublishing.com",
        contact_email="digital@meridianpublishing.com",
        management_model="professionally_managed",
        ssg_engine="eleventy",
        cms_config=cms_config,
        performance_tier="optimized",
        monthly_budget=200,
        setup_budget=2400,
        priority_features=[
            "content_lake",
            "portable_text",
            "content_modeling",
            "large_content_volumes",
            "editorial_workflows"
        ],
        business_requirements={
            "editorial_team_size": 10,
            "content_archive_size": "massive",
            "content_volume": "enterprise",
            "digital_transformation": "in_progress",
            "legacy_content_migration": "required"
        }
    )


def enterprise_marketing_nextjs_advanced() -> ClientConfig:
    """
    Enterprise marketing team using Sanity CMS with Next.js and advanced features.

    Client Profile:
    - Large enterprise with complex marketing requirements
    - 15-person marketing team across multiple departments
    - Global presence requiring multi-language content
    - Budget: $250-300/month with full enterprise features

    Technical Requirements:
    - Next.js with advanced SSR and ISR features
    - Multi-language content support
    - Advanced workflow approvals and content governance
    - Real-time collaboration across time zones
    - Integration with marketing automation tools
    - Advanced analytics and content performance tracking

    Business Value:
    - Enterprise-grade content management
    - Global content coordination and localization
    - Marketing campaign management at scale
    - Content governance and compliance
    - Performance analytics and optimization
    """

    cms_config = CMSIntegrationConfig(
        cms=sanity_cms_config(
            admin_users=[
                "marketing.director@globalcorp.com",
                "content.manager@globalcorp.com",
                "brand.manager@globalcorp.com",
                "digital.lead@globalcorp.com"
            ],
            project_id="gc1h2i3j",
            dataset="production",
            api_version="2023-05-03",
            api_token="skn345enterprise678marketing901advanced234",
            webhook_secret="enterprise_webhook_secret_2024",
            use_cdn=True
        ),
        ssg_engine="nextjs",
        build_command="npm run build",
        output_directory=".next",
        enable_incremental_builds=True,
        cache_content=True
    )

    return create_client_config(
        client_id="globalcorp-marketing",
        company_name="GlobalCorp Enterprise",
        service_tier="tier3",
        stack_type="sanity_cms_tier",
        domain="marketing.globalcorp.com",
        contact_email="digital@globalcorp.com",
        management_model="enterprise_managed",
        ssg_engine="nextjs",
        cms_config=cms_config,
        performance_tier="premium",
        monthly_budget=300,
        setup_budget=3360,
        priority_features=[
            "enterprise_features",
            "multi_language_support",
            "advanced_workflows",
            "real_time_collaboration",
            "content_governance",
            "marketing_automation_integration",
            "advanced_analytics"
        ],
        business_requirements={
            "marketing_team_size": 15,
            "global_presence": True,
            "languages_supported": 8,
            "content_volume": "enterprise",
            "compliance_requirements": "high",
            "marketing_automation": "salesforce_marketo",
            "performance_tracking": "advanced"
        }
    )


def get_all_sanity_examples() -> List[ClientConfig]:
    """Get all Sanity CMS tier client configuration examples"""
    return [
        professional_content_agency_nextjs(),
        api_first_saas_astro(),
        ecommerce_editorial_gatsby(),
        publishing_house_eleventy(),
        enterprise_marketing_nextjs_advanced()
    ]


def get_sanity_cost_analysis() -> Dict[str, Any]:
    """
    Get comprehensive cost analysis for Sanity CMS tier implementations.

    Returns detailed cost breakdown by client type, SSG engine,
    and feature requirements for sales and budgeting purposes.
    """

    examples = get_all_sanity_examples()

    return {
        "cost_summary": {
            "setup_cost_range": "$1,440 - $3,360",
            "monthly_cost_range": "$65 - $280",
            "sanity_cms_plans": {
                "free": "$0/month (up to 3 users, 10k API requests)",
                "growth": "$99/month (team features)",
                "business": "$199/month (enterprise features)"
            },
            "aws_hosting_costs": "$45-80/month (optimized for API-based content)"
        },

        "cost_by_client_type": {
            example.client_id: {
                "company": example.company_name,
                "monthly_budget": example.monthly_budget,
                "setup_budget": example.setup_budget,
                "ssg_engine": example.ssg_engine,
                "team_size": example.business_requirements.get("content_team_size",
                                   example.business_requirements.get("editorial_team_size",
                                   example.business_requirements.get("marketing_team_size", "N/A"))),
                "content_volume": example.business_requirements.get("content_volume", "medium"),
                "sanity_plan": _determine_sanity_plan(example),
                "key_features": example.priority_features[:3]
            }
            for example in examples
        },

        "cost_by_ssg_engine": {
            "nextjs": {
                "setup_range": "$1,800 - $3,360",
                "monthly_range": "$85 - $280",
                "complexity": "Medium to High",
                "best_for": "Professional agencies, Enterprise marketing"
            },
            "astro": {
                "setup_range": "$1,440 - $2,880",
                "monthly_range": "$65 - $220",
                "complexity": "Medium",
                "best_for": "API-first development, Performance-critical sites"
            },
            "gatsby": {
                "setup_range": "$1,680 - $3,120",
                "monthly_range": "$75 - $250",
                "complexity": "Medium to High",
                "best_for": "E-commerce editorial, GraphQL integration"
            },
            "eleventy": {
                "setup_range": "$1,440 - $2,640",
                "monthly_range": "$65 - $200",
                "complexity": "Low to Medium",
                "best_for": "Publishing houses, Large content volumes"
            }
        },

        "roi_analysis": {
            "content_velocity": "3-5x faster content publishing",
            "team_efficiency": "40-60% reduction in content management overhead",
            "development_time": "60-80% faster site updates and launches",
            "content_quality": "Structured content reduces errors by 70%",
            "collaboration": "Real-time editing reduces review cycles by 50%"
        },

        "comparison_with_alternatives": {
            "vs_wordpress": {
                "setup_time": "50% faster (no server management)",
                "monthly_cost": "Similar to managed WordPress + premium plugins",
                "performance": "10x faster page loads",
                "security": "No security updates or maintenance required"
            },
            "vs_contentful": {
                "cost": "20-30% lower for similar feature set",
                "flexibility": "More flexible content modeling",
                "developer_experience": "Better GraphQL and API tools",
                "migration": "Easier content migration and no vendor lock-in"
            },
            "vs_custom_cms": {
                "development_time": "90% faster implementation",
                "maintenance": "Zero maintenance vs ongoing updates",
                "features": "Enterprise features out of the box",
                "cost": "70% lower total cost of ownership"
            }
        }
    }


def _determine_sanity_plan(client_config: ClientConfig) -> str:
    """Determine appropriate Sanity plan based on client requirements"""

    budget = client_config.monthly_budget
    team_size = client_config.business_requirements.get("content_team_size",
                client_config.business_requirements.get("editorial_team_size",
                client_config.business_requirements.get("marketing_team_size", 3)))

    if isinstance(team_size, str):
        # Handle string representations like "1-5_people"
        if "1-5" in team_size:
            team_size = 3
        elif "2-10" in team_size:
            team_size = 6
        elif "3-15" in team_size:
            team_size = 10
        else:
            team_size = 5

    content_volume = client_config.business_requirements.get("content_volume", "medium")

    if budget >= 200 or team_size >= 10 or content_volume in ["large", "enterprise"]:
        return "business ($199/month)"
    elif budget >= 120 or team_size >= 5 or content_volume == "medium":
        return "growth ($99/month)"
    else:
        return "free ($0/month)"


if __name__ == "__main__":
    """
    Example usage and demonstration of Sanity CMS tier configurations
    """

    print("=== Sanity CMS Tier Client Examples ===\n")

    examples = get_all_sanity_examples()

    for example in examples:
        print(f"Client: {example.company_name}")
        print(f"Stack: {example.stack_type} with {example.ssg_engine}")
        print(f"Domain: {example.domain}")
        print(f"Budget: ${example.monthly_budget}/month (setup: ${example.setup_budget})")
        print(f"Management: {example.management_model}")
        print(f"Priority Features: {', '.join(example.priority_features[:3])}")

        # CMS Configuration Details
        sanity_config = example.cms_config.cms
        print(f"Sanity Project: {sanity_config.content_settings['project_id']}")
        print(f"Dataset: {sanity_config.content_settings['dataset']}")
        print(f"API Version: {sanity_config.content_settings['api_version']}")
        print(f"CDN Enabled: {sanity_config.content_settings['use_cdn']}")
        print(f"Admin Users: {len(sanity_config.admin_users)} users")
        print()

    # Cost Analysis
    print("=== Cost Analysis ===\n")
    cost_analysis = get_sanity_cost_analysis()

    print("Setup Cost Range:", cost_analysis["cost_summary"]["setup_cost_range"])
    print("Monthly Cost Range:", cost_analysis["cost_summary"]["monthly_cost_range"])
    print()

    print("Sanity CMS Plans:")
    for plan, cost in cost_analysis["cost_summary"]["sanity_cms_plans"].items():
        print(f"  {plan.title()}: {cost}")
    print()

    print("AWS Hosting:", cost_analysis["cost_summary"]["aws_hosting_costs"])
    print()

    # ROI Analysis
    print("=== ROI Benefits ===\n")
    roi = cost_analysis["roi_analysis"]
    for benefit, value in roi.items():
        print(f"{benefit.replace('_', ' ').title()}: {value}")