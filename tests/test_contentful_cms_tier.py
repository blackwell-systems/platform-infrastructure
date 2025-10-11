"""
Test Suite for Contentful CMS Tier Implementation

This comprehensive test suite validates the Contentful CMS tier stack implementation,
provider functionality, factory integration, and business requirements.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os

# Contentful CMS components
from stacks.cms.contentful_cms_stack import ContentfulCMSStack
from shared.providers.cms.contentful_provider import (
    ContentfulProvider,
    ContentfulContentSettings,
    ContentfulBuildSettings,
    ContentfulEnvironment,
    ContentfulAPIType
)
from shared.factories.platform_stack_factory import PlatformStackFactory
from shared.ssg.core_models import SSGEngineType
from models.service_config import ClientServiceConfig


class TestContentfulProvider:
    """Test Contentful CMS provider functionality"""

    def test_provider_initialization(self):
        """Test Contentful provider initialization with basic parameters"""
        provider = ContentfulProvider(
            space_id="test-space-123",
            environment="master",
            ssg_engine="gatsby"
        )

        assert provider.space_id == "test-space-123"
        assert provider.environment == "master"
        assert provider.ssg_engine == "gatsby"
        assert provider.provider_name == "contentful"
        assert provider.provider_type == "api_based"

    def test_supported_ssg_engines(self):
        """Test that Contentful supports the correct SSG engines"""
        provider = ContentfulProvider(space_id="test-space")
        supported_engines = provider.get_supported_ssg_engines()

        expected_engines = ["gatsby", "astro", "nextjs", "nuxt"]
        assert all(engine in supported_engines for engine in expected_engines)
        assert len(supported_engines) == 4

    def test_ssg_compatibility_validation_valid(self):
        """Test SSG compatibility validation for supported engines"""
        provider = ContentfulProvider(space_id="test-space")

        # Test Gatsby compatibility (should be excellent)
        gatsby_compat = provider.validate_ssg_compatibility("gatsby")
        assert gatsby_compat["compatible"] is True
        assert gatsby_compat["compatibility_score"] == 10
        assert "graphql" in gatsby_compat["features"]

        # Test Astro compatibility
        astro_compat = provider.validate_ssg_compatibility("astro")
        assert astro_compat["compatible"] is True
        assert astro_compat["compatibility_score"] == 9
        assert "component_islands" in astro_compat["features"]

    def test_ssg_compatibility_validation_invalid(self):
        """Test SSG compatibility validation for unsupported engines"""
        provider = ContentfulProvider(space_id="test-space")

        # Test Hugo compatibility (should fail)
        hugo_compat = provider.validate_ssg_compatibility("hugo")
        assert hugo_compat["compatible"] is False
        assert "not supported" in hugo_compat["reason"]
        assert "hugo" not in hugo_compat["supported_engines"]

    def test_api_endpoints_generation(self):
        """Test Contentful API endpoints generation"""
        provider = ContentfulProvider(space_id="test-space-123", environment="staging")
        endpoints = provider.get_api_endpoints()

        assert "delivery_api" in endpoints
        assert "preview_api" in endpoints
        assert "graphql_api" in endpoints
        assert "test-space-123" in endpoints["delivery_api"]
        assert "staging" in endpoints["graphql_api"]

    def test_environment_variables_generation(self):
        """Test environment variables generation for different SSG engines"""
        provider = ContentfulProvider(space_id="test-space", environment="master")

        # Test Gatsby environment variables
        gatsby_vars = provider.generate_environment_variables("gatsby")
        assert "CONTENTFUL_SPACE_ID" in gatsby_vars
        assert "CONTENTFUL_ACCESS_TOKEN" in gatsby_vars
        assert gatsby_vars["CONTENTFUL_SPACE_ID"] == "test-space"

        # Test Next.js environment variables
        nextjs_vars = provider.generate_environment_variables("nextjs")
        assert "CONTENTFUL_ACCESS_TOKEN" in nextjs_vars
        assert "CONTENTFUL_PREVIEW_ACCESS_TOKEN" in nextjs_vars

        # Test Nuxt-specific variables
        nuxt_vars = provider.generate_environment_variables("nuxt")
        assert "CTF_SPACE_ID" in nuxt_vars
        assert "CTF_CDA_ACCESS_TOKEN" in nuxt_vars

    def test_build_dependencies_generation(self):
        """Test build dependencies generation for SSG engines"""
        provider = ContentfulProvider(space_id="test-space")

        # Test Gatsby dependencies
        gatsby_deps = provider.get_build_dependencies("gatsby")
        assert "npm_packages" in gatsby_deps
        assert "gatsby-source-contentful" in gatsby_deps["npm_packages"]
        assert "gatsby_plugins" in gatsby_deps

        # Test Astro dependencies
        astro_deps = provider.get_build_dependencies("astro")
        assert "@astrojs/contentful" in astro_deps["npm_packages"]
        assert "astro_integrations" in astro_deps

        # Test Next.js dependencies
        nextjs_deps = provider.get_build_dependencies("nextjs")
        assert "contentful" in nextjs_deps["npm_packages"]
        assert "@contentful/rich-text-react-renderer" in nextjs_deps["npm_packages"]

    def test_build_configuration_generation(self):
        """Test build configuration generation for SSG engines"""
        provider = ContentfulProvider(space_id="test-space", environment="master")

        # Test Gatsby configuration
        gatsby_config = provider.generate_build_configuration("gatsby")
        assert gatsby_config["ssg_engine"] == "gatsby"
        assert gatsby_config["build_command"] == "gatsby build"
        assert gatsby_config["output_dir"] == "public"
        assert "gatsby_config" in gatsby_config

        # Test Astro configuration
        astro_config = provider.generate_build_configuration("astro")
        assert astro_config["build_command"] == "npm run build"
        assert astro_config["output_dir"] == "dist"
        assert "astro_config" in astro_config

    def test_webhook_configuration(self):
        """Test webhook configuration for Contentful"""
        provider = ContentfulProvider(space_id="test-space")
        webhook_config = provider.get_webhook_configuration()

        assert webhook_config["provider"] == "contentful"
        assert "Entry.save" in webhook_config["events"]
        assert "Asset.publish" in webhook_config["events"]
        assert "X-Contentful-Topic" in webhook_config["headers"]

    def test_content_model_examples(self):
        """Test content model examples for different use cases"""
        provider = ContentfulProvider(space_id="test-space")
        models = provider.get_content_model_examples()

        assert "blog_article" in models
        assert "product_page" in models
        assert "landing_page" in models

        # Validate blog article model
        blog_model = models["blog_article"]
        assert blog_model["name"] == "Blog Article"
        assert len(blog_model["fields"]) >= 6  # title, slug, content, etc.

    def test_monthly_cost_estimation(self):
        """Test monthly cost estimation for Contentful"""
        provider = ContentfulProvider(space_id="test-space")

        # Test basic requirements
        basic_requirements = {
            "api_calls_per_month": 50000,
            "bandwidth_gb": 50
        }
        costs = provider.estimate_monthly_cost(basic_requirements)

        assert "contentful_subscription" in costs
        assert "api_usage" in costs
        assert "aws_integration" in costs
        assert "total" in costs
        assert costs["contentful_subscription"] == 300  # Team plan base
        assert costs["total"] > 300  # Should include AWS and other costs

        # Test enterprise requirements
        enterprise_requirements = {
            "api_calls_per_month": 500000,
            "bandwidth_gb": 500
        }
        enterprise_costs = provider.estimate_monthly_cost(enterprise_requirements)
        assert enterprise_costs["total"] > costs["total"]

    def test_business_positioning(self):
        """Test business positioning information"""
        provider = ContentfulProvider(space_id="test-space")
        positioning = provider.get_business_positioning()

        assert positioning["tier"] == "enterprise"
        assert "large_content_teams" in positioning["target_market"]
        assert "Advanced content workflows" in positioning["key_differentiators"][0]
        assert positioning["ideal_client_profile"]["team_size"] == "10+ content creators"

    @pytest.mark.parametrize("requirements,expected_score_range", [
        ({"team_size": 15, "content_workflows": True, "monthly_budget": 400}, (70, 100)),
        ({"team_size": 2, "simple_content": True, "monthly_budget": 100}, (0, 40)),
        ({"enterprise_security": True, "multi_language": True, "monthly_budget": 500}, (80, 100))
    ])
    def test_client_suitability_scoring(self, requirements, expected_score_range):
        """Test client suitability scoring algorithm"""
        result = ContentfulProvider.get_client_suitability_score(requirements)

        assert "suitability_score" in result
        assert "suitability" in result
        assert "reasons" in result

        score = result["suitability_score"]
        assert expected_score_range[0] <= score <= expected_score_range[1]

        # Validate suitability levels
        if score >= 80:
            assert result["suitability"] == "excellent"
        elif score >= 60:
            assert result["suitability"] == "good"
        elif score >= 40:
            assert result["suitability"] == "fair"
        else:
            assert result["suitability"] == "poor"


class TestContentfulContentSettings:
    """Test Contentful content settings configuration"""

    def test_default_settings(self):
        """Test default content settings initialization"""
        settings = ContentfulContentSettings(space_id="test-space")

        assert settings.space_id == "test-space"
        assert settings.environment == ContentfulEnvironment.MASTER
        assert settings.enable_preview is True
        assert settings.enable_webhooks is True
        assert settings.content_locales == ["en-US"]

    def test_enterprise_settings(self):
        """Test enterprise feature settings"""
        settings = ContentfulContentSettings(
            space_id="enterprise-space",
            enable_workflows=True,
            enable_versioning=True,
            max_editors=100
        )

        assert settings.enable_workflows is True
        assert settings.enable_versioning is True
        assert settings.max_editors == 100


class TestContentfulBuildSettings:
    """Test Contentful build settings for different SSG engines"""

    def test_gatsby_build_settings(self):
        """Test build settings for Gatsby"""
        settings = ContentfulBuildSettings(ssg_engine="gatsby")

        assert settings.ssg_engine == "gatsby"
        assert settings.build_command == "gatsby build"
        assert settings.output_directory == "dist"  # Default
        assert "gatsby-source-contentful" in settings.contentful_plugins

    def test_astro_build_settings(self):
        """Test build settings for Astro"""
        settings = ContentfulBuildSettings(ssg_engine="astro")

        assert settings.build_command == "npm run build"
        assert "@astrojs/contentful" in settings.contentful_plugins

    def test_nextjs_build_settings(self):
        """Test build settings for Next.js"""
        settings = ContentfulBuildSettings(ssg_engine="nextjs")

        assert settings.build_command == "npm run build && npm run export"
        assert "contentful" in settings.contentful_plugins

    def test_custom_build_settings(self):
        """Test custom build settings override"""
        custom_settings = ContentfulBuildSettings(
            ssg_engine="gatsby",
            build_command="custom-build-command",
            output_directory="custom-output",
            contentful_plugins=["custom-plugin"]
        )

        assert custom_settings.build_command == "custom-build-command"
        assert custom_settings.output_directory == "custom-output"
        assert custom_settings.contentful_plugins == ["custom-plugin"]


class TestContentfulCMSStack:
    """Test Contentful CMS stack implementation"""

    @pytest.fixture
    def mock_client_config(self):
        """Mock client configuration for testing"""
        return MagicMock(spec=ClientServiceConfig)

    @pytest.fixture
    def mock_scope(self):
        """Mock CDK scope for testing"""
        return MagicMock()

    def test_stack_initialization_gatsby(self, mock_scope, mock_client_config):
        """Test Contentful stack initialization with Gatsby"""
        mock_client_config.resource_prefix = "test-client"
        mock_client_config.domain = "test.com"

        with patch('stacks.cms.contentful_cms_stack.BaseSSGStack.__init__'):
            stack = ContentfulCMSStack(
                scope=mock_scope,
                construct_id="TestContentfulStack",
                client_config=mock_client_config,
                ssg_engine="gatsby",
                contentful_space_id="test-space-123"
            )

            assert stack.ssg_engine == "gatsby"
            assert stack.contentful_space_id == "test-space-123"
            assert stack.contentful_environment == "master"  # Default

    def test_stack_initialization_custom_environment(self, mock_scope, mock_client_config):
        """Test Contentful stack with custom environment"""
        with patch('stacks.cms.contentful_cms_stack.BaseSSGStack.__init__'):
            stack = ContentfulCMSStack(
                scope=mock_scope,
                construct_id="TestContentfulStack",
                client_config=mock_client_config,
                ssg_engine="astro",
                contentful_space_id="test-space",
                contentful_environment="staging",
                enable_preview=False
            )

            assert stack.contentful_environment == "staging"
            assert stack.enable_preview is False

    def test_unsupported_ssg_engine_validation(self, mock_scope, mock_client_config):
        """Test validation of unsupported SSG engines"""
        with patch('stacks.cms.contentful_cms_stack.BaseSSGStack.__init__'):
            with pytest.raises(ValueError) as exc_info:
                ContentfulCMSStack(
                    scope=mock_scope,
                    construct_id="TestContentfulStack",
                    client_config=mock_client_config,
                    ssg_engine="hugo",  # Not supported by Contentful
                    contentful_space_id="test-space"
                )

            assert "not supported by Contentful CMS tier" in str(exc_info.value)
            assert "hugo" in str(exc_info.value)

    def test_supported_ssg_engines_list(self):
        """Test the list of supported SSG engines"""
        supported = ContentfulCMSStack.SUPPORTED_SSG_ENGINES

        assert "gatsby" in supported
        assert "astro" in supported
        assert "nextjs" in supported
        assert "nuxt" in supported

        # Verify compatibility information
        gatsby_info = supported["gatsby"]
        assert gatsby_info["compatibility"] == "excellent"
        assert gatsby_info["setup_complexity"] == "advanced"
        assert "graphql" in gatsby_info["features"]

    def test_monthly_cost_estimation(self):
        """Test monthly cost estimation for Contentful CMS tier"""
        with patch('stacks.cms.contentful_cms_stack.BaseSSGStack.__init__'):
            with patch('stacks.cms.contentful_cms_stack.BaseSSGStack.estimate_monthly_cost') as mock_base_cost:
                mock_base_cost.return_value = {"hosting": 50, "total": 50}

                stack = ContentfulCMSStack(
                    scope=MagicMock(),
                    construct_id="TestStack",
                    client_config=MagicMock(),
                    ssg_engine="gatsby",
                    contentful_space_id="test-space"
                )

                costs = stack.get_monthly_cost_estimate()

                assert "contentful_subscription" in costs
                assert "enterprise_aws_overhead" in costs
                assert "enterprise_features" in costs
                assert "total_cms_cost" in costs
                assert costs["contentful_subscription"] == 300  # Team plan base

    @pytest.mark.parametrize("client_requirements,expected_suitability", [
        ({"team_size": 15, "content_localization": True, "budget_range": "enterprise"}, "excellent"),
        ({"team_size": 3, "budget_range": "small"}, "poor"),
        ({"content_workflows": True, "technical_complexity": "advanced", "budget_range": "medium"}, "good")
    ])
    def test_client_suitability_assessment(self, client_requirements, expected_suitability):
        """Test client suitability assessment for Contentful CMS tier"""
        result = ContentfulCMSStack.get_client_suitability_score(client_requirements)

        assert result["suitability"] == expected_suitability
        assert isinstance(result["suitability_score"], int)
        assert 0 <= result["suitability_score"] <= 100
        assert isinstance(result["reasons"], list)
        assert len(result["reasons"]) > 0


class TestContentfulFactoryIntegration:
    """Test Contentful integration with SSG Stack Factory"""

    def test_contentful_tier_in_stack_registry(self):
        """Test that Contentful CMS tier is registered in factory"""
        assert "contentful_cms_tier" in PlatformStackFactory.STACK_REGISTRY
        assert PlatformStackFactory.STACK_REGISTRY["contentful_cms_tier"] == ContentfulCMSStack

    def test_contentful_tier_information(self):
        """Test Contentful tier information in factory"""
        contentful_info = PlatformStackFactory.STACK_METADATA["contentful_cms_tier"]

        assert contentful_info["tier_name"] == "Contentful CMS - Enterprise Content Management with Advanced Workflows"
        assert contentful_info["monthly_cost_range"] == (75, 500)
        assert contentful_info["setup_cost_range"] == (2100, 4800)
        assert contentful_info["complexity_level"] == "high"
        assert contentful_info["cms_provider"] == "contentful"
        assert "gatsby" in contentful_info["ssg_engine_options"]

    def test_contentful_recommendations_enterprise_team(self):
        """Test Contentful recommendations for enterprise teams"""
        requirements = {
            "content_management": True,
            "enterprise_cms": True,
            "team_collaboration": True,
            "content_workflows": True,
            "large_content_team": True,
            "multi_language": True
        }

        recommendations = PlatformStackFactory.get_recommendations(requirements)

        # Should recommend Contentful CMS tier
        contentful_recs = [r for r in recommendations if r["stack_type"] == "contentful_cms_tier"]
        assert len(contentful_recs) > 0

        contentful_rec = contentful_recs[0]
        assert contentful_rec["cms_provider"] == "contentful"
        assert contentful_rec["complexity"] == "High"
        assert "enterprise" in contentful_rec["reason"].lower()
        assert contentful_rec["recommended_ssg"] in ["gatsby", "astro", "nextjs", "nuxt"]

    def test_contentful_ssg_engine_selection(self):
        """Test SSG engine selection logic for Contentful"""
        # Test React preference -> Next.js
        react_requirements = {
            "content_management": True,
            "enterprise_cms": True,
            "react_preferred": True
        }
        recommendations = PlatformStackFactory.get_recommendations(react_requirements)
        contentful_rec = next(r for r in recommendations if r["stack_type"] == "contentful_cms_tier")
        assert contentful_rec["ssg_engine"] == "nextjs"

        # Test Vue preference -> Nuxt
        vue_requirements = {
            "content_management": True,
            "enterprise_cms": True,
            "vue_preferred": True
        }
        recommendations = PlatformStackFactory.get_recommendations(vue_requirements)
        contentful_rec = next(r for r in recommendations if r["stack_type"] == "contentful_cms_tier")
        assert contentful_rec["ssg_engine"] == "nuxt"

        # Test modern features without React -> Astro
        modern_requirements = {
            "content_management": True,
            "enterprise_cms": True,
            "modern_features": True
        }
        recommendations = PlatformStackFactory.get_recommendations(modern_requirements)
        contentful_rec = next(r for r in recommendations if r["stack_type"] == "contentful_cms_tier")
        assert contentful_rec["ssg_engine"] == "astro"

    def test_contentful_not_recommended_for_budget_conscious(self):
        """Test that Contentful is not recommended for budget-conscious clients"""
        budget_requirements = {
            "content_management": True,
            "budget_conscious": True,
            "simple_content": True
        }

        recommendations = PlatformStackFactory.get_recommendations(budget_requirements)

        # Should recommend cheaper alternatives first
        if len(recommendations) > 1:
            first_rec = recommendations[0]
            # First recommendation should be Decap (free) for budget-conscious
            assert first_rec["stack_type"] == "decap_cms_tier"
            assert first_rec["cms_cost"] == "$0/month"


class TestContentfulEnterpriseFeatures:
    """Test enterprise-specific features of Contentful implementation"""

    def test_enterprise_features_list(self):
        """Test enterprise features available in Contentful"""
        provider = ContentfulProvider(space_id="test-space")
        features = provider.enterprise_features

        expected_features = [
            "content_workflows", "team_collaboration", "multi_language_support",
            "content_versioning", "scheduled_publishing", "advanced_permissions"
        ]

        for feature in expected_features:
            assert feature in features

    def test_multi_environment_support(self):
        """Test multi-environment content management"""
        # Test different environment configurations
        environments = ["master", "development", "staging"]

        for env in environments:
            provider = ContentfulProvider(space_id="test-space", environment=env)
            endpoints = provider.get_api_endpoints()
            assert env in endpoints["graphql_api"]

    def test_enterprise_cost_scaling(self):
        """Test enterprise cost scaling based on usage"""
        provider = ContentfulProvider(space_id="test-space")

        # Test scaling with high API usage
        high_usage = {
            "api_calls_per_month": 1000000,  # 1M API calls
            "bandwidth_gb": 1000  # 1TB bandwidth
        }

        high_costs = provider.estimate_monthly_cost(high_usage)

        # Should scale significantly with usage
        assert high_costs["api_usage"] > 50  # Significant API costs over free tier
        assert high_costs["bandwidth"] > 50   # Significant bandwidth costs
        assert high_costs["total"] > 500      # Should be enterprise-level pricing

    def test_security_and_compliance_features(self):
        """Test enterprise security and compliance features"""
        positioning = ContentfulProvider.get_business_positioning("", {})

        enterprise_benefits = positioning["enterprise_benefits"]
        security_features = [benefit for benefit in enterprise_benefits if "security" in benefit.lower()]

        assert len(security_features) > 0
        assert any("compliance" in benefit.lower() for benefit in enterprise_benefits)
        assert any("sla" in benefit.lower() for benefit in enterprise_benefits)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])