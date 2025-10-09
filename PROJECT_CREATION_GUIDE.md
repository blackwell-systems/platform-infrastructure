# Project Creation Guide: Dual-Mode Platform Infrastructure

## Overview

This guide explains how to create new client projects using the revolutionary **dual-mode platform infrastructure**. The system provides flexible composition between any CMS and E-commerce provider, with two integration modes: **Direct** (simple webhooks) and **Event-Driven** (composition-ready).

`★ Key Innovation ─────────────────────────────────────`
• **Universal Composition**: Mix any CMS (Decap, Tina, Sanity, Contentful) with any E-commerce provider (Snipcart, Foxy, Shopify) seamlessly
• **Dual-Mode Architecture**: Choose Direct mode for simplicity or Event-Driven for advanced composition capabilities
• **Cost-Democratic**: Same architecture serves $65/month startups to $430/month enterprises through provider choice, not architectural complexity
`─────────────────────────────────────────────────`

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

## 🏗️ Dual-Mode Architecture Overview

### 🎯 Integration Modes

**Direct Mode (Simple & Familiar)**:
- Traditional webhook → build pipeline
- Perfect for simple websites, single providers
- Cost: Base provider + AWS hosting only

**Event-Driven Mode (Composition-Ready)**:
- Unified event system with SNS topics, DynamoDB, Lambda functions
- Enables seamless CMS + E-commerce composition
- Cost: Base provider + AWS hosting + ~$15-25/month for event infrastructure

### 🏭 Core Platform Components

1. **🎯 ClientServiceConfig**: Consolidated Pydantic configuration with automatic validation and cost estimation
2. **⚡ Universal SSG Support**: 6 engines (Hugo, Eleventy, Astro, Gatsby, Next.js, Nuxt.js) across all providers
3. **🔧 EventDrivenIntegrationLayer**: Central event system enabling unlimited provider composition
4. **🏗️ BaseSSGStack**: Universal foundation providing S3, CloudFront, Route53 patterns
5. **🎨 Provider Tier System**: CMS tiers and E-commerce tiers with client choice of SSG engine
6. **📊 Composition Examples**: Working patterns from $65/month to $430/month price points

## 🚀 Creating a New Project

### 🏭 Modern Approach: Direct Stack Creation with Composition

The modern way to create projects is using **ClientServiceConfig** with direct stack instantiation, enabling full composition flexibility.

#### Step 1: Define Client Configuration

```python
from models.service_config import (
    ClientServiceConfig, ServiceIntegrationConfig,
    CMSProviderConfig, EcommerceProviderConfig,
    IntegrationMode, ServiceType, ServiceTier, ManagementModel
)

# Example 1: Budget-conscious CMS site
budget_client = ClientServiceConfig(
    client_id="budget-startup",
    company_name="Budget Startup Co",
    domain="budgetstartup.com",
    contact_email="admin@budgetstartup.com",
    service_tier=ServiceTier.TIER1,
    management_model=ManagementModel.SELF_MANAGED,
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.CMS_TIER,
        ssg_engine="eleventy",
        integration_mode=IntegrationMode.DIRECT,  # Simple webhooks
        cms_config=CMSProviderConfig(
            provider="decap",
            settings={
                "repository": "budget-startup-site",
                "repository_owner": "budget-startup",
                "branch": "main"
            }
        )
    )
)

# Example 2: Professional composition (CMS + E-commerce)
professional_client = ClientServiceConfig(
    client_id="creative-agency",
    company_name="Creative Agency Co",
    domain="creativeagency.com",
    contact_email="admin@creativeagency.com",
    service_tier=ServiceTier.TIER1,
    management_model=ManagementModel.SELF_MANAGED,
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.COMPOSED_STACK,
        ssg_engine="astro",
        integration_mode=IntegrationMode.EVENT_DRIVEN,  # Composition-ready
        cms_config=CMSProviderConfig(
            provider="sanity",
            settings={
                "project_id": "abc123",
                "dataset": "production"
            }
        ),
        ecommerce_config=EcommerceProviderConfig(
            provider="snipcart",
            settings={
                "public_api_key": "key123",
                "currency": "USD"
            }
        )
    )
)

print(f"Budget client monthly cost: ~${budget_client.monthly_cost_estimate}/month")
print(f"Professional client monthly cost: ~${professional_client.monthly_cost_estimate}/month")
```

