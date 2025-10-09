"""
Shopify Basic E-commerce Provider

Standard Shopify store integration with static site generation for enhanced performance,
SEO, and cost optimization. This provider enables flexible SSG engine integration while
maintaining Shopify's proven e-commerce backend capabilities.

SHOPIFY BASIC PROVIDER FEATURES:
- Standard Shopify plan integration with Storefront API
- Product catalog synchronization with static site generation
- Custom frontend with high-performance static delivery
- Shopping cart integration with Shopify's hosted checkout
- Real-time inventory synchronization via webhooks
- Payment processing through Shopify Payments and gateways
- Order management through Shopify Admin dashboard

SUPPORTED SSG ENGINES:
- Eleventy: Simple, fast builds with excellent Shopify integration
- Astro: Modern component architecture with optimal performance
- Next.js: React ecosystem with Shopify JavaScript SDK
- Nuxt: Vue ecosystem with comprehensive e-commerce modules

BUSINESS MODEL:
- Target Market: Small-medium e-commerce businesses, performance-focused brands
- Monthly Cost: $75-125/month (Shopify Basic + AWS hosting + integration)
- Setup Cost: $1,600-3,200 (custom frontend + Shopify configuration)
- Value Proposition: Enterprise performance at small business prices

ARCHITECTURAL INTEGRATION:
- Shopify Storefront API for product data and customer management
- Webhook-driven real-time synchronization with static site rebuilds
- AWS-hosted frontend with CDN optimization and SSL
- Shopify-hosted checkout for PCI compliance and security
- Automated build triggers on product/inventory changes
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from pathlib import Path

from shared.ssg.ssg_engines import SSGEngine
from shared.providers.ecommerce.base_ecommerce_provider import BaseEcommerceProvider


class ShopifyPlan(str, Enum):
    """Shopify plan types for different business needs"""
    BASIC = "basic"
    SHOPIFY = "shopify"  # Standard plan
    ADVANCED = "advanced"


class ShopifyAPIAccess(str, Enum):
    """Shopify API access levels"""
    STOREFRONT = "storefront"  # Public product data
    ADMIN = "admin"           # Store management
    PLUS = "plus"            # Advanced Plus features


@dataclass
class ShopifyBasicSettings:
    """Shopify Basic-specific e-commerce settings"""
    store_domain: str  # mystore.myshopify.com
    shopify_plan: ShopifyPlan = field(default=ShopifyPlan.BASIC)
    enable_storefront_api: bool = field(default=True)
    enable_webhooks: bool = field(default=True)
    enable_cart_api: bool = field(default=True)

    # Product and inventory settings
    sync_inventory: bool = field(default=True)
    sync_collections: bool = field(default=True)
    sync_product_variants: bool = field(default=True)

    # Performance settings
    enable_product_caching: bool = field(default=True)
    cache_duration_hours: int = field(default=24)


@dataclass
class ShopifyBuildSettings:
    """Build configuration for different SSG engines with Shopify Basic"""
    ssg_engine: SSGEngine
    build_command: str = field(default="")
    output_directory: str = field(default="dist")
    environment_variables: Dict[str, str] = field(default_factory=dict)
    shopify_packages: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Set SSG-specific defaults for Shopify Basic integration"""
        if not self.build_command:
            self.build_command = self._get_default_build_command()

        if not self.shopify_packages:
            self.shopify_packages = self._get_default_packages()

    def _get_default_build_command(self) -> str:
        """Get default build command based on SSG engine"""
        commands = {
            SSGEngine.ELEVENTY: "npx @11ty/eleventy",
            SSGEngine.ASTRO: "npm run build",
            SSGEngine.NEXTJS: "npm run build && npm run export",
            SSGEngine.NUXT: "npm run generate"
        }
        return commands.get(self.ssg_engine, "npm run build")

    def _get_default_packages(self) -> List[str]:
        """Get default Shopify packages for SSG engine"""
        packages = {
            SSGEngine.ELEVENTY: ["@shopify/storefront-api-client"],
            SSGEngine.ASTRO: ["@shopify/storefront-api-client", "@astrojs/node"],
            SSGEngine.NEXTJS: ["@shopify/storefront-api-client", "@shopify/react-hooks"],
            SSGEngine.NUXT: ["@shopify/storefront-api-client", "@nuxtjs/axios"]
        }
        return packages.get(self.ssg_engine, ["@shopify/storefront-api-client"])


