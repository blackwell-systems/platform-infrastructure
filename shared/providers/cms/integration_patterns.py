"""
CMS Integration Patterns

Provider-agnostic patterns for integrating CMS systems with SSG stacks.
These patterns provide consistent integration approaches across different
CMS providers while maintaining flexibility for provider-specific optimizations.

Key Patterns:
- GitBasedIntegration: For git-based CMS providers (Decap, Tina)
- APIBasedIntegration: For API-based CMS providers (Sanity, Contentful)
- HybridIntegration: For hybrid CMS providers (Tina with API mode)
- ManagedServiceIntegration: For managed CMS services with bulk operations

Usage:
    from shared.providers.cms.integration_patterns import CMSIntegrationManager

    manager = CMSIntegrationManager(client_config)
    integration = manager.get_integration_pattern()
    integration.setup_build_pipeline(stack)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol
from aws_cdk import Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_apigateway as apigateway

from .base_provider import CMSProvider, CMSType
from .factory import CMSProviderFactory


class SSGBuildTrigger(Protocol):
    """Protocol for SSG build trigger implementations"""

    def trigger_build(self, content_change_event: Dict[str, Any]) -> bool:
        """Trigger SSG build based on content change"""
        ...

    def get_webhook_url(self) -> str:
        """Get webhook URL for CMS to call on content changes"""
        ...


class CMSIntegrationPattern(ABC):
    """
    Abstract base class for CMS integration patterns.

    Each integration pattern provides a consistent way to integrate
    a specific type of CMS (git-based, API-based, hybrid) with SSG stacks.
    """

    def __init__(self, provider: CMSProvider, client_config: Dict[str, Any]):
        self.provider = provider
        self.client_config = client_config

    @abstractmethod
    def setup_build_pipeline(self, stack: Stack) -> None:
        """Set up build pipeline for content changes"""
        pass

    @abstractmethod
    def setup_content_sync(self, stack: Stack) -> None:
        """Set up content synchronization"""
        pass

    @abstractmethod
    def setup_admin_interface(self, stack: Stack) -> None:
        """Set up CMS admin interface"""
        pass

    @abstractmethod
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for this integration"""
        pass

    def get_build_hooks(self) -> List[Dict[str, Any]]:
        """Get build hook configurations"""
        return self.provider.get_build_hooks()

    def setup_infrastructure(self, stack: Stack) -> None:
        """Set up complete CMS infrastructure"""
        self.setup_build_pipeline(stack)
        self.setup_content_sync(stack)
        self.setup_admin_interface(stack)

        # Provider-specific infrastructure
        self.provider.setup_infrastructure(stack)


class GitBasedIntegration(CMSIntegrationPattern):
    """
    Integration pattern for git-based CMS providers.

    Suitable for:
    - Decap CMS (formerly Netlify CMS)
    - Forestry (legacy)
    - Any CMS that stores content in git repositories
    """

    def setup_build_pipeline(self, stack: Stack) -> None:
        """
        Set up build pipeline triggered by git webhooks.

        Creates webhook endpoint that triggers builds when content
        is committed to the repository.
        """
        # Create webhook handler Lambda
        webhook_handler = lambda_.Function(
            stack, "GitWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="webhook_handler.handler",
            code=lambda_.Code.from_inline("""
import json
import boto3

def handler(event, context):
    # Process git webhook payload
    payload = json.loads(event['body'])

    # Check if this is a content change to the main branch
    if payload.get('ref') == 'refs/heads/main':
        # Trigger build pipeline
        codebuild = boto3.client('codebuild')
        codebuild.start_build(
            projectName='SSGBuildProject'
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Webhook processed'})
    }
            """),
            environment={
                "BRANCH": self.client_config.get("branch", "main"),
                "REPOSITORY": self.client_config.get("repository", ""),
            }
        )

        # Create API Gateway for webhook endpoint
        api = apigateway.RestApi(
            stack, "GitWebhookAPI",
            rest_api_name="Git Webhook API",
            description="Handles git webhooks for content updates"
        )

        webhook_integration = apigateway.LambdaIntegration(webhook_handler)
        api.root.add_method("POST", webhook_integration)

        # Store webhook URL for provider configuration
        stack.webhook_url = api.url

    def setup_content_sync(self, stack: Stack) -> None:
        """
        Set up content synchronization for git-based CMS.

        For git-based CMS, content sync is handled by git operations.
        We just need to ensure the build process can access the repository.
        """
        # Content is synchronized via git - no additional infrastructure needed
        # Build process will clone the repository and build from source
        pass

    def setup_admin_interface(self, stack: Stack) -> None:
        """
        Set up admin interface for git-based CMS.

        Deploys the CMS admin interface as static files served
        from the same S3/CloudFront distribution as the site.
        """
        # Admin interface configuration
        admin_config = self.provider.get_admin_config()

        # Store admin configuration for deployment
        if hasattr(stack, 'content_bucket'):
            # Admin interface will be deployed as part of the static site
            stack.admin_interface_config = admin_config

    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for git-based integration"""
        base_vars = self.provider.get_environment_variables()

        integration_vars = {
            "CONTENT_SOURCE": "git",
            "BUILD_TRIGGER": "webhook",
            "ADMIN_INTERFACE": "static"
        }

        return {**base_vars, **integration_vars}


class APIBasedIntegration(CMSIntegrationPattern):
    """
    Integration pattern for API-based CMS providers.

    Suitable for:
    - Sanity
    - Contentful
    - Strapi
    - Ghost
    - Any CMS that provides a content API
    """

    def setup_build_pipeline(self, stack: Stack) -> None:
        """
        Set up build pipeline triggered by CMS webhooks.

        Creates webhook endpoint that handles CMS content change notifications
        and triggers incremental or full builds as needed.
        """
        # Create webhook handler Lambda
        webhook_handler = lambda_.Function(
            stack, "CMSWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="cms_webhook_handler.handler",
            code=lambda_.Code.from_inline("""
