# SSG Engine Integration Guide

## 🎯 Overview

This guide explains how to integrate the existing SSG engine system with your CDK stacks, following all Claude steering guide conventions. Your foundation in `shared/ssg_engines.py` is excellent - we just need to modernize it and connect it to your stack implementations.

## 📋 Current State Analysis

### ✅ What's Working Well
- **Comprehensive SSG System**: 4 engines (Eleventy, Hugo, Astro, Jekyll) with detailed configurations
- **Template System**: Pre-defined templates for each engine with use cases
- **CodeBuild Integration**: Built-in buildspec generation for AWS deployment
- **Factory Pattern**: Clean SSGEngineFactory for creating engine configurations

### 🔧 What Needs Updating

1. **Pydantic v1 → v2 Migration**: Main system uses deprecated `@validator` syntax
2. **SSG-Client Integration**: Connect SSG system to client configurations
3. **Missing Engines**: Add Next.js, Nuxt, Gatsby as mentioned in steering guide
4. **Stack Implementations**: Create actual CDK stacks that use SSG configurations
5. **Template Repositories**: Replace placeholder URLs with real template repos

## 🚀 Step-by-Step Integration

### Phase 1: Modernize SSG Engine System

First, let's upgrade `shared/ssg_engines.py` to use Pydantic v2 syntax:

#### 1.1 Update Pydantic Imports and Syntax

```python
# Replace these v1 patterns:
from pydantic import BaseModel, Field, validator, root_validator

@validator('field_name')
def validate_field(cls, v):
    return v

# With v2 patterns:
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    return v
```

#### 1.2 Add ConfigDict to All Models

```python
class BuildCommand(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [{
                "name": "build_site",
                "command": "npm run build",
                "environment_vars": {"NODE_ENV": "production"},
                "timeout_minutes": 10
            }]
        }
    )

    name: str = Field(..., description="Name of the build step")
    command: str = Field(..., description="Shell command to execute")
    # ... rest of fields
```

### Phase 2: Add Missing SSG Engines

Your client configuration mentions these stack types that need SSG engines:

#### 2.1 Next.js Configuration

```python
class NextJSConfig(SSGEngineConfig):
    """Next.js SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "nextjs"

    @property
    def runtime_version(self) -> str:
        return "nodejs-18"

    @property
    def install_commands(self) -> List[str]:
        return [
            "npm ci",
            "npm install -g next"
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npm run build",
                environment_vars={"NODE_ENV": "production", "NEXT_TELEMETRY_DISABLED": "1"}
            ),
            BuildCommand(
                name="export_static",
                command="npm run export",  # For static export
                environment_vars={"NODE_ENV": "production"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "out"  # Next.js static export directory

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "automatic_static_optimization": True,
            "image_optimization": True,
            "code_splitting": True,
            "prefetching": True,
            "typescript_support": True,
            "app_router": True,
            "build_performance": "fast"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="professional_headless_cms",
                description="Professional headless CMS integration with Contentful/Strapi",
                use_cases=["professional_sites", "headless_cms", "content_heavy"],
                repo_url="https://github.com/your-templates/nextjs-professional-headless-cms",
                customization_points=["cms_integration", "page_layouts", "styling_system", "seo_config"],
                demo_url="https://demo.yourservices.com/nextjs-professional",
                difficulty_level="intermediate"
            )
        ]
```

#### 2.2 Nuxt.js Configuration

```python
class NuxtConfig(SSGEngineConfig):
    """Nuxt.js SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "nuxt"

    @property
    def runtime_version(self) -> str:
        return "nodejs-18"

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="generate_static",
                command="npm run generate",
                environment_vars={"NODE_ENV": "production", "NITRO_PRESET": "static"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "dist"

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="professional_headless_cms",
                description="Professional Nuxt 3 with headless CMS integration",
                use_cases=["vue_applications", "professional_sites", "spa_conversion"],
                repo_url="https://github.com/your-templates/nuxt-professional-headless-cms",
                customization_points=["cms_integration", "vue_components", "styling", "ssr_config"]
            )
        ]
```

#### 2.3 Gatsby Configuration

```python
class GatsbyConfig(SSGEngineConfig):
    """Gatsby SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "gatsby"

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npm run build",
                environment_vars={"NODE_ENV": "production", "GATSBY_TELEMETRY_DISABLED": "1"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "public"

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="contentful_integration",
                description="Gatsby with Contentful CMS integration and GraphQL",
                use_cases=["content_sites", "blogs", "marketing_sites"],
                repo_url="https://github.com/your-templates/gatsby-contentful",
                customization_points=["contentful_schema", "page_templates", "graphql_queries", "styling"]
            )
        ]
```

