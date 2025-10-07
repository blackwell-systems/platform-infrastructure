# Test SSG Engine System
import pytest
from pydantic import ValidationError

from shared.ssg_engines import (
    AstroConfig,
    BuildCommand,
    EleventyConfig,
    HugoConfig,
    SSGEngineFactory,
    SSGTemplate,
    StaticSiteConfig,
)


class TestBuildCommand:
    """Test BuildCommand Pydantic model"""

    def test_valid_build_command(self):
        """Test creating a valid build command"""
        cmd = BuildCommand(
            name="test_build",
            command="npm run build",
            environment_vars={"NODE_ENV": "production"},
            timeout_minutes=15,
        )

        assert cmd.name == "test_build"
        assert cmd.command == "npm run build"
        assert cmd.environment_vars["NODE_ENV"] == "production"
        assert cmd.timeout_minutes == 15

    def test_invalid_build_command_name(self):
        """Test that invalid command names are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            BuildCommand(name="", command="npm run build")  # Empty name

        errors = exc_info.value.errors()
        assert any("Build command name" in str(error["msg"]) for error in errors)

    def test_invalid_build_command_command(self):
        """Test that empty commands are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            BuildCommand(name="test_build", command="")  # Empty command

        errors = exc_info.value.errors()
        assert any(
            "Build command cannot be empty" in str(error["msg"]) for error in errors
        )

    def test_timeout_validation(self):
        """Test timeout minutes validation"""
        # Valid timeout
        cmd = BuildCommand(name="test", command="test", timeout_minutes=30)
        assert cmd.timeout_minutes == 30

        # Invalid timeout (too high)
        with pytest.raises(ValidationError):
            BuildCommand(name="test", command="test", timeout_minutes=100)


class TestSSGTemplate:
    """Test SSGTemplate Pydantic model"""

    def test_valid_template(self):
        """Test creating a valid SSG template"""
        template = SSGTemplate(
            name="test_template",
            description="A test template",
            use_cases=["testing", "development"],
            repo_url="https://github.com/test/repo",
            customization_points=["colors", "fonts", "layout"],
        )

        assert template.name == "test_template"
        assert len(template.use_cases) == 2
        assert template.difficulty_level == "intermediate"  # Default value

    def test_invalid_repo_url(self):
        """Test that invalid repository URLs are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SSGTemplate(
                name="test",
                description="test",
                use_cases=["test"],
                repo_url="https://badsite.com/repo",  # Not GitHub or GitLab
                customization_points=["test"],
            )

        errors = exc_info.value.errors()
        assert any(
            "Repository URL must be from GitHub or GitLab" in str(error["msg"])
            for error in errors
        )

    def test_empty_use_cases(self):
        """Test that empty use cases are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SSGTemplate(
                name="test",
                description="test",
                use_cases=[],  # Empty use cases
                repo_url="https://github.com/test/repo",
                customization_points=["test"],
            )

        errors = exc_info.value.errors()
        assert any(
            "At least one use case must be specified" in str(error["msg"])
            for error in errors
        )


