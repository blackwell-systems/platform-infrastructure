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

### 🎯 Service Tier Architecture
- **🚀 Tier 1 (Essential)**: Foundation stacks with intelligent SSG selection | $360-3,000 setup | $0-150/month
  - Marketing Stack (Eleventy), Developer Stack (Jekyll), Modern Performance Stack (Astro)
- **💼 Tier 2 (Professional)**: Advanced integrations with CMS tiers | $2,400-9,600 setup | $50-400/month
  - 4 CMS tiers × 7 SSG engines = 28+ optimized combinations with client choice
- **🛒 E-commerce Integration**: Provider abstraction with flexible SSG pairing
  - Snipcart tier ($85-125/month), Foxy.io tier ($100-150/month), Shopify tiers
- **🔄 Migration Specialization**: Automated legacy platform modernization tools

### 🏭 Core Platform Components

1. **🤖 Intelligent Stack Factories**: Automated stack selection and recommendations
   - **SSG Stack Factory**: Marketing, Developer, Modern Performance tier automation
   - **E-commerce Stack Factory**: Provider tier selection with flexible SSG engine pairing
2. **🎯 ClientConfig**: Pydantic model for client configuration validation and cost estimation
3. **⚡ SSG Engine System**: 7 SSG engines (Eleventy, Hugo, Astro, Jekyll, Next.js, Nuxt, Gatsby)
4. **🎨 ThemeRegistry**: Professional theme integration (Minimal Mistakes for Jekyll, etc.)
5. **🔧 Provider Abstraction**: E-commerce providers (Snipcart, Foxy.io, Shopify) with extensible patterns
6. **🚀 SharedInfraStack**: Centralized operational infrastructure with cost optimization
7. **📊 Recommendation Engine**: AI-powered stack suggestions based on client requirements

## 🚀 Creating a New Project

### 🏭 Recommended Approach: Stack Factories

The modern way to create projects is using **intelligent stack factories** that automatically recommend and create optimal infrastructure based on client requirements.

#### Step 1: Get Stack Recommendations

```python
from shared.factories.ssg_stack_factory import SSGStackFactory
from shared.factories.ecommerce_stack_factory import EcommerceStackFactory

# Get SSG stack recommendations based on client needs
ssg_recommendations = SSGStackFactory.get_ssg_recommendations({
    'content_focused': True,        # Marketing/content site
    'budget_conscious': True,       # Cost optimization important
    'technical_team': False        # Non-technical client
})

# Get e-commerce recommendations if needed
ecommerce_recommendations = EcommerceStackFactory.get_ecommerce_recommendations({
    'budget_conscious': True,
    'advanced_ecommerce': False,
    'prefer_react': False
})

print(f"Recommended SSG: {ssg_recommendations[0]['stack_type']}")
print(f"Recommended E-commerce: {ecommerce_recommendations[0]['ecommerce_provider']}")
```

#### Step 2: Create Stacks Using Factories

```python
from aws_cdk import App
from shared.factories.ssg_stack_factory import SSGStackFactory
from shared.factories.ecommerce_stack_factory import EcommerceStackFactory

app = App()

# Create SSG stack automatically
ssg_stack = SSGStackFactory.create_ssg_stack(
    scope=app,
    client_id="content-business",
    domain="contentbiz.com",
    stack_type="marketing"  # From recommendations
)

# Create e-commerce stack if needed
if client_needs_ecommerce:
    ecommerce_stack = EcommerceStackFactory.create_ecommerce_stack(
        scope=app,
        client_id="modern-store",
        domain="store.com",
        ecommerce_provider="snipcart",  # Budget-friendly choice
        ssg_engine="eleventy"           # Fast builds, cost-effective
    )
```

#### Step 3: Cost Estimation

