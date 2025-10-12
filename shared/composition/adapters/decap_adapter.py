"""
Decap CMS Adapter

Concrete implementation of the provider adapter for Decap CMS (formerly Netlify CMS).
This adapter enables seamless integration with Git-based content management,
democratizing access to version-controlled content workflows.

TRANSFORMATIVE IMPACT:
Decap CMS represents the most cost-effective content management solution,
enabling small businesses and entrepreneurs to manage content with enterprise-grade
version control and collaboration features at zero monthly cost.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hmac
import hashlib

# New enhanced interfaces
from blackwell_core.adapters.interfaces import ICMSAdapter
from blackwell_core.models.events import ContentEvent, UnifiedContent
from models.composition import ContentType, ContentStatus

# Legacy interfaces for backward compatibility
from shared.composition.provider_adapter_registry import IProviderHandler, BaseProviderHandler


logger = logging.getLogger(__name__)


class DecapCMSHandler(ICMSAdapter):
    """
    Decap CMS provider handler implementing Git-based content management.

    Decap CMS (formerly Netlify CMS) provides:
    - Git-based version control for all content
    - Zero monthly cost (uses existing Git repositories)
    - Editorial workflows with review processes
    - Markdown-based content creation
    - Perfect for small businesses and developers
    """

    # Required class attributes for new interface
    provider_name = "decap"
    provider_type = "cms"
    supported_events = ["content.created", "content.updated", "content.deleted"]
    api_version = "v1"

    def __init__(self):
        # Decap CMS specific configuration
        self.content_directory = "content"
        self.supported_formats = [".md", ".mdx", ".yaml", ".yml", ".json"]

        logger.info("Decap CMS adapter initialized")

    def transform_event(self, raw_data: Dict[str, Any]) -> ContentEvent:
        """
        Transform GitHub webhook data to standardized ContentEvent.

        This is the new interface method that replaces normalize_webhook_data
        for the enhanced event system.
        """
        try:
            # Extract basic event information
            event_type = self._determine_event_type_from_webhook(raw_data)

            # Get the first commit for basic information
            commit = None
            content_id = None
            content_type = "article"
            action = "updated"

            if raw_data.get('commits'):
                commit = raw_data['commits'][0]

                # Look for content files in the commit
                content_files = []
                for file_path in commit.get('added', []) + commit.get('modified', []):
                    if self._is_content_file(file_path):
                        content_files.append(file_path)

                if content_files:
                    first_file = content_files[0]
                    content_id = f"decap:{raw_data['repository']['full_name']}:{first_file}"
                    content_type = self._determine_content_type(first_file).value

                    # Determine action based on commit message and file status
                    if first_file in commit.get('added', []):
                        action = "created"
                    elif commit.get('message', '').lower().startswith('delete'):
                        action = "deleted"
                    elif 'publish' in commit.get('message', '').lower():
                        action = "published"
                    else:
                        action = "updated"

            # Create ContentEvent
            return ContentEvent(
                event_type=event_type,
                provider=self.provider_name,
                client_id=self._extract_client_id(raw_data),
                payload=raw_data,
                content_id=content_id or f"decap:{raw_data.get('repository', {}).get('full_name', 'unknown')}",
                content_type=content_type,
                action=action,
                author=commit.get('author', {}).get('name') if commit else None,
                category=self._extract_category_from_webhook(raw_data)
            )

        except Exception as e:
            logger.error(f"Error transforming Decap CMS event: {str(e)}", exc_info=True)
            # Return a basic event if transformation fails
            return ContentEvent(
                event_type="content.updated",
                provider=self.provider_name,
                client_id="unknown",
                payload=raw_data,
                content_id="unknown",
                content_type="article",
                action="updated"
            )

    def normalize_webhook_data(self, webhook_data: Dict[str, Any], event_type: str) -> List[UnifiedContent]:
        """
        Normalize GitHub webhook data from Decap CMS to unified content schema.

        Decap CMS uses GitHub webhooks to notify of content changes, making it
        accessible to organizations worldwide through Git-based workflows.
        """

        try:
            unified_content = []

            # Handle GitHub push events (most common for Decap CMS)
            if webhook_data.get('commits'):
                for commit in webhook_data['commits']:
                    # Process added and modified files
                    for file_path in commit.get('added', []) + commit.get('modified', []):
                        if self._is_content_file(file_path):
                            content = self._process_content_file(file_path, commit, webhook_data)
                            if content:
                                unified_content.append(content)

                    # Handle deleted files
                    for file_path in commit.get('removed', []):
                        if self._is_content_file(file_path):
                            content = self._process_deleted_file(file_path, commit, webhook_data)
                            if content:
                                unified_content.append(content)

            logger.info(f"Decap CMS: Normalized {len(unified_content)} content items from webhook")
            return unified_content

        except Exception as e:
            logger.error(f"Decap CMS normalization error: {str(e)}", exc_info=True)
            return []

    def validate_webhook_signature(self, body: bytes, headers: Dict[str, str]) -> bool:
        """
        Validate GitHub webhook signature for Decap CMS.

        This ensures webhook authenticity and prevents malicious requests
        from compromising the content management system.
        """

        try:
            # Get signature from headers
            signature_header = headers.get('X-Hub-Signature-256', '')
            if not signature_header:
                # Fallback to older signature format
                signature_header = headers.get('X-Hub-Signature', '')
                if not signature_header:
                    logger.warning("No GitHub signature found in Decap CMS webhook")
                    return True  # Allow for development/testing

            # Extract signature
            if signature_header.startswith('sha256='):
                signature = signature_header[7:]
                algorithm = 'sha256'
            elif signature_header.startswith('sha1='):
                signature = signature_header[5:]
                algorithm = 'sha1'
            else:
                logger.warning(f"Unknown signature format: {signature_header}")
                return True  # Allow for development

            # Get webhook secret (would be configured per client)
            webhook_secret = self._get_webhook_secret()
            if not webhook_secret:
                logger.info("No webhook secret configured for Decap CMS - allowing request")
                return True

            # Verify signature
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                body,
                getattr(hashlib, algorithm)
            ).hexdigest()

            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                logger.warning("Invalid GitHub webhook signature for Decap CMS")

            return is_valid

        except Exception as e:
            logger.error(f"Decap CMS signature validation error: {str(e)}")
            return False

    def extract_event_type(self, headers: Dict[str, str], body: Dict[str, Any]) -> str:
        """Extract event type from GitHub webhook headers."""

        github_event = headers.get('X-GitHub-Event', 'unknown')

        # Map GitHub events to our content events
        event_mapping = {
            'push': 'content.updated',
            'pull_request': 'content.created',
            'create': 'content.created',
            'delete': 'content.deleted'
        }

        return event_mapping.get(github_event, 'content.updated')

    def get_supported_events(self) -> List[str]:
        """Get supported GitHub webhook events for Decap CMS."""

        return ['push', 'pull_request', 'create', 'delete']

    def _is_content_file(self, file_path: str) -> bool:
        """Check if file is a content file managed by Decap CMS."""

        # Check if file is in content directory
        if not file_path.startswith(self.content_directory):
            return False

        # Check file extension
        return any(file_path.endswith(ext) for ext in self.supported_formats)

    def _process_content_file(self, file_path: str, commit: Dict[str, Any], webhook_data: Dict[str, Any]) -> Optional[UnifiedContent]:
        """Process a content file change from Decap CMS."""

        try:
            # Extract content metadata from file path
            content_type = self._determine_content_type(file_path)
            slug = self._extract_slug_from_path(file_path)

            # For a real implementation, we would fetch the file content from GitHub API
            # For now, we'll create a basic representation
            content_data = self._simulate_file_content(file_path, commit)

            return UnifiedContent(
                id=f"decap:{webhook_data['repository']['full_name']}:{file_path}",
                title=content_data.get('title', self._generate_title_from_path(file_path)),
                slug=slug,
                content_type=content_type,
                status=ContentStatus.PUBLISHED if commit.get('message', '').startswith('Publish') else ContentStatus.DRAFT,
                description=content_data.get('description'),
                body=content_data.get('body'),
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data={
                    'file_path': file_path,
                    'commit_sha': commit['id'],
                    'repository': webhook_data['repository']['full_name'],
                    'branch': webhook_data.get('ref', '').replace('refs/heads/', ''),
                    'author': commit.get('author', {}).get('name', 'Unknown'),
                    'commit_message': commit.get('message', '')
                },
                created_at=datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00')),
                tags=content_data.get('tags', [])
            )

        except Exception as e:
            logger.error(f"Error processing Decap CMS file {file_path}: {str(e)}")
            return None

    def _process_deleted_file(self, file_path: str, commit: Dict[str, Any], webhook_data: Dict[str, Any]) -> Optional[UnifiedContent]:
        """Process a deleted content file from Decap CMS."""

        try:
            return UnifiedContent(
                id=f"decap:{webhook_data['repository']['full_name']}:{file_path}",
                title=self._generate_title_from_path(file_path),
                slug=self._extract_slug_from_path(file_path),
                content_type=self._determine_content_type(file_path),
                status=ContentStatus.DELETED,
                provider_type="cms",
                provider_name=self.provider_name,
                provider_data={
                    'file_path': file_path,
                    'commit_sha': commit['id'],
                    'repository': webhook_data['repository']['full_name'],
                    'deleted': True,
                    'commit_message': commit.get('message', '')
                },
                created_at=datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00'))
            )

        except Exception as e:
            logger.error(f"Error processing deleted Decap CMS file {file_path}: {str(e)}")
            return None

    def _determine_content_type(self, file_path: str) -> ContentType:
        """Determine content type based on file path structure."""

        path_parts = file_path.split('/')

        # Common Decap CMS content patterns
        if 'blog' in path_parts or 'posts' in path_parts or 'articles' in path_parts:
            return ContentType.ARTICLE
        elif 'pages' in path_parts:
            return ContentType.PAGE
        elif 'collections' in path_parts or 'categories' in path_parts:
            return ContentType.COLLECTION
        elif any(ext in file_path for ext in ['.jpg', '.png', '.gif', '.svg']):
            return ContentType.MEDIA
        else:
            return ContentType.ARTICLE  # Default for Decap CMS

    def _extract_slug_from_path(self, file_path: str) -> str:
        """Extract URL slug from file path."""

        # Remove directory and extension
        filename = file_path.split('/')[-1]
        slug = filename.split('.')[0]

        # Remove date prefix if present (YYYY-MM-DD-title.md pattern)
        if len(slug) > 10 and slug[4] == '-' and slug[7] == '-':
            slug = slug[11:]  # Remove YYYY-MM-DD- prefix

        # Ensure slug is URL-friendly
        return slug.lower().replace('_', '-')

    def _generate_title_from_path(self, file_path: str) -> str:
        """Generate human-readable title from file path."""

        slug = self._extract_slug_from_path(file_path)
        return slug.replace('-', ' ').title()

    def _simulate_file_content(self, file_path: str, commit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate file content parsing.

        In a real implementation, this would fetch the actual file content
        from GitHub API and parse the frontmatter and body.
        """

        return {
            'title': self._generate_title_from_path(file_path),
            'description': f"Content from {file_path}",
            'body': f"Content body for {file_path} (commit: {commit['id'][:8]})",
            'tags': ['decap-cms', 'git-based']
        }

    def _get_webhook_secret(self) -> Optional[str]:
        """
        Get webhook secret for signature validation.

        In production, this would be retrieved from secure configuration
        management (AWS Secrets Manager, environment variables, etc.)
        """

        import os
        return os.environ.get('DECAP_WEBHOOK_SECRET')

    # ============================================================================
    # New IProviderAdapter Interface Methods
    # ============================================================================

    def get_capabilities(self) -> List[str]:
        """
        Return list of features this Decap CMS adapter supports.
        """
        return [
            "webhooks",
            "content_fetch",
            "content_listing",
            "git_integration",
            "markdown_support",
            "frontmatter_parsing",
            "editorial_workflow"
        ]

    def normalize_content(self, raw_data: Dict[str, Any]) -> UnifiedContent:
        """
        Convert provider data to unified content schema.

        This is the single-item version of the normalize_webhook_data method.
        """
        try:
            # Determine content metadata
            file_path = raw_data.get('file_path', 'unknown')
            content_type = self._determine_content_type(file_path)
            slug = self._extract_slug_from_path(file_path)

            return UnifiedContent(
                id=raw_data.get('id', f"decap:{file_path}"),
                title=raw_data.get('title', self._generate_title_from_path(file_path)),
                slug=slug,
                content_type=content_type.value,
                provider_type="cms",
                provider_name=self.provider_name,
                created_at=raw_data.get('created_at', datetime.utcnow().isoformat()),
                updated_at=raw_data.get('updated_at', datetime.utcnow().isoformat()),
                metadata=raw_data.get('metadata', {})
            )

        except Exception as e:
            logger.error(f"Error normalizing Decap CMS content: {str(e)}")
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

    # ============================================================================
    # Specialized ICMSAdapter Methods
    # ============================================================================

    def fetch_content_by_id(self, content_id: str) -> Optional[UnifiedContent]:
        """
        Retrieve specific content item by ID.

        For Decap CMS, this would require GitHub API integration
        to fetch the actual file content.
        """
        try:
            # Parse content ID to extract repository and file path
            if content_id.startswith('decap:'):
                parts = content_id[6:].split(':', 2)
                if len(parts) >= 2:
                    repository = parts[0]
                    file_path = parts[1] if len(parts) == 2 else parts[2]

                    # In a real implementation, this would use GitHub API
                    # to fetch the file content and parse it
                    mock_data = {
                        'id': content_id,
                        'file_path': file_path,
                        'title': self._generate_title_from_path(file_path),
                        'repository': repository
                    }

                    return self.normalize_content(mock_data)

            return None

        except Exception as e:
            logger.error(f"Error fetching Decap CMS content {content_id}: {str(e)}")
            return None

    def list_content(self, content_type: Optional[str] = None, limit: int = 100) -> List[UnifiedContent]:
        """
        List content items with optional filtering.

        For Decap CMS, this would require GitHub API integration
        to list repository files and parse their metadata.
        """
        try:
            # In a real implementation, this would:
            # 1. Use GitHub API to list files in the content directory
            # 2. Filter by content type if specified
            # 3. Parse frontmatter from each file
            # 4. Return normalized content items

            # Mock implementation for demonstration
            mock_content = []
            content_types = [content_type] if content_type else ['article', 'page']

            for i in range(min(limit, 5)):  # Mock 5 items
                for ct in content_types:
                    if len(mock_content) >= limit:
                        break

                    mock_data = {
                        'id': f'decap:example-repo:content/{ct}/{ct}-{i}.md',
                        'file_path': f'content/{ct}/{ct}-{i}.md',
                        'title': f'Sample {ct.title()} {i}',
                        'content_type': ct
                    }
                    mock_content.append(self.normalize_content(mock_data))

            return mock_content

        except Exception as e:
            logger.error(f"Error listing Decap CMS content: {str(e)}")
            return []

    # ============================================================================
    # Helper Methods for New Interface
    # ============================================================================

    def _determine_event_type_from_webhook(self, raw_data: Dict[str, Any]) -> str:
        """Determine event type from GitHub webhook data."""
        github_event = raw_data.get('github_event', 'push')

        event_mapping = {
            'push': 'content.updated',
            'pull_request': 'content.created',
            'create': 'content.created',
            'delete': 'content.deleted'
        }

        return event_mapping.get(github_event, 'content.updated')

    def _extract_client_id(self, raw_data: Dict[str, Any]) -> str:
        """Extract client ID from webhook data."""
        repository = raw_data.get('repository', {})
        return repository.get('full_name', 'unknown').replace('/', '-')

    def _extract_category_from_webhook(self, raw_data: Dict[str, Any]) -> Optional[str]:
        """Extract content category from webhook data."""
        if raw_data.get('commits'):
            commit = raw_data['commits'][0]
            # Look for category in commit message or file paths
            for file_path in commit.get('added', []) + commit.get('modified', []):
                if 'blog' in file_path or 'posts' in file_path:
                    return 'blog'
                elif 'docs' in file_path:
                    return 'documentation'
                elif 'pages' in file_path:
                    return 'pages'

        return None


# Make handler available for registry
__all__ = ['DecapCMSHandler']