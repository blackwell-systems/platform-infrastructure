"""
Test Suite for Shopify Basic E-commerce Tier Implementation

This comprehensive test suite validates the Shopify Basic tier implementation,
provider functionality, factory integration, and business requirements.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os

# Shopify Basic components
from stacks.ecommerce.shopify_basic_ecommerce_stack import ShopifyBasicEcommerceStack
from shared.providers.ecommerce.shopify_basic_provider import (
    ShopifyBasicProvider,
    ShopifyBasicSettings,
    ShopifyBuildSettings,
    ShopifyPlan,
    ShopifyAPIAccess
)
from shared.factories.platform_stack_factory import PlatformStackFactory
from models.component_enums import SSGEngine
from models.service_config import ClientServiceConfig


@pytest.mark.skip(reason="Provider classes removed during pricing extraction - preserve for future capability-focused implementation")
class TestShopifyBasicProvider:
    """Test Shopify Basic e-commerce provider functionality"""

    def test_provider_initialization(self):
        """Test Shopify Basic provider initialization with basic parameters"""
        provider = ShopifyBasicProvider(
            store_domain="test-store.myshopify.com",
            shopify_plan="basic",
            ssg_engine=SSGEngine.ASTRO
        )

        assert provider.store_domain == "test-store.myshopify.com"
        assert provider.shopify_plan == ShopifyPlan.BASIC
        assert provider.ssg_engine == SSGEngine.ASTRO
        assert provider.provider_name == "shopify_basic"
        assert provider.provider_type == "hosted_platform"

    def test_supported_ssg_engines(self):
        """Test that Shopify Basic supports the correct SSG engines"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")
        supported_engines = provider.get_supported_ssg_engines()

        expected_engines = [SSGEngine.ELEVENTY, SSGEngine.ASTRO, SSGEngine.NEXTJS, SSGEngine.NUXT]
        assert all(engine in supported_engines for engine in expected_engines)
        assert len(supported_engines) == 4

    def test_ssg_compatibility_validation_valid(self):
        """Test SSG compatibility validation for supported engines"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")

        # Test Astro compatibility (should be perfect)
        astro_compat = provider.validate_ssg_compatibility(SSGEngine.ASTRO)
        assert astro_compat["compatible"] is True
        assert astro_compat["compatibility_score"] == 10
        assert "component_islands" in astro_compat["features"]

        # Test Eleventy compatibility
        eleventy_compat = provider.validate_ssg_compatibility(SSGEngine.ELEVENTY)
        assert eleventy_compat["compatible"] is True
        assert eleventy_compat["compatibility_score"] == 9
        assert "fast_builds" in eleventy_compat["features"]

    def test_ssg_compatibility_validation_invalid(self):
        """Test SSG compatibility validation for unsupported engines"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")

        # Test Hugo compatibility (should fail)
        hugo_compat = provider.validate_ssg_compatibility(SSGEngine.HUGO)
        assert hugo_compat["compatible"] is False
        assert "not supported" in hugo_compat["reason"]
        assert "hugo" not in [engine for engine in hugo_compat["supported_engines"]]

    def test_api_endpoints_generation(self):
        """Test Shopify API endpoints generation"""
        provider = ShopifyBasicProvider(store_domain="my-store.myshopify.com")
        endpoints = provider.get_api_endpoints()

        assert "storefront_api" in endpoints
        assert "admin_api" in endpoints
        assert "checkout_url" in endpoints
        assert "my-store" in endpoints["storefront_api"]
        assert "2023-10" in endpoints["storefront_api"]  # API version

    def test_environment_variables_generation(self):
        """Test environment variables generation for different SSG engines"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")

        # Test Eleventy environment variables
        eleventy_vars = provider.generate_environment_variables(SSGEngine.ELEVENTY)
        assert "SHOPIFY_STORE_DOMAIN" in eleventy_vars
        assert "SHOPIFY_STOREFRONT_ACCESS_TOKEN" in eleventy_vars
        assert eleventy_vars["SHOPIFY_STORE_DOMAIN"] == "test-store.myshopify.com"

        # Test Astro environment variables
        astro_vars = provider.generate_environment_variables(SSGEngine.ASTRO)
        assert "PUBLIC_SHOPIFY_STORE_DOMAIN" in astro_vars
        assert "PUBLIC_SHOPIFY_STOREFRONT_TOKEN" in astro_vars

        # Test Next.js environment variables
        nextjs_vars = provider.generate_environment_variables(SSGEngine.NEXTJS)
        assert "NEXT_PUBLIC_SHOPIFY_STORE_DOMAIN" in nextjs_vars
        assert "SHOPIFY_ADMIN_ACCESS_TOKEN" in nextjs_vars

        # Test Nuxt environment variables
        nuxt_vars = provider.generate_environment_variables(SSGEngine.NUXT)
        assert "NUXT_PUBLIC_SHOPIFY_STORE_DOMAIN" in nuxt_vars
        assert "NUXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN" in nuxt_vars

    def test_build_dependencies_generation(self):
        """Test build dependencies generation for SSG engines"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")

        # Test Eleventy dependencies
        eleventy_deps = provider.get_build_dependencies(SSGEngine.ELEVENTY)
        assert "npm_packages" in eleventy_deps
        assert "@shopify/storefront-api-client" in eleventy_deps["npm_packages"]
        assert "graphql" in eleventy_deps["npm_packages"]

        # Test Astro dependencies
        astro_deps = provider.get_build_dependencies(SSGEngine.ASTRO)
        assert "@shopify/storefront-api-client" in astro_deps["npm_packages"]
        assert "@astrojs/node" in astro_deps["npm_packages"]

        # Test Next.js dependencies
        nextjs_deps = provider.get_build_dependencies(SSGEngine.NEXTJS)
        assert "@shopify/react-hooks" in nextjs_deps["npm_packages"]
        assert "react" in nextjs_deps["npm_packages"]

        # Test Nuxt dependencies
        nuxt_deps = provider.get_build_dependencies(SSGEngine.NUXT)
        assert "@nuxtjs/axios" in nuxt_deps["npm_packages"]

    def test_build_configuration_generation(self):
        """Test build configuration generation for SSG engines"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")

        # Test Eleventy configuration
        eleventy_config = provider.generate_build_configuration(SSGEngine.ELEVENTY)
        assert eleventy_config["ssg_engine"] == "eleventy"
        assert eleventy_config["build_command"] == "npx @11ty/eleventy"
        assert eleventy_config["output_dir"] == "dist"

        # Test Astro configuration
        astro_config = provider.generate_build_configuration(SSGEngine.ASTRO)
        assert astro_config["build_command"] == "npm run build"
        assert "astro_config" in astro_config

        # Test Next.js configuration
        nextjs_config = provider.generate_build_configuration(SSGEngine.NEXTJS)
        assert nextjs_config["build_command"] == "npm run build && npm run export"
        assert nextjs_config["output_dir"] == "out"

    def test_webhook_configuration(self):
        """Test webhook configuration for Shopify"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")
        webhook_config = provider.get_webhook_configuration()

        assert webhook_config["provider"] == "shopify_basic"
        assert "products/create" in webhook_config["events"]
        assert "inventory_levels/update" in webhook_config["events"]
        assert "id" in webhook_config["fields"]
        assert "variants" in webhook_config["fields"]

    def test_storefront_queries(self):
        """Test GraphQL queries for Shopify Storefront API"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")
        queries = provider.get_storefront_queries()

        assert "get_products" in queries
        assert "get_product_by_handle" in queries
        assert "get_collections" in queries

        # Validate query structure
        products_query = queries["get_products"]
        assert "products(first: $first)" in products_query
        assert "variants" in products_query
        assert "images" in products_query

    @pytest.mark.legacy_pricing
    def test_monthly_cost_estimation(self):
        """Test monthly cost estimation for Shopify Basic"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")

        # Test basic requirements
        basic_requirements = {
            "traffic_level": "medium",
            "monthly_sales": 5000
        }
        costs = provider.estimate_monthly_cost(basic_requirements)

        assert "shopify_basic_plan" in costs
        assert "aws_infrastructure" in costs
        assert "estimated_transaction_fees" in costs
        assert "total" in costs
        assert costs["shopify_basic_plan"] == 29  # Fixed Shopify Basic cost
        assert costs["total"] > 29  # Should include AWS and other costs

        # Test high traffic requirements
        high_traffic_requirements = {
            "traffic_level": "high",
            "monthly_sales": 20000
        }
        high_costs = provider.estimate_monthly_cost(high_traffic_requirements)
        assert high_costs["total"] > costs["total"]

    @pytest.mark.legacy_pricing
    def test_business_positioning(self):
        """Test business positioning information"""
        provider = ShopifyBasicProvider(store_domain="test-store.myshopify.com")
        positioning = provider.get_business_positioning()

        assert positioning["tier"] == "basic_ecommerce"
        assert "small_medium_stores" in positioning["target_market"]
        assert "Enterprise performance at small business prices" in positioning["key_differentiators"][0]
        assert positioning["ideal_client_profile"]["monthly_sales"] == "$2,000-25,000 per month"



