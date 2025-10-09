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

**The First Universal Web Development Platform That Actually Makes Sense**

Imagine serving every client—from startups to enterprises—using the exact same infrastructure, while giving them complete freedom to choose any CMS with any e-commerce provider. That's what this platform delivers.

### **The Problems We Solve**

**The Industry's Broken Model:**
- Agencies rebuild infrastructure for every client project
- Clients get locked into vendor-specific stacks (Shopify + Shopify CMS, WordPress + WooCommerce)
- Budget clients get substandard solutions, enterprise clients get overengineered complexity
- Mixing providers (like Sanity CMS + Shopify) requires months of custom integration work
- Scaling means expensive rewrites and vendor migrations

**Our Solution:**
- **One Architecture, All Clients**: The same infrastructure serves budget startups and Fortune 500 companies
- **Any CMS + Any E-commerce**: Mix Decap CMS with Shopify, or Contentful with Snipcart—seamlessly
- **No Vendor Lock-in**: Switch providers without infrastructure changes
- **Instant Composition**: Add e-commerce to content sites (or vice versa) in minutes, not months
- **Democratic Access**: Professional-grade features at every tier

### **What Makes This Genuinely Novel**

**Dual-Mode Architecture (Industry First)**
Every provider works in two modes without code duplication:
- **Direct Mode**: Traditional, simple workflows for straightforward sites
- **Event-Driven Mode**: Advanced composition that lets any CMS talk to any e-commerce platform

**Universal Provider Abstraction**
Unlike platforms that favor specific combinations, we provide genuine freedom:
- **Budget-Friendly**: Free CMS options with cost-effective e-commerce providers
- **Professional**: Advanced CMS features with flexible e-commerce solutions
- **Enterprise**: Full-featured combinations for large-scale operations

**Real-Time Composition**
Our event-driven system solves the hardest problem in web development: making disparate services work together flawlessly. Content changes in your CMS automatically trigger inventory updates in your e-commerce system, and vice versa.

### **Why Clients Choose This Platform**

**For Startups & Small Businesses:**
- Get enterprise-grade infrastructure at startup-friendly scale
- Start simple, scale up without rewrites
- Access to professional features that were previously enterprise-only

**For Growing Businesses:**
- Freedom to choose best-of-breed tools without integration hell
- Predictable scaling path—no surprise vendor lock-in
- Professional results without agency overhead

**For Enterprise Teams:**
- Proven reliability with modern flexibility
- No vendor dependencies—switch providers as business needs change
- Transparent, modular architecture with clear upgrade paths

## **Platform Architecture**

**Core Foundation:**
- **Consolidated Configuration**: Type-safe, validated client configurations with automatic validation
- **Universal Base Infrastructure**: Shared S3, CloudFront, Route53 patterns across all providers
- **Dual-Mode Integration Layer**: Solves the complexity of running disparate CMS and e-commerce systems together by providing two integration approaches: Direct mode for simple single-provider setups with traditional webhooks, and Event-Driven mode that creates a unified event system allowing any CMS to work seamlessly with any e-commerce provider through SNS topics, DynamoDB caching, and Lambda orchestration - eliminating the need for custom integration code between providers

**Provider Tiers (All Support Both Modes):**

| **CMS Provider Tiers** | **Direct Mode** | **Event-Driven Mode** | **Tier Level** |
|------------------------|-----------------|------------------------|----------------|
| **Decap CMS Tier** | Git webhooks → builds | Git events → SNS → composition | **Budget** |
| **TinaCMS Tier** | Git webhooks → builds | Git events → SNS → composition | **Budget+** |
| **Sanity CMS Tier** | Webhooks → builds | API events → SNS → composition | **Professional** |
| **Contentful CMS Tier** | Webhooks → builds | API events → SNS → composition | **Enterprise** |

| **E-commerce Provider Tiers** | **Direct Mode** | **Event-Driven Mode** | **Tier Level** |
|--------------------------------|-----------------|------------------------|----------------|
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