```python
# Get cost estimates automatically
ssg_cost = SSGStackFactory.estimate_total_cost("marketing")
ecommerce_cost = EcommerceStackFactory.estimate_total_cost("snipcart", "eleventy")

print(f"SSG Setup: ${ssg_cost['setup_cost_range']}")
print(f"SSG Monthly: ${ssg_cost['monthly_cost_range']}")
print(f"E-commerce Setup: ${ecommerce_cost['setup_cost_range']}")
print(f"E-commerce Monthly: ${ecommerce_cost['monthly_cost_range']}")
```

#### Step 4: Complete Factory System Example

```python
from aws_cdk import App
from shared.factories.ssg_stack_factory import SSGStackFactory
from shared.factories.ecommerce_stack_factory import EcommerceStackFactory

app = App()

# Example: Content-focused business needs marketing site
content_requirements = {
    'content_focused': True,
    'budget_conscious': True,
    'technical_team': False
}

# Get recommendations
ssg_recommendations = SSGStackFactory.get_ssg_recommendations(content_requirements)
print(f"Recommended: {ssg_recommendations[0]['stack_type']} with {ssg_recommendations[0]['ssg_engine']}")
# Output: Recommended: marketing with eleventy

# Create the recommended stack
marketing_stack = SSGStackFactory.create_ssg_stack(
    scope=app,
    client_id="content-business",
    domain="contentbiz.com",
    stack_type=ssg_recommendations[0]['stack_type']
)

# Example: Technical team needs documentation site
tech_requirements = {
    'technical_team': True,
    'git_workflow': True,
    'documentation_site': True
}

# Get recommendations and create stack
tech_recommendations = SSGStackFactory.get_ssg_recommendations(tech_requirements)
docs_stack = SSGStackFactory.create_ssg_stack(
    scope=app,
    client_id="tech-docs",
    domain="docs.techcompany.com",
    stack_type=tech_recommendations[0]['stack_type'],  # Will be "developer"
    github_repo="techcompany/documentation",
    enable_github_pages_fallback=True
)

# Example: E-commerce business needs online store
ecommerce_requirements = {
    'budget_conscious': True,
    'simple_products': True,
    'technical_team': True
}

# Get e-commerce recommendations
ecommerce_recommendations = EcommerceStackFactory.get_ecommerce_recommendations(ecommerce_requirements)
store_stack = EcommerceStackFactory.create_ecommerce_stack(
    scope=app,
    client_id="simple-store",
    domain="store.example.com",
    ecommerce_provider=ecommerce_recommendations[0]['ecommerce_provider'],  # Will be "snipcart"
    ssg_engine=ecommerce_recommendations[0]['recommended_ssg']  # Will be "hugo" for technical team
)

app.synth()
```

#### Step 5: Deploy Your Stacks

```bash
# Deploy all stacks created by the factories
uv run cdk deploy ContentBusiness-Marketing-SSG-Stack
uv run cdk deploy TechDocs-Developer-SSG-Stack
uv run cdk deploy SimpleStore-Snipcart-Hugo-Stack

# Check deployment status
uv run cdk list
```

---

### 📋 Alternative: Traditional Client Configuration

For advanced use cases where you need full control, you can still use the traditional client configuration approach:

