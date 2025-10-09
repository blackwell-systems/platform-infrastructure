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

from aws_cdk import (
    aws_lambda as lambda_,
    aws_ses as ses,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Duration,
)

from shared.ssg.core_models import SSGEngineType
from shared.providers.ecommerce.base_provider import EcommerceProvider


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
    ssg_engine: SSGEngineType
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
            "eleventy": "npx @11ty/eleventy",
            "astro": "npm run build",
            "nextjs": "npm run build && npm run export",
            "nuxt": "npm run generate"
        }
        return commands.get(self.ssg_engine, "npm run build")

    def _get_default_packages(self) -> List[str]:
        """Get default Shopify packages for SSG engine"""
        packages = {
            "eleventy": ["@shopify/storefront-api-client"],
            "astro": ["@shopify/storefront-api-client", "@astrojs/node"],
            "nextjs": ["@shopify/storefront-api-client", "@shopify/react-hooks"],
            "nuxt": ["@shopify/storefront-api-client", "@nuxtjs/axios"]
        }
        return packages.get(self.ssg_engine, ["@shopify/storefront-api-client"])


class ShopifyBasicProvider(EcommerceProvider):
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
        "eleventy": {
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
        "astro": {
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
        "nextjs": {
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
        "nuxt": {
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
        ssg_engine: Optional[SSGEngineType] = None
    ):
        config = {
            "store_domain": store_domain,
            "shopify_plan": shopify_plan,
            "ssg_engine": ssg_engine
        }
        super().__init__("shopify_basic", config)
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

    def get_supported_ssg_engines(self) -> List[SSGEngineType]:
        """Get list of SSG engines supported by Shopify Basic provider"""
        return [
            "eleventy",
            "astro",
            "nextjs",
            "nuxt"
        ]

    def validate_ssg_compatibility(self, ssg_engine: SSGEngineType) -> Dict[str, Any]:
        """Validate and get compatibility information for SSG engine"""
        if ssg_engine not in self.get_supported_ssg_engines():
            return {
                "compatible": False,
                "reason": f"SSG engine {ssg_engine} not supported by Shopify Basic provider",
                "supported_engines": [engine for engine in self.get_supported_ssg_engines()]
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

    def generate_environment_variables(self, ssg_engine: SSGEngineType) -> Dict[str, str]:
        """Generate environment variables for SSG build process"""
        base_vars = {
            "SHOPIFY_STORE_DOMAIN": self.store_domain,
            "SHOPIFY_STOREFRONT_ACCESS_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}",
            "SHOPIFY_API_VERSION": "2023-10"
        }

        # Add SSG-specific variables
        ssg_vars = {
            "eleventy": {
                "SHOPIFY_API_ENDPOINT": f"https://{self.store_domain}/api/2023-10/graphql.json"
            },
            "astro": {
                "PUBLIC_SHOPIFY_STORE_DOMAIN": self.store_domain,
                "PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}"
            },
            "nextjs": {
                "NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN": self.store_domain,
                "NEXT_PUBLIC_SHOPIFY_STOREFRONT_ACCESS_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}",
                "SHOPIFY_ADMIN_ACCESS_TOKEN": "${SHOPIFY_ADMIN_TOKEN}"
            },
            "nuxt": {
                "NUXT_PUBLIC_SHOPIFY_STORE_DOMAIN": self.store_domain,
                "NUXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}"
            }
        }

        base_vars.update(ssg_vars.get(ssg_engine, {}))
        return base_vars

    def get_build_dependencies(self, ssg_engine: SSGEngineType) -> Dict[str, Any]:
        """Get required dependencies for SSG engine with Shopify Basic"""
        dependencies = {
            "eleventy": {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "graphql",
                    "node-fetch"
                ],
                "eleventy_plugins": [
                    "@11ty/eleventy-plugin-syntaxhighlight"
                ]
            },
            "astro": {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "@astrojs/node",
                    "graphql"
                ],
                "astro_integrations": ["@astrojs/node"]
            },
            "nextjs": {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "@shopify/react-hooks",
                    "graphql",
                    "react",
                    "react-dom"
                ]
            },
            "nuxt": {
                "npm_packages": [
                    "@shopify/storefront-api-client",
                    "@nuxtjs/axios",
                    "graphql"
                ],
                "nuxt_modules": ["@nuxtjs/axios"]
            }
        }

        return dependencies.get(ssg_engine, {"npm_packages": ["@shopify/storefront-api-client"]})

    def generate_build_configuration(self, ssg_engine: SSGEngineType) -> Dict[str, Any]:
        """Generate build configuration for specific SSG engine"""
        base_config = {
            "provider": "shopify_basic",
            "store_domain": self.store_domain,
            "shopify_plan": self.shopify_plan.value,
            "ssg_engine": ssg_engine
        }

        # SSG-specific configurations
        ssg_configs = {
            "eleventy": {
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
            "astro": {
                "astro_config": {
                    "output": "static",
                    "integrations": ["@astrojs/node"],
                    "vite": {
                        "define": {
                            "__SHOPIFY_STORE_DOMAIN__": json.dumps(self.store_domain)
                        }
                    }
                },
                "build_command": "npm run build",
                "output_dir": "dist"
            },
            "nextjs": {
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
            "nuxt": {
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

    # ================================
    # Abstract Method Implementations
    # ================================

    def get_environment_variables(self) -> Dict[str, str]:
        """Get Shopify Basic-specific environment variables"""
        return {
            # Core Shopify configuration
            "SHOPIFY_STORE_DOMAIN": self.store_domain,
            "SHOPIFY_STOREFRONT_ACCESS_TOKEN": "${SHOPIFY_STOREFRONT_TOKEN}",  # CDK parameter
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "${SHOPIFY_ADMIN_TOKEN}",  # CDK parameter
            "SHOPIFY_API_VERSION": "2023-10",  # Latest stable API version

            # Store configuration
            "SHOPIFY_PLAN": self.shopify_plan.value,
            "STORE_NAME": self.config.get("store_name", "Online Store"),
            "STORE_CURRENCY": self.config.get("currency", "USD"),

            # E-commerce optimizations
            "SITE_TYPE": "ecommerce",
            "NODE_ENV": "production",
            "SHOPIFY_PRODUCTION": "true",

            # Shopify-specific features
            "SHOPIFY_STOREFRONT_API_ENABLED": "true",
            "SHOPIFY_WEBHOOK_ENABLED": "true",
            "SHOPIFY_INVENTORY_SYNC": "true",
            "SHOPIFY_PRODUCT_SYNC": "true",

            # Performance optimizations
            "SHOPIFY_CACHE_PRODUCTS": "true",
            "SHOPIFY_CACHE_DURATION": "3600",  # 1 hour cache
            "SHOPIFY_BUILD_INCREMENTAL": "true",  # Faster rebuilds

            # Analytics integration
            "GOOGLE_ANALYTICS_ID": "${GOOGLE_ANALYTICS_ID}",  # CDK parameter
            "GOOGLE_ANALYTICS_ECOMMERCE": "true",
            "FACEBOOK_PIXEL_ID": "${FACEBOOK_PIXEL_ID}",  # CDK parameter
            "SHOPIFY_CONVERSION_TRACKING": "true",

            # Performance monitoring
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "TRACK_CART_ABANDONMENT": "true",
            "SHOPIFY_PERFORMANCE_METRICS": "true",

            # Security and compliance
            "SHOPIFY_WEBHOOK_SECRET": "${SHOPIFY_WEBHOOK_SECRET}",  # CDK parameter
            "SHOPIFY_SSL_REQUIRED": "true"
        }

    def setup_infrastructure(self, stack) -> None:
        """Set up Shopify Basic-specific AWS infrastructure"""
        self._setup_order_notification_system(stack)
        self._setup_webhook_processing(stack)
        self._setup_api_gateway(stack)

    def _setup_order_notification_system(self, stack) -> None:
        """Set up SES for order email notifications"""
        # Create SES configuration set for order notifications
        self.notification_config = ses.CfnConfigurationSet(
            stack,
            "ShopifyNotificationConfigSet",
            name=f"{stack.ssg_config.client_id}-shopify-notifications"
        )

    def _setup_webhook_processing(self, stack) -> None:
        """Set up Lambda function for processing Shopify webhooks"""
        # Create Lambda function for Shopify webhook processing
        self.order_processor = lambda_.Function(
            stack,
            "ShopifyOrderProcessor",
            function_name=f"{stack.ssg_config.client_id}-shopify-order-processor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="shopify_webhook.handler",
            code=lambda_.Code.from_inline(self._get_webhook_lambda_code()),
            environment={
                "NOTIFICATION_FROM_EMAIL": f"orders@{self._get_root_domain(stack)}",
                "NOTIFICATION_TO_EMAIL": "${NOTIFICATION_EMAIL}",  # CDK parameter
                "STORE_NAME": self.config.get("store_name", "Online Store"),
                "SHOPIFY_WEBHOOK_SECRET": "${SHOPIFY_WEBHOOK_SECRET}",  # CDK parameter
                "SHOPIFY_STORE_DOMAIN": self.store_domain,
                "SHOPIFY_API_VERSION": "2023-10",
            },
            timeout=Duration.seconds(45),  # Shopify webhooks can be complex
            memory_size=512  # More memory for product processing
        )

        # Grant SES permissions to the Lambda function
        self.order_processor.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ses:SendEmail",
                    "ses:SendRawEmail"
                ],
                resources=[
                    f"arn:aws:ses:{stack.region}:{stack.account}:identity/*"
                ]
            )
        )

        # Store the Lambda function reference for stack access
        stack.shopify_order_processor = self.order_processor

    def _setup_api_gateway(self, stack) -> None:
        """Set up API Gateway for Shopify webhook endpoints"""
        # Create API Gateway for webhook endpoints
        self.webhook_api = apigateway.RestApi(
            stack,
            "ShopifyWebhookAPI",
            rest_api_name=f"{stack.ssg_config.client_id}-shopify-webhooks",
            description="API Gateway for Shopify webhook processing and build triggers"
        )

        # Create webhook resource and method
        webhook_resource = self.webhook_api.root.add_resource("shopify-webhook")
        webhook_integration = apigateway.LambdaIntegration(self.order_processor)
        webhook_resource.add_method("POST", webhook_integration)

        # Store API Gateway reference for stack access
        stack.shopify_webhook_api = self.webhook_api

    def _get_webhook_lambda_code(self) -> str:
        """Get the Lambda function code for Shopify webhook processing"""
        return """
import json
import boto3
import os
import hmac
import hashlib
import base64
from datetime import datetime

def handler(event, context):
    '''
    Process Shopify webhook for product updates, order notifications, and build triggers.

    Shopify sends webhook data for products, orders, inventory changes, and other events.
    This function validates the webhook signature, processes the event, and triggers
    site rebuilds when content changes.
    '''

    try:
        # Validate webhook signature (security)
        signature = event.get('headers', {}).get('X-Shopify-Hmac-Sha256', '')
        body = event.get('body', '')

        if not _validate_signature(body, signature):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid webhook signature'})
            }

        # Parse Shopify webhook data
        webhook_data = json.loads(body) if body else {}
        topic = event.get('headers', {}).get('X-Shopify-Topic', 'unknown')

        # Process different types of events
        if topic.startswith('products/'):
            _process_product_event(webhook_data, topic)
        elif topic.startswith('orders/'):
            _process_order_event(webhook_data, topic)
        elif topic.startswith('inventory_levels/'):
            _process_inventory_event(webhook_data, topic)
        elif topic.startswith('collections/'):
            _process_collection_event(webhook_data, topic)
        else:
            print(f"Unhandled webhook topic: {topic}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Webhook processed successfully'})
        }

    except Exception as e:
        print(f"Error processing Shopify webhook: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Failed to process webhook'})
        }

def _validate_signature(body, signature):
    '''Validate Shopify webhook signature for security'''
    webhook_secret = os.environ.get('SHOPIFY_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return True  # Skip validation if no secret configured

    # Shopify sends base64-encoded HMAC-SHA256
    expected_signature = base64.b64encode(
        hmac.new(
            webhook_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')

    return hmac.compare_digest(signature, expected_signature)

def _process_product_event(product_data, topic):
    '''Process product events (create, update, delete)'''
    product_id = product_data.get('id', 'unknown')
    product_title = product_data.get('title', 'Unknown Product')
    product_handle = product_data.get('handle', 'unknown')

    print(f"Product event: {topic} - {product_title} (ID: {product_id})")

    # Trigger site rebuild for product changes
    if topic in ['products/create', 'products/update', 'products/delete']:
        _trigger_site_rebuild('product_change', {
            'product_id': product_id,
            'product_handle': product_handle,
            'action': topic.split('/')[-1]
        })

def _process_order_event(order_data, topic):
    '''Process order events'''
    order_id = order_data.get('id', 'unknown')
    order_number = order_data.get('order_number', order_id)
    customer_email = order_data.get('email', 'unknown')
    total_price = order_data.get('total_price', '0.00')
    currency = order_data.get('currency', 'USD')

    print(f"Order event: {topic} - Order #{order_number} (${total_price} {currency})")

    # Send order notification for completed orders
    if topic == 'orders/paid':
        _send_order_notification(order_number, customer_email, total_price, currency, 'order_paid')

def _process_inventory_event(inventory_data, topic):
    '''Process inventory level events'''
    inventory_item_id = inventory_data.get('inventory_item_id', 'unknown')
    location_id = inventory_data.get('location_id', 'unknown')
    available = inventory_data.get('available', 0)

    print(f"Inventory event: {topic} - Item {inventory_item_id} at location {location_id}: {available} available")

    # Trigger site rebuild for inventory changes if low stock
    if available <= 5:  # Low stock threshold
        _trigger_site_rebuild('inventory_low', {
            'inventory_item_id': inventory_item_id,
            'available': available
        })

def _process_collection_event(collection_data, topic):
    '''Process collection events'''
    collection_id = collection_data.get('id', 'unknown')
    collection_title = collection_data.get('title', 'Unknown Collection')
    collection_handle = collection_data.get('handle', 'unknown')

    print(f"Collection event: {topic} - {collection_title} (ID: {collection_id})")

    # Trigger site rebuild for collection changes
    _trigger_site_rebuild('collection_change', {
        'collection_id': collection_id,
        'collection_handle': collection_handle,
        'action': topic.split('/')[-1]
    })

def _send_order_notification(order_number, customer_email, total_price, currency, event_type):
    '''Send order notification email via SES'''
    ses_client = boto3.client('ses')

    subject = f"New Order #{order_number} - {os.environ['STORE_NAME']}"
    body_text = f'''
New Shopify order received!

Order Details:
- Order Number: #{order_number}
- Customer: {customer_email}
- Total: {currency} {total_price}
- Event: {event_type}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- Store: {os.environ.get('SHOPIFY_STORE_DOMAIN', 'N/A')}

Please check your Shopify admin panel for complete order details:
https://{os.environ.get('SHOPIFY_STORE_DOMAIN', '')}/admin/orders

Shopify Basic Integration:
- Static site performance with full e-commerce functionality
- Real-time synchronization between Shopify and your website
- Automated build triggers for content updates

Thank you for using Shopify Basic with static site integration!
    '''

    try:
        ses_client.send_email(
            Source=os.environ['NOTIFICATION_FROM_EMAIL'],
            Destination={'ToAddresses': [os.environ['NOTIFICATION_TO_EMAIL']]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body_text}}
            }
        )
        print(f"Order notification sent for order #{order_number}")
    except Exception as e:
        print(f"Failed to send order notification: {str(e)}")

def _trigger_site_rebuild(trigger_type, trigger_data):
    '''Trigger site rebuild for content changes'''
    # This would typically trigger CodeBuild or another build system
    # For now, just log the rebuild trigger
    print(f"Site rebuild triggered: {trigger_type} - {json.dumps(trigger_data)}")

    # In a full implementation, this would:
    # 1. Trigger AWS CodeBuild project
    # 2. Invalidate CloudFront cache
    # 3. Update build status in DynamoDB
    # 4. Send SNS notification
        """

    def _get_root_domain(self, stack) -> str:
        """Extract root domain from stack configuration"""
        domain_parts = stack.ssg_config.domain.split('.')
        if len(domain_parts) >= 2:
            return '.'.join(domain_parts[-2:])
        return stack.ssg_config.domain

    def get_configuration_metadata(self) -> Dict[str, Any]:
        """Get Shopify Basic configuration metadata"""
        return {
            "provider": "shopify_basic",
            "integration_method": "headless_api",
            "setup_complexity": "medium",
            "estimated_setup_hours": 4.5,

            # Cost structure
            "monthly_cost_range": [75, 125],  # AWS hosting + Shopify Basic plan + integration
            "shopify_plan_cost": 29,  # Shopify Basic plan
            "transaction_fee_percent": 2.9,  # Shopify Basic transaction fees
            "additional_transaction_fee": 0.30,  # Fixed per transaction
            "additional_aws_costs": "$46-96/month",  # AWS infrastructure

            # Features
            "features": [
                "product_catalog", "inventory_tracking", "shopping_cart", "secure_checkout",
                "order_management", "customer_accounts", "payment_processing", "mobile_optimization",
                "ssl_security", "basic_analytics", "storefront_api", "webhook_integration",
                "app_ecosystem", "abandoned_cart_recovery", "discount_codes", "gift_cards"
            ],
            "payment_methods": [
                "shopify_payments", "paypal", "stripe", "square", "apple_pay", "google_pay",
                "amazon_pay", "shop_pay", "afterpay", "klarna", "credit_cards", "debit_cards"
            ],
            "supported_currencies": [
                "USD", "CAD", "EUR", "GBP", "AUD", "JPY", "CHF", "DKK", "NOK", "SEK",
                "NZD", "SGD", "HKD", "PLN", "CZK", "HUF", "RON", "BGN", "HRK", "MXN"
            ],

            # Technical capabilities
            "supports_webhooks": True,
            "supports_storefront_api": True,
            "supports_admin_api": True,
            "supports_graphql": True,
            "supports_rest_api": True,
            "pci_compliant": True,
            "ssl_required": True,
            "cdn_optimized": True,
            "mobile_responsive": True,

            # Performance advantages
            "performance_benefits": [
                "Static site delivery with 2-3x faster page loads",
                "CDN optimization with global content delivery",
                "Superior SEO with static HTML generation",
                "Mobile-first responsive design optimization",
                "Automated image optimization and compression"
            ],

            # Business advantages
            "business_benefits": [
                "80-90% cost reduction vs traditional Shopify agencies",
                "Enterprise performance at small business prices",
                "Automated maintenance and updates",
                "Proven Shopify platform with custom frontend",
                "Flexible SSG engine choice for technical preferences"
            ],

            # Integration requirements
            "required_environment_vars": [
                "SHOPIFY_STORE_DOMAIN",  # From Shopify admin
                "SHOPIFY_STOREFRONT_TOKEN",  # Storefront API access token
                "SHOPIFY_ADMIN_TOKEN",  # Admin API access token (optional)
                "NOTIFICATION_EMAIL",  # For order notifications
                "SHOPIFY_WEBHOOK_SECRET",  # For webhook security
            ],
            "optional_environment_vars": [
                "GOOGLE_ANALYTICS_ID",  # For e-commerce tracking
                "FACEBOOK_PIXEL_ID",  # For conversion tracking
                "STORE_NAME",  # Custom store name
                "STORE_CURRENCY",  # Store currency override
            ],

            # SSG engine compatibility
            "supported_ssg_engines": [
                {
                    "engine": "eleventy",
                    "compatibility_score": 9,
                    "setup_complexity": "simple",
                    "recommended_for": ["small_stores", "budget_conscious", "simple_catalogs"]
                },
                {
                    "engine": "astro",
                    "compatibility_score": 10,
                    "setup_complexity": "intermediate",
                    "recommended_for": ["performance_critical", "modern_brands", "component_based"]
                },
                {
                    "engine": "nextjs",
                    "compatibility_score": 9,
                    "setup_complexity": "advanced",
                    "recommended_for": ["react_teams", "complex_interactions", "custom_features"]
                },
                {
                    "engine": "nuxt",
                    "compatibility_score": 8,
                    "setup_complexity": "advanced",
                    "recommended_for": ["vue_teams", "ssr_applications", "european_markets"]
                }
            ],

            # Documentation and resources
            "documentation_url": "https://shopify.dev/api/storefront",
            "admin_url": f"https://{self.store_domain}/admin",
            "api_documentation": "https://shopify.dev/api",
            "template_repo": "https://github.com/your-templates/shopify-static-store",
            "demo_url": "https://demo.yourservices.com/shopify-basic",

            # Business model information
            "target_market": [
                "small_medium_ecommerce",
                "performance_focused_brands",
                "shopify_theme_upgrades",
                "agency_alternatives",
                "budget_conscious_businesses"
            ],
            "ideal_client_profile": {
                "monthly_sales": "$2,000-25,000",
                "business_size": "Small to medium stores",
                "technical_comfort": "Low to medium",
                "budget_range": "$75-125/month",
                "current_pain_points": "Slow themes, expensive agencies"
            },

            # ROI and value proposition
            "roi_factors": [
                "Improved conversion rates through faster page loads (average 15-25% increase)",
                "Reduced development costs vs traditional agencies (80-90% savings)",
                "Better SEO performance through static HTML delivery",
                "Eliminated theme limitations with custom frontend",
                "Automated scaling and performance optimization"
            ]
        }

    def get_required_aws_services(self) -> List[str]:
        """Get AWS services required by Shopify Basic integration"""
        return [
            "Lambda",      # Webhook processing and build triggers
            "SES",         # Order notification emails
            "API Gateway"  # Webhook endpoints and API management
        ]

    def validate_configuration(self) -> bool:
        """Validate Shopify Basic provider configuration"""
        # Validate store domain format
        if not self.store_domain:
            raise ValueError("Shopify store domain is required")

        # Ensure store domain ends with .myshopify.com
        if not self.store_domain.endswith('.myshopify.com'):
            raise ValueError(
                f"Invalid Shopify store domain '{self.store_domain}'. "
                "Must end with '.myshopify.com' (e.g., 'your-store.myshopify.com')"
            )

        # Validate store domain format (no spaces, special characters)
        store_name = self.store_domain.replace('.myshopify.com', '')
        if not store_name or not store_name.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                f"Invalid store name '{store_name}'. "
                "Store name should contain only letters, numbers, hyphens, and underscores"
            )

        # Validate Shopify plan
        valid_plans = [plan.value for plan in ShopifyPlan]
        if self.shopify_plan.value not in valid_plans:
            raise ValueError(
                f"Invalid Shopify plan '{self.shopify_plan.value}'. "
                f"Must be one of: {valid_plans}"
            )

        # Validate SSG engine if specified
        if self.ssg_engine:
            supported_engines = self.get_supported_ssg_engines()
            if self.ssg_engine not in supported_engines:
                raise ValueError(
                    f"SSG engine '{self.ssg_engine}' not supported by Shopify Basic provider. "
                    f"Supported engines: {supported_engines}"
                )

        # Validate currency if specified in config
        currency = self.config.get("currency", "USD")
        supported_currencies = self.get_configuration_metadata()["supported_currencies"]
        if currency not in supported_currencies:
            raise ValueError(
                f"Unsupported currency '{currency}'. "
                f"Supported currencies: {', '.join(supported_currencies[:10])}... (and {len(supported_currencies)-10} more)"
            )

        # Validate optional configuration parameters
        if "monthly_sales" in self.config:
            monthly_sales = self.config["monthly_sales"]
            if not isinstance(monthly_sales, (int, float)) or monthly_sales < 0:
                raise ValueError("Monthly sales must be a non-negative number")

        if "store_name" in self.config:
            store_name = self.config["store_name"]
            if not isinstance(store_name, str) or len(store_name.strip()) == 0:
                raise ValueError("Store name must be a non-empty string")

        # Validate Shopify-specific settings
        if hasattr(self, 'ecommerce_settings'):
            settings = self.ecommerce_settings

            # Check cache duration is reasonable
            if settings.cache_duration_hours < 1 or settings.cache_duration_hours > 168:  # 1 hour to 1 week
                raise ValueError("Cache duration must be between 1 and 168 hours (1 week)")

        return True

    def get_webhook_endpoint_name(self) -> str:
        """Get Shopify webhook endpoint name"""
        return "shopify-webhook"

    def get_client_integration_guide(self) -> Dict[str, Any]:
        """
        Get step-by-step integration guide for clients.

        Returns detailed instructions for setting up Shopify Basic
        with static site integration.
        """
        return {
            "title": "Shopify Basic Static Site Integration Setup Guide",
            "steps": [
                {
                    "step": 1,
                    "title": "Verify Shopify Basic Plan",
                    "description": "Ensure your Shopify store is on the Basic plan or higher",
                    "action": "Check your plan in Shopify Admin > Settings > Plan and permissions",
                    "cost": "$29/month for Shopify Basic plan"
                },
                {
                    "step": 2,
                    "title": "Create Storefront API Access Token",
                    "description": "Generate a private app with Storefront API access",
                    "action": "Navigate to Apps > Develop apps > Create an app",
                    "required_permissions": [
                        "Storefront API access",
                        "Read products",
                        "Read collections",
                        "Read customer tags",
                        "Read inventory"
                    ]
                },
                {
                    "step": 3,
                    "title": "Generate Admin API Access Token (Optional)",
                    "description": "Create admin API access for advanced features",
                    "action": "In your private app, configure Admin API scopes",
                    "required_scopes": [
                        "read_products",
                        "read_orders",
                        "read_inventory",
                        "read_customers"
                    ]
                },
                {
                    "step": 4,
                    "title": "Configure CDK Parameters",
                    "description": "Set the required CDK parameters for deployment",
                    "parameters": {
                        "SHOPIFY_STORE_DOMAIN": f"{self.store_domain}",
                        "SHOPIFY_STOREFRONT_TOKEN": "Your Storefront API access token",
                        "SHOPIFY_ADMIN_TOKEN": "Your Admin API access token (optional)",
                        "NOTIFICATION_EMAIL": "Email for order notifications",
                        "SHOPIFY_WEBHOOK_SECRET": "Webhook verification secret (recommended)"
                    }
                },
                {
                    "step": 5,
                    "title": "Choose SSG Engine",
                    "description": "Select your preferred static site generator",
                    "options": {
                        "eleventy": "Simple, fast builds - great for beginners",
                        "astro": "Modern performance - best overall choice",
                        "nextjs": "React ecosystem - for React developers",
                        "nuxt": "Vue ecosystem - for Vue developers"
                    }
                },
                {
                    "step": 6,
                    "title": "Deploy Infrastructure",
                    "description": "Deploy the CDK stack with Shopify Basic integration",
                    "action": "Run: cdk deploy YourStackName --parameters ShopifyStoreDomain=your-store.myshopify.com"
                },
                {
                    "step": 7,
                    "title": "Configure Shopify Webhooks",
                    "description": "Set up webhooks in Shopify admin for real-time sync",
                    "webhook_url": "https://your-domain.com/api/shopify-webhook",
                    "events": [
                        "Product creation",
                        "Product updates",
                        "Product deletion",
                        "Inventory updates",
                        "Collection changes",
                        "Order creation (optional)"
                    ]
                },
                {
                    "step": 8,
                    "title": "Test Integration",
                    "description": "Verify the integration is working correctly",
                    "verification_steps": [
                        "Check that products are displayed on your static site",
                        "Verify cart functionality redirects to Shopify checkout",
                        "Test webhook processing by creating a test product",
                        "Confirm order notification emails are working"
                    ]
                }
            ],
            "testing": {
                "test_products": "Create test products in Shopify admin",
                "test_checkout": "Add items to cart and complete checkout process",
                "verification": "Verify static site updates when you change products in Shopify"
            },
            "costs": {
                "shopify_plan": "$29/month (Shopify Basic)",
                "aws_hosting": "$20-35/month (varies by traffic)",
                "integration_maintenance": "$15/month (automated)",
                "performance_optimization": "$8/month (CDN and caching)",
                "transaction_fees": "2.9% + 30¢ per transaction (Shopify Basic rate)",
                "total_estimate": "$75-125/month depending on traffic and sales volume"
            },
            "performance_benefits": {
                "page_load_speed": "2-3x faster than standard Shopify themes",
                "seo_improvement": "Static HTML provides superior search engine optimization",
                "conversion_rate": "15-25% average improvement due to faster loading",
                "mobile_performance": "Optimized responsive design with faster mobile loading",
                "global_delivery": "CDN ensures fast loading worldwide"
            },
            "ongoing_maintenance": {
                "automated_updates": "Site automatically rebuilds when products change",
                "security_updates": "AWS infrastructure managed and updated automatically",
                "performance_monitoring": "Built-in monitoring and alerting",
                "support": "Email support for technical issues and optimization"
            }
        }