# Test SSG Engine System (without CDK dependencies)

from typing import Dict, List, Literal, Optional, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, field_validator, ValidationError

# Copy the core system without CDK imports for testing
SSGEngineType = Literal["eleventy", "hugo", "astro", "jekyll"]

class BuildCommand(BaseModel):
    name: str = Field(..., description="Name of the build step")
    command: str = Field(..., description="Shell command to execute")
    environment_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    timeout_minutes: int = Field(default=10, ge=1, le=60, description="Timeout for this build step")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Build command name must be alphanumeric with underscores/hyphens')
        return v

class SSGTemplate(BaseModel):
    name: str = Field(..., description="Template identifier")
    description: str = Field(..., description="Human-readable description")
    use_cases: List[str] = Field(..., description="List of appropriate use cases")
    repo_url: str = Field(..., description="Git repository URL for template")
    customization_points: List[str] = Field(..., description="List of customizable aspects")
    demo_url: Optional[str] = Field(None, description="URL of live demo")
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = Field(default="intermediate")

    @field_validator('repo_url')
    @classmethod
    def validate_repo_url(cls, v):
        if not (v.startswith('https://github.com/') or v.startswith('https://gitlab.com/')):
            raise ValueError('Repository URL must be from GitHub or GitLab')
        return v

class SSGEngineConfig(ABC):
    def __init__(self, template_variant: str = "default"):
        self.template_variant = template_variant

    @property
    @abstractmethod
    def engine_name(self) -> str:
        pass

    @property
    @abstractmethod
    def runtime_version(self) -> str:
        pass

    @property
    @abstractmethod
    def build_commands(self) -> List[BuildCommand]:
        pass

    @property
    @abstractmethod
    def optimization_features(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def available_templates(self) -> List[SSGTemplate]:
        pass

class EleventyConfig(SSGEngineConfig):
    @property
    def engine_name(self) -> str:
        return "eleventy"

    @property
    def runtime_version(self) -> str:
        return "nodejs-18"

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(name="build_site", command="npx @11ty/eleventy", environment_vars={"ELEVENTY_PRODUCTION": "true"}),
            BuildCommand(name="optimize_assets", command="npm run optimize", environment_vars={"NODE_ENV": "production"})
        ]

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "incremental_builds": True,
            "template_caching": True,
            "build_performance": "fast",
            "html_minification": True
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="business_modern",
                description="Modern business website with hero, services, testimonials",
                use_cases=["business_sites", "professional_services"],
                repo_url="https://github.com/your-templates/eleventy-business-modern",
                customization_points=["colors", "fonts", "hero_content", "services_grid"]
            )
        ]

class HugoConfig(SSGEngineConfig):
    @property
    def engine_name(self) -> str:
        return "hugo"

    @property
    def runtime_version(self) -> str:
        return "golang-1.21"

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(name="build_site", command="hugo --minify --gc", environment_vars={"HUGO_ENV": "production"})
        ]

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "extremely_fast_builds": True,
            "built_in_minification": True,
            "build_performance": "extremely_fast"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="corporate_clean",
                description="Clean corporate design",
                use_cases=["corporate_sites", "large_content_sites"],
                repo_url="https://github.com/your-templates/hugo-corporate-clean",
                customization_points=["theme_colors", "layout_options"]
            )
        ]

class AstroConfig(SSGEngineConfig):
    @property
    def engine_name(self) -> str:
        return "astro"

    @property
    def runtime_version(self) -> str:
        return "nodejs-18"

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(name="build_site", command="npm run build", environment_vars={"NODE_ENV": "production"})
        ]

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "component_islands": True,
            "partial_hydration": True,
            "zero_js_by_default": True,
            "build_performance": "fast"
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="modern_interactive",
                description="Interactive components with React/Vue islands",
                use_cases=["interactive_sites", "modern_apps"],
                repo_url="https://github.com/your-templates/astro-modern-interactive",
                customization_points=["component_framework", "interactive_elements"]
            )
        ]

class SSGEngineFactory:
    _engines = {
        "eleventy": EleventyConfig,
        "hugo": HugoConfig,
        "astro": AstroConfig
    }

    @classmethod
    def create_engine(cls, engine_type: SSGEngineType, template_variant: str = "default") -> SSGEngineConfig:
        if engine_type not in cls._engines:
            raise ValueError(f"Unsupported SSG engine: {engine_type}")
        return cls._engines[engine_type](template_variant)

    @classmethod
    def get_available_engines(cls) -> List[str]:
        return list(cls._engines.keys())

