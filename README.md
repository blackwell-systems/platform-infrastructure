# Dual-Delivery Web Services Infrastructure

Multi-client web development services infrastructure using AWS CDK with flexible service delivery models.

## Table of Contents

- [Overview](#overview)
- [Current Implementation Status](#current-implementation-status)
- [Quick Start](#quick-start)
- [Getting Started Checklist](#getting-started-checklist)
- [Architecture](#architecture)
- [Complete Stack Variants](#complete-stack-variants)
- [SSG Engine Support](#ssg-engine-support)
- [Development Workflow](#development-workflow)
- [Common Patterns](#common-patterns)
- [Essential Commands Reference](#essential-commands-reference)

## Overview

This repository provides a complete **multi-client web services infrastructure platform** built on AWS CDK, designed for web development agencies and service providers who need scalable, cost-effective client management.

### What This Platform Provides

- **30 Pre-configured Stack Variants** across 3 service tiers (Tier 1: $360-3K setup, Tier 2: $2.4K-9.6K setup, Dual-delivery: Custom pricing)
- **7 Static Site Generators** (Eleventy, Hugo, Astro, Jekyll, Next.js, Nuxt, Gatsby) with optimized configurations
- **E-commerce Integration**: Built-in support for Snipcart, Foxy.io, Shopify (3 tiers), with cost transparency
- **Dual-Delivery Service Models**: Deploy in your AWS account (hosted) OR deliver infrastructure code to clients (template)
- **Migration Specialization**: 7 specialized stacks for legacy platform migrations
- **Type-Safe Configuration**: Pydantic-based client configuration with automatic validation and cost estimation

### Who This Is For

- **Web development agencies** managing multiple client sites
- **Freelance developers** seeking professional infrastructure templates
- **Consultants** offering modern web platform migrations
- **Development teams** needing standardized deployment patterns

The platform implements a monorepo architecture organized by delivery capability for maximum flexibility and operational efficiency.

## Current Implementation Status

**Dual-Delivery Service Model**: Complete service delivery flexibility
**30 Hosted Stack Variants**: Comprehensive technology matrix
**Shared Infrastructure**: Operational backbone for hosted clients
**Pydantic Client Configuration**: Type-safe validation and configuration management
**Migration Specialization**: 7 specialized migration service stacks

### Core Features

- **SharedInfraStack**: Operational infrastructure serving all hosted clients (minimizing $/month total cost)
  - Business domain DNS management (Route53)
  - Centralized monitoring and alerting (CloudWatch + SNS)
  - Automated cost allocation and billing
  - Client isolation through IAM and resource tagging
- **Dual-Delivery Configuration**: Pydantic models supporting both hosted and template delivery modes
- **Service Delivery Templates**: Pre-configured setups for all service tiers and deployment modes

## Quick Start

### Prerequisites

- **Python**: 3.13+ (required)
- **Package Manager**: `uv` (never use pip, poetry, or conda)
- **AWS CLI**: Configured with appropriate permissions
- **Node.js**: 18+ (for CDK CLI)
- **AWS CDK**: v2.100.0+

### Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install CDK CLI globally
npm install -g aws-cdk

# Verify environment setup
uv run python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"
uv run cdk --version

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Deploy Shared Infrastructure

```bash
# Deploy the shared operational infrastructure (one-time)
uv run cdk deploy WebServices-SharedInfra --context account=123456789012 --context region=us-east-1
```

### Create Your First Client

```bash
# Quick client creation examples
uv run python -c "
from clients._templates.client_config import small_business_client
client = small_business_client('acme-corp', 'Acme Corporation', 'acme.com', 'admin@acme.com')
print(f'Created: {client.deployment_name}')
print(f'Stack type: {client.stack_type}')
print(f'Monthly cost range: \${client.monthly_cost_range[0]}-\${client.monthly_cost_range[1]}')
"

# Deploy client infrastructure
uv run cdk deploy AcmeCorp-Prod-WordPressEcsProfessional
```

## Getting Started Checklist

**For your first client deployment:**

- [ ] **Environment Setup**: Complete [Prerequisites](#prerequisites) and run `uv sync`
- [ ] **Choose Service Model**: Review [Complete Stack Variants](#complete-stack-variants) to select appropriate tier
- [ ] **Deploy Shared Infrastructure**: One-time setup with `uv run cdk deploy WebServices-SharedInfra`
- [ ] **Create Client Configuration**: Use template functions from [Development Workflow](#development-workflow)
- [ ] **Deploy Client Stack**: Follow examples in [Client Onboarding Process](#client-onboarding-process)
- [ ] **Explore Patterns**: Check [Common Patterns](#common-patterns) for advanced configurations

**For ongoing management:**
- [ ] Use [Essential Commands Reference](#essential-commands-reference) for daily operations
- [ ] Implement [Error Handling and Recovery](#error-handling-and-recovery) patterns
- [ ] Consider [Cost Optimization Patterns](#cost-optimization-patterns) for scaling

> **Next Steps**: See [Complete Stack Variants](#complete-stack-variants) for all available options, or jump to [Development Workflow](#development-workflow) for detailed configuration examples.

## Architecture

### Service Delivery Models

**Hosted-Only Solutions** (18 stack variants)
- Deploy and manage infrastructure in our AWS account
- Comprehensive ongoing hosting and maintenance
- Shared infrastructure cost optimization
- Service tiers: Tier 1 (11 variants), Tier 2 (7 variants)

**Dual-Delivery Solutions** (5 stack variants)
- **Hosted Mode**: Managed service in our AWS account
- **Template Mode**: Infrastructure code delivered to client AWS account
- Client choice based on technical capabilities and compliance requirements
- Examples: FastAPI backends, advanced Shopify integrations, AWS Amplify

**Migration Support Services** (7 specialized stacks)
- Legacy platform assessment and modernization planning

### Repository Structure

```
platform-infrastructure/
├── stacks/                         # CDK stack definitions
│   ├── hosted-only/               # 18 hosted-only stack variants
│   │   ├── tier1/                 # 11 essential solution stacks
│   │   └── tier2/                 # 7 professional solution stacks
│   ├── dual-delivery/             # 5 dual-delivery stack variants
│   ├── migration-support/         # 7 migration service stacks
│   └── shared/                    # Shared infrastructure (hosted clients only)
├── clients/                       # Client configurations
│   ├── _templates/               # Pydantic configuration models
│   └── [client-folders]/         # Individual client configurations
├── constructs/                    # Reusable CDK constructs
├── tools/                         # Business automation and deployment tools
└── tests/                         # Infrastructure testing
```

## Complete Stack Variants

### Tier 1 (Essential) - 11 Stack Variants
*Setup: $360-3,000 | Monthly: $0-150*

| Stack Type | Description | Use Cases |
|------------|-------------|-----------|
| `eleventy_marketing_stack` | Static marketing sites with Eleventy SSG | Marketing sites, landing pages |
| `astro_portfolio_stack` | Portfolio/showcase sites with Astro | Creative portfolios, agencies |
| `jekyll_github_stack` | GitHub Pages compatible Jekyll sites | Documentation, simple blogs |
| `eleventy_decap_cms_stack` | Static sites with Decap CMS integration | Small business sites with CMS |
| `astro_tina_cms_stack` | Astro with Tina CMS for content management | Content sites, blogs |
| `astro_sanity_stack` | Astro with Sanity headless CMS | Media-rich content sites |
| `gatsby_contentful_stack` | Gatsby with Contentful CMS integration | Marketing sites, blogs |
| `astro_template_basic_stack` | Basic Astro template for quick deployment | Simple business sites |
| `eleventy_snipcart_stack` | Eleventy with Snipcart e-commerce ($29-99/month, 2% fee) | Small online stores |
| `astro_foxy_stack` | Astro with Foxy.io e-commerce ($75-300/month, 1.5% fee) | Advanced e-commerce sites |
| `shopify_standard_dns_stack` | Shopify DNS-only setup | Basic Shopify stores |

### Tier 2 (Professional) - 7 Stack Variants
*Setup: $2,400-9,600 | Monthly: $50-400*

| Stack Type | Description | Use Cases |
|------------|-------------|-----------|
| `astro_advanced_cms_stack` | Advanced Astro with multiple CMS options | Complex content sites |
| `gatsby_headless_cms_stack` | Gatsby with advanced headless CMS features | Enterprise marketing sites |
| `nextjs_professional_headless_cms_stack` | Next.js with professional CMS integration | High-performance web apps |
| `nuxtjs_professional_headless_cms_stack` | Nuxt.js with professional CMS features | Vue-based applications |
| `wordpress_lightsail_stack` | WordPress on AWS Lightsail | Traditional WordPress sites |
| `wordpress_ecs_professional_stack` | WordPress on ECS with professional features | Scalable WordPress solutions |
| `shopify_aws_basic_integration_stack` | Shopify with basic AWS integrations | Enhanced Shopify stores |

### Dual-Delivery - 5 Stack Variants
*Hosted Mode: $3,600-12,000 setup | Template Mode: $1,800-6,000*

| Stack Type | Description | Deployment Modes |
|------------|-------------|------------------|
| `shopify_advanced_aws_integration_stack` | Advanced Shopify with full AWS integration | Hosted, Template |
| `headless_shopify_custom_frontend_stack` | Headless Shopify with custom frontend | Hosted, Template |
| `amplify_custom_development_stack` | AWS Amplify with custom development | Hosted, Template |
| `fastapi_pydantic_api_stack` | FastAPI backend with Pydantic validation | Hosted, Template |
| `fastapi_react_vue_stack` | Full-stack FastAPI with React/Vue frontend | Hosted, Template |

### Migration Support - 7 Specialized Stacks
*40% of total revenue | Custom pricing based on complexity*

| Migration Type | Target Platform | Complexity |
|----------------|-----------------|------------|
| `magento_migration_stack` | Modern e-commerce platform | High |
| `drupal_migration_stack` | Modern CMS/framework | Medium |
| `joomla_migration_stack` | Modern CMS solution | Medium |
| `legacy_php_migration_stack` | Modern PHP/framework | Medium-High |
| `wordpress_modernization_stack` | Enhanced WordPress | Low-Medium |
| `static_site_conversion_stack` | JAMstack solution | Low |
| `platform_assessment_stack` | Migration planning tools | Low |

## SSG Engine Support

The platform supports 7 Static Site Generators with optimized configurations:

| Engine | Best For | Performance | Build Speed |
|--------|----------|-------------|-------------|
| **Eleventy** | Marketing sites, flexibility | Very Good | Excellent |
| **Hugo** | Large sites, speed | Excellent | Excellent |
| **Astro** | Interactive sites, modern | Excellent | Very Good |
| **Jekyll** | GitHub integration, simple | Good | Good |
| **Next.js** | React apps, enterprise | Excellent | Good |
| **Nuxt** | Vue apps, SSR | Excellent | Good |
| **Gatsby** | React, GraphQL | Very Good | Fair |

> **See Also**: [Development Workflow](#development-workflow) for SSG integration examples, or [Common Patterns](#common-patterns) for business-specific configurations.

## Development Workflow

### Client Configuration Examples

#### Template Functions for Common Use Cases

```python
from clients._templates.client_config import (
    individual_client, small_business_client, enterprise_client,
    astro_client, wordpress_client, shopify_client
)

# Individual/Freelancer (Tier 1)
freelancer = individual_client(
    "johns-design", "John's Design Studio",
    "johnsdesign.com", "john@johnsdesign.com"
)
# Results in: eleventy_marketing_stack, $360-1,500 setup, $0-50/month

# Small Business (Tier 2)
business = small_business_client(
    "acme-corp", "Acme Corporation",
    "acme.com", "admin@acme.com"
)
# Results in: wordpress_ecs_professional_stack, $2,400-4,800 setup, $50-200/month

# Enterprise with Template Delivery
enterprise = enterprise_client(
    "bigcorp", "BigCorp Industries",
    "bigcorp.com", "devops@bigcorp.com",
    deployment_mode="template"  # Deploy to client's AWS account
)
# Results in: fastapi_react_vue_stack, $1,800-6,000 template delivery

# Technology-Specific Configurations
astro_site = astro_client(
    "design-studio", "Creative Design Studio",
    "designstudio.com", "admin@designstudio.com",
    advanced=True  # Tier 2 vs Tier 1
)
# Results in: astro_advanced_cms_stack

wordpress_site = wordpress_client(
    "local-business", "Local Business",
    "localbusiness.com", "admin@localbusiness.com",
    enterprise=False  # Professional vs Enterprise tier
)
# Results in: wordpress_ecs_professional_stack

shopify_store = shopify_client(
    "online-store", "Online Store",
    "onlinestore.com", "admin@onlinestore.com",
    integration_level="advanced"  # "dns", "basic", "advanced", "headless"
)
# Results in: shopify_advanced_aws_integration_stack
```

#### Environment-Specific Configurations

```python
# Development Environment
dev_client = small_business_client(
    "acme-corp", "Acme Corporation",
    "dev.acme.com", "dev@acme.com"
)
dev_client.environment = "dev"  # Affects naming and resource allocation

# Staging Environment
staging_client = small_business_client(
    "acme-corp", "Acme Corporation",
    "staging.acme.com", "staging@acme.com"
)
staging_client.environment = "staging"

# Production Environment (default)
prod_client = small_business_client(
    "acme-corp", "Acme Corporation",
    "acme.com", "admin@acme.com"
)
# environment defaults to "prod"
```

#### SSG Engine Integration

```python
# Static site with specific SSG engine
from shared.ssg_engines import StaticSiteConfig

# Modern Astro site with CMS
astro_config = StaticSiteConfig(
    client_id="creative-agency",
    domain="creativeagency.com",
    ssg_engine="astro",
    template_variant="modern_interactive",
    performance_tier="premium",  # "basic", "optimized", "premium"
    cms_provider="sanity"
)

# Fast Hugo corporate site
hugo_config = StaticSiteConfig(
    client_id="corp-site",
    domain="corpsite.com",
    ssg_engine="hugo",
    template_variant="corporate_clean",
    performance_tier="optimized",
    cdn_caching_strategy="aggressive"
)

# Next.js with headless CMS
nextjs_config = StaticSiteConfig(
    client_id="app-company",
    domain="appcompany.com",
    ssg_engine="nextjs",
    template_variant="professional_headless_cms",
    performance_tier="premium",
    cms_provider="contentful"
)
```

### Configuration Validation

```python
from pydantic import ValidationError

# Automatic validation with helpful error messages
try:
    client = small_business_client(
        "Invalid Client Name",  # ❌ Spaces not allowed in client_id
        "Acme Corporation",
        "acme.com",
        "admin@acme.com"
    )
except ValidationError as e:
    print(f"Configuration errors: {e}")

# Valid configuration
client = small_business_client(
    "acme-corp",  # ✅ Valid kebab-case client_id
    "Acme Corporation",
    "acme.com",
    "admin@acme.com"
)

# Check generated values
print(f"Deployment name: {client.deployment_name}")  # AcmeCorp-Prod-WordPressEcsProfessional
print(f"Monthly cost range: ${client.monthly_cost_range[0]}-${client.monthly_cost_range[1]}")
print(f"AWS tags: {client.tags}")
```

### Client Onboarding Process

```bash
# 1. Create and validate client configuration
uv run python -c "
from clients._templates.client_config import small_business_client
from clients._templates.matrix_parser import get_matrix

# Create client
client = small_business_client('acme-corp', 'Acme Corporation', 'acme.com', 'admin@acme.com')
print(f'✓ Created client: {client.deployment_name}')
print(f'  Stack type: {client.stack_type}')
print(f'  Setup cost: \$2,400-4,800')
print(f'  Monthly cost: \$50-200')

# Validate with matrix
matrix = get_matrix()
stack_info = matrix.get_stack_info(client.stack_type)
if stack_info:
    print(f'  AWS services: {stack_info.aws_services}')
    print(f'  Suitability: {stack_info.suitability}')
"

# 2. Save client configuration
mkdir -p clients/acme-corp
uv run python -c "
import json
from pathlib import Path
from clients._templates.client_config import small_business_client

client = small_business_client('acme-corp', 'Acme Corporation', 'acme.com', 'admin@acme.com')

# Save configuration
config_file = Path('clients/acme-corp/config.json')
with open(config_file, 'w') as f:
    json.dump(client.to_dict(), f, indent=2)

print(f'✓ Saved configuration to {config_file}')
"

# 3. Deploy infrastructure
uv run cdk deploy AcmeCorp-Prod-WordPressEcsProfessional

# 4. For template delivery mode
uv run cdk synth AcmeCorp-Prod-WordPressEcsProfessional --output clients/acme-corp/cdk-out
# Then deliver the synthesized CloudFormation templates to client
```

### Migration Projects

```python
# Legacy platform migration
from clients._templates.matrix_parser import get_matrix

migration_client = ClientConfig(
    client_id="legacy-migrate",
    company_name="Legacy Company",
    service_tier="tier2",
    stack_type="magento_migration_stack",  # Specialized migration stack
    domain="legacy.com",
    contact_email="admin@legacy.com",
    migration_source="magento_1x"  # Source platform identifier
)

# Get migration recommendations
matrix = get_matrix()
recommendations = matrix.get_migration_recommendations("magento 1.x")
print(f"Recommended migration targets: {recommendations}")
```

## Common Patterns

### Stack Selection by Business Type

```python
# E-commerce businesses
ecommerce_basic = shopify_client(
    "small-store", "Small Store", "smallstore.com", "admin@smallstore.com",
    integration_level="basic"  # Shopify + AWS basic integration
)

ecommerce_advanced = shopify_client(
    "big-retailer", "Big Retailer", "bigretailer.com", "dev@bigretailer.com",
    integration_level="headless"  # Headless Shopify with custom frontend
)

# Content-heavy sites
content_basic = astro_client(
    "blog-site", "Blog Site", "blogsite.com", "editor@blogsite.com",
    advanced=False  # Basic Astro with CMS
)

content_enterprise = astro_client(
    "media-company", "Media Company", "mediacompany.com", "tech@mediacompany.com",
    advanced=True  # Advanced Astro with multiple CMS options
)

# Corporate websites
corporate_simple = individual_client(
    "law-firm", "Law Firm", "lawfirm.com", "admin@lawfirm.com"
)  # Results in Eleventy marketing stack

corporate_complex = small_business_client(
    "consulting-group", "Consulting Group", "consultinggroup.com", "it@consultinggroup.com"
)  # Results in WordPress ECS professional
```

### Cost Optimization Patterns

```python
# Development → Staging → Production progression
def create_environment_configs(base_client_id, company_name, domain, email):
    """Create cost-optimized environment configurations"""

    # Dev: Tier 1 for development
    dev = individual_client(
        f"{base_client_id}-dev", company_name, f"dev.{domain}", email
    )
    dev.environment = "dev"

    # Staging: Same as production but smaller scale
    staging = small_business_client(
        f"{base_client_id}-staging", company_name, f"staging.{domain}", email
    )
    staging.environment = "staging"

    # Production: Full featured
    production = small_business_client(
        base_client_id, company_name, domain, email
    )

    return dev, staging, production

# Usage
dev, staging, prod = create_environment_configs(
    "acme-corp", "Acme Corporation", "acme.com", "admin@acme.com"
)

print(f"Development cost: ${dev.monthly_cost_range[0]}-${dev.monthly_cost_range[1]}/month")
print(f"Staging cost: ${staging.monthly_cost_range[0]}-${staging.monthly_cost_range[1]}/month")
print(f"Production cost: ${prod.monthly_cost_range[0]}-${prod.monthly_cost_range[1]}/month")
```

### Template vs Hosted Decision Matrix

```python
def recommend_deployment_mode(client_requirements):
    """Recommend deployment mode based on client requirements"""

    # Factors favoring template delivery
    template_factors = {
        "has_dedicated_devops": client_requirements.get("has_devops_team", False),
        "compliance_requirements": client_requirements.get("strict_compliance", False),
        "multi_region": client_requirements.get("global_deployment", False),
        "integration_heavy": client_requirements.get("complex_integrations", False),
        "cost_sensitive": client_requirements.get("prefer_lower_monthly", True)
    }

    # Factors favoring hosted delivery
    hosted_factors = {
        "no_devops_team": not client_requirements.get("has_devops_team", False),
        "quick_deployment": client_requirements.get("fast_time_to_market", True),
        "managed_service_preference": client_requirements.get("prefer_managed", True),
        "standard_requirements": not client_requirements.get("complex_integrations", False)
    }

    template_score = sum(template_factors.values())
    hosted_score = sum(hosted_factors.values())

    if template_score > hosted_score:
        return "template", template_score, "Consider template delivery for greater control"
    else:
        return "hosted", hosted_score, "Hosted delivery recommended for easier management"

# Example usage
client_needs = {
    "has_devops_team": True,
    "strict_compliance": True,
    "complex_integrations": True,
    "prefer_lower_monthly": True
}

mode, score, reason = recommend_deployment_mode(client_needs)
print(f"Recommended: {mode} delivery (score: {score}) - {reason}")
```

### Configuration Validation Patterns

```python
def validate_business_requirements(client_config, business_type):
    """Validate client configuration meets business requirements"""

    validation_rules = {
        "ecommerce": {
            "required_integrations": ["payment_processing", "inventory_management"],
            "recommended_tiers": ["tier2", "tier3_dual_delivery"],
            "min_monthly_budget": 100
        },
        "content_publishing": {
            "required_features": ["cms_integration", "seo_optimization"],
            "recommended_engines": ["astro", "gatsby", "nextjs"],
            "performance_requirements": ["fast_build", "cdn_optimization"]
        },
        "corporate": {
            "required_features": ["professional_design", "contact_forms"],
            "security_requirements": ["ssl_certificates", "backup_strategy"],
            "compliance_needs": ["gdpr_ready", "accessibility"]
        }
    }

    rules = validation_rules.get(business_type)
    if not rules:
        return True, "No specific validation rules for business type"

    # Check monthly budget
    if "min_monthly_budget" in rules:
        if client_config.monthly_cost_range[1] < rules["min_monthly_budget"]:
            return False, f"Monthly budget too low for {business_type} requirements"

    # Check tier compatibility
    if "recommended_tiers" in rules:
        if client_config.service_tier not in rules["recommended_tiers"]:
            return False, f"Service tier {client_config.service_tier} not recommended for {business_type}"

    return True, "Configuration meets business requirements"

# Usage example
ecommerce_client = shopify_client(
    "store", "Online Store", "store.com", "admin@store.com",
    integration_level="basic"
)

is_valid, message = validate_business_requirements(ecommerce_client, "ecommerce")
print(f"Validation result: {is_valid} - {message}")
```

### Bulk Client Management

```python
def create_multi_client_deployment():
    """Pattern for managing multiple related clients"""

    clients = {}

    # Agency managing multiple client sites
    agency_clients = [
        ("restaurant-a", "Restaurant A", "restauranta.com"),
        ("restaurant-b", "Restaurant B", "restaurantb.com"),
        ("restaurant-c", "Restaurant C", "restaurantc.com")
    ]

    for client_id, name, domain in agency_clients:
        client = individual_client(
            client_id, name, domain, f"admin@{domain}"
        )
        clients[client_id] = client

        print(f"Created {client.deployment_name}")
        print(f"  Cost: ${client.monthly_cost_range[0]}-${client.monthly_cost_range[1]}/month")
        print(f"  Stack: {client.stack_type}")
        print()

    return clients

# Deploy all clients
clients = create_multi_client_deployment()

# Generate deployment commands
for client_id, client in clients.items():
    print(f"uv run cdk deploy {client.deployment_name}")
```

### Error Handling and Recovery

```python
from pydantic import ValidationError
import logging

def safe_client_creation(client_data):
    """Safely create client with comprehensive error handling"""

    try:
        # Attempt client creation
        client = ClientConfig.model_validate(client_data)

        # Business logic validation
        if client.service_tier == "tier1" and client.monthly_cost_range[1] > 150:
            raise ValueError("Tier 1 monthly costs cannot exceed $150")

        # Matrix validation
        from clients._templates.matrix_parser import get_matrix
        matrix = get_matrix()

        if not matrix.validate_pricing(
            client.stack_type,
            setup_cost=sum(client.setup_cost_range) // 2,
            monthly_fee=sum(client.monthly_cost_range) // 2
        ):
            raise ValueError("Pricing validation failed against matrix")

        return client, None

    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error['loc'])
            error_details.append(f"{field}: {error['msg']}")

        return None, f"Validation errors: {'; '.join(error_details)}"

    except ValueError as e:
        return None, f"Business rule violation: {str(e)}"

    except Exception as e:
        logging.error(f"Unexpected error creating client: {e}")
        return None, f"Unexpected error: {str(e)}"

# Usage with error handling
client_data = {
    "client_id": "test-client",
    "company_name": "Test Company",
    # ... other fields
}

client, error = safe_client_creation(client_data)
if error:
    print(f"Failed to create client: {error}")
else:
    print(f"Successfully created: {client.deployment_name}")
```

## Essential Commands Reference

```bash
# Environment setup
uv sync                                    # Install dependencies
uv run python -c "import pydantic; print(pydantic.__version__)"  # Verify setup

# Client configuration
uv run python -c "from clients._templates.client_config import small_business_client; print(small_business_client('test', 'Test', 'test.com', 'admin@test.com'))"

# Matrix operations
uv run python -c "from clients._templates.matrix_parser import get_matrix; matrix = get_matrix(); print(matrix.get_recommended_stacks('small_business', 'medium_ecommerce'))"

# Deployment operations
uv run cdk list                            # List all stacks
uv run cdk deploy WebServices-SharedInfra  # Deploy shared infrastructure
uv run cdk deploy [ClientStack]           # Deploy client stack
uv run cdk destroy [ClientStack]          # Remove client stack

# Validation and testing
uv run pytest tests/ -v                   # Run all tests
uv run pytest tests/test_client_config.py # Test specific module
uv run black .                            # Format code
uv run ruff check .                       # Lint code
```

## License

MIT License - See LICENSE file for details.