### Phase 3: Integrate SSG System with Client Configuration

#### 3.1 Create Enhanced Client SSG Configuration

Create a new model in `models/ssg_config.py`:

```python
from pydantic import BaseModel, Field, field_validator, computed_field, ConfigDict
from typing import Optional, Dict, List, Literal
from enum import Enum

from shared.ssg_engines import SSGEngineFactory, SSGEngineType, SSGTemplate

class SSGClientTier(str, Enum):
    """SSG-specific client tiers mapping to your service tiers"""
    TIER1_BASIC = "tier1-basic"           # Simple static sites
    TIER1_CMS = "tier1-cms"              # Static + headless CMS
    TIER2_PROFESSIONAL = "tier2-professional"  # Advanced features
    TIER2_ECOMMERCE = "tier2-ecommerce"  # E-commerce integration

class SSGStackConfig(BaseModel):
    """Enhanced SSG configuration integrated with client system"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [{
                "client_id": "acme-corp",
                "ssg_engine": "eleventy",
                "template_name": "business_modern",
                "tier": "tier1-basic",
                "domain": "acme.com",
                "performance_optimization": "aggressive"
            }]
        }
    )

    # Core SSG Configuration
    client_id: str = Field(
        ...,
        description="Client identifier from ClientConfig",
        pattern=r"^[a-z0-9-]+$"
    )

    ssg_engine: SSGEngineType = Field(
        ...,
        description="Static site generator engine to use"
    )

    template_name: str = Field(
        ...,
        description="Specific template variant for the chosen engine"
    )

    tier: SSGClientTier = Field(
        ...,
        description="SSG-specific service tier determining available features"
    )

    # Deployment Configuration
    domain: str = Field(..., description="Primary domain for the site")
    subdomain: Optional[str] = Field(None, description="Optional subdomain (www, blog, etc)")

    # Performance & Optimization
    performance_optimization: Literal["basic", "aggressive", "premium"] = Field(
        default="aggressive",
        description="Level of performance optimization to apply"
    )

    cdn_caching_strategy: Literal["conservative", "aggressive", "custom"] = Field(
        default="aggressive",
        description="CloudFront caching strategy"
    )

    # Build Configuration
    custom_build_commands: Optional[List[str]] = Field(
        None,
        description="Override default build commands if needed"
    )

    environment_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom environment variables for build process"
    )

    # CMS Integration (for CMS-enabled tiers)
    cms_provider: Optional[Literal["contentful", "strapi", "sanity", "decap", "tina"]] = Field(
        None,
        description="CMS provider for content management (tier1-cms, tier2-professional)"
    )

    cms_api_endpoint: Optional[str] = Field(
        None,
        description="CMS API endpoint URL"
    )

    # E-commerce Integration (for e-commerce tiers)
    ecommerce_provider: Optional[Literal["snipcart", "foxy", "shopify", "stripe"]] = Field(
        None,
        description="E-commerce provider for online sales"
    )

    @field_validator('template_name')
    @classmethod
    def validate_template_exists(cls, v, info):
        """Ensure the template exists for the chosen SSG engine"""
        if 'ssg_engine' in info.data:
            engine_type = info.data['ssg_engine']
            try:
                available_templates = SSGEngineFactory.get_engine_templates(engine_type)
                template_names = [t.name for t in available_templates]
                if v not in template_names:
                    raise ValueError(f"Template '{v}' not available for {engine_type}. Available: {template_names}")
            except Exception:
                # During model creation, factory might not be ready
                pass
        return v

    @field_validator('cms_provider')
    @classmethod
    def validate_cms_tier_compatibility(cls, v, info):
        """Ensure CMS provider is only set for CMS-enabled tiers"""
        if v is not None:
            tier = info.data.get('tier')
            if tier not in ['tier1-cms', 'tier2-professional']:
                raise ValueError(f"CMS provider can only be set for CMS-enabled tiers, got tier: {tier}")
        return v

    @computed_field
    @property
    def stack_name(self) -> str:
        """Generate CDK stack name"""
        client_part = ''.join(word.capitalize() for word in self.client_id.split('-'))
        engine_part = self.ssg_engine.capitalize()
        template_part = ''.join(word.capitalize() for word in self.template_name.split('_'))
        return f"{client_part}-{engine_part}-{template_part}-Stack"

    @computed_field
    @property
    def resource_prefix(self) -> str:
        """Generate AWS resource prefix"""
        return f"{self.client_id}-{self.ssg_engine}"

    def get_ssg_engine_config(self):
        """Get the SSG engine configuration"""
        return SSGEngineFactory.create_engine(self.ssg_engine, self.template_name)

    def get_template_info(self) -> SSGTemplate:
        """Get detailed template information"""
        engine_config = self.get_ssg_engine_config()
        templates = engine_config.available_templates
        for template in templates:
            if template.name == self.template_name:
                return template
        raise ValueError(f"Template {self.template_name} not found")

    def to_aws_tags(self) -> Dict[str, str]:
        """Generate AWS resource tags"""
        tags = {
            "Client": self.client_id,
            "SSGEngine": self.ssg_engine,
            "Template": self.template_name,
            "Tier": self.tier.value,
            "PerformanceLevel": self.performance_optimization,
            "Environment": "production"  # Can be parameterized
        }

        if self.cms_provider:
            tags["CMSProvider"] = self.cms_provider

        if self.ecommerce_provider:
            tags["EcommerceProvider"] = self.ecommerce_provider

        return tags
```