#### Step 2: Create Stacks with Dual-Mode Support

```python
from aws_cdk import App
from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack
from stacks.cms.sanity_cms_tier_stack import SanityCMSTierStack
from stacks.ecommerce.snipcart_ecommerce_stack_new import SnipcartEcommerceStack

app = App()

# Create budget CMS stack (Direct mode)
budget_cms_stack = DecapCMSTierStack(
    app,
    "BudgetStartup-CMS-Stack",
    client_config=budget_client
)

# Create professional composition (Event-driven mode)
professional_cms_stack = SanityCMSTierStack(
    app,
    "CreativeAgency-CMS-Stack",
    client_config=professional_client
)

professional_ecommerce_stack = SnipcartEcommerceStack(
    app,
    "CreativeAgency-Ecommerce-Stack",
    client_config=professional_client
)

app.synth()
```

#### Step 3: Automatic Cost Estimation

```python
# Get detailed cost breakdowns
budget_costs = budget_cms_stack.get_monthly_cost_estimate()
professional_cms_costs = professional_cms_stack.get_monthly_cost_estimate()
professional_ecommerce_costs = professional_ecommerce_stack.get_monthly_cost_estimate()

print("Budget Site Costs:")
for service, cost in budget_costs.items():
    print(f"  {service}: ${cost}")

print("\nProfessional Composition Costs:")
print("CMS Stack:")
for service, cost in professional_cms_costs.items():
    print(f"  {service}: ${cost}")
print("E-commerce Stack:")
for service, cost in professional_ecommerce_costs.items():
    print(f"  {service}: ${cost}")

total_professional = professional_cms_costs['total'] + professional_ecommerce_costs['total']
print(f"\nTotal Professional Monthly: ~${total_professional}")
```

#### Step 4: Complete Composition Examples

```python
from aws_cdk import App
from models.client_templates import tier1_composed_client

app = App()

# Budget-friendly composition ($65-90/month)
budget_composed = tier1_composed_client(
    client_id="budget-store",
    company_name="Budget Store",
    domain="budgetstore.com",
    contact_email="admin@budgetstore.com",
    cms_provider="decap",           # FREE CMS
    ecommerce_provider="snipcart",  # 2% transaction fees only
    ssg_engine="eleventy",          # Fast, reliable builds
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Create composed infrastructure
from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack
from stacks.ecommerce.snipcart_ecommerce_stack_new import SnipcartEcommerceStack

budget_cms = DecapCMSTierStack(app, "BudgetStore-CMS", client_config=budget_composed)
budget_ecommerce = SnipcartEcommerceStack(app, "BudgetStore-Ecommerce", client_config=budget_composed)

# Enterprise composition ($430-580/month)
enterprise_composed = tier1_composed_client(
    client_id="enterprise-corp",
    company_name="Enterprise Corp",
    domain="enterprisecorp.com",
    contact_email="admin@enterprisecorp.com",
    cms_provider="contentful",         # Enterprise CMS features
    ecommerce_provider="shopify_basic", # Proven e-commerce platform
    ssg_engine="gatsby",               # React ecosystem
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Create enterprise infrastructure
from stacks.cms.contentful_cms_stack import ContentfulCMSStack
from stacks.ecommerce.shopify_basic_ecommerce_stack_new import ShopifyBasicEcommerceStack

enterprise_cms = ContentfulCMSStack(app, "Enterprise-CMS", client_config=enterprise_composed)
enterprise_ecommerce = ShopifyBasicEcommerceStack(app, "Enterprise-Ecommerce", client_config=enterprise_composed)

app.synth()
```

#### Step 5: Deploy Your Dual-Mode Infrastructure

```bash
# Deploy budget site (Direct mode)
uv run cdk deploy BudgetStartup-CMS-Stack

# Deploy professional composition (Event-driven mode)
uv run cdk deploy CreativeAgency-CMS-Stack
uv run cdk deploy CreativeAgency-Ecommerce-Stack

# Deploy composed stacks
uv run cdk deploy BudgetStore-CMS BudgetStore-Ecommerce
uv run cdk deploy Enterprise-CMS Enterprise-Ecommerce

# Check all deployments
uv run cdk list
```

## 🔧 EventDrivenIntegrationLayer Deep Dive

When using Event-Driven mode, the **EventDrivenIntegrationLayer** creates a sophisticated event system that enables seamless composition between providers.

### Event Layer Architecture