import json
import boto3
from datetime import datetime

def handler(event, context):
    # Process CMS webhook payload
    payload = json.loads(event['body'])

    # Determine if this requires a full or incremental build
    event_type = payload.get('event_type', 'content.updated')
    content_type = payload.get('content_type', 'unknown')

    # Trigger appropriate build type
    codebuild = boto3.client('codebuild')

    build_env = {
        'WEBHOOK_EVENT': event_type,
        'CONTENT_TYPE': content_type,
        'TIMESTAMP': str(datetime.utcnow())
    }

    if should_trigger_full_build(event_type):
        build_env['BUILD_TYPE'] = 'full'
    else:
        build_env['BUILD_TYPE'] = 'incremental'

    codebuild.start_build(
        projectName='SSGBuildProject',
        environmentVariablesOverride=[
            {'name': k, 'value': v} for k, v in build_env.items()
        ]
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Webhook processed',
            'build_type': build_env['BUILD_TYPE']
        })
    }

def should_trigger_full_build(event_type):
    # Full rebuild for schema changes, partial for content updates
    full_build_events = ['schema.updated', 'content_type.created']
    return event_type in full_build_events
            """),
            environment={
                "CMS_PROVIDER": self.provider.provider_name,
                "API_ENDPOINT": self.client_config.get("api_endpoint", ""),
            }
        )

        # Create API Gateway for webhook endpoint
        api = apigateway.RestApi(
            stack, "CMSWebhookAPI",
            rest_api_name="CMS Webhook API",
            description="Handles CMS webhooks for content updates"
        )

        webhook_integration = apigateway.LambdaIntegration(webhook_handler)
        webhook_resource = api.root.add_resource("webhook")
        webhook_resource.add_method("POST", webhook_integration)

        # Store webhook URL for provider configuration
        stack.webhook_url = f"{api.url}webhook"

    def setup_content_sync(self, stack: Stack) -> None:
        """
        Set up content synchronization for API-based CMS.

        Creates Lambda function for fetching content from CMS API
        and caching it for build optimization.
        """
        # Create content sync Lambda
        content_sync = lambda_.Function(
            stack, "ContentSyncFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="content_sync.handler",
            code=lambda_.Code.from_inline("""
import json
import boto3
import requests
from datetime import datetime

def handler(event, context):
    # Fetch content from CMS API
    cms_provider = event.get('cms_provider')
    api_endpoint = event.get('api_endpoint')

    # Use CMS API client to fetch content
    # This would use the actual API client implementation
    content = fetch_cms_content(api_endpoint)

    # Cache content in S3 for build process
    s3 = boto3.client('s3')
    cache_key = f"content-cache/{datetime.utcnow().isoformat()}.json"

    s3.put_object(
        Bucket=event['content_bucket'],
        Key=cache_key,
        Body=json.dumps(content),
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Content synced',
            'cache_key': cache_key,
            'content_items': len(content.get('items', []))
        })
    }

