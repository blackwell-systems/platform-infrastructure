# Provider Metadata Registry Architecture

## Executive Summary

The Provider Metadata Registry replaces the current in-memory `STACK_METADATA` system with a persistent, versioned, and globally distributed metadata store. This architectural improvement enables operational flexibility, business agility, and clean separation between business data and application code.

## Current System Analysis

### What STACK_METADATA Currently Contains

The current `PlatformStackFactory.STACK_METADATA` is a 235-line hardcoded dictionary containing:

- **Stack Categories**: SSG templates, foundation services, CMS tiers, E-commerce tiers, composed services
- **Rich Metadata per Stack**: Cost ranges, target markets, complexity levels, SSG compatibility, features, hosting patterns
- **Provider Information**:
  - CMS providers (decap, tina, sanity, contentful)
  - E-commerce providers (snipcart, foxy, shopify_basic)
  - SSG engines (hugo, gatsby, nextjs, nuxt, eleventy, astro, jekyll)
- **Business Intelligence**: Target market segments, best-for scenarios, key benefits

### Current Limitations

1. **Deployment Coupling**: Metadata changes require full application redeployment
2. **No External Management**: Cannot update provider data without code changes
3. **No Versioning**: No history or rollback capability for metadata changes
4. **Limited Querying**: Only accessible through programmatic API, no direct queries
5. **No Real-time Updates**: Changes require restart of all dependent services
6. **Tightly Coupled Architecture**: Business data embedded in infrastructure code

## Recommended Architecture

### 🧱 Primary Architecture: S3 + CloudFront

**Primary Store**: S3 bucket `blackwell-registry` with versioning + public-read JSONs

**Access Layer**: CloudFront distribution for global low-latency reads

**Write Access**: Signed URL or IAM role for CI/CD pipeline writes

**Usage Patterns**:
- **Core & CLI**: Fetch JSON directly from CloudFront (cached)
- **API**: Fetch & cache registry in memory / EFS
- **Versioning**: S3 Versioning + manifest.json for schema + provider versions

### Benefits of S3 + CloudFront Approach

| Aspect | Benefit | Impact |
|--------|---------|---------|
| **Cost** | ~$5-10/month vs $50+ for DynamoDB | 80-90% cost reduction |
| **Global Performance** | CloudFront edge locations worldwide | <100ms response times globally |
| **Simplicity** | JSON files in git, standard CI/CD | Familiar developer workflows |
| **Zero Deployment Coupling** | Update metadata without code deployment | Faster business iteration |
| **Built-in Caching** | CloudFront handles edge caching | High availability, low latency |

### 🧠 Future Hybrid Upgrade Path

When scaling to thousands of providers or requiring advanced analytics:

**S3 = Canonical Data (Truth)**
**DynamoDB = Indexed Cache (Fast Querying)**

A "registry indexer" Lambda can:
1. Trigger on S3 PUT events
2. Parse provider JSON
3. Insert indexed attributes into DynamoDB
4. Enable fast queries: `/search?feature=visual_editing`

## Implementation Plan

### Phase 1: S3 Registry Foundation (Week 1)

#### 1.1 Create Registry Infrastructure

```yaml
# AWS Resources
S3Bucket: blackwell-registry
  - Versioning: Enabled
  - Public Read Access: Enabled
  - CORS: Configured for web access

CloudFrontDistribution: registry.blackwell.dev
  - Origin: S3 bucket
  - Cache Behaviors: Long TTL for JSON files
  - Custom Error Pages: 404 → fallback.json

IAMRole: BlackwellRegistryWriter
  - CI/CD pipeline access
  - S3 PutObject permissions
  - CloudFront cache invalidation
```

#### 1.2 JSON Schema Design

