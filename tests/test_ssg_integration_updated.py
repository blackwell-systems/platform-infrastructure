"""
SSG Integration Tests

Tests the end-to-end integration between SSG configurations and CDK stacks.
Validates that SSG engine configurations work seamlessly with CDK infrastructure.
"""

import pytest
from aws_cdk import App
from pydantic import ValidationError

from shared.ssg import StaticSiteConfig, SSGEngineFactory
from shared.factories.ssg_stack_factory import SSGStackFactory


class TestSSGIntegration:
    """Test SSG configuration → CDK stack integration"""

    def test_eleventy_stack_integration(self):
        """Test SSG config → Eleventy CDK stack integration using factory"""

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

        # ✅ REFACTORED: Use SSG Stack Factory instead of manual instantiation
        app = App()
        stack = SSGStackFactory.create_ssg_stack(
            scope=app,
            client_id="test-client",
            domain="test.example.com",
            stack_type="marketing"  # Uses EleventyMarketingStack internally
        )

        # Validate stack outputs
        outputs = stack.outputs
        assert "content_bucket_name" in outputs
        assert "site_domain" in outputs
        assert outputs["site_domain"] == "test.example.com"
