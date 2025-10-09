"""
Core SSG Models

Defines the foundational Pydantic models used across all SSG engines.
These models represent build commands, e-commerce integrations, and templates.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Import centralized enums for type safety
from models.component_enums import SSGEngine, EcommerceProvider

# Type definitions
SSGEngineType = SSGEngine  # Alias for backwards compatibility
ECommerceProvider = EcommerceProvider  # Alias for backwards compatibility

HostingPattern = Literal[
    "aws",           # Full AWS hosting (S3 + CloudFront + Route53)
    "github",        # GitHub Pages hosting only
    "hybrid",        # AWS primary + GitHub Pages fallback
    "aws_minimal"    # AWS hosting with minimal features (cost-optimized)
]


class BuildCommand(BaseModel):
    """Represents a build step for SSG compilation"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "build_site",
                    "command": "npm run build",
                    "environment_vars": {"NODE_ENV": "production"},
                    "timeout_minutes": 10,
                }
            ]
        },
    )

    name: str = Field(..., description="Name of the build step")
    command: str = Field(..., description="Shell command to execute")
    environment_vars: Dict[str, str] = Field(
        default_factory=dict, description="Environment variables for this command"
    )
    timeout_minutes: int = Field(
        default=10, ge=1, le=60, description="Timeout for this build step"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Build command name must be alphanumeric with underscores/hyphens"
            )
        return v

    @field_validator("command")
    @classmethod
    def validate_command(cls, v):
        if not v.strip():
            raise ValueError("Build command cannot be empty")
        return v.strip()


class ECommerceIntegration(BaseModel):
    """E-commerce platform integration configuration"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "provider": "snipcart",
                    "features": ["cart", "checkout", "inventory"],
                    "setup_complexity": "low",
                    "monthly_cost_range": [29, 99],
                    "transaction_fee_percent": 2.0,
                    "integration_method": "javascript_snippet"
                }
            ]
        },
    )

    provider: EcommerceProvider = Field(..., description="E-commerce platform provider")
    features: List[str] = Field(..., description="Available e-commerce features")
    setup_complexity: Literal["low", "medium", "high"] = Field(default="medium")
    monthly_cost_range: List[int] = Field(description="Monthly cost range [min, max]")
    transaction_fee_percent: Optional[float] = Field(None, description="Transaction fee percentage")
    integration_method: Literal[
        "javascript_snippet", "api_integration", "headless_api", "plugin_based", "custom_backend"
    ] = Field(description="How the e-commerce platform integrates")
    required_environment_vars: List[str] = Field(
        default_factory=list, description="Required environment variables"
    )
    build_dependencies: List[str] = Field(
        default_factory=list, description="Additional build dependencies needed"
    )
    aws_services_needed: List[str] = Field(
        default_factory=list, description="Additional AWS services required"
    )


class SSGTemplate(BaseModel):
    """Template configuration for SSG engines"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "business_modern",
                    "description": "Modern business website with hero, services, testimonials",
                    "use_cases": [
                        "business_sites",
                        "professional_services",
                        "consulting",
                    ],
                    "repo_url": "https://github.com/your-templates/eleventy-business-modern",
                    "customization_points": [
                        "colors",
                        "fonts",
                        "hero_content",
                        "services_grid",
                    ],
                    "demo_url": "https://demo.yourservices.com/business-modern",
                    "difficulty_level": "intermediate",
                    "estimated_setup_hours": 2.0,
                    "ecommerce_integration": None
                }
            ]
        },
    )

    name: str = Field(..., description="Template identifier")
    description: str = Field(..., description="Human-readable description")
    use_cases: List[str] = Field(..., description="List of appropriate use cases")
    repo_url: str = Field(..., description="Git repository URL for template")
    customization_points: List[str] = Field(
        ..., description="List of customizable aspects"
    )
    demo_url: Optional[str] = Field(None, description="URL of live demo")
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(
        default="intermediate"
    )
    estimated_setup_hours: float = Field(
        default=2.0, ge=0.5, le=40.0, description="Estimated setup time in hours"
    )
    ecommerce_integration: Optional[ECommerceIntegration] = Field(
        None, description="E-commerce platform integration if applicable"
    )
    supports_ecommerce: bool = Field(
        default=False, description="Whether this template supports e-commerce features"
    )

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v):
        if not (
            v.startswith("https://github.com/") or v.startswith("https://gitlab.com/")
        ):
            raise ValueError("Repository URL must be from GitHub or GitLab")
        return v

    @field_validator("use_cases")
    @classmethod
    def validate_use_cases(cls, v):
        if not v:
            raise ValueError("At least one use case must be specified")
        return v