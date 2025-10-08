"""
Static Site Configuration

Main client integration layer that validates and configures static site deployments.
Handles hosting patterns, e-commerce integration, theme system, and business tier logic.
"""

from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .core_models import SSGEngineType, ECommerceProvider, HostingPattern, ECommerceIntegration
from .base_engine import SSGEngineConfig


class StaticSiteConfig(BaseModel):
    """Configuration for static site deployment with e-commerce support"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
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

    client_id: str = Field(
        ..., description="Unique client identifier", pattern=r"^[a-z0-9-]+$"
    )
    domain: str = Field(..., description="Primary domain for the site")
    ssg_engine: SSGEngineType = Field(
        default="eleventy", description="Static site generator to use"
    )
    template_variant: str = Field(
        default="business_modern", description="Template variant to use"
    )
    custom_build_commands: Optional[List[str]] = Field(
        None, description="Custom build commands if needed"
    )
    environment_vars: Dict[str, str] = Field(
        default_factory=dict, description="Custom environment variables"
    )
    performance_tier: Literal["basic", "optimized", "premium"] = Field(
        default="optimized", description="Performance optimization level"
    )
    
    # Hosting pattern configuration - key business decision per client
    hosting_pattern: Optional[HostingPattern] = Field(
        default=None,
        description="Hosting pattern: 'aws' (full), 'github' (pages only), 'hybrid' (AWS+GitHub), 'aws_minimal' (cost-optimized). Auto-selected based on tier if not specified."
    )
    
    cdn_caching_strategy: Literal["aggressive", "moderate", "minimal"] = Field(
        default="moderate", description="CDN caching strategy"
    )
    
    # E-commerce specific configurations
    ecommerce_provider: Optional[ECommerceProvider] = Field(
        None, description="E-commerce platform provider if applicable"
    )
    ecommerce_config: Dict[str, Any] = Field(
        default_factory=dict, description="E-commerce platform specific configuration"
    )
    
    # Theme system configuration
    theme_id: Optional[str] = Field(
        None,
        description="Theme identifier from theme registry (e.g., 'minimal-mistakes'). If not specified, uses SSG engine default.",
        pattern=r"^[a-z0-9-]+$"
    )
    theme_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Theme-specific customization options (colors, layouts, features, etc.)"
    )
    requires_backend_api: bool = Field(
        default=False, description="Whether this configuration requires backend API services"
    )
    webhook_endpoints: List[str] = Field(
        default_factory=list, description="Required webhook endpoints for e-commerce integrations"
    )

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        # Basic domain validation
        import re

        domain_pattern = (
            r"^[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?)*$"
        )
        if not re.match(domain_pattern, v):
            raise ValueError("Invalid domain format")
        return v.lower()

    @field_validator("client_id")
    @classmethod
    def validate_client_id(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Client ID must be between 3 and 50 characters")
        return v

    @model_validator(mode="after")
    def validate_theme_compatibility(self):
        """Validate theme compatibility with SSG engine and hosting pattern"""
        if self.theme_id:
            theme_info = self.get_theme_info()
            if not theme_info:
                raise ValueError(f"Theme '{self.theme_id}' not found in theme registry")
                
            theme = theme_info["theme"]
            
            # Check hosting pattern compatibility
            if self.hosting_pattern and not theme.is_compatible_with_hosting(self.hosting_pattern):
                raise ValueError(
                    f"Theme '{self.theme_id}' is not compatible with hosting pattern '{self.hosting_pattern}'"
                )
        
        return self
    
    @model_validator(mode="after")
    def validate_template_engine_compatibility(self):
        """Ensure template variant is compatible with selected engine and validate e-commerce config"""
        ssg_engine = self.ssg_engine
        template_variant = self.template_variant

        if ssg_engine and template_variant:
            # Import here to avoid circular imports
            from .factory import SSGEngineFactory
            
            # Get engine configuration - let errors propagate for validation
            engine_config = SSGEngineFactory.create_engine(ssg_engine, template_variant)
            
            # Check if template exists for this engine
            available_templates = [t.name for t in engine_config.available_templates]
            if template_variant not in available_templates:
                available = ", ".join(available_templates)
                raise ValueError(
                    f'Template "{template_variant}" not available for '
                    f'{ssg_engine}. Available: {available}'
                )
            
            # Get the specific template object for e-commerce validation
            template_obj = next(
                (t for t in engine_config.available_templates if t.name == template_variant), 
                None
            )
            
            if template_obj:
                # Check if e-commerce template requires provider
                if template_obj.supports_ecommerce and not self.ecommerce_provider:
                    provider_hint = (
                        template_obj.ecommerce_integration.provider 
                        if template_obj.ecommerce_integration 
                        else "unknown"
                    )
                    raise ValueError(
                        f'Template "{template_variant}" is an e-commerce template but no '
                        f'ecommerce_provider specified. Required provider: {provider_hint}'
                    )
                
                # Check if non-ecommerce template has provider specified
                if not template_obj.supports_ecommerce and self.ecommerce_provider:
                    ecommerce_templates = [
                        t.name for t in engine_config.available_templates 
                        if t.supports_ecommerce
                    ]
                    suggestion = (
                        f" Try: {', '.join(ecommerce_templates)}" 
                        if ecommerce_templates 
                        else ""
                    )
                    raise ValueError(
                        f'Template "{template_variant}" does not support e-commerce but '
                        f'ecommerce_provider "{self.ecommerce_provider}" was specified.{suggestion}'
                    )
                
                # Validate provider matches template integration
                if (template_obj.supports_ecommerce and 
                    template_obj.ecommerce_integration and 
                    self.ecommerce_provider and 
                    template_obj.ecommerce_integration.provider != self.ecommerce_provider):
                    raise ValueError(
                        f'Template "{template_variant}" is configured for '
                        f'{template_obj.ecommerce_integration.provider} but '
                        f'{self.ecommerce_provider} was specified'
                    )

        return self

    @model_validator(mode="after") 
    def set_hosting_pattern_defaults(self):
        """Auto-select hosting pattern based on business tier and client requirements"""
        
        # If hosting pattern is explicitly set, respect the client choice
        if self.hosting_pattern is not None:
            return self
        
        # Matrix-based hosting pattern selection aligned with business strategy
        # Based on tech-stack-product-matrix.md service tier positioning
        
        # Technical tier: Jekyll + GitHub Pages users prefer GitHub/hybrid
        if self.ssg_engine == "jekyll" and self.performance_tier == "basic":
            # Technical users often want GitHub Pages option for cost/control
            self.hosting_pattern = "hybrid"  # AWS primary + GitHub fallback
            
        # Individual/small business tier: Cost-optimized patterns
        elif self.performance_tier == "basic":
            # Basic tier focuses on cost optimization
            if self.ecommerce_provider in ["snipcart", "foxy"]:
                # E-commerce needs AWS for proper integration
                self.hosting_pattern = "aws_minimal"  # Cost-optimized AWS
            else:
                # Static sites can use GitHub for ultra-low cost
                self.hosting_pattern = "github"
                
        # Professional tier: Full AWS with performance optimization
        elif self.performance_tier == "optimized":
            # Professional small business tier needs reliable AWS
            self.hosting_pattern = "aws"  # Full AWS hosting
            
        # Premium/Enterprise tier: Hybrid for maximum flexibility
        elif self.performance_tier == "premium":
            # Premium clients want options and redundancy
            self.hosting_pattern = "hybrid"  # AWS + GitHub fallback
            
        # Default fallback to AWS for undefined cases
        else:
            self.hosting_pattern = "aws"
        
        return self

    def get_hosting_pattern_config(self) -> Dict[str, Any]:
        """Get detailed hosting pattern configuration and costs"""
        
        pattern = self.hosting_pattern or "aws"  # Default fallback
        
        # Hosting pattern configurations aligned with business matrix
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
        # Import here to avoid circular imports
        from .factory import SSGEngineFactory
        return SSGEngineFactory.create_engine(self.ssg_engine, self.template_variant)

    def get_available_templates(self) -> List[Any]:
        """Get available templates for selected engine"""
        # Import here to avoid circular imports  
        from .factory import SSGEngineFactory
        return SSGEngineFactory.get_engine_templates(self.ssg_engine)

    def get_ecommerce_integration(self) -> Optional[ECommerceIntegration]:
        """Get the e-commerce integration configuration for the selected template"""
        if not self.ecommerce_provider:
            return None
            
        try:
            engine_config = self.get_ssg_config()
            template_obj = next(
                (t for t in engine_config.available_templates if t.name == self.template_variant),
                None
            )
            return template_obj.ecommerce_integration if template_obj else None
        except Exception:
            return None
    
    def get_required_aws_services(self) -> List[str]:
        """Get list of AWS services required for this configuration"""
        base_services = ["S3", "CloudFront", "Route53", "Certificate Manager"]
        
        ecommerce_integration = self.get_ecommerce_integration()
        if ecommerce_integration:
            base_services.extend(ecommerce_integration.aws_services_needed)
            
        return list(set(base_services))  # Remove duplicates
    
    def get_theme_info(self) -> Optional[Dict[str, Any]]:
        """Get theme information from theme registry"""
        if not self.theme_id:
            return None
            
        # Import here to avoid circular imports
        try:
            from stacks.shared.theme_registry import ThemeRegistry
            theme = ThemeRegistry.get_theme(self.theme_id)
            if not theme:
                return None
                
            # Validate theme compatibility with engine
            if theme.engine != self.ssg_engine:
                raise ValueError(
                    f"Theme '{self.theme_id}' is for {theme.engine} but engine is {self.ssg_engine}"
                )
                
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
            # Theme registry not available
            return None
    
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
        theme_info = self.get_theme_info()
        if theme_info and "theme_env_vars" in theme_info:
            env_vars.update(theme_info["theme_env_vars"])
        
        return env_vars

    def to_aws_tags(self) -> Dict[str, str]:
        """Convert configuration to AWS resource tags"""
        tags = {
            "Client": self.client_id,
            "SSGEngine": self.ssg_engine,
            "Template": self.template_variant,
            "PerformanceTier": self.performance_tier,
            "Environment": "production",  # Can be parameterized later
            "HostingPattern": self.hosting_pattern or "aws"
        }
        
        if self.theme_id:
            tags["ThemeId"] = self.theme_id
            tags["HasTheme"] = "true"
        else:
            tags["HasTheme"] = "false"
        
        if self.ecommerce_provider:
            tags["ECommerceProvider"] = self.ecommerce_provider
            tags["HasECommerce"] = "true"
        else:
            tags["HasECommerce"] = "false"
            
        return tags