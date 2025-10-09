"""
Unified Service Configuration Models

Consolidates all service configuration concerns into a cohesive system:
- Core client configuration (who, what, where)
- Service integration configuration (CMS, e-commerce, event-driven)
- Provider-specific settings
- Integration mode selection (direct vs event-driven)

This replaces the sprawling configuration across multiple files with a
unified, composable system.
"""

from typing import Dict, Any, List, Optional, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, computed_field
from enum import Enum

# Import component enums for type-safe stack configuration
from models.component_enums import SSGEngine, CMSProvider, EcommerceProvider, Environment


class IntegrationMode(str, Enum):
    """Integration architecture mode"""
    DIRECT = "direct"           # Direct provider integration
    EVENT_DRIVEN = "event_driven"  # Event-driven composition with SNS/DynamoDB


class ServiceType(str, Enum):
    """Core service types"""
    STATIC_SITE = "static_site"
    CMS_TIER = "cms_tier"
    ECOMMERCE_TIER = "ecommerce_tier"
    COMPOSED_STACK = "composed_stack"  # CMS + E-commerce combination


class ServiceTier(str, Enum):
    """Service delivery tiers"""
    TIER1 = "tier1"  # Essential (individual/small business)
    TIER2 = "tier2"  # Professional (growing business)
    TIER3 = "tier3"  # Enterprise (large organization)


class ManagementModel(str, Enum):
    """Service management models (Tier 1 only)"""
    DEVELOPER_MANAGED = "developer_managed"  # 1A: We manage everything
    SELF_MANAGED = "self_managed"           # 1B: Client manages content via CMS
    TECHNICAL = "technical"                 # 1C: Client manages via Git/code


class DeliveryModel(str, Enum):
    """Service delivery models"""
    HOSTED = "hosted"                    # We deploy and manage in our AWS
    CONSULTING_TEMPLATE = "consulting_template"  # Client deploys in their AWS


class CMSProviderConfig(BaseModel):
    """CMS provider-specific configuration"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    provider: CMSProvider = Field(..., description="CMS provider with validated options")
    admin_users: List[str] = Field(default_factory=list, description="Admin user emails")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific settings")

    @field_validator('admin_users')
    @classmethod
    def validate_emails(cls, v):
        for email in v:
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError(f"Invalid email: {email}")
        return v


class EcommerceProviderConfig(BaseModel):
    """E-commerce provider-specific configuration"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    provider: EcommerceProvider = Field(..., description="E-commerce provider with validated options")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific settings")


