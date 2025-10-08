"""
CMS Data Models

Common data models used across all CMS providers.
These models provide type safety and validation for content management operations
while remaining provider-agnostic.

Key Models:
- ContentType: Content schema definitions
- ContentItem: Individual content pieces (posts, pages, etc.)
- MediaAsset: Media file management
- Author: Content author information
- ContentCollection: Content grouping and organization
- CMSWebhook: Webhook event handling for content updates
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, validator
from datetime import datetime
from enum import Enum
from decimal import Decimal


class ContentStatus(str, Enum):
    """Content publication status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"
    REVIEW = "review"


class FieldType(str, Enum):
    """Content field types"""
    STRING = "string"
    TEXT = "text"
    MARKDOWN = "markdown"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    IMAGE = "image"
    FILE = "file"
    SELECT = "select"
    MULTISELECT = "multiselect"
    REFERENCE = "reference"
    LIST = "list"
    OBJECT = "object"
    URL = "url"
    EMAIL = "email"
    COLOR = "color"
    LOCATION = "location"


class MediaType(str, Enum):
    """Media asset types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class WebhookEventType(str, Enum):
    """CMS webhook event types"""
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_PUBLISHED = "content.published"
    CONTENT_DELETED = "content.deleted"
    MEDIA_UPLOADED = "media.uploaded"
    MEDIA_DELETED = "media.deleted"
    SCHEMA_UPDATED = "schema.updated"


class ContentField(BaseModel):
    """Content field definition"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(..., description="Field name/identifier")
    label: str = Field(..., description="Human-readable field label")
    field_type: FieldType = Field(..., description="Field data type")
    required: bool = Field(default=False, description="Whether field is required")
    default_value: Optional[Any] = Field(None, description="Default field value")
    help_text: Optional[str] = Field(None, description="Help text for editors")

    # Field validation
    min_length: Optional[int] = Field(None, description="Minimum string length")
    max_length: Optional[int] = Field(None, description="Maximum string length")
    pattern: Optional[str] = Field(None, description="Regex validation pattern")

    # Select field options
    options: Optional[List[Dict[str, str]]] = Field(None, description="Options for select fields")

    # Reference field configuration
    reference_collection: Optional[str] = Field(None, description="Referenced collection name")

    # Provider-specific configuration
    provider_config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific field config")

    @validator('options')
    def validate_select_options(cls, v, values):
        """Validate options for select fields"""
        if values.get('field_type') in [FieldType.SELECT, FieldType.MULTISELECT] and not v:
            raise ValueError('Select fields must have options defined')
        return v

    @validator('reference_collection')
    def validate_reference_collection(cls, v, values):
        """Validate reference collection for reference fields"""
        if values.get('field_type') == FieldType.REFERENCE and not v:
            raise ValueError('Reference fields must specify a reference_collection')
        return v


class ContentType(BaseModel):
    """Content type/collection definition"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(..., description="Content type identifier", pattern=r"^[a-z0-9_]+$")
    label: str = Field(..., description="Human-readable content type name")
    description: Optional[str] = Field(None, description="Content type description")

    # Content structure
    fields: List[ContentField] = Field(..., description="Content fields definition")
    slug_field: Optional[str] = Field(None, description="Field to use for URL slugs")
    title_field: Optional[str] = Field("title", description="Field to use as content title")

    # Content behavior
    supports_draft: bool = Field(default=True, description="Whether content supports draft status")
    supports_scheduling: bool = Field(default=False, description="Whether content supports scheduled publishing")
    supports_seo: bool = Field(default=True, description="Whether to include SEO fields")

    # Organization
    folder: Optional[str] = Field(None, description="Content folder/directory")
    create_path: Optional[str] = Field(None, description="Path template for new content")

    # Provider-specific configuration
    provider_config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific collection config")

    def get_field(self, field_name: str) -> Optional[ContentField]:
        """Get field definition by name"""
        return next((field for field in self.fields if field.name == field_name), None)

    def get_required_fields(self) -> List[ContentField]:
        """Get list of required fields"""
        return [field for field in self.fields if field.required]

    def validate_content_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate content data against this content type.

        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}

        # Check required fields
        for field in self.get_required_fields():
            if field.name not in data or data[field.name] is None:
                errors[field.name] = f"Field '{field.label}' is required"

        # Validate field types and constraints
        for field in self.fields:
            if field.name not in data:
                continue

            value = data[field.name]
            field_errors = self._validate_field_value(field, value)
            if field_errors:
                errors[field.name] = field_errors

        return errors

    def _validate_field_value(self, field: ContentField, value: Any) -> Optional[str]:
        """Validate individual field value"""
        if value is None:
            return None

        # String validation
        if field.field_type in [FieldType.STRING, FieldType.TEXT, FieldType.MARKDOWN]:
            if not isinstance(value, str):
                return f"Expected string value"

            if field.min_length and len(value) < field.min_length:
                return f"Minimum length is {field.min_length} characters"

            if field.max_length and len(value) > field.max_length:
                return f"Maximum length is {field.max_length} characters"

        # Number validation
        elif field.field_type == FieldType.NUMBER:
            if not isinstance(value, (int, float)):
                return f"Expected numeric value"

        # Boolean validation
        elif field.field_type == FieldType.BOOLEAN:
            if not isinstance(value, bool):
                return f"Expected boolean value"

        # Date validation
        elif field.field_type in [FieldType.DATE, FieldType.DATETIME]:
            if not isinstance(value, (str, datetime)):
                return f"Expected date/datetime value"

        # Select validation
        elif field.field_type == FieldType.SELECT:
            if field.options:
                valid_values = [opt.get("value", opt.get("label")) for opt in field.options]
                if value not in valid_values:
                    return f"Value must be one of: {', '.join(valid_values)}"

        return None


class Author(BaseModel):
    """Content author information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    id: Optional[str] = Field(None, description="Author identifier")
    name: str = Field(..., description="Author display name")
    email: Optional[str] = Field(None, description="Author email address")
    bio: Optional[str] = Field(None, description="Author biography")
    avatar: Optional[str] = Field(None, description="Author avatar image URL")
    social_links: Dict[str, str] = Field(default_factory=dict, description="Social media links")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional author metadata")

    @validator('email')
    def validate_email(cls, v):
        """Basic email validation"""
        if v and ('@' not in v or '.' not in v.split('@')[1]):
            raise ValueError('Invalid email format')
        return v.lower() if v else v