**Directory Structure**:
```
blackwell-registry/
├── manifest.json                 # Schema version + catalog
├── providers/
│   ├── cms/
│   │   ├── decap.json
│   │   ├── sanity.json
│   │   ├── tina.json
│   │   └── contentful.json
│   ├── ecommerce/
│   │   ├── snipcart.json
│   │   ├── foxy.json
│   │   └── shopify-basic.json
│   └── ssg/
│       ├── hugo.json
│       ├── gatsby.json
│       ├── nextjs.json
│       └── nuxt.json
└── stacks/
    ├── templates/
    │   ├── hugo-template.json
    │   ├── gatsby-template.json
    │   └── nextjs-template.json
    ├── foundation/
    │   ├── marketing.json
    │   ├── developer.json
    │   └── modern-performance.json
    └── composed/
        └── cms-ecommerce-composed.json
```

**Manifest Schema**:
```json
{
  "schema_version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "providers": {
    "cms": ["decap", "sanity", "tina", "contentful"],
    "ecommerce": ["snipcart", "foxy", "shopify-basic"],
    "ssg": ["hugo", "gatsby", "nextjs", "nuxt", "eleventy", "astro", "jekyll"]
  },
  "stacks": {
    "templates": ["hugo-template", "gatsby-template", "nextjs-template", "nuxt-template"],
    "foundation": ["marketing", "developer", "modern-performance"],
    "cms-tiers": ["decap-cms-tier", "sanity-cms-tier", "tina-cms-tier", "contentful-cms-tier"],
    "ecommerce-tiers": ["snipcart-ecommerce", "foxy-ecommerce", "shopify-basic-ecommerce"],
    "composed": ["cms-ecommerce-composed"]
  },
  "cdn_urls": {
    "base": "https://registry.blackwell.dev",
    "manifest": "https://registry.blackwell.dev/manifest.json"
  }
}
```

**Provider Schema Example** (`providers/cms/sanity.json`):
```json
{
  "provider_name": "sanity",
  "provider_type": "cms",
  "display_name": "Sanity CMS",
  "tier_name": "Sanity CMS - Structured Content with Real-Time APIs",
  "category": "cms_tier_service",
  "monthly_cost_range": [65, 280],
  "setup_cost_range": [1440, 3360],
  "target_market": [
    "professional_content_teams",
    "api_first_developers",
    "structured_content_needs",
    "enterprise_ready"
  ],
  "best_for": "Professional structured content management with real-time APIs and advanced querying",
  "complexity_level": "medium_to_high",
  "cms_type": "api_based",
  "ssg_engine_options": ["nextjs", "astro", "gatsby", "eleventy"],
  "template_variants": ["structured_content", "api_driven", "professional_editorial"],
  "key_features": [
    "structured_content",
    "groq_querying",
    "real_time_apis",
    "content_validation",
    "advanced_media",
    "webhook_automation"
  ],
  "hosting_pattern": "aws_optimized",
  "performance_tier": "premium",
  "last_updated": "2024-01-15T10:30:00Z",
  "schema_version": "1.0.0"
}
```

#### 1.3 Migration Scripts

Create migration utilities in `tools/registry_migration/`:

```python
# tools/registry_migration/extract_metadata.py
"""
Extract current STACK_METADATA and convert to JSON registry format
"""

def extract_stack_metadata():
    """Convert PlatformStackFactory.STACK_METADATA to JSON files"""

def create_manifest():
    """Generate manifest.json from extracted metadata"""

def validate_json_schema():
    """Validate all JSON files against schema"""

def upload_to_s3():
    """Initial upload to blackwell-registry S3 bucket"""
```

### Phase 2: Registry Access Layer (Week 1-2)

#### 2.1 blackwell-core Registry Client

Create `blackwell_core/registry/provider_registry.py`:

