# SSG Engine Configuration System
# Foundation for all static site stacks

from typing import Dict, List, Literal, Optional, Any, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, validator, root_validator
import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild


SSGEngineType = Literal["eleventy", "hugo", "astro", "jekyll"]


class BuildCommand(BaseModel):
    """Represents a build step for SSG compilation"""
    name: str = Field(..., description="Name of the build step")
    command: str = Field(..., description="Shell command to execute")
    environment_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables for this command")
    timeout_minutes: int = Field(default=10, ge=1, le=60, description="Timeout for this build step")

    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Build command name must be alphanumeric with underscores/hyphens')
        return v

    @validator('command')
    def validate_command(cls, v):
        if not v.strip():
            raise ValueError('Build command cannot be empty')
        return v.strip()


class SSGTemplate(BaseModel):
    """Template configuration for SSG engines"""
    name: str = Field(..., description="Template identifier")
    description: str = Field(..., description="Human-readable description")
    use_cases: List[str] = Field(..., description="List of appropriate use cases")
    repo_url: str = Field(..., description="Git repository URL for template")
    customization_points: List[str] = Field(..., description="List of customizable aspects")
    demo_url: Optional[str] = Field(None, description="URL of live demo")
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(default="intermediate")
    estimated_setup_hours: float = Field(default=2.0, ge=0.5, le=40.0, description="Estimated setup time in hours")

    @validator('repo_url')
    def validate_repo_url(cls, v):
        if not (v.startswith('https://github.com/') or v.startswith('https://gitlab.com/')):
            raise ValueError('Repository URL must be from GitHub or GitLab')
        return v

    @validator('use_cases')
    def validate_use_cases(cls, v):
        if not v:
            raise ValueError('At least one use case must be specified')
        return v


class SSGEngineConfig(ABC):
    """Abstract base class for SSG engine configurations"""

    def __init__(self, template_variant: str = "default"):
        self.template_variant = template_variant

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of the SSG engine"""
        pass

    @property
    @abstractmethod
    def runtime_version(self) -> str:
        """Node.js or other runtime version"""
        pass

    @property
    @abstractmethod
    def install_commands(self) -> List[str]:
        """Commands to install dependencies"""
        pass

    @property
    @abstractmethod
    def build_commands(self) -> List[BuildCommand]:
        """Commands to build the site"""
        pass

    @property
    @abstractmethod
    def output_directory(self) -> str:
        """Directory containing built site files"""
        pass

    @property
    @abstractmethod
    def optimization_features(self) -> Dict[str, Any]:
        """Engine-specific optimization settings"""
        pass

    @property
    @abstractmethod
    def available_templates(self) -> List[SSGTemplate]:
        """Templates available for this engine"""
        pass

    def get_codebuild_environment(self) -> codebuild.BuildEnvironment:
        """Generate CodeBuild environment for this engine"""
        return codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
            environment_variables={
                "SSG_ENGINE": codebuild.BuildEnvironmentVariable(value=self.engine_name),
                "TEMPLATE_VARIANT": codebuild.BuildEnvironmentVariable(value=self.template_variant),
                "OUTPUT_DIR": codebuild.BuildEnvironmentVariable(value=self.output_directory),
            }
        )

    def get_buildspec(self) -> Dict[str, Any]:
        """Generate CodeBuild buildspec for this engine"""
        install_phase = {
            "runtime-versions": {"nodejs": self.runtime_version.split("nodejs-")[1]},
            "commands": self.install_commands
        }

        build_phase = {
            "commands": [cmd.command for cmd in self.build_commands]
        }

        return {
            "version": "0.2",
            "phases": {
                "install": install_phase,
                "build": build_phase
            },
            "artifacts": {
                "files": ["**/*"],
                "base-directory": self.output_directory
            }
        }


class EleventyConfig(SSGEngineConfig):
    """Eleventy (11ty) SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "eleventy"

    @property
    def runtime_version(self) -> str:
        return "nodejs-18"

    @property
    def install_commands(self) -> List[str]:
        return [
            "npm ci",  # Clean install from package-lock.json
            "npm install -g @11ty/eleventy"  # Global install for CLI
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npx @11ty/eleventy",
                environment_vars={"ELEVENTY_PRODUCTION": "true"}
            ),
            BuildCommand(
                name="optimize_assets",
                command="npm run optimize",  # Custom optimization script
                environment_vars={"NODE_ENV": "production"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "_site"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "incremental_builds": True,
            "template_caching": True,
            "asset_optimization": True,
            "html_minification": True,
            "css_minification": True,
            "js_minification": True,
            "image_optimization": True,
            "build_performance": "fast"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="business_modern",
                description="Modern business website with hero, services, testimonials",
                use_cases=["business_sites", "professional_services", "consulting"],
                repo_url="https://github.com/your-templates/eleventy-business-modern",
                customization_points=["colors", "fonts", "hero_content", "services_grid", "contact_info"],
                demo_url="https://demo.yourservices.com/business-modern"
            ),
            SSGTemplate(
                name="service_provider",
                description="Service-focused layout with pricing, FAQ, booking integration",
                use_cases=["service_businesses", "freelancers", "agencies"],
                repo_url="https://github.com/your-templates/eleventy-service-provider",
                customization_points=["service_categories", "pricing_tiers", "booking_system", "testimonials"],
                demo_url="https://demo.yourservices.com/service-provider"
            ),
            SSGTemplate(
                name="marketing_landing",
                description="High-conversion landing page with clear CTA and social proof",
                use_cases=["product_launches", "lead_generation", "campaigns"],
                repo_url="https://github.com/your-templates/eleventy-marketing-landing",
                customization_points=["hero_cta", "feature_highlights", "social_proof", "conversion_forms"],
                demo_url="https://demo.yourservices.com/marketing-landing"
            )
        ]