class TestShopifyBasicSettings:
    """Test Shopify Basic settings configuration"""

    def test_default_settings(self):
        """Test default Shopify Basic settings initialization"""
        settings = ShopifyBasicSettings(store_domain="test-store.myshopify.com")

        assert settings.store_domain == "test-store.myshopify.com"
        assert settings.shopify_plan == ShopifyPlan.BASIC
        assert settings.enable_storefront_api is True
        assert settings.enable_webhooks is True
        assert settings.sync_inventory is True

    def test_advanced_settings(self):
        """Test advanced feature settings"""
        settings = ShopifyBasicSettings(
            store_domain="advanced-store.myshopify.com",
            enable_product_caching=True,
            cache_duration_hours=48,
            sync_product_variants=True
        )

        assert settings.enable_product_caching is True
        assert settings.cache_duration_hours == 48
        assert settings.sync_product_variants is True


class TestShopifyBuildSettings:
    """Test Shopify build settings for different SSG engines"""

    def test_eleventy_build_settings(self):
        """Test build settings for Eleventy"""
        settings = ShopifyBuildSettings(ssg_engine=SSGEngine.ELEVENTY)

        assert settings.ssg_engine == SSGEngine.ELEVENTY
        assert settings.build_command == "npx @11ty/eleventy"
        assert settings.output_directory == "dist"  # Default
        assert "@shopify/storefront-api-client" in settings.shopify_packages

    def test_astro_build_settings(self):
        """Test build settings for Astro"""
        settings = ShopifyBuildSettings(ssg_engine=SSGEngine.ASTRO)

        assert settings.build_command == "npm run build"
        assert "@shopify/storefront-api-client" in settings.shopify_packages
        assert "@astrojs/node" in settings.shopify_packages

    def test_nextjs_build_settings(self):
        """Test build settings for Next.js"""
        settings = ShopifyBuildSettings(ssg_engine=SSGEngine.NEXTJS)

        assert settings.build_command == "npm run build && npm run export"
        assert "@shopify/react-hooks" in settings.shopify_packages

    def test_custom_build_settings(self):
        """Test custom build settings override"""
        custom_settings = ShopifyBuildSettings(
            ssg_engine=SSGEngine.ASTRO,
            build_command="custom-build-command",
            output_directory="custom-output",
            shopify_packages=["custom-package"]
        )

        assert custom_settings.build_command == "custom-build-command"
        assert custom_settings.output_directory == "custom-output"
        assert custom_settings.shopify_packages == ["custom-package"]


