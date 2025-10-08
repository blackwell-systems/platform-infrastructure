"""
CMS Configuration Models

Pydantic models for CMS provider configuration within the client configuration system.
These models integrate with the CMS provider architecture to provide type-safe
configuration for content management systems.

Key Models:
- CMSConfig: Base CMS configuration with provider selection
- CMSProviderSettings: Provider-specific configuration settings
- ContentManagementConfig: Content structure and workflow settings

Usage:
    from models.cms_config import CMSConfig

    cms_config = CMSConfig(
        provider="decap",
        auth_method="github_oauth",
        admin_users=["admin@example.com"],
        content_settings={
            "content_path": "content",
            "media_path": "static/images"
        }
    )
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum

from shared.providers.cms.base_provider import CMSType, CMSAuthMethod


class CMSConfig(BaseModel):
    """
    CMS configuration for client sites.

    Integrates with the CMS provider factory system to provide
    type-safe configuration for content management systems.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "provider": "decap",
                    "auth_method": "github_oauth",
                    "admin_users": ["admin@example.com"],
                    "content_settings": {
                        "content_path": "content",
                        "media_path": "static/images",
                        "branch": "main"
                    }
                },
                {
                    "provider": "sanity",
                    "auth_method": "api_key",
                    "admin_users": ["editor@company.com"],
                    "content_settings": {
                        "project_id": "abc123",
                        "dataset": "production",
                        "api_version": "2023-01-01"
                    }
                }
            ]
        }
    )

    # CMS Provider Selection
    provider: str = Field(
        ...,
        description="CMS provider name (decap, tina, sanity, contentful, etc.)"
    )

    cms_type: Optional[CMSType] = Field(
        default=None,
        description="CMS architecture type (auto-detected from provider if not specified)"
    )

    auth_method: Optional[CMSAuthMethod] = Field(
        default=None,
        description="Authentication method (auto-detected from provider if not specified)"
    )

    # Access Control
    admin_users: List[str] = Field(
        default_factory=list,
        description="List of admin user emails with full CMS access"
    )

    editor_users: List[str] = Field(
        default_factory=list,
        description="List of editor user emails with content editing access"
    )

    # Content Management Settings
    content_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific content management settings"
    )

    # Editorial Workflow
    enable_editorial_workflow: bool = Field(
        default=True,
        description="Enable draft/review/publish workflow"
    )

    enable_media_management: bool = Field(
        default=True,
        description="Enable built-in media management"
    )

    # Integration Settings
    webhook_endpoints: List[str] = Field(
        default_factory=list,
        description="Additional webhook endpoints for content change notifications"
    )

    build_hook_url: Optional[str] = Field(
        default=None,
        description="URL to trigger site rebuild on content changes"
    )

    # Environment Variables
    environment_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional environment variables for CMS integration"
    )

    @field_validator('admin_users', 'editor_users')
    @classmethod
    def validate_email_list(cls, v):
        """Validate email addresses in user lists"""
        for email in v:
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError(f"Invalid email format: {email}")
        return v

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        """Validate provider name"""
        # Import here to avoid circular imports
        from shared.providers.cms.factory import CMSProviderFactory

        if not CMSProviderFactory.is_provider_supported(v):
            available = CMSProviderFactory.get_available_providers()
            raise ValueError(f"Unsupported CMS provider '{v}'. Available: {available}")
        return v

    def get_provider_config(self) -> Dict[str, Any]:
        """
        Get provider-specific configuration dictionary.

        Combines content_settings with standard fields to create
        the configuration dictionary expected by CMS providers.
        """
        config = {
            "provider": self.provider,
            "admin_users": self.admin_users,
            "editor_users": self.editor_users,
            "editorial_workflow": self.enable_editorial_workflow,
            "media_management": self.enable_media_management,
        }

        # Add authentication settings if specified
        if self.auth_method:
            config["auth_method"] = self.auth_method

        # Add webhook settings
        if self.webhook_endpoints:
            config["webhook_endpoints"] = self.webhook_endpoints
        if self.build_hook_url:
            config["build_hook_url"] = self.build_hook_url

        # Merge provider-specific settings
        config.update(self.content_settings)

        return config

    def validate_with_provider(self) -> bool:
        """
        Validate configuration against the selected CMS provider.

        Creates a temporary provider instance to validate the configuration
        meets the provider's requirements.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        from shared.providers.cms.factory import CMSProviderFactory

        provider_config = self.get_provider_config()
        provider = CMSProviderFactory.create_provider(self.provider, provider_config)

        return provider.validate_configuration()


class ContentTypeConfig(BaseModel):
    """
    Configuration for a content type/collection.

    Defines the structure and behavior of content types
    like blog posts, pages, products, etc.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(
        ...,
        description="Content type identifier (e.g., 'posts', 'pages')",
        pattern=r"^[a-z0-9_]+$"
    )

    label: str = Field(
        ...,
        description="Human-readable content type name"
    )

    description: Optional[str] = Field(
        default=None,
        description="Description of this content type"
    )

    # Content Structure
    folder: Optional[str] = Field(
        default=None,
        description="Folder path for content files (git-based CMS)"
    )

    slug_template: Optional[str] = Field(
        default="{{slug}}",
        description="Template for generating content URLs"
    )

    # Content Fields
    fields: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Field definitions for this content type"
    )

    # Publishing Settings
    supports_draft: bool = Field(
        default=True,
        description="Whether content supports draft status"
    )

    supports_scheduling: bool = Field(
        default=False,
        description="Whether content supports scheduled publishing"
    )

    auto_publish: bool = Field(
        default=False,
        description="Whether content is automatically published on save"
    )

    def get_default_fields(self) -> List[Dict[str, Any]]:
        """Get default field configuration for this content type"""
        if self.name == "posts":
            return [
                {"name": "title", "type": "string", "required": True},
                {"name": "date", "type": "datetime", "required": True},
                {"name": "slug", "type": "string", "required": True},
                {"name": "excerpt", "type": "text"},
                {"name": "body", "type": "markdown", "required": True},
                {"name": "featured_image", "type": "image"},
                {"name": "tags", "type": "list"}
            ]
        elif self.name == "pages":
            return [
                {"name": "title", "type": "string", "required": True},
                {"name": "slug", "type": "string", "required": True},
                {"name": "body", "type": "markdown", "required": True},
                {"name": "featured_image", "type": "image"}
            ]
        else:
            return [
                {"name": "title", "type": "string", "required": True},
                {"name": "body", "type": "markdown", "required": True}
            ]