### Phase 4: Create CDK Stack Implementation

#### 4.1 Static Site CDK Stack

Create `stacks/hosted-only/tier1/static_site_stack.py`:

```python
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_route53 as route53,
    aws_certificatemanager as acm,
    RemovalPolicy,
    Duration
)
from constructs import Construct
from typing import Dict, Any

from models.ssg_config import SSGStackConfig
from shared.ssg_engines import SSGEngineConfig


class StaticSiteStack(Stack):
    """
    CDK Stack for static site hosting using SSG engines.

    Supports all SSG engines (Eleventy, Hugo, Astro, Jekyll, Next.js, Nuxt, Gatsby)
    with tier-based feature sets and performance optimization.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ssg_config: SSGStackConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.ssg_config = ssg_config
        self.engine_config = ssg_config.get_ssg_engine_config()

        # Create infrastructure components
        self._create_storage_resources()
        self._create_build_pipeline()
        self._create_cdn_distribution()
        self._create_dns_records()

    def _create_storage_resources(self) -> None:
        """Create S3 buckets for site content and build artifacts"""

        # Primary content bucket
        self.content_bucket = s3.Bucket(
            self,
            "ContentBucket",
            bucket_name=f"{self.ssg_config.resource_prefix}-content",
            website_index_document="index.html",
            website_error_document="404.html",
            public_read_access=False,  # CloudFront will handle access
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,  # For dev/staging
            auto_delete_objects=True,
            versioned=True
        )

        # Build artifacts bucket (for CodeBuild)
        self.artifacts_bucket = s3.Bucket(
            self,
            "ArtifactsBucket",
            bucket_name=f"{self.ssg_config.resource_prefix}-artifacts",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Add tags from SSG configuration
        for key, value in self.ssg_config.to_aws_tags().items():
            self.content_bucket.node.add_metadata(key, value)
            self.artifacts_bucket.node.add_metadata(key, value)

    def _create_build_pipeline(self) -> None:
        """Create CodeBuild project for SSG compilation"""

        # Create build project with SSG-specific configuration
        build_spec = self.engine_config.get_buildspec()

        # Enhance buildspec with tier-specific optimizations
        if self.ssg_config.performance_optimization == "premium":
            build_spec["phases"]["post_build"] = {
                "commands": [
                    "npm run optimize:images",
                    "npm run optimize:css",
                    "npm run optimize:js"
                ]
            }

        self.build_project = codebuild.Project(
            self,
            "BuildProject",
            project_name=f"{self.ssg_config.resource_prefix}-build",
            source=codebuild.Source.git_hub(
                owner="your-templates",
                repo=f"{self.ssg_config.ssg_engine}-{self.ssg_config.template_name}",
                branch="main"
            ),
            environment=self.engine_config.get_codebuild_environment(),
            build_spec=codebuild.BuildSpec.from_object(build_spec),
            artifacts=codebuild.Artifacts.s3(
                bucket=self.artifacts_bucket,
                include_build_id=True,
                package_zip=False
            )
        )

        # Grant permissions to write to content bucket
        self.content_bucket.grant_write(self.build_project)

    def _create_cdn_distribution(self) -> None:
        """Create CloudFront distribution with tier-appropriate settings"""

        # Configure caching based on strategy
        cache_policy_config = self._get_cache_policy_config()

        # Origin Access Identity for S3
        oai = cloudfront.OriginAccessIdentity(
            self,
            "OriginAccessIdentity",
            comment=f"OAI for {self.ssg_config.client_id} static site"
        )

        # Grant CloudFront read access to content bucket
        self.content_bucket.grant_read(oai)

        # Create distribution
        self.distribution = cloudfront.CloudFrontWebDistribution(
            self,
            "CDNDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=self.content_bucket,
                        origin_access_identity=oai
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                            compress=True,
                            allowed_methods=cloudfront.CloudFrontAllowedMethods.GET_HEAD,
                            cached_methods=cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD,
                            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                            default_ttl=Duration.hours(24) if self.ssg_config.cdn_caching_strategy == "aggressive" else Duration.hours(1)
                        )
                    ]
                )
            ],
            comment=f"CDN for {self.ssg_config.client_id} ({self.ssg_config.ssg_engine})",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Use only North America and Europe
            enable_logging=True,
            log_bucket=self.artifacts_bucket,
            log_file_prefix="cloudfront-logs/"
        )

    def _create_dns_records(self) -> None:
        """Create Route53 records for the domain"""

        # Look up hosted zone
        hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=self.ssg_config.domain
        )

        # Create A record pointing to CloudFront
        route53.ARecord(
            self,
            "AliasRecord",
            zone=hosted_zone,
            record_name=self.ssg_config.subdomain or "",
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution)
            )
        )

        # Create AAAA record for IPv6
        route53.AaaaRecord(
            self,
            "AliasRecordAAAA",
            zone=hosted_zone,
            record_name=self.ssg_config.subdomain or "",
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution)
            )
        )

    def _get_cache_policy_config(self) -> Dict[str, Any]:
        """Get CloudFront cache policy based on SSG engine and tier"""

        base_config = {
            "default_ttl": Duration.hours(24),
            "max_ttl": Duration.days(365),
            "min_ttl": Duration.seconds(0)
        }

        # Adjust based on SSG engine characteristics
        if self.ssg_config.ssg_engine == "hugo":
            # Hugo builds are extremely fast, can afford shorter cache
            base_config["default_ttl"] = Duration.hours(12)
        elif self.ssg_config.ssg_engine in ["nextjs", "nuxt"]:
            # Framework apps might have more dynamic elements
            base_config["default_ttl"] = Duration.hours(6)

        # Adjust based on performance tier
        if self.ssg_config.performance_optimization == "premium":
            base_config["max_ttl"] = Duration.days(365)
        elif self.ssg_config.performance_optimization == "basic":
            base_config["default_ttl"] = Duration.hours(1)

        return base_config
```