@pytest.mark.skip(reason="Stack implementation classes removed during pricing extraction - preserve for future capability-focused implementation")
class TestShopifyBasicEcommerceStack:
    """Test Shopify Basic e-commerce stack implementation"""

    @pytest.fixture
    def mock_client_config(self):
        """Mock client configuration for testing"""
        return MagicMock(spec=ClientServiceConfig)

    @pytest.fixture
    def mock_scope(self):
        """Mock CDK scope for testing"""
        return MagicMock()

    def test_stack_initialization_astro(self, mock_scope, mock_client_config):
        """Test Shopify Basic stack initialization with Astro"""
        mock_client_config.resource_prefix = "test-client"
        mock_client_config.domain = "test.com"

        with patch('stacks.ecommerce.shopify_basic_ecommerce_stack.BaseSSGStack.__init__'):
            stack = ShopifyBasicEcommerceStack(
                scope=mock_scope,
                construct_id="TestShopifyBasicStack",
                client_config=mock_client_config,
                ssg_engine="astro",
                shopify_store_domain="test-store.myshopify.com"
            )

            assert stack.ssg_engine == "astro"
            assert stack.shopify_store_domain == "test-store.myshopify.com"
            assert stack.shopify_plan == "basic"  # Default

    def test_stack_initialization_custom_plan(self, mock_scope, mock_client_config):
        """Test Shopify Basic stack with custom Shopify plan"""
        with patch('stacks.ecommerce.shopify_basic_ecommerce_stack.BaseSSGStack.__init__'):
            stack = ShopifyBasicEcommerceStack(
                scope=mock_scope,
                construct_id="TestShopifyBasicStack",
                client_config=mock_client_config,
                ssg_engine="eleventy",
                shopify_store_domain="premium-store.myshopify.com",
                shopify_plan="shopify",
                enable_webhooks=False
            )

            assert stack.shopify_plan == "shopify"
            assert stack.enable_webhooks is False

    def test_unsupported_ssg_engine_validation(self, mock_scope, mock_client_config):
        """Test validation of unsupported SSG engines"""
        with patch('stacks.ecommerce.shopify_basic_ecommerce_stack.BaseSSGStack.__init__'):
            with pytest.raises(ValueError) as exc_info:
                ShopifyBasicEcommerceStack(
                    scope=mock_scope,
                    construct_id="TestShopifyBasicStack",
                    client_config=mock_client_config,
                    ssg_engine="hugo",  # Not supported by Shopify Basic
                    shopify_store_domain="test-store.myshopify.com"
                )

            assert "not supported by Shopify Basic tier" in str(exc_info.value)
            assert "hugo" in str(exc_info.value)

    def test_supported_ssg_engines_list(self):
        """Test the list of supported SSG engines"""
        supported = ShopifyBasicEcommerceStack.SUPPORTED_SSG_ENGINES

        assert "eleventy" in supported
        assert "astro" in supported
        assert "nextjs" in supported
        assert "nuxt" in supported

        # Verify compatibility information
        astro_info = supported["astro"]
        assert astro_info["compatibility"] == "perfect"
        assert astro_info["setup_complexity"] == "intermediate"
        assert "component_islands" in astro_info["features"]

    @pytest.mark.legacy_pricing
    def test_monthly_cost_estimation(self):
        """Test monthly cost estimation for Shopify Basic tier"""
        with patch('stacks.ecommerce.shopify_basic_ecommerce_stack.BaseSSGStack.__init__'):
            with patch('stacks.ecommerce.shopify_basic_ecommerce_stack.BaseSSGStack.estimate_monthly_cost') as mock_base_cost:
                mock_base_cost.return_value = {"hosting": 20, "total": 20}

                stack = ShopifyBasicEcommerceStack(
                    scope=MagicMock(),
                    construct_id="TestStack",
                    client_config=MagicMock(),
                    ssg_engine="astro",
                    shopify_store_domain="test-store.myshopify.com"
                )

                costs = stack.get_monthly_cost_estimate()

                assert "shopify_basic_plan" in costs
                assert "ecommerce_aws_overhead" in costs
                assert "integration_maintenance" in costs
                assert "total_ecommerce_cost" in costs
                assert costs["shopify_basic_plan"] == 29  # Shopify Basic plan

    @pytest.mark.capability_focused
    @pytest.mark.parametrize("client_requirements,expected_suitability", [
        ({"ecommerce_needed": True, "performance_critical": True, "technical_comfort": "intermediate"}, "excellent"),
        ({"enterprise_features": True, "business_size": "large_enterprise", "advanced_requirements": True}, "poor"),
        ({"agency_alternative": True, "product_catalog": True, "performance_optimization": True}, "excellent")
    ])
    def test_client_capability_alignment_assessment(self, client_requirements, expected_suitability):
        """Test client capability alignment assessment for Shopify Basic tier - validates stack suitability based on client capabilities"""
        result = ShopifyBasicEcommerceStack.get_client_capability_alignment_score(client_requirements)

        assert result["capability_alignment"] == expected_suitability
        assert isinstance(result["alignment_score"], int)
        assert 0 <= result["alignment_score"] <= 100
        assert isinstance(result["capability_reasons"], list)
        assert len(result["capability_reasons"]) > 0


