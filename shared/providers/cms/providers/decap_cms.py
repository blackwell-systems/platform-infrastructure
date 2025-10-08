"""
Decap CMS Provider Implementation

Decap CMS (formerly Netlify CMS) is a git-based content management system
that provides a web-based admin interface for editing markdown files stored
in a Git repository. It's ideal for static site generators and offers
zero-cost content management for developers.

Key Features:
- Git-based workflow with version control
- GitHub OAuth integration
- Markdown editing with live preview
- Media management with git-lfs support
- Editorial workflow with publish/draft states
- Custom field types and validation

Architecture:
- Content stored as markdown files in git repository
- Admin interface served as static files
- Authentication via GitHub OAuth or Netlify Identity
- Build triggers via git webhooks
"""

from typing import Dict, Any, List, Optional
from aws_cdk import aws_s3 as s3, aws_cloudfront as cloudfront

from ..base_provider import CMSProvider, CMSType, CMSAuthMethod, CMSFeatures
from ..api_client import CMSAPIClient, AuthenticationManager


class DecapCMSProvider(CMSProvider):
    """
    Decap CMS provider implementation.

    Provides git-based content management with GitHub integration,
    ideal for static site generators and developer-friendly workflows.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("decap", config)

    def get_cms_type(self) -> CMSType:
        """Decap CMS is git-based (files stored in repository)"""
        return CMSType.GIT_BASED

    def get_auth_method(self) -> CMSAuthMethod:
        """Decap CMS primarily uses GitHub OAuth for authentication"""
        auth_method = self.config.get("auth_method", "github_oauth")
        if auth_method == "netlify_identity":
            return CMSAuthMethod.NETLIFY_IDENTITY
        return CMSAuthMethod.GITHUB_OAUTH

    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get environment variables for Decap CMS integration.

        Returns variables for:
        - GitHub OAuth application configuration
        - Content repository settings
        - Admin interface configuration
        """
        base_vars = {
            "CMS_PROVIDER": "decap",
            "CMS_TYPE": "git_based",
            "CONTENT_PATH": self.config.get("content_path", "content"),
            "MEDIA_FOLDER": self.config.get("media_path", "static/images"),
            "PUBLIC_FOLDER": self.config.get("public_path", "static"),
            "BRANCH": self.config.get("branch", "main"),
        }

        # GitHub OAuth configuration
        if self.get_auth_method() == CMSAuthMethod.GITHUB_OAUTH:
            base_vars.update({
                "GITHUB_CLIENT_ID": "${GITHUB_CLIENT_ID}",
                "GITHUB_CLIENT_SECRET": "${GITHUB_CLIENT_SECRET}",
                "GITHUB_REPO": self.config.get("repository", "${GITHUB_REPO}"),
                "GITHUB_OWNER": self.config.get("repository_owner", "${GITHUB_OWNER}"),
            })

        # Netlify Identity configuration
        elif self.get_auth_method() == CMSAuthMethod.NETLIFY_IDENTITY:
            base_vars.update({
                "NETLIFY_SITE_ID": "${NETLIFY_SITE_ID}",
                "NETLIFY_IDENTITY_URL": "${NETLIFY_IDENTITY_URL}",
            })

        return base_vars

    def setup_infrastructure(self, stack) -> None:
        """
        Set up AWS infrastructure for Decap CMS.

        For git-based CMS, infrastructure is minimal:
        - Admin interface served from S3/CloudFront
        - Optional webhook processing for build triggers
        """
        # Create admin interface configuration file
        admin_config = self._generate_admin_config()

        # For git-based CMS, we mainly need to serve the admin interface
        # The actual content management happens in the git repository

        # Store admin configuration in S3 for serving
        if hasattr(stack, 'content_bucket'):
            # Add admin config as a deployment asset
            stack.admin_config = admin_config

    def get_configuration_metadata(self) -> Dict[str, Any]:
        """
        Get Decap CMS configuration metadata.

        Returns comprehensive information about costs, setup complexity,
        and supported features for client documentation.
        """
        return {
            "provider": "decap",
            "cms_type": "git_based",
            "monthly_cost_range": [0, 0],  # Free to use
            "setup_complexity": "low",
            "estimated_setup_hours": 2,
            "ongoing_maintenance": "low",

            "features": [
                CMSFeatures.MARKDOWN_EDITOR,
                CMSFeatures.MEDIA_MANAGEMENT,
                CMSFeatures.WORKFLOW_MANAGEMENT,
                CMSFeatures.CUSTOM_FIELDS,
                CMSFeatures.PREVIEW_MODE,
                CMSFeatures.REVISION_HISTORY,  # Via git
                CMSFeatures.ROLE_BASED_ACCESS,
                CMSFeatures.SEO_TOOLS,
            ],

            "strengths": [
                "Completely free to use",
                "Git-based version control",
                "Developer-friendly workflow",
                "No vendor lock-in",
                "Integrates with any static site generator",
                "Editorial workflow with draft/publish states"
            ],

            "limitations": [
                "Requires technical setup",
                "No real-time collaboration",
                "Limited to markdown/file-based content",
                "Requires GitHub account for contributors",
                "No built-in image optimization"
            ],

            "ideal_for": [
                "Developer-managed sites",
                "Blog and documentation sites",
                "Small to medium content teams",
                "Budget-conscious projects",
                "Version-controlled content workflows"
            ],

            "documentation_links": {
                "official_docs": "https://decapcms.org/docs/",
                "quick_start": "https://decapcms.org/docs/quick-start/",
                "configuration": "https://decapcms.org/docs/configuration-options/",
                "authentication": "https://decapcms.org/docs/authentication-backends/"
            }
        }

    def get_admin_config(self) -> Dict[str, Any]:
        """
        Get Decap CMS admin panel configuration.

        Returns the admin interface configuration including
        content collections, fields, and editor settings.
        """
        return {
            "admin_path": "/admin",
            "config_file": "admin/config.yml",
            "auth_required": True,
            "supports_preview": True,
            "editorial_workflow": self.config.get("editorial_workflow", True),
            "content_collections": self._get_content_collections(),
            "media_settings": {
                "media_folder": self.config.get("media_path", "static/images"),
                "public_folder": self.config.get("public_path", "/images"),
                "media_library": {
                    "name": "uploadcare",
                    "config": {"publicKey": "${UPLOADCARE_PUBLIC_KEY}"}
                } if self.config.get("use_uploadcare") else None
            }
        }

    def validate_configuration(self) -> bool:
        """
        Validate Decap CMS configuration.

        Checks required settings for git-based CMS operation.
        """
        required_fields = ["repository", "repository_owner"]

        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Decap CMS requires '{field}' in configuration")

        # Validate authentication method
        auth_method = self.config.get("auth_method", "github_oauth")
        if auth_method not in ["github_oauth", "netlify_identity"]:
            raise ValueError(f"Unsupported auth method: {auth_method}")

        # Validate content path
        content_path = self.config.get("content_path", "content")
        if not content_path or content_path.startswith("/"):
            raise ValueError("Content path must be relative to repository root")

        return True

    def get_ssg_compatibility(self) -> List[str]:
        """
        Get SSG engines compatible with Decap CMS.

        Decap CMS works with any SSG that can process markdown files.
        """
        return [
            "eleventy", "hugo", "astro", "gatsby", "nextjs",
            "nuxt", "jekyll", "hexo", "gridsome", "vuepress"
        ]

    def get_required_dependencies(self, ssg_engine: str) -> List[str]:
        """
        Get required dependencies for SSG integration.

        For git-based CMS, dependencies are minimal and mostly
        related to markdown processing and build optimization.
        """
        base_deps = []

        # SSG-specific dependencies
        ssg_deps = {
            "eleventy": ["@11ty/eleventy", "markdown-it"],
            "astro": ["@astrojs/markdown-remark", "remark", "rehype"],
            "gatsby": ["gatsby-transformer-remark", "gatsby-source-filesystem"],
            "nextjs": ["next-mdx-remote", "gray-matter"],
            "nuxt": ["@nuxt/content", "@nuxtjs/markdownit"],
            "hugo": [],  # Hugo has built-in markdown support
            "jekyll": []  # Jekyll has built-in markdown support
        }

        return base_deps + ssg_deps.get(ssg_engine, [])

    def estimate_monthly_cost(self, content_volume: str = "small") -> Dict[str, Any]:
        """
        Estimate monthly costs for Decap CMS.

        Decap CMS itself is free, costs come from hosting and optional services.
        """
        # Base Decap CMS is free
        base_cost = 0

        # Optional service costs
        optional_costs = 0

        # Uploadcare media management (if enabled)
        if self.config.get("use_uploadcare"):
            uploadcare_costs = {
                "small": 25,    # Up to 1GB storage, 10GB CDN
                "medium": 49,   # Up to 3GB storage, 25GB CDN
                "large": 99     # Up to 10GB storage, 100GB CDN
            }
            optional_costs += uploadcare_costs.get(content_volume, 25)

        return {
            "base_monthly_fee": base_cost,
            "optional_services": optional_costs,
            "total_estimated": base_cost + optional_costs,
            "content_volume": content_volume,
            "cost_breakdown": {
                "decap_cms": 0,  # Always free
                "uploadcare": optional_costs if self.config.get("use_uploadcare") else 0,
                "github": 0,     # Free for public repos, varies for private
                "hosting": "Included in platform"
            }
        }

    def get_integration_guide(self) -> Dict[str, Any]:
        """
        Get step-by-step integration guide for Decap CMS.
        """
        return {
            "title": "Decap CMS Integration Guide",
            "description": "Set up git-based content management with GitHub integration",

            "prerequisites": [
                "GitHub account with repository access",
                "Static site generator configured",
                "GitHub OAuth app created (for authentication)"
            ],

            "steps": [
                {
                    "step": 1,
                    "title": "Create GitHub OAuth App",
                    "description": "Set up GitHub OAuth for admin authentication",
                    "action": "Create OAuth app in GitHub Settings > Developer settings",
                    "details": {
                        "homepage_url": "https://your-site.com",
                        "authorization_callback_url": "https://your-site.com/admin/",
                        "note_client_secret": "Save Client ID and Secret for environment variables"
                    }
                },
                {
                    "step": 2,
                    "title": "Configure Content Collections",
                    "description": "Define content types and field schemas",
                    "action": "Set up collections in admin configuration",
                    "config_example": self._get_sample_admin_config()
                },
                {
                    "step": 3,
                    "title": "Deploy Admin Interface",
                    "description": "Add admin interface to your static site",
                    "action": "Create admin/index.html and admin/config.yml files",
                    "files_to_create": [
                        {"path": "admin/index.html", "purpose": "Admin interface entry point"},
                        {"path": "admin/config.yml", "purpose": "CMS configuration"}
                    ]
                },
                {
                    "step": 4,
                    "title": "Test Content Management",
                    "description": "Verify admin access and content creation",
                    "action": "Access /admin, authenticate, and create test content",
                    "verification": [
                        "Can access admin interface",
                        "Authentication works with GitHub",
                        "Can create and edit content",
                        "Changes trigger site rebuilds"
                    ]
                }
            ],

            "requirements": {
                "technical_skill": "Low to Medium",
                "estimated_setup_time": "2-3 hours",
                "ongoing_maintenance": "Minimal",
                "team_training": "30 minutes for content editors"
            },

            "troubleshooting": {
                "common_issues": [
                    {
                        "issue": "OAuth authentication fails",
                        "solution": "Check callback URL matches GitHub OAuth app settings"
                    },
                    {
                        "issue": "Admin interface shows 404",
                        "solution": "Ensure admin/index.html is deployed and accessible"
                    },
                    {
                        "issue": "Content changes don't trigger builds",
                        "solution": "Verify GitHub webhook is configured for repository"
                    }
                ]
            }
        }

    def _generate_admin_config(self) -> Dict[str, Any]:
        """Generate the admin configuration for Decap CMS"""
        return {
            "backend": {
                "name": "git-gateway" if self.get_auth_method() == CMSAuthMethod.NETLIFY_IDENTITY else "github",
                "repo": f"{self.config.get('repository_owner')}/{self.config.get('repository')}",
                "branch": self.config.get("branch", "main")
            },
            "media_folder": self.config.get("media_path", "static/images"),
            "public_folder": self.config.get("public_path", "/images"),
            "collections": self._get_content_collections()
        }

    def _get_content_collections(self) -> List[Dict[str, Any]]:
        """Get content collection definitions for Decap CMS"""
        return [
            {
                "name": "posts",
                "label": "Blog Posts",
                "folder": f"{self.config.get('content_path', 'content')}/posts",
                "create": True,
                "slug": "{{year}}-{{month}}-{{day}}-{{slug}}",
                "fields": [
                    {"label": "Title", "name": "title", "widget": "string"},
                    {"label": "Date", "name": "date", "widget": "datetime"},
                    {"label": "Description", "name": "description", "widget": "text"},
                    {"label": "Featured Image", "name": "image", "widget": "image", "required": False},
                    {"label": "Tags", "name": "tags", "widget": "list", "required": False},
                    {"label": "Body", "name": "body", "widget": "markdown"}
                ]
            },
            {
                "name": "pages",
                "label": "Pages",
                "folder": f"{self.config.get('content_path', 'content')}/pages",
                "create": True,
                "slug": "{{slug}}",
                "fields": [
                    {"label": "Title", "name": "title", "widget": "string"},
                    {"label": "Permalink", "name": "permalink", "widget": "string", "required": False},
                    {"label": "Description", "name": "description", "widget": "text"},
                    {"label": "Body", "name": "body", "widget": "markdown"}
                ]
            }
        ]

    def _get_sample_admin_config(self) -> str:
        """Get sample admin configuration YAML"""
        return """
backend:
  name: github
  repo: your-username/your-repo
  branch: main

media_folder: static/images
public_folder: /images

collections:
  - name: posts
    label: Blog Posts
    folder: content/posts
    create: true
    slug: '{{year}}-{{month}}-{{day}}-{{slug}}'
    fields:
      - {label: Title, name: title, widget: string}
      - {label: Date, name: date, widget: datetime}
      - {label: Description, name: description, widget: text}
      - {label: Body, name: body, widget: markdown}
        """


