"""
Provider Adapter Registry

This module implements the ProviderAdapterRegistry to eliminate if/elif routing
in Lambda handlers and provide a scalable, modular approach to content
normalization across different CMS and E-commerce providers.

Addresses the content normalization optimization recommendation from the
event-driven composition architecture review.
"""

from typing import Dict, Any, List, Optional, Type, Callable
from abc import ABC, abstractmethod
import importlib
import logging
from dataclasses import dataclass

from models.composition import UnifiedContent, ContentEvent
from shared.interfaces.composable_component import ComposableComponent


logger = logging.getLogger(__name__)


@dataclass
class ProviderAdapter:
    """Provider adapter configuration"""
    provider_name: str
    provider_type: str  # "cms" or "ecommerce"
    handler_module: str
    handler_class: str
    normalization_method: str
    webhook_events: List[str]
    priority: int = 100  # Lower numbers = higher priority


class IProviderHandler(ABC):
    """Interface for provider-specific content handlers"""

    @abstractmethod
    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """Normalize webhook data to unified content schema"""
        pass

    @abstractmethod
    def validate_webhook_signature(self, body: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Validate webhook signature for security"""
        pass

    @abstractmethod
    def get_supported_events(self) -> List[str]:
        """Get list of supported webhook events"""
        pass

    @abstractmethod
    def extract_event_type(self, headers: Dict[str, str], body: Dict[str, Any]) -> str:
        """Extract event type from webhook"""
        pass


class ProviderAdapterRegistry:
    """
    Registry for provider adapters that eliminates if/elif routing
    and provides modular, scalable content normalization.
    """

    def __init__(self):
        self._adapters: Dict[str, ProviderAdapter] = {}
        self._handlers: Dict[str, IProviderHandler] = {}
        self._handler_cache: Dict[str, IProviderHandler] = {}

    def register_adapter(self, adapter: ProviderAdapter) -> None:
        """
        Register a provider adapter.

        Args:
            adapter: ProviderAdapter configuration
        """
        self._adapters[adapter.provider_name] = adapter
        logger.info(f"Registered provider adapter: {adapter.provider_name}")

    def register_builtin_adapters(self) -> None:
        """Register all built-in provider adapters"""

        # CMS Provider Adapters
        cms_adapters = [
            ProviderAdapter(
                provider_name="decap",
                provider_type="cms",
                handler_module="shared.composition.adapters.decap_adapter",
                handler_class="DecapCMSHandler",
                normalization_method="normalize_github_webhook",
                webhook_events=["push", "pull_request"],
                priority=10
            ),
            ProviderAdapter(
                provider_name="sanity",
                provider_type="cms",
                handler_module="shared.composition.adapters.sanity_adapter",
                handler_class="SanityCMSHandler",
                normalization_method="normalize_sanity_webhook",
                webhook_events=["document.create", "document.update", "document.delete"],
                priority=20
            ),
            ProviderAdapter(
                provider_name="tina",
                provider_type="cms",
                handler_module="shared.composition.adapters.tina_adapter",
                handler_class="TinaCMSHandler",
                normalization_method="normalize_tina_webhook",
                webhook_events=["content.create", "content.update", "content.delete"],
                priority=30
            ),
            ProviderAdapter(
                provider_name="contentful",
                provider_type="cms",
                handler_module="shared.composition.adapters.contentful_adapter",
                handler_class="ContentfulCMSHandler",
                normalization_method="normalize_contentful_webhook",
                webhook_events=["Entry.create", "Entry.save", "Entry.delete", "Entry.publish"],
                priority=40
            )
        ]

        # E-commerce Provider Adapters
        ecommerce_adapters = [
            ProviderAdapter(
                provider_name="snipcart",
                provider_type="ecommerce",
                handler_module="shared.composition.adapters.snipcart_adapter",
                handler_class="SnipcartEcommerceHandler",
                normalization_method="normalize_snipcart_webhook",
                webhook_events=["order.completed", "subscription.created"],
                priority=10
            ),
            ProviderAdapter(
                provider_name="foxy",
                provider_type="ecommerce",
                handler_module="shared.composition.adapters.foxy_adapter",
                handler_class="FoxyEcommerceHandler",
                normalization_method="normalize_foxy_webhook",
                webhook_events=["transaction/create", "subscription/create"],
                priority=20
            ),
            ProviderAdapter(
                provider_name="shopify_basic",
                provider_type="ecommerce",
                handler_module="shared.composition.adapters.shopify_basic_adapter",
                handler_class="ShopifyBasicHandler",
                normalization_method="normalize_shopify_webhook",
                webhook_events=[
                    "products/create", "products/update", "products/delete",
                    "inventory_levels/update", "collections/create", "collections/update"
                ],
                priority=30
            )
        ]

        # Register all adapters
        for adapter in cms_adapters + ecommerce_adapters:
            self.register_adapter(adapter)

    def get_handler(self, provider_name: str) -> Optional[IProviderHandler]:
        """
        Get handler instance for provider, using caching for performance.

        Args:
            provider_name: Name of the provider

        Returns:
            IProviderHandler instance or None if not found
        """

        # Check cache first
        if provider_name in self._handler_cache:
            return self._handler_cache[provider_name]

        # Check if adapter is registered
        if provider_name not in self._adapters:
            logger.warning(f"No adapter registered for provider: {provider_name}")
            return None

        adapter = self._adapters[provider_name]

        try:
            # Dynamically import and instantiate handler
            module = importlib.import_module(adapter.handler_module)
            handler_class = getattr(module, adapter.handler_class)
            handler_instance = handler_class()

            # Validate handler implements interface
            if not isinstance(handler_instance, IProviderHandler):
                logger.error(f"Handler {adapter.handler_class} does not implement IProviderHandler")
                return None

            # Cache the handler
            self._handler_cache[provider_name] = handler_instance
            logger.info(f"Loaded and cached handler for provider: {provider_name}")

            return handler_instance

        except Exception as e:
            logger.error(f"Failed to load handler for provider {provider_name}: {str(e)}")
            return None

    def normalize_content(
        self,
        provider_name: str,
        webhook_data: Dict[str, Any],
        headers: Dict[str, str]
    ) -> List[UnifiedContent]:
        """
        Normalize content using the appropriate provider handler.

        Args:
            provider_name: Name of the provider
            webhook_data: Raw webhook data
            headers: HTTP headers from webhook

        Returns:
            List of UnifiedContent objects

        Raises:
            ValueError: If provider not supported or normalization fails
        """

        handler = self.get_handler(provider_name)
        if not handler:
            raise ValueError(f"No handler available for provider: {provider_name}")

        try:
            # Validate webhook signature
            if not handler.validate_webhook_signature(webhook_data, headers):
                raise ValueError(f"Invalid webhook signature for provider: {provider_name}")

            # Extract event type
            event_type = handler.extract_event_type(headers, webhook_data)

            # Normalize content
            unified_content = handler.normalize_webhook_data(webhook_data, event_type)

            logger.info(f"Normalized {len(unified_content)} items from {provider_name} webhook")
            return unified_content

        except Exception as e:
            logger.error(f"Content normalization failed for {provider_name}: {str(e)}")
            raise

    def validate_webhook(
        self,
        provider_name: str,
        webhook_data: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bool:
        """
        Validate webhook for provider.

        Args:
            provider_name: Name of the provider
            webhook_data: Raw webhook data
            headers: HTTP headers from webhook

        Returns:
            True if webhook is valid, False otherwise
        """

        handler = self.get_handler(provider_name)
        if not handler:
            return False

        try:
            return handler.validate_webhook_signature(webhook_data, headers)
        except Exception as e:
            logger.error(f"Webhook validation failed for {provider_name}: {str(e)}")
            return False

    def get_supported_providers(self, provider_type: Optional[str] = None) -> List[str]:
        """
        Get list of supported providers.

        Args:
            provider_type: Filter by provider type ("cms" or "ecommerce")

        Returns:
            List of provider names
        """

        providers = []
        for name, adapter in self._adapters.items():
            if provider_type is None or adapter.provider_type == provider_type:
                providers.append(name)

        return sorted(providers)

    def get_provider_events(self, provider_name: str) -> List[str]:
        """
        Get supported events for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            List of supported event names
        """

        if provider_name not in self._adapters:
            return []

        return self._adapters[provider_name].webhook_events

    def get_provider_type(self, provider_name: str) -> Optional[str]:
        """
        Get provider type (cms or ecommerce).

        Args:
            provider_name: Name of the provider

        Returns:
            Provider type or None if not found
        """

        if provider_name not in self._adapters:
            return None

        return self._adapters[provider_name].provider_type

    def list_adapters(self) -> List[ProviderAdapter]:
        """
        List all registered adapters.

        Returns:
            List of ProviderAdapter objects
        """

        return list(self._adapters.values())

    def clear_cache(self) -> None:
        """Clear the handler cache (useful for testing)"""
        self._handler_cache.clear()
        logger.info("Provider handler cache cleared")

    def get_adapter_stats(self) -> Dict[str, Any]:
        """
        Get statistics about registered adapters.

        Returns:
            Dictionary with adapter statistics
        """

        total_adapters = len(self._adapters)
        cms_adapters = len([a for a in self._adapters.values() if a.provider_type == "cms"])
        ecommerce_adapters = len([a for a in self._adapters.values() if a.provider_type == "ecommerce"])
        cached_handlers = len(self._handler_cache)

        return {
            "total_adapters": total_adapters,
            "cms_adapters": cms_adapters,
            "ecommerce_adapters": ecommerce_adapters,
            "cached_handlers": cached_handlers,
            "cache_hit_ratio": cached_handlers / total_adapters if total_adapters > 0 else 0
        }


# Global registry instance
provider_registry = ProviderAdapterRegistry()

# Initialize with built-in adapters
provider_registry.register_builtin_adapters()


class OptimizedIntegrationHandler:
    """
    Optimized integration handler using ProviderAdapterRegistry
    instead of if/elif routing for better performance and maintainability.
    """

    def __init__(self):
        self.provider_registry = provider_registry
        # Other initialization code...

    def handle_webhook(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Handle webhook using provider registry instead of if/elif routing.

        This eliminates the complex conditional logic and provides
        better performance through handler caching.
        """

        try:
            # Extract provider from path
            path_parameters = event.get('pathParameters', {})
            provider_name = path_parameters.get('proxy', '').split('/')[0]

            # Get webhook body and headers
            body = event.get('body', '{}')
            headers = event.get('headers', {})

            if isinstance(body, str):
                import json
                body = json.loads(body)

            logger.info(f"Processing webhook from {provider_name}")

            # Use registry to normalize content (eliminates if/elif routing)
            unified_content = self.provider_registry.normalize_content(
                provider_name=provider_name,
                webhook_data=body,
                headers=headers
            )

            # Process normalized content
            events_published = []
            for content in unified_content:
                # Store in unified cache
                self._store_unified_content(content)

                # Publish SNS event
                event_published = self._publish_content_event(
                    event_type="content.updated" if content.status == "published" else "content.created",
                    content=content
                )
                events_published.append(event_published)

            return self._create_response(200, {
                'message': f'Processed {len(unified_content)} content items from {provider_name}',
                'events_published': len(events_published),
                'provider_type': self.provider_registry.get_provider_type(provider_name)
            })

        except ValueError as e:
            logger.error(f"Webhook validation error: {str(e)}")
            return self._create_response(400, {'error': str(e)})

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return self._create_response(500, {'error': 'Internal server error'})

    def _create_response(self, status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
        """Create HTTP response"""
        import json
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(body)
        }

    def _store_unified_content(self, content: UnifiedContent) -> None:
        """Store unified content in DynamoDB cache"""
        # Implementation would be here
        pass

    def _publish_content_event(self, event_type: str, content: UnifiedContent) -> str:
        """Publish content change event to SNS"""
        # Implementation would be here
        pass


# Example adapter implementation
class BaseProviderHandler(IProviderHandler):
    """Base class for provider handlers with common functionality"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def validate_webhook_signature(self, body: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Default implementation - should be overridden by specific providers"""
        # For development/testing, allow all webhooks
        # In production, implement proper signature validation
        return True

    def extract_event_type(self, headers: Dict[str, str], body: Dict[str, Any]) -> str:
        """Extract event type from webhook - should be overridden"""
        return headers.get('X-Event-Type', 'unknown')

    def get_supported_events(self) -> List[str]:
        """Get supported events - should be overridden"""
        return []

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """Normalize webhook data - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement normalize_webhook_data")


# Usage example in Lambda
def lambda_handler(event, context):
    """
    Example Lambda handler using the optimized approach
    """
    handler = OptimizedIntegrationHandler()
    return handler.handle_webhook(event, context)