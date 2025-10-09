"""
Composable Component Protocol Interface

This module defines the standard protocol that all CMS and E-commerce components
must implement for event-driven composition integration. This interface ensures
consistent behavior across all providers and enables pluggable architecture.

Based on the event-driven composition architecture:
docs/architecture/event-driven-composition-architecture.md
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, Dict, Any, List, Optional
from models.composition import (
    UnifiedContent, ComponentRegistration, CostBreakdown,
    ContentEvent, CompositionConfiguration
)
from shared.ssg.core_models import SSGEngineType


@runtime_checkable
class ComposableComponent(Protocol):
    """
    Standard protocol that all CMS and E-commerce components must implement
    for event-driven composition integration.

    This protocol defines the contract for:
    - Webhook registration with integration layer
    - Content normalization to unified schema
    - Event handling and generation
    - Configuration validation
    - Cost estimation
    """

    def register_with_integration_layer(self, integration_api_url: str) -> ComponentRegistration:
        """
        Register component webhooks with the integration layer.

        This method configures the component's webhooks to point to the
        integration API and returns registration information for the
        integration layer to process.

        Args:
            integration_api_url: Base URL of the integration API

        Returns:
            ComponentRegistration with webhook endpoints and metadata

        Raises:
            ValueError: If registration fails due to invalid configuration
            ConnectionError: If unable to register webhooks with provider
        """
        ...

    def normalize_content(self, raw_data: Dict[str, Any]) -> List[UnifiedContent]:
        """
        Convert provider-specific data to unified content schema.

        This is the core normalization function that transforms raw webhook
        data or API responses into the standardized UnifiedContent format
        that can be consumed by any SSG engine.

        Args:
            raw_data: Raw data from provider webhook or API

        Returns:
            List of UnifiedContent objects

        Raises:
            ValueError: If raw_data cannot be normalized
        """
        ...

    def get_webhook_events(self) -> List[str]:
        """
        Return list of webhook events this component can handle.

        Returns:
            List of webhook event names (e.g., ['products/create', 'products/update'])
        """
        ...

    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate component configuration before deployment.

        Args:
            config: Component configuration dictionary

        Returns:
            True if configuration is valid, False otherwise
        """
        ...

    def get_build_dependencies(self, ssg_engine: SSGEngineType) -> Dict[str, List[str]]:
        """
        Return build dependencies needed for SSG integration.

        Args:
            ssg_engine: Target SSG engine

        Returns:
            Dictionary with dependency lists (e.g., {"npm_packages": ["package1", "package2"]})
        """
        ...

    def estimate_monthly_cost(self, requirements: Dict[str, Any]) -> CostBreakdown:
        """
        Estimate monthly operational costs for this component.

        Args:
            requirements: Client requirements and usage estimates

        Returns:
            CostBreakdown with component-specific costs
        """
        ...

    def generate_environment_variables(self, ssg_engine: SSGEngineType) -> Dict[str, str]:
        """
        Generate environment variables needed for SSG build process.

        Args:
            ssg_engine: Target SSG engine

        Returns:
            Dictionary of environment variables
        """
        ...

    def get_component_metadata(self) -> Dict[str, Any]:
        """
        Get component metadata for monitoring and debugging.

        Returns:
            Dictionary with component information
        """
        ...