class MediaAsset(BaseModel):
    """Media asset information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    id: str = Field(..., description="Asset identifier")
    filename: str = Field(..., description="Original filename")
    title: Optional[str] = Field(None, description="Asset title")
    alt_text: Optional[str] = Field(None, description="Alt text for accessibility")
    description: Optional[str] = Field(None, description="Asset description")

    # File information
    media_type: MediaType = Field(..., description="Media asset type")
    mime_type: str = Field(..., description="MIME type")
    file_size: int = Field(..., description="File size in bytes")

    # URLs
    url: str = Field(..., description="Public URL to access the asset")
    secure_url: Optional[str] = Field(None, description="HTTPS URL if different")

    # Image-specific properties
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")

    # Metadata
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    uploaded_by: Optional[Author] = Field(None, description="User who uploaded the asset")
    tags: List[str] = Field(default_factory=list, description="Asset tags")
    folder: Optional[str] = Field(None, description="Asset folder/directory")

    # Provider-specific data
    provider: str = Field(..., description="CMS provider name")
    provider_id: Optional[str] = Field(None, description="Provider-specific asset ID")
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific metadata")

    @property
    def is_image(self) -> bool:
        """Check if asset is an image"""
        return self.media_type == MediaType.IMAGE

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return round(self.file_size / (1024 * 1024), 2)

    def get_responsive_urls(self) -> Dict[str, str]:
        """Get responsive image URLs (provider-specific implementation)"""
        # This would be implemented by specific CMS providers
        return {"original": self.url}


class ContentItem(BaseModel):
    """Individual content item (post, page, etc.)"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    id: str = Field(..., description="Content identifier")
    content_type: str = Field(..., description="Content type name")
    title: str = Field(..., description="Content title")
    slug: str = Field(..., description="URL slug")

    # Content data
    fields: Dict[str, Any] = Field(default_factory=dict, description="Content field data")

    # Publication status
    status: ContentStatus = Field(default=ContentStatus.DRAFT, description="Publication status")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")

    # Authorship
    author: Optional[Author] = Field(None, description="Content author")

    # SEO and metadata
    meta_title: Optional[str] = Field(None, description="SEO meta title")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    featured_image: Optional[MediaAsset] = Field(None, description="Featured image")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    categories: List[str] = Field(default_factory=list, description="Content categories")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Provider-specific data
    provider: str = Field(..., description="CMS provider name")
    provider_id: Optional[str] = Field(None, description="Provider-specific content ID")
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific metadata")

    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """Get value of a specific field"""
        return self.fields.get(field_name, default)

    def set_field_value(self, field_name: str, value: Any) -> None:
        """Set value of a specific field"""
        self.fields[field_name] = value

    @property
    def is_published(self) -> bool:
        """Check if content is published"""
        return self.status == ContentStatus.PUBLISHED and (
            self.published_at is None or self.published_at <= datetime.utcnow()
        )

    @property
    def is_scheduled(self) -> bool:
        """Check if content is scheduled for future publication"""
        return (
            self.status == ContentStatus.SCHEDULED and
            self.scheduled_at is not None and
            self.scheduled_at > datetime.utcnow()
        )

    def get_url_path(self, base_path: str = "") -> str:
        """Generate URL path for this content"""
        if base_path:
            return f"{base_path.rstrip('/')}/{self.slug}"
        return f"/{self.slug}"