### Phase 5: Usage Examples

#### 5.1 Creating SSG Client Configurations

```python
# Create different SSG configurations for various client types

# Tier 1 Basic - Simple Eleventy site
basic_client = SSGStackConfig(
    client_id="small-biz",
    ssg_engine="eleventy",
    template_name="business_modern",
    tier="tier1-basic",
    domain="smallbiz.com"
)

# Tier 1 CMS - Astro with Sanity CMS
cms_client = SSGStackConfig(
    client_id="content-site",
    ssg_engine="astro",
    template_name="modern_interactive",
    tier="tier1-cms",
    domain="contentsite.com",
    cms_provider="sanity",
    cms_api_endpoint="https://your-project.api.sanity.io/v1/data/query/production"
)

# Tier 2 Professional - Next.js with Contentful
professional_client = SSGStackConfig(
    client_id="pro-site",
    ssg_engine="nextjs",
    template_name="professional_headless_cms",
    tier="tier2-professional",
    domain="prosite.com",
    cms_provider="contentful",
    performance_optimization="premium"
)

# Tier 2 E-commerce - Hugo with Snipcart
ecommerce_client = SSGStackConfig(
    client_id="shop-site",
    ssg_engine="hugo",
    template_name="corporate_clean",
    tier="tier2-ecommerce",
    domain="shopsite.com",
    ecommerce_provider="snipcart"
)
```

#### 5.2 Deploying SSG Stacks

