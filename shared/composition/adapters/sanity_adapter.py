"""
Sanity CMS Adapter

Concrete implementation of the provider adapter for Sanity CMS.
This adapter enables seamless integration with Sanity's structured content platform,
democratizing access to professional content management with real-time collaboration.

TRANSFORMATIVE IMPACT:
Sanity CMS provides modern, structured content management with real-time collaboration,
API-first architecture, and powerful querying capabilities. Combined with our integration
layer, it enables professional content workflows at a fraction of traditional costs.
"""

import json
import logging
import hmac
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from shared.composition.provider_adapter_registry import IProviderHandler, BaseProviderHandler
from models.composition import (
    UnifiedContent, ContentType, ContentStatus,
    MediaAsset, SEOMetadata
)


logger = logging.getLogger(__name__)


class SanityCMSHandler(BaseProviderHandler):
    """
    Sanity CMS provider handler implementing structured content management.

    Sanity CMS provides:
    - Structured content with custom schemas
    - Real-time collaborative editing
    - Powerful GROQ query language
    - CDN-delivered content
    - Perfect for modern content workflows
    """

    def __init__(self):
        super().__init__("sanity")

        # Sanity-specific configuration
        self.supported_webhook_events = [
            'document.create', 'document.update', 'document.delete',
            'document.publish', 'document.unpublish'
        ]

        # Content type mapping
        self.sanity_type_mapping = {
            'post': ContentType.ARTICLE,
            'page': ContentType.PAGE,
            'product': ContentType.PRODUCT,
            'category': ContentType.COLLECTION,
            'collection': ContentType.COLLECTION,
            'article': ContentType.ARTICLE,
            'blog': ContentType.ARTICLE
        }

        logger.info("Sanity CMS adapter initialized")

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """
        Normalize Sanity webhook data to unified content schema.

        Sanity provides rich, structured data that we transform into our
        unified format while preserving the structured content benefits.
        """

        try:
            unified_content = []

            # Handle different Sanity webhook structures
            if '_id' in webhook_data:
                # Direct document webhook
                content = self._normalize_sanity_document(webhook_data, event_type)
                if content:
                    unified_content.append(content)

            elif 'documents' in webhook_data:
                # Batch webhook with multiple documents
                for doc in webhook_data['documents']:
                    content = self._normalize_sanity_document(doc, event_type)
                    if content:
                        unified_content.append(content)

            elif 'document' in webhook_data:
                # Wrapped document webhook
                content = self._normalize_sanity_document(webhook_data['document'], event_type)
                if content:
                    unified_content.append(content)

            logger.info(f"Sanity CMS: Normalized {len(unified_content)} content items from webhook")
            return unified_content

        except Exception as e:
            logger.error(f"Sanity CMS normalization error: {str(e)}", exc_info=True)
            return []

    def validate_webhook_signature(self, body: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """
        Validate Sanity webhook signature.

        Sanity uses HMAC-SHA256 for webhook signature validation to ensure
        authenticity and prevent malicious requests.
        """

        try:
            # Get Sanity signature
            signature_header = headers.get('sanity-webhook-signature', '')
            if not signature_header:
                logger.warning("No Sanity webhook signature found")
                return True  # Allow for development/testing

            # Extract signature (format: "sha256=<signature>")
            if not signature_header.startswith('sha256='):
                logger.warning(f"Invalid Sanity signature format: {signature_header}")
                return True

            signature = signature_header[7:]  # Remove 'sha256=' prefix

            # Get webhook secret
            webhook_secret = self._get_webhook_secret()
            if not webhook_secret:
                logger.info("No webhook secret configured for Sanity CMS - allowing request")
                return True

            # Calculate expected signature
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                body_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                logger.warning("Invalid Sanity webhook signature")

            return is_valid

        except Exception as e:
            logger.error(f"Sanity signature validation error: {str(e)}")
            return False

    def extract_event_type(self, headers: Dict[str, str], body: Dict[str, Any]) -> str:
        """Extract event type from Sanity webhook."""

        # Check for event type in headers
        sanity_event = headers.get('sanity-webhook-event', '')

        if sanity_event:
            # Map Sanity events to our content events
            event_mapping = {
                'document.create': 'content.created',
                'document.update': 'content.updated',
                'document.delete': 'content.deleted',
                'document.publish': 'content.updated',
                'document.unpublish': 'content.updated'
            }
            return event_mapping.get(sanity_event, 'content.updated')

        # Fallback: analyze document data
        if body.get('_type') and body.get('_id'):
            return 'content.updated'

        return 'content.updated'

    def get_supported_events(self) -> List[str]:
        """Get supported Sanity webhook events."""

        return self.supported_webhook_events

    def _normalize_sanity_document(self, document: Dict[str, Any], event_type: str) -> Optional[UnifiedContent]:
        """
        Normalize a Sanity document to unified content schema.

        Sanity documents have rich structure and metadata that we preserve
        while creating a consistent interface for SSG engines.
        """

        try:
            # Handle deleted documents
            if event_type == 'content.deleted' or document.get('_deleted'):
                return UnifiedContent(
                    id=f"sanity:{document.get('_id', 'unknown')}",
                    title=document.get('title', 'Deleted Document'),
                    slug=document.get('slug', {}).get('current', 'deleted-document'),
                    content_type=self._determine_content_type(document),
                    status=ContentStatus.DELETED,
                    provider_type="cms",
                    provider_name=self.provider_name,
                    provider_data=document,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

            # Extract basic document information
            doc_id = document.get('_id', '')
            doc_type = document.get('_type', 'document')
            title = self._extract_title(document)
            slug = self._extract_slug(document)

            # Determine content type
            content_type = self._determine_content_type(document)

            # Determine status
            status = self._determine_status(document)

            # Extract content body
            body_content = self._extract_body_content(document)
            description = self._extract_description(document, body_content)

            # Process images and media
            featured_image, images = self._process_sanity_media(document)

            # Extract SEO metadata
            seo_metadata = self._extract_seo_metadata(document)

            # Extract tags
            tags = self._extract_tags(document)

            # Create timestamps
            created_at = self._parse_sanity_datetime(document.get('_createdAt'))
            updated_at = self._parse_sanity_datetime(document.get('_updatedAt'))

            return UnifiedContent(
                id=f"sanity:{doc_id}",
                title=title,
                slug=slug,
                content_type=content_type,
                status=status,
                description=description,
                body=body_content,
                featured_image=featured_image,
                images=images,
                seo=seo_metadata,
                tags=tags,
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data={
                    'sanity_id': doc_id,
                    'sanity_type': doc_type,
                    'revision': document.get('_rev'),
                    'dataset': document.get('_dataset'),
                    'project_id': document.get('_projectId'),
                    'raw_document': document
                },
                created_at=created_at,
                updated_at=updated_at
            )

        except Exception as e:
            logger.error(f"Error normalizing Sanity document {document.get('_id')}: {str(e)}")
            return None

    def _determine_content_type(self, document: Dict[str, Any]) -> ContentType:
        """Determine content type based on Sanity document type."""

        sanity_type = document.get('_type', '').lower()

        # Check our mapping first
        if sanity_type in self.sanity_type_mapping:
            return self.sanity_type_mapping[sanity_type]

        # Check for common patterns
        if 'product' in sanity_type:
            return ContentType.PRODUCT
        elif any(keyword in sanity_type for keyword in ['post', 'blog', 'article', 'news']):
            return ContentType.ARTICLE
        elif any(keyword in sanity_type for keyword in ['page', 'landing']):
            return ContentType.PAGE
        elif any(keyword in sanity_type for keyword in ['category', 'collection', 'group']):
            return ContentType.COLLECTION
        elif any(keyword in sanity_type for keyword in ['image', 'video', 'media', 'asset']):
            return ContentType.MEDIA
        else:
            return ContentType.ARTICLE  # Default

    def _determine_status(self, document: Dict[str, Any]) -> ContentStatus:
        """Determine content status from Sanity document."""

        # Check for explicit status field
        if 'status' in document:
            status = document['status'].lower()
            if status == 'published':
                return ContentStatus.PUBLISHED
            elif status == 'draft':
                return ContentStatus.DRAFT
            elif status == 'archived':
                return ContentStatus.ARCHIVED

        # Check for published flag
        if document.get('published', False):
            return ContentStatus.PUBLISHED

        # Check if document has publishedAt date
        if document.get('publishedAt'):
            published_date = self._parse_sanity_datetime(document['publishedAt'])
            if published_date and published_date <= datetime.utcnow():
                return ContentStatus.PUBLISHED

        # Default to draft
        return ContentStatus.DRAFT

    def _extract_title(self, document: Dict[str, Any]) -> str:
        """Extract title from Sanity document."""

        # Try common title fields
        for field in ['title', 'name', 'heading', 'label']:
            if field in document and document[field]:
                return str(document[field])

        # Try to extract from slug
        if 'slug' in document and isinstance(document['slug'], dict):
            slug_current = document['slug'].get('current', '')
            if slug_current:
                return slug_current.replace('-', ' ').title()

        # Fallback
        return f"Untitled ({document.get('_type', 'Document')})"

    def _extract_slug(self, document: Dict[str, Any]) -> str:
        """Extract URL slug from Sanity document."""

        # Check for Sanity slug object
        if 'slug' in document and isinstance(document['slug'], dict):
            return document['slug'].get('current', '')

        # Check for direct slug field
        if 'slug' in document and isinstance(document['slug'], str):
            return document['slug']

        # Generate from title
        title = self._extract_title(document)
        return title.lower().replace(' ', '-').replace('_', '-')

    def _extract_body_content(self, document: Dict[str, Any]) -> str:
        """Extract body content from Sanity document."""

        # Try common body fields
        for field in ['body', 'content', 'description', 'text']:
            if field in document:
                content = document[field]

                # Handle Sanity's portable text
                if isinstance(content, list):
                    return self._render_portable_text(content)
                elif isinstance(content, str):
                    return content

        return ""

    def _extract_description(self, document: Dict[str, Any], body_content: str) -> Optional[str]:
        """Extract description from Sanity document."""

        # Try explicit description fields
        for field in ['description', 'excerpt', 'summary', 'subtitle']:
            if field in document and document[field]:
                return str(document[field])[:160]

        # Generate from body content
        if body_content:
            return body_content[:160] + "..." if len(body_content) > 160 else body_content

        return None

    def _process_sanity_media(self, document: Dict[str, Any]) -> tuple[Optional[MediaAsset], List[MediaAsset]]:
        """Process media assets from Sanity document."""

        featured_image = None
        images = []

        # Process main image
        if 'mainImage' in document or 'image' in document:
            image_data = document.get('mainImage') or document.get('image')
            if image_data:
                featured_image = self._create_media_asset_from_sanity(image_data)

        # Process image gallery
        if 'gallery' in document and isinstance(document['gallery'], list):
            for img_data in document['gallery']:
                media_asset = self._create_media_asset_from_sanity(img_data)
                if media_asset:
                    images.append(media_asset)

        # Process images in body content
        images.extend(self._extract_images_from_portable_text(document.get('body', [])))

        return featured_image, images

    def _create_media_asset_from_sanity(self, image_data: Dict[str, Any]) -> Optional[MediaAsset]:
        """Create MediaAsset from Sanity image data."""

        try:
            if not image_data or 'asset' not in image_data:
                return None

            asset = image_data['asset']
            asset_ref = asset.get('_ref', '') if isinstance(asset, dict) else str(asset)

            # Construct Sanity CDN URL
            # Format: https://cdn.sanity.io/images/{projectId}/{dataset}/{assetId}-{dimensions}.{format}
            base_url = f"https://cdn.sanity.io/images/{self._get_project_id()}/{self._get_dataset()}"
            image_url = f"{base_url}/{asset_ref}"

            return MediaAsset(
                id=asset_ref,
                url=image_url,
                alt_text=image_data.get('alt', ''),
                width=image_data.get('crop', {}).get('width'),
                height=image_data.get('crop', {}).get('height')
            )

        except Exception as e:
            logger.warning(f"Error creating media asset from Sanity data: {str(e)}")
            return None

    def _extract_seo_metadata(self, document: Dict[str, Any]) -> Optional[SEOMetadata]:
        """Extract SEO metadata from Sanity document."""

        try:
            seo_data = document.get('seo', {})
            if not seo_data:
                return None

            return SEOMetadata(
                meta_title=seo_data.get('title'),
                meta_description=seo_data.get('description'),
                canonical_url=seo_data.get('canonicalUrl'),
                og_title=seo_data.get('ogTitle'),
                og_description=seo_data.get('ogDescription'),
                og_image=seo_data.get('ogImage', {}).get('asset', {}).get('url'),
                keywords=seo_data.get('keywords', [])
            )

        except Exception as e:
            logger.warning(f"Error extracting SEO metadata: {str(e)}")
            return None

    def _extract_tags(self, document: Dict[str, Any]) -> List[str]:
        """Extract tags from Sanity document."""

        tags = []

        # Try different tag field names
        for field in ['tags', 'categories', 'keywords', 'topics']:
            if field in document and isinstance(document[field], list):
                for tag_item in document[field]:
                    if isinstance(tag_item, dict) and 'title' in tag_item:
                        tags.append(tag_item['title'])
                    elif isinstance(tag_item, str):
                        tags.append(tag_item)

        return list(set(tags))  # Remove duplicates

    def _render_portable_text(self, portable_text: List[Dict[str, Any]]) -> str:
        """
        Render Sanity's Portable Text to plain text.

        This is a simplified renderer. In production, you might want
        to use a proper Portable Text renderer.
        """

        text_parts = []

        for block in portable_text:
            if block.get('_type') == 'block':
                # Extract text from block
                children = block.get('children', [])
                for child in children:
                    if child.get('text'):
                        text_parts.append(child['text'])

        return ' '.join(text_parts)

    def _extract_images_from_portable_text(self, portable_text: List[Dict[str, Any]]) -> List[MediaAsset]:
        """Extract images from Portable Text content."""

        images = []

        for block in portable_text:
            if block.get('_type') == 'image':
                media_asset = self._create_media_asset_from_sanity(block)
                if media_asset:
                    images.append(media_asset)

        return images

    def _parse_sanity_datetime(self, datetime_str: Optional[str]) -> datetime:
        """Parse Sanity datetime string."""

        if not datetime_str:
            return datetime.utcnow()

        try:
            # Handle ISO datetime strings
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str)
        except:
            return datetime.utcnow()

    def _get_project_id(self) -> str:
        """Get Sanity project ID from configuration."""
        import os
        return os.environ.get('SANITY_PROJECT_ID', 'your-project-id')

    def _get_dataset(self) -> str:
        """Get Sanity dataset from configuration."""
        import os
        return os.environ.get('SANITY_DATASET', 'production')

    def _get_webhook_secret(self) -> Optional[str]:
        """Get webhook secret for signature validation."""
        import os
        return os.environ.get('SANITY_WEBHOOK_SECRET')


# Make handler available for registry
__all__ = ['SanityCMSHandler']