```python
# Event-driven mode automatically creates:
integration_layer = EventDrivenIntegrationLayer(
    scope=stack,
    construct_id="IntegrationLayer",
    client_config=client_config
)

# Components created:
# - SNS Topics: content-events, commerce-events, build-events
# - DynamoDB Tables: unified-content-cache, build-batching
# - Lambda Functions: integration-handler, build-trigger, batching-handler
# - API Gateway: webhook endpoints for all providers
```

### Event Flow Examples

**Content Update Flow:**
```
1. Editor updates content in Sanity CMS
2. Sanity webhook → API Gateway → Integration Handler
3. Handler transforms to unified event → SNS Topic
4. Build Batching Handler receives event
5. Intelligent batching → CodeBuild trigger
6. Build completes → S3 → CloudFront invalidation
```

**E-commerce Order Flow:**
```
1. Customer places order via Snipcart
2. Snipcart webhook → API Gateway → Integration Handler
3. Handler processes order → Updates inventory in content cache
4. If product content changed → Triggers build
5. Order confirmation → Customer notification
```

### Integration Endpoints

The EventDrivenIntegrationLayer creates unified webhook endpoints:

```python
# Generated endpoints for all providers:
endpoints = integration_layer.get_integration_endpoints()

print(endpoints)
# Output:
{
    "webhook_base_url": "https://abc123.execute-api.us-east-1.amazonaws.com/prod/",
    "decap_webhook": "https://abc123.execute-api.us-east-1.amazonaws.com/prod/webhooks/decap",
    "sanity_webhook": "https://abc123.execute-api.us-east-1.amazonaws.com/prod/webhooks/sanity",
    "snipcart_webhook": "https://abc123.execute-api.us-east-1.amazonaws.com/prod/webhooks/snipcart",
    "content_api_url": "https://abc123.execute-api.us-east-1.amazonaws.com/prod/content",
    "health_check_url": "https://abc123.execute-api.us-east-1.amazonaws.com/prod/health"
}
```

## 🎯 Provider Selection Guide

### CMS Provider Comparison

| Provider | Monthly Cost | Best For | SSG Engines | Integration Modes |
|----------|-------------|----------|-------------|-------------------|
| **Decap CMS** | $0 (FREE) | Budget-conscious, technical teams | Hugo, Eleventy, Astro, Gatsby | Direct, Event-Driven |
| **Tina CMS** | $0-29 | Visual editing, small teams | Astro, Eleventy, Next.js, Nuxt | Direct, Event-Driven |
| **Sanity CMS** | $0-99 | Structured content, growing businesses | Astro, Gatsby, Next.js, Eleventy | Direct, Event-Driven |
| **Contentful** | $300+ | Enterprise teams, complex workflows | Gatsby, Astro, Next.js, Nuxt | Direct, Event-Driven |

### E-commerce Provider Comparison

| Provider | Monthly Cost | Transaction Fees | Best For | SSG Engines |
|----------|-------------|------------------|----------|-------------|
| **Snipcart** | $29-99 | 2.0% + 30¢ | Simple stores, digital products | Hugo, Eleventy, Astro, Gatsby |
| **Foxy.io** | $75-300 | 1.5% + 15¢ | Subscriptions, advanced features | Hugo, Eleventy, Astro, Gatsby |
| **Shopify Basic** | $29+ | 2.9% + 30¢ | Standard e-commerce, inventory | Eleventy, Astro, Next.js, Nuxt |

### SSG Engine Selection Matrix

| Engine | Complexity | Build Speed | Best For | CMS Compatibility | E-commerce Compatibility |
|--------|------------|-------------|----------|-------------------|-------------------------|
| **Hugo** | Technical | Fastest | Documentation, performance-critical | All CMS providers | All E-commerce providers |
| **Eleventy** | Intermediate | Very Fast | Business sites, balanced complexity | All CMS providers | All E-commerce providers |
| **Astro** | Modern | Fast | Component islands, modern sites | All CMS providers | All E-commerce providers |
| **Gatsby** | Advanced | Good | React ecosystem, GraphQL | All CMS providers | All E-commerce providers |
| **Next.js** | Advanced | Good | React apps, enterprise features | Tina, Sanity, Contentful | Astro, Next.js, Nuxt compatible |
| **Nuxt.js** | Advanced | Good | Vue ecosystem, SSR | Tina, Sanity, Contentful | Astro, Next.js, Nuxt compatible |

