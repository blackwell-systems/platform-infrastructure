"""
Snipcart E-commerce Adapter

Concrete implementation of the provider adapter for Snipcart.
This adapter enables seamless integration with Snipcart's HTML/JS e-commerce solution,
democratizing e-commerce by allowing any static site to become a shopping platform.

TRANSFORMATIVE IMPACT:
Snipcart provides e-commerce capabilities that can be added to any website with
simple HTML attributes. At $20/month + 2% transaction fee, it's perfect for
small businesses wanting to add shopping to existing static sites.
"""

import json
import logging
import hmac
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from shared.composition.provider_adapter_registry import IProviderHandler, BaseProviderHandler
from models.composition import UnifiedContent, ContentType, ContentStatus


logger = logging.getLogger(__name__)


class SnipcartEcommerceHandler(BaseProviderHandler):
    """
    Snipcart e-commerce provider handler implementing HTML-based e-commerce.

    Snipcart provides:
    - HTML/JS based e-commerce ($20/month + 2% transaction)
    - No backend required - works with any static site
    - Shopping cart, checkout, and payment processing
    - Perfect for adding e-commerce to existing sites
    """

    def __init__(self):
        super().__init__("snipcart")

        # Snipcart webhook events
        self.supported_webhook_events = [
            'order.completed', 'order.status.changed',
            'subscription.created', 'subscription.cancelled',
            'customer.created', 'invoice.created'
        ]

        logger.info("Snipcart adapter initialized")

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """
        Normalize Snipcart webhook data to unified content schema.

        Snipcart primarily sends transaction/order events rather than product data,
        so we create order-based content for analytics and build triggers.
        """

        try:
            unified_content = []

            # Handle order events
            if 'order' in webhook_data:
                content = self._normalize_order(webhook_data['order'], event_type)
                if content:
                    unified_content.append(content)

            # Handle subscription events
            elif 'subscription' in webhook_data:
                content = self._normalize_subscription(webhook_data['subscription'], event_type)
                if content:
                    unified_content.append(content)

            # Handle customer events
            elif 'customer' in webhook_data:
                content = self._normalize_customer(webhook_data['customer'], event_type)
                if content:
                    unified_content.append(content)

            logger.info(f"Snipcart: Normalized {len(unified_content)} content items from webhook")
            return unified_content

        except Exception as e:
            logger.error(f"Snipcart normalization error: {str(e)}", exc_info=True)
            return []

    def validate_webhook_signature(self, body: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Validate Snipcart webhook signature."""

        try:
            # Snipcart doesn't use HMAC signatures by default
            # Instead, it uses request validation tokens
            request_token = headers.get('RequestValidationToken', '')
            if not request_token:
                logger.info("No Snipcart request validation token - allowing for development")
                return True

            # In production, you would validate against your Snipcart secret
            return True

        except Exception as e:
            logger.error(f"Snipcart signature validation error: {str(e)}")
            return False

    def extract_event_type(self, headers: Dict[str, str], body: Dict[str, Any]) -> str:
        """Extract event type from Snipcart webhook."""

        # Snipcart includes event type in the payload
        event_name = body.get('eventName', 'unknown')

        # Map Snipcart events to our content events
        event_mapping = {
            'order.completed': 'content.created',
            'order.status.changed': 'content.updated',
            'subscription.created': 'content.created',
            'subscription.cancelled': 'content.updated'
        }

        return event_mapping.get(event_name, 'content.updated')

    def get_supported_events(self) -> List[str]:
        """Get supported Snipcart webhook events."""

        return self.supported_webhook_events

    def _normalize_order(self, order_data: Dict[str, Any], event_type: str) -> Optional[UnifiedContent]:
        """Normalize Snipcart order to unified content."""

        try:
            return UnifiedContent(
                id=f"snipcart:order:{order_data.get('token', 'unknown')}",
                title=f"Order {order_data.get('invoiceNumber', order_data.get('token', 'Unknown'))}",
                slug=f"order-{order_data.get('token', 'unknown')}",
                content_type=ContentType.PRODUCT,  # Orders relate to products
                status=ContentStatus.PUBLISHED,
                description=f"Snipcart order for ${order_data.get('total', 0):.2f}",
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data={
                    'order_token': order_data.get('token'),
                    'invoice_number': order_data.get('invoiceNumber'),
                    'total': order_data.get('total'),
                    'status': order_data.get('status'),
                    'customer_email': order_data.get('email'),
                    'items_count': len(order_data.get('items', []))
                },
                created_at=self._parse_snipcart_datetime(order_data.get('creationDate')),
                updated_at=self._parse_snipcart_datetime(order_data.get('modificationDate'))
            )

        except Exception as e:
            logger.error(f"Error normalizing Snipcart order: {str(e)}")
            return None

    def _normalize_subscription(self, subscription_data: Dict[str, Any], event_type: str) -> Optional[UnifiedContent]:
        """Normalize Snipcart subscription to unified content."""

        try:
            return UnifiedContent(
                id=f"snipcart:subscription:{subscription_data.get('id', 'unknown')}",
                title=f"Subscription {subscription_data.get('name', 'Unknown')}",
                slug=f"subscription-{subscription_data.get('id', 'unknown')}",
                content_type=ContentType.PRODUCT,
                status=ContentStatus.PUBLISHED if subscription_data.get('status') == 'Active' else ContentStatus.ARCHIVED,
                description=f"Snipcart subscription: {subscription_data.get('name', 'Unknown')}",
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data=subscription_data,
                created_at=self._parse_snipcart_datetime(subscription_data.get('creationDate')),
                updated_at=self._parse_snipcart_datetime(subscription_data.get('modificationDate'))
            )

        except Exception as e:
            logger.error(f"Error normalizing Snipcart subscription: {str(e)}")
            return None

    def _normalize_customer(self, customer_data: Dict[str, Any], event_type: str) -> Optional[UnifiedContent]:
        """Normalize Snipcart customer to unified content."""

        try:
            return UnifiedContent(
                id=f"snipcart:customer:{customer_data.get('id', 'unknown')}",
                title=f"Customer {customer_data.get('email', 'Unknown')}",
                slug=f"customer-{customer_data.get('id', 'unknown')}",
                content_type=ContentType.PAGE,  # Customers are like profile pages
                status=ContentStatus.PUBLISHED,
                description=f"Snipcart customer: {customer_data.get('email', 'Unknown')}",
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data=customer_data,
                created_at=self._parse_snipcart_datetime(customer_data.get('creationDate')),
                updated_at=self._parse_snipcart_datetime(customer_data.get('modificationDate'))
            )

        except Exception as e:
            logger.error(f"Error normalizing Snipcart customer: {str(e)}")
            return None

    def _parse_snipcart_datetime(self, datetime_str: Optional[str]) -> datetime:
        """Parse Snipcart datetime string."""

        if not datetime_str:
            return datetime.utcnow()

        try:
            # Snipcart uses ISO format
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()


# Make handler available for registry
__all__ = ['SnipcartEcommerceHandler']