class StaticSiteConfig(BaseModel):
    client_id: str = Field(..., description="Unique client identifier", pattern=r'^[a-z0-9-]+$')
    domain: str = Field(..., description="Primary domain for the site")
    ssg_engine: SSGEngineType = Field(default="eleventy", description="Static site generator to use")
    template_variant: str = Field(default="business_modern", description="Template variant to use")
    performance_tier: Literal["basic", "optimized", "premium"] = Field(default="optimized", description="Performance optimization level")

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{1,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid domain format')
        return v.lower()

    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Client ID must be between 3 and 50 characters')
        return v

    def get_ssg_config(self) -> SSGEngineConfig:
        return SSGEngineFactory.create_engine(self.ssg_engine, self.template_variant)

# Test the system
if __name__ == "__main__":
    print("🚀 Testing SSG Engine System")
    print("=" * 50)

    # Test 1: Factory functionality
    print("\n1. Available SSG Engines:")
    engines = SSGEngineFactory.get_available_engines()
    print(f"   {', '.join(engines)}")

    # Test 2: Engine configurations
    print("\n2. Engine Configurations:")
    for engine_type in engines:
        engine = SSGEngineFactory.create_engine(engine_type)
        print(f"   {engine.engine_name}:")
        print(f"     • Runtime: {engine.runtime_version}")
        print(f"     • Build Performance: {engine.optimization_features.get('build_performance', 'N/A')}")
        print(f"     • Templates: {len(engine.available_templates)}")

    # Test 3: Client configuration
    print("\n3. Client Configuration Example:")
    client_config = StaticSiteConfig(
        client_id="demo-client",
        domain="demo-client.yourservices.com",
        ssg_engine="eleventy",
        template_variant="business_modern"
    )

    ssg_config = client_config.get_ssg_config()
    print(f"   Client: {client_config.client_id}")
    print(f"   Engine: {ssg_config.engine_name}")
    print(f"   Template: {client_config.template_variant}")
    print(f"   Build Commands: {len(ssg_config.build_commands)}")

    # Test 4: Template system
    print("\n4. Template Details:")
    template = ssg_config.available_templates[0]
    print(f"   Name: {template.name}")
    print(f"   Description: {template.description}")
    print(f"   Use Cases: {', '.join(template.use_cases)}")
    print(f"   Customization Points: {len(template.customization_points)}")

    # Test 5: Build command details
    print("\n5. Build Pipeline:")
    for i, cmd in enumerate(ssg_config.build_commands, 1):
        print(f"   Step {i}: {cmd.name}")
        print(f"     Command: {cmd.command}")
        print(f"     Env Vars: {cmd.environment_vars}")

    # Test 6: Pydantic Validation
    print("\n6. Pydantic Validation Tests:")

    # Valid configuration
    try:
        valid_config = StaticSiteConfig(
            client_id="demo-client",
            domain="demo-client.com",
            ssg_engine="eleventy",
            template_variant="business_modern"
        )
        print("   ✅ Valid configuration accepted")
        print(f"      Domain normalized: {valid_config.domain}")
    except ValidationError as e:
        print(f"   ❌ Unexpected validation error: {e}")

    # Invalid client ID (should fail)
    try:
        invalid_config = StaticSiteConfig(
            client_id="X",  # Too short
            domain="demo.com"
        )
        print("   ❌ Should have failed client ID validation!")
    except ValidationError as e:
        print("   ✅ Correctly rejected invalid client ID")
        print(f"      Error: {e.errors()[0]['msg']}")

    # Invalid domain (should fail)
    try:
        invalid_domain = StaticSiteConfig(
            client_id="demo-client",
            domain="invalid..domain"  # Invalid format
        )
        print("   ❌ Should have failed domain validation!")
    except ValidationError as e:
        print("   ✅ Correctly rejected invalid domain")
        print(f"      Error: {e.errors()[0]['msg']}")

    # Test JSON serialization
    print("\n7. Pydantic Serialization:")
    config_dict = valid_config.dict()
    print(f"   Serialized: {config_dict}")

    # Test JSON Schema generation
    schema = StaticSiteConfig.schema()
    print(f"   Schema properties: {len(schema['properties'])} fields")
    print(f"   Required fields: {schema.get('required', [])}")

    print("\n✅ SSG Engine System Test Complete!")
    print("\nPydantic Benefits Demonstrated:")
    print("   ✅ Automatic data validation")
    print("   ✅ Type safety and coercion")
    print("   ✅ Detailed error messages")
    print("   ✅ JSON serialization/deserialization")
    print("   ✅ Schema generation for documentation")

    print("\nNext Steps:")
    print("   • Integrate with CDK static site stacks")
    print("   • Create actual template repositories")
    print("   • Build CodeBuild integration")
    print("   • Test with real client configurations")