class TestSSGEngineFactory:
    """Test SSG Engine Factory"""

    def test_available_engines(self):
        """Test getting available engines"""
        engines = SSGEngineFactory.get_available_engines()
        assert isinstance(engines, list)
        assert "eleventy" in engines
        assert "hugo" in engines
        assert "astro" in engines
        assert "jekyll" in engines

    def test_create_engine(self):
        """Test creating engine configurations"""
        # Test Eleventy
        eleventy = SSGEngineFactory.create_engine("eleventy")
        assert isinstance(eleventy, EleventyConfig)
        assert eleventy.engine_name == "eleventy"
        assert eleventy.runtime_version == "nodejs-18"

        # Test Hugo
        hugo = SSGEngineFactory.create_engine("hugo")
        assert isinstance(hugo, HugoConfig)
        assert hugo.engine_name == "hugo"
        assert hugo.runtime_version == "golang-1.21"

        # Test Astro
        astro = SSGEngineFactory.create_engine("astro")
        assert isinstance(astro, AstroConfig)
        assert astro.engine_name == "astro"

    def test_unsupported_engine(self):
        """Test that unsupported engines raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported SSG engine"):
            SSGEngineFactory.create_engine("unsupported_engine")

    def test_get_engine_templates(self):
        """Test getting templates for an engine"""
        templates = SSGEngineFactory.get_engine_templates("eleventy")
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert all(isinstance(t, SSGTemplate) for t in templates)


class TestSSGEngineConfigurations:
    """Test individual SSG engine configurations"""

    def test_eleventy_config(self):
        """Test Eleventy configuration"""
        eleventy = EleventyConfig()

        assert eleventy.engine_name == "eleventy"
        assert eleventy.runtime_version == "nodejs-18"
        assert eleventy.output_directory == "_site"

        # Test build commands
        build_commands = eleventy.build_commands
        assert len(build_commands) >= 1
        assert all(isinstance(cmd, BuildCommand) for cmd in build_commands)

        # Test optimization features
        features = eleventy.optimization_features
        assert features["incremental_builds"] is True
        assert features["build_performance"] == "fast"

        # Test templates
        templates = eleventy.available_templates
        assert len(templates) > 0
        assert any(t.name == "business_modern" for t in templates)

    def test_hugo_config(self):
        """Test Hugo configuration"""
        hugo = HugoConfig()

        assert hugo.engine_name == "hugo"
        assert hugo.runtime_version == "golang-1.21"
        assert hugo.output_directory == "public"

        features = hugo.optimization_features
        assert features["extremely_fast_builds"] is True
        assert features["build_performance"] == "extremely_fast"

    def test_astro_config(self):
        """Test Astro configuration"""
        astro = AstroConfig()

        assert astro.engine_name == "astro"
        assert astro.runtime_version == "nodejs-18"
        assert astro.output_directory == "dist"

        features = astro.optimization_features
        assert features["component_islands"] is True
        assert features["zero_js_by_default"] is True


class TestStaticSiteConfig:
    """Test StaticSiteConfig model"""

    def test_valid_config(self):
        """Test creating a valid static site configuration"""
        config = StaticSiteConfig(
            client_id="test-client",
            domain="test.com",
            ssg_engine="eleventy",
            template_variant="business_modern",
        )

        assert config.client_id == "test-client"
        assert config.domain == "test.com"
        assert config.ssg_engine == "eleventy"
        assert config.performance_tier == "optimized"  # Default value

    def test_invalid_client_id(self):
        """Test invalid client ID validation"""
        # Too short
        with pytest.raises(ValidationError):
            StaticSiteConfig(client_id="x", domain="test.com")

        # Invalid characters
        with pytest.raises(ValidationError):
            StaticSiteConfig(
                client_id="test_client", domain="test.com"  # Underscores not allowed
            )

    def test_invalid_domain(self):
        """Test invalid domain validation"""
        with pytest.raises(ValidationError):
            StaticSiteConfig(client_id="test-client", domain="invalid..domain")

    def test_domain_normalization(self):
        """Test that domains are normalized to lowercase"""
        config = StaticSiteConfig(client_id="test-client", domain="TEST.COM")
        assert config.domain == "test.com"

    def test_get_ssg_config(self):
        """Test getting SSG engine configuration"""
        config = StaticSiteConfig(
            client_id="test-client", domain="test.com", ssg_engine="eleventy"
        )

        ssg_config = config.get_ssg_config()
        assert ssg_config.engine_name == "eleventy"

    def test_get_available_templates(self):
        """Test getting available templates"""
        config = StaticSiteConfig(
            client_id="test-client", domain="test.com", ssg_engine="hugo"
        )

        templates = config.get_available_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_aws_tags_generation(self):
        """Test AWS tags generation"""
        config = StaticSiteConfig(
            client_id="test-client",
            domain="test.com",
            ssg_engine="astro",
            template_variant="modern_interactive",
            performance_tier="premium",
        )

        tags = config.to_aws_tags()
        assert tags["Client"] == "test-client"
        assert tags["SSGEngine"] == "astro"
        assert tags["Template"] == "modern_interactive"
        assert tags["PerformanceTier"] == "premium"
        assert tags["Environment"] == "production"


class TestPydanticV2Features:
    """Test Pydantic v2 specific features"""

    def test_config_dict_validation(self):
        """Test that ConfigDict is working properly"""
        # Test whitespace stripping
        config = StaticSiteConfig(
            client_id="  test-client  ",  # Should be stripped
            domain="  test.com  ",  # Should be stripped
        )

        assert config.client_id == "test-client"
        assert config.domain == "test.com"

    def test_json_schema_generation(self):
        """Test JSON schema generation works"""
        schema = StaticSiteConfig.model_json_schema()

        assert "properties" in schema
        assert "client_id" in schema["properties"]
        assert "domain" in schema["properties"]
        assert "examples" in schema

    def test_model_serialization(self):
        """Test model serialization to dict/JSON"""
        config = StaticSiteConfig(client_id="test-client", domain="test.com")

        # Test dict serialization
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["client_id"] == "test-client"

        # Test JSON serialization
        config_json = config.model_dump_json()
        assert isinstance(config_json, str)
        assert "test-client" in config_json

    def test_model_validation_from_dict(self):
        """Test creating model from dictionary"""
        data = {
            "client_id": "test-client",
            "domain": "test.com",
            "ssg_engine": "eleventy",
        }

        config = StaticSiteConfig.model_validate(data)
        assert config.client_id == "test-client"
        assert config.ssg_engine == "eleventy"


if __name__ == "__main__":
    # Run a simple test when executed directly
    print("🚀 Running SSG Engine System Tests")

    # Test basic functionality
    engines = SSGEngineFactory.get_available_engines()
    print(f"Available engines: {engines}")

    eleventy = SSGEngineFactory.create_engine("eleventy")
    print(f"Eleventy engine: {eleventy.engine_name}")

    config = StaticSiteConfig(client_id="demo-client", domain="demo.com")
    print(f"Created config: {config.client_id} -> {config.domain}")

    print("✅ Basic functionality test passed!")