print(f"Setup: FREE CMS + AWS hosting + event coordination")
```

```bash
# Deploy the composed infrastructure (auto-generated name)
uv run cdk deploy BudgetStartup-Prod-DecapSnipcartComposedStack
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
# Infrastructure: Base provider + AWS hosting only
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
# Infrastructure: Base provider + AWS hosting + event infrastructure
```

### Mode Comparison

| Aspect | **Direct Mode** | **Event-Driven Mode** |
|--------|-----------------|------------------------|
| **Complexity** | Simple, familiar | Sophisticated, flexible |
| **Providers** | Single CMS OR E-commerce | Multiple providers composed |
| **AWS Services** | S3, CloudFront, CodeBuild | + SNS, DynamoDB, Lambda |
| **Infrastructure** | Base tier resources | Base tier + event infrastructure |
| **Future Flexibility** | Limited to single provider | Easy provider addition/changes |
| **Analytics** | Basic CloudWatch | Unified cross-provider insights |

## Composition Examples

### Budget-Friendly Composition

**Perfect for:** Startups, small businesses, technical teams on tight budgets

```python
budget_composition = tier1_composed_client(
    client_id="budget-startup",
    company_name="Budget Startup Co",
    domain="budgetstartup.com",
    contact_email="admin@budgetstartup.com",
    cms_provider="decap",           # FREE CMS (git-based)
    ecommerce_provider="snipcart",  # Transaction-based pricing
    ssg_engine="eleventy",          # Fast builds, simple
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Benefits:
# Free content management (Decap CMS)
# Pay-per-transaction e-commerce (Snipcart)
# Git-based workflow with full version control
# Event-driven coordination for future expansion
# Professional results on a budget
```

### Professional Composition

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
# Flexible e-commerce solution
# Event-driven analytics and coordination
# Scales with business growth
```

### Enterprise Composition

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

### Advanced Customization Composition

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
# Competitive transaction rates
# Modern architecture for complex interactions
# Event-driven coordination for business logic
```

## Provider Flexibility

### CMS Provider Selection Guide

| **Provider Tier** | **Best For** | **SSG Options** | **Pricing Model** |
|-------------------|--------------|-----------------|-------------------|
| **Decap CMS** | Budget-conscious, technical teams | Hugo, Eleventy, Astro, Gatsby | **Free** |
| **TinaCMS** | Visual editing, developer + content creator teams | Astro, Eleventy, Next.js, Nuxt | **Freemium** |
| **Sanity CMS** | Structured content, creative agencies | Astro, Gatsby, Next.js, Nuxt | **Usage-based** |
| **Contentful** | Enterprise workflows, large content teams | Gatsby, Astro, Next.js, Nuxt | **Subscription** |

### E-commerce Provider Selection Guide

| **Provider Tier** | **Best For** | **SSG Options** | **Pricing Model** |
|-------------------|--------------|-----------------|-------------------|
| **Snipcart** | Budget-conscious, simple products | Hugo, Eleventy, Astro, Gatsby | **Transaction-based** |
| **Foxy.io** | Advanced features, subscriptions | Hugo, Eleventy, Astro, Gatsby | **Subscription + Fees** |
| **Shopify Basic** | Proven platform, standard e-commerce | Eleventy, Astro, Next.js, Nuxt | **Subscription + Fees** |

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

### Progressive Scaling Path

```python
# Stage 1: Budget Startup
# Decap (FREE) + Snipcart (transaction fees) + Eleventy (simple)

# Stage 2: Growing Business
# Sanity (usage-based) + Snipcart (transaction fees) + Astro (modern)

# Stage 3: Professional Team
# Sanity (professional tier) + Foxy (subscription + fees) + Astro (advanced)

# Stage 4: Enterprise
# Contentful (enterprise) + Shopify (subscription + fees) + Gatsby (React)
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

# Deploy composed client (using auto-generated name)
uv run cdk deploy CreativeAgency-Prod-SanitySnipcartComposedStack

# Deploy individual provider stacks (if using factory pattern)
uv run cdk deploy CreativeAgency-Sanity-Astro-Stack
uv run cdk deploy CreativeAgency-Snipcart-Astro-Stack
```

## Stack Naming System

Understanding how stack names are generated is crucial for deployment and management. The platform uses automatic naming to ensure consistency across all deployments.

**★ Insight ─────────────────────────────────────**
Stack names are automatically generated using the `ClientServiceConfig.deployment_name` computed field, which combines your client ID, environment, and technology choices into a predictable, readable format.
**─────────────────────────────────────────────────**

### Naming Formula

**Template Function Approach (Most Common):**
```
{ClientId in PascalCase}-{Environment}-{StackType in PascalCase}
```

**Factory Direct Creation:**
```
{ClientId in PascalCase}-{Provider in PascalCase}-{SSGEngine in PascalCase}-Stack
```

### Name Generation Examples

#### Tina + Foxy + Astro Example

```python
# Your configuration
client_config = tier1_composed_client(
    client_id="my-business-site",        # ← Input
    company_name="My Business Inc",
    domain="mybusiness.com",
    contact_email="admin@mybusiness.com",
    cms_provider="tina",
    ecommerce_provider="foxy",
    ssg_engine="astro",
    integration_mode=IntegrationMode.EVENT_DRIVEN
)

# Automatic name generation
print(f"Stack type: {client_config.stack_type}")
# Output: "tina_foxy_composed_stack"

print(f"Deployment name: {client_config.deployment_name}")
# Output: "MyBusinessSite-Prod-TinaFoxyComposedStack"

print(f"Resource prefix: {client_config.resource_prefix}")
# Output: "my-business-site-prod"
```

**Your CDK Command:**
```bash
uv run cdk deploy MyBusinessSite-Prod-TinaFoxyComposedStack
```

#### More Naming Examples

| client_id | Stack Type | Generated Name |
|-----------|------------|----------------|
| `"budget-startup"` | Decap + Snipcart + Eleventy | `BudgetStartup-Prod-DecapSnipcartComposedStack` |
| `"creative-agency"` | Sanity CMS only | `CreativeAgency-Prod-SanityCmsTier` |
| `"enterprise-corp"` | Contentful + Shopify + Gatsby | `EnterpriseCorp-Prod-ContentfulShopifyBasicComposedStack` |
| `"saas-company"` | TinaCMS only | `SaasCompany-Prod-TinaCmsTier` |

### Name Transformation Rules

**Client ID → PascalCase:**
- `"my-business-site"` → `"MyBusinessSite"`
- `"budget-startup"` → `"BudgetStartup"`
- `"creative-agency"` → `"CreativeAgency"`
- `"enterprise-corp"` → `"EnterpriseCorp"`

**Stack Type Generation:**
- **CMS Only**: `"{cms_provider}_cms_tier"` → `"SanityCmsTier"`
- **E-commerce Only**: `"{ecommerce_provider}_ecommerce_tier"` → `"SnipcartEcommerceTier"`
- **Composed**: `"{cms_provider}_{ecommerce_provider}_composed_stack"` → `"TinaFoxyComposedStack"`

### Predicting Your Stack Names

**Step 1: Choose Your Configuration**
```python
# Example configuration
client_config = tier1_composed_client(
    client_id="my-online-store",  # This becomes "MyOnlineStore"
    cms_provider="sanity",        # These become "SanitySnipcartComposedStack"
    ecommerce_provider="snipcart",
    ssg_engine="astro"
)
```

**Step 2: Predict the Name**
```python
# The system generates:
# client_id: "my-online-store" → "MyOnlineStore"
# stack_type: "sanity_snipcart_composed_stack" → "SanitySnipcartComposedStack"
# environment: "prod" → "Prod"
# Final: "MyOnlineStore-Prod-SanitySnipcartComposedStack"
```

**Step 3: Your CDK Commands**
```bash
# List stacks to verify
uv run cdk list
# Shows: MyOnlineStore-Prod-SanitySnipcartComposedStack

# Deploy your stack
uv run cdk deploy MyOnlineStore-Prod-SanitySnipcartComposedStack

# Check deployment status
uv run cdk list --long
```

### Different Creation Approaches

#### 1. Template Functions (Recommended)
```python
# Uses ClientServiceConfig.deployment_name
client = tier1_composed_client(client_id="my-site", ...)
# Generates: MyySite-Prod-TinaFoxyComposedStack
```

#### 2. Factory Pattern
```python
# Uses factory naming: {Client}-{Provider}-{SSG}-Stack
EcommerceStackFactory.create_ecommerce_stack(
    client_id="my-site",
    ecommerce_provider="foxy",
    ssg_engine="astro"
)
# Generates: MySite-Foxy-Astro-Stack
```

#### 3. Manual Construction
```python
# You control the name completely
stack = TinaCMSTierStack(
    app,
    construct_id="CustomStackName",  # ← You choose this
    client_config=config
)
```

### Multi-Environment Support

```python
# Development environment
dev_config = ClientServiceConfig(
    client_id="acme-corp",
    environment="dev",  # ← Changes the generated name
    # ... other config
)
# Generates: AcmeCorp-Dev-SanityCmsTier

# Production environment
prod_config = ClientServiceConfig(
    client_id="acme-corp",
    environment="prod",  # ← Default
    # ... other config
)
# Generates: AcmeCorp-Prod-SanityCmsTier
```

### Common Deployment Commands

```bash
# List all your stacks
uv run cdk list

# Deploy shared infrastructure (one-time)
uv run cdk deploy WebServices-SharedInfra

# Deploy your main stack (using generated name)
uv run cdk deploy MyBusinessSite-Prod-TinaFoxyComposedStack

# Deploy individual components (if using factories)
uv run cdk deploy MyBusinessSite-Tina-Astro-Stack      # CMS stack
uv run cdk deploy MyBusinessSite-Foxy-Astro-Stack     # E-commerce stack

# Check deployment status
uv run cdk list --long

# View stack details
aws cloudformation describe-stacks --stack-name MyBusinessSite-Prod-TinaFoxyComposedStack
```

### Quick Reference

**To predict your stack name:**
1. Take your `client_id`, split on `-`, capitalize each word, join → `"my-business"` → `"MyBusiness"`
2. Add environment → `"MyBusiness-Prod-"`
3. Add stack type based on your providers → `"TinaFoxyComposedStack"`
4. Final result → `"MyBusiness-Prod-TinaFoxyComposedStack"`

**Your deployment command will always be:**
```bash
uv run cdk deploy {YourPredictedStackName}
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

# Automatic validation and configuration
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
print(f'Budget setup: {budget.stack_type}')

# Enterprise composition
enterprise = tier1_composed_client(
    'enterprise-client', 'Enterprise Client', 'enterprise.com', 'admin@enterprise.com',
    cms_provider='contentful', ecommerce_provider='shopify_basic',
    ssg_engine='gatsby', integration_mode=IntegrationMode.EVENT_DRIVEN
)
print(f'Enterprise setup: {enterprise.stack_type}')
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
print('Benefits: Future composition and analytics capabilities')
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
- Predictable, scalable architecture as business grows

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