def fetch_cms_content(api_endpoint):
    # Placeholder - would use actual CMS API client
    return {'items': [], 'total': 0}
            """),
            environment={
                "CMS_PROVIDER": self.provider.provider_name,
            }
        )

        # Grant S3 permissions for content caching
        if hasattr(stack, 'content_bucket'):
            stack.content_bucket.grant_write(content_sync)

    def setup_admin_interface(self, stack: Stack) -> None:
        """
        Set up admin interface for API-based CMS.

        For API-based CMS, the admin interface is typically hosted
        by the CMS provider (e.g., Sanity Studio, Contentful web app).
        We just need to configure access and authentication.
        """
        admin_config = self.provider.get_admin_config()

        # Store admin configuration - typically just URLs and access info
        stack.admin_interface_config = {
            **admin_config,
            "hosted_externally": True,
            "admin_url": self.client_config.get("admin_url", "")
        }

    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for API-based integration"""
        base_vars = self.provider.get_environment_variables()

        integration_vars = {
            "CONTENT_SOURCE": "api",
            "BUILD_TRIGGER": "webhook",
            "ADMIN_INTERFACE": "external",
            "ENABLE_CONTENT_CACHE": "true"
        }

        return {**base_vars, **integration_vars}


class HybridIntegration(CMSIntegrationPattern):
    """
    Integration pattern for hybrid CMS providers.

    Suitable for:
    - Tina CMS (git + API)
    - Any CMS that supports both git-based and API-based workflows
    """

    def __init__(self, provider: CMSProvider, client_config: Dict[str, Any]):
        super().__init__(provider, client_config)

        # Determine primary mode (git or API)
        self.primary_mode = client_config.get("primary_mode", "git")

        # Initialize delegate patterns
        self.git_integration = GitBasedIntegration(provider, client_config)
        self.api_integration = APIBasedIntegration(provider, client_config)

    def setup_build_pipeline(self, stack: Stack) -> None:
        """Set up build pipeline for hybrid CMS"""
        if self.primary_mode == "git":
            self.git_integration.setup_build_pipeline(stack)
        else:
            self.api_integration.setup_build_pipeline(stack)

        # Add fallback webhook for alternate mode
        self._setup_fallback_pipeline(stack)

    def setup_content_sync(self, stack: Stack) -> None:
        """Set up content synchronization for hybrid CMS"""
        # Set up both git and API sync mechanisms
        self.git_integration.setup_content_sync(stack)
        self.api_integration.setup_content_sync(stack)

    def setup_admin_interface(self, stack: Stack) -> None:
        """Set up admin interface for hybrid CMS"""
        admin_config = self.provider.get_admin_config()

        # Hybrid CMS typically provides both interfaces
        stack.admin_interface_config = {
            **admin_config,
            "supports_git_mode": True,
            "supports_api_mode": True,
            "primary_mode": self.primary_mode
        }

    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for hybrid integration"""
        base_vars = self.provider.get_environment_variables()

        integration_vars = {
            "CONTENT_SOURCE": "hybrid",
            "PRIMARY_MODE": self.primary_mode,
            "SUPPORTS_GIT": "true",
            "SUPPORTS_API": "true"
        }

        return {**base_vars, **integration_vars}

    def _setup_fallback_pipeline(self, stack: Stack) -> None:
        """Set up fallback build pipeline for alternate mode"""
        # Create a secondary webhook handler for the alternate mode
        pass


class ManagedServiceIntegration(CMSIntegrationPattern):
    """
    Integration pattern for managed CMS services.

    Provides additional capabilities for clients who need managed
    content services including bulk operations, content migration,
    and programmatic content management.
    """

    def __init__(self, provider: CMSProvider, client_config: Dict[str, Any]):
        super().__init__(provider, client_config)

        # Determine base integration type
        cms_type = provider.get_cms_type()
        if cms_type == CMSType.GIT_BASED:
            self.base_integration = GitBasedIntegration(provider, client_config)
        elif cms_type == CMSType.API_BASED:
            self.base_integration = APIBasedIntegration(provider, client_config)
        else:  # HYBRID
            self.base_integration = HybridIntegration(provider, client_config)

    def setup_build_pipeline(self, stack: Stack) -> None:
        """Set up build pipeline with managed service capabilities"""
        # Use base integration for standard build pipeline
        self.base_integration.setup_build_pipeline(stack)

        # Add managed service endpoints
        self._setup_managed_service_api(stack)

    def setup_content_sync(self, stack: Stack) -> None:
        """Set up content synchronization with bulk operations"""
        # Use base integration for standard sync
        self.base_integration.setup_content_sync(stack)

        # Add bulk operation capabilities
        self._setup_bulk_operations(stack)

    def setup_admin_interface(self, stack: Stack) -> None:
        """Set up admin interface with managed service dashboard"""
        self.base_integration.setup_admin_interface(stack)

        # Add managed service dashboard
        self._setup_managed_dashboard(stack)

    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for managed service integration"""
        base_vars = self.base_integration.get_environment_variables()

        managed_vars = {
            "MANAGED_SERVICES": "enabled",
            "BULK_OPERATIONS": "enabled",
            "CONTENT_MIGRATION": "enabled",
            "API_ACCESS": "full"
        }

        return {**base_vars, **managed_vars}

    def _setup_managed_service_api(self, stack: Stack) -> None:
        """Set up API endpoints for managed services"""
        # Create Lambda functions for managed operations
        managed_api = lambda_.Function(
            stack, "ManagedServiceAPI",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="managed_service.handler",
            code=lambda_.Code.from_inline("""
import json
from cms_api_client import CMSAPIClient

def handler(event, context):
    # Handle managed service API requests
    operation = event.get('operation')

    if operation == 'bulk_import':
        return handle_bulk_import(event)
    elif operation == 'export_content':
        return handle_export_content(event)
    elif operation == 'migrate_content':
        return handle_migrate_content(event)

    return {'statusCode': 400, 'body': 'Unknown operation'}

def handle_bulk_import(event):
    # Implement bulk content import
    return {'statusCode': 200, 'body': 'Bulk import completed'}

def handle_export_content(event):
    # Implement content export
    return {'statusCode': 200, 'body': 'Content exported'}

def handle_migrate_content(event):
    # Implement content migration
    return {'statusCode': 200, 'body': 'Content migrated'}
            """)
        )

    def _setup_bulk_operations(self, stack: Stack) -> None:
        """Set up bulk content operation capabilities"""
        # Create SQS queue for bulk operations
        from aws_cdk import aws_sqs as sqs

        bulk_queue = sqs.Queue(
            stack, "BulkOperationsQueue",
            queue_name=f"{stack.client_config.resource_prefix}-bulk-ops"
        )

    def _setup_managed_dashboard(self, stack: Stack) -> None:
        """Set up managed service dashboard"""
        # This would set up a dashboard for managed service operations
        pass


