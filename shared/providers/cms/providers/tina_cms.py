"""
Tina CMS Provider Implementation

Provides git-based visual editing through Tina CMS, combining the power of
git workflows with user-friendly visual editing capabilities.

Key Features:
- Visual editing with real-time preview
- Git-based storage with version history
- GitHub integration and authentication
- Support for Next.js, Astro, and Gatsby
- Optional Tina Cloud integration for enhanced features
- Rich media management with optimized delivery

Architecture:
- Hybrid CMS: Git storage + visual editing interface
- React-based admin interface
- GraphQL API for content queries
- Real-time collaboration (with Tina Cloud)
- Branch-based editing workflows

Target Market:
- Content creators wanting visual editing
- Teams needing collaboration features
- Developers wanting git workflow control
- Agencies managing multiple client sites

Pricing:
- Self-hosted: Free (git-only)
- Tina Cloud: $0-50/month based on usage
- Total monthly cost: $60-125 including hosting
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from shared.providers.cms.base_provider import CMSProvider, CMSType, CMSAuthMethod, CMSFeatures


class TinaCMSProvider(CMSProvider):
    """
    Tina CMS provider implementation for visual git-based content management.

    Provides visual editing capabilities while maintaining git-based storage,
    making it ideal for teams that want user-friendly editing without
    sacrificing developer workflow control.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Tina CMS provider.

        Args:
            config: Configuration dictionary containing:
                - repository: GitHub repository name
                - repository_owner: GitHub repository owner
                - branch: Git branch (default: main)
                - content_path: Content directory path
                - media_path: Media assets path
                - tina_token: Optional Tina Cloud token
                - tina_client_id: Optional Tina Cloud client ID
        """
        super().__init__("tina", config)

        # Validate required Tina configuration
        self._validate_tina_config()

        # Git-based storage settings
        self.repository = config["repository"]
        self.repository_owner = config["repository_owner"]
        self.branch = config.get("branch", "main")
        self.content_path = config.get("content_path", "content")
        self.media_path = config.get("media_path", "public/images")

        # Tina Cloud settings (optional)
        self.tina_token = config.get("tina_token")
        self.tina_client_id = config.get("tina_client_id")
        self.is_cloud_enabled = bool(self.tina_token and self.tina_client_id)

        # Initialize GraphQL API settings
        self.graphql_endpoint = self._get_graphql_endpoint()

    @property
    def provider_name(self) -> str:
        return "tina"

    def get_cms_type(self) -> CMSType:
        return CMSType.HYBRID

    def get_auth_method(self) -> CMSAuthMethod:
        return CMSAuthMethod.GITHUB_OAUTH

    def get_supported_features(self) -> List[str]:
        features = [
            CMSFeatures.VISUAL_EDITOR,
            CMSFeatures.MARKDOWN_EDITOR,
            CMSFeatures.MEDIA_MANAGEMENT,
            CMSFeatures.PREVIEW_MODE,
            CMSFeatures.API_ACCESS,
            CMSFeatures.WEBHOOK_SUPPORT,
            CMSFeatures.REVISION_HISTORY,
            CMSFeatures.CUSTOM_FIELDS
        ]

        # Add cloud-specific features
        if self.is_cloud_enabled:
            features.extend([
                CMSFeatures.REAL_TIME_COLLABORATION,
                CMSFeatures.WORKFLOW_MANAGEMENT,
                CMSFeatures.ROLE_BASED_ACCESS
            ])

        return features

    def get_supported_ssg_engines(self) -> List[str]:
        """Tina CMS works best with React-based SSGs"""
        return ["nextjs", "astro", "gatsby"]

    def get_admin_interface_config(self) -> Dict[str, Any]:
        """Get Tina CMS admin interface configuration"""
        config = {
            "interface_type": "visual_editor",
            "admin_path": "/admin",
            "editor_path": "/admin/index.html",
            "api_path": "/api/tina/graphql",
            "preview_mode": True,
            "real_time_preview": True,
            "git_integration": True,
            "branch_switching": True,
            "media_library": True,
            "collaborative_editing": self.is_cloud_enabled
        }

        if self.is_cloud_enabled:
            config.update({
                "cloud_integration": True,
                "tina_client_id": self.tina_client_id,
                "real_time_sync": True,
                "team_collaboration": True
            })

        return config

    def get_content_model_schema(self) -> Dict[str, Any]:
        """Get Tina CMS content model schema"""
        return {
            "schema_format": "tina_schema",
            "collections": [
                {
                    "name": "posts",
                    "label": "Blog Posts",
                    "path": f"{self.content_path}/posts",
                    "format": "mdx",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "date", "type": "datetime", "required": True},
                        {"name": "author", "type": "string"},
                        {"name": "excerpt", "type": "rich-text"},
                        {"name": "featured_image", "type": "image"},
                        {"name": "tags", "type": "string", "list": True},
                        {"name": "body", "type": "rich-text", "isBody": True}
                    ]
                },
                {
                    "name": "pages",
                    "label": "Pages",
                    "path": f"{self.content_path}/pages",
                    "format": "mdx",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "slug", "type": "string", "required": True},
                        {"name": "description", "type": "string"},
                        {"name": "body", "type": "rich-text", "isBody": True}
                    ]
                }
            ],
            "media": {
                "tina": {
                    "mediaRoot": self.media_path,
                    "publicFolder": "public"
                }
            }
        }

    def get_build_integration_config(self) -> Dict[str, Any]:
        """Get build integration configuration for different SSG engines"""
        return {
            "nextjs": {
                "build_command": "npm run build",
                "output_directory": ".next",
                "install_command": "npm install @tinacms/cli tinacms",
                "dev_command": "npm run dev",
                "tina_init": "npx @tinacms/cli init",
                "schema_file": "tina/config.ts",
                "env_vars": {
                    "NEXT_PUBLIC_TINA_CLIENT_ID": self.tina_client_id,
                    "TINA_TOKEN": self.tina_token,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                }
            },
            "astro": {
                "build_command": "npm run build",
                "output_directory": "dist",
                "install_command": "npm install @tinacms/cli tinacms @astrojs/react",
                "dev_command": "npm run dev",
                "tina_init": "npx @tinacms/cli init",
                "schema_file": "tina/config.ts",
                "env_vars": {
                    "PUBLIC_TINA_CLIENT_ID": self.tina_client_id,
                    "TINA_TOKEN": self.tina_token,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                }
            },
            "gatsby": {
                "build_command": "npm run build",
                "output_directory": "public",
                "install_command": "npm install @tinacms/cli tinacms gatsby-plugin-tinacms",
                "dev_command": "npm run develop",
                "tina_init": "npx @tinacms/cli init",
                "schema_file": "tina/config.ts",
                "env_vars": {
                    "GATSBY_TINA_CLIENT_ID": self.tina_client_id,
                    "TINA_TOKEN": self.tina_token,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                }
            }
        }

    def estimate_monthly_cost(self, content_volume: str = "medium") -> Dict[str, Any]:
        """Estimate monthly costs for Tina CMS"""

        # Volume-based cost calculation
        volume_multipliers = {
            "small": 0.5,    # < 100 pages
            "medium": 1.0,   # 100-1000 pages
            "large": 1.8,    # 1000-5000 pages
            "enterprise": 3.0 # > 5000 pages
        }

        multiplier = volume_multipliers.get(content_volume, 1.0)

        if self.is_cloud_enabled:
            # Tina Cloud pricing
            base_cost = 29 * multiplier  # Tina Cloud starts at $29/month

            # Additional costs based on usage
            collaboration_cost = 10 if content_volume in ["large", "enterprise"] else 0
            advanced_features = 15 if multiplier > 1.5 else 0

            total_cms_cost = base_cost + collaboration_cost + advanced_features
        else:
            # Self-hosted Tina (free CMS, but consider GitHub costs)
            total_cms_cost = 0

        return {
            "provider": "tina",
            "base_monthly_fee": total_cms_cost,
            "content_volume": content_volume,
            "additional_features": {
                "visual_editing": 0,  # Included
                "git_integration": 0,  # Included
                "real_time_collaboration": 0 if not self.is_cloud_enabled else 10,
                "advanced_media": 0 if not self.is_cloud_enabled else 5
            },
            "total_estimated": total_cms_cost
        }

    def get_environment_variables(self) -> Dict[str, str]:
        """Get Tina CMS environment variables"""
        base_vars = {
            "CMS_PROVIDER": "tina",
            "CMS_TYPE": "hybrid",
            "GITHUB_REPO": self.repository,
            "GITHUB_OWNER": self.repository_owner,
            "BRANCH": self.branch,
            "CONTENT_PATH": self.content_path,
            "MEDIA_PATH": self.media_path
        }

        if self.is_cloud_enabled:
            base_vars.update({
                "TINA_CLIENT_ID": self.tina_client_id,
                "TINA_TOKEN": self.tina_token,
                "TINA_CLOUD_ENABLED": "true"
            })
        else:
            base_vars["TINA_CLOUD_ENABLED"] = "false"

        return base_vars

    def setup_infrastructure(self, stack) -> None:
        """Set up Tina CMS infrastructure"""
        # Tina CMS is primarily client-side, minimal AWS infrastructure needed
        pass

    def get_configuration_metadata(self) -> Dict[str, Any]:
        """Get Tina CMS configuration metadata"""
        return {
            "provider": "tina",
            "cms_type": "hybrid",
            "monthly_cost_range": [0, 125],
            "setup_complexity": "medium",
            "estimated_setup_hours": 4.0,
            "features": self.get_supported_features(),
            "strengths": [
                "Visual editing with git workflow",
                "Real-time preview",
                "Developer-friendly",
                "Flexible content schema",
                "Optional cloud features"
            ],
            "limitations": [
                "Requires React/JavaScript knowledge",
                "Limited to React-based SSGs",
                "Cloud features require subscription"
            ],
            "ideal_for": [
                "Developer teams wanting visual editing",
                "Content creators needing real-time preview",
                "Teams wanting git-based workflow with ease of use",
                "Projects requiring custom content fields"
            ],
            "documentation_links": {
                "official_docs": "https://tina.io/docs/",
                "setup_guide": "https://tina.io/docs/setup-overview/",
                "examples": "https://tina.io/examples/"
            }
        }

    def _validate_tina_config(self) -> None:
        """Validate Tina CMS specific configuration"""
        required_fields = ["repository", "repository_owner"]

        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Tina CMS configuration missing required field: {field}")

        # If Tina Cloud settings are provided, validate both are present
        tina_token = self.config.get("tina_token")
        tina_client_id = self.config.get("tina_client_id")

        if (tina_token and not tina_client_id) or (tina_client_id and not tina_token):
            raise ValueError("Both tina_token and tina_client_id must be provided for Tina Cloud integration")

    def get_admin_config(self) -> Dict[str, Any]:
        """Get Tina CMS admin configuration"""
        return self.get_admin_interface_config()

    def validate_configuration(self) -> bool:
        """Validate Tina CMS configuration"""
        self._validate_tina_config()
        return True

    def _get_graphql_endpoint(self) -> str:
        """Get GraphQL API endpoint"""
        if self.is_cloud_enabled:
            return f"https://content.tinajs.io/content/{self.tina_client_id}/github/{self.repository_owner}/{self.repository}"
        else:
            return "/api/tina/graphql"  # Local development endpoint