class HugoConfig(SSGEngineConfig):
    """Hugo SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "hugo"

    @property
    def runtime_version(self) -> str:
        return "golang-1.21"  # Hugo is Go-based

    @property
    def install_commands(self) -> List[str]:
        return [
            "wget https://github.com/gohugoio/hugo/releases/download/v0.121.0/hugo_extended_0.121.0_Linux-64bit.tar.gz",
            "tar -xzf hugo_extended_0.121.0_Linux-64bit.tar.gz",
            "chmod +x hugo",
            "sudo mv hugo /usr/local/bin/"
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="hugo --minify --gc",
                environment_vars={"HUGO_ENV": "production"}
            ),
            BuildCommand(
                name="optimize_images",
                command="hugo --minify --gc --enableGitInfo",
                environment_vars={"HUGO_ENV": "production"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "public"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "extremely_fast_builds": True,
            "built_in_minification": True,
            "image_processing": True,
            "asset_bundling": True,
            "template_caching": True,
            "incremental_builds": False,  # Hugo rebuilds everything but very fast
            "build_performance": "extremely_fast"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="corporate_clean",
                description="Clean corporate design with powerful content management",
                use_cases=["corporate_sites", "large_content_sites", "multi_language"],
                repo_url="https://github.com/your-templates/hugo-corporate-clean",
                customization_points=["theme_colors", "layout_options", "content_sections", "navigation"],
                demo_url="https://demo.yourservices.com/hugo-corporate"
            ),
            SSGTemplate(
                name="content_publisher",
                description="Content-heavy site with blog, resources, and knowledge base",
                use_cases=["content_sites", "blogs", "documentation", "knowledge_bases"],
                repo_url="https://github.com/your-templates/hugo-content-publisher",
                customization_points=["content_taxonomy", "search_functionality", "author_profiles", "content_types"],
                demo_url="https://demo.yourservices.com/hugo-content"
            )
        ]


class AstroConfig(SSGEngineConfig):
    """Astro SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "astro"

    @property
    def runtime_version(self) -> str:
        return "nodejs-18"

    @property
    def install_commands(self) -> List[str]:
        return [
            "npm ci",
            "npm install -g astro"
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="npm run build",
                environment_vars={"NODE_ENV": "production"}
            ),
            BuildCommand(
                name="optimize_components",
                command="npm run build:optimize",
                environment_vars={"ASTRO_TELEMETRY_DISABLED": "1"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "dist"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "component_islands": True,
            "partial_hydration": True,
            "framework_agnostic": True,
            "zero_js_by_default": True,
            "built_in_optimizations": True,
            "modern_build_tools": True,
            "typescript_support": True,
            "build_performance": "fast"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="modern_interactive",
                description="Interactive components with React/Vue islands for dynamic features",
                use_cases=["interactive_sites", "component_showcases", "modern_apps"],
                repo_url="https://github.com/your-templates/astro-modern-interactive",
                customization_points=["component_framework", "interactive_elements", "styling_system", "integrations"],
                demo_url="https://demo.yourservices.com/astro-interactive"
            ),
            SSGTemplate(
                name="performance_focused",
                description="Ultra-fast loading with component islands and minimal JavaScript",
                use_cases=["performance_critical", "mobile_first", "conversion_optimization"],
                repo_url="https://github.com/your-templates/astro-performance",
                customization_points=["performance_budgets", "critical_css", "lazy_loading", "optimization_settings"],
                demo_url="https://demo.yourservices.com/astro-performance"
            )
        ]


class JekyllConfig(SSGEngineConfig):
    """Jekyll SSG engine configuration (for GitHub Pages)"""

    @property
    def engine_name(self) -> str:
        return "jekyll"

    @property
    def runtime_version(self) -> str:
        return "ruby-3.1"

    @property
    def install_commands(self) -> List[str]:
        return [
            "gem install bundler",
            "bundle install"
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="bundle exec jekyll build",
                environment_vars={"JEKYLL_ENV": "production"}
            )
        ]

    @property
    def output_directory(self) -> str:
        return "_site"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "github_pages_compatible": True,
            "liquid_templating": True,
            "markdown_processing": True,
            "sass_support": True,
            "plugin_ecosystem": True,
            "free_hosting": True,  # GitHub Pages
            "build_performance": "moderate"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="nonprofit_charity",
                description="Charity/nonprofit focused with donation integration and volunteer signup",
                use_cases=["nonprofits", "charities", "community_organizations"],
                repo_url="https://github.com/your-templates/jekyll-nonprofit",
                customization_points=["cause_focus", "donation_integration", "volunteer_forms", "impact_metrics"],
                demo_url="https://demo.yourservices.com/jekyll-nonprofit"
            ),
            SSGTemplate(
                name="simple_blog",
                description="Clean, simple blog with GitHub Pages compatibility",
                use_cases=["personal_blogs", "content_creators", "documentation"],
                repo_url="https://github.com/your-templates/jekyll-simple-blog",
                customization_points=["theme_colors", "layout_style", "social_integration", "comments_system"],
                demo_url="https://demo.yourservices.com/jekyll-blog"
            )
        ]