class CMSIntegrationConfig(BaseModel):
    """
    Complete CMS integration configuration.

    Combines CMS provider settings with content type definitions
    and integration settings for a complete CMS setup.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    # Core CMS Configuration
    cms: CMSConfig = Field(
        ...,
        description="CMS provider configuration"
    )

    # Content Types
    content_types: List[ContentTypeConfig] = Field(
        default_factory=list,
        description="Content type definitions"
    )

    # SSG Integration
    ssg_engine: Optional[str] = Field(
        default=None,
        description="Target SSG engine for content integration"
    )

    build_command: Optional[str] = Field(
        default=None,
        description="Custom build command for SSG integration"
    )

    output_directory: str = Field(
        default="dist",
        description="Build output directory"
    )

    # Performance Settings
    enable_incremental_builds: bool = Field(
        default=True,
        description="Enable incremental builds for faster rebuild times"
    )

    cache_content: bool = Field(
        default=True,
        description="Enable content caching for better performance"
    )

    def get_default_content_types(self) -> List[ContentTypeConfig]:
        """Get default content type configurations"""
        return [
            ContentTypeConfig(
                name="posts",
                label="Blog Posts",
                folder="content/posts",
                slug_template="{{year}}-{{month}}-{{day}}-{{slug}}"
            ),
            ContentTypeConfig(
                name="pages",
                label="Pages",
                folder="content/pages",
                slug_template="{{slug}}"
            )
        ]

    def ensure_default_content_types(self) -> None:
        """Ensure default content types are present"""
        existing_types = {ct.name for ct in self.content_types}

        for default_type in self.get_default_content_types():
            if default_type.name not in existing_types:
                self.content_types.append(default_type)

    def get_provider_instance(self):
        """Get configured CMS provider instance"""
        from shared.providers.cms.factory import CMSProviderFactory

        provider_config = self.cms.get_provider_config()

        # Add SSG engine if specified
        if self.ssg_engine:
            provider_config["ssg_engine"] = self.ssg_engine

        return CMSProviderFactory.create_provider(self.cms.provider, provider_config)

    def validate_integration(self) -> bool:
        """
        Validate the complete CMS integration configuration.

        Checks provider compatibility, content type validity,
        and SSG integration requirements.
        """
        # Validate CMS provider configuration
        self.cms.validate_with_provider()

        # Validate SSG compatibility if specified
        if self.ssg_engine:
            provider = self.get_provider_instance()
            compatible_ssgs = provider.get_ssg_compatibility()

            if self.ssg_engine not in compatible_ssgs:
                raise ValueError(
                    f"SSG engine '{self.ssg_engine}' not compatible with "
                    f"CMS provider '{self.cms.provider}'. "
                    f"Compatible engines: {compatible_ssgs}"
                )

        # Ensure we have at least basic content types
        if not self.content_types:
            self.ensure_default_content_types()

        return True


# Convenience functions for common CMS configurations

def decap_cms_config(
    admin_users: List[str],
    repository: str,
    repository_owner: str,
    branch: str = "main",
    content_path: str = "content",
    media_path: str = "static/images"
) -> CMSConfig:
    """Create Decap CMS configuration"""
    return CMSConfig(
        provider="decap",
        auth_method=CMSAuthMethod.GITHUB_OAUTH,
        admin_users=admin_users,
        content_settings={
            "repository": repository,
            "repository_owner": repository_owner,
            "branch": branch,
            "content_path": content_path,
            "media_path": media_path
        }
    )


def sanity_cms_config(
    admin_users: List[str],
    project_id: str,
    dataset: str = "production",
    api_version: str = "2023-01-01"
) -> CMSConfig:
    """Create Sanity CMS configuration"""
    return CMSConfig(
        provider="sanity",
        auth_method=CMSAuthMethod.API_KEY,
        admin_users=admin_users,
        content_settings={
            "project_id": project_id,
            "dataset": dataset,
            "api_version": api_version
        }
    )


def tina_cms_config(
    admin_users: List[str],
    repository: str,
    repository_owner: str,
    branch: str = "main",
    content_path: str = "content"
) -> CMSConfig:
    """Create Tina CMS configuration"""
    return CMSConfig(
        provider="tina",
        auth_method=CMSAuthMethod.GITHUB_OAUTH,
        admin_users=admin_users,
        content_settings={
            "repository": repository,
            "repository_owner": repository_owner,
            "branch": branch,
            "content_path": content_path
        }
    )


def contentful_cms_config(
    admin_users: List[str],
    space_id: str,
    environment: str = "master",
    delivery_api: bool = True
) -> CMSConfig:
    """Create Contentful CMS configuration"""
    return CMSConfig(
        provider="contentful",
        auth_method=CMSAuthMethod.API_KEY,
        admin_users=admin_users,
        content_settings={
            "space_id": space_id,
            "environment": environment,
            "delivery_api": delivery_api
        }
    )


# Export all models
__all__ = [
    "CMSConfig",
    "ContentTypeConfig",
    "CMSIntegrationConfig",
    "decap_cms_config",
    "sanity_cms_config",
    "tina_cms_config",
    "contentful_cms_config"
]