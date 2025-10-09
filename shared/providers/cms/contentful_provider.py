"""
Contentful CMS Provider

Enterprise-grade CMS provider for Contentful with advanced API integration, content management
workflows, and multi-environment support. This provider enables flexible SSG engine integration
while maintaining enterprise security and compliance features.

CONTENTFUL PROVIDER FEATURES:
- Enterprise API integration with GraphQL and REST endpoints
- Advanced content modeling and relationship management
- Multi-language and localization workflow support
- Team collaboration with roles and permissions
- Content versioning, scheduling, and publishing workflows
- Rich media management with asset optimization
- Preview API integration for draft content
- Webhook-driven content synchronization

SUPPORTED SSG ENGINES:
- Gatsby: Perfect GraphQL integration with advanced content sourcing
- Astro: Modern component architecture with Contentful API integration
- Next.js: Full React ecosystem with Contentful JavaScript SDK
- Nuxt: Vue ecosystem with comprehensive Contentful modules

ENTERPRISE BUSINESS MODEL:
- Target Market: Enterprise clients, large content teams, complex workflows
- Monthly Cost: $75-125/month (AWS + Contentful subscription)
- Setup Cost: $2,100-4,800 (enterprise complexity and customization)
- Value Proposition: Advanced workflows justify premium pricing

ARCHITECTURAL INTEGRATION:
- API-based content management with REST and GraphQL
- Webhook-driven real-time content synchronization
- Enterprise security with API key rotation and access controls
- Advanced monitoring and analytics for content performance
- Multi-environment content delivery (dev/staging/production)
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from pathlib import Path

from shared.ssg.ssg_engines import SSGEngine
from shared.providers.cms.base_cms_provider import BaseCMSProvider


class ContentfulEnvironment(str, Enum):
    """Contentful environment types for multi-stage workflows"""
    MASTER = "master"
    DEVELOPMENT = "development"
    STAGING = "staging"


class ContentfulAPIType(str, Enum):
    """Contentful API types for different content access patterns"""
    DELIVERY = "delivery"  # Published content
    PREVIEW = "preview"    # Draft and published content
    MANAGEMENT = "management"  # Content management operations


@dataclass
class ContentfulContentSettings:
    """Contentful-specific content management settings"""
    space_id: str
    environment: ContentfulEnvironment = field(default=ContentfulEnvironment.MASTER)
    enable_preview: bool = field(default=True)
    enable_webhooks: bool = field(default=True)
    content_locales: List[str] = field(default_factory=lambda: ["en-US"])
    asset_optimization: bool = field(default=True)

    # Enterprise workflow settings
    enable_workflows: bool = field(default=True)
    enable_versioning: bool = field(default=True)
    enable_scheduling: bool = field(default=True)

    # Team collaboration settings
    enable_roles: bool = field(default=True)
    max_editors: int = field(default=25)  # Contentful Team plan limit


@dataclass
class ContentfulBuildSettings:
    """Build configuration for different SSG engines with Contentful"""
    ssg_engine: SSGEngine
    build_command: str = field(default="")
    output_directory: str = field(default="dist")
    environment_variables: Dict[str, str] = field(default_factory=dict)
    contentful_plugins: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Set SSG-specific defaults for Contentful integration"""
        if not self.build_command:
            self.build_command = self._get_default_build_command()

        if not self.contentful_plugins:
            self.contentful_plugins = self._get_default_plugins()

    def _get_default_build_command(self) -> str:
        """Get default build command based on SSG engine"""
        commands = {
            SSGEngine.GATSBY: "gatsby build",
            SSGEngine.ASTRO: "npm run build",
            SSGEngine.NEXTJS: "npm run build && npm run export",
            SSGEngine.NUXT: "npm run generate"
        }
        return commands.get(self.ssg_engine, "npm run build")

    def _get_default_plugins(self) -> List[str]:
        """Get default Contentful plugins/packages for SSG engine"""
        plugins = {
            SSGEngine.GATSBY: ["gatsby-source-contentful"],
            SSGEngine.ASTRO: ["@astrojs/contentful"],
            SSGEngine.NEXTJS: ["contentful"],
            SSGEngine.NUXT: ["@nuxtjs/contentful"]
        }
        return plugins.get(self.ssg_engine, ["contentful"])