#### Step 1: Define Client Configuration

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
    service_tier="tier3_dual_delivery",
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
# ✅ UPDATED: Flexible Architecture - Client Choice Within Service Types
tier1_service_types = {
    # Static Sites (No CMS)
    "static_sites": [
        "eleventy_marketing_stack",     # Static marketing sites
        "astro_portfolio_stack",        # Portfolio/showcase sites
        "jekyll_github_stack",          # ✅ COMPLETED - GitHub Pages compatible
        "astro_template_basic_stack"    # Basic Astro template
    ],

    # CMS-Enabled Sites (Client Choice: CMS tier → SSG engine)
    "cms_sites": {
        "decap_cms_tier": ["hugo", "eleventy", "astro", "gatsby"],           # $50-75/month
        "tina_cms_tier": ["astro", "eleventy", "nextjs", "nuxt"],            # $60-85/month
        "sanity_cms_tier": ["astro", "gatsby", "nextjs", "nuxt"],            # $65-90/month
        "contentful_cms_tier": ["gatsby", "astro", "nextjs", "nuxt"]         # $75-125/month
    },

    # E-commerce Sites (Client Choice: Provider tier → SSG engine)
    "ecommerce_sites": {
        "snipcart_ecommerce_tier": ["hugo", "eleventy", "astro", "gatsby"],  # $85-125/month
        "foxy_ecommerce_tier": ["hugo", "eleventy", "astro", "gatsby"],      # $100-150/month
        "shopify_basic_tier": ["eleventy", "astro", "nextjs", "nuxt"],       # $75-125/month
        "shopify_standard_dns_stack": []  # DNS-only, no SSG choice needed
    }
}
```

#### E-commerce Stack Details

**Snipcart E-commerce (Simple):**
- **Cost**: $29-99/month + 2.0% transaction fee
- **Best for**: Small stores, digital products, simple catalogs
- **Setup time**: ~3 hours (low complexity)
- **Features**: Cart, checkout, inventory, digital products, subscriptions

**Foxy.io E-commerce (Advanced):**
- **Cost**: $75-300/month + 1.5% transaction fee  
- **Best for**: Advanced features, subscriptions, complex catalogs
- **Setup time**: ~6 hours (high complexity)
- **Features**: Cart, checkout, inventory, subscriptions, customer portal, advanced shipping

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
tier3_dual_delivery_stacks = [
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

# E-commerce Specific Templates
client = snipcart_client(
    "small-shop", "Small Shop",
    "smallshop.com", "admin@smallshop.com",
    complexity="simple"  # "simple", "advanced"
)

client = foxy_client(
    "premium-store", "Premium Store",
    "premiumstore.com", "admin@premiumstore.com",
    features=["subscriptions", "multi_currency"]  # Advanced features
)
```

### Step 4: Configure SSG Engine (For Static Sites)

For static site stacks, configure the SSG engine:

```python
from shared.ssg import SSGEngineFactory, StaticSiteConfig

# Create SSG configuration
ssg_config = StaticSiteConfig(
    client_id="demo-client",
    domain="demo-client.com", 
    ssg_engine="eleventy",  # "eleventy", "hugo", "astro", "jekyll", "nextjs", "nuxt", "gatsby"
    template_variant="business_modern",
    performance_tier="optimized",  # "basic", "optimized", "premium"
    cdn_caching_strategy="moderate"  # "minimal", "moderate", "aggressive"
)

# Get engine-specific configuration
engine = ssg_config.get_ssg_config()
print(f"Engine: {engine.engine_name}")
print(f"Build commands: {[cmd.command for cmd in engine.build_commands]}")
print(f"Output directory: {engine.output_directory}")

# ✅ NEW: Jekyll with Minimal Mistakes Theme
jekyll_config = StaticSiteConfig(
    client_id="tech-docs",
    domain="docs.client.com",
    ssg_engine="jekyll",
    template_variant="simple_blog",
    performance_tier="basic",  # Auto-selects hybrid hosting (AWS + GitHub Pages)
    theme_id="minimal-mistakes",  # Professional theme integration
    theme_config={
        "skin": "mint",
        "author_name": "Technical Team", 
        "search": True,
        "navigation": True
    }
)
```

### Step 4b: Configure E-commerce Sites

For e-commerce enabled sites, use the enhanced e-commerce configuration:

