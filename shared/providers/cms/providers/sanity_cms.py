"""
Sanity CMS Provider Implementation

Provides structured content management through Sanity's API-based platform,
combining powerful content modeling with real-time APIs and GROQ querying.

Key Features:
- Structured content with rich schemas and validation
- Real-time editing and collaboration
- GROQ query language for flexible content retrieval
- Advanced media management with image transformations
- Webhook-based content synchronization
- CDN-delivered content for global performance

Architecture:
- API-based CMS with real-time content delivery
- Structured content schemas with relationships
- GROQ query language for content access
- Webhook integration for live updates
- CDN optimization for media assets

Target Market:
- Professional websites requiring structured content
- API-first development teams
- Sites with complex content relationships
- Teams wanting real-time collaboration
- Organizations needing content governance

Pricing:
- Free tier: Up to 3 users, 10k API requests/month
- Growth: $99/month for team features
- Business: $199/month for enterprise features
- Total monthly cost: $80-180 including hosting
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import json

from shared.providers.cms.base_provider import CMSProvider, CMSType, CMSAuthMethod
from shared.providers.cms.models import (
    ContentCollection,
    MediaAsset
)


# Temporary model classes for Sanity CMS provider
class CMSCostEstimate:
    def __init__(self, provider: str, base_monthly_fee: float, content_volume: str,
                 additional_features: Dict[str, float], total_estimated: float):
        self.provider = provider
        self.base_monthly_fee = base_monthly_fee
        self.content_volume = content_volume
        self.additional_features = additional_features
        self.total_estimated = total_estimated


class CMSUser:
    def __init__(self, id: str, email: str, name: str, role: str,
                 permissions: List[str], last_login: datetime, created_at: datetime):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.permissions = permissions
        self.last_login = last_login
        self.created_at = created_at


class CMSMetrics:
    def __init__(self, total_content_items: int, monthly_edits: int, active_users: int,
                 storage_usage: int, api_requests: int, last_updated: datetime):
        self.total_content_items = total_content_items
        self.monthly_edits = monthly_edits
        self.active_users = active_users
        self.storage_usage = storage_usage
        self.api_requests = api_requests
        self.last_updated = last_updated


class SanityCMSProvider(CMSProvider):
    """
    Sanity CMS provider implementation for structured content management.

    Provides API-based content management with real-time collaboration,
    powerful querying capabilities, and advanced content modeling for
    professional websites and applications.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Sanity CMS provider.

        Args:
            config: Configuration dictionary containing:
                - project_id: Sanity project ID
                - dataset: Sanity dataset name
                - api_version: Sanity API version
                - api_token: Sanity API token (optional)
                - webhook_secret: Webhook validation secret (optional)
                - use_cdn: Whether to use Sanity's CDN
        """
        super().__init__("sanity", config)

        # Validate required Sanity configuration
        self._validate_sanity_config()

        # API-based settings
        self.project_id = config["project_id"]
        self.dataset = config.get("dataset", "production")
        self.api_version = config.get("api_version", "2023-05-03")
        self.use_cdn = config.get("use_cdn", True)

        # Optional authentication and webhook settings
        self.api_token = config.get("api_token")
        self.webhook_secret = config.get("webhook_secret")

        # Initialize API endpoints
        self.api_base_url = self._get_api_base_url()
        self.cdn_base_url = self._get_cdn_base_url()

    # provider_name is set by base class

    def get_cms_type(self) -> CMSType:
        return CMSType.API_BASED

    def get_auth_method(self) -> CMSAuthMethod:
        return CMSAuthMethod.API_KEY

    def get_supported_capabilities(self) -> List[str]:
        return [
            "structured_content",
            "real_time_collaboration",
            "rich_text_editing",
            "media_management",
            "developer_api",
            "webhook_integration",
            "content_validation",
            "version_control",
            "preview_mode",
            "content_scheduling",
            "advanced_media",
            "team_management",
            "analytics_dashboard",
            "multi_language"
        ]

    def get_supported_ssg_engines(self) -> List[str]:
        """Sanity works well with modern SSGs that can consume APIs"""
        return ["nextjs", "astro", "gatsby", "eleventy"]

    def get_admin_interface_config(self) -> Dict[str, Any]:
        """Get Sanity Studio configuration"""
        return {
            "interface_type": "structured_editor",
            "admin_path": "/studio",
            "studio_url": f"https://{self.project_id}.sanity.studio",
            "project_id": self.project_id,
            "dataset": self.dataset,
            "api_version": self.api_version,
            "real_time_editing": True,
            "collaborative_editing": True,
            "schema_validation": True,
            "rich_text_editor": "portable_text",
            "media_management": True,
            "preview_integration": True,
            "groq_playground": True
        }

    def get_content_model_schema(self) -> Dict[str, Any]:
        """Get Sanity content schema configuration"""
        return {
            "schema_format": "sanity_schema",
            "schema_types": [
                {
                    "name": "post",
                    "title": "Blog Post",
                    "type": "document",
                    "fields": [
                        {
                            "name": "title",
                            "title": "Title",
                            "type": "string",
                            "validation": "required"
                        },
                        {
                            "name": "slug",
                            "title": "Slug",
                            "type": "slug",
                            "options": {"source": "title", "maxLength": 96},
                            "validation": "required"
                        },
                        {
                            "name": "author",
                            "title": "Author",
                            "type": "reference",
                            "to": [{"type": "author"}]
                        },
                        {
                            "name": "publishedAt",
                            "title": "Published at",
                            "type": "datetime",
                            "validation": "required"
                        },
                        {
                            "name": "excerpt",
                            "title": "Excerpt",
                            "type": "text",
                            "rows": 4
                        },
                        {
                            "name": "mainImage",
                            "title": "Main image",
                            "type": "image",
                            "options": {"hotspot": True},
                            "fields": [
                                {
                                    "name": "alt",
                                    "type": "string",
                                    "title": "Alternative Text"
                                }
                            ]
                        },
                        {
                            "name": "categories",
                            "title": "Categories",
                            "type": "array",
                            "of": [{"type": "reference", "to": {"type": "category"}}]
                        },
                        {
                            "name": "body",
                            "title": "Body",
                            "type": "blockContent"
                        }
                    ],
                    "preview": {
                        "select": {
                            "title": "title",
                            "author": "author.name",
                            "media": "mainImage"
                        },
                        "prepare": {
                            "title": "${title}",
                            "subtitle": "by ${author}"
                        }
                    }
                },
                {
                    "name": "author",
                    "title": "Author",
                    "type": "document",
                    "fields": [
                        {
                            "name": "name",
                            "title": "Name",
                            "type": "string",
                            "validation": "required"
                        },
                        {
                            "name": "slug",
                            "title": "Slug",
                            "type": "slug",
                            "options": {"source": "name", "maxLength": 96}
                        },
                        {
                            "name": "image",
                            "title": "Image",
                            "type": "image",
                            "options": {"hotspot": True}
                        },
                        {
                            "name": "bio",
                            "title": "Bio",
                            "type": "array",
                            "of": [{"type": "block"}]
                        }
                    ]
                },
                {
                    "name": "category",
                    "title": "Category",
                    "type": "document",
                    "fields": [
                        {
                            "name": "title",
                            "title": "Title",
                            "type": "string"
                        },
                        {
                            "name": "description",
                            "title": "Description",
                            "type": "text"
                        }
                    ]
                },
                {
                    "name": "blockContent",
                    "title": "Block Content",
                    "type": "array",
                    "of": [
                        {
                            "type": "block",
                            "styles": [
                                {"title": "Normal", "value": "normal"},
                                {"title": "H1", "value": "h1"},
                                {"title": "H2", "value": "h2"},
                                {"title": "H3", "value": "h3"},
                                {"title": "Quote", "value": "blockquote"}
                            ],
                            "lists": [
                                {"title": "Bullet", "value": "bullet"},
                                {"title": "Numbered", "value": "number"}
                            ],
                            "marks": {
                                "decorators": [
                                    {"title": "Strong", "value": "strong"},
                                    {"title": "Emphasis", "value": "em"}
                                ],
                                "annotations": [
                                    {
                                        "title": "URL",
                                        "name": "link",
                                        "type": "object",
                                        "fields": [
                                            {
                                                "title": "URL",
                                                "name": "href",
                                                "type": "url"
                                            }
                                        ]
                                    }
                                ]
                            }
                        },
                        {
                            "type": "image",
                            "options": {"hotspot": True}
                        }
                    ]
                }
            ]
        }

    def get_build_integration_config(self) -> Dict[str, Any]:
        """Get build integration configuration for different SSG engines"""
        base_env_vars = {
            "SANITY_PROJECT_ID": self.project_id,
            "SANITY_DATASET": self.dataset,
            "SANITY_API_VERSION": self.api_version,
            "SANITY_TOKEN": self.api_token or "${SANITY_TOKEN}",
            "SANITY_WEBHOOK_SECRET": self.webhook_secret or "${SANITY_WEBHOOK_SECRET}"
        }

        return {
            "nextjs": {
                "build_command": "npm run build",
                "output_directory": ".next",
                "install_command": "npm install next-sanity @sanity/image-url",
                "dev_command": "npm run dev",
                "env_vars": {
                    **base_env_vars,
                    "NEXT_PUBLIC_SANITY_PROJECT_ID": self.project_id,
                    "NEXT_PUBLIC_SANITY_DATASET": self.dataset
                },
                "features": {
                    "isr": True,  # Incremental Static Regeneration
                    "preview_mode": True,
                    "real_time_updates": True
                }
            },
            "astro": {
                "build_command": "npm run build",
                "output_directory": "dist",
                "install_command": "npm install @sanity/client @sanity/image-url",
                "dev_command": "npm run dev",
                "env_vars": {
                    **base_env_vars,
                    "PUBLIC_SANITY_PROJECT_ID": self.project_id,
                    "PUBLIC_SANITY_DATASET": self.dataset
                },
                "features": {
                    "static_generation": True,
                    "component_islands": True,
                    "dynamic_imports": True
                }
            },
            "gatsby": {
                "build_command": "npm run build",
                "output_directory": "public",
                "install_command": "npm install gatsby-source-sanity @sanity/image-url",
                "dev_command": "npm run develop",
                "env_vars": {
                    **base_env_vars,
                    "GATSBY_SANITY_PROJECT_ID": self.project_id,
                    "GATSBY_SANITY_DATASET": self.dataset
                },
                "features": {
                    "graphql_integration": True,
                    "incremental_builds": True,
                    "source_plugin": "gatsby-source-sanity"
                }
            },
            "eleventy": {
                "build_command": "npm run build",
                "output_directory": "_site",
                "install_command": "npm install @sanity/client",
                "dev_command": "npm run serve",
                "env_vars": base_env_vars,
                "features": {
                    "data_fetching": True,
                    "build_time_queries": True
                }
            }
        }

    def get_groq_queries(self) -> Dict[str, str]:
        """Get common GROQ queries for content retrieval"""
        return {
            "all_posts": "*[_type == 'post'] | order(publishedAt desc)",
            "post_by_slug": "*[_type == 'post' && slug.current == $slug][0]",
            "posts_with_author": """
                *[_type == 'post'] | order(publishedAt desc) {
                    _id,
                    title,
                    slug,
                    publishedAt,
                    excerpt,
                    mainImage,
                    author->{name, slug, image},
                    categories[]->{title, _id}
                }
            """,
            "featured_posts": "*[_type == 'post' && featured == true] | order(publishedAt desc)[0...3]",
            "posts_by_category": "*[_type == 'post' && $category in categories[]->slug.current]",
            "all_authors": "*[_type == 'author'] | order(name asc)",
            "author_with_posts": """
                *[_type == 'author' && slug.current == $slug][0] {
                    ...,
                    "posts": *[_type == 'post' && references(^._id)] | order(publishedAt desc)
                }
            """
        }

    def estimate_monthly_cost(self, content_volume: str = "medium") -> CMSCostEstimate:
        """Estimate monthly costs for Sanity CMS"""

        # Volume-based cost calculation
        volume_tiers = {
            "small": {
                "api_requests": 5000,   # < 5k requests/month
                "users": 2,
                "base_cost": 0          # Free tier
            },
            "medium": {
                "api_requests": 50000,  # 5k-50k requests/month
                "users": 5,
                "base_cost": 99         # Growth plan
            },
            "large": {
                "api_requests": 200000, # 50k-200k requests/month
                "users": 15,
                "base_cost": 199        # Business plan
            },
            "enterprise": {
                "api_requests": 1000000, # > 200k requests/month
                "users": 50,
                "base_cost": 499        # Enterprise plan
            }
        }

        tier = volume_tiers.get(content_volume, volume_tiers["medium"])
        base_cost = tier["base_cost"]

        # Additional feature costs
        additional_costs = {
            "cdn_bandwidth": 5 if content_volume in ["large", "enterprise"] else 0,
            "image_transformations": 10 if content_volume in ["large", "enterprise"] else 0,
            "advanced_workflows": 20 if content_volume == "enterprise" else 0
        }

        total_additional = sum(additional_costs.values())

        return CMSCostEstimate(
            provider="sanity",
            base_monthly_fee=base_cost,
            content_volume=content_volume,
            additional_features=additional_costs,
            total_estimated=base_cost + total_additional
        )

    async def create_user(self, user_data: Dict[str, Any]) -> CMSUser:
        """Create a new user in Sanity CMS"""
        return CMSUser(
            id=user_data.get("sanity_user_id", ""),
            email=user_data["email"],
            name=user_data.get("name", ""),
            role=user_data.get("role", "editor"),
            permissions=self._get_default_permissions(user_data.get("role", "editor")),
            last_login=datetime.now(),
            created_at=datetime.now()
        )

    async def get_content_collections(self) -> List[ContentCollection]:
        """Get content collections from Sanity CMS"""
        schema = self.get_content_model_schema()
        collections = []

        for schema_type in schema["schema_types"]:
            if schema_type["type"] == "document":
                collections.append(ContentCollection(
                    id=schema_type["name"],
                    name=schema_type["title"],
                    slug=schema_type["name"],
                    content_type="structured",
                    fields=schema_type["fields"],
                    item_count=await self._get_document_count(schema_type["name"]),
                    last_modified=datetime.now()
                ))

        return collections

    async def upload_media(self, file_data: bytes, filename: str, metadata: Dict[str, Any]) -> MediaAsset:
        """Upload media asset to Sanity CMS"""
        # In real implementation, this would use Sanity's asset API
        asset_id = f"image-{hash(filename)}"

        return MediaAsset(
            id=asset_id,
            filename=filename,
            url=f"https://cdn.sanity.io/images/{self.project_id}/{self.dataset}/{asset_id}",
            content_type=metadata.get("content_type", ""),
            size=len(file_data),
            alt_text=metadata.get("alt_text", ""),
            created_at=datetime.now()
        )

    async def get_analytics(self) -> CMSMetrics:
        """Get Sanity CMS analytics and metrics"""
        return CMSMetrics(
            total_content_items=await self._get_total_document_count(),
            monthly_edits=await self._get_monthly_edit_count(),
            active_users=await self._get_active_user_count(),
            storage_usage=await self._get_storage_usage(),
            api_requests=await self._get_api_request_count(),
            last_updated=datetime.now()
        )

    def _validate_sanity_config(self) -> None:
        """Validate Sanity CMS specific configuration"""
        required_fields = ["project_id"]

        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Sanity CMS configuration missing required field: {field}")

        # Validate project ID format
        project_id = self.config["project_id"]
        if not isinstance(project_id, str) or len(project_id) < 8:
            raise ValueError("Sanity project_id must be a valid string (8+ characters)")

    def _get_api_base_url(self) -> str:
        """Get Sanity API base URL"""
        if self.use_cdn:
            return f"https://{self.project_id}.apicdn.sanity.io/v{self.api_version}/data/query/{self.dataset}"
        else:
            return f"https://{self.project_id}.api.sanity.io/v{self.api_version}/data/query/{self.dataset}"

    def _get_cdn_base_url(self) -> str:
        """Get Sanity CDN base URL for assets"""
        return f"https://cdn.sanity.io/images/{self.project_id}/{self.dataset}"

    def _get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions for user role"""
        permissions = {
            "admin": ["read", "write", "delete", "publish", "manage_users", "manage_schema", "manage_tokens"],
            "editor": ["read", "write", "publish"],
            "author": ["read", "write"],
            "reviewer": ["read", "comment"],
            "viewer": ["read"]
        }
        return permissions.get(role, permissions["viewer"])

    async def _get_document_count(self, document_type: str) -> int:
        """Get document count for a specific type"""
        # This would query Sanity API: count(*[_type == $document_type])
        return 0  # Placeholder

    async def _get_total_document_count(self) -> int:
        """Get total document count across all types"""
        return 0  # Placeholder

    async def _get_monthly_edit_count(self) -> int:
        """Get monthly edit count from Sanity analytics"""
        return 0  # Placeholder

    async def _get_active_user_count(self) -> int:
        """Get active user count"""
        return len(self.config.get("admin_users", []))

    async def _get_storage_usage(self) -> int:
        """Get storage usage in bytes"""
        return 0  # Placeholder - would query Sanity project usage API

    async def _get_api_request_count(self) -> int:
        """Get API request count"""
        return 0  # Placeholder

    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables required by Sanity CMS"""
        return {
            "SANITY_PROJECT_ID": self.project_id,
            "SANITY_DATASET": self.dataset,
            "SANITY_API_VERSION": self.api_version,
            "SANITY_TOKEN": self.api_token or "",
            "SANITY_USE_CDN": str(self.use_cdn).lower()
        }

    def setup_infrastructure(self, stack) -> None:
        """Set up AWS infrastructure specific to Sanity CMS"""
        # Infrastructure setup is handled by SanityCMSTierStack
        pass

    def get_configuration_metadata(self) -> Dict[str, Any]:
        """Get CMS configuration metadata for client documentation"""
        return {
            "provider": "sanity",
            "cms_type": "api_based",
            "auth_method": "api_key",
            "monthly_cost_range": [0, 199],
            "setup_complexity": "medium_to_high",
            "features": [
                "structured_content",
                "groq_querying",
                "real_time_apis",
                "content_validation",
                "advanced_media",
                "webhook_automation"
            ],
            "supported_ssg_engines": ["nextjs", "astro", "gatsby", "eleventy"],
            "required_config": {
                "project_id": "Sanity project identifier",
                "dataset": "Sanity dataset name (default: production)",
                "api_version": "Sanity API version (default: 2023-05-03)"
            },
            "optional_config": {
                "api_token": "Sanity API token for server-side operations",
                "webhook_secret": "Secret for webhook validation",
                "use_cdn": "Whether to use Sanity's CDN (default: true)"
            }
        }

    def get_admin_config(self) -> Dict[str, Any]:
        """Get Sanity Studio admin panel configuration"""
        return self.get_admin_interface_config()

    def validate_configuration(self) -> bool:
        """Validate that the Sanity CMS configuration is complete and correct"""
        try:
            self._validate_sanity_config()
            return True
        except ValueError:
            return False