class BaseCMSComponent(ABC):
    """
    Abstract base class for CMS components implementing ComposableComponent protocol.

    Provides common functionality for CMS providers while requiring
    implementation of provider-specific methods.
    """

    def __init__(self, provider_name: str, **kwargs):
        self.provider_name = provider_name
        self.component_type = "cms"
        self.configuration = kwargs

    @abstractmethod
    def _fetch_content_from_provider(self) -> List[Dict[str, Any]]:
        """Fetch content from CMS provider"""
        pass

    @abstractmethod
    def _parse_webhook_data(self, webhook_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse webhook data from CMS provider"""
        pass

    @abstractmethod
    def _create_provider_webhooks(self, webhook_url: str) -> List[str]:
        """Create webhooks with CMS provider"""
        pass

    def normalize_content(self, raw_data: Dict[str, Any]) -> List[UnifiedContent]:
        """Default implementation for CMS content normalization"""

        # Parse webhook or API data
        parsed_items = self._parse_webhook_data(raw_data)

        unified_content = []
        for item in parsed_items:
            content = self._normalize_single_item(item)
            if content:
                unified_content.append(content)

        return unified_content

    def _normalize_single_item(self, item: Dict[str, Any]) -> Optional[UnifiedContent]:
        """Normalize a single content item - to be overridden by subclasses"""

        # Basic normalization that works for most CMS providers
        return UnifiedContent(
            id=str(item.get("id", "")),
            title=item.get("title", "Untitled"),
            slug=item.get("slug", ""),
            content_type="article",  # Default for CMS
            description=item.get("description"),
            body=item.get("body") or item.get("content"),
            provider_type="cms",
            provider_name=self.provider_name,
            provider_data=item,
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
            tags=item.get("tags", [])
        )

    def get_webhook_events(self) -> List[str]:
        """Default CMS webhook events"""
        return [
            "content.created",
            "content.updated",
            "content.deleted",
            "content.published"
        ]

    def get_component_metadata(self) -> Dict[str, Any]:
        """Default component metadata"""
        return {
            "provider_name": self.provider_name,
            "component_type": self.component_type,
            "version": "1.0.0",
            "capabilities": self.get_webhook_events(),
            "configuration": self.configuration
        }


class BaseEcommerceComponent(ABC):
    """
    Abstract base class for E-commerce components implementing ComposableComponent protocol.

    Provides common functionality for E-commerce providers while requiring
    implementation of provider-specific methods.
    """

    def __init__(self, provider_name: str, **kwargs):
        self.provider_name = provider_name
        self.component_type = "ecommerce"
        self.configuration = kwargs

    @abstractmethod
    def _fetch_products_from_provider(self) -> List[Dict[str, Any]]:
        """Fetch products from E-commerce provider"""
        pass

    @abstractmethod
    def _parse_webhook_data(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse webhook data from E-commerce provider"""
        pass

    @abstractmethod
    def _create_provider_webhooks(self, webhook_url: str) -> List[str]:
        """Create webhooks with E-commerce provider"""
        pass

    def normalize_content(self, raw_data: Dict[str, Any]) -> List[UnifiedContent]:
        """Default implementation for E-commerce content normalization"""

        # Parse webhook or API data
        parsed_item = self._parse_webhook_data(raw_data)

        if parsed_item:
            content = self._normalize_product(parsed_item)
            return [content] if content else []

        return []

    def _normalize_product(self, product_data: Dict[str, Any]) -> Optional[UnifiedContent]:
        """Normalize a product - to be overridden by subclasses"""

        # Basic normalization that works for most E-commerce providers
        return UnifiedContent(
            id=str(product_data.get("id", "")),
            title=product_data.get("title") or product_data.get("name", "Untitled Product"),
            slug=product_data.get("slug") or product_data.get("handle", ""),
            content_type="product",
            description=product_data.get("description"),
            provider_type="ecommerce",
            provider_name=self.provider_name,
            provider_data=product_data,
            created_at=product_data.get("created_at"),
            updated_at=product_data.get("updated_at"),
            tags=product_data.get("tags", [])
        )

    def get_webhook_events(self) -> List[str]:
        """Default E-commerce webhook events"""
        return [
            "products/create",
            "products/update",
            "products/delete",
            "inventory_levels/update",
            "collections/create",
            "collections/update"
        ]

    def get_component_metadata(self) -> Dict[str, Any]:
        """Default component metadata"""
        return {
            "provider_name": self.provider_name,
            "component_type": self.component_type,
            "version": "1.0.0",
            "capabilities": self.get_webhook_events(),
            "configuration": self.configuration
        }


class ComponentRegistry:
    """
    Registry for managing composable components in the integration layer.

    This class maintains a registry of all registered components and provides
    methods for component discovery, validation, and management.
    """

    def __init__(self):
        self._components: Dict[str, ComposableComponent] = {}
        self._registrations: Dict[str, ComponentRegistration] = {}

    def register_component(
        self,
        component: ComposableComponent,
        integration_api_url: str
    ) -> ComponentRegistration:
        """
        Register a new component with the integration layer.

        Args:
            component: Component implementing ComposableComponent protocol
            integration_api_url: Integration API URL for webhook registration

        Returns:
            ComponentRegistration information

        Raises:
            ValueError: If component registration fails
        """

        # Validate component implements protocol
        if not isinstance(component, ComposableComponent):
            raise ValueError("Component must implement ComposableComponent protocol")

        # Register with integration layer
        registration = component.register_with_integration_layer(integration_api_url)

        # Store in registry
        self._components[registration.component_id] = component
        self._registrations[registration.component_id] = registration

        return registration

    def get_component(self, component_id: str) -> Optional[ComposableComponent]:
        """Get component by ID"""
        return self._components.get(component_id)

    def get_registration(self, component_id: str) -> Optional[ComponentRegistration]:
        """Get registration by component ID"""
        return self._registrations.get(component_id)

    def list_components(self, component_type: Optional[str] = None) -> List[ComponentRegistration]:
        """
        List all registered components, optionally filtered by type.

        Args:
            component_type: Filter by component type ("cms" or "ecommerce")

        Returns:
            List of ComponentRegistration objects
        """

        registrations = list(self._registrations.values())

        if component_type:
            registrations = [
                reg for reg in registrations
                if reg.component_type == component_type
            ]

        return registrations

    def unregister_component(self, component_id: str) -> bool:
        """
        Unregister a component from the integration layer.

        Args:
            component_id: ID of component to unregister

        Returns:
            True if unregistered successfully, False if not found
        """

        if component_id in self._components:
            del self._components[component_id]
            del self._registrations[component_id]
            return True

        return False

    def validate_all_components(self) -> Dict[str, bool]:
        """
        Validate all registered components.

        Returns:
            Dictionary mapping component IDs to validation results
        """

        results = {}

        for component_id, component in self._components.items():
            try:
                # Validate component configuration
                registration = self._registrations[component_id]
                is_valid = component.validate_configuration(registration.configuration)
                results[component_id] = is_valid
            except Exception:
                results[component_id] = False

        return results

    def get_components_by_provider(self, provider_name: str) -> List[ComposableComponent]:
        """
        Get all components for a specific provider.

        Args:
            provider_name: Provider name to filter by

        Returns:
            List of components for the provider
        """

        components = []

        for registration in self._registrations.values():
            if registration.provider_name == provider_name:
                component = self._components[registration.component_id]
                components.append(component)

        return components

    def estimate_total_cost(self, requirements: Dict[str, Any]) -> CostBreakdown:
        """
        Estimate total cost for all registered components.

        Args:
            requirements: Client requirements and usage estimates

        Returns:
            Aggregated CostBreakdown
        """

        total_breakdown = CostBreakdown()

        for component in self._components.values():
            component_cost = component.estimate_monthly_cost(requirements)

            # Aggregate costs (simplified - would need more sophisticated logic)
            total_breakdown.cms_monthly_cost += component_cost.cms_monthly_cost
            total_breakdown.ecommerce_monthly_cost += component_cost.ecommerce_monthly_cost
            total_breakdown.aws_hosting_cost += component_cost.aws_hosting_cost

        return total_breakdown


# Global component registry instance
component_registry = ComponentRegistry()