```python
# Simple E-commerce with Snipcart
snipcart_config = StaticSiteConfig(
    client_id="online-store",
    domain="store.example.com",
    ssg_engine="eleventy",
    template_variant="snipcart_ecommerce",  # E-commerce template
    performance_tier="optimized",
    ecommerce_provider="snipcart",
    ecommerce_config={
        "store_name": "My Online Store",
        "currency": "USD",
        "tax_included": False
    }
)

# Advanced E-commerce with Foxy.io
foxy_config = StaticSiteConfig(
    client_id="advanced-store",
    domain="advanced-store.com",
    ssg_engine="astro",
    template_variant="foxy_ecommerce",  # Advanced e-commerce template
    performance_tier="premium",
    ecommerce_provider="foxy",
    ecommerce_config={
        "store_name": "Advanced Store",
        "currency": "USD",
        "subscription_enabled": True,
        "multi_currency": True
    }
)

# Get e-commerce integration details
ecommerce_integration = snipcart_config.get_ecommerce_integration()
if ecommerce_integration:
    print(f"Provider: {ecommerce_integration.provider}")
    print(f"Monthly cost: ${ecommerce_integration.monthly_cost_range[0]}-${ecommerce_integration.monthly_cost_range[1]}")
    print(f"Transaction fee: {ecommerce_integration.transaction_fee_percent}%")
    print(f"Setup complexity: {ecommerce_integration.setup_complexity}")
    print(f"Required AWS services: {ecommerce_integration.aws_services_needed}")
    
# Get required environment variables
env_vars = snipcart_config.get_environment_variables()
print(f"Required environment variables: {env_vars}")

# Get AWS services needed
aws_services = snipcart_config.get_required_aws_services()
print(f"AWS services required: {aws_services}")
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

### Step 7: Create Stacks Using Factories

Create stacks using the intelligent factory system:

```python
# app.py - Modern factory-based approach
from aws_cdk import App
from shared.factories.ssg_stack_factory import SSGStackFactory
from shared.factories.ecommerce_stack_factory import EcommerceStackFactory

app = App()

# Create marketing site stack
marketing_stack = SSGStackFactory.create_ssg_stack(
    scope=app,
    client_id="acme-corp",
    domain="acme.com",
    stack_type="marketing"  # Intelligent Eleventy stack with optimizations
)

# Optional: Add e-commerce if needed
ecommerce_stack = EcommerceStackFactory.create_ecommerce_stack(
    scope=app,
    client_id="acme-store",
    domain="store.acme.com",
    ecommerce_provider="snipcart",
    ssg_engine="eleventy"  # Consistent with marketing site
)

app.synth()
```

**Alternative: Traditional Client-Specific Stack** (for advanced users):

```python
# clients/acme-corp/stack.py - Traditional approach
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

        # Create client-specific resources based on factory patterns
        self._create_resources_via_factories()

    def _create_resources_via_factories(self):
        # Use factories internally for consistency
        pass
```

### Step 8: Deploy Your Stacks

Deploy the factory-created stacks:

```bash
# Deploy the stacks created by factories
uv run cdk deploy AcmeCorp-Marketing-SSG-Stack
uv run cdk deploy AcmeStore-Snipcart-Eleventy-Stack

# Check all available stacks
uv run cdk list

# Deploy with custom parameters if needed
uv run cdk deploy AcmeCorp-Marketing-SSG-Stack --parameters Domain=acme.com
```

**Alternative: Traditional Client Stack Deployment** (for advanced users):

```python
# clients/acme-corp/app.py - Traditional approach
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

    # Create client stack (now uses factories internally)
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

## 🎨 Theme System Integration

### ✅ Minimal Mistakes Theme for Jekyll

The Jekyll stack now includes professional theme integration with the popular minimal-mistakes theme:

