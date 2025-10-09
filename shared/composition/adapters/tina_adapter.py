"""
Tina CMS Adapter

Concrete implementation of the provider adapter for Tina CMS.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from shared.composition.provider_adapter_registry import BaseProviderHandler
from models.composition import UnifiedContent, ContentType, ContentStatus

logger = logging.getLogger(__name__)

class TinaCMSHandler(BaseProviderHandler):
    def __init__(self):
        super().__init__("tina")

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        try:
            return [UnifiedContent(
                id=f"tina:{webhook_data.get('_id', 'unknown')}",
                title=webhook_data.get('title', 'Untitled'),
                slug=webhook_data.get('slug', 'untitled'),
                content_type=ContentType.ARTICLE,
                status=ContentStatus.PUBLISHED,
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data=webhook_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )]
        except Exception as e:
            logger.error(f"Tina normalization error: {str(e)}")
            return []

    def get_supported_events(self) -> List[str]:
        return ['content.create', 'content.update', 'content.delete']

__all__ = ['TinaCMSHandler']