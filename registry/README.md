# Provider Registry

This directory contains the provider metadata registry for the platform infrastructure system. The registry uses a JSON-based approach to separate provider discovery metadata from implementation code.

## Architecture Overview

```
registry/
├── schema/                          # JSON Schema definitions
│   └── provider_metadata_schema.json
├── providers/                       # Provider metadata files
│   ├── cms/                        # CMS provider metadata
│   │   ├── tina.json
│   │   ├── sanity.json
│   │   └── decap.json
│   └── ecommerce/                  # E-commerce provider metadata
│       ├── shopify_basic.json
│       ├── foxy.json
│       └── snipcart.json
├── validation/                     # Validation tools
│   └── validate_metadata.py
└── examples/                       # Example metadata files
    └── example_provider.json
```

## Design Principles

### Separation of Concerns
- **Metadata**: Lightweight JSON files for discovery, capabilities, and characteristics
- **Implementation**: Full CDK stacks and provider logic in Python classes
- **Registry**: Dynamic loading system that connects metadata to implementations

### Performance Optimization
- Fast CLI operations using only JSON metadata
- Heavy AWS/CDK imports only when deployment is triggered
- Metadata can be cached globally (S3/CloudFront)

### Maintainability
- Single source of truth for provider capabilities
- Automated validation ensures metadata accuracy
- Version control for metadata changes

## Usage

### Discovery Operations (Fast)
```python
from registry.provider_registry import ProviderRegistry

registry = ProviderRegistry()

# List all CMS providers
cms_providers = registry.list_providers(category="cms")

# Get provider capabilities
tina_meta = registry.get_provider_metadata("tina")
print(tina_meta.features)  # ['visual_editing', 'git_based', ...]
```

### Implementation Operations (Full Load)
```python
# Only when actually deploying
provider_class = registry.get_provider_implementation("tina")
provider = provider_class(config)
provider.deploy()
```

### CLI Integration
```bash
# Fast metadata operations
blackwell providers list --category=cms
blackwell providers show tina --features

# Full implementation when needed
blackwell deploy --provider=tina --ssg=astro
```

## Metadata Schema

See `schema/provider_metadata_schema.json` for the complete JSON Schema definition.

### Key Fields
- `provider_id`: Unique identifier (snake_case)
- `category`: Provider type (cms, ecommerce, etc.)
- `features`: Capability list using controlled vocabulary
- `supported_ssg_engines`: Compatible SSG engines
- `integration_modes`: Direct and/or event-driven
- `implementation_class`: Python import path to CDK stack
- `provider_class`: Python import path to provider logic

### Example Structure
```json
{
  "provider_id": "tina",
  "provider_name": "TinaCMS",
  "category": "cms",
  "tier_name": "Visual CMS with Git Workflow",
  "features": ["visual_editing", "git_based", "real_time_preview"],
  "supported_ssg_engines": ["astro", "nextjs", "gatsby"],
  "integration_modes": ["direct", "event_driven"],
  "complexity_level": "intermediate",
  "implementation_class": "stacks.cms.tina_cms_tier_stack.TinaCMSTierStack"
}
```

## Validation

All metadata files are validated against the JSON schema:

```bash
# Validate all metadata
python registry/validation/validate_metadata.py

# Validate specific provider
python registry/validation/validate_metadata.py --provider=tina
```

### Automated Validation
- Schema compliance checking
- Implementation class verification
- Feature capability verification
- SSG engine compatibility verification

## Adding New Providers

1. **Create Implementation**: Add CDK stack and provider class in `platform-infrastructure`
2. **Create Metadata**: Add JSON file in appropriate `registry/providers/` subdirectory
3. **Validate**: Run validation tools to ensure accuracy
4. **Test**: Verify both metadata and implementation work correctly

## Version Control

- Metadata changes are tracked in git alongside code changes
- Schema evolution is versioned using semantic versioning
- Backward compatibility is maintained for metadata consumers

## Performance Characteristics

### Metadata Operations
- **Cold start**: <50ms for complete provider discovery
- **Memory usage**: <1MB for all provider metadata
- **Network**: Can be served from CDN for global access

### Implementation Loading
- **Lazy loading**: Only import provider classes when needed
- **Caching**: Implementation classes cached after first import
- **Resource usage**: Full AWS/CDK imports only during deployment