```python
from shared.ssg import StaticSiteConfig
from shared.factories.ssg_stack_factory import SSGStackFactory

# Create Jekyll site with minimal-mistakes theme using SSG Stack Factory
jekyll_config = StaticSiteConfig(
    client_id="professional-docs",
    domain="docs.professional.com",
    ssg_engine="jekyll",
    template_variant="simple_blog",
    performance_tier="basic",
    theme_id="minimal-mistakes",  # Professional theme
    theme_config={
        "skin": "mint",            # Theme color scheme
        "author_name": "Company Name",
        "author_bio": "Professional documentation",
        "search": True,            # Enable site search
        "navigation": True,        # Enable main navigation
        "sidebar": True,           # Enable sidebar
        "social_sharing": True     # Enable social media sharing
    }
)

# Deploy Jekyll stack using SSG Stack Factory
jekyll_stack = SSGStackFactory.create_ssg_stack(
    scope=app,
    client_id="professional-docs",
    domain="docs.professional.com",
    stack_type="developer",  # Uses JekyllGitHubStack internally
    theme_id="minimal-mistakes",
    theme_config={
        "skin": "mint",
        "author_name": "Company Name",
        "author_bio": "Professional documentation",
        "search": True,
        "navigation": True,
        "sidebar": True,
        "social_sharing": True
    }
)
```

### Theme Features
- **GitHub Pages Compatible**: Uses remote_theme method
- **Professional Design**: Clean, responsive layout from mmistakes/minimal-mistakes
- **Customizable**: Multiple skins, layouts, and feature options
- **Automatic Installation**: Theme setup integrated into build process
- **Environment Variables**: Theme configuration via build environment

### Theme Customization Options
- **Skins**: `default`, `dark`, `dirt`, `mint`, `plum`, `sunrise`
- **Layouts**: `single`, `splash`, `archive`, `search`, `home`
- **Features**: Author profiles, navigation, search, social sharing, comments

## 🛒 E-commerce Configuration Examples

### Snipcart E-commerce Setup

```python
# Simple Snipcart store
snipcart_store = StaticSiteConfig(
    client_id="boutique-store",
    domain="boutique.example.com",
    ssg_engine="eleventy",
    template_variant="snipcart_ecommerce",
    performance_tier="optimized",
    ecommerce_provider="snipcart",
    ecommerce_config={
        "store_name": "Boutique Store",
        "currency": "USD",
        "tax_included": False,
        "shipping_same_as_billing": True,
        "inventory_management": True
    },
    environment_vars={
        "SNIPCART_API_KEY": "${SNIPCART_API_KEY}",
        "SNIPCART_PUBLIC_KEY": "${SNIPCART_PUBLIC_KEY}"
    }
)

# Get cost breakdown
integration = snipcart_store.get_ecommerce_integration()
print(f"Monthly platform cost: ${integration.monthly_cost_range[0]}-${integration.monthly_cost_range[1]}")
print(f"Transaction fee: {integration.transaction_fee_percent}%")
print(f"AWS services needed: {integration.aws_services_needed}")
```

### Foxy.io Advanced E-commerce Setup

```python
# Advanced Foxy.io store
foxy_store = StaticSiteConfig(
    client_id="premium-electronics",
    domain="electronics.example.com", 
    ssg_engine="astro",
    template_variant="foxy_ecommerce",
    performance_tier="premium",
    ecommerce_provider="foxy",
    ecommerce_config={
        "store_name": "Premium Electronics",
        "currency": "USD",
        "multi_currency": True,
        "subscription_products": True,
        "customer_accounts": True,
        "advanced_shipping": True,
        "tax_calculation": True
    },
    environment_vars={
        "FOXY_STORE_DOMAIN": "${FOXY_STORE_DOMAIN}",
        "FOXY_API_KEY": "${FOXY_API_KEY}",
        "FOXY_WEBHOOK_SECRET": "${FOXY_WEBHOOK_SECRET}"
    },
    webhook_endpoints=[
        "/api/webhooks/foxy/order-created",
        "/api/webhooks/foxy/subscription-modified"
    ],
    requires_backend_api=True
)

# Get comprehensive setup details
integration = foxy_store.get_ecommerce_integration()
print(f"Setup complexity: {integration.setup_complexity}")
print(f"Build dependencies: {integration.build_dependencies}")
print(f"AWS services: {integration.aws_services_needed}")
print(f"Required webhooks: {foxy_store.webhook_endpoints}")
```

