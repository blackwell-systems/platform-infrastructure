"""
Static Site Configuration

Main client integration layer that validates and configures static site deployments.
Handles hosting patterns, e-commerce integration, theme system, and business tier logic.

Refactored to address:
- Circular import issues
- Complex validation methods
- Business logic separation
- Better error handling
- Improved maintainability
"""

from typing import Dict, List, Any, Optional, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, computed_field
import re
from enum import Enum

from .core_models import SSGEngineType, ECommerceProvider, HostingPattern, ECommerceIntegration
from .base_engine import SSGEngineConfig


class PerformanceTier(str, Enum):
    """Performance tier options for static sites"""
    BASIC = "basic"
    OPTIMIZED = "optimized"
    PREMIUM = "premium"


class CachingStrategy(str, Enum):
    """CDN caching strategy options"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class HostingPatternSelector:
    """Service class to handle hosting pattern selection logic"""

    @staticmethod
    def select_optimal_pattern(
        ssg_engine: SSGEngineType,
        performance_tier: PerformanceTier,
        ecommerce_provider: Optional[ECommerceProvider] = None,
        explicit_pattern: Optional[HostingPattern] = None
    ) -> HostingPattern:
        """
        Select optimal hosting pattern based on client requirements.

        Args:
            ssg_engine: Selected SSG engine
            performance_tier: Performance requirements
            ecommerce_provider: E-commerce provider if any
            explicit_pattern: Explicitly requested pattern (overrides auto-selection)

        Returns:
            Optimal hosting pattern for the configuration
        """
        # Respect explicit client choice
        if explicit_pattern:
            return explicit_pattern

        # Technical tier: Jekyll + GitHub Pages users prefer GitHub/hybrid
        if ssg_engine == "jekyll" and performance_tier == PerformanceTier.BASIC:
            return "hybrid"  # AWS primary + GitHub fallback

        # Basic tier with e-commerce needs AWS for integration
        elif performance_tier == PerformanceTier.BASIC:
            if ecommerce_provider in ["snipcart", "foxy"]:
                return "aws_minimal"  # Cost-optimized AWS
            else:
                return "github"  # Ultra-low cost for static sites

        # Professional tier needs reliable AWS
        elif performance_tier == PerformanceTier.OPTIMIZED:
            return "aws"  # Full AWS hosting

        # Premium clients want flexibility and redundancy
        elif performance_tier == PerformanceTier.PREMIUM:
            return "hybrid"  # AWS + GitHub fallback

        # Default fallback
        else:
            return "aws"


class StaticSiteConfig(BaseModel):
    """
    Configuration for static site deployment with comprehensive validation.

    This class handles:
    - SSG engine configuration
    - Template and theme management
    - E-commerce integration
    - Hosting pattern selection
    - AWS resource requirements
    - Environment variable management
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={
            "examples": [
                {
                    "client_id": "demo-client",
                    "domain": "demo-client.com",
                    "ssg_engine": "eleventy",
                    "template_variant": "business_modern",
                    "performance_tier": "optimized",
                    "cdn_caching_strategy": "moderate",
                    "ecommerce_provider": None,
                    "ecommerce_config": {}
                }
            ]
        },
    )

    # Core configuration
    client_id: str = Field(
        ...,
        description="Unique client identifier",
        pattern=r"^[a-z0-9-]+$",
        min_length=3,
        max_length=50
    )
    domain: str = Field(
        ...,
        description="Primary domain for the site"
    )
    ssg_engine: SSGEngineType = Field(
        default="eleventy",
        description="Static site generator to use"
    )
    template_variant: str = Field(
        default="business_modern",
        description="Template variant to use"
    )

    # Build configuration
    custom_build_commands: Optional[List[str]] = Field(
        None,
        description="Custom build commands if needed"
    )
    environment_vars: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom environment variables"
    )

    # Performance and hosting
    performance_tier: PerformanceTier = Field(
        default=PerformanceTier.OPTIMIZED,
        description="Performance optimization level"
    )
    hosting_pattern: Optional[HostingPattern] = Field(
        default=None,
        description="Hosting pattern: auto-selected based on tier if not specified"
    )
    cdn_caching_strategy: CachingStrategy = Field(
        default=CachingStrategy.MODERATE,
        description="CDN caching strategy"
    )

    # E-commerce configuration
    ecommerce_provider: Optional[ECommerceProvider] = Field(
        None,
        description="E-commerce platform provider if applicable"
    )
    ecommerce_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="E-commerce platform specific configuration"
    )

    # Theme system
    theme_id: Optional[str] = Field(
        None,
        description="Theme identifier from theme registry",
        pattern=r"^[a-z0-9-]*$"
    )
    theme_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Theme-specific customization options"
    )

    # Advanced features
    requires_backend_api: bool = Field(
        default=False,
        description="Whether this configuration requires backend API services"
    )
    webhook_endpoints: List[str] = Field(
        default_factory=list,
        description="Required webhook endpoints for e-commerce integrations"
    )

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate domain format"""
        domain_pattern = (
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?)*$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError(f"Invalid domain format: {v}")
        return v.lower()

    @model_validator(mode="after")
    def validate_template_compatibility(self) -> "StaticSiteConfig":
        """Validate template exists for selected SSG engine"""
        try:
            engine_config = self._get_ssg_config()
            available_templates = [t.name for t in engine_config.available_templates]

            if self.template_variant not in available_templates:
                available = ", ".join(available_templates)
                raise ValueError(
                    f'Template "{self.template_variant}" not available for '
                    f'{self.ssg_engine}. Available: {available}'
                )
        except ImportError as e:
            raise ValueError(f"SSG engine configuration not available: {e}")

        return self

    @model_validator(mode="after")
    def validate_ecommerce_configuration(self) -> "StaticSiteConfig":
        """Validate e-commerce provider matches template requirements"""
        if not self.ecommerce_provider:
            return self

        try:
            engine_config = self._get_ssg_config()
            template_obj = next(
                (t for t in engine_config.available_templates
                 if t.name == self.template_variant),
                None
            )

            if not template_obj:
                return self  # Template validation handled elsewhere

            # Check e-commerce template requirements
            if template_obj.supports_ecommerce:
                if template_obj.ecommerce_integration:
                    expected_provider = template_obj.ecommerce_integration.provider
                    if expected_provider != self.ecommerce_provider:
                        raise ValueError(
                            f'Template "{self.template_variant}" requires '
                            f'{expected_provider} but {self.ecommerce_provider} specified'
                        )
            else:
                # Template doesn't support e-commerce but provider specified
                ecommerce_templates = [
                    t.name for t in engine_config.available_templates
                    if t.supports_ecommerce
                ]
                suggestion = f" Try: {', '.join(ecommerce_templates)}" if ecommerce_templates else ""
                raise ValueError(
                    f'Template "{self.template_variant}" does not support e-commerce.{suggestion}'
                )

        except ImportError:
            # Factory not available - skip validation
            pass

        return self

    @model_validator(mode="after")
    def validate_theme_compatibility(self) -> "StaticSiteConfig":
        """Validate theme compatibility with SSG engine and hosting pattern"""
        if not self.theme_id:
            return self

        theme_info = self._get_theme_info()
        if not theme_info:
            raise ValueError(f"Theme '{self.theme_id}' not found in theme registry")

        theme = theme_info["theme"]

        # Check engine compatibility
        if theme.engine != self.ssg_engine:
            raise ValueError(
                f"Theme '{self.theme_id}' is for {theme.engine} but engine is {self.ssg_engine}"
            )

        # Check hosting pattern compatibility
        resolved_pattern = self.resolved_hosting_pattern
        if not theme.is_compatible_with_hosting(resolved_pattern):
            raise ValueError(
                f"Theme '{self.theme_id}' is not compatible with hosting pattern '{resolved_pattern}'"
            )

        return self

    @computed_field
    @property
    def resolved_hosting_pattern(self) -> HostingPattern:
        """Get the resolved hosting pattern (auto-selected if not explicitly set)"""
        return HostingPatternSelector.select_optimal_pattern(
            ssg_engine=self.ssg_engine,
            performance_tier=self.performance_tier,
            ecommerce_provider=self.ecommerce_provider,
            explicit_pattern=self.hosting_pattern
        )

    def get_hosting_pattern_config(self) -> Dict[str, Any]:
        """Get detailed hosting pattern configuration and costs"""
        pattern = self.resolved_hosting_pattern

        configs = {
            "aws": {
                "name": "Full AWS Hosting",
                "description": "Complete AWS hosting with S3, CloudFront, and Route53",
                "services": ["S3", "CloudFront", "Route53", "Certificate Manager", "CodeBuild"],
                "monthly_cost_range": "$5-50",
                "setup_complexity": "Medium",
                "best_for": ["Professional sites", "Business tier", "Custom domains"],
                "features": ["Global CDN", "SSL certificates", "Custom domains", "Performance optimization"]
            },
            "github": {
                "name": "GitHub Pages Only",
                "description": "GitHub Pages hosting with optional custom domain",
                "services": ["GitHub Pages"],
                "monthly_cost_range": "$0",
                "setup_complexity": "Low",
                "best_for": ["Technical users", "Documentation", "Personal sites"],
                "features": ["Free hosting", "Git-based workflow", "Built-in CI/CD", "Jekyll support"]
            },
            "hybrid": {
                "name": "AWS + GitHub Fallback",
                "description": "Primary AWS hosting with GitHub Pages as backup option",
                "services": ["S3", "CloudFront", "Route53", "GitHub Pages"],
                "monthly_cost_range": "$5-50 (AWS) + $0 (GitHub)",
                "setup_complexity": "High",
                "best_for": ["Technical users", "Enterprise clients", "Maximum flexibility"],
                "features": ["Redundancy", "Cost flexibility", "Multiple deployment options", "Technical control"]
            },
            "aws_minimal": {
                "name": "Cost-Optimized AWS",
                "description": "AWS hosting with minimal features for cost optimization",
                "services": ["S3", "CloudFront (basic)", "Route53"],
                "monthly_cost_range": "$1-15",
                "setup_complexity": "Low",
                "best_for": ["Budget-conscious clients", "Simple sites", "Basic e-commerce"],
                "features": ["Low cost", "Essential CDN", "Basic SSL", "Simplified setup"]
            }
        }

        return configs.get(pattern, configs["aws"])

    def get_ssg_config(self) -> SSGEngineConfig:
        """Get the SSG engine configuration"""
        return self._get_ssg_config()

    def get_available_templates(self) -> List[Any]:
        """Get available templates for selected engine"""
        try:
            from .factory import SSGEngineFactory
            return SSGEngineFactory.get_engine_templates(self.ssg_engine)
        except ImportError:
            return []

    def get_ecommerce_integration(self) -> Optional[ECommerceIntegration]:
        """Get the e-commerce integration configuration for the selected template"""
        if not self.ecommerce_provider:
            return None

        try:
            engine_config = self._get_ssg_config()
            template_obj = next(
                (t for t in engine_config.available_templates
                 if t.name == self.template_variant),
                None
            )
            return template_obj.ecommerce_integration if template_obj else None
        except (ImportError, AttributeError):
            return None

    def get_required_aws_services(self) -> List[str]:
        """Get list of AWS services required for this configuration"""
        base_services = ["S3", "CloudFront", "Route53", "Certificate Manager"]

        ecommerce_integration = self.get_ecommerce_integration()
        if ecommerce_integration:
            base_services.extend(ecommerce_integration.aws_services_needed)

        return sorted(list(set(base_services)))  # Remove duplicates and sort

    def get_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables including e-commerce and theme specific ones"""
        env_vars = self.environment_vars.copy()

        # Add e-commerce environment variables
        ecommerce_integration = self.get_ecommerce_integration()
        if ecommerce_integration:
            for var in ecommerce_integration.required_environment_vars:
                if var not in env_vars:
                    env_vars[var] = f"${{{var}}}"  # Placeholder for CDK parameter

        # Add theme environment variables
        theme_info = self._get_theme_info()
        if theme_info and "theme_env_vars" in theme_info:
            env_vars.update(theme_info["theme_env_vars"])

        return env_vars

    def to_aws_tags(self) -> Dict[str, str]:
        """Convert configuration to AWS resource tags"""
        tags = {
            "Client": self.client_id,
            "SSGEngine": self.ssg_engine,
            "Template": self.template_variant,
            "PerformanceTier": str(self.performance_tier),  # Handle both enum and string values
            "Environment": "production",  # Can be parameterized later
            "HostingPattern": self.resolved_hosting_pattern,
            "HasTheme": "true" if self.theme_id else "false",
            "HasECommerce": "true" if self.ecommerce_provider else "false"
        }

        if self.theme_id:
            tags["ThemeId"] = self.theme_id

        if self.ecommerce_provider:
            tags["ECommerceProvider"] = self.ecommerce_provider

        return tags

    # Private helper methods
    def _get_ssg_config(self) -> SSGEngineConfig:
        """Get SSG engine configuration with proper error handling"""
        try:
            from .factory import SSGEngineFactory
            return SSGEngineFactory.create_engine(self.ssg_engine, self.template_variant)
        except ImportError as e:
            raise ImportError(f"SSG Factory not available: {e}")

    def _get_theme_info(self) -> Optional[Dict[str, Any]]:
        """Get theme information from theme registry with graceful fallback"""
        if not self.theme_id:
            return None

        try:
            from shared.theme_registry import ThemeRegistry
            theme = ThemeRegistry.get_theme(self.theme_id)
            if not theme:
                return None

            return {
                "theme": theme,
                "installation_method": theme.installation_method,
                "source": theme.source,
                "required_plugins": theme.required_plugins,
                "github_pages_compatible": theme.github_pages_compatible,
                "customization_options": theme.customization_options,
                "installation_commands": theme.get_installation_commands(),
                "theme_env_vars": theme.get_customization_env_vars(self.theme_config)
            }
        except ImportError:
            # Theme registry not available - return None gracefully
            return None
        except AttributeError as e:
            # Theme object missing expected methods
            return None