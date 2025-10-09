# Platform Infrastructure

**Modern Multi-Client Web Development Platform with Dual-Mode Architecture**

A comprehensive infrastructure-as-code platform that democratizes professional web development through intelligent composition, cost-effective scaling, and provider flexibility. Built with AWS CDK and featuring dual-mode integration architecture.

## Table of Contents

- [Overview](#overview)
- [Architecture Revolution](#architecture-revolution)
- [Quick Start](#quick-start)
- [Dual-Mode Integration](#dual-mode-integration)
- [Composition Examples](#composition-examples)
- [Provider Flexibility](#provider-flexibility)
- [Cost-Effective Scaling](#cost-effective-scaling)
- [Development Workflow](#development-workflow)
- [Configuration System](#configuration-system)
- [Essential Commands](#essential-commands)

## Overview

This platform has undergone a **major architectural transformation**, evolving from hardcoded provider pairings to a flexible, composition-ready system that serves clients from budget-conscious startups ($65/month) to enterprise organizations ($430+/month) using the same unified architecture.

### **What Makes This Platform Unique**

- **Dual-Mode Architecture**: Choose Direct (simple) or Event-Driven (composition-ready) integration per client needs
- **Universal Composition**: Mix any CMS with any E-commerce provider seamlessly
- **Cost-Democratic**: Same architecture serves budget and enterprise clients with appropriate provider choices
- **Future-Proof**: Easy to add new CMS/E-commerce providers without architectural changes
- **Clean Configuration**: Consolidated from 1,538+ lines of sprawling config to 780 lines of validated models
- **Production-Ready**: Comprehensive testing with working event-driven integration

### **Who This Platform Serves**

**For Development Teams:**
- Consistent, scalable infrastructure patterns across diverse client projects
- One architecture that scales from simple static sites to complex compositions

**For Web Agencies:**
- Serve budget clients and enterprise clients with the same operational model
- Mix best-of-breed providers without vendor lock-in

**For Platform Engineers:**
- Clean, maintainable architecture with comprehensive validation
- Event-driven patterns that enable sophisticated integrations

## **Platform Architecture**

**Core Foundation:**
- **Consolidated Configuration**: Type-safe, validated client configurations with automatic cost estimation
- **Universal Base Infrastructure**: Shared S3, CloudFront, Route53 patterns across all providers
- **Dual-Mode Integration Layer**: Solves the complexity of running disparate CMS and e-commerce systems together by providing two integration approaches: Direct mode for simple single-provider setups with traditional webhooks, and Event-Driven mode that creates a unified event system allowing any CMS to work seamlessly with any e-commerce provider through SNS topics, DynamoDB caching, and Lambda orchestration - eliminating the need for custom integration code between providers

**Provider Tiers (All Support Both Modes):**

| **CMS Provider Tiers** | **Direct Mode** | **Event-Driven Mode** | **Monthly Cost** |
|------------------------|-----------------|------------------------|------------------|
| **Decap CMS Tier** | Git webhooks → builds | Git events → SNS → composition | **Budget** |
| **TinaCMS Tier** | Git webhooks → builds | Git events → SNS → composition | **Budget+** |
| **Sanity CMS Tier** | Webhooks → builds | API events → SNS → composition | **Professional** |
| **Contentful CMS Tier** | Webhooks → builds | API events → SNS → composition | **Enterprise** |

| **E-commerce Provider Tiers** | **Direct Mode** | **Event-Driven Mode** | **Monthly Cost** |
|--------------------------------|-----------------|------------------------|------------------|
| **Snipcart Tier** | Simple integration | Order events → SNS → composition | **Budget** |
| **Foxy.io Tier** | Advanced integration | Order events → SNS → composition | **Professional** |
| **Shopify Basic Tier** | Standard integration | Webhook events → SNS → composition | **Enterprise** |

## **SSG Engine Architecture & Global Distribution**

The platform provides universal support for 6 modern Static Site Generators, each optimized for global distribution via AWS CloudFront CDN.

### **Supported SSG Engines**

| **SSG Engine** | **Runtime** | **Build Speed** | **Best For** | **Global CDN Performance** |
|----------------|-------------|-----------------|--------------|---------------------------|
| **Hugo** | Go binary | Fastest (1000+ pages/sec) | Technical teams, blogs | Excellent (static assets) |
| **Eleventy** | Node.js 20 | Very Fast | Flexible templating, agencies | Excellent (static assets) |
| **Astro** | Node.js 20 | Fast | Component islands, modern sites | Outstanding (partial hydration) |
| **Gatsby** | Node.js 20 | Good | React ecosystem, GraphQL | Very Good (React hydration) |
| **Next.js** | Node.js 20 | Good | Enterprise React apps | Outstanding (edge computing) |
| **Nuxt.js** | Node.js 20 | Good | Vue ecosystem, SSR | Outstanding (edge computing) |

### **Global CDN Distribution Architecture**

Every SSG engine benefits from the same optimized global distribution:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Build System  │───▶│   S3 Origin      │───▶│  CloudFront CDN     │
│                 │    │                  │    │                     │
│ • CodeBuild     │    │ • Static Assets  │    │ • Global Edge Cache │
│ • Node.js 20    │    │ • Gzip/Brotli    │    │ • Price Class 100   │
│ • Engine-Spec   │    │ • Versioning     │    │ • 24hr TTL          │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                              ▲                           │
                              │                           ▼
                    ┌─────────────────┐         ┌─────────────────────┐
                    │  Event System   │         │   Global Audience   │
                    │                 │         │                     │
                    │ • Build Events  │         │ • <200ms latency    │
                    │ • Cache Inval   │         │ • 99.9% uptime      │
                    │ • Deploy Status │         │ • Auto-scale        │
                    └─────────────────┘         └─────────────────────┘
```

### **SSG Engine Build Specifications**

Each engine has optimized build configurations:

<details>
<summary><strong>Hugo Build Spec</strong></summary>

```yaml
Runtime: Go 1.19
Build Command: hugo --minify
Output Directory: public
Build Time: ~30 seconds (1000+ pages)
CDN Optimization:
  - Static asset bundling
  - Automatic minification
  - Image optimization
```
</details>

<details>
<summary><strong>Eleventy Build Spec</strong></summary>

```yaml
Runtime: Node.js 20
Build Command: npx @11ty/eleventy
Output Directory: _site
Build Time: ~45 seconds (1000+ pages)
CDN Optimization:
  - JavaScript module bundling
  - CSS optimization
  - Template caching
```
</details>

<details>
<summary><strong>Astro Build Spec</strong></summary>

```yaml
Runtime: Node.js 20
Build Command: npm run build
Output Directory: dist
Build Time: ~60 seconds (component islands)
CDN Optimization:
  - Partial hydration support
  - Component-level caching
  - Modern JS delivery
```
</details>

<details>
<summary><strong>Modern Framework Build Specs</strong></summary>

**Gatsby:**
```yaml
Runtime: Node.js 20
Build Command: gatsby build
Output Directory: public
Build Time: ~90 seconds (GraphQL optimization)
CDN Features: React hydration, GraphQL caching
```

**Next.js:**
```yaml
Runtime: Node.js 20
Build Command: npm run build && npm run export
Output Directory: out
Build Time: ~75 seconds (SSG mode)
CDN Features: Edge computing, API routes
```

**Nuxt.js:**
```yaml
Runtime: Node.js 20
Build Command: npm run generate
Output Directory: dist
Build Time: ~75 seconds (SSG mode)
CDN Features: Vue hydration, Nitro engine
```
</details>

## **Event-Driven Integration Layer Architecture**

The EventDrivenIntegrationLayer is the heart of the composition system, enabling seamless integration between any CMS and E-commerce provider through a unified event system.

### **Event Layer Components**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EventDrivenIntegrationLayer                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │   SNS Topics    │  │  DynamoDB       │  │  Lambda         │            │
│  │                 │  │  Tables         │  │  Functions      │            │
│  │ • ContentEvents │  │                 │  │                 │            │
│  │ • OrderEvents   │  │ • UnifiedCache  │  │ • Integration   │            │
│  │ • BuildEvents   │  │ • BuildBatch    │  │ • BuildTrigger  │            │
│  │                 │  │ • EventStore    │  │ • BatchHandler  │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│           │                     │                     │                    │
│           └─────────┬───────────┼─────────────────────┘                    │
│                     │           │                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                 HTTP API Gateway Integration                        │  │
│  │                                                                     │  │
│  │  POST /webhooks/{provider}  ←  Unified webhook router              │  │
│  │  GET  /content/{id}         ←  Content API for builds              │  │
│  │  GET  /health               ←  Health check endpoint               │  │
│  │                                                                     │  │
│  │  Supported providers: decap, tina, sanity, contentful,             │  │
│  │                      snipcart, foxy, shopify_basic                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **Unified Webhook Router (Production-Ready)**

The platform features a production-ready unified webhook router built with HTTP API Gateway, providing enterprise-grade security and cost optimization:

**Key Features:**
- **Single Endpoint**: `POST /webhooks/{provider}` handles all providers
- **70% Cost Reduction**: HTTP API Gateway vs REST API Gateway
- **Production Security**: Signature verification, replay protection, idempotency
- **Comprehensive Monitoring**: Per-provider CloudWatch metrics
- **Auto-scaling**: Built-in burst protection and error handling

**Security Layers (Processing Order):**
1. **Signature Verification** - Provider-specific HMAC validation
2. **Timestamp Validation** - Replay attack prevention (5-minute window)
3. **JSON Validation** - Payload parsing and content-type checking
4. **Idempotency Check** - DynamoDB-based duplicate prevention (24h TTL)
5. **Content Processing** - Provider adapter registry normalization

**Production Features:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                   Unified Webhook Router                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  HTTP API Gateway → Lambda Proxy v2 → Security Layers              │
│                                                                     │
│  Security:           Monitoring:         Storage:                   │
│  • Signature Auth    • CloudWatch        • DynamoDB Cache          │
│  • Replay Protection • Per-provider      • Webhook Receipts       │
│  • Idempotency       • Error tracking    • Event Store            │
│  • Input Validation  • Latency metrics   • TTL Cleanup            │
│                                                                     │
│  Response Format:    Error Handling:     Performance:              │
│  • Standardized     • Detailed context   • <100ms avg response    │
│  • Request IDs      • Support guidance   • Burst protection       │
│  • API versioning   • Retry guidance     • Auto-scaling           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### **Event Flow Architecture**

**1. Content Events Flow:**
```
CMS Provider → POST /webhooks/{provider} → Security Layers → Integration Handler → SNS Topic
     ↓
Unified Content Cache (DynamoDB) ← Build Batching Handler ← SNS Subscription
     ↓
Build Trigger → CodeBuild → S3 → CloudFront Invalidation
```

**2. E-commerce Events Flow:**
```
E-commerce Provider → POST /webhooks/{provider} → Security Layers → Integration Handler → SNS Topic
     ↓
Order Processing → Inventory Updates → Content Cache Update → Build Trigger
```

**3. Unified Event Schema (Versioned):**
```json
{
  "schema_version": "1.0",
  "event_type": "content_updated|order_placed|inventory_changed",
  "provider": "decap|sanity|contentful|tina|snipcart|foxy|shopify_basic",
  "content_id": "unique-content-identifier",
  "content_type": "article|page|product|order",
  "timestamp": "2023-01-01T00:00:00Z",
  "data": {
    "provider_specific_payload": "...",
    "unified_fields": "...",
    "build_required": true,
    "priority": "high|normal|low"
  }
}
```

### **Event Layer Components Detail**

**SNS Topics:**
- `content-events`: All CMS content changes
- `commerce-events`: E-commerce transactions and inventory
- `build-events`: Build status and deployment notifications
- Message filtering reduces costs by 80%

**DynamoDB Tables:**
- `unified-content-cache`: GSI-optimized content storage
- `build-batching`: Intelligent build scheduling
- `event-audit`: Event history and debugging
- Pay-per-request billing for cost efficiency

**Lambda Functions:**
- `integration-handler`: Provider webhook processing
- `build-trigger-handler`: Intelligent build decisions
- `build-batching-handler`: Cost-optimized build scheduling
- Optimized for 512MB memory, 30-second timeout

## **Composition and Inheritance Structure**

The platform uses a clean inheritance hierarchy that enables flexible composition:

```
                    ┌─────────────────────┐
                    │   ClientServiceConfig│
                    │                     │
                    │ • client_id         │
                    │ • service_tier      │
                    │ • integration_mode  │
                    │ • cms_config        │
                    │ • ecommerce_config  │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   BaseSSGStack      │
                    │   (Abstract Base)   │
                    │                     │
                    │ • S3 + CloudFront   │
                    │ • Route53 + ACM     │
                    │ • Build Role        │
                    │ • Cost Estimation   │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼───────┐ ┌─────▼─────┐ ┌──────▼──────┐
    │  CMS Tier       │ │ E-commerce│ │ Jekyll      │
    │  Stacks         │ │ Stacks    │ │ Stack       │
    │                 │ │           │ │             │
    │ • DecapCMS      │ │ • Snipcart│ │ • GitHub    │
    │ • SanityCMS     │ │ • Foxy    │ │   Integration│
    │ • ContentfulCMS │ │ • Shopify │ │ • Theme Sys │
    │ • TinaCMS       │ │           │ │             │
    └─────────────────┘ └───────────┘ └─────────────┘
```

### **Composition Pattern**

**Direct Mode Composition:**
```python
# Simple: One provider, direct webhooks
client_config = ClientServiceConfig(
    integration_mode=IntegrationMode.DIRECT,
    cms_config=CMSProviderConfig(provider="decap"),
    ssg_engine="hugo"
)

# Result: DecapCMSTierStack with direct GitHub webhooks
```

**Event-Driven Mode Composition:**
```python
# Complex: Multiple providers, unified events
client_config = ClientServiceConfig(
    integration_mode=IntegrationMode.EVENT_DRIVEN,
    cms_config=CMSProviderConfig(provider="sanity"),
    ecommerce_config=EcommerceProviderConfig(provider="snipcart"),
    ssg_engine="astro"
)

# Result: SanityCMSTierStack + SnipcartEcommerceStack + EventDrivenIntegrationLayer
```

### **Stack Inheritance Chain**

```python
class DecapCMSTierStack(BaseSSGStack):
    """
    Inherits: S3, CloudFront, Route53, build infrastructure
    Adds: Decap CMS admin, GitHub webhook handling
    Integration: Optional EventDrivenIntegrationLayer
    """

    def __init__(self, scope, construct_id, client_config):
        super().__init__(scope, construct_id, client_config)

        # Mode-specific infrastructure
        if client_config.integration_mode == IntegrationMode.EVENT_DRIVEN:
            self.integration_layer = EventDrivenIntegrationLayer(...)
            self._create_event_driven_infrastructure()
        else:
            self._create_direct_mode_infrastructure()
```

### **Provider Factory Pattern**

```python
# Dynamic provider instantiation
cms_provider = CMSProviderFactory.create_provider(
    provider_name="sanity",
    settings={"project_id": "abc123", "dataset": "production"}
)

ecommerce_provider = EcommerceProviderFactory.create_provider(
    provider_name="snipcart",
    settings={"public_api_key": "key123", "currency": "USD"}
)

# Result: Type-safe provider instances with unified interfaces
```

## Quick Start

### Prerequisites

- **Python**: 3.13+ (project requires 3.13)
- **Package Manager**: `uv` (never use pip, poetry, or conda)
- **AWS CLI**: Configured with appropriate permissions
- **Node.js**: 18+ (for CDK CLI)

### Installation

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install CDK CLI globally
npm install -g aws-cdk

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Your First Composed Client

```python
# Create a budget-conscious client with CMS + E-commerce
from models.client_templates import tier1_composed_client
from models.service_config import IntegrationMode

# Budget-friendly composition: FREE CMS + cost-effective E-commerce
budget_client = tier1_composed_client(
    client_id="budget-startup",
    company_name="Budget Startup Co",
    domain="budgetstartup.com",
    contact_email="admin@budgetstartup.com",
    cms_provider="decap",           # FREE CMS
    ecommerce_provider="snipcart",  # 2% transaction fees only
    ssg_engine="eleventy",          # Fast, simple builds
    integration_mode=IntegrationMode.EVENT_DRIVEN  # Composition-ready
)

print(f"Monthly cost: Budget tier + transaction fees")
print(f"Setup: FREE CMS + AWS hosting + event coordination")
```

```bash
# Deploy the composed infrastructure
uv run cdk deploy BudgetStartup-ComposedStack
```

## Dual-Mode Integration

The platform's key innovation is **dual-mode architecture** - every provider supports both integration approaches without code duplication.

### Direct Mode (Simple & Familiar)

**When to Use:** Simple websites, traditional workflows, cost-sensitive projects

**How it Works:**
- CMS webhooks → CodeBuild → S3/CloudFront (traditional CI/CD)
- E-commerce webhooks → build triggers (familiar patterns)
- No additional AWS services required

```python
# Direct mode configuration
client_config.service_integration.integration_mode = IntegrationMode.DIRECT

# Result: Traditional webhook → build → deploy workflow
# Cost: Base provider + AWS hosting only
```

### Event-Driven Mode (Composition-Ready)

**When to Use:** Complex compositions, multiple providers, future scalability needs

**How it Works:**
- Provider events → SNS topics → unified content system
- Cross-provider coordination and analytics
- Build optimization and intelligent batching

```python
# Event-driven mode configuration
client_config.service_integration.integration_mode = IntegrationMode.EVENT_DRIVEN

# Result: Unified event system with composition capabilities
# Cost: Base provider + AWS hosting + minimal event infrastructure fee
```

### Mode Comparison

| Aspect | **Direct Mode** | **Event-Driven Mode** |
|--------|-----------------|------------------------|
| **Complexity** | Simple, familiar | Sophisticated, flexible |
| **Providers** | Single CMS OR E-commerce | Multiple providers composed |
| **AWS Services** | S3, CloudFront, CodeBuild | + SNS, DynamoDB, Lambda |
| **Monthly Cost** | Base tier cost | Base tier + event infrastructure |
| **Future Flexibility** | Limited to single provider | Easy provider addition/changes |
| **Analytics** | Basic CloudWatch | Unified cross-provider insights |

## Composition Examples

### Budget-Friendly Composition ($65-90/month)

**Perfect for:** Startups, small businesses, technical teams on tight budgets

```python
budget_composition = tier1_composed_client(
    client_id="budget-startup",
    company_name="Budget Startup Co",
    domain="budgetstartup.com",
    contact_email="admin@budgetstartup.com",
    cms_provider="decap",           # FREE CMS (git-based)
    ecommerce_provider="snipcart",  # 2% transaction fees only
    ssg_engine="eleventy",          # Fast builds, simple
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Benefits:
# FREE content management (Decap CMS)
# No monthly e-commerce fees (Snipcart)
# Git-based workflow with full version control
# Event-driven coordination for future expansion
# Professional results under budget
```

### Professional Composition ($180-220/month)

**Perfect for:** Growing businesses, content-heavy sites, design agencies

```python
professional_composition = tier1_composed_client(
    client_id="creative-agency",
    company_name="Creative Agency Co",
    domain="creativeagency.com",
    contact_email="admin@creativeagency.com",
    cms_provider="sanity",          # Structured content CMS
    ecommerce_provider="snipcart",  # Cost-effective e-commerce
    ssg_engine="astro",             # Modern performance
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Benefits:
# Structured content with real-time collaboration
# Modern component-based architecture (Astro)
# Still cost-effective e-commerce
# Event-driven analytics and coordination
# Scales with business growth
```

### Enterprise Composition ($430-580/month)

**Perfect for:** Large content teams, enterprise workflows, proven reliability needs

```python
enterprise_composition = tier1_composed_client(
    client_id="enterprise-corp",
    company_name="Enterprise Corp",
    domain="enterprisecorp.com",
    contact_email="admin@enterprisecorp.com",
    cms_provider="contentful",         # Enterprise CMS features
    ecommerce_provider="shopify_basic", # Proven e-commerce platform
    ssg_engine="gatsby",               # React ecosystem
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Benefits:
# Enterprise-grade content workflows and permissions
# Proven e-commerce platform (Shopify)
# React ecosystem with GraphQL (Gatsby)
# Advanced team collaboration features
# Unified analytics across content and commerce
```

### Advanced Customization Composition ($300-350/month)

**Perfect for:** Complex products, subscription models, custom checkout needs

```python
advanced_composition = tier1_composed_client(
    client_id="saas-company",
    company_name="SaaS Company Inc",
    domain="saascompany.com",
    contact_email="admin@saascompany.com",
    cms_provider="sanity",     # Structured content for complex data
    ecommerce_provider="foxy", # Advanced features, subscriptions
    ssg_engine="astro",        # Modern performance
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Benefits:
# Complex content modeling (Sanity)
# Advanced e-commerce features: subscriptions, custom checkout
# Lower transaction fees
# Modern architecture for complex interactions
# Event-driven coordination for business logic
```

## Provider Flexibility

### CMS Provider Selection Guide

| **Provider Tier** | **Best For** | **SSG Options** | **Monthly Cost** |
|-------------------|--------------|-----------------|------------------|
| **Decap CMS** | Budget-conscious, technical teams | Hugo, Eleventy, Astro, Gatsby | **$50-75** |
| **TinaCMS** | Visual editing, developer + content creator teams | Astro, Eleventy, Next.js, Nuxt | **$60-85** |
| **Sanity CMS** | Structured content, creative agencies | Astro, Gatsby, Next.js, Nuxt | **$65-90** |
| **Contentful** | Enterprise workflows, large content teams | Gatsby, Astro, Next.js, Nuxt | **$75-125** |

### E-commerce Provider Selection Guide

| **Provider Tier** | **Best For** | **SSG Options** | **Monthly Cost** |
|-------------------|--------------|-----------------|------------------|
| **Snipcart** | Budget-conscious, simple products | Hugo, Eleventy, Astro, Gatsby | **$85-125** |
| **Foxy.io** | Advanced features, subscriptions | Hugo, Eleventy, Astro, Gatsby | **$100-150** |
| **Shopify Basic** | Proven platform, standard e-commerce | Eleventy, Astro, Next.js, Nuxt | **$75-125** |

### SSG Engine Selection Guide

| **SSG Engine** | **Best For** | **Complexity** | **Performance** |
|----------------|--------------|----------------|-----------------|
| **Hugo** | Technical teams, fastest builds | Advanced | Excellent |
| **Eleventy** | Balanced approach, flexible templating | Intermediate | Very Good |
| **Astro** | Modern sites, component islands | Intermediate | Excellent |
| **Gatsby** | React ecosystem, GraphQL | Advanced | Very Good |
| **Next.js** | React apps, enterprise features | Advanced | Excellent |
| **Nuxt.js** | Vue ecosystem, SSR | Advanced | Excellent |

## Cost-Effective Scaling

The platform's unified architecture enables cost-effective scaling from budget to enterprise:

### Budget Scaling Path ($65 → $430/month)

```python
# Stage 1: Budget Startup ($65-90/month)
# Decap (FREE) + Snipcart (2% fees) + Eleventy (simple)

# Stage 2: Growing Business ($180-220/month)
# Sanity ($99) + Snipcart (2% fees) + Astro (modern)

# Stage 3: Professional Team ($300-350/month)
# Sanity ($199) + Foxy ($20 + 1.5% fees) + Astro (advanced)

# Stage 4: Enterprise ($430-580/month)
# Contentful ($300) + Shopify ($29 + 2.9% fees) + Gatsby (React)
```

**Key Benefits:**
- **Same Architecture**: No rewrites, just provider upgrades
- **Gradual Scaling**: Upgrade CMS or E-commerce independently
- **Consistent Operations**: Same deployment, monitoring, backup patterns
- **Future-Proof**: Event-driven mode enables easy provider changes

## Development Workflow

### Creating Composed Clients

```python
from models.client_templates import tier1_composed_client
from models.service_config import IntegrationMode

# Step 1: Choose client requirements
client_needs = {
    "budget_conscious": True,
    "technical_team": True,
    "visual_editing": False,
    "simple_products": True
}

# Step 2: Create composed configuration
client = tier1_composed_client(
    client_id="my-client",
    company_name="My Client Co",
    domain="myclient.com",
    contact_email="admin@myclient.com",
    cms_provider="decap",           # Based on budget_conscious
    ecommerce_provider="snipcart",  # Based on simple_products
    ssg_engine="hugo",              # Based on technical_team
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Step 3: Validate and deploy
print(f"Stack type: {client.stack_type}")
print(f"Monthly cost: ${client.monthly_cost_estimate}")
print(f"Integration mode: {client.service_integration.integration_mode}")
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

### Deployment Examples

```bash
# Deploy shared infrastructure (one-time)
uv run cdk deploy WebServices-SharedInfra

# Deploy composed client (CMS + E-commerce)
uv run cdk deploy MyClient-ComposedStack

# Deploy individual provider stacks
uv run cdk deploy MyClient-CMS-Stack
uv run cdk deploy MyClient-Ecommerce-Stack
```

## Configuration System

### Consolidated Configuration Model

The platform uses a clean, validated configuration system:

```python
from models.service_config import (
    ClientServiceConfig, ServiceIntegrationConfig,
    CMSProviderConfig, EcommerceProviderConfig,
    IntegrationMode, ServiceType
)

# Complete client configuration
client_config = ClientServiceConfig(
    client_id="example-client",
    company_name="Example Company",
    domain="example.com",
    contact_email="admin@example.com",
    service_tier=ServiceTier.TIER1,
    management_model=ManagementModel.SELF_MANAGED,
    service_integration=ServiceIntegrationConfig(
        service_type=ServiceType.COMPOSED_STACK,
        integration_mode=IntegrationMode.EVENT_DRIVEN,
        ssg_engine="astro",
        cms_config=CMSProviderConfig(
            provider="sanity",
            settings={"project_id": "abc123", "dataset": "production"}
        ),
        ecommerce_config=EcommerceProviderConfig(
            provider="snipcart",
            settings={"public_api_key": "key123", "currency": "USD"}
        )
    )
)

# Automatic validation and cost estimation
print(f"Monthly cost: ${client_config.monthly_cost_estimate}")
print(f"Resource prefix: {client_config.resource_prefix}")
print(f"Stack type: {client_config.stack_type}")
```

### Template Functions

```python
# Simplified client creation with templates
from models.client_templates import (
    tier1_self_managed_client,
    tier1_composed_client,
    tier2_business_client
)

# Self-managed CMS only
cms_client = tier1_self_managed_client(
    client_id="content-site",
    company_name="Content Site",
    domain="content.com",
    contact_email="admin@content.com",
    cms_provider="tina",
    ssg_engine="astro"
)

# Composed CMS + E-commerce
composed_client = tier1_composed_client(
    client_id="full-site",
    company_name="Full Site Co",
    domain="fullsite.com",
    contact_email="admin@fullsite.com",
    cms_provider="sanity",
    ecommerce_provider="foxy",
    ssg_engine="astro"
)
```

## Essential Commands

```bash
# Environment setup
uv sync                                    # Install dependencies
uv run python -c "import aws_cdk; print('CDK ready')"  # Verify setup

# Client configuration examples
uv run python -c "
from models.client_templates import tier1_composed_client
from models.service_config import IntegrationMode

# Budget composition
budget = tier1_composed_client(
    'budget-client', 'Budget Client', 'budget.com', 'admin@budget.com',
    cms_provider='decap', ecommerce_provider='snipcart',
    ssg_engine='eleventy', integration_mode=IntegrationMode.EVENT_DRIVEN
)
print(f'Budget: {budget.monthly_cost_estimate}/month')

# Enterprise composition
enterprise = tier1_composed_client(
    'enterprise-client', 'Enterprise Client', 'enterprise.com', 'admin@enterprise.com',
    cms_provider='contentful', ecommerce_provider='shopify_basic',
    ssg_engine='gatsby', integration_mode=IntegrationMode.EVENT_DRIVEN
)
print(f'Enterprise: {enterprise.monthly_cost_estimate}/month')
"

# Stack operations
uv run cdk list                            # List all available stacks
uv run cdk diff                            # Show changes before deploy
uv run cdk deploy [StackName]              # Deploy specific stack
uv run cdk destroy [StackName]             # Remove stack

# Testing and validation
uv run pytest tests/ -v                    # Run all tests
uv run pytest tests/test_event_driven_integration.py -v  # Test composition
uv run black .                             # Format code
uv run ruff check .                        # Lint code

# Mode switching examples
uv run python -c "
from models.service_config import IntegrationMode

# Same client, different modes
print('Direct Mode: Simple webhook → build workflow')
print('Event-Driven Mode: Unified events → composition workflow')
print('Cost difference: +$15-25/month for event infrastructure')
print('Benefit: Future composition and analytics capabilities')
"

# Composition examples
uv run python examples/composed_stack_examples.py  # See all composition patterns
```

## Getting Help

- **Documentation**: All examples in this README are working code
- **Testing**: `uv run pytest tests/ -v` validates all functionality
- **Examples**: `examples/composed_stack_examples.py` shows real compositions
- **Configuration**: `models/client_templates.py` has template functions

## Architecture Benefits

**For Clients:**
- Start simple (Direct mode) → upgrade to composition when needed
- Choose best-of-breed providers without vendor lock-in
- Predictable, scalable pricing as business grows

**For Development Teams:**
- One architecture serves budget and enterprise clients
- Clean, maintainable codebase with comprehensive testing
- Future-proof: easy to add new CMS/E-commerce providers

**For Business:**
- Serve clients across budget and enterprise tiers with same operational model
- Democratic access to professional web development
- Maximum flexibility with minimal complexity

---

## License

MIT License - See LICENSE file for details.

**Built with AWS CDK, Python 3.13, and uv package management.**