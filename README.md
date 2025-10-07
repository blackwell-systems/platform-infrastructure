# Dual-Delivery Web Services Infrastructure

Multi-client web development services infrastructure using AWS CDK with flexible service delivery models.

## Overview

This repository contains the infrastructure-as-code for a web development services business supporting **dual-delivery service models**: hosted solutions (managed service) and consulting templates (infrastructure code delivery). It implements a monorepo architecture organized by delivery capability for maximum flexibility and operational efficiency.

## Current Implementation Status

✅ **Dual-Delivery Service Model**: Complete service delivery flexibility
✅ **30 Hosted Stack Variants**: Comprehensive technology matrix
✅ **Shared Infrastructure**: Operational backbone for hosted clients
✅ **Pydantic Client Configuration**: Type-safe validation and configuration management
✅ **Migration Specialization**: 7 specialized migration service stacks

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

- Python 3.13+
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
- Zero-downtime migration execution with SEO preservation
- Targeting 525,000+ businesses on end-of-life platforms
- Revenue focus: 40% of business from migration services

### Repository Structure

```
web-services-infrastructure/
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

## Business Model Integration

This infrastructure directly supports the dual-delivery business model:

- **Service Delivery Flexibility**: Support both hosted and template delivery modes
- **Operational Efficiency**: 90% reduction in management overhead through shared infrastructure
- **Cost Leadership**: $5.80/month serves unlimited hosted clients vs $50-75/month per client traditional
- **Migration Market**: Infrastructure for 40% of revenue from 525,000+ legacy platform migrations
- **Scalable Growth**: Sub-linear operational scaling (100 clients = 1.5x effort of 10 clients)

## Development Workflow

### Client Configuration with Pydantic

```python
from clients._templates.client_config import (
    individual_client, small_business_client, enterprise_client
)

# Tier 1 hosted client
client = individual_client(
    "demo-client", "Demo Company", "demo.com", "admin@demo.com"
)

# Dual-delivery client (hosted mode)
client = enterprise_client(
    "tech-corp", "Tech Corp", "techcorp.com", "devops@techcorp.com",
    deployment_mode="hosted"
)

# Dual-delivery client (template mode)
client = enterprise_client(
    "enterprise-client", "Enterprise Co", "enterprise.com", "it@enterprise.com",
    deployment_mode="template"
)
```

### Client Onboarding

```bash
# Create client configuration
python -c "
from clients._templates.client_config import small_business_client
client = small_business_client('acme-corp', 'Acme Corporation', 'acme.com', 'admin@acme.com')
print(f'Created: {client}')
"

# Deploy hosted client infrastructure
cdk deploy AcmeCorp-Prod-WordPressEcsProfessionalStack

# Or generate template for client AWS account
cdk synth AcmeCorp-Prod-WordPressEcsProfessionalStack --deployment-mode template
```
## Documentation

- [CDK Strategy Document](../cdk-strategy.md): Complete business strategy and implementation plan
- [Development Services](../development-services.md): Service offerings and pricing
- [Tech Stack Matrix](../tech-stack-product-matrix.md): Technology and service mappings

## Security

- **Client Isolation**: IAM-based isolation with resource tagging
- **Encryption**: At-rest and in-transit encryption for all data
- **Access Control**: Role-based access with least privilege principles
- **Audit Logging**: Complete CloudTrail logging across all resources

## License

MIT License - See LICENSE file for details.
