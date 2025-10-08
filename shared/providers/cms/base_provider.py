"""
Abstract Base CMS Provider

Defines the interface that all CMS providers must implement.
This abstraction allows SSG stacks to support multiple CMS platforms
(Decap CMS, Tina CMS, Sanity, Contentful, etc.) without duplicating integration logic.

Design Principles:
- Provider-agnostic content management setup
- Consistent environment variable management
- Standardized configuration metadata
- Clean separation between SSG logic and CMS logic
- Support for both git-based and API-based CMS systems
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class CMSType(str, Enum):
    """CMS architecture types"""
    GIT_BASED = "git_based"      # Decap CMS, Forestry (file-based)
    API_BASED = "api_based"      # Sanity, Contentful, Strapi
    HYBRID = "hybrid"            # Tina CMS (git + API)


class CMSAuthMethod(str, Enum):
    """CMS authentication methods"""
    GITHUB_OAUTH = "github_oauth"      # GitHub OAuth integration
    NETLIFY_IDENTITY = "netlify_identity"  # Netlify Identity
    API_KEY = "api_key"                # API key authentication
    JWT = "jwt"                        # JWT token authentication
    OAUTH2 = "oauth2"                  # Generic OAuth2


class CMSProvider(ABC):
    """
    Abstract base class for all CMS provider integrations.

    Each CMS provider (Decap, Tina, Sanity, Contentful, etc.) implements
    this interface to provide consistent integration across all SSG stacks.

    The provider is responsible for:
    - CMS-specific configuration and setup
    - Environment variables for build-time integration
    - Admin panel configuration and authentication
    - Content schema and field definitions
    - Build hooks and content synchronization
    """

    def __init__(self, provider_name: str, config: Dict[str, Any]):
        """
        Initialize the CMS provider.

        Args:
            provider_name: Identifier for this provider (e.g., "decap", "tina", "sanity")
            config: Provider-specific configuration from StaticSiteConfig.cms_config
        """
        self.provider_name = provider_name
        self.config = config

    @abstractmethod
    def get_cms_type(self) -> CMSType:
        """
        Get the CMS architecture type.

        Returns:
            CMS type (git_based, api_based, or hybrid)
        """
        pass

    @abstractmethod
    def get_auth_method(self) -> CMSAuthMethod:
        """
        Get the primary authentication method for this CMS.

        Returns:
            Authentication method used by this CMS
        """
        pass

    @abstractmethod
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get environment variables required by this CMS provider.

        Returns variables needed for:
        - CMS API keys and configuration
        - Build-time integration settings
        - Admin panel configuration
        - Content synchronization

        Returns:
            Dict of environment variable names to values.
            Values starting with "${...}" are CDK parameters.

        Example:
            {
                "SANITY_PROJECT_ID": "${SANITY_PROJECT_ID}",
                "SANITY_DATASET": "production",
                "SANITY_API_VERSION": "2023-01-01",
                "CMS_PROVIDER": "sanity"
            }
        """
        pass

    @abstractmethod
    def setup_infrastructure(self, stack) -> None:
        """
        Set up AWS infrastructure specific to this CMS provider.

        This method is called by the SSG stack to create CMS-specific
        AWS resources such as:
        - Lambda functions for webhook processing (API-based CMS)
        - Build triggers for content updates
        - Authentication infrastructure (if needed)
        - Content synchronization services

        Args:
            stack: The CDK stack instance where resources should be created
        """
        pass

    @abstractmethod
    def get_configuration_metadata(self) -> Dict[str, Any]:
        """
        Get CMS configuration metadata for client documentation.

        Returns comprehensive information about:
        - Cost structure (monthly fees, usage limits)
        - Setup complexity and estimated time
        - Supported content types and features
        - Integration requirements
        - Documentation and resources

        Returns:
            Dictionary with standardized CMS information

        Example:
            {
                "provider": "sanity",
                "cms_type": "api_based",
                "monthly_cost_range": [0, 99],
                "setup_complexity": "medium",
                "features": ["visual_editor", "real_time_collaboration", "image_processing"]
            }
        """
        pass

    @abstractmethod
    def get_admin_config(self) -> Dict[str, Any]:
        """
        Get CMS admin panel configuration.

        Returns configuration for the CMS admin interface including:
        - Admin panel URL and access
        - Authentication setup
        - Content schema definitions
        - Editor configuration

        Returns:
            Dictionary with admin panel configuration

        Example:
            {
                "admin_path": "/admin",
                "auth_required": True,
                "content_types": ["posts", "pages", "settings"],
                "editor_config": {"preview": True, "media_folder": "/static/images"}
            }
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """
        Validate that the CMS configuration is complete and correct.

        Checks that required configuration parameters are present
        and have valid values for this CMS provider.

        Returns:
            True if configuration is valid, raises ValueError otherwise

        Raises:
            ValueError: If configuration is invalid with descriptive message
        """
        pass

    def get_provider_name(self) -> str:
        """Get the CMS provider name"""
        return self.provider_name

    def get_config(self) -> Dict[str, Any]:
        """Get the CMS provider configuration"""
        return self.config

    def supports_feature(self, feature: str) -> bool:
        """
        Check if this CMS provider supports a specific feature.

        Args:
            feature: Feature name to check (e.g., "visual_editor", "media_management")

        Returns:
            True if feature is supported
        """
        metadata = self.get_configuration_metadata()
        supported_features = metadata.get("features", [])
        return feature in supported_features

    def get_content_schema(self) -> Dict[str, Any]:
        """
        Get default content schema for this CMS.

        Returns basic content types and field definitions
        that work well with SSG integration.

        Returns:
            Dictionary with content schema definitions
        """
        return {
            "collections": [
                {
                    "name": "posts",
                    "label": "Blog Posts",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "date", "type": "datetime", "required": True},
                        {"name": "slug", "type": "string", "required": True},
                        {"name": "excerpt", "type": "text"},
                        {"name": "body", "type": "markdown", "required": True},
                        {"name": "featured_image", "type": "image"},
                        {"name": "tags", "type": "list"}
                    ]
                },
                {
                    "name": "pages",
                    "label": "Pages",
                    "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "slug", "type": "string", "required": True},
                        {"name": "body", "type": "markdown", "required": True},
                        {"name": "featured_image", "type": "image"}
                    ]
                }
            ]
        }

    def get_build_hooks(self) -> List[Dict[str, Any]]:
        """
        Get build hooks configuration for content updates.

        Returns webhook URLs and configurations needed to trigger
        site rebuilds when content changes.

        Returns:
            List of build hook configurations
        """
        return []

    def estimate_monthly_cost(self, content_volume: str = "small") -> Dict[str, Any]:
        """
        Estimate monthly costs for this CMS based on usage.

        Args:
            content_volume: Expected content volume ("small", "medium", "large")

        Returns:
            Cost breakdown dictionary

        Example:
            {
                "base_monthly_fee": 0,
                "usage_costs": 25,
                "total_estimated": 25,
                "content_volume": "medium"
            }
        """
        metadata = self.get_configuration_metadata()
        cost_range = metadata.get("monthly_cost_range", [0, 0])

        volume_multipliers = {
            "small": 0.3,    # Use lower end of cost range
            "medium": 0.6,   # Use middle of cost range
            "large": 1.0     # Use upper end of cost range
        }

        multiplier = volume_multipliers.get(content_volume, 0.6)
        base_cost = cost_range[0]
        usage_cost = (cost_range[1] - cost_range[0]) * multiplier

        return {
            "base_monthly_fee": base_cost,
            "usage_costs": round(usage_cost, 2),
            "total_estimated": round(base_cost + usage_cost, 2),
            "content_volume": content_volume
        }

    def get_ssg_compatibility(self) -> List[str]:
        """
        Get list of SSG engines compatible with this CMS.

        Returns:
            List of compatible SSG engine names
        """
        # Default compatibility - override in concrete providers
        return ["eleventy", "hugo", "astro", "gatsby", "nextjs", "nuxt"]

    def get_required_dependencies(self, ssg_engine: str) -> List[str]:
        """
        Get required dependencies for SSG integration.

        Args:
            ssg_engine: Target SSG engine name

        Returns:
            List of npm packages or other dependencies needed
        """
        return []

    def get_integration_guide(self) -> Dict[str, Any]:
        """
        Get step-by-step integration guide for clients.

        Returns detailed instructions for setting up this CMS
        with SSG integration.

        Returns:
            Dictionary with integration steps and requirements
        """
        return {
            "title": f"{self.provider_name.title()} CMS Integration Guide",
            "steps": [
                {
                    "step": 1,
                    "title": "CMS Account Setup",
                    "description": f"Create account with {self.provider_name}",
                    "action": "Sign up and verify account"
                },
                {
                    "step": 2,
                    "title": "Project Configuration",
                    "description": "Configure CMS project settings",
                    "action": "Set up content schema and access permissions"
                },
                {
                    "step": 3,
                    "title": "SSG Integration",
                    "description": "Connect CMS to SSG build process",
                    "action": "Configure build hooks and content synchronization"
                },
                {
                    "step": 4,
                    "title": "Deploy and Test",
                    "description": "Deploy site and test content management",
                    "action": "Verify admin access and content publishing"
                }
            ],
            "requirements": {
                "technical_skill": "Medium",
                "estimated_setup_time": "2-4 hours",
                "ongoing_maintenance": "Low"
            }
        }


class CMSProviderConfig(BaseModel):
    """
    Base configuration model for CMS provider validation.

    Concrete CMS providers can extend this model to add
    provider-specific configuration fields.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow"  # Allow provider-specific fields
    )

    provider: str = Field(..., description="CMS provider name")
    cms_type: CMSType = Field(..., description="CMS architecture type")
    auth_method: CMSAuthMethod = Field(..., description="Authentication method")
    admin_users: List[str] = Field(default_factory=list, description="Admin user emails")
    content_path: str = Field(default="content", description="Content directory path")
    media_path: str = Field(default="static/images", description="Media files path")
    branch: str = Field(default="main", description="Git branch for content (git-based CMS)")


# Common CMS features that providers can reference
class CMSFeatures:
    """Standard CMS features for capability checking"""

    VISUAL_EDITOR = "visual_editor"
    MARKDOWN_EDITOR = "markdown_editor"
    MEDIA_MANAGEMENT = "media_management"
    REAL_TIME_COLLABORATION = "real_time_collaboration"
    WORKFLOW_MANAGEMENT = "workflow_management"
    CONTENT_SCHEDULING = "content_scheduling"
    MULTI_LANGUAGE = "multi_language"
    CUSTOM_FIELDS = "custom_fields"
    API_ACCESS = "api_access"
    WEBHOOK_SUPPORT = "webhook_support"
    PREVIEW_MODE = "preview_mode"
    REVISION_HISTORY = "revision_history"
    ROLE_BASED_ACCESS = "role_based_access"
    ASSET_OPTIMIZATION = "asset_optimization"
    SEO_TOOLS = "seo_tools"