### E-commerce Recommendations Engine

```python
from shared.ssg import SSGEngineFactory

# Get recommendations by complexity level
simple_recs = SSGEngineFactory.get_recommended_stack_for_ecommerce("snipcart", "simple")
for rec in simple_recs:
    print(f"Engine: {rec['engine']}, Template: {rec['template']}")
    print(f"Estimated setup: {rec['estimated_hours']} hours")
    print(f"Monthly cost: ${rec['monthly_cost_range'][0]}-${rec['monthly_cost_range'][1]}")

# Get all e-commerce templates
ecommerce_templates = SSGEngineFactory.get_ecommerce_templates()
for engine, templates in ecommerce_templates.items():
    print(f"\n{engine.upper()} E-commerce Templates:")
    for template in templates:
        integration = template.ecommerce_integration
        if integration:
            print(f"  - {template.name}: {integration.provider} ({integration.setup_complexity})")

# Get templates by specific provider
snipcart_templates = SSGEngineFactory.get_templates_by_provider("snipcart")
foxy_templates = SSGEngineFactory.get_templates_by_provider("foxy")
```

### E-commerce Cost Planning

```python
def calculate_ecommerce_costs(client_config, monthly_sales=5000):
    """Calculate total monthly e-commerce costs including platform fees."""
    
    # Get e-commerce integration details
    if hasattr(client_config, 'get_ecommerce_integration'):
        integration = client_config.get_ecommerce_integration()
        if integration:
            platform_cost = integration.monthly_cost_range[1]  # Use max
            transaction_fee = (monthly_sales * integration.transaction_fee_percent) / 100
            
            # AWS hosting costs (estimated)
            aws_services = client_config.get_required_aws_services()
            aws_cost = len(aws_services) * 15  # ~$15 per service
            
            total_cost = platform_cost + transaction_fee + aws_cost
            
            return {
                "platform_monthly": platform_cost,
                "transaction_fees": transaction_fee,
                "aws_hosting": aws_cost,
                "total_monthly": total_cost,
                "cost_per_sale": total_cost / (monthly_sales / 100) if monthly_sales > 0 else 0
            }
    
    return None

# Example usage
costs = calculate_ecommerce_costs(snipcart_store, monthly_sales=3000)
if costs:
    print(f"Total monthly cost: ${costs['total_monthly']:.2f}")
    print(f"Cost per $100 in sales: ${costs['cost_per_sale']:.2f}")
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
    service_tier="tier3_dual_delivery",
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
            
        if client.deployment_mode == "template" and client.service_tier != "tier3_dual_delivery":
            raise ValueError("Template mode only available for tier3_dual_delivery tier")
            
        return client
        
    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        raise
```

### Stack Type Validation

```python
def validate_stack_type(stack_type: str, service_tier: str) -> bool:
    """Validate stack type is appropriate for service tier."""
    
    # ✅ UPDATED: Flexible Architecture Validation
    tier_mappings = {
        "tier1": [
            # Static Sites
            "eleventy_marketing_stack", "astro_portfolio_stack",
            "jekyll_github_stack", "astro_template_basic_stack",
            # CMS Tiers (via factory patterns)
            "decap_cms_tier", "tina_cms_tier", "sanity_cms_tier", "contentful_cms_tier",
            # E-commerce Provider Tiers (via factory patterns)
            "snipcart_ecommerce_tier", "foxy_ecommerce_tier", "shopify_basic_tier",
            "shopify_standard_dns_stack"
        ],
        "tier2": [
            "astro_advanced_cms_stack", "gatsby_headless_cms_stack",
            "nextjs_professional_headless_cms_stack", 
            "nuxtjs_professional_headless_cms_stack",
            "wordpress_lightsail_stack", "wordpress_ecs_professional_stack",
            "shopify_aws_basic_integration_stack"
        ],
        "tier3_dual_delivery": [
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
    deployment_mode="template"  # Only tier3_dual_delivery supports template mode
)

# ✓ Valid combinations  
ClientConfig(
    service_tier="tier1",
    stack_type="eleventy_marketing_stack"  # Tier 1 stack
)

ClientConfig(
    service_tier="tier3_dual_delivery",
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
- `snipcart_client()` - Simple e-commerce with Snipcart integration
- `foxy_client()` - Advanced e-commerce with Foxy.io integration

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

# E-commerce specific testing
uv run python -c "from shared.ssg import SSGEngineFactory; print('E-commerce templates:', SSGEngineFactory.get_ecommerce_templates())"
```

