# Project Creation Guide: Platform Infrastructure Config System

## Overview

This guide explains how to create new client projects using the platform infrastructure configuration system. The system supports a tier-based service model with 30 different stack variants across multiple deployment modes.

## 📋 Prerequisites

### Environment Setup
- **Python**: 3.13+ (required)
- **Package Manager**: `uv` (never use pip, poetry, or conda)
- **AWS CDK**: v2.100.0+
- **AWS Account**: Configured with appropriate permissions

### Initial Setup Commands
```bash
# Install dependencies
uv sync

# Verify environment
uv run python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"
uv run cdk --version
```

## 🏗️ Configuration System Architecture

### Service Tiers
- **Tier 1 (Essential)**: 11 hosted-only stacks | $360-3,000 setup | $0-150/month
- **Tier 2 (Professional)**: 7 hosted-only stacks | $2,400-9,600 setup | $50-400/month  
- **Dual-Delivery**: 5 stacks supporting both hosted and template delivery modes
- **Migration Support**: 7 specialized migration stacks (40% of revenue)

### Core Components
1. **ClientConfig**: Pydantic model for client configuration validation
2. **SSGEngineFactory**: Static Site Generator management system
3. **TechStackMatrix**: Dynamic pricing and suitability validation
4. **SharedInfraStack**: Common operational infrastructure
5. **Tier-specific Stacks**: Service tier implementations

## 🚀 Creating a New Project

### Step 1: Define Client Configuration

Create a client configuration using the `ClientConfig` model:

```python
from clients._templates.client_config import ClientConfig, create_client_config

# Method 1: Using the factory function
client = create_client_config(
    client_id="acme-corp",
    company_name="Acme Corporation", 
    service_tier="tier2",
    stack_type="wordpress_ecs_professional_stack",
    domain="acme.com",
    contact_email="admin@acme.com"
)

# Method 2: Using template functions
from clients._templates.client_config import small_business_client

client = small_business_client(
    client_id="local-biz", 
    company_name="Local Business",
    domain="localbiz.com",
    contact_email="owner@localbiz.com"
)

# Method 3: Direct instantiation with full control
client = ClientConfig(
    client_id="enterprise-co",
    company_name="Enterprise Company",
    service_tier="dual_delivery",
    stack_type="fastapi_react_vue_stack",
    deployment_mode="hosted",  # or "template"
    domain="enterprise.com",
    environment="prod",  # or "staging", "dev"
    contact_email="devops@enterprise.com",
    aws_account="123456789012",  # for template mode
    region="us-east-1",
    custom_settings={"tag:Department": "Engineering"}
)
```

### Step 2: Validate Configuration

The system automatically validates your configuration:

```python
# Validation happens automatically, but you can check manually:
try:
    # This will raise ValidationError if invalid
    validated_client = ClientConfig.model_validate(client_data)
    print(f"✓ Configuration valid: {validated_client}")
except ValidationError as e:
    print(f"✗ Configuration errors: {e}")
```

### Step 3: Choose Technology Stack

#### Available Stack Types by Tier

**Tier 1 (Essential) - 11 Stack Variants:**
```python
tier1_stacks = [
    "eleventy_marketing_stack",        # Static marketing sites
    "astro_portfolio_stack",           # Portfolio/showcase sites  
    "jekyll_github_stack",             # GitHub Pages compatible
    "eleventy_decap_cms_stack",        # Static + Decap CMS
    "astro_tina_cms_stack",            # Astro + Tina CMS
    "astro_sanity_stack",              # Astro + Sanity CMS
    "gatsby_contentful_stack",         # Gatsby + Contentful
    "astro_template_basic_stack",      # Basic Astro template
    "eleventy_snipcart_stack",         # Eleventy + Snipcart ecommerce
    "astro_foxy_stack",                # Astro + Foxy.io ecommerce
    "shopify_standard_dns_stack"       # Shopify DNS-only setup
]
```

**Tier 2 (Professional) - 7 Stack Variants:**
```python
tier2_stacks = [
    "astro_advanced_cms_stack",                    # Advanced Astro + CMS
    "gatsby_headless_cms_stack",                   # Gatsby headless CMS
    "nextjs_professional_headless_cms_stack",      # Next.js professional
    "nuxtjs_professional_headless_cms_stack",      # Nuxt.js professional
    "wordpress_lightsail_stack",                   # WordPress Lightsail
    "wordpress_ecs_professional_stack",            # WordPress ECS
    "shopify_aws_basic_integration_stack"          # Shopify + AWS basic
]
```

