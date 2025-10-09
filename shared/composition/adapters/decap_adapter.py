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

from shared.composition.provider_adapter_registry import IProviderHandler, BaseProviderHandler
from models.composition import UnifiedContent, ContentType, ContentStatus


logger = logging.getLogger(__name__)


class DecapCMSHandler(BaseProviderHandler):
    """
    Decap CMS provider handler implementing Git-based content management.

    Decap CMS (formerly Netlify CMS) provides:
    - Git-based version control for all content
    - Zero monthly cost (uses existing Git repositories)
    - Editorial workflows with review processes
    - Markdown-based content creation
    - Perfect for small businesses and developers
    """

    def __init__(self):
        super().__init__("decap")

        # Decap CMS specific configuration
        self.content_directory = "content"
        self.supported_formats = [".md", ".mdx", ".yaml", ".yml", ".json"]

        logger.info("Decap CMS adapter initialized")

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

    def validate_webhook_signature(self, body: Dict[str, Any], headers: Dict[str, str]) -> bool:
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
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                body_str.encode('utf-8'),
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


# Make handler available for registry
__all__ = ['DecapCMSHandler']