## 🚀 Advanced Configuration Examples

### Multi-Environment Setup

```python
# Development environment
dev_config = ClientServiceConfig(
    client_id="acme-corp-dev",
    company_name="Acme Corporation (Dev)",
    domain="dev.acme.com",
    contact_email="dev@acme.com",
    service_tier=ServiceTier.TIER1,
    management_model=ManagementModel.SELF_MANAGED,
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.CMS_TIER,
        ssg_engine="astro",
        integration_mode=IntegrationMode.DIRECT,  # Simpler for dev
        cms_config=CMSProviderConfig(
            provider="sanity",
            settings={
                "project_id": "abc123",
                "dataset": "development"
            }
        )
    )
)

# Production environment
prod_config = ClientServiceConfig(
    client_id="acme-corp",
    company_name="Acme Corporation",
    domain="acme.com",
    contact_email="admin@acme.com",
    service_tier=ServiceTier.TIER1,
    management_model=ManagementModel.SELF_MANAGED,
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.COMPOSED_STACK,
        ssg_engine="astro",
        integration_mode=IntegrationMode.EVENT_DRIVEN,  # Full composition for prod
        cms_config=CMSProviderConfig(
            provider="sanity",
            settings={
                "project_id": "abc123",
                "dataset": "production"
            }
        ),
        ecommerce_config=EcommerceProviderConfig(
            provider="snipcart",
            settings={
                "public_api_key": "prod-key123",
                "currency": "USD"
            }
        )
    )
)
```

### Template Functions for Quick Setup

For common use cases, use pre-configured templates:

```python
from models.client_templates import (
    tier1_self_managed_client,
    tier1_composed_client
)

# Self-managed CMS client
cms_client = tier1_self_managed_client(
    client_id="content-site",
    company_name="Content Site Co",
    domain="content.com",
    contact_email="admin@content.com",
    cms_provider="tina",
    ssg_engine="astro"
)

# Composed CMS + E-commerce client
composed_client = tier1_composed_client(
    client_id="full-site",
    company_name="Full Site Co",
    domain="fullsite.com",
    contact_email="admin@fullsite.com",
    cms_provider="sanity",
    ecommerce_provider="snipcart",
    ssg_engine="astro",
    integration_mode=IntegrationMode.EVENT_DRIVEN
)
```

## 🎯 Cost Planning & Decision Framework

### Budget-Based Provider Selection

**Budget-Conscious ($65-90/month)**:
```python
budget_client = tier1_composed_client(
    client_id="budget-startup",
    company_name="Budget Startup Co",
    domain="budgetstartup.com",
    contact_email="admin@budgetstartup.com",
    cms_provider="decap",           # FREE CMS
    ecommerce_provider="snipcart",  # 2% transaction fees only
    ssg_engine="eleventy",          # Fast, reliable builds
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

print(f"Monthly cost: ~$65-90 + 2% of sales")
print(f"Setup: FREE CMS + AWS hosting + event coordination")
```

**Professional ($180-220/month)**:
```python
professional_client = tier1_composed_client(
    client_id="creative-agency",
    company_name="Creative Agency Co",
    domain="creativeagency.com",
    contact_email="admin@creativeagency.com",
    cms_provider="sanity",          # Structured content CMS
    ecommerce_provider="snipcart",  # Cost-effective e-commerce
    ssg_engine="astro",             # Modern performance
    integration_mode=IntegrationMode.EVENT_DRIVEN
)
```

**Enterprise ($430-580/month)**:
```python
enterprise_client = tier1_composed_client(
    client_id="enterprise-corp",
    company_name="Enterprise Corp",
    domain="enterprisecorp.com",
    contact_email="admin@enterprisecorp.com",
    cms_provider="contentful",         # Enterprise CMS features
    ecommerce_provider="shopify_basic", # Proven e-commerce platform
    ssg_engine="gatsby",               # React ecosystem
    integration_mode=IntegrationMode.EVENT_DRIVEN
)
```

### Mode Selection Logic