class ServiceIntegrationConfig(BaseModel):
    """Unified service integration configuration"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "service_type": "cms_tier",
                    "integration_mode": "direct",
                    "ssg_engine": "astro",
                    "cms_config": {
                        "provider": "tina",
                        "admin_users": ["admin@example.com"],
                        "settings": {"repository": "site-repo", "repository_owner": "company"}
                    }
                },
                {
                    "service_type": "composed_stack",
                    "integration_mode": "event_driven",
                    "ssg_engine": "astro",
                    "cms_config": {
                        "provider": "contentful",
                        "admin_users": ["editor@company.com"],
                        "settings": {"space_id": "abc123"}
                    },
                    "ecommerce_config": {
                        "provider": "shopify_basic",
                        "settings": {"store_domain": "company-store.myshopify.com"}
                    }
                }
            ]
        }
    )

    # Core Service Configuration
    service_type: ServiceType = Field(..., description="Primary service type")
    integration_mode: IntegrationMode = Field(
        default=IntegrationMode.DIRECT,
        description="Integration architecture: direct provider calls or event-driven composition"
    )

    # Service Components (optional based on service_type)
    cms_config: Optional[CMSProviderConfig] = Field(
        default=None,
        description="CMS configuration (required for cms_tier and composed_stack)"
    )

    ecommerce_config: Optional[EcommerceProviderConfig] = Field(
        default=None,
        description="E-commerce configuration (required for ecommerce_tier and composed_stack)"
    )

    # SSG Engine Selection
    ssg_engine: SSGEngine = Field(..., description="SSG engine with validated options")

    # Integration Settings
    enable_webhooks: bool = Field(default=True, description="Enable provider webhooks")
    enable_caching: bool = Field(default=True, description="Enable content/data caching")

    # Event-Driven Configuration (when integration_mode = event_driven)
    event_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-driven architecture configuration"
    )

    @model_validator(mode='after')
    def validate_service_requirements(self):
        """Validate service type has required configurations"""

        if self.service_type == ServiceType.CMS_TIER:
            if not self.cms_config:
                raise ValueError("CMS tier requires cms_config")

        elif self.service_type == ServiceType.ECOMMERCE_TIER:
            if not self.ecommerce_config:
                raise ValueError("E-commerce tier requires ecommerce_config")

        elif self.service_type == ServiceType.COMPOSED_STACK:
            if not self.cms_config or not self.ecommerce_config:
                raise ValueError("Composed stack requires both cms_config and ecommerce_config")

        elif self.service_type == ServiceType.STATIC_SITE:
            # Static sites don't need CMS or e-commerce config
            pass

        return self

    @model_validator(mode='after')
    def validate_integration_mode_config(self):
        """Validate event-driven mode has proper configuration"""

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            # Composed stacks benefit most from event-driven architecture
            if self.service_type not in [ServiceType.COMPOSED_STACK, ServiceType.CMS_TIER, ServiceType.ECOMMERCE_TIER]:
                print(f"⚠️  Warning: Event-driven mode typically used with CMS/e-commerce services, not {self.service_type}")

            # Ensure event configuration is present
            if not self.event_config:
                self.event_config = {
                    "sns_topic_prefix": "content-events",
                    "dynamodb_table_prefix": "unified-content",
                    "enable_content_sync": True,
                    "enable_cross_provider_webhooks": True
                }

        return self


class ClientServiceConfig(BaseModel):
    """
    Consolidated client service configuration.

    Replaces the sprawling ClientConfig with a cleaner, more focused model
    that separates client identity from service configuration.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "client_id": "tech-startup",
                    "company_name": "Tech Startup LLC",
                    "domain": "techstartup.com",
                    "contact_email": "admin@techstartup.com",
                    "service_tier": "tier1",
                    "management_model": "self_managed",
                    "delivery_model": "hosted",
                    "service_integration": {
                        "service_type": "cms_tier",
                        "integration_mode": "direct",
                        "ssg_engine": "astro",
                        "cms_config": {
                            "provider": "tina",
                            "admin_users": ["admin@techstartup.com"],
                            "settings": {"repository": "techstartup-site", "repository_owner": "techstartup"}
                        }
                    }
                }
            ]
        }
    )

    # Client Identity
    client_id: str = Field(
        ...,
        description="URL-safe client identifier",
        pattern=r'^[a-z0-9-]+$'
    )
    company_name: str = Field(..., description="Human-readable company name")
    domain: str = Field(..., description="Primary domain")
    contact_email: str = Field(..., description="Primary contact email")

    # Service Delivery Configuration
    service_tier: ServiceTier = Field(..., description="Service delivery tier")
    management_model: Optional[ManagementModel] = Field(
        default=None,
        description="Management model (tier1 only)"
    )
    delivery_model: DeliveryModel = Field(
        default=DeliveryModel.HOSTED,
        description="Service delivery model"
    )

    # Service Integration
    service_integration: ServiceIntegrationConfig = Field(
        ...,
        description="Service and integration configuration"
    )

    # Deployment Settings
    environment: Environment = Field(
        default=Environment.PRODUCTION,
        description="Deployment environment with validated options"
    )
    region: str = Field(default="us-east-1", description="AWS region")

    # Optional Settings
    custom_settings: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional custom settings"
    )

    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v):
        if v.startswith('-') or v.endswith('-') or '--' in v:
            raise ValueError("Invalid client_id format")
        return v

    @field_validator('contact_email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        if '.' not in v or ' ' in v:
            raise ValueError("Invalid domain format")
        return v

    @model_validator(mode='after')
    def validate_tier_management_model(self):
        """Validate management model consistency"""

        if self.service_tier == ServiceTier.TIER1:
            if not self.management_model:
                raise ValueError("Tier1 requires management_model")
        else:
            if self.management_model:
                raise ValueError(f"Management model only applies to tier1, not {self.service_tier}")

        return self

    @computed_field
    @property
    def stack_type(self) -> str:
        """Generate stack type identifier for CDK deployment"""

        service_config = self.service_integration

        if service_config.service_type == ServiceType.STATIC_SITE:
            return f"{service_config.ssg_engine}_static_stack"

        elif service_config.service_type == ServiceType.CMS_TIER:
            return f"{service_config.cms_config.provider}_cms_tier"

        elif service_config.service_type == ServiceType.ECOMMERCE_TIER:
            return f"{service_config.ecommerce_config.provider}_ecommerce_tier"

        elif service_config.service_type == ServiceType.COMPOSED_STACK:
            cms_provider = service_config.cms_config.provider
            ecommerce_provider = service_config.ecommerce_config.provider
            return f"{cms_provider}_{ecommerce_provider}_composed_stack"

        return "unknown_stack"

    @computed_field
    @property
    def deployment_name(self) -> str:
        """CDK deployment name: TechStartup-Prod-TinaCmsTier"""
        client_part = ''.join(word.capitalize() for word in self.client_id.split('-'))
        env_part = self.environment.capitalize()
        stack_part = ''.join(word.capitalize() for word in self.stack_type.split('_'))
        return f"{client_part}-{env_part}-{stack_part}"

    @computed_field
    @property
    def resource_prefix(self) -> str:
        """AWS resource prefix: tech-startup-prod"""
        return f"{self.client_id}-{self.environment}"

    @computed_field
    @property
    def tags(self) -> Dict[str, str]:
        """Standard AWS tags for cost allocation and management"""

        tags = {
            "Client": self.client_id,
            "Company": self.company_name,
            "Environment": self.environment,
            "StackType": self.stack_type,
            "ServiceTier": self.service_tier.value,
            "DeliveryModel": self.delivery_model.value,
            "IntegrationMode": self.service_integration.integration_mode.value,
            "BillingGroup": f"{self.client_id}-{self.environment}",
            "CostCenter": self.client_id,
            "Contact": self.contact_email,
            "ManagedBy": "CDK",
            "Project": "WebServices"
        }

        # Add management model if applicable
        if self.management_model:
            tags["ManagementModel"] = self.management_model.value

        # Add service-specific tags
        service_config = self.service_integration
        if service_config.cms_config:
            tags["CMSProvider"] = service_config.cms_config.provider
        if service_config.ecommerce_config:
            tags["EcommerceProvider"] = service_config.ecommerce_config.provider

        tags["SSGEngine"] = service_config.ssg_engine

        # Add custom tags
        for key, value in self.custom_settings.items():
            if key.startswith('tag:'):
                tags[key[4:]] = value

        return tags

    def is_event_driven(self) -> bool:
        """Check if using event-driven integration mode"""
        return self.service_integration.integration_mode == IntegrationMode.EVENT_DRIVEN

    def has_cms(self) -> bool:
        """Check if configuration includes CMS"""
        return self.service_integration.cms_config is not None

    def has_ecommerce(self) -> bool:
        """Check if configuration includes e-commerce"""
        return self.service_integration.ecommerce_config is not None

    def is_composed_stack(self) -> bool:
        """Check if this is a composed stack (CMS + E-commerce)"""
        return self.service_integration.service_type == ServiceType.COMPOSED_STACK

    def get_integration_config(self) -> Dict[str, Any]:
        """Get integration configuration for stack deployment"""

        config = {
            "integration_mode": self.service_integration.integration_mode.value,
            "ssg_engine": self.service_integration.ssg_engine,
            "enable_webhooks": self.service_integration.enable_webhooks,
            "enable_caching": self.service_integration.enable_caching
        }

        if self.has_cms():
            config["cms"] = {
                "provider": self.service_integration.cms_config.provider,
                "settings": self.service_integration.cms_config.settings
            }

        if self.has_ecommerce():
            config["ecommerce"] = {
                "provider": self.service_integration.ecommerce_config.provider,
                "settings": self.service_integration.ecommerce_config.settings
            }

        if self.is_event_driven():
            config["event_config"] = self.service_integration.event_config

        return config


# Export key models
__all__ = [
    "IntegrationMode",
    "ServiceType",
    "ServiceTier",
    "ManagementModel",
    "DeliveryModel",
    "CMSProviderConfig",
    "EcommerceProviderConfig",
    "ServiceIntegrationConfig",
    "ClientServiceConfig"
]