class ContentfulProvider(BaseCMSProvider):
    """
    Enterprise Contentful CMS provider with advanced API integration and workflow support.

    ARCHITECTURE:
    - API-based content management with GraphQL and REST
    - Multi-environment support (master/development/staging)
    - Enterprise security with API key management
    - Advanced content modeling and relationships
    - Real-time webhook synchronization
    - Rich media and asset optimization

    ENTERPRISE FEATURES:
    - Content workflows with approval processes
    - Team collaboration with granular permissions
    - Multi-language content and localization
    - Content versioning and change tracking
    - Scheduled publishing and content automation
    - Advanced analytics and performance monitoring

    FLEXIBLE SSG INTEGRATION:
    - Client chooses CMS tier (Contentful) for enterprise features
    - Client chooses SSG engine (Gatsby/Astro/Next.js/Nuxt) for technical preference
    - Same monthly cost serves different technical comfort levels
    - Enterprise features available regardless of SSG choice
    """

    # SSG engine compatibility and optimization matrix
    SSG_COMPATIBILITY = {
        SSGEngine.GATSBY: {
            "compatibility_score": 10,  # Perfect GraphQL integration
            "setup_complexity": "advanced",
            "build_performance": "good",
            "features": ["graphql", "image_optimization", "content_sourcing", "rich_text"],
            "recommended_for": ["enterprise_marketing", "content_heavy_sites", "developer_teams"],
            "contentful_advantages": [
                "Native GraphQL API integration",
                "Advanced image optimization pipeline",
                "Rich text rendering with gatsby-transformer-contentful-richtext"
            ]
        },
        SSGEngine.ASTRO: {
            "compatibility_score": 9,   # Excellent modern integration
            "setup_complexity": "intermediate",
            "build_performance": "excellent",
            "features": ["component_islands", "modern_architecture", "performance_optimization"],
            "recommended_for": ["modern_businesses", "performance_critical", "component_based"],
            "contentful_advantages": [
                "Component islands with Contentful data",
                "Excellent build performance with content caching",
                "Modern TypeScript integration patterns"
            ]
        },
        SSGEngine.NEXTJS: {
            "compatibility_score": 9,   # Excellent React ecosystem fit
            "setup_complexity": "advanced",
            "build_performance": "good",
            "features": ["react_ecosystem", "api_routes", "enterprise_scaling"],
            "recommended_for": ["react_teams", "enterprise_applications", "full_stack_needs"],
            "contentful_advantages": [
                "React ecosystem with Contentful JavaScript SDK",
                "API routes for advanced Contentful integrations",
                "Enterprise scaling with Contentful's CDN"
            ]
        },
        SSGEngine.NUXT: {
            "compatibility_score": 8,   # Good Vue ecosystem integration
            "setup_complexity": "advanced",
            "build_performance": "good",
            "features": ["vue_ecosystem", "ssr_support", "enterprise_features"],
            "recommended_for": ["vue_teams", "ssr_applications", "european_markets"],
            "contentful_advantages": [
                "Vue ecosystem with @nuxtjs/contentful module",
                "Server-side rendering with Contentful data",
                "Built-in localization for international content"
            ]
        }
    }

    def __init__(
        self,
        space_id: str,
        environment: str = "master",
        ssg_engine: Optional[SSGEngine] = None
    ):
        super().__init__()
        self.space_id = space_id
        self.environment = environment
        self.ssg_engine = ssg_engine

        # Initialize provider configuration
        self._setup_contentful_config()

    def _setup_contentful_config(self) -> None:
        """Initialize Contentful provider configuration"""
        self.content_settings = ContentfulContentSettings(
            space_id=self.space_id,
            environment=ContentfulEnvironment(self.environment)
        )

        if self.ssg_engine:
            self.build_settings = ContentfulBuildSettings(ssg_engine=self.ssg_engine)

    @property
    def provider_name(self) -> str:
        return "contentful"

    @property
    def provider_type(self) -> str:
        return "api_based"  # Contentful is API-first CMS

    @property
    def enterprise_features(self) -> List[str]:
        """List enterprise features available with Contentful"""
        return [
            "content_workflows",
            "team_collaboration",
            "multi_language_support",
            "content_versioning",
            "scheduled_publishing",
            "advanced_permissions",
            "content_analytics",
            "api_rate_limits_enterprise",
            "sla_guarantees",
            "dedicated_support"
        ]

    def get_supported_ssg_engines(self) -> List[SSGEngine]:
        """Get list of SSG engines supported by Contentful provider"""
        return [
            SSGEngine.GATSBY,
            SSGEngine.ASTRO,
            SSGEngine.NEXTJS,
            SSGEngine.NUXT
        ]

    def validate_ssg_compatibility(self, ssg_engine: SSGEngine) -> Dict[str, Any]:
        """Validate and get compatibility information for SSG engine"""
        if ssg_engine not in self.get_supported_ssg_engines():
            return {
                "compatible": False,
                "reason": f"SSG engine {ssg_engine.value} not supported by Contentful provider",
                "supported_engines": [engine.value for engine in self.get_supported_ssg_engines()]
            }

        compatibility = self.SSG_COMPATIBILITY[ssg_engine]
        return {
            "compatible": True,
            "compatibility_score": compatibility["compatibility_score"],
            "setup_complexity": compatibility["setup_complexity"],
            "build_performance": compatibility["build_performance"],
            "features": compatibility["features"],
            "recommended_for": compatibility["recommended_for"],
            "contentful_advantages": compatibility["contentful_advantages"]
        }

    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Contentful API endpoints for different access patterns"""
        base_url = "https://api.contentful.com"
        preview_url = "https://preview.contentful.com"
        management_url = "https://api.contentful.com"

        return {
            "delivery_api": f"{base_url}/spaces/{self.space_id}",
            "preview_api": f"{preview_url}/spaces/{self.space_id}",
            "management_api": f"{management_url}/spaces/{self.space_id}",
            "graphql_api": f"{base_url}/spaces/{self.space_id}/environments/{self.environment}",
            "images_api": "https://images.ctfassets.net"
        }

    def generate_environment_variables(self, ssg_engine: SSGEngine) -> Dict[str, str]:
        """Generate environment variables for SSG build process"""
        base_vars = {
            "CONTENTFUL_SPACE_ID": self.space_id,
            "CONTENTFUL_ENVIRONMENT": self.environment,
            "CONTENTFUL_HOST": "api.contentful.com"
        }

        # Add SSG-specific variables
        ssg_vars = {
            SSGEngine.GATSBY: {
                "CONTENTFUL_ACCESS_TOKEN": "${CONTENTFUL_DELIVERY_TOKEN}",
                "CONTENTFUL_PREVIEW_ACCESS_TOKEN": "${CONTENTFUL_PREVIEW_TOKEN}"
            },
            SSGEngine.ASTRO: {
                "CONTENTFUL_DELIVERY_TOKEN": "${CONTENTFUL_DELIVERY_TOKEN}",
                "CONTENTFUL_PREVIEW_TOKEN": "${CONTENTFUL_PREVIEW_TOKEN}"
            },
            SSGEngine.NEXTJS: {
                "CONTENTFUL_ACCESS_TOKEN": "${CONTENTFUL_DELIVERY_TOKEN}",
                "CONTENTFUL_PREVIEW_ACCESS_TOKEN": "${CONTENTFUL_PREVIEW_TOKEN}",
                "CONTENTFUL_MANAGEMENT_TOKEN": "${CONTENTFUL_MANAGEMENT_TOKEN}"
            },
            SSGEngine.NUXT: {
                "CTF_SPACE_ID": self.space_id,
                "CTF_CDA_ACCESS_TOKEN": "${CONTENTFUL_DELIVERY_TOKEN}",
                "CTF_ENVIRONMENT": self.environment
            }
        }

        base_vars.update(ssg_vars.get(ssg_engine, {}))
        return base_vars

    def get_build_dependencies(self, ssg_engine: SSGEngine) -> Dict[str, Any]:
        """Get required dependencies for SSG engine with Contentful"""
        dependencies = {
            SSGEngine.GATSBY: {
                "npm_packages": [
                    "gatsby-source-contentful",
                    "gatsby-transformer-contentful-richtext",
                    "@contentful/gatsby-transformer-contentful-richtext"
                ],
                "gatsby_plugins": [
                    {
                        "resolve": "gatsby-source-contentful",
                        "options": {
                            "spaceId": "${CONTENTFUL_SPACE_ID}",
                            "accessToken": "${CONTENTFUL_ACCESS_TOKEN}",
                            "environment": "${CONTENTFUL_ENVIRONMENT}",
                            "host": "${CONTENTFUL_HOST}"
                        }
                    }
                ]
            },
            SSGEngine.ASTRO: {
                "npm_packages": [
                    "@astrojs/contentful",
                    "contentful"
                ],
                "astro_integrations": ["@astrojs/contentful"]
            },
            SSGEngine.NEXTJS: {
                "npm_packages": [
                    "contentful",
                    "@contentful/rich-text-react-renderer",
                    "@contentful/rich-text-types"
                ]
            },
            SSGEngine.NUXT: {
                "npm_packages": [
                    "@nuxtjs/contentful",
                    "contentful"
                ],
                "nuxt_modules": ["@nuxtjs/contentful"],
                "contentful_config": {
                    "space": "${CTF_SPACE_ID}",
                    "accessToken": "${CTF_CDA_ACCESS_TOKEN}",
                    "environment": "${CTF_ENVIRONMENT}"
                }
            }
        }

        return dependencies.get(ssg_engine, {"npm_packages": ["contentful"]})

    def generate_build_configuration(self, ssg_engine: SSGEngine) -> Dict[str, Any]:
        """Generate build configuration for specific SSG engine"""
        base_config = {
            "provider": "contentful",
            "space_id": self.space_id,
            "environment": self.environment,
            "ssg_engine": ssg_engine.value
        }

        # SSG-specific configurations
        ssg_configs = {
            SSGEngine.GATSBY: {
                "gatsby_config": {
                    "plugins": self.get_build_dependencies(ssg_engine).get("gatsby_plugins", [])
                },
                "build_command": "gatsby build",
                "output_dir": "public"
            },
            SSGEngine.ASTRO: {
                "astro_config": {
                    "integrations": ["@astrojs/contentful"],
                    "contentful": {
                        "space": self.space_id,
                        "accessToken": "${CONTENTFUL_DELIVERY_TOKEN}",
                        "environment": self.environment
                    }
                },
                "build_command": "npm run build",
                "output_dir": "dist"
            },
            SSGEngine.NEXTJS: {
                "next_config": {
                    "env": {
                        "CONTENTFUL_SPACE_ID": self.space_id,
                        "CONTENTFUL_ACCESS_TOKEN": "${CONTENTFUL_ACCESS_TOKEN}",
                        "CONTENTFUL_ENVIRONMENT": self.environment
                    }
                },
                "build_command": "npm run build && npm run export",
                "output_dir": "out"
            },
            SSGEngine.NUXT: {
                "nuxt_config": {
                    "modules": ["@nuxtjs/contentful"],
                    "contentful": self.get_build_dependencies(ssg_engine).get("contentful_config", {})
                },
                "build_command": "npm run generate",
                "output_dir": "dist"
            }
        }

        base_config.update(ssg_configs.get(ssg_engine, {}))
        return base_config

    def get_webhook_configuration(self) -> Dict[str, Any]:
        """Get webhook configuration for Contentful content synchronization"""
        return {
            "provider": "contentful",
            "webhook_url": "{INTEGRATION_API_URL}/webhooks/contentful",
            "events": [
                "Entry.save",
                "Entry.publish",
                "Entry.unpublish",
                "Entry.archive",
                "Entry.delete",
                "Asset.save",
                "Asset.publish",
                "Asset.unpublish",
                "Asset.archive",
                "Asset.delete"
            ],
            "headers": {
                "X-Contentful-Topic": "{sys.type}.{sys.action}",
                "X-Contentful-Webhook-Name": "platform-infrastructure-sync"
            },
            "transforms": [
                {
                    "method": "POST",
                    "body": {
                        "space_id": "{sys.space.sys.id}",
                        "environment_id": "{sys.environment.sys.id}",
                        "entry_id": "{sys.id}",
                        "content_type": "{sys.contentType.sys.id}",
                        "action": "{sys.action}",
                        "data": "{fields}"
                    }
                }
            ]
        }

    def get_content_model_examples(self) -> Dict[str, Any]:
        """Get example content models for different business use cases"""
        return {
            "blog_article": {
                "name": "Blog Article",
                "description": "Standard blog post with rich content",
                "fields": [
                    {"id": "title", "name": "Title", "type": "Symbol", "required": True},
                    {"id": "slug", "name": "Slug", "type": "Symbol", "required": True, "unique": True},
                    {"id": "excerpt", "name": "Excerpt", "type": "Text"},
                    {"id": "content", "name": "Content", "type": "RichText", "required": True},
                    {"id": "featuredImage", "name": "Featured Image", "type": "Link", "linkType": "Asset"},
                    {"id": "author", "name": "Author", "type": "Link", "linkType": "Entry"},
                    {"id": "publishDate", "name": "Publish Date", "type": "Date", "required": True},
                    {"id": "tags", "name": "Tags", "type": "Array", "items": {"type": "Symbol"}}
                ]
            },
            "product_page": {
                "name": "Product Page",
                "description": "E-commerce product with rich content",
                "fields": [
                    {"id": "name", "name": "Product Name", "type": "Symbol", "required": True},
                    {"id": "slug", "name": "Slug", "type": "Symbol", "required": True, "unique": True},
                    {"id": "description", "name": "Description", "type": "RichText", "required": True},
                    {"id": "price", "name": "Price", "type": "Number", "required": True},
                    {"id": "images", "name": "Product Images", "type": "Array", "items": {"type": "Link", "linkType": "Asset"}},
                    {"id": "category", "name": "Category", "type": "Link", "linkType": "Entry"},
                    {"id": "specifications", "name": "Specifications", "type": "Object"},
                    {"id": "availability", "name": "Availability", "type": "Boolean", "defaultValue": {"en-US": True}}
                ]
            },
            "landing_page": {
                "name": "Landing Page",
                "description": "Marketing landing page with flexible sections",
                "fields": [
                    {"id": "title", "name": "Page Title", "type": "Symbol", "required": True},
                    {"id": "slug", "name": "Slug", "type": "Symbol", "required": True, "unique": True},
                    {"id": "metaDescription", "name": "Meta Description", "type": "Text"},
                    {"id": "heroSection", "name": "Hero Section", "type": "Link", "linkType": "Entry"},
                    {"id": "contentSections", "name": "Content Sections", "type": "Array", "items": {"type": "Link", "linkType": "Entry"}},
                    {"id": "ctaSection", "name": "Call-to-Action Section", "type": "Link", "linkType": "Entry"}
                ]
            }
        }

    def estimate_monthly_cost(self, client_requirements: Dict[str, Any]) -> Dict[str, float]:
        """Estimate monthly cost for Contentful CMS tier"""

        # Contentful subscription costs (enterprise tier)
        contentful_base = 300  # Contentful Team plan

        # Usage-based scaling
        api_calls_cost = client_requirements.get("api_calls_per_month", 100000) * 0.0001  # $0.0001 per API call over limit
        bandwidth_cost = client_requirements.get("bandwidth_gb", 100) * 0.10  # $0.10 per GB over limit

        # AWS integration costs
        aws_lambda = 5   # Webhook handling and content sync
        aws_dynamodb = 3 # Content caching
        aws_secrets = 1  # API key management

        # Enterprise features overhead
        enterprise_monitoring = 5
        enterprise_security = 5

        total_cost = (
            contentful_base +
            api_calls_cost +
            bandwidth_cost +
            aws_lambda +
            aws_dynamodb +
            aws_secrets +
            enterprise_monitoring +
            enterprise_security
        )

        return {
            "contentful_subscription": contentful_base,
            "api_usage": api_calls_cost,
            "bandwidth": bandwidth_cost,
            "aws_integration": aws_lambda + aws_dynamodb + aws_secrets,
            "enterprise_features": enterprise_monitoring + enterprise_security,
            "total": total_cost
        }

    def get_business_positioning(self) -> Dict[str, Any]:
        """Get business positioning information for Contentful CMS tier"""
        return {
            "tier": "enterprise",
            "target_market": [
                "large_content_teams",
                "enterprise_organizations",
                "complex_workflows",
                "multi_brand_companies",
                "international_businesses"
            ],
            "key_differentiators": [
                "Advanced content workflows with approval processes",
                "Team collaboration with granular permissions",
                "Multi-language content with localization workflows",
                "Enterprise security and compliance features",
                "Dedicated support and SLA guarantees",
                "Advanced analytics and content performance tracking"
            ],
            "ideal_client_profile": {
                "team_size": "10+ content creators",
                "content_volume": "500+ pieces per month",
                "technical_requirements": "API-first architecture",
                "budget_range": "$300-500+ per month",
                "compliance_needs": "Enterprise security and governance"
            },
            "competitive_advantages": [
                "Most mature headless CMS with proven enterprise scale",
                "Rich ecosystem of integrations and developer tools",
                "Flexible content modeling with powerful relationships",
                "GraphQL API with excellent performance characteristics",
                "Strong multi-language and localization capabilities"
            ],
            "roi_factors": [
                "Reduced content management overhead through workflows",
                "Improved content consistency across channels",
                "Faster time-to-market for content campaigns",
                "Better content performance through analytics",
                "Reduced development costs through flexible APIs"
            ]
        }

    @classmethod
    def get_client_suitability_score(
        cls,
        client_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate suitability score for Contentful CMS tier based on client requirements"""

        score = 0
        reasons = []

        # Enterprise features strongly favor Contentful
        if client_requirements.get("team_size", 1) >= 10:
            score += 30
            reasons.append("Large content team benefits from collaboration features")

        if client_requirements.get("content_workflows", False):
            score += 25
            reasons.append("Content approval workflows and governance")

        if client_requirements.get("multi_language", False):
            score += 20
            reasons.append("Advanced multi-language and localization support")

        if client_requirements.get("api_first", False):
            score += 20
            reasons.append("API-first architecture with GraphQL and REST")

        if client_requirements.get("enterprise_security", False):
            score += 15
            reasons.append("Enterprise security and compliance requirements")

        if client_requirements.get("content_analytics", False):
            score += 15
            reasons.append("Advanced content performance analytics")

        # Budget considerations
        budget = client_requirements.get("monthly_budget", 0)
        if budget >= 300:
            score += 20
            reasons.append("Budget supports enterprise CMS features")
        elif budget < 150:
            score -= 30
            reasons.append("Budget may be insufficient for enterprise CMS tier")

        # Technical complexity requirements
        if client_requirements.get("technical_complexity", "simple") == "enterprise":
            score += 15
            reasons.append("Enterprise technical requirements align with Contentful")

        # Penalties for over-engineering
        if client_requirements.get("simple_content", False) and client_requirements.get("team_size", 1) <= 3:
            score -= 25
            reasons.append("May be over-engineered for simple content needs")

        # Determine suitability level
        if score >= 80:
            suitability = "excellent"
        elif score >= 60:
            suitability = "good"
        elif score >= 40:
            suitability = "fair"
        else:
            suitability = "poor"

        return {
            "suitability_score": max(0, min(100, score)),
            "suitability": suitability,
            "reasons": reasons,
            "recommended_ssg_engines": ["gatsby", "astro", "nextjs", "nuxt"],
            "monthly_cost_estimate": "$375-500+",
            "setup_complexity": "high",
            "ongoing_complexity": "medium"
        }