**Dual-Delivery - 5 Stack Variants:**
```python
dual_delivery_stacks = [
    "shopify_advanced_aws_integration_stack",      # Advanced Shopify + AWS
    "headless_shopify_custom_frontend_stack",      # Headless Shopify
    "amplify_custom_development_stack",            # AWS Amplify custom
    "fastapi_pydantic_api_stack",                  # FastAPI + Pydantic
    "fastapi_react_vue_stack"                      # FastAPI + React/Vue
]
```

#### Using Template Functions for Common Cases

```python
# Individual/Freelancer (Tier 1)
client = individual_client(
    "johns-design", "John's Design Studio", 
    "johnsdesign.com", "john@johnsdesign.com"
)

# Small Business (Tier 2) 
client = small_business_client(
    "acme-corp", "Acme Corporation",
    "acme.com", "admin@acme.com"
)

# Enterprise (Dual-Delivery)
client = enterprise_client(
    "bigcorp", "BigCorp Industries",
    "bigcorp.com", "devops@bigcorp.com", 
    deployment_mode="hosted"  # or "template"
)

# Technology-Specific Templates
client = astro_client(
    "design-studio", "Design Studio",
    "designstudio.com", "admin@designstudio.com",
    advanced=True  # Tier 2 vs Tier 1
)

client = wordpress_client(
    "local-business", "Local Business", 
    "localbusiness.com", "admin@localbusiness.com",
    enterprise=False  # Professional vs Enterprise
)

client = shopify_client(
    "online-store", "Online Store",
    "onlinestore.com", "admin@onlinestore.com",
    integration_level="basic"  # "dns", "basic", "advanced", "headless"
)
```

### Step 4: Configure SSG Engine (For Static Sites)

For static site stacks, configure the SSG engine:

```python
from shared.ssg_engines import SSGEngineFactory, StaticSiteConfig

# Create SSG configuration
ssg_config = StaticSiteConfig(
    client_id="demo-client",
    domain="demo-client.com", 
    ssg_engine="eleventy",  # "eleventy", "hugo", "astro", "jekyll"
    template_variant="business_modern",
    performance_tier="optimized",  # "basic", "optimized", "premium"
    cdn_caching_strategy="moderate"  # "minimal", "moderate", "aggressive"
)

# Get engine-specific configuration
engine = ssg_config.get_ssg_config()
print(f"Engine: {engine.engine_name}")
print(f"Build commands: {[cmd.command for cmd in engine.build_commands]}")
print(f"Output directory: {engine.output_directory}")
```

### Step 5: Save Configuration

```python
import json
from pathlib import Path

# Save client configuration
client_dir = Path(f"clients/{client.client_id}")
client_dir.mkdir(exist_ok=True)

# Save main config
config_file = client_dir / "config.json"
with open(config_file, 'w') as f:
    json.dump(client.to_dict(), f, indent=2)

# Generate deployment name and tags
print(f"Deployment name: {client.deployment_name}")
print(f"Resource prefix: {client.resource_prefix}")
print(f"Tags: {client.tags}")
```

## 📊 Using the Matrix Parser

The matrix parser provides dynamic validation and recommendations:

```python
from clients._templates.matrix_parser import get_matrix

matrix = get_matrix()

# Get stack information
stack_info = matrix.get_stack_info("wordpress_ecs_professional_stack")
if stack_info:
    print(f"Setup cost range: ${stack_info.setup_cost_range[0]:,}-${stack_info.setup_cost_range[1]:,}")
    print(f"Monthly cost range: ${stack_info.monthly_cost_range[0]}-${stack_info.monthly_cost_range[1]}")
    print(f"AWS services: {stack_info.aws_services}")

# Get recommendations
recommendations = matrix.get_recommended_stacks("small_business", "medium_ecommerce")
print(f"Recommended stacks: {recommendations}")

# Validate pricing
is_valid = matrix.validate_pricing("wordpress_ecs_professional_stack", setup_cost=5000, monthly_fee=200)
print(f"Pricing valid: {is_valid}")

# Migration recommendations
migration_targets = matrix.get_migration_recommendations("magento 1.x")
print(f"Migration targets: {migration_targets}")
```

## 🏭 Deployment Process

### Step 6: Deploy Shared Infrastructure (One-time)

```bash
# Deploy shared operational infrastructure
uv run cdk deploy WebServices-SharedInfra --context account=123456789012 --context region=us-east-1
```

### Step 7: Create Client Stack

Create a client-specific stack file:

