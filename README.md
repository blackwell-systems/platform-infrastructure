# Web Services Infrastructure

Multi-client web development services infrastructure using AWS CDK.

## Overview

This repository contains the infrastructure-as-code for a web development services business that serves multiple clients across different service tiers. It implements a monorepo architecture with client-centric organization for operational efficiency and cost optimization.

## Phase 1 - Week 1 Implementation Status

✅ **Repository Structure**: Complete monorepo organization  
✅ **Shared Infrastructure**: Basic operational infrastructure stack  
✅ **Client Configuration**: Schema and validation system  
✅ **CDK Application**: Basic deployment framework  

### Current Features

- **SharedInfraStack**: Operational infrastructure for business management
  - Business domain DNS management (Route53)
  - Centralized monitoring and alerting (CloudWatch + SNS)
  - Cost allocation and billing foundation
  - Shared storage for operations and backups
- **Client Configuration System**: Pydantic-based validation for client configs
- **Service Tier Templates**: Ready-to-use configurations for Tiers 1, 2, and 3

## Quick Start

### Prerequisites

- Python 3.9+
- AWS CLI configured
- Node.js (for CDK CLI)
- uv (recommended) or pip

### Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install CDK CLI globally
npm install -g aws-cdk

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Deploy Shared Infrastructure

```bash
# Deploy the shared operational infrastructure
cdk deploy WebServices-SharedInfra
```

## Architecture

### Service Tiers

**Tier 1: Essential Solutions** ($360-3,000 setup | $0-150/month)
- Static marketing and portfolio sites
- Template-based development
- Basic CMS solutions (Decap, Tina, Sanity, Contentful)
- Simple e-commerce (Snipcart, Foxy.io)

**Tier 2: Professional Solutions** ($2,400-9,600 setup | $50-400/month)  
- Advanced frameworks (Gatsby, Next.js, Nuxt.js, Astro)
- WordPress solutions (Lightsail, ECS)
- FastAPI backends
- Enhanced e-commerce and Shopify customizations

**Tier 3: Enterprise Solutions** ($6,000+ setup | $250+/month)
- Custom applications and enterprise platforms
- Multi-tenant SaaS platforms
- Advanced AWS services (Amplify, Serverless)
- Enterprise WordPress on ECS + RDS + ElastiCache

### Repository Structure

```
web-services-infrastructure/
├── stacks/                     # CDK stack definitions
│   ├── tier1/                  # Tier 1 service stacks
│   ├── tier2/                  # Tier 2 service stacks  
│   ├── tier3/                  # Tier 3 service stacks
│   ├── commerce/               # Commerce-specific patterns
│   ├── migration/              # Legacy migration support
│   └── shared/                 # Shared operational infrastructure
├── clients/                    # Client configurations
│   └── _templates/             # Configuration templates
├── constructs/                 # Reusable CDK constructs
├── tools/                      # Business automation tools
├── deploy/                     # Deployment orchestration
└── tests/                      # Infrastructure testing
```

## Business Model Integration

This infrastructure directly supports the business model outlined in the strategy documents:

- **Cost Optimization**: 20-40% AWS cost reduction through shared resources
- **Operational Efficiency**: 60-80% faster client onboarding  
- **Revenue Streams**: Complete coverage of all service offerings
- **Migration Support**: Infrastructure for 40% of revenue from legacy migrations

## Development Workflow

### Client Onboarding (Future Implementation)

```bash
# Create new client from template
python tools/client_onboarding.py create \
  --client "acme-corp" \
  --tier 3 \
  --services "wordpress_ecs,migration_support" \
  --domain "acme.com"

# Deploy client infrastructure
cdk deploy acme-corp-prod-wordpress-ecs
```

### Daily Operations (Future Implementation)

```bash
# Health check across all clients
python tools/health_checker.py --all-clients

# Cost optimization analysis
python tools/cost_optimizer.py --analyze-all

# Generate monthly billing reports
python tools/billing_reporter.py --month 2025-01
```

## Next Steps (Phase 1 - Weeks 2-4)

- [ ] **Week 2**: Client onboarding automation and deployment orchestration
- [ ] **Week 3**: High-revenue Tier 1 stacks (static_marketing, astro_headless_cms, static_decap_cms)
- [ ] **Week 4**: WordPress and migration support infrastructure
- [ ] **Weeks 5-6**: CMS variants and e-commerce patterns

## Documentation

- [CDK Strategy Document](../cdk-strategy.md): Complete business strategy and implementation plan
- [Development Services](../development-services.md): Service offerings and pricing
- [Tech Stack Matrix](../tech-stack-product-matrix.md): Technology and service mappings

## Security

- **Client Isolation**: IAM-based isolation with resource tagging
- **Encryption**: At-rest and in-transit encryption for all data
- **Access Control**: Role-based access with least privilege principles
- **Audit Logging**: Complete CloudTrail logging across all resources

## Contributing

This infrastructure follows the 12-week implementation timeline outlined in the CDK strategy document. Each phase builds upon the previous foundation to create a comprehensive multi-client infrastructure platform.

## License

MIT License - See LICENSE file for details.