```python
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json

class S3ProviderRegistry:
    """
    S3-backed provider registry with CloudFront global caching
    """

    def __init__(self,
                 cloudfront_url: str = "https://registry.blackwell.dev",
                 cache_ttl: int = 300,
                 fallback_data: Optional[Dict] = None):
        self.base_url = cloudfront_url
        self.cache_ttl = cache_ttl
        self.cache = {}  # In-memory cache with TTL
        self.fallback_data = fallback_data or {}

    async def get_manifest(self) -> Dict[str, Any]:
        """Get registry manifest with schema version and catalog"""
        return await self._fetch_cached("manifest.json")

    async def get_provider(self, category: str, name: str) -> Dict[str, Any]:
        """Get provider metadata by category and name"""
        url = f"providers/{category}/{name}.json"
        return await self._fetch_cached(url)

    async def get_stack_metadata(self, stack_type: str) -> Dict[str, Any]:
        """Get stack configuration metadata"""
        # Determine stack category and fetch appropriate JSON
        category = self._determine_stack_category(stack_type)
        url = f"stacks/{category}/{stack_type}.json"
        return await self._fetch_cached(url)

    async def get_all_providers(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all providers, optionally filtered by category"""
        manifest = await self.get_manifest()
        providers = []

        categories = [category] if category else manifest["providers"].keys()
        for cat in categories:
            for provider_name in manifest["providers"][cat]:
                provider_data = await self.get_provider(cat, provider_name)
                providers.append(provider_data)

        return providers

    async def _fetch_cached(self, path: str) -> Dict[str, Any]:
        """Fetch JSON with in-memory caching and TTL"""
        cache_key = path
        now = datetime.now()

        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if now - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_data

        # Fetch from CloudFront
        try:
            url = f"{self.base_url}/{path}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cache[cache_key] = (data, now)
                        return data
                    else:
                        raise Exception(f"HTTP {response.status}: {response.reason}")

        except Exception as e:
            # Fallback to embedded data if available
            if path in self.fallback_data:
                return self.fallback_data[path]
            raise Exception(f"Failed to fetch {path}: {e}")

    def _determine_stack_category(self, stack_type: str) -> str:
        """Determine stack category from stack type name"""
        if "template" in stack_type:
            return "templates"
        elif stack_type in ["marketing", "developer", "modern_performance"]:
            return "foundation"
        elif "composed" in stack_type:
            return "composed"
        else:
            return "templates"  # default

# Global registry instance
default_registry = S3ProviderRegistry()
```

#### 2.2 CLI Integration

Update `blackwell/core/platform_integration.py`:

```python
from blackwell_core.registry.provider_registry import default_registry
import asyncio

def get_platform_metadata() -> Dict[str, Any]:
    """
    Get platform metadata from S3 registry with graceful fallback.
    """
    if is_platform_available():
        try:
            # Try current PlatformStackFactory first
            metadata = PlatformStackFactory.STACK_METADATA
            logger.debug(f"Retrieved platform metadata: {len(metadata)} stack types")
            return metadata
        except Exception as e:
            logger.warning(f"Failed to retrieve platform metadata: {e}")

    # Fallback to S3 registry
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Fetch from registry
        manifest = loop.run_until_complete(default_registry.get_manifest())
        metadata = {}

        # Convert registry format back to STACK_METADATA format
        for category in ["templates", "foundation", "cms-tiers", "ecommerce-tiers", "composed"]:
            if category in manifest.get("stacks", {}):
                for stack_type in manifest["stacks"][category]:
                    stack_data = loop.run_until_complete(
                        default_registry.get_stack_metadata(stack_type)
                    )
                    metadata[stack_type] = stack_data

        logger.info(f"Retrieved registry metadata: {len(metadata)} stack types")
        return metadata

    except Exception as e:
        logger.error(f"Failed to retrieve registry metadata: {e}")
        return {}

    finally:
        loop.close()
```

#### 2.3 Platform Infrastructure Integration

Update `PlatformStackFactory` to use registry:

```python
# In shared/factories/platform_stack_factory.py

from blackwell_core.registry.provider_registry import default_registry
import asyncio

class PlatformStackFactory:
    # Keep STACK_METADATA as fallback during transition
    STACK_METADATA = { ... }  # Current metadata as fallback

    @classmethod
    def get_stack_metadata_from_registry(cls, stack_type: str) -> Dict[str, Any]:
        """Get stack metadata from S3 registry with fallback to embedded data"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            registry_data = loop.run_until_complete(
                default_registry.get_stack_metadata(stack_type)
            )
            return registry_data

        except Exception as e:
            _log('warning', f"Registry fetch failed, using embedded data: {e}")
            return cls.STACK_METADATA.get(stack_type, {})

        finally:
            loop.close()

    @classmethod
    def get_stack_metadata(cls, stack_type: str) -> Dict[str, Any]:
        """Get detailed metadata for a specific stack type."""
        # During transition: try registry first, fallback to embedded
        if os.getenv("USE_REGISTRY", "true").lower() == "true":
            return cls.get_stack_metadata_from_registry(stack_type)
        else:
            return cls.STACK_METADATA.get(stack_type, {})
```

