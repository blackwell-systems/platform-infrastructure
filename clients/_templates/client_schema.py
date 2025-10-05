"""
Client Configuration Schema and Validation

Defines the structure and validation for client configurations
using Pydantic models for type safety and validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Literal
from enum import Enum


class ServiceTier(int, Enum):
    """Client service tier enumeration."""
    TIER_1 = 1  # Essential Solutions ($360-3,000 | $0-150/month)
    TIER_2 = 2  # Professional Solutions ($2,400-9,600 | $50-400/month) 
    TIER_3 = 3  # Enterprise Solutions ($6,000+ | $250+/month)


class ContractType(str, Enum):
    """Contract type enumeration."""
    MONTHLY = "monthly"
    ANNUAL = "annual"
    PROJECT = "project"


class BillingModel(str, Enum):
    """Billing model enumeration."""
    FIXED_MONTHLY = "fixed_monthly"
    FIXED_PLUS_AWS = "fixed_plus_aws"
    ENTERPRISE_CONTRACT = "enterprise_contract"


class SupportLevel(str, Enum):
    """Support level enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class Environment(str, Enum):
    """Environment enumeration."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class PerformanceProfile(str, Enum):
    """Performance profile enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    ENTERPRISE = "enterprise"


# Stack type mappings from the strategy document
TIER_1_STACKS = [
    "static_marketing", "static_portfolio", "jekyll_github", 
    "astro_headless_cms", "static_decap_cms", "static_tina_cms",
    "static_sanity", "static_contentful", "static_snipcart", "static_foxy"
]

TIER_2_STACKS = [
    "astro_advanced_cms", "gatsby_headless_cms", "nextjs_headless_cms",
    "nuxtjs_headless_cms", "fastapi_pydantic_api", "wordpress_lightsail",
    "wordpress_ecs", "shopify_customizations"
]

TIER_3_STACKS = [
    "fastapi_react_vue", "custom_applications", "amplify_ecommerce",
    "serverless_applications", "enterprise_ecommerce", "multitenant_platforms",
    "wordpress_enterprise_ecs"
]

COMMERCE_STACKS = [
    "shopify_standard", "shopify_aws_integrated", "headless_shopify_gatsby",
    "headless_shopify_nextjs", "legacy_ecommerce_modernization"
]

MIGRATION_STACKS = [
    "migration_assessment", "data_migration_pipeline", "magento_migration",
    "prestashop_migration", "opencart_migration", "wordpress_migration",
    "legacy_cms_migration", "custom_platform_migration"
]

ALL_STACK_TYPES = TIER_1_STACKS + TIER_2_STACKS + TIER_3_STACKS + COMMERCE_STACKS + MIGRATION_STACKS


class ClientMetadata(BaseModel):
    """Client business metadata."""
    company_name: str = Field(..., min_length=1, max_length=255)
    client_id: str = Field(..., regex=r'^[a-z0-9-]+$', min_length=3, max_length=50)
    service_tier: ServiceTier
    contract_start: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD format
    contract_type: ContractType
    billing_model: BillingModel
    support_level: SupportLevel
    
    @validator('client_id')
    def validate_client_id(cls, v):
        """Ensure client_id follows naming conventions."""
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('client_id cannot start or end with hyphens')
        if '--' in v:
            raise ValueError('client_id cannot contain consecutive hyphens')
        return v


class BusinessInfo(BaseModel):
    """Client business information."""
    industry: str = Field(..., min_length=1, max_length=100)
    employee_count: Optional[int] = Field(None, ge=1)
    primary_contact: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')  # Basic email validation
    technical_contact: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')


class BillingInfo(BaseModel):
    """Client billing information."""
    monthly_fee: int = Field(..., ge=0)  # In dollars
    aws_cost_passthrough: bool = False
    billing_day: int = Field(1, ge=1, le=28)
    payment_terms: str = Field("net_30", regex=r'^net_\d+$')


class DomainConfig(BaseModel):
    """Domain configuration."""
    primary_domain: str = Field(..., min_length=4, max_length=255)
    hosted_zone_id: Optional[str] = None
    ssl_validation: Literal["dns", "email"] = "dns"


class ResourceConfig(BaseModel):
    """Resource configuration for environments."""
    ecs_cpu: Optional[int] = Field(None, ge=256)
    ecs_memory: Optional[int] = Field(None, ge=512)
    rds_instance_class: Optional[str] = Field(None, regex=r'^db\.[a-z0-9]+\.[a-z0-9]+$')
    rds_multi_az: bool = False
    elasticache_enabled: bool = False


