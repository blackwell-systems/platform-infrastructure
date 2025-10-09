"""
Foxy E-commerce Adapter

Concrete implementation of the provider adapter for Foxy Cart.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from shared.composition.provider_adapter_registry import BaseProviderHandler
from models.composition import UnifiedContent, ContentType, ContentStatus

logger = logging.getLogger(__name__)

class FoxyEcommerceHandler(BaseProviderHandler):
    def __init__(self):
        super().__init__("foxy")

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        try:
            return [UnifiedContent(
                id=f"foxy:{webhook_data.get('id', 'unknown')}",
                title=f"Foxy Transaction {webhook_data.get('id', 'Unknown')}",
                slug=f"transaction-{webhook_data.get('id', 'unknown')}",
                content_type=ContentType.PRODUCT,
                status=ContentStatus.PUBLISHED,
                provider_type="ecommerce",
                provider_name=self.provider_name,
                provider_data=webhook_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )]
        except Exception as e:
            logger.error(f"Foxy normalization error: {str(e)}")
            return []

    def get_supported_events(self) -> List[str]:
        return ['transaction/create', 'subscription/create']

__all__ = ['FoxyEcommerceHandler']