### Phase 3: CI/CD Integration (Week 2)

#### 3.1 Registry Management Repository

Create `blackwell-registry` Git repository:

```
blackwell-registry/
├── .github/workflows/
│   └── deploy-registry.yml      # CI/CD pipeline
├── schemas/
│   ├── provider.schema.json     # JSON Schema validation
│   ├── stack.schema.json
│   └── manifest.schema.json
├── src/
│   ├── providers/               # JSON source files
│   ├── stacks/
│   └── manifest.json
├── scripts/
│   ├── validate.py              # Schema validation
│   ├── deploy.py                # S3 upload + CloudFront invalidation
│   └── rollback.py              # Version rollback utility
└── README.md
```

#### 3.2 CI/CD Pipeline

`.github/workflows/deploy-registry.yml`:

```yaml
name: Deploy Provider Registry

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install jsonschema boto3 pydantic

      - name: Validate JSON schemas
        run: python scripts/validate.py

      - name: Validate provider data
        run: python scripts/validate_providers.py

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to S3
        run: |
          aws s3 sync src/ s3://blackwell-registry --delete

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

      - name: Update version tags
        run: |
          git tag "v$(date +%Y%m%d-%H%M%S)"
          git push origin --tags
```

#### 3.3 Rollback Capability

`scripts/rollback.py`:

```python
import boto3
import argparse
from datetime import datetime

def rollback_registry(version_id: str = None, hours_ago: int = None):
    """
    Rollback registry to previous version
    """
    s3 = boto3.client('s3')
    bucket = 'blackwell-registry'

    if hours_ago:
        # Find version from X hours ago
        response = s3.list_object_versions(Bucket=bucket, Prefix='manifest.json')
        # Logic to find version from hours_ago

    elif version_id:
        # Use specific version ID
        pass

    # Copy old version to current
    # Invalidate CloudFront
    # Update version tracking

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version-id", help="Specific version to rollback to")
    parser.add_argument("--hours-ago", type=int, help="Rollback to version X hours ago")

    args = parser.parse_args()
    rollback_registry(args.version_id, args.hours_ago)
```

### Phase 4: Future DynamoDB Upgrade Path (Week 3+)

#### 4.1 Registry Indexer Lambda

When advanced querying is needed:

```python
import json
import boto3
from typing import Dict, Any

def lambda_handler(event, context):
    """
    Triggered on S3 PUT events to index provider metadata in DynamoDB
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('provider-metadata-index')

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if key.endswith('.json') and key != 'manifest.json':
            # Download JSON from S3
            s3_client = boto3.client('s3')
            response = s3_client.get_object(Bucket=bucket, Key=key)
            provider_data = json.loads(response['Body'].read())

            # Index in DynamoDB
            index_provider_metadata(table, key, provider_data)

def index_provider_metadata(table, key: str, data: Dict[str, Any]):
    """Index provider metadata for fast querying"""

    # Extract indexable attributes
    item = {
        'pk': key,
        'provider_name': data.get('provider_name'),
        'provider_type': data.get('provider_type'),
        'category': data.get('category'),
        'complexity_level': data.get('complexity_level'),
        'monthly_cost_min': data.get('monthly_cost_range', [0, 0])[0],
        'monthly_cost_max': data.get('monthly_cost_range', [0, 0])[1],
        'features': data.get('key_features', []),
        'ssg_engines': data.get('ssg_engine_options', []),
        'target_market': data.get('target_market', []),
        'last_updated': data.get('last_updated'),
        'raw_data': json.dumps(data)  # Store full data for retrieval
    }

    # Handle list attributes for DynamoDB
    if item['features']:
        item['features_set'] = set(item['features'])
    if item['ssg_engines']:
        item['ssg_engines_set'] = set(item['ssg_engines'])

    table.put_item(Item=item)
```