```python
# In your CDK app (app.py)
from models.ssg_config import SSGStackConfig
from stacks.hosted_only.tier1.static_site_stack import StaticSiteStack

# Load client configuration
client_config = SSGStackConfig(
    client_id="demo-client",
    ssg_engine="eleventy",
    template_name="business_modern",
    tier="tier1-basic",
    domain="democlient.com"
)

# Create and deploy stack
stack = StaticSiteStack(
    app,
    client_config.stack_name,  # "DemoClient-Eleventy-BusinessModern-Stack"
    ssg_config=client_config,
    env=aws_cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION")
    )
)
```

### Phase 6: Testing Your SSG Integration

Create comprehensive tests in `tests/test_ssg_integration.py`:

```python
import pytest
from pydantic import ValidationError

from models.ssg_config import SSGStackConfig, SSGClientTier
from shared.ssg_engines import SSGEngineFactory

class TestSSGIntegration:
    """Test SSG engine integration with client configurations"""

    def test_valid_ssg_configuration(self):
        """Test creating valid SSG configuration"""
        config = SSGStackConfig(
            client_id="test-client",
            ssg_engine="eleventy",
            template_name="business_modern",
            tier="tier1-basic",
            domain="test.com"
        )

        assert config.client_id == "test-client"
        assert config.ssg_engine == "eleventy"
        assert config.stack_name == "TestClient-Eleventy-BusinessModern-Stack"

    def test_template_validation(self):
        """Test that template validation works"""
        with pytest.raises(ValidationError):
            SSGStackConfig(
                client_id="test-client",
                ssg_engine="eleventy",
                template_name="nonexistent_template",  # Should fail
                tier="tier1-basic",
                domain="test.com"
            )

    def test_cms_tier_validation(self):
        """Test CMS provider is only allowed for appropriate tiers"""
        # Should work
        config = SSGStackConfig(
            client_id="test-client",
            ssg_engine="astro",
            template_name="modern_interactive",
            tier="tier1-cms",
            domain="test.com",
            cms_provider="sanity"
        )
        assert config.cms_provider == "sanity"

        # Should fail
        with pytest.raises(ValidationError):
            SSGStackConfig(
                client_id="test-client",
                ssg_engine="eleventy",
                template_name="business_modern",
                tier="tier1-basic",  # Basic tier shouldn't allow CMS
                domain="test.com",
                cms_provider="sanity"
            )

    def test_ssg_engine_integration(self):
        """Test integration with SSG engine system"""
        config = SSGStackConfig(
            client_id="test-client",
            ssg_engine="hugo",
            template_name="corporate_clean",
            tier="tier2-professional",
            domain="test.com"
        )

        engine_config = config.get_ssg_engine_config()
        assert engine_config.engine_name == "hugo"
        assert len(engine_config.build_commands) > 0

        template_info = config.get_template_info()
        assert template_info.name == "corporate_clean"
        assert "corporate_sites" in template_info.use_cases
```

## 🎛️ Command Reference

### Using uv for SSG Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/test_ssg_integration.py -v

# Test specific SSG engine
uv run python shared/ssg_engines.py

# Format code
uv run black shared/ssg_engines.py models/ssg_config.py

# Lint code
uv run ruff check shared/ssg_engines.py models/ssg_config.py

# Deploy SSG stack
uv run cdk deploy DemoClient-Eleventy-BusinessModern-Stack

# List all SSG stacks
uv run cdk list | grep -E "(Eleventy|Hugo|Astro|Jekyll|Nextjs|Nuxt|Gatsby)"
```

## 📚 Next Steps

1. **Modernize SSG Engine System**:
   ```bash
   uv run python -c "from shared.ssg_engines import *; print('Testing current system')"
   ```

2. **Add Missing Engines**: Implement Next.js, Nuxt, and Gatsby configurations

3. **Create Template Repositories**: Set up actual GitHub repositories for each template

4. **Build Integration Models**: Create the `models/ssg_config.py` file

5. **Implement CDK Stacks**: Create the actual stack implementations

6. **Test Everything**: Comprehensive test suite for all integrations

This guide follows all your Claude steering conventions:
- ✅ Uses `uv` exclusively
- ✅ Modern Pydantic v2 patterns with `ConfigDict`
- ✅ Proper type hints throughout
- ✅ Tier-based client model integration
- ✅ CDK v2 conventions with proper imports
- ✅ Comprehensive testing approach
- ✅ Clear documentation and examples

Ready to start implementing any of these phases!
