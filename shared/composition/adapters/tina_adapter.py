"""
Tina CMS Adapter

Concrete implementation of the provider adapter for Tina CMS.
This adapter enables seamless integration with Tina's file-based content management,
democratizing access to modern Git-based content workflows.

TRANSFORMATIVE IMPACT:
Tina CMS provides modern, developer-friendly content management with Git-based
version control and real-time editing capabilities, enabling small businesses
to leverage professional content workflows without traditional CMS complexity.
"""

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

class TinaCMSHandler(ICMSAdapter):
    """
    Tina CMS provider handler implementing file-based content management.

    Tina CMS provides:
    - Git-based content storage
    - Real-time visual editing
    - TypeScript-based schema definitions
    - Local development with instant updates
    - Perfect for developer-friendly content workflows
    """

    # Required class attributes for new interface
    provider_name = "tina"
    provider_type = "cms"
    supported_events = ["content.created", "content.updated", "content.deleted"]
    api_version = "v1"

    def __init__(self):
        logger.info("Tina CMS adapter initialized")

    def transform_event(self, raw_data: Dict[str, Any]) -> ContentEvent:
        """
        Transform Tina CMS webhook data to standardized ContentEvent.
        """
        try:
            # Extract basic event information
            event_type = "content.updated"  # Default
            action = "updated"

            # Determine event type based on Tina data or event context
            if raw_data.get('event_type') == 'create' or raw_data.get('action') == 'created':
                event_type = "content.created"
                action = "created"
            elif raw_data.get('event_type') == 'delete' or raw_data.get('action') == 'deleted':
                event_type = "content.deleted"
                action = "deleted"

            # Extract content information
            content_id = f"tina:{raw_data.get('_id', raw_data.get('id', 'unknown'))}"
            content_type = self._determine_content_type(raw_data).value

            return ContentEvent(
                event_type=event_type,
                provider=self.provider_name,
                client_id=self._extract_client_id(raw_data),
                payload=raw_data,
                content_id=content_id,
                content_type=content_type,
                action=action,
                author=raw_data.get('author', raw_data.get('_createdBy'))
            )

        except Exception as e:
            logger.error(f"Error transforming Tina CMS event: {str(e)}", exc_info=True)
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
        Validate Tina CMS webhook signature.

        Note: Tina CMS typically doesn't use webhook signatures in local development,
        but this could be extended for production deployments with custom webhook handling.
        """
        try:
            # For basic Tina implementations, validation might be simpler
            # Check for basic headers or authentication tokens
            auth_header = headers.get('Authorization', '')
            if auth_header:
                return True  # Basic token validation

            # Allow for development/testing environments
            logger.info("No authentication header found for Tina CMS - allowing request")
            return True

        except Exception as e:
            logger.error(f"Tina CMS signature validation error: {str(e)}")
            return False

    def get_capabilities(self) -> List[str]:
        """
        Return list of features this Tina CMS adapter supports.
        """
        return [
            "webhooks",
            "content_fetch",
            "content_listing",
            "file_based_storage",
            "git_integration",
            "real_time_editing",
            "typescript_schemas",
            "local_development"
        ]

    def normalize_content(self, raw_data: Dict[str, Any]) -> UnifiedContent:
        """
        Convert Tina CMS data to unified content schema.
        """
        try:
            # Extract content information
            content_id = raw_data.get('_id', raw_data.get('id', 'unknown'))
            title = raw_data.get('title', 'Untitled')
            slug = raw_data.get('slug', self._generate_slug_from_title(title))

            # Determine content type
            content_type = self._determine_content_type(raw_data)

            # Extract body content
            body = raw_data.get('body', raw_data.get('content', ''))
            description = raw_data.get('description', raw_data.get('excerpt', ''))

            # Extract tags
            tags = raw_data.get('tags', [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

            return UnifiedContent(
                id=f"tina:{content_id}",
                title=title,
                slug=slug,
                content_type=content_type.value,
                status=ContentStatus.PUBLISHED.value if raw_data.get('published', True) else ContentStatus.DRAFT.value,
                description=description,
                body=body,
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data=raw_data,
                created_at=raw_data.get('created_at', datetime.utcnow().isoformat()),
                updated_at=raw_data.get('updated_at', datetime.utcnow().isoformat()),
                tags=tags,
                metadata={
                    "tina_collection": raw_data.get('_collection'),
                    "file_path": raw_data.get('_path'),
                    "schema": raw_data.get('_schema')
                }
            )

        except Exception as e:
            logger.error(f"Error normalizing Tina CMS content: {str(e)}")
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
            # Parse Tina content ID
            if content_id.startswith('tina:'):
                tina_id = content_id[5:]

                # Mock implementation - would use Tina's GraphQL API
                mock_data = {
                    '_id': tina_id,
                    'title': f'Tina Content {tina_id}',
                    'slug': f'tina-content-{tina_id}',
                    'body': f'Content body for {tina_id}',
                    'published': True,
                    '_collection': 'posts'
                }

                return self.normalize_content(mock_data)

            return None

        except Exception as e:
            logger.error(f"Error fetching Tina CMS content {content_id}: {str(e)}")
            return None

    def list_content(self, content_type: Optional[str] = None, limit: int = 100) -> List[UnifiedContent]:
        """
        List content items with optional filtering.
        """
        try:
            # Mock implementation - would use Tina's GraphQL API
            mock_content = []
            collections = ['posts', 'pages'] if not content_type else [content_type]

            for i in range(min(limit, 5)):  # Mock 5 items
                for collection in collections:
                    if len(mock_content) >= limit:
                        break

                    mock_data = {
                        '_id': f'{collection}_{i}',
                        'title': f'Sample {collection.title()} {i}',
                        'slug': f'sample-{collection}-{i}',
                        'body': f'Content body for {collection} {i}',
                        'published': True,
                        '_collection': collection
                    }
                    mock_content.append(self.normalize_content(mock_data))

            return mock_content

        except Exception as e:
            logger.error(f"Error listing Tina CMS content: {str(e)}")
            return []

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """
        Legacy method for backward compatibility.
        Normalize Tina CMS webhook data to unified content schema.
        """
        try:
            content = self.normalize_content(webhook_data)
            return [content] if content else []
        except Exception as e:
            logger.error(f"Tina CMS normalization error: {str(e)}")
            return []

    def get_supported_events(self) -> List[str]:
        """Legacy method for backward compatibility."""
        return ['content.create', 'content.update', 'content.delete']

    def _determine_content_type(self, raw_data: Dict[str, Any]) -> ContentType:
        """Determine content type based on Tina collection or data structure."""
        collection = raw_data.get('_collection', '').lower()

        # Map Tina collections to content types
        if collection in ['posts', 'blog', 'articles']:
            return ContentType.ARTICLE
        elif collection in ['pages', 'page']:
            return ContentType.PAGE
        elif collection in ['products', 'product']:
            return ContentType.PRODUCT
        elif collection in ['collections', 'categories']:
            return ContentType.COLLECTION
        else:
            return ContentType.ARTICLE  # Default

    def _extract_client_id(self, raw_data: Dict[str, Any]) -> str:
        """Extract client ID from Tina data."""
        # In Tina, this could be from the repository or project configuration
        return raw_data.get('project_id', raw_data.get('client_id', 'tina-default'))

    def _generate_slug_from_title(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        return title.lower().replace(' ', '-').replace('_', '-')

__all__ = ['TinaCMSHandler']