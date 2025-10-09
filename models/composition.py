"""
Composition Architecture Models

This module defines the Pydantic models and types for the event-driven
composition architecture, enabling CMS and E-commerce provider integration
through a unified content schema and event system.

Based on the architecture defined in:
docs/architecture/event-driven-composition-architecture.md
"""

from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, Dict, Any, List, Literal, Union
from datetime import datetime
from enum import Enum
import uuid


class ContentType(str, Enum):
    """Content types supported across all providers"""
    PRODUCT = "product"           # E-commerce product
    ARTICLE = "article"           # Blog post, news article
    PAGE = "page"                 # Static page content
    COLLECTION = "collection"     # Product collection, content category
    MEDIA = "media"               # Images, videos, documents


class ContentStatus(str, Enum):
    """Content lifecycle status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MediaAsset(BaseModel):
    """Media asset representation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [{
                "id": "img_123456789",
                "url": "https://cdn.example.com/image.jpg",
                "alt_text": "Product image",
                "width": 800,
                "height": 600,
                "mime_type": "image/jpeg"
            }]
        }
    )

    id: str = Field(
        ...,
        description="Unique media asset identifier"
    )

    url: str = Field(
        ...,
        description="Public URL for the media asset"
    )

    alt_text: Optional[str] = Field(
        default=None,
        description="Alternative text for accessibility"
    )

    width: Optional[int] = Field(
        default=None,
        ge=1,
        description="Image width in pixels"
    )

    height: Optional[int] = Field(
        default=None,
        ge=1,
        description="Image height in pixels"
    )

    file_size: Optional[int] = Field(
        default=None,
        ge=0,
        description="File size in bytes"
    )

    mime_type: Optional[str] = Field(
        default=None,
        description="MIME type of the media file"
    )


class Price(BaseModel):
    """Product pricing information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    amount: float = Field(
        ...,
        ge=0,
        description="Price amount"
    )

    currency_code: str = Field(
        ...,
        pattern=r"^[A-Z]{3}$",
        description="Three-letter ISO currency code"
    )

    compare_at_amount: Optional[float] = Field(
        default=None,
        ge=0,
        description="Compare at price for discounts"
    )

    @computed_field
    @property
    def formatted_price(self) -> str:
        """Format price for display"""
        if self.currency_code == "USD":
            return f"${self.amount:.2f}"
        else:
            return f"{self.amount:.2f} {self.currency_code}"

    @computed_field
    @property
    def has_discount(self) -> bool:
        """Check if item has a discount"""
        return (
            self.compare_at_amount is not None and
            self.compare_at_amount > self.amount
        )


class Inventory(BaseModel):
    """Product inventory tracking"""
    model_config = ConfigDict(validate_assignment=True)

    quantity: int = Field(
        ...,
        ge=0,
        description="Available quantity"
    )

    track_quantity: bool = Field(
        default=True,
        description="Whether to track inventory levels"
    )

    continue_selling_when_out_of_stock: bool = Field(
        default=False,
        description="Allow selling when out of stock"
    )

    inventory_policy: Literal["deny", "continue"] = Field(
        default="deny",
        description="Policy when out of stock"
    )

    @computed_field
    @property
    def in_stock(self) -> bool:
        """Check if item is in stock"""
        if not self.track_quantity:
            return True
        return self.quantity > 0 or self.continue_selling_when_out_of_stock


class ProductVariant(BaseModel):
    """Product variant information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    id: str = Field(
        ...,
        description="Unique variant identifier"
    )

    title: str = Field(
        ...,
        description="Variant title"
    )

    price: Price = Field(
        ...,
        description="Variant pricing"
    )

    inventory: Optional[Inventory] = Field(
        default=None,
        description="Variant inventory information"
    )

    options: Dict[str, str] = Field(
        default_factory=dict,
        description="Variant options (e.g., Size: L, Color: Blue)"
    )

    sku: Optional[str] = Field(
        default=None,
        description="Stock keeping unit"
    )

    weight: Optional[float] = Field(
        default=None,
        ge=0,
        description="Variant weight for shipping"
    )