class SSGEngineFactory:
    """Factory for creating SSG engine configurations"""

    _engines = {
        "eleventy": EleventyConfig,
        "hugo": HugoConfig,
        "astro": AstroConfig,
        "jekyll": JekyllConfig
    }

    @classmethod
    def create_engine(cls, engine_type: SSGEngineType, template_variant: str = "default") -> SSGEngineConfig:
        """Create an SSG engine configuration"""
        if engine_type not in cls._engines:
            raise ValueError(f"Unsupported SSG engine: {engine_type}")

        return cls._engines[engine_type](template_variant)

    @classmethod
    def get_available_engines(cls) -> List[str]:
        """Get list of available SSG engines"""
        return list(cls._engines.keys())

    @classmethod
    def get_engine_templates(cls, engine_type: SSGEngineType) -> List[SSGTemplate]:
        """Get available templates for an engine"""
        engine = cls.create_engine(engine_type)
        return engine.available_templates


# Client Configuration Integration
class StaticSiteConfig(BaseModel):
    """Configuration for static site deployment"""
    client_id: str = Field(..., description="Unique client identifier", regex=r'^[a-z0-9-]+$')
    domain: str = Field(..., description="Primary domain for the site")
    ssg_engine: SSGEngineType = Field(default="eleventy", description="Static site generator to use")
    template_variant: str = Field(default="business_modern", description="Template variant to use")
    custom_build_commands: Optional[List[str]] = Field(None, description="Custom build commands if needed")
    environment_vars: Dict[str, str] = Field(default_factory=dict, description="Custom environment variables")
    performance_tier: Literal["basic", "optimized", "premium"] = Field(default="optimized", description="Performance optimization level")
    cdn_caching_strategy: Literal["aggressive", "moderate", "minimal"] = Field(default="moderate", description="CDN caching strategy")

    @validator('domain')
    def validate_domain(cls, v):
        # Basic domain validation
        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid domain format')
        return v.lower()

    @validator('client_id')
    def validate_client_id(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Client ID must be between 3 and 50 characters')
        return v

    @root_validator
    def validate_template_engine_compatibility(cls, values):
        """Ensure template variant is compatible with selected engine"""
        ssg_engine = values.get('ssg_engine')
        template_variant = values.get('template_variant')

        if ssg_engine and template_variant:
            try:
                engine_config = SSGEngineFactory.create_engine(ssg_engine, template_variant)
                available_templates = [t.name for t in engine_config.available_templates]
                if template_variant not in available_templates:
                    available = ', '.join(available_templates)
                    raise ValueError(f'Template "{template_variant}" not available for {ssg_engine}. Available: {available}')
            except Exception:
                # During initialization, factory might not be ready
                pass

        return values

    def get_ssg_config(self) -> SSGEngineConfig:
        """Get the SSG engine configuration"""
        return SSGEngineFactory.create_engine(self.ssg_engine, self.template_variant)

    def get_available_templates(self) -> List[SSGTemplate]:
        """Get available templates for selected engine"""
        return SSGEngineFactory.get_engine_templates(self.ssg_engine)

    def to_aws_tags(self) -> Dict[str, str]:
        """Convert configuration to AWS resource tags"""
        return {
            "Client": self.client_id,
            "SSGEngine": self.ssg_engine,
            "Template": self.template_variant,
            "PerformanceTier": self.performance_tier,
            "Environment": "production"  # Can be parameterized later
        }


# Usage Examples and Testing
if __name__ == "__main__":
    # Example: Create different engine configurations
    eleventy = SSGEngineFactory.create_engine("eleventy", "business_modern")
    hugo = SSGEngineFactory.create_engine("hugo", "corporate_clean")
    astro = SSGEngineFactory.create_engine("astro", "modern_interactive")

    print(f"Eleventy templates: {len(eleventy.available_templates)}")
    print(f"Hugo build performance: {hugo.optimization_features['build_performance']}")
    print(f"Astro supports component islands: {astro.optimization_features['component_islands']}")

    # Example: Client configuration
    client_config = StaticSiteConfig(
        client_id="demo-client",
        domain="demo-client.yourservices.com",
        ssg_engine="eleventy",
        template_variant="business_modern"
    )

    ssg_config = client_config.get_ssg_config()
    buildspec = ssg_config.get_buildspec()
    print(f"Generated buildspec for {ssg_config.engine_name}")