"""
Client Configuration Templates

Simplified template functions using the consolidated service configuration system.
These replace the sprawling template functions in the previous client_config.py.
"""

from typing import Optional, Dict, Any
from models.service_config import (
    ClientServiceConfig,
    ServiceIntegrationConfig,
    CMSProviderConfig,
    EcommerceProviderConfig,
    ServiceType,
    ServiceTier,
    ManagementModel,
    DeliveryModel,
    IntegrationMode
)


def tier1_developer_managed_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    ssg_engine: str = "eleventy",
    integration_mode: IntegrationMode = IntegrationMode.DIRECT
) -> ClientServiceConfig:
    """
    Template for Tier 1A: Developer-Managed clients ($480-1,440 setup | $75-125/month).

    For busy professionals who want "set it and forget it" service with professional maintenance.
    We handle all content updates, performance optimization, and maintenance.

    Example:
        client = tier1_developer_managed_client("law-firm", "Smith Law Firm", "smithlaw.com", "admin@smithlaw.com")
    """
    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER1,
        management_model=ManagementModel.DEVELOPER_MANAGED,
        delivery_model=DeliveryModel.HOSTED,
        service_integration=ServiceIntegrationConfig(
            service_type=ServiceType.STATIC_SITE,
            ssg_engine=ssg_engine,
            integration_mode=integration_mode
        )
    )


def tier1_self_managed_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    cms_provider: str = "tina",
    ssg_engine: str = "astro",
    integration_mode: IntegrationMode = IntegrationMode.DIRECT,
    repository: Optional[str] = None,
    repository_owner: Optional[str] = None
) -> ClientServiceConfig:
    """
    Template for Tier 1B: Self-Managed clients ($720-2,400 setup | $50-75/month).

    For clients comfortable with CMS editing who want complete control over their content
    through easy-to-use web-based editing tools.

    Example:
        client = tier1_self_managed_client("content-biz", "Content Business", "contentbiz.com", "admin@contentbiz.com")
    """
    # Create CMS settings
    cms_settings = {}
    if repository and repository_owner:
        cms_settings.update({
            "repository": repository,
            "repository_owner": repository_owner,
            "branch": "main",
            "content_path": "content"
        })

    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER1,
        management_model=ManagementModel.SELF_MANAGED,
        delivery_model=DeliveryModel.HOSTED,
        service_integration=ServiceIntegrationConfig(
            service_type=ServiceType.CMS_TIER,
            ssg_engine=ssg_engine,
            integration_mode=integration_mode,
            cms_config=CMSProviderConfig(
                provider=cms_provider,
                admin_users=[contact_email],
                settings=cms_settings
            )
        )
    )


def tier1_technical_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    ssg_engine: str = "hugo",
    integration_mode: IntegrationMode = IntegrationMode.DIRECT
) -> ClientServiceConfig:
    """
    Template for Tier 1C: Technical clients ($360-960 setup | $0-50/month).

    For developers, agencies, and technical users comfortable with Git, Markdown,
    and basic web development.

    Example:
        client = tier1_technical_client("dev-agency", "Dev Agency", "devagency.com", "team@devagency.com")
    """
    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER1,
        management_model=ManagementModel.TECHNICAL,
        delivery_model=DeliveryModel.HOSTED,
        service_integration=ServiceIntegrationConfig(
            service_type=ServiceType.STATIC_SITE,
            ssg_engine=ssg_engine,
            integration_mode=integration_mode
        )
    )


def tier1_ecommerce_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    ecommerce_provider: str = "snipcart",
    ssg_engine: str = "eleventy",
    integration_mode: IntegrationMode = IntegrationMode.DIRECT,
    store_settings: Optional[Dict[str, Any]] = None
) -> ClientServiceConfig:
    """
    Template for Tier 1: E-commerce clients.

    For small businesses wanting simple e-commerce with static site performance.

    Example:
        client = tier1_ecommerce_client("tech-store", "Tech Store LLC", "techstore.com", "orders@techstore.com")
    """
    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER1,
        management_model=ManagementModel.DEVELOPER_MANAGED,
        delivery_model=DeliveryModel.HOSTED,
        service_integration=ServiceIntegrationConfig(
            service_type=ServiceType.ECOMMERCE_TIER,
            ssg_engine=ssg_engine,
            integration_mode=integration_mode,
            ecommerce_config=EcommerceProviderConfig(
                provider=ecommerce_provider,
                settings=store_settings or {}
            )
        )
    )