class SEOMetadata(BaseModel):
    """SEO optimization metadata"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    meta_title: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Page title for search engines"
    )

    meta_description: Optional[str] = Field(
        default=None,
        max_length=160,
        description="Page description for search engines"
    )

    canonical_url: Optional[str] = Field(
        default=None,
        description="Canonical URL for SEO"
    )

    og_title: Optional[str] = Field(
        default=None,
        description="Open Graph title for social sharing"
    )

    og_description: Optional[str] = Field(
        default=None,
        description="Open Graph description for social sharing"
    )

    og_image: Optional[str] = Field(
        default=None,
        description="Open Graph image URL for social sharing"
    )

    keywords: List[str] = Field(
        default_factory=list,
        description="SEO keywords"
    )


class UnifiedContent(BaseModel):
    """
    Unified content schema normalizing data from all CMS and E-commerce providers.
    This schema enables SSG engines to work with any provider combination.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [{
                "id": "gid://shopify/Product/123456789",
                "title": "Premium T-Shirt",
                "slug": "premium-t-shirt",
                "content_type": "product",
                "status": "published",
                "provider_type": "ecommerce",
                "provider_name": "shopify_basic",
                "price": {
                    "amount": 29.99,
                    "currency_code": "USD"
                },
                "created_at": "2025-01-08T10:30:00Z",
                "updated_at": "2025-01-08T10:30:00Z"
            }]
        }
    )

    # Universal content identifiers
    id: str = Field(
        ...,
        description="Unique identifier from source provider"
    )

    title: str = Field(
        ...,
        description="Content title/name"
    )

    slug: str = Field(
        ...,
        description="URL-friendly identifier",
        pattern=r"^[a-z0-9-]+$"
    )

    # Content classification
    content_type: ContentType = Field(
        ...,
        description="Type of content for routing and rendering"
    )

    status: ContentStatus = Field(
        default=ContentStatus.PUBLISHED,
        description="Content publication status"
    )

    # Content body and metadata
    description: Optional[str] = Field(
        default=None,
        description="Content description/excerpt"
    )

    body: Optional[str] = Field(
        default=None,
        description="Full content body (HTML/Markdown)"
    )

    # Media and assets
    featured_image: Optional[MediaAsset] = Field(
        default=None,
        description="Primary image for content"
    )

    images: List[MediaAsset] = Field(
        default_factory=list,
        description="Additional images and media"
    )

    # E-commerce specific fields (Optional for products)
    price: Optional[Price] = Field(
        default=None,
        description="Product pricing information"
    )

    inventory: Optional[Inventory] = Field(
        default=None,
        description="Product inventory tracking"
    )

    variants: List[ProductVariant] = Field(
        default_factory=list,
        description="Product variants (size, color, etc.)"
    )

    # SEO and metadata
    seo: Optional[SEOMetadata] = Field(
        default=None,
        description="SEO optimization data"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Content tags and categories"
    )

    # Provider tracking
    provider_type: Literal["cms", "ecommerce"] = Field(
        ...,
        description="Type of provider that created this content"
    )

    provider_name: str = Field(
        ...,
        description="Specific provider name (e.g., 'shopify_basic', 'sanity')"
    )

    provider_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific data for advanced features"
    )

    # Timestamps and versioning
    created_at: datetime = Field(
        ...,
        description="Content creation timestamp"
    )

    updated_at: datetime = Field(
        ...,
        description="Last modification timestamp"
    )

    synced_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last synchronization with integration layer"
    )

    @computed_field
    @property
    def is_product(self) -> bool:
        """Check if content is a product"""
        return self.content_type == ContentType.PRODUCT

    @computed_field
    @property
    def is_published(self) -> bool:
        """Check if content is published"""
        return self.status == ContentStatus.PUBLISHED

    @computed_field
    @property
    def has_price(self) -> bool:
        """Check if content has pricing information"""
        return self.price is not None

    @computed_field
    @property
    def display_price(self) -> Optional[str]:
        """Get formatted display price"""
        if self.price:
            return self.price.formatted_price
        return None


class ContentEvent(BaseModel):
    """Standard content event format for SNS messaging"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier"
    )

    event_type: Literal[
        "content.created", "content.updated", "content.deleted",
        "inventory.updated", "collection.created", "collection.updated"
    ] = Field(
        ...,
        description="Type of content event"
    )

    # Content identification
    content_id: str = Field(
        ...,
        description="ID of the affected content"
    )

    content_type: ContentType = Field(
        ...,
        description="Type of the affected content"
    )

    provider_name: str = Field(
        ...,
        description="Provider that generated the event"
    )

    # Event metadata
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp"
    )

    requires_build: bool = Field(
        default=True,
        description="Whether this event should trigger site rebuild"
    )

    # Event data
    content_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Content data payload"
    )

    previous_content: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Previous content state for update events"
    )

    # Client context
    client_id: str = Field(
        ...,
        description="Client identifier"
    )

    environment: Literal["dev", "staging", "prod"] = Field(
        default="prod",
        description="Environment context"
    )

    @computed_field
    @property
    def is_creation_event(self) -> bool:
        """Check if this is a content creation event"""
        return self.event_type == "content.created"

    @computed_field
    @property
    def is_update_event(self) -> bool:
        """Check if this is a content update event"""
        return self.event_type == "content.updated"

    @computed_field
    @property
    def is_deletion_event(self) -> bool:
        """Check if this is a content deletion event"""
        return self.event_type == "content.deleted"


class ComponentRegistration(BaseModel):
    """Component registration information for integration layer"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    component_id: str = Field(
        ...,
        description="Unique component identifier"
    )

    component_type: Literal["cms", "ecommerce"] = Field(
        ...,
        description="Type of component"
    )

    provider_name: str = Field(
        ...,
        description="Provider name (e.g., 'shopify_basic', 'sanity')"
    )

    webhook_endpoints: List['WebhookEndpoint'] = Field(
        ...,
        description="Webhook endpoints this component handles"
    )

    supported_events: List[str] = Field(
        ...,
        description="Events this component can generate"
    )

    health_check_url: Optional[str] = Field(
        default=None,
        description="Health check endpoint for monitoring"
    )

    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Component-specific configuration"
    )