```python
def choose_integration_mode(client_requirements):
    """Help clients choose the right integration mode"""

    # Factors favoring Event-Driven mode
    event_driven_factors = [
        client_requirements.get("multiple_providers", False),
        client_requirements.get("future_composition", False),
        client_requirements.get("analytics_needs", False),
        client_requirements.get("complex_workflows", False)
    ]

    # Factors favoring Direct mode
    direct_factors = [
        client_requirements.get("simple_site", False),
        client_requirements.get("minimal_cost", False),
        client_requirements.get("traditional_workflow", False)
    ]

    if sum(event_driven_factors) > sum(direct_factors):
        return IntegrationMode.EVENT_DRIVEN, "Composition capabilities recommended"
    else:
        return IntegrationMode.DIRECT, "Simple workflow recommended"

# Usage
mode, reason = choose_integration_mode({
    "multiple_providers": True,
    "future_composition": True
})
print(f"Recommended: {mode.value} - {reason}")
```

## 🚀 Deployment Process

### Step 1: Deploy Shared Infrastructure (One-time)

```bash
# Deploy shared operational infrastructure
uv run cdk deploy WebServices-SharedInfra --context account=123456789012 --context region=us-east-1
```

### Step 2: Deploy Client Stacks

```bash
# Deploy CMS-only stack (Direct mode)
uv run cdk deploy BudgetStartup-CMS-Stack

# Deploy composed stacks (Event-driven mode)
uv run cdk deploy CreativeAgency-CMS-Stack
uv run cdk deploy CreativeAgency-Ecommerce-Stack

# Deploy with parameters if needed
uv run cdk deploy Enterprise-CMS-Stack --parameters Domain=enterprisecorp.com
```

### Step 3: Verify Deployment

```bash
# Check deployment status
uv run cdk list

# Get stack outputs
aws cloudformation describe-stacks --stack-name BudgetStartup-CMS-Stack --query 'Stacks[0].Outputs'
```

## ✅ Validation and Testing

### Configuration Validation

```python
from pydantic import ValidationError

def validate_client_config(config_data: dict) -> ClientServiceConfig:
    """Validate and return client configuration."""
    try:
        client = ClientServiceConfig.model_validate(config_data)

        # Automatic validation includes:
        # - Client ID format (kebab-case)
        # - Required fields presence
        # - Provider settings validation
        # - SSG engine compatibility
        # - Cost estimation

        return client

    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        raise

# Example usage
valid_config = validate_client_config({
    "client_id": "test-client",
    "company_name": "Test Company",
    "domain": "test.com",
    "contact_email": "test@test.com",
    "service_tier": "tier1",
    "management_model": "self_managed",
    "service_integration": {
        "service_type": "cms_tier",
        "ssg_engine": "astro",
        "integration_mode": "direct",
        "cms_config": {
            "provider": "decap",
            "settings": {
                "repository": "test-repo",
                "repository_owner": "test-owner"
            }
        }
    }
})
```

### Integration Testing

```bash
# Run integration tests
uv run pytest tests/test_event_driven_integration.py -v

# Test specific provider combinations
uv run pytest tests/test_event_driven_integration.py::TestEventDrivenIntegration::test_composed_stack_creation -v

# Test cost estimation
uv run python -c "
from models.client_templates import tier1_composed_client
from models.service_config import IntegrationMode

client = tier1_composed_client(
    'test-client', 'Test Company', 'test.com', 'test@test.com',
    cms_provider='sanity', ecommerce_provider='snipcart',
    ssg_engine='astro', integration_mode=IntegrationMode.EVENT_DRIVEN
)

print(f'Monthly cost estimate: ${client.monthly_cost_estimate}')
print(f'Resource prefix: {client.resource_prefix}')
print(f'Stack type: {client.stack_type}')
"
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

### 2. Integration Mode Mismatches
```python
# ✗ Invalid combinations
# Direct mode with multiple providers
ClientServiceConfig(
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.COMPOSED_STACK,  # Requires event-driven
        integration_mode=IntegrationMode.DIRECT   # Can't compose in direct mode
    )
)

# ✓ Valid combinations
# Event-driven mode for composition
ClientServiceConfig(
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.COMPOSED_STACK,
        integration_mode=IntegrationMode.EVENT_DRIVEN  # Correct for composition
    )
)
```

### 3. Provider Settings Validation
```python
# ✗ Missing required settings
CMSProviderConfig(
    provider="decap",
    settings={}  # Missing required repository settings
)

# ✓ Complete provider settings
CMSProviderConfig(
    provider="decap",
    settings={
        "repository": "my-site",
        "repository_owner": "my-org",
        "branch": "main"
    }
)
```

## 📚 Essential Commands Reference

### Environment Setup
```bash
# Install dependencies
uv sync