class CMSIntegrationManager:
    """
    Manager for selecting and configuring CMS integration patterns.

    Analyzes client configuration and CMS provider to determine
    the most appropriate integration pattern.
    """

    def __init__(self, client_config: Dict[str, Any]):
        self.client_config = client_config

    def get_integration_pattern(self) -> CMSIntegrationPattern:
        """
        Get the appropriate integration pattern for the client configuration.

        Returns:
            CMSIntegrationPattern instance configured for the client
        """
        # Get CMS provider
        cms_config = self.client_config.get("cms_config")
        if not cms_config:
            raise ValueError("No CMS configuration provided")

        provider_name = cms_config["cms"]["provider"]
        provider_config = cms_config["cms"]["content_settings"]

        provider = CMSProviderFactory.create_provider(provider_name, provider_config)

        # Determine if managed services are needed
        service_tier = self.client_config.get("service_tier", "tier1")
        offers_managed_services = self.client_config.get("offers_managed_services", False)

        if offers_managed_services or service_tier in ["tier2", "tier3"]:
            return ManagedServiceIntegration(provider, provider_config)

        # Select based on CMS type
        cms_type = provider.get_cms_type()

        if cms_type == CMSType.GIT_BASED:
            return GitBasedIntegration(provider, provider_config)
        elif cms_type == CMSType.API_BASED:
            return APIBasedIntegration(provider, provider_config)
        else:  # HYBRID
            return HybridIntegration(provider, provider_config)

    def get_recommended_integration(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get integration pattern recommendation based on requirements.

        Args:
            requirements: Dict with keys like 'content_volume', 'technical_skill',
                         'collaboration_needs', 'budget'

        Returns:
            Dict with recommendation details and reasoning
        """
        content_volume = requirements.get("content_volume", "medium")
        technical_skill = requirements.get("technical_skill", "medium")
        collaboration = requirements.get("collaboration_needs", "basic")
        budget = requirements.get("budget", 100)

        recommendations = []

        # Git-based for technical users with version control needs
        if technical_skill == "high" and budget < 50:
            recommendations.append({
                "pattern": "git_based",
                "providers": ["decap"],
                "score": 9,
                "reason": "Perfect for technical users who want version control and zero cost"
            })

        # API-based for high collaboration and content volume
        if collaboration == "high" or content_volume == "large":
            recommendations.append({
                "pattern": "api_based",
                "providers": ["sanity", "contentful"],
                "score": 8,
                "reason": "Best for high collaboration and large content volumes"
            })

        # Hybrid for flexibility
        if technical_skill == "medium":
            recommendations.append({
                "pattern": "hybrid",
                "providers": ["tina"],
                "score": 7,
                "reason": "Provides flexibility for growing teams"
            })

        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return {
            "recommended": recommendations[0] if recommendations else None,
            "alternatives": recommendations[1:],
            "requirements": requirements
        }


# Export key classes
__all__ = [
    "CMSIntegrationPattern",
    "GitBasedIntegration",
    "APIBasedIntegration",
    "HybridIntegration",
    "ManagedServiceIntegration",
    "CMSIntegrationManager"
]