class TestShopifyBasicFactoryIntegration:
    """Test Shopify Basic integration with E-commerce Stack Factory"""

    def test_shopify_basic_in_stack_registry(self):
        """Test that Shopify Basic is registered in factory"""
        assert "shopify_basic_ecommerce" in PlatformStackFactory.STACK_REGISTRY
        assert PlatformStackFactory.STACK_REGISTRY["shopify_basic_ecommerce"] == ShopifyBasicEcommerceStack

    @pytest.mark.legacy_pricing
    def test_shopify_basic_tier_information(self):
        """Test Shopify Basic tier information in factory"""
        shopify_info = PlatformStackFactory.STACK_METADATA["shopify_basic_ecommerce"]

        assert shopify_info["tier_name"] == "Shopify Basic - Performance E-commerce with Flexible SSG"
        assert shopify_info["monthly_cost_range"] == (75, 125)
        assert shopify_info["setup_cost_range"] == (1600, 3200)
        assert shopify_info["complexity_level"] == "medium"
        assert shopify_info["ecommerce_provider"] == "shopify_basic"
        assert "astro" in shopify_info["ssg_engine_options"]

    @pytest.mark.capability_focused
    @pytest.mark.skip(reason="Metadata fields removed during pricing extraction - preserve for future capability-focused implementation")
    def test_shopify_basic_tier_capability_metadata(self):
        """Test Shopify Basic tier capability metadata in factory - validates technical capabilities without pricing"""
        shopify_info = PlatformStackFactory.STACK_METADATA["shopify_basic_ecommerce"]

        # Validate capability-focused metadata fields
        assert shopify_info["tier_name"] == "Shopify Basic - Performance E-commerce with Flexible SSG"
        assert shopify_info["complexity_level"] == "medium"
        assert shopify_info["ecommerce_provider"] == "shopify_basic"
        assert shopify_info["provider_type"] == "platform_based"

        # Validate supported SSG engine options
        expected_engines = ["astro", "nextjs", "nuxt", "eleventy"]
        for engine in expected_engines:
            assert engine in shopify_info["ssg_engine_options"]

        # Validate target market and capabilities (TODO: implement in capability-focused architecture)
        assert "performance_ecommerce" in shopify_info.get("target_market", [])
        assert "flexible_ssg_integration" in shopify_info.get("key_capabilities", [])

    def test_shopify_basic_recommendations_agency_alternative(self):
        """Test Shopify Basic recommendations for agency alternatives"""
        requirements = {
            "agency_alternative": True,
            "performance_ecommerce": True,
            "product_catalog": True,
            "performance_critical": True
        }

        recommendations = PlatformStackFactory.get_recommendations(requirements)

        # Should recommend Shopify Basic
        shopify_recs = [r for r in recommendations if r["ecommerce_provider"] == "shopify_basic"]
        assert len(shopify_recs) > 0

        shopify_rec = shopify_recs[0]
        assert shopify_rec["monthly_cost"] == "$75-125"
        assert shopify_rec["complexity"] == "Medium"
        assert "80-90% cost reduction" in shopify_rec["reason"]
        assert shopify_rec["recommended_ssg"] in ["eleventy", "astro", "nextjs", "nuxt"]

    def test_shopify_basic_ssg_engine_selection(self):
        """Test SSG engine selection logic for Shopify Basic"""
        # Test React preference -> Next.js
        react_requirements = {
            "agency_alternative": True,
            "prefer_react": True
        }
        recommendations = PlatformStackFactory.get_recommendations(react_requirements)
        shopify_rec = next(r for r in recommendations if r["ecommerce_provider"] == "shopify_basic")
        assert shopify_rec["recommended_ssg"] == "nextjs"

        # Test Vue preference -> Nuxt
        vue_requirements = {
            "shopify_theme_upgrade": True,
            "prefer_vue": True
        }
        recommendations = PlatformStackFactory.get_recommendations(vue_requirements)
        shopify_rec = next(r for r in recommendations if r["ecommerce_provider"] == "shopify_basic")
        assert shopify_rec["recommended_ssg"] == "nuxt"

        # Test performance + technical -> Astro
        performance_requirements = {
            "performance_ecommerce": True,
            "performance_critical": True,
            "technical_team": True
        }
        recommendations = PlatformStackFactory.get_recommendations(performance_requirements)
        shopify_rec = next(r for r in recommendations if r["ecommerce_provider"] == "shopify_basic")
        assert shopify_rec["recommended_ssg"] == "astro"

    def test_shopify_basic_not_recommended_for_enterprise(self):
        """Test that Shopify Basic is not recommended for enterprise clients"""
        enterprise_requirements = {
            "enterprise_ecommerce": True,
            "shopify_plus": True,
            "monthly_budget": 500
        }

        recommendations = PlatformStackFactory.get_recommendations(enterprise_requirements)

        # Should recommend Shopify Advanced for enterprise
        shopify_recs = [r for r in recommendations if r["ecommerce_provider"].startswith("shopify")]
        if shopify_recs:
            # Should be shopify_advanced, not shopify_basic
            assert shopify_recs[0]["ecommerce_provider"] == "shopify_advanced"

    @pytest.mark.legacy_pricing
    def test_cost_estimation_accuracy(self):
        """Test cost estimation accuracy for Shopify Basic"""
        cost_info = PlatformStackFactory.estimate_total_cost(
            stack_type="shopify_basic_ecommerce",
            ssg_engine="astro",
            client_requirements={"monthly_sales": 10000}
        )

        assert cost_info["setup_cost_range"][0] >= 1600  # Min setup cost
        assert cost_info["setup_cost_range"][1] <= 3840  # Max with multiplier (3200 * 1.2)
        assert cost_info["monthly_cost_range"] == (75, 125)
        assert cost_info["ssg_complexity_multiplier"] == 1.2  # Astro multiplier