def tier1_composed_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    cms_provider: str = "tina",
    ecommerce_provider: str = "snipcart",
    ssg_engine: str = "astro",
    integration_mode: IntegrationMode = IntegrationMode.EVENT_DRIVEN,  # Default to event-driven for composition
    cms_settings: Optional[Dict[str, Any]] = None,
    ecommerce_settings: Optional[Dict[str, Any]] = None
) -> ClientServiceConfig:
    """
    Template for Tier 1: Composed Stack clients (CMS + E-commerce).

    For businesses needing both content management and e-commerce functionality.
    Defaults to event-driven integration for better composition.

    Example:
        client = tier1_composed_client("full-service", "Full Service Co", "fullservice.com", "admin@fullservice.com")
    """
    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER1,
        management_model=ManagementModel.SELF_MANAGED,
        delivery_model=DeliveryModel.HOSTED,
        service_integration=ServiceIntegrationConfig(
            service_type=ServiceType.COMPOSED_STACK,
            ssg_engine=ssg_engine,
            integration_mode=integration_mode,
            cms_config=CMSProviderConfig(
                provider=cms_provider,
                admin_users=[contact_email],
                settings=cms_settings or {}
            ),
            ecommerce_config=EcommerceProviderConfig(
                provider=ecommerce_provider,
                settings=ecommerce_settings or {}
            )
        )
    )


def tier2_professional_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    service_type: ServiceType = ServiceType.CMS_TIER,
    cms_provider: str = "contentful",
    ssg_engine: str = "gatsby",
    integration_mode: IntegrationMode = IntegrationMode.DIRECT
) -> ClientServiceConfig:
    """
    Template for Tier 2: Professional Solutions clients ($2,400-9,600 setup | $50-400/month).

    For growing businesses, established service providers, and content-heavy sites.
    More advanced than tier1 with better CMS integration and performance.

    Example:
        client = tier2_professional_client("growing-biz", "Growing Business", "growingbiz.com", "admin@growingbiz.com")
    """
    service_integration = ServiceIntegrationConfig(
        service_type=service_type,
        ssg_engine=ssg_engine,
        integration_mode=integration_mode
    )

    # Add CMS config for CMS-enabled services
    if service_type in [ServiceType.CMS_TIER, ServiceType.COMPOSED_STACK]:
        service_integration.cms_config = CMSProviderConfig(
            provider=cms_provider,
            admin_users=[contact_email],
            settings={}
        )

    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER2,
        delivery_model=DeliveryModel.HOSTED,
        service_integration=service_integration
    )


def tier3_enterprise_client(
    client_id: str,
    company_name: str,
    domain: str,
    contact_email: str,
    delivery_model: DeliveryModel = DeliveryModel.HOSTED,
    service_type: ServiceType = ServiceType.COMPOSED_STACK,
    integration_mode: IntegrationMode = IntegrationMode.EVENT_DRIVEN,  # Enterprise benefits from event-driven
    cms_provider: str = "contentful",
    ecommerce_provider: str = "shopify_advanced",
    ssg_engine: str = "nextjs"
) -> ClientServiceConfig:
    """
    Template for Tier 3: Enterprise clients ($6,000-60,000+ setup | $250-2,000/month).

    For enterprise clients who need flexible delivery and advanced integration.
    Defaults to event-driven architecture for better scalability.

    Example:
        client = tier3_enterprise_client("bigcorp", "BigCorp Industries", "bigcorp.com", "devops@bigcorp.com")
    """
    service_integration = ServiceIntegrationConfig(
        service_type=service_type,
        ssg_engine=ssg_engine,
        integration_mode=integration_mode
    )

    # Add providers for composed stacks
    if service_type == ServiceType.COMPOSED_STACK:
        service_integration.cms_config = CMSProviderConfig(
            provider=cms_provider,
            admin_users=[contact_email],
            settings={}
        )
        service_integration.ecommerce_config = EcommerceProviderConfig(
            provider=ecommerce_provider,
            settings={}
        )

    return ClientServiceConfig(
        client_id=client_id,
        company_name=company_name,
        domain=domain,
        contact_email=contact_email,
        service_tier=ServiceTier.TIER3,
        delivery_model=delivery_model,
        service_integration=service_integration
    )


# Export all templates
__all__ = [
    "tier1_developer_managed_client",
    "tier1_self_managed_client",
    "tier1_technical_client",
    "tier1_ecommerce_client",
    "tier1_composed_client",
    "tier2_professional_client",
    "tier3_enterprise_client"
]