class WebhookEndpoint(BaseModel):
    """Webhook endpoint configuration"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    event_type: str = Field(
        ...,
        description="Type of event this endpoint handles"
    )

    endpoint_path: str = Field(
        ...,
        description="API endpoint path"
    )

    http_method: Literal["POST", "PUT", "PATCH"] = Field(
        default="POST",
        description="HTTP method for webhook"
    )

    expected_headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Expected HTTP headers"
    )

    signature_verification: Optional[str] = Field(
        default=None,
        description="Signature verification method (hmac, jwt, etc.)"
    )


class CompositionConfiguration(BaseModel):
    """Configuration for composed CMS + E-commerce stacks"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [{
                "cms_provider": "sanity",
                "ecommerce_provider": "shopify_basic",
                "ssg_engine": "astro",
                "integration_level": "standard",
                "enable_real_time_sync": True,
                "build_on_content_change": True
            }]
        }
    )

    # Provider selection
    cms_provider: str = Field(
        ...,
        description="CMS provider name"
    )

    ecommerce_provider: str = Field(
        ...,
        description="E-commerce provider name"
    )

    ssg_engine: str = Field(
        ...,
        description="Static Site Generator engine"
    )

    # Integration configuration
    integration_level: Literal["minimal", "standard", "full"] = Field(
        default="standard",
        description="Level of integration between providers"
    )

    enable_real_time_sync: bool = Field(
        default=True,
        description="Enable real-time content synchronization"
    )

    build_on_content_change: bool = Field(
        default=True,
        description="Trigger builds on content changes"
    )

    # Advanced options
    content_cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,  # 1 week max
        description="Content cache TTL in hours"
    )

    webhook_retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of webhook retry attempts"
    )

    build_timeout_minutes: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Build timeout in minutes"
    )

    # Provider-specific configurations
    cms_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="CMS provider specific configuration"
    )

    ecommerce_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="E-commerce provider specific configuration"
    )

    @computed_field
    @property
    def composition_id(self) -> str:
        """Generate unique composition identifier"""
        return f"{self.cms_provider}-{self.ecommerce_provider}-{self.ssg_engine}"

    @computed_field
    @property
    def is_shopify_composition(self) -> bool:
        """Check if composition uses Shopify"""
        return self.ecommerce_provider.startswith("shopify")

    @computed_field
    @property
    def complexity_level(self) -> str:
        """Estimate composition complexity level"""
        complexity_scores = {
            ("decap", "snipcart", "eleventy"): "low",
            ("sanity", "shopify_basic", "astro"): "medium",
            ("contentful", "shopify_basic", "nextjs"): "high"
        }

        combination = (self.cms_provider, self.ecommerce_provider, self.ssg_engine)
        return complexity_scores.get(combination, "medium")


class CostBreakdown(BaseModel):
    """Cost breakdown for composition architecture"""
    model_config = ConfigDict(validate_assignment=True)

    # Provider costs
    cms_monthly_cost: float = Field(
        default=0.0,
        ge=0,
        description="Monthly CMS provider cost"
    )

    ecommerce_monthly_cost: float = Field(
        default=0.0,
        ge=0,
        description="Monthly e-commerce provider cost"
    )

    # Infrastructure costs
    aws_hosting_cost: float = Field(
        default=0.0,
        ge=0,
        description="AWS hosting and CDN costs"
    )

    integration_overhead_cost: float = Field(
        default=15.0,
        ge=0,
        description="Integration layer overhead (Lambda, DynamoDB, SNS)"
    )

    # Setup costs
    setup_cost_range: tuple[float, float] = Field(
        default=(2400.0, 4800.0),
        description="Setup cost range (min, max)"
    )

    # Calculated totals
    @computed_field
    @property
    def total_monthly_cost(self) -> float:
        """Calculate total monthly cost"""
        return (
            self.cms_monthly_cost +
            self.ecommerce_monthly_cost +
            self.aws_hosting_cost +
            self.integration_overhead_cost
        )

    @computed_field
    @property
    def estimated_annual_cost(self) -> float:
        """Calculate estimated annual cost"""
        return self.total_monthly_cost * 12

    @computed_field
    @property
    def setup_cost_midpoint(self) -> float:
        """Get midpoint of setup cost range"""
        return (self.setup_cost_range[0] + self.setup_cost_range[1]) / 2


# Forward reference resolution
ComponentRegistration.model_rebuild()