class DecapCMSAPIClient(CMSAPIClient):
    """
    API client for Decap CMS.

    Note: Decap CMS is git-based, so this client primarily interacts
    with GitHub API for repository operations rather than a dedicated CMS API.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("decap", config)

    def _create_auth_manager(self) -> AuthenticationManager:
        """Create GitHub API authentication manager"""
        from ..api_client import AuthManagerFactory
        return AuthManagerFactory.create_auth_manager(CMSAuthMethod.API_KEY, {
            "api_key": self.config.get("github_token"),
            "auth_header": "Authorization",
            "auth_format": "token {}"
        })

    def _get_base_url(self) -> str:
        """Get GitHub API base URL"""
        return "https://api.github.com"

    async def get_content_types(self) -> List:
        """Get content types (collections) from repository structure"""
        # For git-based CMS, content types are determined by folder structure
        # This would implement GitHub API calls to explore repository structure
        pass

    async def get_content(self, query) -> Any:
        """Get content from git repository via GitHub API"""
        # This would implement fetching markdown files from GitHub
        pass

    async def get_content_item(self, content_type: str, item_id: str) -> Any:
        """Get specific content item from repository"""
        pass

    async def create_content(self, content) -> Any:
        """Create content by committing new file to repository"""
        pass

    async def update_content(self, content) -> Any:
        """Update content by committing changes to repository"""
        pass

    async def delete_content(self, content_type: str, item_id: str) -> bool:
        """Delete content by removing file from repository"""
        pass

    async def upload_media(self, file_path: str, metadata: Dict[str, Any]) -> Any:
        """Upload media file to repository"""
        pass

    async def get_media_assets(self, folder: Optional[str] = None) -> List:
        """Get media assets from repository"""
        pass