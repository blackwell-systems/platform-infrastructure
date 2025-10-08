"""
Test E-commerce Provider Flexibility Architecture

This test suite validates the architectural transformation from hardcoded
e-commerce/SSG pairings to flexible client choice within provider tiers.

TESTS VALIDATE:
- Client choice of SSG engine within e-commerce provider tiers
- Provider/SSG compatibility validation
- Factory pattern for flexible stack creation
- Cost estimation with SSG complexity multipliers
- Recommendation engine for optimal combinations

BUSINESS IMPACT VALIDATION:
- Same monthly pricing serves multiple technical comfort levels
- Client choice eliminates arbitrary technology constraints
- Revenue optimization through appropriate complexity alignment
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch

from stacks.shared.ecommerce_stack_factory import EcommerceStackFactory
from stacks.ecommerce.snipcart_ecommerce_stack import SnipcartEcommerceStack
from stacks.ecommerce.foxy_ecommerce_stack import FoxyEcommerceStack


class TestEcommerceProviderFlexibility:
    """Test e-commerce provider flexibility architecture"""

    def test_snipcart_supports_multiple_ssg_engines(self):
        """Test that Snipcart tier supports client choice of SSG engine"""
        scope = Mock()

        # Test each compatible SSG engine with Snipcart
        compatible_engines = ["hugo", "eleventy", "astro", "gatsby"]

        for ssg_engine in compatible_engines:
            with patch('stacks.ecommerce.snipcart_ecommerce_stack.BaseSSGStack.__init__'):
                stack = SnipcartEcommerceStack(
                    scope=scope,
                    construct_id=f"Test-Snipcart-{ssg_engine.title()}",
                    client_id="test-client",
                    domain="test.com",
                    ssg_engine=ssg_engine  # CLIENT CHOICE - not hardcoded!
                )

                # Validate that client choice is preserved
                assert stack.ssg_config.ssg_engine == ssg_engine
                assert stack.ecommerce_provider == "snipcart"

                # Validate SSG-specific configuration is applied
                ssg_config = stack._get_ssg_specific_snipcart_config()
                assert ssg_config  # Should have SSG-specific configuration

    def test_foxy_supports_multiple_ssg_engines(self):
        """Test that Foxy tier supports client choice of SSG engine"""
        scope = Mock()

        # Test each compatible SSG engine with Foxy
        compatible_engines = ["hugo", "eleventy", "astro", "gatsby"]

        for ssg_engine in compatible_engines:
            with patch('stacks.ecommerce.foxy_ecommerce_stack.BaseSSGStack.__init__'):
                stack = FoxyEcommerceStack(
                    scope=scope,
                    construct_id=f"Test-Foxy-{ssg_engine.title()}",
                    client_id="test-client",
                    domain="test.com",
                    ssg_engine=ssg_engine  # CLIENT CHOICE - not hardcoded!
                )

                # Validate that client choice is preserved
                assert stack.ssg_config.ssg_engine == ssg_engine
                assert stack.ecommerce_provider == "foxy"

                # Validate advanced features configuration
                advanced_features = stack.get_foxy_advanced_features()
                assert len(advanced_features) > 0
                assert any("Subscription" in feature["name"] for feature in advanced_features)

    def test_incompatible_combinations_rejected(self):
        """Test that incompatible provider/SSG combinations are rejected"""
        scope = Mock()

        # Test incompatible combinations
        incompatible_tests = [
            ("snipcart", "nextjs"),  # Next.js not compatible with Snipcart
            ("snipcart", "nuxt"),    # Nuxt not compatible with Snipcart
            ("foxy", "nextjs"),      # Next.js not compatible with Foxy
            ("foxy", "nuxt"),        # Nuxt not compatible with Foxy
        ]

        for provider, ssg_engine in incompatible_tests:
            with pytest.raises(ValueError, match="not compatible"):
                if provider == "snipcart":
                    SnipcartEcommerceStack(
                        scope=scope,
                        construct_id="Test-Invalid",
                        client_id="test-client",
                        domain="test.com",
                        ssg_engine=ssg_engine
                    )
                elif provider == "foxy":
                    FoxyEcommerceStack(
                        scope=scope,
                        construct_id="Test-Invalid",
                        client_id="test-client",
                        domain="test.com",
                        ssg_engine=ssg_engine
                    )

    def test_factory_creates_correct_combinations(self):
        """Test that factory creates correct provider/SSG combinations"""
        scope = Mock()

        # Test valid combinations through factory
        valid_combinations = [
            ("snipcart", "hugo"),
            ("snipcart", "eleventy"),
            ("snipcart", "astro"),
            ("snipcart", "gatsby"),
            ("foxy", "hugo"),
            ("foxy", "eleventy"),
            ("foxy", "astro"),
            ("foxy", "gatsby"),
        ]

        for provider, ssg_engine in valid_combinations:
            with patch('stacks.shared.base_ssg_stack.BaseSSGStack.__init__'):
                stack = EcommerceStackFactory.create_ecommerce_stack(
                    scope=scope,
                    client_id="test-client",
                    domain="test.com",
                    ecommerce_provider=provider,
                    ssg_engine=ssg_engine
                )

                # Validate correct stack type created
                if provider == "snipcart":
                    assert isinstance(stack, SnipcartEcommerceStack)
                elif provider == "foxy":
                    assert isinstance(stack, FoxyEcommerceStack)

                # Validate configuration
                assert stack.ssg_config.ssg_engine == ssg_engine
                assert stack.ecommerce_provider == provider

    def test_cost_estimation_with_ssg_complexity(self):
        """Test that cost estimation varies by SSG engine complexity"""

        # Test cost estimation for different SSG engines with same provider
        test_cases = [
            ("snipcart", "hugo", 0.8),      # Fastest setup
            ("snipcart", "eleventy", 1.0),  # Baseline
            ("snipcart", "astro", 1.2),     # Modern features
            ("snipcart", "gatsby", 1.4),    # Complex GraphQL
        ]

        for provider, ssg_engine, expected_multiplier in test_cases:
            cost_estimate = EcommerceStackFactory.estimate_total_cost(
                ecommerce_provider=provider,
                ssg_engine=ssg_engine
            )

            # Validate multiplier is applied
            assert cost_estimate["ssg_complexity_multiplier"] == expected_multiplier

            # Validate cost ranges are realistic
            assert cost_estimate["setup_cost_range"][0] > 0
            assert cost_estimate["setup_cost_range"][1] > cost_estimate["setup_cost_range"][0]

            # Hugo should be cheapest, Gatsby most expensive
            if ssg_engine == "hugo":
                base_cost = 960  # Base Snipcart setup cost
                expected_min = int(base_cost * expected_multiplier)
                assert cost_estimate["setup_cost_range"][0] == expected_min

    def test_recommendation_engine_for_client_choice(self):
        """Test recommendation engine provides optimal combinations"""

        # Test budget-conscious recommendations
        budget_requirements = {
            "budget_conscious": True,
            "technical_team": True
        }

        recommendations = EcommerceStackFactory.get_ecommerce_recommendations(budget_requirements)

        # Should recommend Snipcart with technical SSG options
        budget_rec = next((r for r in recommendations if r["ecommerce_provider"] == "snipcart"), None)
        assert budget_rec is not None
        assert "hugo" in budget_rec["ssg_options"]  # Technical team should get Hugo option
        assert budget_rec["recommended_ssg"] == "hugo"

        # Test advanced features recommendations
        advanced_requirements = {
            "advanced_ecommerce": True,
            "subscriptions": True,
            "prefer_react": True
        }

        recommendations = EcommerceStackFactory.get_ecommerce_recommendations(advanced_requirements)

        # Should recommend Foxy with React-friendly SSG options
        advanced_rec = next((r for r in recommendations if r["ecommerce_provider"] == "foxy"), None)
        assert advanced_rec is not None
        assert "gatsby" in advanced_rec["ssg_options"]  # React preference should get Gatsby
        assert advanced_rec["recommended_ssg"] == "gatsby"

    def test_client_decision_framework(self):
        """Test that client decision framework guides optimal choices"""

        framework = EcommerceStackFactory.get_client_decision_framework()

        # Validate framework structure
        assert "step_1_choose_provider_tier" in framework
        assert "step_2_choose_ssg_engine" in framework
        assert "step_3_validate_choice" in framework

        # Validate step 1 has provider tier guidance
        step1 = framework["step_1_choose_provider_tier"]
        assert "budget_conscious" in step1["decision_points"]
        assert "advanced_features" in step1["decision_points"]

        # Validate step 2 has SSG engine guidance
        step2 = framework["step_2_choose_ssg_engine"]
        assert "technical_team" in step2["decision_points"]
        assert "modern_features" in step2["decision_points"]

    def test_template_variant_resolution(self):
        """Test that template variants are resolved for SSG/provider combinations"""
        scope = Mock()

        # Test template variant resolution for different combinations
        test_combinations = [
            ("snipcart", "hugo", "snipcart_ecommerce_performance"),
            ("snipcart", "eleventy", "snipcart_ecommerce_simple"),
            ("snipcart", "astro", "snipcart_ecommerce_modern"),
            ("snipcart", "gatsby", "snipcart_ecommerce_react"),
            ("foxy", "astro", "foxy_ecommerce_advanced"),
            ("foxy", "gatsby", "foxy_ecommerce_react"),
        ]

        for provider, ssg_engine, expected_variant in test_combinations:
            with patch('stacks.shared.base_ssg_stack.BaseSSGStack.__init__'):
                stack = EcommerceStackFactory.create_ecommerce_stack(
                    scope=scope,
                    client_id="test-client",
                    domain="test.com",
                    ecommerce_provider=provider,
                    ssg_engine=ssg_engine
                )

                # Validate correct template variant resolved
                assert stack.ssg_config.template_variant == expected_variant

    def test_all_valid_combinations_coverage(self):
        """Test that all documented valid combinations are supported"""

        all_combinations = EcommerceStackFactory.get_all_valid_combinations()

        # Validate Snipcart combinations
        assert "snipcart" in all_combinations
        snipcart_engines = all_combinations["snipcart"]
        assert set(snipcart_engines) == {"eleventy", "astro", "hugo", "gatsby"}

        # Validate Foxy combinations
        assert "foxy" in all_combinations
        foxy_engines = all_combinations["foxy"]
        assert set(foxy_engines) == {"eleventy", "astro", "hugo", "gatsby"}

        # Validate future Shopify combinations are documented
        assert "shopify_basic" in all_combinations
        assert "shopify_advanced" in all_combinations

    def test_provider_tier_information(self):
        """Test that provider tier information supports business decisions"""

        # Test Snipcart tier info
        snipcart_info = EcommerceStackFactory.get_provider_tier_info("snipcart")
        assert snipcart_info["tier_name"] == "Simple E-commerce"
        assert snipcart_info["complexity_level"] == "low_to_medium"
        assert "small_businesses" in snipcart_info["target_market"]

        # Test Foxy tier info
        foxy_info = EcommerceStackFactory.get_provider_tier_info("foxy")
        assert foxy_info["tier_name"] == "Advanced E-commerce"
        assert foxy_info["complexity_level"] == "medium_to_high"
        assert "subscription_services" in foxy_info["target_market"]


class TestBusinessImpactValidation:
    """Test that the flexible architecture achieves business objectives"""

    def test_same_pricing_multiple_technical_levels(self):
        """Test that same monthly pricing serves multiple technical comfort levels"""

        # Get cost estimates for same provider, different SSG engines
        hugo_cost = EcommerceStackFactory.estimate_total_cost("snipcart", "hugo")
        eleventy_cost = EcommerceStackFactory.estimate_total_cost("snipcart", "eleventy")
        astro_cost = EcommerceStackFactory.estimate_total_cost("snipcart", "astro")
        gatsby_cost = EcommerceStackFactory.estimate_total_cost("snipcart", "gatsby")

        # Monthly costs should be the same (same provider tier)
        assert hugo_cost["monthly_cost_range"] == eleventy_cost["monthly_cost_range"]
        assert eleventy_cost["monthly_cost_range"] == astro_cost["monthly_cost_range"]
        assert astro_cost["monthly_cost_range"] == gatsby_cost["monthly_cost_range"]

        # Setup costs should vary by complexity (technical alignment)
        assert hugo_cost["setup_cost_range"][0] < gatsby_cost["setup_cost_range"][0]
        assert eleventy_cost["setup_cost_range"][0] < astro_cost["setup_cost_range"][0]

    def test_client_choice_eliminates_constraints(self):
        """Test that clients are no longer constrained by arbitrary pairings"""

        # Before: Client wanting Snipcart was forced to use Eleventy
        # After: Client can choose any compatible SSG engine

        scope = Mock()
        client_choices = [
            ("snipcart", "hugo"),     # Technical client choice
            ("snipcart", "eleventy"), # Balanced client choice
            ("snipcart", "astro"),    # Modern client choice
            ("snipcart", "gatsby"),   # React client choice
        ]

        for provider, ssg_choice in client_choices:
            with patch('stacks.shared.base_ssg_stack.BaseSSGStack.__init__'):
                # This should NOT raise an error - client choice is supported
                stack = EcommerceStackFactory.create_ecommerce_stack(
                    scope=scope,
                    client_id="flexible-client",
                    domain="flexible.com",
                    ecommerce_provider=provider,
                    ssg_engine=ssg_choice
                )

                assert stack.ssg_config.ssg_engine == ssg_choice
                assert stack.ecommerce_provider == provider

    def test_revenue_optimization_through_complexity_alignment(self):
        """Test that setup costs align with technical complexity appropriately"""

        # Technical clients (Hugo) should pay less for setup
        hugo_estimate = EcommerceStackFactory.estimate_total_cost("snipcart", "hugo")

        # Advanced clients (Gatsby) should pay more for setup complexity
        gatsby_estimate = EcommerceStackFactory.estimate_total_cost("snipcart", "gatsby")

        # Hugo should be cheaper setup (technical clients do more themselves)
        assert hugo_estimate["setup_cost_range"][0] < gatsby_estimate["setup_cost_range"][0]
        assert hugo_estimate["setup_cost_range"][1] < gatsby_estimate["setup_cost_range"][1]

        # But same monthly costs (same provider tier features)
        assert hugo_estimate["monthly_cost_range"] == gatsby_estimate["monthly_cost_range"]

    def test_code_efficiency_through_flexibility(self):
        """Test that flexible architecture reduces code duplication"""

        # Before: Would need separate stack classes for each combination
        # After: Single stack class supports multiple SSG engines

        # Test that one Snipcart stack class supports all compatible engines
        scope = Mock()
        snipcart_engines = ["hugo", "eleventy", "astro", "gatsby"]

        stack_instances = []
        for engine in snipcart_engines:
            with patch('stacks.shared.base_ssg_stack.BaseSSGStack.__init__'):
                stack = SnipcartEcommerceStack(
                    scope=scope,
                    construct_id=f"Test-{engine}",
                    client_id="test-client",
                    domain="test.com",
                    ssg_engine=engine
                )
                stack_instances.append(stack)

        # All instances are same class type (code reuse)
        assert all(isinstance(stack, SnipcartEcommerceStack) for stack in stack_instances)

        # But each has different SSG engine configuration (flexibility)
        engine_configs = [stack.ssg_config.ssg_engine for stack in stack_instances]
        assert set(engine_configs) == set(snipcart_engines)


# Convenience test functions demonstrating usage patterns
class TestUsagePatterns:
    """Test common client usage patterns with flexible architecture"""

    def test_budget_conscious_technical_client(self):
        """Test optimal configuration for budget-conscious technical client"""

        requirements = {
            "budget_conscious": True,
            "technical_team": True,
            "performance_critical": True
        }

        recommendations = EcommerceStackFactory.get_ecommerce_recommendations(requirements)

        # Should get Snipcart + Hugo recommendation
        budget_rec = next(r for r in recommendations if r["ecommerce_provider"] == "snipcart")
        assert budget_rec["recommended_ssg"] == "hugo"

        # Validate cost alignment
        cost_estimate = EcommerceStackFactory.estimate_total_cost("snipcart", "hugo")
        assert cost_estimate["ssg_complexity_multiplier"] == 0.8  # Reduced complexity

    def test_modern_business_intermediate_client(self):
        """Test optimal configuration for modern business with intermediate team"""

        requirements = {
            "modern_features": True,
            "visual_appeal": True,
            "balanced_complexity": True
        }

        recommendations = EcommerceStackFactory.get_ecommerce_recommendations(requirements)

        # Should get options including Astro for modern features
        has_astro_option = any(
            "astro" in rec.get("ssg_options", [])
            for rec in recommendations
        )
        assert has_astro_option

    def test_advanced_features_react_client(self):
        """Test optimal configuration for client needing advanced features with React preference"""

        requirements = {
            "advanced_ecommerce": True,
            "subscriptions": True,
            "prefer_react": True
        }

        recommendations = EcommerceStackFactory.get_ecommerce_recommendations(requirements)

        # Should get Foxy + Gatsby recommendation
        advanced_rec = next(r for r in recommendations if r["ecommerce_provider"] == "foxy")
        assert advanced_rec["recommended_ssg"] == "gatsby"
        assert "Subscription" in advanced_rec["best_for"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])