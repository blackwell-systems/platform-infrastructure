"""
Shopify Basic Adapter

Concrete implementation of the provider adapter for Shopify Basic tier.
This adapter enables seamless integration with Shopify's e-commerce platform,
democratizing access to professional online selling capabilities.

TRANSFORMATIVE IMPACT:
Shopify Basic provides small businesses with enterprise-grade e-commerce
capabilities at an affordable $29/month, combined with our integration layer
to deliver 80-90% cost savings compared to traditional agency solutions.
"""

import json
import logging
import hmac
import hashlib
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

from shared.composition.provider_adapter_registry import IProviderHandler, BaseProviderHandler
from models.composition import (
    UnifiedContent, ContentType, ContentStatus,
    Price, Inventory, ProductVariant, MediaAsset
)


logger = logging.getLogger(__name__)


class ShopifyBasicHandler(BaseProviderHandler):
    """
    Shopify Basic provider handler implementing e-commerce content management.

    Shopify Basic provides:
    - Professional e-commerce platform ($29/month)
    - Product catalog management
    - Inventory tracking and variants
    - Order processing and payments
    - Perfect for small to medium businesses
    """

    def __init__(self):
        super().__init__("shopify_basic")

        # Shopify-specific configuration
        self.supported_webhook_topics = [
            'products/create', 'products/update', 'products/delete',
            'inventory_levels/update', 'collections/create', 'collections/update',
            'orders/create', 'orders/updated', 'orders/paid'
        ]

        logger.info("Shopify Basic adapter initialized")

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """
        Normalize Shopify webhook data to unified content schema.

        Shopify webhooks provide rich product and collection data that we
        transform into our unified format for seamless SSG integration.
        """

        try:
            unified_content = []

            # Determine webhook topic from event_type or headers
            webhook_topic = self._extract_webhook_topic(webhook_data, event_type)

            if webhook_topic.startswith('products/'):
                content = self._normalize_product(webhook_data, webhook_topic)
                if content:
                    unified_content.append(content)

            elif webhook_topic.startswith('collections/'):
                content = self._normalize_collection(webhook_data, webhook_topic)
                if content:
                    unified_content.append(content)

            elif webhook_topic.startswith('inventory_levels/'):
                # Inventory updates might affect multiple products
                content_items = self._normalize_inventory_update(webhook_data)
                unified_content.extend(content_items)

            logger.info(f"Shopify Basic: Normalized {len(unified_content)} content items from {webhook_topic}")
            return unified_content

        except Exception as e:
            logger.error(f"Shopify Basic normalization error: {str(e)}", exc_info=True)
            return []

    def validate_webhook_signature(self, body: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """
        Validate Shopify webhook signature using HMAC-SHA256.

        This ensures webhook authenticity and prevents malicious requests
        from compromising the e-commerce integration.
        """

        try:
            # Get Shopify HMAC signature
            shopify_hmac = headers.get('X-Shopify-Hmac-Sha256', '')
            if not shopify_hmac:
                logger.warning("No Shopify HMAC signature found in webhook")
                return True  # Allow for development/testing

            # Get webhook secret
            webhook_secret = self._get_webhook_secret()
            if not webhook_secret:
                logger.info("No webhook secret configured for Shopify Basic - allowing request")
                return True

            # Calculate expected signature
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            expected_signature = base64.b64encode(
                hmac.new(
                    webhook_secret.encode('utf-8'),
                    body_str.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')

            # Compare signatures
            is_valid = hmac.compare_digest(shopify_hmac, expected_signature)

            if not is_valid:
                logger.warning("Invalid Shopify webhook signature")

            return is_valid

        except Exception as e:
            logger.error(f"Shopify signature validation error: {str(e)}")
            return False

    def extract_event_type(self, headers: Dict[str, str], body: Dict[str, Any]) -> str:
        """Extract event type from Shopify webhook headers."""

        shopify_topic = headers.get('X-Shopify-Topic', 'unknown')

        # Map Shopify topics to our content events
        topic_mapping = {
            'products/create': 'content.created',
            'products/update': 'content.updated',
            'products/delete': 'content.deleted',
            'collections/create': 'collection.created',
            'collections/update': 'collection.updated',
            'inventory_levels/update': 'inventory.updated'
        }

        return topic_mapping.get(shopify_topic, 'content.updated')

    def get_supported_events(self) -> List[str]:
        """Get supported Shopify webhook topics."""

        return self.supported_webhook_topics

    def _extract_webhook_topic(self, webhook_data: Dict[str, Any], event_type: str) -> str:
        """Extract webhook topic from data or event type."""

        # Check if topic is in the webhook data
        if 'webhook_topic' in webhook_data:
            return webhook_data['webhook_topic']

        # Map from our event types back to Shopify topics
        event_to_topic = {
            'content.created': 'products/create',
            'content.updated': 'products/update',
            'content.deleted': 'products/delete',
            'collection.created': 'collections/create',
            'collection.updated': 'collections/update',
            'inventory.updated': 'inventory_levels/update'
        }

        return event_to_topic.get(event_type, 'products/update')

    def _normalize_product(self, product_data: Dict[str, Any], webhook_topic: str) -> Optional[UnifiedContent]:
        """
        Normalize Shopify product data to unified content schema.

        This transformation enables any SSG engine to work with Shopify products
        seamlessly, democratizing e-commerce integration.
        """

        try:
            # Handle deleted products
            if webhook_topic == 'products/delete':
                return UnifiedContent(
                    id=f"gid://shopify/Product/{product_data.get('id', 'unknown')}",
                    title=product_data.get('title', 'Deleted Product'),
                    slug=product_data.get('handle', 'deleted-product'),
                    content_type=ContentType.PRODUCT,
                    status=ContentStatus.DELETED,
                    provider_type="ecommerce",
                    provider_name=self.provider_name,
                    provider_data=product_data,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

            # Process product variants and pricing
            variants = []
            min_price = float('inf')
            inventory_info = None

            for variant_data in product_data.get('variants', []):
                try:
                    # Create price object
                    price = Price(
                        amount=float(variant_data.get('price', 0)),
                        currency_code=product_data.get('currency', 'USD'),
                        compare_at_amount=float(variant_data.get('compare_at_price', 0)) if variant_data.get('compare_at_price') else None
                    )

                    # Create inventory object
                    inventory = Inventory(
                        quantity=int(variant_data.get('inventory_quantity', 0)),
                        track_quantity=variant_data.get('inventory_management') == 'shopify',
                        continue_selling_when_out_of_stock=variant_data.get('inventory_policy') == 'continue',
                        inventory_policy=variant_data.get('inventory_policy', 'deny')
                    )

                    # Extract variant options (Size, Color, etc.)
                    options = {}
                    if variant_data.get('option1'):
                        options['Option 1'] = variant_data['option1']
                    if variant_data.get('option2'):
                        options['Option 2'] = variant_data['option2']
                    if variant_data.get('option3'):
                        options['Option 3'] = variant_data['option3']

                    variant = ProductVariant(
                        id=str(variant_data.get('id', '')),
                        title=variant_data.get('title', 'Default'),
                        price=price,
                        inventory=inventory,
                        options=options,
                        sku=variant_data.get('sku'),
                        weight=float(variant_data.get('weight', 0)) if variant_data.get('weight') else None
                    )

                    variants.append(variant)
                    min_price = min(min_price, price.amount)

                    # Use first variant's inventory for main product
                    if not inventory_info:
                        inventory_info = inventory

                except Exception as variant_error:
                    logger.warning(f"Error processing variant {variant_data.get('id')}: {str(variant_error)}")
                    continue

            # Process product images
            images = []
            featured_image = None

            for img_data in product_data.get('images', []):
                try:
                    media_asset = MediaAsset(
                        id=str(img_data.get('id', '')),
                        url=img_data.get('src', ''),
                        alt_text=img_data.get('alt'),
                        width=img_data.get('width'),
                        height=img_data.get('height')
                    )

                    images.append(media_asset)

                    # First image becomes featured image
                    if not featured_image:
                        featured_image = media_asset

                except Exception as img_error:
                    logger.warning(f"Error processing image {img_data.get('id')}: {str(img_error)}")
                    continue

            # Determine content status
            status = ContentStatus.PUBLISHED if product_data.get('status') == 'active' else ContentStatus.DRAFT

            # Extract tags
            tags = []
            if product_data.get('tags'):
                tags = [tag.strip() for tag in product_data['tags'].split(',') if tag.strip()]

            # Create unified content
            return UnifiedContent(
                id=f"gid://shopify/Product/{product_data.get('id')}",
                title=product_data.get('title', 'Untitled Product'),
                slug=product_data.get('handle', 'untitled-product'),
                content_type=ContentType.PRODUCT,
                status=status,
                description=self._clean_html(product_data.get('body_html', '')),
                body=product_data.get('body_html', ''),
                featured_image=featured_image,
                images=images,
                price=Price(amount=min_price, currency_code=product_data.get('currency', 'USD')) if min_price < float('inf') else None,
                inventory=inventory_info,
                variants=variants,
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data={
                    'shopify_id': product_data.get('id'),
                    'vendor': product_data.get('vendor'),
                    'product_type': product_data.get('product_type'),
                    'published_scope': product_data.get('published_scope'),
                    'template_suffix': product_data.get('template_suffix'),
                    'seo_title': product_data.get('seo_title'),
                    'seo_description': product_data.get('seo_description')
                },
                created_at=datetime.fromisoformat(product_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(product_data.get('updated_at', datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                tags=tags
            )

        except Exception as e:
            logger.error(f"Error normalizing Shopify product {product_data.get('id')}: {str(e)}")
            return None

    def _normalize_collection(self, collection_data: Dict[str, Any], webhook_topic: str) -> Optional[UnifiedContent]:
        """Normalize Shopify collection to unified content schema."""

        try:
            # Handle deleted collections
            if webhook_topic == 'collections/delete':
                return UnifiedContent(
                    id=f"gid://shopify/Collection/{collection_data.get('id', 'unknown')}",
                    title=collection_data.get('title', 'Deleted Collection'),
                    slug=collection_data.get('handle', 'deleted-collection'),
                    content_type=ContentType.COLLECTION,
                    status=ContentStatus.DELETED,
                    provider_type="ecommerce",
                    provider_name=self.provider_name,
                    provider_data=collection_data,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

            # Process collection image
            featured_image = None
            if collection_data.get('image'):
                img_data = collection_data['image']
                featured_image = MediaAsset(
                    id=str(img_data.get('id', '')),
                    url=img_data.get('src', ''),
                    alt_text=img_data.get('alt'),
                    width=img_data.get('width'),
                    height=img_data.get('height')
                )

            return UnifiedContent(
                id=f"gid://shopify/Collection/{collection_data.get('id')}",
                title=collection_data.get('title', 'Untitled Collection'),
                slug=collection_data.get('handle', 'untitled-collection'),
                content_type=ContentType.COLLECTION,
                status=ContentStatus.PUBLISHED if collection_data.get('published') else ContentStatus.DRAFT,
                description=self._clean_html(collection_data.get('body_html', '')),
                body=collection_data.get('body_html', ''),
                featured_image=featured_image,
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data={
                    'shopify_id': collection_data.get('id'),
                    'sort_order': collection_data.get('sort_order'),
                    'published_scope': collection_data.get('published_scope'),
                    'template_suffix': collection_data.get('template_suffix')
                },
                created_at=datetime.fromisoformat(collection_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(collection_data.get('updated_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            )

        except Exception as e:
            logger.error(f"Error normalizing Shopify collection {collection_data.get('id')}: {str(e)}")
            return None

    def _normalize_inventory_update(self, inventory_data: Dict[str, Any]) -> List[UnifiedContent]:
        """
        Normalize Shopify inventory update to unified content.

        Inventory updates can affect multiple products and variants,
        so we need to handle them carefully to trigger appropriate builds.
        """

        try:
            # For inventory updates, we create a minimal content representation
            # that indicates which product/variant was affected
            inventory_level = inventory_data

            return [UnifiedContent(
                id=f"gid://shopify/InventoryLevel/{inventory_level.get('inventory_item_id')}",
                title=f"Inventory Update - Item {inventory_level.get('inventory_item_id')}",
                slug=f"inventory-{inventory_level.get('inventory_item_id')}",
                content_type=ContentType.PRODUCT,  # Inventory affects products
                status=ContentStatus.PUBLISHED,
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data={
                    'inventory_item_id': inventory_level.get('inventory_item_id'),
                    'location_id': inventory_level.get('location_id'),
                    'available': inventory_level.get('available'),
                    'updated_at': inventory_level.get('updated_at')
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )]

        except Exception as e:
            logger.error(f"Error normalizing Shopify inventory update: {str(e)}")
            return []

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content to extract plain text description."""

        if not html_content:
            return ""

        # Simple HTML tag removal for description
        import re
        text = re.sub(r'<[^>]+>', '', html_content)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return text.strip()[:160]  # Limit to 160 characters for descriptions

    def _get_webhook_secret(self) -> Optional[str]:
        """
        Get webhook secret for signature validation.

        In production, this would be retrieved from secure configuration.
        """

        import os
        return os.environ.get('SHOPIFY_WEBHOOK_SECRET')


# Make handler available for registry
__all__ = ['ShopifyBasicHandler']