class ShopifyBasicProvider(BaseEcommerceProvider):
    """
    Shopify Basic e-commerce provider with static site integration and performance optimization.

    ARCHITECTURE:
    - Shopify backend handles all e-commerce logic (cart, checkout, payments, orders)
    - Custom static frontend provides superior performance and SEO
    - Real-time synchronization between Shopify data and static site
    - AWS hosting for frontend with CDN optimization and global delivery
    - Shopify webhooks trigger automatic site rebuilds on data changes

    PERFORMANCE BENEFITS:
    - Static site delivery: 0.8-1.5s page loads vs 3-6s typical Shopify themes
    - CDN optimization: Global content delivery and edge caching
    - SEO excellence: Static HTML with perfect search engine optimization
    - Mobile performance: Optimized responsive design and fast loading

    FLEXIBLE SSG INTEGRATION:
    - Client chooses e-commerce tier (Shopify Basic) for proven platform
    - Client chooses SSG engine (Eleventy/Astro/Next.js/Nuxt) for technical preference
    - Same monthly cost serves different technical comfort levels
    - Shopify handles all complex e-commerce logic while frontend optimized for performance

    BUSINESS VALUE:
    - 80-90% cost reduction vs traditional Shopify agencies
    - Enterprise performance at small business prices
    - Automated maintenance and updates
    - Proven e-commerce platform with custom presentation layer
    """

    # SSG engine compatibility and optimization matrix for Shopify Basic
    SSG_COMPATIBILITY = {
        SSGEngine.ELEVENTY: {
            "compatibility_score": 9,   # Excellent for simple, fast builds
            "setup_complexity": "simple",
            "build_performance": "excellent",
            "features": ["fast_builds", "simple_templating", "shopify_data_integration"],
            "recommended_for": ["small_stores", "budget_conscious", "simple_product_catalogs"],
            "shopify_advantages": [
                "Lightning-fast builds with Shopify product data",
                "Simple templating with Nunjucks for product pages",
                "Minimal complexity for straightforward e-commerce sites"
            ]
        },
        SSGEngine.ASTRO: {
            "compatibility_score": 10,  # Perfect for modern performance
            "setup_complexity": "intermediate",
            "build_performance": "excellent",
            "features": ["component_islands", "performance_optimization", "modern_architecture"],
            "recommended_for": ["performance_critical", "modern_brands", "component_based_design"],
            "shopify_advantages": [
                "Component islands with Shopify product data",
                "Optimal performance with partial hydration",
                "Modern architecture with excellent Shopify API integration"
            ]
        },
        SSGEngine.NEXTJS: {
            "compatibility_score": 9,   # Excellent React ecosystem integration
            "setup_complexity": "advanced",
            "build_performance": "good",
            "features": ["react_ecosystem", "api_routes", "shopify_sdk"],
            "recommended_for": ["react_teams", "complex_interactions", "custom_features"],
            "shopify_advantages": [
                "React ecosystem with Shopify React hooks",
                "API routes for advanced Shopify integrations",
                "Rich ecosystem of React e-commerce components"
            ]
        },
        SSGEngine.NUXT: {
            "compatibility_score": 8,   # Good Vue ecosystem integration
            "setup_complexity": "advanced",
            "build_performance": "good",
            "features": ["vue_ecosystem", "ssr_support", "shopify_modules"],
            "recommended_for": ["vue_teams", "ssr_applications", "european_markets"],
            "shopify_advantages": [
                "Vue ecosystem with Shopify integration modules",
                "Server-side rendering for better SEO",
                "Strong European developer community and support"
            ]
        }
    }

    def __init__(
        self,
        store_domain: str,
        shopify_plan: str = "basic",
        ssg_engine: Optional[SSGEngine] = None
    ):
        super().__init__()
        self.store_domain = store_domain
        self.shopify_plan = ShopifyPlan(shopify_plan)
        self.ssg_engine = ssg_engine

        # Initialize provider configuration
        self._setup_shopify_config()

    def _setup_shopify_config(self) -> None:
        """Initialize Shopify Basic provider configuration"""
        self.ecommerce_settings = ShopifyBasicSettings(
            store_domain=self.store_domain,
            shopify_plan=self.shopify_plan
        )

        if self.ssg_engine:
            self.build_settings = ShopifyBuildSettings(ssg_engine=self.ssg_engine)

    @property
    def provider_name(self) -> str:
        return "shopify_basic"

    @property
    def provider_type(self) -> str:
        return "hosted_platform"  # Shopify hosts the e-commerce backend

    @property
    def tier_features(self) -> List[str]:
        """List features available with Shopify Basic tier"""
        return [
            "product_catalog_management",
            "inventory_tracking",
            "shopping_cart_api",
            "secure_checkout",
            "payment_processing",
            "order_management",
            "customer_accounts",
            "basic_analytics",
            "mobile_optimization",
            "ssl_security",
            "storefront_api",
            "webhook_integration",
            "app_ecosystem"
        ]

    def get_supported_ssg_engines(self) -> List[SSGEngine]:
        """Get list of SSG engines supported by Shopify Basic provider"""
        return [
            SSGEngine.ELEVENTY,
            SSGEngine.ASTRO,
            SSGEngine.NEXTJS,
            SSGEngine.NUXT
        ]

    def validate_ssg_compatibility(self, ssg_engine: SSGEngine) -> Dict[str, Any]:
        """Validate and get compatibility information for SSG engine"""
        if ssg_engine not in self.get_supported_ssg_engines():
            return {
                "compatible": False,
                "reason": f"SSG engine {ssg_engine.value} not supported by Shopify Basic provider",
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
            "shopify_advantages": compatibility["shopify_advantages"]
        }

    def get_api_endpoints(self) -> Dict[str, str]:
        """Get Shopify API endpoints for different access patterns"""
        store_domain = self.store_domain.replace('.myshopify.com', '')

        return {
            "storefront_api": f"https://{store_domain}.myshopify.com/api/2023-10/graphql.json",
            "admin_api": f"https://{store_domain}.myshopify.com/admin/api/2023-10",
            "checkout_url": f"https://{store_domain}.myshopify.com/cart",
            "webhooks_endpoint": f"https://{store_domain}.myshopify.com/admin/api/2023-10/webhooks.json",
            "products_api": f"https://{store_domain}.myshopify.com/admin/api/2023-10/products.json"
        }

    def generate_environment_variables(self, ssg_engine: SSGEngine) -> Dict[str, str]:
        """Generate environment variables for SSG build process"""
        base_vars = {
            "SHOPIFY_STORE_DOMAIN": self.store_domain,
            "SHOPIFY_STOREFRONT_ACCESS_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}",
            "SHOPIFY_API_VERSION": "2023-10"
        }

        # Add SSG-specific variables
        ssg_vars = {
            SSGEngine.ELEVENTY: {
                "SHOPIFY_API_ENDPOINT": f"https://{self.store_domain}/api/2023-10/graphql.json"
            },
            SSGEngine.ASTRO: {
                "PUBLIC_SHOPIFY_STORE_DOMAIN": self.store_domain,
                "PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}"
            },
            SSGEngine.NEXTJS: {
                "NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN": self.store_domain,
                "NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}",
                "SHOPIFY_ADMIN_ACCESS_TOKEN": "${SHOPIFY_ADMIN_TOKEN}"
            },
            SSGEngine.NUXT: {
                "NUXT_PUBLIC_SHOPIFY_STORE_DOMAIN": self.store_domain,
                "NUXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}"
            }
        }

        base_vars.update(ssg_vars.get(ssg_engine, {}))
        return base_vars

    def get_build_dependencies(self, ssg_engine: SSGEngine) -> Dict[str, Any]:
        """Get required dependencies for SSG engine with Shopify Basic"""
        dependencies = {
            SSGEngine.ELEVENTY: {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "graphql",
                    "node-fetch"
                ],
                "eleventy_plugins": [
                    "@11ty/eleventy-plugin-syntaxhighlight"
                ]
            },
            SSGEngine.ASTRO: {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "@astrojs/node",
                    "graphql"
                ],
                "astro_integrations": ["@astrojs/node"]
            },
            SSGEngine.NEXTJS: {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "@shopify/react-hooks",
                    "graphql",
                    "react",
                    "react-dom"
                ]
            },
            SSGEngine.NUXT: {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "@nuxtjs/axios",
                    "graphql"
                ],
                "nuxt_modules": ["@nuxtjs/axios"]
            }
        }

        return dependencies.get(ssg_engine, {"npm_packages": ["@shopify/storefront-api-client"]})

    def generate_build_configuration(self, ssg_engine: SSGEngine) -> Dict[str, Any]:
        """Generate build configuration for specific SSG engine"""
        base_config = {
            "provider": "shopify_basic",
            "store_domain": self.store_domain,
            "shopify_plan": self.shopify_plan.value,
            "ssg_engine": ssg_engine.value
        }

        # SSG-specific configurations
        ssg_configs = {
            SSGEngine.ELEVENTY: {
                "eleventy_config": {
                    "dir": {
                        "input": "src",
                        "output": "dist"
                    },
                    "templateFormats": ["njk", "md", "html"],
                    "dataTemplateEngine": "njk"
                },
                "build_command": "npx @11ty/eleventy",
                "output_dir": "dist"
            },
            SSGEngine.ASTRO: {
                "astro_config": {
                    "output": "static",
                    "integrations": ["@astrojs/node"],
                    "vite": {
                        "define": {
                            "__SHOPIFY_STORE_DOMAIN__": JSON.dumps(self.store_domain)
                        }
                    }
                },
                "build_command": "npm run build",
                "output_dir": "dist"
            },
            SSGEngine.NEXTJS: {
                "next_config": {
                    "output": "export",
                    "trailingSlash": True,
                    "images": {
                        "unoptimized": True
                    },
                    "env": {
                        "SHOPIFY_STORE_DOMAIN": self.store_domain
                    }
                },
                "build_command": "npm run build && npm run export",
                "output_dir": "out"
            },
            SSGEngine.NUXT: {
                "nuxt_config": {
                    "ssr": False,
                    "target": "static",
                    "modules": ["@nuxtjs/axios"],
                    "publicRuntimeConfig": {
                        "shopifyStoreDomain": self.store_domain
                    }
                },
                "build_command": "npm run generate",
                "output_dir": "dist"
            }
        }

        base_config.update(ssg_configs.get(ssg_engine, {}))
        return base_config

    def get_webhook_configuration(self) -> Dict[str, Any]:
        """Get webhook configuration for Shopify product/inventory synchronization"""
        return {
            "provider": "shopify_basic",
            "webhook_url": "{INTEGRATION_API_URL}/webhooks/shopify",
            "events": [
                "products/create",
                "products/update",
                "products/delete",
                "product_listings/add",
                "product_listings/remove",
                "product_listings/update",
                "inventory_levels/update",
                "collections/create",
                "collections/update",
                "collections/delete"
            ],
            "format": "json",
            "fields": [
                "id", "title", "handle", "description", "vendor",
                "product_type", "tags", "status", "images",
                "variants", "options", "created_at", "updated_at"
            ]
        }

    def get_storefront_queries(self) -> Dict[str, str]:
        """Get GraphQL queries for Shopify Storefront API"""
        return {
            "get_products": """
                query getProducts($first: Int!) {
                  products(first: $first) {
                    edges {
                      node {
                        id
                        title
                        handle
                        description
                        vendor
                        productType
                        tags
                        createdAt
                        updatedAt
                        images(first: 10) {
                          edges {
                            node {
                              id
                              url
                              altText
                              width
                              height
                            }
                          }
                        }
                        variants(first: 10) {
                          edges {
                            node {
                              id
                              title
                              price {
                                amount
                                currencyCode
                              }
                              compareAtPrice {
                                amount
                                currencyCode
                              }
                              availableForSale
                              quantityAvailable
                            }
                          }
                        }
                        priceRange {
                          minVariantPrice {
                            amount
                            currencyCode
                          }
                          maxVariantPrice {
                            amount
                            currencyCode
                          }
                        }
                      }
                    }
                  }
                }
            """,
            "get_product_by_handle": """
                query getProductByHandle($handle: String!) {
                  productByHandle(handle: $handle) {
                    id
                    title
                    handle
                    description
                    descriptionHtml
                    vendor
                    productType
                    tags
                    images(first: 10) {
                      edges {
                        node {
                          id
                          url
                          altText
                          width
                          height
                        }
                      }
                    }
                    variants(first: 10) {
                      edges {
                        node {
                          id
                          title
                          price {
                            amount
                            currencyCode
                          }
                          compareAtPrice {
                            amount
                            currencyCode
                          }
                          availableForSale
                          quantityAvailable
                          selectedOptions {
                            name
                            value
                          }
                        }
                      }
                    }
                    options {
                      id
                      name
                      values
                    }
                    seo {
                      title
                      description
                    }
                  }
                }
            """,
            "get_collections": """
                query getCollections($first: Int!) {
                  collections(first: $first) {
                    edges {
                      node {
                        id
                        title
                        handle
                        description
                        image {
                          id
                          url
                          altText
                        }
                        products(first: 10) {
                          edges {
                            node {
                              id
                              title
                              handle
                              images(first: 1) {
                                edges {
                                  node {
                                    url
                                    altText
                                  }
                                }
                              }
                              priceRange {
                                minVariantPrice {
                                  amount
                                  currencyCode
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
            """
        }

    def estimate_monthly_cost(self, client_requirements: Dict[str, Any]) -> Dict[str, float]:
        """Estimate monthly cost for Shopify Basic tier"""

        # Shopify Basic plan cost
        shopify_basic = 29  # Fixed Shopify Basic plan cost

        # AWS infrastructure costs
        aws_hosting = client_requirements.get("traffic_level", "medium") == "high" and 35 or 20
        aws_lambda = 5   # Build triggers and webhook handling
        aws_storage = 3  # S3 storage for static assets

        # Integration and maintenance
        integration_maintenance = 15  # Automated sync and monitoring
        performance_optimization = 8  # CDN and caching

        # Transaction fees (estimated)
        monthly_sales = client_requirements.get("monthly_sales", 5000)
        transaction_fees = monthly_sales * 0.029  # 2.9% Shopify Basic transaction fee

        total_cost = (
            shopify_basic +
            aws_hosting +
            aws_lambda +
            aws_storage +
            integration_maintenance +
            performance_optimization +
            transaction_fees
        )

        return {
            "shopify_basic_plan": shopify_basic,
            "aws_infrastructure": aws_hosting + aws_lambda + aws_storage,
            "integration_maintenance": integration_maintenance,
            "performance_optimization": performance_optimization,
            "estimated_transaction_fees": transaction_fees,
            "total": total_cost
        }

    def get_business_positioning(self) -> Dict[str, Any]:
        """Get business positioning information for Shopify Basic tier"""
        return {
            "tier": "basic_ecommerce",
            "target_market": [
                "small_medium_stores",
                "performance_focused_brands",
                "budget_conscious_businesses",
                "shopify_theme_upgrades",
                "agency_alternatives"
            ],
            "key_differentiators": [
                "Enterprise performance at small business prices",
                "80-90% cost reduction vs traditional Shopify agencies",
                "Static site performance with full Shopify e-commerce",
                "Flexible SSG engine choice for technical preference",
                "Automated maintenance and updates",
                "Proven Shopify platform with custom frontend"
            ],
            "ideal_client_profile": {
                "business_size": "Small to medium e-commerce stores",
                "monthly_sales": "$2,000-25,000 per month",
                "technical_requirements": "Performance-focused, SEO-critical",
                "budget_range": "$75-125 per month",
                "current_pain_points": "Slow Shopify themes or expensive agency maintenance"
            },
            "competitive_advantages": [
                "Shopify's proven e-commerce platform with superior frontend performance",
                "Automated infrastructure eliminates agency maintenance costs",
                "Static site delivery provides 2-3x faster page loads",
                "Flexible SSG engine choice serves different technical preferences",
                "Professional e-commerce features without enterprise complexity"
            ],
            "roi_factors": [
                "Improved conversion rates through faster page loads",
                "Reduced development and maintenance costs vs agencies",
                "Better SEO performance through static HTML delivery",
                "Eliminated theme limitations with custom frontend",
                "Automated scaling and performance optimization"
            ]
        }

    @classmethod
    def get_client_suitability_score(
        cls,
        client_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate suitability score for Shopify Basic tier based on client requirements"""

        score = 0
        reasons = []

        # E-commerce business requirements
        if client_requirements.get("ecommerce_needed", False):
            score += 25
            reasons.append("E-commerce functionality required")

        if client_requirements.get("product_catalog", False):
            score += 20
            reasons.append("Product catalog management needed")

        # Performance and technical requirements
        if client_requirements.get("performance_critical", False):
            score += 20
            reasons.append("Performance-critical requirements align with static site benefits")

        if client_requirements.get("seo_focused", False):
            score += 15
            reasons.append("SEO-focused business benefits from static HTML delivery")

        # Budget considerations
        monthly_budget = client_requirements.get("monthly_budget", 0)
        if 75 <= monthly_budget <= 200:
            score += 20
            reasons.append("Budget range ideal for Shopify Basic tier")
        elif monthly_budget < 75:
            score -= 15
            reasons.append("Budget may be tight for full Shopify Basic tier")
        elif monthly_budget > 300:
            score += 5
            reasons.append("Budget supports Shopify Basic with room for growth")

        # Business size and complexity
        business_size = client_requirements.get("business_size", "small")
        if business_size in ["small", "medium"]:
            score += 15
            reasons.append("Business size fits Shopify Basic tier perfectly")
        elif business_size == "enterprise":
            score -= 10
            reasons.append("Enterprise size might need Shopify Advanced tier")

        # Technical preferences
        if client_requirements.get("static_site_preferred", False):
            score += 10
            reasons.append("Static site preference aligns with architecture")

        # Current situation penalties/bonuses
        if client_requirements.get("current_platform") == "shopify_theme":
            score += 15
            reasons.append("Perfect upgrade path from basic Shopify themes")

        if client_requirements.get("agency_maintenance_cost", 0) > 200:
            score += 25
            reasons.append("Significant cost savings vs current agency maintenance")

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
            "recommended_ssg_engines": ["eleventy", "astro", "nextjs", "nuxt"],
            "monthly_cost_estimate": "$75-125",
            "setup_complexity": "medium",
            "ongoing_complexity": "low"
        }