class TestShopifyBasicPerformanceFeatures:
    """Test performance-specific features of Shopify Basic implementation"""

    def test_performance_benefits(self):
        """Test performance benefits over traditional Shopify themes"""
        provider = ShopifyBasicProvider(store_domain="performance-store.myshopify.com")
        positioning = provider.get_business_positioning()

        performance_advantages = [adv for adv in positioning["competitive_advantages"] if "faster" in adv.lower()]
        assert len(performance_advantages) > 0
        assert any("2-3x faster" in advantage for advantage in performance_advantages)

    def test_caching_configuration(self):
        """Test caching configuration for performance optimization"""
        settings = ShopifyBasicSettings(
            store_domain="cache-store.myshopify.com",
            enable_product_caching=True,
            cache_duration_hours=24
        )

        assert settings.enable_product_caching is True
        assert settings.cache_duration_hours == 24

    def test_webhook_optimization(self):
        """Test webhook configuration for real-time updates"""
        provider = ShopifyBasicProvider(store_domain="realtime-store.myshopify.com")
        webhook_config = provider.get_webhook_configuration()

        # Should include inventory updates for real-time sync
        assert "inventory_levels/update" in webhook_config["events"]
        assert "products/update" in webhook_config["events"]
        assert webhook_config["format"] == "json"

    def test_build_performance_optimization(self):
        """Test build performance optimization for different SSG engines"""
        provider = ShopifyBasicProvider(store_domain="build-optimized.myshopify.com")

        # Test Eleventy (fastest builds)
        eleventy_config = provider.generate_build_configuration(SSGEngine.ELEVENTY)
        assert eleventy_config["build_command"] == "npx @11ty/eleventy"  # Simple, fast command

        # Test Astro (performance-optimized)
        astro_config = provider.generate_build_configuration(SSGEngine.ASTRO)
        assert "vite" in astro_config["astro_config"]  # Includes Vite optimizations




if __name__ == "__main__":
    pytest.main([__file__, "-v"])