# Verify setup
uv run python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"
uv run cdk --version

# Run tests
uv run pytest tests/test_event_driven_integration.py -v
```

### Configuration Examples
```bash
# Test budget composition
uv run python -c "
from models.client_templates import tier1_composed_client
from models.service_config import IntegrationMode

budget = tier1_composed_client(
    'budget-client', 'Budget Client', 'budget.com', 'admin@budget.com',
    cms_provider='decap', ecommerce_provider='snipcart',
    ssg_engine='eleventy', integration_mode=IntegrationMode.EVENT_DRIVEN
)
print(f'Budget: {budget.monthly_cost_estimate}/month')
"

# Test enterprise composition
uv run python -c "
from models.client_templates import tier1_composed_client
from models.service_config import IntegrationMode

enterprise = tier1_composed_client(
    'enterprise-client', 'Enterprise Client', 'enterprise.com', 'admin@enterprise.com',
    cms_provider='contentful', ecommerce_provider='shopify_basic',
    ssg_engine='gatsby', integration_mode=IntegrationMode.EVENT_DRIVEN
)
print(f'Enterprise: {enterprise.monthly_cost_estimate}/month')
"
```

### Stack Operations
```bash
# List all available stacks
uv run cdk list

# Show changes before deploy
uv run cdk diff

# Deploy specific stack
uv run cdk deploy [StackName]

# Remove stack
uv run cdk destroy [StackName]
```

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
```

## 🎯 Next Steps

1. **Set up your development environment** with Python 3.13+ and uv
2. **Deploy shared infrastructure** using the SharedInfraStack
3. **Try the dual-mode system**:
   ```bash
   # Test configuration creation
   uv run python -c "
   from models.service_config import ClientServiceConfig, ServiceIntegrationConfig, CMSProviderConfig, IntegrationMode
   from models.service_config import ServiceType, ServiceTier, ManagementModel

   config = ClientServiceConfig(
       client_id='test-client',
       company_name='Test Company',
       domain='test.com',
       contact_email='test@test.com',
       service_tier=ServiceTier.TIER1,
       management_model=ManagementModel.SELF_MANAGED,
       service_integration=ServiceIntegrationConfig(
           service_type=ServiceType.CMS_TIER,
           ssg_engine='astro',
           integration_mode=IntegrationMode.DIRECT,
           cms_config=CMSProviderConfig(
               provider='decap',
               settings={'repository': 'test-repo', 'repository_owner': 'test-owner'}
           )
       )
   )
   print(f'Configuration valid: {config.client_id}')
   print(f'Monthly cost: ${config.monthly_cost_estimate}')
   "
   ```

4. **Create your first dual-mode stack**:
   ```bash
   # Create and deploy a CMS stack
   uv run python -c "
   from aws_cdk import App
   from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack
   from models.client_templates import tier1_self_managed_client

   app = App()
   config = tier1_self_managed_client(
       'my-business', 'My Business', 'mybusiness.com', 'admin@mybusiness.com',
       cms_provider='decap', ssg_engine='astro'
   )
   stack = DecapCMSTierStack(app, 'MyBusiness-CMS-Stack', client_config=config)
   app.synth()
   "
   uv run cdk deploy MyBusiness-CMS-Stack
   ```

5. **For composition sites**: Use the template functions for intelligent provider combinations
6. **Explore event-driven capabilities**: Try IntegrationMode.EVENT_DRIVEN for advanced compositions
7. **Review cost implications**: Use the built-in cost estimation in ClientServiceConfig

## 📋 Architecture Benefits Summary

**🎯 For Clients:**
- Start simple (Direct mode) → upgrade to composition when needed
- Choose best-of-breed providers without vendor lock-in
- Predictable, scalable pricing as business grows ($65-430/month range)

**🎯 For Development Teams:**
- One architecture serves budget and enterprise clients
- Clean, maintainable codebase with comprehensive testing
- Future-proof: easy to add new CMS/E-commerce providers

**🎯 For Business:**
- Serve $65/month and $430/month clients with same operational model
- Democratic access to professional web development
- Maximum flexibility with minimal complexity

---

**Built with AWS CDK, Python 3.13, uv package management, and dual-mode composition architecture.**

This dual-mode platform provides the foundation for a scalable, well-organized multi-client web services platform with intelligent provider selection, comprehensive composition support, and automated cost optimization.