#### 4.2 Advanced Query API

```python
from fastapi import FastAPI, Query
from typing import List, Optional
import boto3

app = FastAPI()

@app.get("/search/providers")
async def search_providers(
    provider_type: Optional[str] = None,
    feature: Optional[str] = None,
    max_cost: Optional[int] = None,
    complexity: Optional[str] = None,
    ssg_engine: Optional[str] = None
):
    """
    Advanced provider search using DynamoDB index
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('provider-metadata-index')

    # Build filter expression
    filter_expressions = []
    expression_values = {}

    if provider_type:
        filter_expressions.append("provider_type = :provider_type")
        expression_values[":provider_type"] = provider_type

    if feature:
        filter_expressions.append("contains(features_set, :feature)")
        expression_values[":feature"] = feature

    if max_cost:
        filter_expressions.append("monthly_cost_min <= :max_cost")
        expression_values[":max_cost"] = max_cost

    if complexity:
        filter_expressions.append("complexity_level = :complexity")
        expression_values[":complexity"] = complexity

    if ssg_engine:
        filter_expressions.append("contains(ssg_engines_set, :ssg_engine)")
        expression_values[":ssg_engine"] = ssg_engine

    # Execute query
    scan_kwargs = {}
    if filter_expressions:
        scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
        scan_kwargs['ExpressionAttributeValues'] = expression_values

    response = table.scan(**scan_kwargs)

    # Return results
    results = []
    for item in response['Items']:
        results.append(json.loads(item['raw_data']))

    return {
        "providers": results,
        "count": len(results),
        "query": {
            "provider_type": provider_type,
            "feature": feature,
            "max_cost": max_cost,
            "complexity": complexity,
            "ssg_engine": ssg_engine
        }
    }
```

## Migration Strategy

### Week 1: Foundation
1. **Day 1-2**: Set up S3 bucket, CloudFront distribution, IAM roles
2. **Day 3-4**: Create JSON schemas and migration scripts
3. **Day 5**: Extract current STACK_METADATA to JSON format and upload

### Week 2: Integration
1. **Day 1-3**: Implement S3ProviderRegistry in blackwell-core
2. **Day 4-5**: Update CLI to use registry with fallback to embedded data

### Week 3: Platform Integration
1. **Day 1-3**: Update PlatformStackFactory to use registry
2. **Day 4-5**: Deploy to staging with dual-read mode (registry + fallback)

### Week 4: Production Rollout
1. **Day 1-2**: Production deployment with monitoring
2. **Day 3-4**: Performance validation and optimization
3. **Day 5**: Documentation and team training

## Success Metrics

### Operational Metrics
- **Deployment Coupling**: Reduce metadata update time from hours to minutes
- **Global Performance**: <100ms response times from all regions
- **Availability**: 99.9% uptime for registry access
- **Cost Efficiency**: <$10/month operational cost

### Business Metrics
- **Agility**: Business team can update provider data independently
- **Time to Market**: New provider integration from days to hours
- **Data Quality**: Versioned, validated, and auditable metadata
- **Developer Experience**: Clear separation of concerns and clean APIs

## Risk Mitigation

### Technical Risks
1. **CloudFront Cache Issues**: Implement cache invalidation in CI/CD
2. **S3 Availability**: Configure multiple fallback mechanisms
3. **JSON Schema Evolution**: Version management and backward compatibility
4. **Performance Degradation**: In-memory caching and monitoring

### Business Risks
1. **Data Consistency**: Automated validation in CI/CD pipeline
2. **Rollback Capability**: S3 versioning and automated rollback scripts
3. **Access Control**: IAM roles and signed URLs for write access
4. **Audit Trail**: Git history + S3 versioning for complete audit trail

## Conclusion

The S3 + CloudFront Provider Metadata Registry provides immediate value with minimal complexity while maintaining a clear upgrade path to advanced features. This architecture aligns with the "start simple, scale smart" principle and delivers significant operational and business benefits.

**Next Steps**: Begin Phase 1 implementation with S3 bucket setup and JSON schema design.