### Migration and Updates
```python
from clients._templates.matrix_parser import migrate_stack_type

# Update existing configurations
old_stack = "astro_headless_cms" 
new_stack = migrate_stack_type(old_stack)  # Returns "astro_template_basic_stack"
```

---

## 🛠️ E-commerce Deployment Checklist

When deploying e-commerce sites, follow this checklist:

### Pre-deployment
- [ ] **Provider Setup**: Create account with Snipcart/Foxy.io
- [ ] **API Keys**: Obtain and secure API keys in AWS Parameter Store
- [ ] **Domain**: Ensure SSL certificate is ready
- [ ] **Testing**: Set up sandbox/test environment first

### Configuration
- [ ] **Template Selection**: Choose appropriate e-commerce template
- [ ] **Environment Variables**: Configure all required variables
- [ ] **Webhooks**: Set up webhook endpoints for order processing
- [ ] **AWS Services**: Ensure Lambda, SES, and other services are configured

### Post-deployment
- [ ] **Payment Testing**: Test checkout flow thoroughly
- [ ] **Order Processing**: Verify webhook delivery and processing
- [ ] **Performance**: Monitor site performance under load
- [ ] **Cost Monitoring**: Set up billing alerts for platform and AWS costs

## 🎯 Next Steps

1. **Set up your development environment** with Python 3.13+ and uv
2. **Deploy shared infrastructure** using the SharedInfraStack
3. **Try the intelligent factory system**:
   ```bash
   # Get stack recommendations
   uv run python -c "
   from shared.factories.ssg_stack_factory import SSGStackFactory
   requirements = {'content_focused': True, 'budget_conscious': True}
   recommendations = SSGStackFactory.get_ssg_recommendations(requirements)
   print('Recommended:', recommendations[0])
   "
   ```
4. **Create your first stack using factories**:
   ```bash
   # Create and deploy a marketing stack
   uv run python -c "
   from aws_cdk import App
   from shared.factories.ssg_stack_factory import SSGStackFactory

   app = App()
   stack = SSGStackFactory.create_ssg_stack(
       scope=app, client_id='my-business',
       domain='mybusiness.com', stack_type='marketing'
   )
   app.synth()
   "
   uv run cdk deploy MyBusiness-Marketing-SSG-Stack
   ```
5. **For e-commerce sites**: Use the EcommerceStackFactory for intelligent provider selection
6. **Explore advanced features**: Check out the SSG Integration Guide for detailed configurations
7. **Review cost implications**: Use the built-in cost estimation features in both factories

**Factory System Benefits:**
- 🎯 **Intelligent Recommendations**: Get stack suggestions based on your specific requirements
- 🚀 **Consistent Architecture**: All stacks follow proven patterns and best practices
- 💰 **Cost Transparency**: Built-in cost estimation for setup and monthly expenses
- 🔧 **Easy Deployment**: Simplified CDK stack creation with minimal configuration
- 📈 **Scalable Patterns**: Architecture designed for growth from individual to enterprise

This factory-based system provides the foundation for a scalable, well-organized multi-client web services platform with intelligent stack selection, comprehensive e-commerce support, and automated operational monitoring.