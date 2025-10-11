"""
SSG Integration Tests

Tests the end-to-end integration between SSG configurations and CDK stacks.
Validates that SSG engine configurations work seamlessly with CDK infrastructure.
"""

import pytest
from aws_cdk import App
from pydantic import ValidationError

from shared.ssg import StaticSiteConfig, SSGEngineFactory
from shared.factories.platform_stack_factory import PlatformStackFactory


class TestSSGIntegration:
    """Test SSG configuration → CDK stack integration"""

    def test_eleventy_stack_integration(self):
        """Test SSG config → Eleventy CDK stack integration"""

        # Create SSG configuration
        ssg_config = StaticSiteConfig(
            client_id="test-client",
            domain="test.example.com",
            ssg_engine="eleventy",
            template_variant="business_modern"
        )

        # Validate configuration works with SSG system
        assert ssg_config.ssg_engine == "eleventy"
        assert ssg_config.get_ssg_config().engine_name == "eleventy"

        # Validate CDK stack can be created
        app = App()
        stack = PlatformStackFactory.create_stack(
            scope=app,
            client_id="test-client",
            domain="test.example.com",
            stack_type="marketing"
        )

        # Validate stack outputs
        outputs = stack.outputs
        assert "content_bucket_name" in outputs
        assert "site_domain" in outputs
        assert outputs["site_domain"] == "test.example.com"

    def test_base_ssg_stack_integration(self):
        """Test base SSG stack can work with any SSG engine"""

        from stacks.shared.base_ssg_stack import BaseSSGStack

        # Test with Astro configuration
        ssg_config = StaticSiteConfig(
            client_id="test-base",
            domain="base.example.com",
            ssg_engine="astro",
            template_variant="modern_interactive"
        )

        # Validate configuration
        assert ssg_config.ssg_engine == "astro"
        engine_config = ssg_config.get_ssg_config()
        assert engine_config.engine_name == "astro"
        assert engine_config.optimization_features["component_islands"] == True

        # Validate base stack can be created with any SSG config
        app = App()
        stack = BaseSSGStack(
            app,
            "TestBaseStack",
            ssg_config
        )

        # Validate stack properties
        assert stack.ssg_config.ssg_engine == "astro"
        assert stack.engine_config.engine_name == "astro"

    def test_ssg_engine_factory_integration(self):
        """Test SSG engine factory with CDK integration"""

        # Test all available engines can be created
        available_engines = SSGEngineFactory.get_available_engines()
        assert len(available_engines) == 7  # All 7 engines

        for engine_type in available_engines:
            engine_config = SSGEngineFactory.create_engine(engine_type)
            assert engine_config.engine_name == engine_type

            # Validate buildspec generation
            buildspec = engine_config.get_buildspec()
            assert "version" in buildspec
            assert "phases" in buildspec
            assert "artifacts" in buildspec

    def test_template_validation_integration(self):
        """Test template validation works with CDK requirements"""

        # Test valid template configuration
        valid_config = StaticSiteConfig(
            client_id="valid-test",
            domain="valid.example.com",
            ssg_engine="eleventy",
            template_variant="business_modern"
        )

        # Should not raise an error
        engine_config = valid_config.get_ssg_config()
        assert engine_config is not None

        # Test invalid template configuration
        with pytest.raises(ValidationError) as exc_info:
            StaticSiteConfig(
                client_id="invalid-test",
                domain="invalid.example.com",
                ssg_engine="eleventy",
                template_variant="nonexistent_template"  # This template doesn't exist
            )

        # Validate error message is helpful
        error_message = str(exc_info.value)
        assert "not available for eleventy" in error_message

    def test_ecommerce_integration(self):
        """Test e-commerce SSG configurations work with CDK"""

        # Test Snipcart e-commerce configuration
        ecommerce_config = StaticSiteConfig(
            client_id="store-test",
            domain="store.example.com",
            ssg_engine="eleventy",
            template_variant="snipcart_ecommerce",
            ecommerce_provider="snipcart",
            ecommerce_config={
                "store_name": "Test Store",
                "currency": "USD"
            }
        )

        # Validate e-commerce integration
        integration = ecommerce_config.get_ecommerce_integration()
        assert integration is not None
        assert integration.provider == "snipcart"

        # Validate required AWS services
        aws_services = ecommerce_config.get_required_aws_services()
        assert "S3" in aws_services
        assert "CloudFront" in aws_services
        assert "Lambda" in aws_services  # For Snipcart integration

        # Validate environment variables
        env_vars = ecommerce_config.get_environment_variables()
        assert "SNIPCART_API_KEY" in env_vars

    def test_aws_tags_generation(self):
        """Test AWS tags are generated correctly for CDK"""

        config = StaticSiteConfig(
            client_id="tag-test",
            domain="tag.example.com",
            ssg_engine="hugo",
            template_variant="corporate_clean",
            performance_tier="premium"
        )

        tags = config.to_aws_tags()

        # Validate required tags for cost allocation
        assert tags["Client"] == "tag-test"
        assert tags["SSGEngine"] == "hugo"
        assert tags["Template"] == "corporate_clean"
        assert tags["PerformanceTier"] == "premium"
        assert tags["Environment"] == "production"
        assert tags["HasECommerce"] == "false"


class TestRevenueCriticalStacks:
    """Test the revenue-critical stacks from Phase 5 roadmap"""

    def test_phase5_foundation_readiness(self):
        """Test Phase 5 foundation: Base SSG stack + first Tier 1 implementation"""

        from stacks.shared.base_ssg_stack import BaseSSGStack

        app = App()

        # Test base SSG stack foundation
        ssg_config = StaticSiteConfig(
            client_id="foundation-test",
            domain="foundation.example.com",
            ssg_engine="hugo",
            template_variant="corporate_clean"
        )

        base_stack = BaseSSGStack(
            app,
            "TestBaseStack",
            ssg_config
        )

        assert base_stack.ssg_config.ssg_engine == "hugo"
        assert len(base_stack.outputs) >= 4

        # Test Eleventy marketing stack (first revenue-critical implementation)
        eleventy_stack = PlatformStackFactory.create_stack(
            scope=app,
            client_id="marketing-test",
            domain="marketing.example.com",
            stack_type="marketing"
        )

        assert eleventy_stack.ssg_config.ssg_engine == "eleventy"
        assert eleventy_stack.ssg_config.template_variant == "business_modern"
        assert len(eleventy_stack.outputs) >= 4

    def test_client_config_ssg_integration(self):
        """Test client configuration system integrates with SSG stacks"""

        from clients._templates.client_config import tier1_developer_managed_client

        # Create client using template function
        client = tier1_developer_managed_client(
            "integration-test",
            "Integration Test Company",
            "integration.example.com",
            "admin@integration.example.com",
            "eleventy_marketing_stack"
        )

        # Validate client configuration
        assert client.service_tier == "tier1"
        assert client.management_model == "developer_managed"
        assert client.stack_type == "eleventy_marketing_stack"

        # Validate deployment name generation
        expected_name = "IntegrationTest-Prod-EleventyMarketingStack"
        assert client.deployment_name == expected_name