class SecurityConfig(BaseModel):
    """Security configuration."""
    waf_enabled: bool = False
    backup_retention_days: int = Field(7, ge=1, le=365)
    cross_region_backup: bool = False


class MonitoringConfig(BaseModel):
    """Monitoring and alerting configuration."""
    level: SupportLevel = SupportLevel.BASIC
    slack_alerts: bool = False
    email_alerts: List[str] = Field(default_factory=list)


class ClientConfig(BaseModel):
    """Complete client configuration."""
    client_metadata: ClientMetadata
    services: List[str] = Field(default_factory=list)
    business_info: BusinessInfo
    billing_info: BillingInfo


class EnvironmentConfig(BaseModel):
    """Environment-specific configuration."""
    environment: Environment
    stack_type: str = Field(..., regex=f"^({'|'.join(ALL_STACK_TYPES)})$")
    domain_config: DomainConfig
    performance_profile: PerformanceProfile = PerformanceProfile.BASIC
    resources: ResourceConfig = Field(default_factory=ResourceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    @validator('stack_type')
    def validate_stack_type_for_tier(cls, v, values):
        """Validate that stack type is appropriate for client tier."""
        if 'client_metadata' in values:
            tier = values['client_metadata'].service_tier
            if tier == ServiceTier.TIER_1 and v not in TIER_1_STACKS + COMMERCE_STACKS + MIGRATION_STACKS:
                raise ValueError(f'Stack type {v} not available for Tier 1 clients')
            elif tier == ServiceTier.TIER_2 and v not in TIER_1_STACKS + TIER_2_STACKS + COMMERCE_STACKS + MIGRATION_STACKS:
                raise ValueError(f'Stack type {v} not available for Tier 2 clients')
        return v


def validate_client_config(config_dict: Dict) -> ClientConfig:
    """Validate and return a ClientConfig from a dictionary."""
    return ClientConfig(**config_dict)


def validate_environment_config(config_dict: Dict) -> EnvironmentConfig:
    """Validate and return an EnvironmentConfig from a dictionary."""
    return EnvironmentConfig(**config_dict)


# Template configurations for different tiers
TIER_1_TEMPLATE = {
    "client_metadata": {
        "company_name": "Example Company",
        "client_id": "example-company",
        "service_tier": 1,
        "contract_start": "2025-01-01",
        "contract_type": "monthly",
        "billing_model": "fixed_monthly",
        "support_level": "basic"
    },
    "services": ["static_marketing"],
    "business_info": {
        "industry": "professional_services",
        "employee_count": 5,
        "primary_contact": "contact@example.com"
    },
    "billing_info": {
        "monthly_fee": 75,
        "aws_cost_passthrough": False,
        "billing_day": 1,
        "payment_terms": "net_30"
    }
}

TIER_2_TEMPLATE = {
    "client_metadata": {
        "company_name": "Business Corp",
        "client_id": "business-corp", 
        "service_tier": 2,
        "contract_start": "2025-01-01",
        "contract_type": "annual",
        "billing_model": "fixed_plus_aws",
        "support_level": "standard"
    },
    "services": ["wordpress_lightsail"],
    "business_info": {
        "industry": "retail",
        "employee_count": 25,
        "primary_contact": "admin@businesscorp.com",
        "technical_contact": "tech@businesscorp.com"
    },
    "billing_info": {
        "monthly_fee": 200,
        "aws_cost_passthrough": True,
        "billing_day": 1,
        "payment_terms": "net_30"
    }
}

TIER_3_TEMPLATE = {
    "client_metadata": {
        "company_name": "Enterprise Inc",
        "client_id": "enterprise-inc",
        "service_tier": 3,
        "contract_start": "2025-01-01", 
        "contract_type": "annual",
        "billing_model": "enterprise_contract",
        "support_level": "premium"
    },
    "services": ["fastapi_react_vue", "custom_applications"],
    "business_info": {
        "industry": "technology",
        "employee_count": 250,
        "primary_contact": "cto@enterprise.com",
        "technical_contact": "devops@enterprise.com"
    },
    "billing_info": {
        "monthly_fee": 1500,
        "aws_cost_passthrough": True,
        "billing_day": 1,
        "payment_terms": "net_30"
    }
}