```python
# clients/acme-corp/stack.py
from aws_cdk import Stack, App
from constructs import Construct
from clients._templates.client_config import ClientConfig

class AcmeCorpStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, client_config: ClientConfig, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.client_config = client_config
        
        # Apply client tags to all resources
        for key, value in client_config.tags.items():
            self.add_tags(**{key: value})
        
        # Create client-specific resources
        self._create_storage_resources()
        self._create_networking_resources() 
        self._create_compute_resources()
        
    def _create_storage_resources(self):
        # Implementation based on stack_type
        pass
        
    def _create_networking_resources(self):
        # Implementation based on stack_type
        pass
        
    def _create_compute_resources(self):
        # Implementation based on stack_type
        pass
```

### Step 8: Deploy Client Stack

```python
# clients/acme-corp/app.py
#!/usr/bin/env python3
import json
from pathlib import Path
import aws_cdk as cdk
from clients._templates.client_config import ClientConfig
from clients.acme_corp.stack import AcmeCorpStack

def main():
    app = cdk.App()
    
    # Load client configuration
    config_file = Path(__file__).parent / "config.json"
    with open(config_file) as f:
        config_data = json.load(f)
    
    client_config = ClientConfig.from_dict(config_data)
    
    # Create client stack
    AcmeCorpStack(
        app,
        client_config.deployment_name,
        client_config=client_config,
        description=f"Infrastructure for {client_config.company_name}",
        env=cdk.Environment(
            account=client_config.aws_account or app.node.try_get_context("account"),
            region=client_config.region
        )
    )
    
    app.synth()

if __name__ == "__main__":
    main()
```

```bash
# Deploy client stack
cd clients/acme-corp
uv run cdk deploy AcmeCorp-Prod-WordPressEcsProfessional
```

## 🔧 Advanced Configuration

### Environment-Specific Configs

```python
# Development environment
dev_client = ClientConfig(
    client_id="acme-corp",
    company_name="Acme Corporation",
    service_tier="tier2", 
    stack_type="wordpress_ecs_professional_stack",
    domain="dev.acme.com",
    environment="dev",  # Different from prod
    contact_email="dev@acme.com"
)

# Staging environment  
staging_client = ClientConfig(
    client_id="acme-corp",
    company_name="Acme Corporation",
    service_tier="tier2",
    stack_type="wordpress_ecs_professional_stack", 
    domain="staging.acme.com",
    environment="staging",
    contact_email="staging@acme.com"
)
```

### Migration Projects

```python
# Migration from legacy platform
migration_client = ClientConfig(
    client_id="legacy-migrate",
    company_name="Legacy Company",
    service_tier="tier2",
    stack_type="magento_migration_stack", 
    domain="legacy.com",
    contact_email="admin@legacy.com",
    migration_source="magento_1x"  # Source platform
)
```

### Dual-Delivery Template Mode

```python
# Template delivery (client deploys in their AWS account)
template_client = ClientConfig(
    client_id="enterprise-template",
    company_name="Enterprise Template Co",
    service_tier="dual_delivery",
    stack_type="fastapi_react_vue_stack",
    deployment_mode="template",  # Template delivery
    domain="enterprise-template.com", 
    contact_email="devops@enterprise-template.com",
    aws_account="987654321098",  # Client's AWS account
    region="eu-west-1"
)
```

## ✅ Validation and Testing

### Configuration Validation

```python
def validate_client_config(config_data: dict) -> ClientConfig:
    """Validate and return client configuration."""
    try:
        client = ClientConfig.model_validate(config_data)
        
        # Additional business rule validation
        if client.service_tier == "tier1" and client.monthly_cost_range[1] > 150:
            raise ValueError("Tier 1 clients cannot exceed $150/month AWS costs")
            
        if client.deployment_mode == "template" and client.service_tier != "dual_delivery":
            raise ValueError("Template mode only available for dual_delivery tier")
            
        return client
        
    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        raise
```

### Stack Type Validation

