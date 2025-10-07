"""
Client Configuration System for Dual-Delivery Web Services Platform

Supports the complete service delivery model:
- Hosted-Only Solutions: Deploy and manage in our AWS account
- Dual-Delivery Solutions: Support both hosted mode and consulting template delivery
- Migration Services: Legacy platform migrations to modern solutions

Aligned with 30 hosted stack variants across Tier 1, Tier 2, and Dual-Delivery service tiers.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Dict, Optional, Literal
import re


class ClientConfig(BaseModel):
    """
    Complete client configuration for dual-delivery web services platform.

    Supports hosted solutions, consulting templates, and migration services.
    Aligned with current CDK strategy and service delivery models.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [{
                "client_id": "acme-corp",
                "company_name": "Acme Corporation",
                "service_tier": "tier2",
                "stack_type": "wordpress_ecs_professional_stack",
                "domain": "acme.com",
                "contact_email": "admin@acme.com"
            }]
        }
    )

    # Core identifiers - these uniquely identify the client
    client_id: str = Field(
        ...,
        description="URL-safe identifier used for AWS resource names, file paths",
        pattern=r'^[a-z0-9-]+$'
    )

    company_name: str = Field(..., description="Human readable name for invoices, emails")

    # Service delivery configuration
    service_tier: Literal["tier1", "tier2", "dual_delivery"] = Field(
        ...,
        description="Service tier for cost tracking and resource allocation"
    )

    stack_type: str = Field(
        ...,
        description="Technology stack variant from CDK strategy (30 hosted variants)"
    )

    # Dual-delivery support (only for dual-delivery service tier)
    deployment_mode: Literal["hosted", "template"] = Field(
        default="hosted",
        description="Deployment mode for dual-delivery stacks"
    )

    domain: str = Field(..., description="Primary domain where website will be hosted")
    environment: Literal["prod", "staging", "dev"] = Field(
        default="prod",
        description="Deployment environment"
    )

    # Contact and billing - who pays and who to call when things break
    contact_email: str = Field(..., description="Primary contact for technical issues")

    # Migration support (optional - only for migration clients)
    migration_source: Optional[str] = Field(
        default=None,
        description="Source platform for migration clients (e.g., magento_1x, prestashop_16x)"
    )

    # AWS deployment settings - where this actually gets deployed
    aws_account: Optional[str] = Field(
        default=None,
        description="Client AWS account ID for template mode deployments"
    )

    region: str = Field(
        default="us-east-1",
        description="AWS region for deployment"
    )

    # Optional customizations - escape hatch for special client needs
    custom_settings: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional configuration settings"
    )

    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v):
        """Validate client_id format for AWS resource naming."""
        if v.startswith('-') or v.endswith('-'):
            raise ValueError("client_id cannot start or end with hyphens")

        if '--' in v:
            raise ValueError("client_id cannot contain consecutive hyphens")

        return v

    @field_validator('contact_email')
    @classmethod
    def validate_email(cls, v):
        """Basic email validation."""
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        """Basic domain validation."""
        if '.' not in v or ' ' in v:
            raise ValueError("Invalid domain format")
        return v

    @model_validator(mode='after')
    def validate_deployment_mode(self):
        """Validate deployment mode consistency."""
        if self.deployment_mode == 'template' and self.service_tier != 'dual_delivery':
            raise ValueError("Template deployment mode only available for dual_delivery service tier")
        return self

    @field_validator('stack_type')
    @classmethod
    def validate_stack_type(cls, v):
        """Validate stack type against known hosted variants."""
        # Define the 30 hosted stack variants from CDK strategy
        hosted_stack_variants = {
            # Tier 1 Hosted-Only Stacks (11 variants)
            "eleventy_marketing_stack",
            "astro_portfolio_stack",
            "jekyll_github_stack",
            "eleventy_decap_cms_stack",
            "astro_tina_cms_stack",
            "astro_sanity_stack",
            "gatsby_contentful_stack",
            "astro_template_basic_stack",
            "eleventy_snipcart_stack",
            "astro_foxy_stack",
            "shopify_standard_dns_stack",

            # Tier 2 Hosted-Only Stacks (7 variants)
            "astro_advanced_cms_stack",
            "gatsby_headless_cms_stack",
            "nextjs_professional_headless_cms_stack",
            "nuxtjs_professional_headless_cms_stack",
            "wordpress_lightsail_stack",
            "wordpress_ecs_professional_stack",
            "shopify_aws_basic_integration_stack",

            # Dual-Delivery Stacks (5 variants - when used in hosted mode)
            "shopify_advanced_aws_integration_stack",
            "headless_shopify_custom_frontend_stack",
            "amplify_custom_development_stack",
            "fastapi_pydantic_api_stack",
            "fastapi_react_vue_stack",

            # Migration Support Stacks (7 variants)
            "migration_assessment_stack",
            "magento_migration_stack",
            "prestashop_migration_stack",
            "opencart_migration_stack",
            "wordpress_migration_stack",
            "legacy_cms_migration_stack",
            "custom_platform_migration_stack"
        }

        if v not in hosted_stack_variants:
            raise ValueError(f"Unknown stack type: {v}. Must be one of the 30 hosted stack variants.")

        return v

    @property
    def deployment_name(self) -> str:
        """
        CDK deployment name: AcmeCorp-Prod-WordPressLightsail

        This is what you'll see in `cdk list` and `cdk deploy X`.
        It's human-readable and follows CDK naming conventions.

        Examples:
        - acme-corp + prod + wordpress_lightsail = AcmeCorp-Prod-WordPressLightsail
        - johns-pizza + staging + static_marketing = JohnsPizza-Staging-StaticMarketing
        """
        client_part = ''.join(word.capitalize() for word in self.client_id.split('-'))
        env_part = self.environment.capitalize()
        stack_part = ''.join(word.capitalize() for word in self.stack_type.split('_'))
        return f"{client_part}-{env_part}-{stack_part}"

    @property
    def resource_prefix(self) -> str:
        """
        AWS resource naming prefix: acme-corp-prod

        Used for naming individual AWS resources like S3 buckets, RDS instances, etc.
        Keeps it short and URL-safe for resource names that have length limits.
        """
        return f"{self.client_id}-{self.environment}"

    @property
    def tags(self) -> Dict[str, str]:
        """
        Standard AWS tags for cost allocation and resource management.

        These tags get applied to ALL AWS resources for this client.
        Super important for:
        1. Cost tracking - see exactly what each client costs you
        2. Resource management - find all resources for a client
        3. Billing - charge clients based on actual AWS usage
        """
        tags = {
            # Core identification - who this belongs to
            "Client": self.client_id,
            "Company": self.company_name,
            "Environment": self.environment,
            "StackType": self.stack_type,
            "ServiceTier": self.service_tier,
            "DeploymentMode": self.deployment_mode,

            # Cost allocation - for AWS Cost Explorer and billing
            "BillingGroup": f"{self.client_id}-{self.environment}",  # Group costs together
            "CostCenter": self.client_id,                            # Roll up all client costs

            # Operational - who to contact when things break
            "Contact": self.contact_email,
            "ManagedBy": "CDK",      # How this was deployed
            "Project": "WebServices", # Your business

            # Migration tracking (if applicable)
            "MigrationSource": self.migration_source or "new_development"
        }

        # Allow custom tags via custom_settings like "tag:Department": "Marketing"
        for key, value in self.custom_settings.items():
            if key.startswith('tag:'):
                tag_name = key[4:]  # Remove 'tag:' prefix
                tags[tag_name] = value

        return tags

    def to_dict(self) -> Dict:
        """
        Convert to dictionary for JSON serialization.

        Use this to save client configs to JSON files:
        json.dump(client.to_dict(), open('acme-corp.json', 'w'))
        """
        return {
            "client_id": self.client_id,
            "company_name": self.company_name,
            "service_tier": self.service_tier,
            "stack_type": self.stack_type,
            "deployment_mode": self.deployment_mode,
            "domain": self.domain,
            "environment": self.environment,
            "contact_email": self.contact_email,
            "migration_source": self.migration_source,
            "aws_account": self.aws_account,
            "region": self.region,
            "custom_settings": self.custom_settings
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ClientConfig':
        """
        Create from dictionary (JSON deserialization).

        Use this to load client configs from JSON files:
        client = ClientConfig.from_dict(json.load(open('acme-corp.json')))
        """
        return cls.model_validate(data)

    def __str__(self) -> str:
        """Human readable representation for debugging/logging"""
        mode_info = f" [{self.deployment_mode}]" if self.service_tier == "dual_delivery" else ""
        migration_info = f" (migrating from {self.migration_source})" if self.migration_source else ""
        return f"{self.company_name} ({self.client_id}) - {self.service_tier.upper()} {self.stack_type}{mode_info} in {self.environment}{migration_info}"


def create_client_config(
    client_id: str,
    company_name: str,
    service_tier: str,
    stack_type: str,
    domain: str,
    contact_email: str,
    environment: str = "prod",
    deployment_mode: str = "hosted",
    **kwargs
) -> ClientConfig:
    """
    Factory function to create a client configuration.

    Args:
        client_id: URL-safe identifier (e.g., "acme-corp")
        company_name: Human readable name (e.g., "Acme Corporation")
        service_tier: Service tier ("tier1", "tier2", "dual_delivery")
        stack_type: Technology stack from CDK strategy (30 hosted variants)
        domain: Client domain (e.g., "acme.com")
        contact_email: Primary contact email
        environment: Deployment environment ("prod", "staging", "dev")
        deployment_mode: Deployment mode ("hosted", "template") - only for dual_delivery tier
        **kwargs: Additional settings (migration_source, aws_account, region, custom_settings)

    Returns:
        ClientConfig: Validated client configuration
    """
    return ClientConfig(
        client_id=client_id,
        company_name=company_name,
        service_tier=service_tier,
        stack_type=stack_type,
        domain=domain,
        environment=environment,
        contact_email=contact_email,
        deployment_mode=deployment_mode,
        **kwargs
    )


# Quick templates for common client types
# These are just shortcuts - you can create configs manually too

def individual_client(client_id: str, company_name: str, domain: str, contact_email: str) -> ClientConfig:
    """
    Template for individual/freelancer clients (Tier 1).

    Assumes they want a simple marketing site using Eleventy (most common for individuals).
    Low cost, fast performance, easy to manage.

    Example:
        client = individual_client("johns-design", "John's Design Studio", "johnsdesign.com", "john@johnsdesign.com")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier1",
        stack_type="eleventy_marketing_stack",  # Most common for individuals
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def small_business_client(client_id: str, company_name: str, domain: str, contact_email: str) -> ClientConfig:
    """
    Template for small business clients (Tier 2).

    Assumes they want WordPress ECS Professional (most common for small businesses).
    More scalable than Lightsail, suitable for growing businesses.

    Example:
        client = small_business_client("acme-corp", "Acme Corporation", "acme.com", "admin@acme.com")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier2",
        stack_type="wordpress_ecs_professional_stack",
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def enterprise_client(client_id: str, company_name: str, domain: str, contact_email: str,
                     deployment_mode: str = "hosted") -> ClientConfig:
    """
    Template for enterprise clients (Dual-Delivery).

    Assumes they want FastAPI + React/Vue (most common for enterprise).
    These clients usually have complex requirements and may prefer template delivery.

    Example:
        # Hosted mode
        client = enterprise_client("bigcorp", "BigCorp Industries", "bigcorp.com", "devops@bigcorp.com")

        # Template mode
        client = enterprise_client("tech-corp", "Tech Corp", "techcorp.com", "devops@techcorp.com", "template")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="dual_delivery",
        stack_type="fastapi_react_vue_stack",
        domain=domain,
        contact_email=contact_email,
        deployment_mode=deployment_mode,
        environment="prod"
    )


def astro_client(client_id: str, company_name: str, domain: str, contact_email: str,
                advanced: bool = False) -> ClientConfig:
    """
    Template for Astro-based clients.

    Args:
        advanced: If True, uses Tier 2 advanced CMS setup. If False, uses Tier 1 basic setup.

    Example:
        # Tier 1 basic
        client = astro_client("design-studio", "Design Studio", "designstudio.com", "admin@designstudio.com")

        # Tier 2 advanced
        client = astro_client("content-biz", "Content Business", "contentbiz.com", "admin@contentbiz.com", advanced=True)
    """
    stack_type = "astro_advanced_cms" if advanced else "astro_template_basic"

    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def wordpress_client(client_id: str, company_name: str, domain: str, contact_email: str,
                    enterprise: bool = False) -> ClientConfig:
    """
    Template for WordPress-based clients.

    Args:
        enterprise: If True, uses Tier 3 enterprise ECS setup. If False, uses Tier 2 professional setup.

    Example:
        # Tier 2 professional
        client = wordpress_client("local-business", "Local Business", "localbusiness.com", "admin@localbusiness.com")

        # Tier 3 enterprise
        client = wordpress_client("bigcorp", "BigCorp", "bigcorp.com", "devops@bigcorp.com", enterprise=True)
    """
    stack_type = "wordpress_ecs_enterprise" if enterprise else "wordpress_ecs_professional"

    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def shopify_client(client_id: str, company_name: str, domain: str, contact_email: str,
                  integration_level: str = "basic") -> ClientConfig:
    """
    Template for Shopify-based clients.

    Args:
        integration_level: "dns" (Tier 1), "basic" (Tier 2), "advanced" (Tier 2/3), "headless" (Tier 3)

    Example:
        # Tier 1 DNS-only
        client = shopify_client("small-shop", "Small Shop", "smallshop.com", "admin@smallshop.com", "dns")

        # Tier 2 basic integration
        client = shopify_client("growing-shop", "Growing Shop", "growingshop.com", "admin@growingshop.com", "basic")

        # Tier 3 headless
        client = shopify_client("premium-shop", "Premium Shop", "premiumshop.com", "admin@premiumshop.com", "headless")
    """
    stack_mapping = {
        "dns": "shopify_standard_dns",
        "basic": "shopify_aws_basic_integration",
        "advanced": "shopify_aws_advanced_integration",
        "headless": "headless_shopify_custom_frontend"
    }

    stack_type = stack_mapping.get(integration_level, "shopify_aws_basic_integration")

    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def nextjs_client(client_id: str, company_name: str, domain: str, contact_email: str,
                 enterprise: bool = False) -> ClientConfig:
    """
    Template for Next.js-based clients.

    Args:
        enterprise: If True, uses Tier 3 enterprise applications. If False, uses Tier 2 professional.

    Example:
        # Tier 2 professional
        client = nextjs_client("modern-biz", "Modern Business", "modernbiz.com", "admin@modernbiz.com")

        # Tier 3 enterprise
        client = nextjs_client("tech-corp", "Tech Corp", "techcorp.com", "devops@techcorp.com", enterprise=True)
    """
    stack_type = "nextjs_enterprise_applications" if enterprise else "nextjs_professional_headless_cms"

    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )