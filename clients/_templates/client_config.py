"""
Client Configuration System for Dual-Delivery Web Services Platform

Supports the complete service delivery model:
- Hosted-Only Solutions: Deploy and manage in our AWS account
- Dual-Delivery Solutions: Support both hosted mode and consulting template delivery
- Migration Services: Legacy platform migrations to modern solutions

✅ UPDATED: Supports flexible architecture with CMS tiers and e-commerce provider tiers enabling client SSG engine choice.
"""

from typing import Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from models.cms_config import CMSIntegrationConfig


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
            "examples": [
                {
                    "client_id": "content-business",
                    "company_name": "Content Business Co",
                    "service_tier": "tier1",
                    "stack_type": "tina_cms_tier",
                    "ssg_engine": "astro",
                    "domain": "contentbiz.com",
                    "contact_email": "admin@contentbiz.com",
                    "cms_config": {
                        "cms": {
                            "provider": "tina",
                            "admin_users": ["admin@contentbiz.com"],
                            "content_settings": {
                                "repository": "contentbiz-site",
                                "repository_owner": "contentbiz",
                                "branch": "main"
                            }
                        },
                        "ssg_engine": "astro"
                    }
                },
                {
                    "client_id": "tech-store",
                    "company_name": "Tech Store LLC",
                    "service_tier": "tier1",
                    "stack_type": "snipcart_ecommerce_tier",
                    "ssg_engine": "hugo",
                    "domain": "techstore.com",
                    "contact_email": "orders@techstore.com"
                },
                {
                    "client_id": "acme-corp",
                    "company_name": "Acme Corporation",
                    "service_tier": "tier2",
                    "stack_type": "wordpress_ecs_professional_stack",
                    "domain": "acme.com",
                    "contact_email": "admin@acme.com"
                }
            ]
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
    service_tier: Literal["tier1", "tier2", "tier3"] = Field(
        ...,
        description="Primary service tier (tier1: Essential, tier2: Professional, tier3: Enterprise)"
    )

    # Management model for tier1 services (Tier 1A, 1B, 1C)
    management_model: Optional[Literal["developer_managed", "self_managed", "technical"]] = Field(
        default=None,
        description="Service management model for tier1: developer_managed (1A), self_managed (1B), technical (1C)"
    )

    # Service delivery model (applies to all tiers)
    delivery_model: Literal["hosted", "consulting_template"] = Field(
        default="hosted",
        description="Service delivery: hosted (we manage) or consulting_template (client manages)"
    )

    # Service type within tier (especially for tier3)
    service_type: Optional[Literal["dual_delivery", "consultation", "migration", "standard"]] = Field(
        default="standard",
        description="Specific service type: dual_delivery, consultation, migration, or standard"
    )

    stack_type: str = Field(
        ...,
        description="Service type: static sites, CMS tiers (decap_cms_tier, tina_cms_tier, etc.), or e-commerce tiers (snipcart_ecommerce_tier, etc.)"
    )

    ssg_engine: Optional[str] = Field(
        default=None,
        description="SSG engine choice for flexible tiers (hugo, eleventy, astro, gatsby, nextjs, nuxt). Required for CMS/e-commerce tiers, ignored for static sites."
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

    # CMS Configuration (for CMS-enabled stacks)
    cms_config: Optional[CMSIntegrationConfig] = Field(
        default=None,
        description="CMS integration configuration for CMS-enabled stack types"
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
    def validate_service_configuration(self):
        """Validate service configuration consistency."""
        
        # Validate management model is only for tier1
        if self.management_model and self.service_tier != 'tier1':
            raise ValueError("Management model only applies to tier1 services")
        
        # Validate tier1 requires management model
        if self.service_tier == 'tier1' and not self.management_model:
            raise ValueError("Tier1 services must specify management_model: developer_managed, self_managed, or technical")
        
        # Validate consulting_template delivery model restrictions
        if self.delivery_model == 'consulting_template':
            # Only certain service types support consulting templates
            if self.service_tier == 'tier1':
                raise ValueError("Tier1 services do not support consulting_template delivery")
            if self.service_tier == 'tier2' and self.service_type not in ['dual_delivery', 'standard']:
                raise ValueError("Tier2 consulting_template only available for dual_delivery or standard services")
        
        # Validate service_type consistency
        if self.service_tier == 'tier3':
            if self.service_type == 'standard' and self.delivery_model == 'consulting_template':
                # Tier3 standard services can be consulting templates
                pass
            elif self.service_type not in ['dual_delivery', 'consultation', 'migration', 'standard']:
                raise ValueError("Tier3 services must specify service_type: dual_delivery, consultation, migration, or standard")
        
        return self

    @model_validator(mode='after')
    def validate_cms_configuration(self):
        """Validate CMS configuration for CMS-enabled stacks."""

        # CMS tiers that require CMS configuration
        cms_tiers = {
            "decap_cms_tier", "tina_cms_tier", "sanity_cms_tier",
            "contentful_cms_tier", "strapi_cms_tier", "ghost_cms_tier"
        }

        if self.stack_type in cms_tiers:
            if not self.cms_config:
                raise ValueError(f"Stack type '{self.stack_type}' requires cms_config to be specified")

            # Validate CMS configuration
            try:
                self.cms_config.validate_integration()
            except Exception as e:
                raise ValueError(f"Invalid CMS configuration: {str(e)}")

            # Ensure CMS provider matches stack type expectations
            expected_providers = {
                "decap_cms_tier": ["decap"],
                "tina_cms_tier": ["tina"],
                "sanity_cms_tier": ["sanity"],
                "contentful_cms_tier": ["contentful"],
                "strapi_cms_tier": ["strapi"],
                "ghost_cms_tier": ["ghost"]
            }

            if self.stack_type in expected_providers:
                expected = expected_providers[self.stack_type]
                if self.cms_config.cms.provider not in expected:
                    raise ValueError(
                        f"Stack type '{self.stack_type}' expects CMS provider to be one of {expected}, "
                        f"but got '{self.cms_config.cms.provider}'"
                    )

            # Ensure SSG engine is compatible with CMS provider
            if self.ssg_engine and self.cms_config.ssg_engine:
                if self.ssg_engine != self.cms_config.ssg_engine:
                    raise ValueError(
                        f"SSG engine mismatch: client config specifies '{self.ssg_engine}' "
                        f"but CMS config specifies '{self.cms_config.ssg_engine}'"
                    )
            elif self.ssg_engine:
                # Set CMS config SSG engine from client config
                self.cms_config.ssg_engine = self.ssg_engine

        elif self.cms_config:
            # Warn if CMS config is provided for non-CMS stack
            print(f"⚠️  Warning: CMS configuration provided for non-CMS stack '{self.stack_type}' - will be ignored")

        return self

    @model_validator(mode='after')
    def validate_stack_service_alignment(self):
        """Validate stack type matches service tier and management model."""
        
        # ✅ UPDATED: Flexible Architecture - Service Types & Tiers (not hardcoded stacks)
        # Static Sites (implemented as individual stacks)
        tier1_developer_managed = {"eleventy_marketing_stack", "astro_portfolio_stack", "jekyll_github_stack"}
        tier1_self_managed = {"astro_template_basic_stack"}  # Basic Astro template
        tier1_technical = {"jekyll_github_stack"}

        # Flexible Service Tiers (implemented via factory patterns)
        tier1_cms_tiers = {"decap_cms_tier", "tina_cms_tier", "sanity_cms_tier", "contentful_cms_tier"}
        tier1_ecommerce_tiers = {"snipcart_ecommerce_tier", "foxy_ecommerce_tier", "shopify_basic_tier", "shopify_standard_dns_stack"}

        # All valid tier1 stack types (combine static + flexible tiers)
        all_tier1_stacks = tier1_developer_managed | tier1_self_managed | tier1_technical | tier1_cms_tiers | tier1_ecommerce_tiers
        tier2_stacks = {"astro_advanced_cms_stack", "gatsby_headless_cms_stack", "nextjs_professional_headless_cms_stack", "nuxtjs_professional_headless_cms_stack", "wordpress_lightsail_stack", "wordpress_ecs_professional_stack", "wordpress_headless_basic_stack", "shopify_aws_basic_integration_stack", "fastapi_pydantic_api_stack"}
        tier3_dual_delivery = {"shopify_advanced_aws_integration_stack", "headless_shopify_custom_frontend_stack", "amplify_custom_development_stack", "fastapi_pydantic_api_stack", "fastapi_react_vue_stack"}
        tier3_migration = {"migration_assessment_stack", "magento_migration_stack", "prestashop_migration_stack", "opencart_migration_stack", "wordpress_migration_stack", "wordpress_headless_professional_stack", "wordpress_woocommerce_headless_stack", "legacy_cms_migration_stack", "custom_platform_migration_stack"}
        tier3_consultation = {"fastapi_react_vue_stack", "amplify_custom_development_stack", "nextjs_enterprise_applications_stack", "nuxtjs_enterprise_applications_stack", "wordpress_custom_development_stack", "aws_serverless_custom_stack"}
        
        # ✅ UPDATED: Flexible Architecture Validation
        if self.service_tier == 'tier1':
            # Validate stack type is valid for tier1
            if self.stack_type not in all_tier1_stacks:
                raise ValueError(f"Stack '{self.stack_type}' not valid for tier1. Available: {list(all_tier1_stacks)}")

            # Validate management model compatibility
            if self.management_model == 'developer_managed':
                # Developer-managed: static sites + any CMS/e-commerce tier (we manage content)
                valid_for_developer = tier1_developer_managed | tier1_cms_tiers | tier1_ecommerce_tiers
                if self.stack_type not in valid_for_developer:
                    raise ValueError(f"Stack '{self.stack_type}' not compatible with developer_managed model")

            elif self.management_model == 'self_managed':
                # Self-managed: CMS tiers only (client manages content via CMS interface)
                valid_for_self = tier1_self_managed | tier1_cms_tiers
                if self.stack_type not in valid_for_self:
                    raise ValueError(f"Stack '{self.stack_type}' requires CMS interface for self_managed model")

            elif self.management_model == 'technical':
                # Technical: static sites only (client manages code directly)
                if self.stack_type not in tier1_technical:
                    raise ValueError(f"Stack '{self.stack_type}' not compatible with technical model. Use: {list(tier1_technical)}")
        
        # Validate tier2 stacks
        elif self.service_tier == 'tier2' and self.stack_type not in tier2_stacks:
            raise ValueError(f"Stack '{self.stack_type}' not compatible with tier2. Use tier2 stacks: {list(tier2_stacks)}")
        
        # Validate tier3 stacks match service type
        elif self.service_tier == 'tier3':
            if self.service_type == 'dual_delivery' and self.stack_type not in tier3_dual_delivery:
                raise ValueError(f"Stack '{self.stack_type}' not compatible with dual_delivery. Use: {list(tier3_dual_delivery)}")
            elif self.service_type == 'migration' and self.stack_type not in tier3_migration:
                raise ValueError(f"Stack '{self.stack_type}' not compatible with migration services. Use: {list(tier3_migration)}")
            elif self.service_type == 'consultation' and self.stack_type not in tier3_consultation:
                raise ValueError(f"Stack '{self.stack_type}' not compatible with consultation services. Use: {list(tier3_consultation)}")
        
        return self

    @model_validator(mode='after')
    def validate_ssg_engine_compatibility(self):
        """Validate SSG engine choice is compatible with selected stack type."""

        # Define SSG compatibility for flexible tiers
        flexible_tier_ssg_compatibility = {
            # CMS Tiers
            "decap_cms_tier": ["hugo", "eleventy", "astro", "gatsby"],
            "tina_cms_tier": ["astro", "eleventy", "nextjs", "nuxt"],
            "sanity_cms_tier": ["astro", "gatsby", "nextjs", "nuxt"],
            "contentful_cms_tier": ["gatsby", "astro", "nextjs", "nuxt"],

            # E-commerce Provider Tiers
            "snipcart_ecommerce_tier": ["hugo", "eleventy", "astro", "gatsby"],
            "foxy_ecommerce_tier": ["hugo", "eleventy", "astro", "gatsby"],
            "shopify_basic_tier": ["eleventy", "astro", "nextjs", "nuxt"],
            "shopify_advanced_tier": ["astro", "nextjs", "nuxt", "gatsby"]
        }

        # Static sites don't need SSG engine specification
        static_sites = {"eleventy_marketing_stack", "astro_portfolio_stack", "jekyll_github_stack", "astro_template_basic_stack", "shopify_standard_dns_stack"}

        if self.stack_type in flexible_tier_ssg_compatibility:
            # Flexible tiers REQUIRE SSG engine specification
            if not self.ssg_engine:
                raise ValueError(f"SSG engine required for '{self.stack_type}'. Choose from: {flexible_tier_ssg_compatibility[self.stack_type]}")

            # Validate SSG engine is compatible with the tier
            if self.ssg_engine not in flexible_tier_ssg_compatibility[self.stack_type]:
                raise ValueError(f"SSG engine '{self.ssg_engine}' not compatible with '{self.stack_type}'. Choose from: {flexible_tier_ssg_compatibility[self.stack_type]}")

        elif self.stack_type in static_sites:
            # Static sites ignore SSG engine (warn if specified)
            if self.ssg_engine:
                print(f"⚠️  Warning: SSG engine '{self.ssg_engine}' ignored for static site '{self.stack_type}'")

        else:
            # Other stack types (tier2, tier3) ignore SSG engine for now
            if self.ssg_engine:
                print(f"⚠️  Warning: SSG engine '{self.ssg_engine}' ignored for '{self.stack_type}'")

        return self

    @field_validator('stack_type')
    @classmethod
    def validate_stack_type(cls, v):
        """Validate stack type against service tier and management model."""
        
        # ✅ UPDATED: Flexible Architecture - Tier 1 stack variants
        # Static Sites (implemented as individual stacks)
        tier1_static_sites = {
            "eleventy_marketing_stack",      # Static Marketing Sites
            "astro_portfolio_stack",         # Portfolio/Business Sites
            "jekyll_github_stack",           # Documentation Sites
            "astro_template_basic_stack",    # Astro + Basic Headless CMS
        }

        # Flexible Service Tiers (implemented via factory patterns)
        tier1_flexible_tiers = {
            # CMS Tiers (client chooses SSG engine)
            "decap_cms_tier",                # Hugo/Eleventy/Astro/Gatsby choice
            "tina_cms_tier",                 # Astro/Eleventy/Next.js/Nuxt choice
            "sanity_cms_tier",               # Astro/Gatsby/Next.js/Nuxt choice
            "contentful_cms_tier",           # Gatsby/Astro/Next.js/Nuxt choice

            # E-commerce Provider Tiers (client chooses SSG engine)
            "snipcart_ecommerce_tier",       # Hugo/Eleventy/Astro/Gatsby choice
            "foxy_ecommerce_tier",           # Hugo/Eleventy/Astro/Gatsby choice
            "shopify_basic_tier",            # Eleventy/Astro/Next.js/Nuxt choice
            "shopify_standard_dns_stack",    # DNS-only (no SSG choice needed)
        }

        # Combined Tier 1 stacks
        tier1_all_stacks = tier1_static_sites.union(tier1_flexible_tiers)

        # Tier 2 stack variants
        tier2_stacks = {
            "astro_advanced_cms_stack",              # Advanced CMS solutions
            "gatsby_headless_cms_stack",             # Content-heavy sites
            "nextjs_professional_headless_cms_stack", # Professional frameworks
            "nuxtjs_professional_headless_cms_stack", # Professional frameworks
            "wordpress_lightsail_stack",             # WordPress solutions
            "wordpress_ecs_professional_stack",      # WordPress professional
            "shopify_aws_basic_integration_stack",   # Enhanced Shopify
            "fastapi_pydantic_api_stack",            # Python backend (dual-delivery capable)
        }

        # Tier 3 stack variants organized by service type
        tier3_dual_delivery = {
            "shopify_advanced_aws_integration_stack",
            "headless_shopify_custom_frontend_stack",
            "amplify_custom_development_stack",
            "fastapi_pydantic_api_stack",
            "fastapi_react_vue_stack",
        }
        
        tier3_migration = {
            "migration_assessment_stack",
            "magento_migration_stack", 
            "prestashop_migration_stack",
            "opencart_migration_stack",
            "wordpress_migration_stack",
            "legacy_cms_migration_stack",
            "custom_platform_migration_stack"
        }
        
        tier3_consultation = {
            "fastapi_react_vue_stack",
            "amplify_custom_development_stack",
            "nextjs_enterprise_applications_stack",
            "nuxtjs_enterprise_applications_stack",
            "wordpress_custom_development_stack",
            "aws_serverless_custom_stack"
        }
        
        tier3_standard = tier3_dual_delivery.union(tier3_migration).union(tier3_consultation)

        # All valid stacks (updated for flexible architecture)
        all_stacks = (tier1_all_stacks.union(tier2_stacks).union(tier3_standard))

        if v not in all_stacks:
            raise ValueError(f"Unknown stack type: {v}. Must be one of the documented stack variants.")

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
            "DeliveryModel": self.delivery_model,

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

        # Add service-specific tags
        if self.management_model:
            tags["ManagementModel"] = self.management_model
        if self.service_type and self.service_type != "standard":
            tags["ServiceType"] = self.service_type

        # Allow custom tags via custom_settings like "tag:Department": "Marketing"
        for key, value in self.custom_settings.items():
            if key.startswith('tag:'):
                tag_name = key[4:]  # Remove 'tag:' prefix
                tags[tag_name] = value

        return tags

    def get_cms_provider_instance(self):
        """
        Get configured CMS provider instance if CMS is enabled.

        Returns:
            CMSProvider instance or None if no CMS configuration

        Example:
            if client.has_cms():
                provider = client.get_cms_provider_instance()
                env_vars = provider.get_environment_variables()
        """
        if not self.cms_config:
            return None

        return self.cms_config.get_provider_instance()

    def has_cms(self) -> bool:
        """Check if this client configuration includes CMS integration"""
        return self.cms_config is not None

    def get_cms_environment_variables(self) -> Dict[str, str]:
        """
        Get CMS environment variables for stack deployment.

        Returns:
            Dict of environment variables needed for CMS integration
        """
        if not self.has_cms():
            return {}

        provider = self.get_cms_provider_instance()
        if not provider:
            return {}

        return provider.get_environment_variables()

    def setup_cms_infrastructure(self, stack):
        """
        Set up CMS infrastructure on the CDK stack.

        Args:
            stack: CDK stack instance to add CMS resources to
        """
        if not self.has_cms():
            return

        provider = self.get_cms_provider_instance()
        if provider:
            provider.setup_infrastructure(stack)

    def validate_cms_compatibility(self) -> bool:
        """
        Validate that the CMS configuration is compatible with the stack type and SSG engine.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is incompatible
        """
        if not self.has_cms():
            return True

        # This validation is also done in model validators, but can be called explicitly
        return self.cms_config.validate_integration()

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
            "management_model": self.management_model,
            "delivery_model": self.delivery_model,
            "service_type": self.service_type,
            "stack_type": self.stack_type,
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
        
        # Build service description
        service_parts = [self.service_tier.upper()]
        
        if self.service_tier == 'tier1' and self.management_model:
            service_parts.append(f"({self.management_model.replace('_', '-')})")
        elif self.service_tier == 'tier3' and self.service_type != 'standard':
            service_parts.append(f"({self.service_type})")
        
        if self.delivery_model == 'consulting_template':
            service_parts.append("[consulting]")
        
        service_desc = " ".join(service_parts)
        
        migration_info = f" (migrating from {self.migration_source})" if self.migration_source else ""
        return f"{self.company_name} ({self.client_id}) - {service_desc} {self.stack_type} in {self.environment}{migration_info}"


def create_client_config(
    client_id: str,
    company_name: str,
    service_tier: str,
    stack_type: str,
    domain: str,
    contact_email: str,
    environment: str = "prod",
    delivery_model: str = "hosted",
    cms_config: Optional[CMSIntegrationConfig] = None,
    **kwargs
) -> ClientConfig:
    """
    Factory function to create a client configuration.

    Args:
        client_id: URL-safe identifier (e.g., "acme-corp")
        company_name: Human readable name (e.g., "Acme Corporation")
        service_tier: Service tier ("tier1", "tier2", "tier3")
        stack_type: Technology stack from CDK strategy (30 hosted variants)
        domain: Client domain (e.g., "acme.com")
        contact_email: Primary contact email
        environment: Deployment environment ("prod", "staging", "dev")
        delivery_model: Service delivery ("hosted", "consulting_template")
        cms_config: CMS integration configuration for CMS-enabled stacks
        management_model: Management model for tier1 ("developer_managed", "self_managed", "technical")
        service_type: Service type for tier3 ("dual_delivery", "consultation", "migration", "standard")
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
        delivery_model=delivery_model,
        cms_config=cms_config,
        **kwargs
    )


# Quick templates for common client types
# These are just shortcuts - you can create configs manually too

def tier1_developer_managed_client(client_id: str, company_name: str, domain: str, contact_email: str,
                                  stack_type: str = "eleventy_marketing_stack") -> ClientConfig:
    """
    Template for Tier 1A: Developer-Managed clients ($480-1,440 setup | $75-125/month).
    
    For busy professionals who want "set it and forget it" service with professional maintenance.
    We handle all content updates, performance optimization, and maintenance.

    Example:
        client = tier1_developer_managed_client("law-firm", "Smith Law Firm", "smithlaw.com", "admin@smithlaw.com")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier1",
        management_model="developer_managed",
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def tier1_self_managed_client(client_id: str, company_name: str, domain: str, contact_email: str,
                             stack_type: str = "tina_cms_tier",
                             cms_provider: str = None,
                             repository: str = None,
                             repository_owner: str = None) -> ClientConfig:
    """
    Template for Tier 1B: Self-Managed clients ($720-2,400 setup | $50-75/month).

    For clients comfortable with CMS editing who want complete control over their content
    through easy-to-use web-based editing tools.

    ✅ UPDATED: Uses flexible CMS tier architecture - client chooses SSG engine within tier.
    Default: Tina CMS tier supports Astro/Eleventy/Next.js/Nuxt client choice.

    Example:
        # Uses Tina CMS tier (client can choose Astro, Eleventy, Next.js, or Nuxt)
        client = tier1_self_managed_client("content-biz", "Content Business", "contentbiz.com", "admin@contentbiz.com")

        # Or specify different CMS tier with custom provider
        client = tier1_self_managed_client(
            "budget-client", "Budget Co", "budget.com", "admin@budget.com",
            "decap_cms_tier", "decap", "budget-site", "budget-co"
        )
    """
    from models.cms_config import CMSIntegrationConfig, CMSConfig

    # Create CMS configuration if parameters provided
    cms_config = None
    if stack_type.endswith("_cms_tier"):
        # Infer CMS provider from stack type if not specified
        if not cms_provider:
            provider_mapping = {
                "decap_cms_tier": "decap",
                "tina_cms_tier": "tina",
                "sanity_cms_tier": "sanity",
                "contentful_cms_tier": "contentful"
            }
            cms_provider = provider_mapping.get(stack_type, "tina")

        # Create basic CMS configuration
        cms_settings = {"admin_users": [contact_email]}

        # Add git-based settings if provided
        if repository and repository_owner:
            cms_settings.update({
                "repository": repository,
                "repository_owner": repository_owner,
                "branch": "main",
                "content_path": "content"
            })

        cms_config = CMSIntegrationConfig(
            cms=CMSConfig(
                provider=cms_provider,
                admin_users=[contact_email],
                content_settings=cms_settings
            )
        )

    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier1",
        management_model="self_managed",
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod",
        cms_config=cms_config
    )


def tier1_technical_client(client_id: str, company_name: str, domain: str, contact_email: str,
                          stack_type: str = "jekyll_github_stack") -> ClientConfig:
    """
    Template for Tier 1C: Technical clients ($360-960 setup | $0-50/month).
    
    For developers, agencies, and technical users comfortable with Git, Markdown, 
    and basic web development.

    Example:
        client = tier1_technical_client("dev-agency", "Dev Agency", "devagency.com", "team@devagency.com")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier1",
        management_model="technical",
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def tier2_professional_client(client_id: str, company_name: str, domain: str, contact_email: str,
                             stack_type: str = "astro_advanced_cms_stack") -> ClientConfig:
    """
    Template for Tier 2: Professional Solutions clients ($2,400-9,600 setup | $50-400/month).

    For growing businesses, established service providers, and content-heavy sites.
    More advanced than tier1 with better CMS integration and performance.

    Example:
        client = tier2_professional_client("growing-biz", "Growing Business", "growingbiz.com", "admin@growingbiz.com")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier2",
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def tier3_dual_delivery_client(client_id: str, company_name: str, domain: str, contact_email: str,
                              delivery_model: str = "hosted",
                              stack_type: str = "fastapi_react_vue_stack") -> ClientConfig:
    """
    Template for Tier 3: Dual-Delivery clients ($6,000-60,000+ setup | $250-2,000/month).

    For enterprise clients who need flexible delivery - either hosted solutions or 
    consulting templates deployed in their own infrastructure.

    Example:
        # Hosted mode
        client = tier3_dual_delivery_client("bigcorp", "BigCorp Industries", "bigcorp.com", "devops@bigcorp.com")

        # Consulting template mode  
        client = tier3_dual_delivery_client("tech-corp", "Tech Corp", "techcorp.com", "devops@techcorp.com", "consulting_template")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier3",
        service_type="dual_delivery",
        delivery_model=delivery_model,
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


def tier3_migration_client(client_id: str, company_name: str, domain: str, contact_email: str,
                          stack_type: str = "magento_migration_stack",
                          migration_source: str = None) -> ClientConfig:
    """
    Template for Tier 3: Migration Services clients (40% of revenue).

    Specialized platform migration services to move from legacy systems to modern solutions.
    High-value, urgent projects with comprehensive migration support.

    Example:
        client = tier3_migration_client("legacy-store", "Legacy Store", "legacystore.com", "admin@legacystore.com", 
                                       "magento_migration_stack", "magento_1x")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier3",
        service_type="migration",
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        migration_source=migration_source,
        environment="prod"
    )


def tier3_consultation_client(client_id: str, company_name: str, domain: str, contact_email: str,
                             stack_type: str = "fastapi_react_vue_stack") -> ClientConfig:
    """
    Template for Tier 3: Consultation-Only clients.

    Pure consulting services where we deliver infrastructure templates and guidance
    but client manages their own deployment and infrastructure.

    Example:
        client = tier3_consultation_client("enterprise-dev", "Enterprise Dev Team", "enterprisedev.com", "cto@enterprisedev.com")
    """
    return create_client_config(
        client_id=client_id,
        company_name=company_name,
        service_tier="tier3",
        service_type="consultation",
        delivery_model="consulting_template",
        stack_type=stack_type,
        domain=domain,
        contact_email=contact_email,
        environment="prod"
    )


# Legacy template functions - deprecated, use tier-specific functions above
# Kept for backward compatibility but should migrate to new structure

def astro_client(client_id: str, company_name: str, domain: str, contact_email: str,
                advanced: bool = False) -> ClientConfig:
    """
    DEPRECATED: Use tier1_self_managed_client() or tier2_professional_client() instead.
    
    Template for Astro-based clients.
    """
    if advanced:
        return tier2_professional_client(client_id, company_name, domain, contact_email, "astro_advanced_cms_stack")
    else:
        return tier1_self_managed_client(client_id, company_name, domain, contact_email, "astro_template_basic_stack")


def wordpress_client(client_id: str, company_name: str, domain: str, contact_email: str,
                    enterprise: bool = False) -> ClientConfig:
    """
    DEPRECATED: Use tier2_professional_client() or tier3_dual_delivery_client() instead.
    
    Template for WordPress-based clients.
    """
    if enterprise:
        return tier3_dual_delivery_client(client_id, company_name, domain, contact_email, "hosted", "wordpress_ecs_professional_stack")
    else:
        return tier2_professional_client(client_id, company_name, domain, contact_email, "wordpress_ecs_professional_stack")


# Additional legacy functions - use tier-specific functions instead

def shopify_client(client_id: str, company_name: str, domain: str, contact_email: str,
                  integration_level: str = "basic") -> ClientConfig:
    """
    DEPRECATED: Use appropriate tier-specific functions instead.
    
    Example mappings:
    - DNS-only -> tier1_developer_managed_client(..., "shopify_standard_dns_stack") 
    - Basic -> tier2_professional_client(..., "shopify_aws_basic_integration_stack")
    - Advanced -> tier3_dual_delivery_client(..., stack_type="shopify_advanced_aws_integration_stack")
    - Headless -> tier3_dual_delivery_client(..., stack_type="headless_shopify_custom_frontend_stack")
    """
    if integration_level == "dns":
        return tier1_developer_managed_client(client_id, company_name, domain, contact_email, "shopify_standard_dns_stack")
    elif integration_level == "basic":
        return tier2_professional_client(client_id, company_name, domain, contact_email, "shopify_aws_basic_integration_stack")
    elif integration_level == "advanced":
        return tier3_dual_delivery_client(client_id, company_name, domain, contact_email, "hosted", "shopify_advanced_aws_integration_stack")
    elif integration_level == "headless":
        return tier3_dual_delivery_client(client_id, company_name, domain, contact_email, "hosted", "headless_shopify_custom_frontend_stack")
    else:
        return tier2_professional_client(client_id, company_name, domain, contact_email, "shopify_aws_basic_integration_stack")


def nextjs_client(client_id: str, company_name: str, domain: str, contact_email: str,
                 enterprise: bool = False) -> ClientConfig:
    """
    DEPRECATED: Use tier2_professional_client() or tier3_consultation_client() instead.
    """
    if enterprise:
        return tier3_consultation_client(client_id, company_name, domain, contact_email, "nextjs_enterprise_applications_stack")
    else:
        return tier2_professional_client(client_id, company_name, domain, contact_email, "nextjs_professional_headless_cms_stack")