```python
def validate_stack_type(stack_type: str, service_tier: str) -> bool:
    """Validate stack type is appropriate for service tier."""
    
    tier_mappings = {
        "tier1": [
            "eleventy_marketing_stack", "astro_portfolio_stack", 
            "jekyll_github_stack", "eleventy_decap_cms_stack",
            "astro_tina_cms_stack", "astro_sanity_stack",
            "gatsby_contentful_stack", "astro_template_basic_stack",
            "eleventy_snipcart_stack", "astro_foxy_stack", 
            "shopify_standard_dns_stack"
        ],
        "tier2": [
            "astro_advanced_cms_stack", "gatsby_headless_cms_stack",
            "nextjs_professional_headless_cms_stack", 
            "nuxtjs_professional_headless_cms_stack",
            "wordpress_lightsail_stack", "wordpress_ecs_professional_stack",
            "shopify_aws_basic_integration_stack"
        ],
        "dual_delivery": [
            "shopify_advanced_aws_integration_stack",
            "headless_shopify_custom_frontend_stack",
            "amplify_custom_development_stack", 
            "fastapi_pydantic_api_stack", "fastapi_react_vue_stack"
        ]
    }
    
    return stack_type in tier_mappings.get(service_tier, [])
```

## 🏷️ Tagging and Cost Management

The system automatically applies comprehensive tags for cost allocation:

```python
client = ClientConfig(...)

# Automatic tagging
tags = client.tags
# Output:
{
    "Client": "acme-corp",
    "Company": "Acme Corporation", 
    "Environment": "prod",
    "StackType": "wordpress_ecs_professional_stack",
    "ServiceTier": "tier2",
    "DeploymentMode": "hosted",
    "BillingGroup": "acme-corp-prod",
    "CostCenter": "acme-corp", 
    "Contact": "admin@acme.com",
    "ManagedBy": "CDK",
    "Project": "WebServices"
}
```

## 🚨 Common Pitfalls and Solutions

### 1. Client ID Format
```python
# ✗ Invalid client IDs
"Acme Corp"        # Contains spaces
"acme_corp"        # Contains underscores  
"acme-"            # Ends with hyphen
"-acme-corp"       # Starts with hyphen
"acme--corp"       # Double hyphens

# ✓ Valid client IDs
"acme-corp"        # Kebab case
"acme-corporation-llc"  # Multiple words
"client123"        # Numbers allowed
```

### 2. Service Tier Mismatches
```python
# ✗ Invalid combinations
ClientConfig(
    service_tier="tier1",
    stack_type="wordpress_ecs_professional_stack"  # Tier 2 stack
)

ClientConfig(
    service_tier="tier2", 
    deployment_mode="template"  # Only dual_delivery supports template mode
)

# ✓ Valid combinations  
ClientConfig(
    service_tier="tier1",
    stack_type="eleventy_marketing_stack"  # Tier 1 stack
)

ClientConfig(
    service_tier="dual_delivery",
    deployment_mode="template"  # Correct tier for template mode
)
```

### 3. Environment Setup Issues
```bash
# ✗ Wrong package managers
pip install aws-cdk-lib    # Don't use pip
poetry add aws-cdk-lib     # Don't use poetry

# ✓ Correct package manager
uv add aws-cdk-lib         # Always use uv
uv sync                    # Install all dependencies
```

## 📚 Quick Reference

### Template Functions
- `individual_client()` - Tier 1 individual/freelancer
- `small_business_client()` - Tier 2 small business  
- `enterprise_client()` - Dual-delivery enterprise
- `astro_client()` - Astro-based sites (basic/advanced)
- `wordpress_client()` - WordPress sites (professional/enterprise)
- `shopify_client()` - Shopify integrations (dns/basic/advanced/headless)
- `nextjs_client()` - Next.js applications (professional/enterprise)

### Key Properties  
- `client.deployment_name` - CDK deployment identifier
- `client.resource_prefix` - AWS resource naming prefix
- `client.tags` - Complete AWS tagging dict
- `client.to_dict()` - JSON serialization
- `ClientConfig.from_dict()` - JSON deserialization

### Essential Commands
```bash
uv sync                    # Install dependencies
uv run python app.py       # Execute with project deps
uv run cdk deploy          # Deploy infrastructure
uv run pytest             # Run tests
uv run black .             # Format code
uv run ruff check .        # Lint code
```

### Migration and Updates
```python
from clients._templates.matrix_parser import migrate_stack_type

# Update existing configurations
old_stack = "astro_headless_cms" 
new_stack = migrate_stack_type(old_stack)  # Returns "astro_template_basic_stack"
```

---

## 🎯 Next Steps

1. **Review the tech stack matrix** in `documents/tech-stack-product-matrix.md`
2. **Set up your development environment** with Python 3.13+ and uv  
3. **Deploy shared infrastructure** using the SharedInfraStack
4. **Create your first client configuration** using the template functions
5. **Validate pricing and suitability** using the matrix parser
6. **Deploy client infrastructure** following the CDK patterns

This configuration system provides the foundation for a scalable, well-organized multi-client web services platform with proper cost allocation, validation, and operational monitoring.