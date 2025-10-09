"""
Contentful CMS Adapter

Concrete implementation of the provider adapter for Contentful CMS.
This adapter enables seamless integration with Contentful's enterprise content platform.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from shared.composition.provider_adapter_registry import BaseProviderHandler
from models.composition import UnifiedContent, ContentType, ContentStatus

logger = logging.getLogger(__name__)

class ContentfulCMSHandler(BaseProviderHandler):
    def __init__(self):
        super().__init__("contentful")

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