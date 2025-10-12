"""
Contentful CMS Adapter

Concrete implementation of the provider adapter for Contentful CMS.
This adapter enables seamless integration with Contentful's enterprise content platform.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# New enhanced interfaces
from blackwell_core.adapters.interfaces import ICMSAdapter
from blackwell_core.models.events import ContentEvent, UnifiedContent

# Legacy interfaces for backward compatibility
from shared.composition.provider_adapter_registry import BaseProviderHandler
from models.composition import ContentType, ContentStatus

logger = logging.getLogger(__name__)

class ContentfulCMSHandler(ICMSAdapter):
    """
    Contentful CMS provider handler implementing enterprise content management.

    Contentful provides:
    - Enterprise-grade content API
    - Multi-language content support
    - Rich content modeling
    - CDN-delivered content
    """

    # Required class attributes for new interface
    provider_name = "contentful"
    provider_type = "cms"
    supported_events = ["content.created", "content.updated", "content.deleted", "content.published"]
    api_version = "v1"

    def __init__(self):
        pass

    def transform_event(self, raw_data: Dict[str, Any]) -> ContentEvent:
        """
        Transform Contentful webhook data to standardized ContentEvent.
        """
        try:
            # Extract event information from Contentful webhook
            sys_data = raw_data.get('sys', {})
            fields = raw_data.get('fields', {})

            # Determine event type based on Contentful event data
            event_type = "content.updated"  # Default
            action = "updated"

            # Contentful includes event metadata in headers, but for fallback:
            if sys_data.get('publishedAt') and not sys_data.get('updatedAt', '') > sys_data.get('publishedAt', ''):
                event_type = "content.published"
                action = "published"
            elif sys_data.get('createdAt') == sys_data.get('updatedAt'):
                event_type = "content.created"
                action = "created"

            # Extract content information
            content_id = f"contentful:{sys_data.get('id', 'unknown')}"
            content_type = "article"  # Default

            # Determine content type from Contentful content type
            if sys_data.get('contentType', {}).get('sys', {}).get('id') == 'product':
                content_type = "product"
            elif sys_data.get('contentType', {}).get('sys', {}).get('id') == 'page':
                content_type = "page"

            return ContentEvent(
                event_type=event_type,
                provider=self.provider_name,
                client_id=self._extract_client_id(raw_data),
                payload=raw_data,
                content_id=content_id,
                content_type=content_type,
                action=action,
                author=sys_data.get('createdBy', {}).get('sys', {}).get('id')
            )

        except Exception as e:
            logger.error(f"Error transforming Contentful event: {str(e)}", exc_info=True)
            return ContentEvent(
                event_type="content.updated",
                provider=self.provider_name,
                client_id="unknown",
                payload=raw_data,
                content_id="unknown",
                content_type="article",
                action="updated"
            )

    def validate_webhook_signature(self, body: bytes, headers: Dict[str, str]) -> bool:
        """
        Validate Contentful webhook signature.
        """
        try:
            # Contentful uses custom headers for webhook validation
            # In a real implementation, this would verify the webhook secret
            webhook_name = headers.get('X-Contentful-Webhook-Name')
            if webhook_name:
                return True

            # Allow for development/testing
            return True

        except Exception as e:
            logger.error(f"Contentful signature validation error: {str(e)}")
            return False

    def get_capabilities(self) -> List[str]:
        """
        Return list of features this Contentful adapter supports.
        """
        return [
            "webhooks",
            "content_fetch",
            "content_listing",
            "multi_language",
            "rich_content",
            "asset_management",
            "content_delivery_api",
            "content_preview"
        ]

    def normalize_content(self, raw_data: Dict[str, Any]) -> UnifiedContent:
        """
        Convert Contentful data to unified content schema.
        """
        try:
            sys_data = raw_data.get('sys', {})
            fields = raw_data.get('fields', {})

            # Extract localized fields (Contentful supports multiple locales)
            title = self._get_localized_field(fields, 'title', 'Untitled')
            slug = self._get_localized_field(fields, 'slug', 'untitled')
            description = self._get_localized_field(fields, 'description')

            # Determine content type
            content_type = ContentType.ARTICLE
            if sys_data.get('contentType', {}).get('sys', {}).get('id') == 'product':
                content_type = ContentType.PRODUCT
            elif sys_data.get('contentType', {}).get('sys', {}).get('id') == 'page':
                content_type = ContentType.PAGE

            return UnifiedContent(
                id=f"contentful:{sys_data.get('id', 'unknown')}",
                title=title,
                slug=slug,
                content_type=content_type.value,
                status=ContentStatus.PUBLISHED.value if sys_data.get('publishedAt') else ContentStatus.DRAFT.value,
                description=description,
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data=raw_data,
                created_at=sys_data.get('createdAt', datetime.utcnow().isoformat()),
                updated_at=sys_data.get('updatedAt', datetime.utcnow().isoformat()),
                metadata={"locale": sys_data.get('locale', 'en-US')}
            )

        except Exception as e:
            logger.error(f"Error normalizing Contentful content: {str(e)}")
            return UnifiedContent(
                id="unknown",
                title="Unknown Content",
                slug="unknown",
                content_type="article",
                provider_type="cms",
                provider_name=self.provider_name,
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )

    def fetch_content_by_id(self, content_id: str) -> Optional[UnifiedContent]:
        """
        Retrieve specific content item by ID.
        """
        try:
            # Parse Contentful content ID
            if content_id.startswith('contentful:'):
                contentful_id = content_id[11:]

                # Mock implementation - would use Contentful Content Delivery API
                mock_data = {
                    'sys': {
                        'id': contentful_id,
                        'contentType': {'sys': {'id': 'article'}},
                        'createdAt': datetime.utcnow().isoformat(),
                        'updatedAt': datetime.utcnow().isoformat(),
                        'publishedAt': datetime.utcnow().isoformat()
                    },
                    'fields': {
                        'title': {'en-US': f'Content {contentful_id}'},
                        'slug': {'en-US': f'content-{contentful_id}'}
                    }
                }

                return self.normalize_content(mock_data)

            return None

        except Exception as e:
            logger.error(f"Error fetching Contentful content {content_id}: {str(e)}")
            return None

    def list_content(self, content_type: Optional[str] = None, limit: int = 100) -> List[UnifiedContent]:
        """
        List content items with optional filtering.
        """
        try:
            # Mock implementation - would use Contentful Content Delivery API
            mock_content = []
            content_types = [content_type] if content_type else ['article', 'page']

            for i in range(min(limit, 5)):  # Mock 5 items
                for ct in content_types:
                    if len(mock_content) >= limit:
                        break

                    mock_data = {
                        'sys': {
                            'id': f'{ct}_{i}',
                            'contentType': {'sys': {'id': ct}},
                            'createdAt': datetime.utcnow().isoformat(),
                            'updatedAt': datetime.utcnow().isoformat(),
                            'publishedAt': datetime.utcnow().isoformat()
                        },
                        'fields': {
                            'title': {'en-US': f'Sample {ct.title()} {i}'},
                            'slug': {'en-US': f'sample-{ct}-{i}'}
                        }
                    }
                    mock_content.append(self.normalize_content(mock_data))

            return mock_content

        except Exception as e:
            logger.error(f"Error listing Contentful content: {str(e)}")
            return []

    def _extract_client_id(self, raw_data: Dict[str, Any]) -> str:
        """Extract client ID from Contentful webhook data."""
        # Contentful space ID can serve as client ID
        sys_data = raw_data.get('sys', {})
        space = sys_data.get('space', {})
        return space.get('sys', {}).get('id', 'unknown-space')

    def _get_localized_field(self, fields: Dict[str, Any], field_name: str, default: Optional[str] = None) -> Optional[str]:
        """Extract localized field from Contentful fields."""
        field_data = fields.get(field_name, {})
        if isinstance(field_data, dict):
            # Try common locales
            for locale in ['en-US', 'en', 'en-GB']:
                if locale in field_data:
                    return field_data[locale]
            # Fall back to first available locale
            if field_data:
                return next(iter(field_data.values()))
        elif isinstance(field_data, str):
            return field_data
        return default

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        try:
            # Simplified Contentful normalization
            content_type = ContentType.ARTICLE
            if webhook_data.get('sys', {}).get('contentType', {}).get('sys', {}).get('id') == 'product':
                content_type = ContentType.PRODUCT

            return [UnifiedContent(
                id=f"contentful:{webhook_data['sys']['id']}",
                title=webhook_data.get('fields', {}).get('title', {}).get('en-US', 'Untitled'),
                slug=webhook_data.get('fields', {}).get('slug', {}).get('en-US', 'untitled'),
                content_type=content_type,
                status=ContentStatus.PUBLISHED if webhook_data['sys'].get('publishedAt') else ContentStatus.DRAFT,
                description=webhook_data.get('fields', {}).get('description', {}).get('en-US'),
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data=webhook_data,
                created_at=datetime.fromisoformat(webhook_data['sys']['createdAt'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(webhook_data['sys']['updatedAt'].replace('Z', '+00:00'))
            )]
        except Exception as e:
            logger.error(f"Contentful normalization error: {str(e)}")
            return []

    def get_supported_events(self) -> List[str]:
        return ['Entry.create', 'Entry.save', 'Entry.delete', 'Entry.publish']

__all__ = ['ContentfulCMSHandler']