class ContentCollection(BaseModel):
    """Collection of related content items"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(..., description="Collection name")
    content_type: str = Field(..., description="Type of content in this collection")
    items: List[ContentItem] = Field(default_factory=list, description="Content items")
    total_count: Optional[int] = Field(None, description="Total items (for pagination)")

    # Pagination
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=20, description="Items per page")
    has_more: bool = Field(default=False, description="Whether more items are available")

    # Filtering and sorting
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

    # Metadata
    provider: str = Field(..., description="CMS provider name")
    fetched_at: datetime = Field(default_factory=datetime.utcnow, description="Collection fetch timestamp")

    def get_published_items(self) -> List[ContentItem]:
        """Get only published content items"""
        return [item for item in self.items if item.is_published]

    def get_items_by_tag(self, tag: str) -> List[ContentItem]:
        """Get items with a specific tag"""
        return [item for item in self.items if tag in item.tags]

    def get_items_by_author(self, author_id: str) -> List[ContentItem]:
        """Get items by a specific author"""
        return [item for item in self.items if item.author and item.author.id == author_id]


class CMSWebhook(BaseModel):
    """CMS webhook event data"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    event_type: WebhookEventType = Field(..., description="Type of webhook event")
    provider: str = Field(..., description="CMS provider name")

    # Event data
    content_item: Optional[ContentItem] = Field(None, description="Content item (for content events)")
    media_asset: Optional[MediaAsset] = Field(None, description="Media asset (for media events)")
    content_type: Optional[ContentType] = Field(None, description="Content type (for schema events)")

    # Event metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    user_id: Optional[str] = Field(None, description="User who triggered the event")

    # Raw webhook data
    raw_payload: Dict[str, Any] = Field(default_factory=dict, description="Raw webhook payload")
    headers: Dict[str, str] = Field(default_factory=dict, description="Webhook headers")

    # Processing metadata
    processed: bool = Field(default=False, description="Whether webhook has been processed")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    build_triggered: bool = Field(default=False, description="Whether build was triggered")

    def should_trigger_build(self) -> bool:
        """Determine if this webhook should trigger a site rebuild"""
        # Content publication/update events should trigger builds
        rebuild_events = [
            WebhookEventType.CONTENT_PUBLISHED,
            WebhookEventType.CONTENT_UPDATED,
            WebhookEventType.CONTENT_DELETED
        ]

        return self.event_type in rebuild_events

    def get_affected_paths(self) -> List[str]:
        """Get list of site paths affected by this webhook"""
        paths = []

        if self.content_item:
            # Add the content item's URL path
            paths.append(self.content_item.get_url_path())

            # Add index pages that might list this content
            if self.content_item.content_type == "posts":
                paths.extend(["/", "/blog", "/posts"])
            elif self.content_item.content_type == "pages":
                paths.append("/")

        return paths


class CMSQueryFilter(BaseModel):
    """Query filter for content retrieval"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    field: str = Field(..., description="Field to filter on")
    operator: str = Field(default="eq", description="Filter operator (eq, ne, gt, lt, contains, etc.)")
    value: Any = Field(..., description="Filter value")

    def to_provider_filter(self, provider: str) -> Dict[str, Any]:
        """Convert to provider-specific filter format"""
        # This would be implemented by specific CMS providers
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value
        }


class CMSQuery(BaseModel):
    """Query parameters for content retrieval"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    content_type: str = Field(..., description="Content type to query")
    filters: List[CMSQueryFilter] = Field(default_factory=list, description="Query filters")

    # Sorting
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    # Field selection
    select_fields: Optional[List[str]] = Field(None, description="Specific fields to retrieve")
    include_drafts: bool = Field(default=False, description="Whether to include draft content")

    def add_filter(self, field: str, value: Any, operator: str = "eq") -> None:
        """Add a filter to the query"""
        self.filters.append(CMSQueryFilter(field=field, value=value, operator=operator))

    def get_published_only_filter(self) -> "CMSQuery":
        """Get a copy of this query with published-only filter"""
        query = self.model_copy()
        if not self.include_drafts:
            query.add_filter("status", ContentStatus.PUBLISHED)
        return query


# Export all models for easy importing
__all__ = [
    "ContentStatus", "FieldType", "MediaType", "WebhookEventType",
    "ContentField", "ContentType", "Author", "MediaAsset",
    "ContentItem", "ContentCollection", "CMSWebhook",
    "CMSQueryFilter", "CMSQuery"
]