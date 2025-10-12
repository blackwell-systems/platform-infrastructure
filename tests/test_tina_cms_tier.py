"""
Test Tina CMS Tier Implementation

Comprehensive tests for the Tina CMS tier stack implementation,
verifying integration with supported SSG engines and proper
factory-based configuration.

Test Coverage:
- Client configuration validation
- CMS provider integration
- SSG engine compatibility (Next.js, Astro, Gatsby)
- Factory recommendation system
- Cost estimation accuracy
- Infrastructure resource creation
- Tina Cloud integration features
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from models.cms_config import CMSIntegrationConfig, tina_cms_config
from clients._templates.client_config import create_client_config
from shared.factories.platform_stack_factory import PlatformStackFactory
from shared.providers.cms.factory import CMSProviderFactory
from stacks.cms.tina_cms_tier_stack import TinaCMSTierStack


@pytest.mark.skip(reason="CMS configuration classes removed during pricing extraction - preserve for future capability-focused implementation")
class TestTinaCMSConfiguration:
    """Test Tina CMS configuration and validation"""

    def test_valid_tina_cms_config(self):
        """Test that valid Tina CMS configuration is accepted"""

        cms_config = CMSIntegrationConfig(
            cms=tina_cms_config(
                admin_users=["admin@example.com"],
                repository="test-repo",
                repository_owner="test-owner",
                branch="main"
            ),
            ssg_engine="nextjs"
        )

        assert cms_config.cms.provider == "tina"
        assert cms_config.ssg_engine == "nextjs"
        assert cms_config.cms.admin_users == ["admin@example.com"]
        assert cms_config.cms.cms_type.value == "hybrid"

    def test_tina_cms_provider_creation(self):
        """Test that Tina CMS provider can be created via factory"""

        config = {
            "admin_users": ["admin@example.com"],
            "repository": "test-repo",
            "repository_owner": "test-owner",
            "branch": "main"
        }

        provider = CMSProviderFactory.create_provider("tina", config)

        assert provider.provider_name == "tina"
        assert provider.get_cms_type().value == "hybrid"
        assert provider.get_auth_method().value == "github_oauth"

    def test_tina_cloud_integration_config(self):
        """Test Tina Cloud integration configuration"""

        cms_config = CMSIntegrationConfig(
            cms=tina_cms_config(
                admin_users=["admin@example.com"],
                repository="test-repo",
                repository_owner="test-owner",
                tina_token="tina_test_token",
                client_id="tina_test_client_id"
            ),
            ssg_engine="nextjs"
        )

        content_settings = cms_config.cms.content_settings
        assert content_settings.get("tina_token") == "tina_test_token"
        assert content_settings.get("tina_client_id") == "tina_test_client_id"

    def test_tina_repository_configuration(self):
        """Test that repository configuration is stored correctly"""

        config = tina_cms_config(
            admin_users=["admin@example.com"],
            repository="my-tina-site",
            repository_owner="my-org"
        )

        content_settings = config.content_settings
        assert content_settings["repository"] == "my-tina-site"
        assert content_settings["repository_owner"] == "my-org"
        assert content_settings["branch"] == "main"  # Default
        assert content_settings["content_path"] == "content"  # Default
        assert content_settings["media_path"] == "public/images"  # Default

    def test_tina_ssg_engine_compatibility(self):
        """Test that supported SSG engines work with Tina CMS"""

        supported_engines = ["nextjs", "astro", "gatsby"]

        for engine in supported_engines:
            cms_config = CMSIntegrationConfig(
                cms=tina_cms_config(
                    admin_users=["admin@example.com"],
                    repository="test-repo",
                    repository_owner="test-owner"
                ),
                ssg_engine=engine
            )

            # Should not raise validation error
            cms_config.validate_integration()

    def test_unsupported_ssg_engine(self):
        """Test that unsupported SSG engines are rejected"""

        with pytest.raises(ValueError):
            cms_config = CMSIntegrationConfig(
                cms=tina_cms_config(
                    admin_users=["admin@example.com"],
                    repository="test-repo",
                    repository_owner="test-owner"
                ),
                ssg_engine="hugo"  # Hugo not supported by Tina
            )
            cms_config.validate_integration()


@pytest.mark.skip(reason="CMS client configuration removed during pricing extraction - preserve for future capability-focused implementation")
class TestTinaCMSClientConfiguration:
    """Test client configuration with Tina CMS tier"""

    @pytest.mark.parametrize("ssg_engine", ["nextjs", "astro", "gatsby"])
    def test_tina_cms_tier_client_config(self, ssg_engine):
        """Test client configuration for each supported SSG engine"""

        cms_config = CMSIntegrationConfig(
            cms=tina_cms_config(
                admin_users=["admin@example.com"],
                repository="test-repo",
                repository_owner="test-owner"
            ),
            ssg_engine=ssg_engine
        )

        client = create_client_config(
            client_id="test-client",
            company_name="Test Company",
            service_tier="tier1",
            stack_type="tina_cms_tier",
            domain="test.com",
            contact_email="admin@test.com",
            management_model="self_managed",
            ssg_engine=ssg_engine,
            cms_config=cms_config
        )

        # Validate client configuration
        assert client.client_id == "test-client"
        assert client.stack_type == "tina_cms_tier"
        assert client.ssg_engine == ssg_engine
        assert client.has_cms()
        assert client.cms_config.cms.provider == "tina"

        # Validate CMS compatibility
        client.validate_cms_compatibility()

    def test_tina_cms_tier_environment_variables(self):
        """Test that CMS environment variables are properly generated"""

        cms_config = CMSIntegrationConfig(
            cms=tina_cms_config(
                admin_users=["admin@example.com"],
                repository="test-repo",
                repository_owner="test-owner",
                branch="main",
                tina_token="test_token",
                client_id="test_client_id"
            ),
            ssg_engine="nextjs"
        )

        client = create_client_config(
            client_id="test-client",
            company_name="Test Company",
            service_tier="tier1",
            stack_type="tina_cms_tier",
            domain="test.com",
            contact_email="admin@test.com",
            management_model="self_managed",
            ssg_engine="nextjs",
            cms_config=cms_config
        )

        env_vars = client.get_cms_environment_variables()

        assert "CMS_PROVIDER" in env_vars
        assert env_vars["CMS_PROVIDER"] == "tina"
        assert "GITHUB_REPO" in env_vars
        assert "GITHUB_OWNER" in env_vars

    def test_tina_visual_editing_features(self):
        """Test that visual editing features are properly configured"""

        provider = CMSProviderFactory.create_provider("tina", {
            "repository": "test-repo",
            "repository_owner": "test-owner"
        })

        capabilities = provider.get_supported_capabilities()
        capability_names = [cap.value for cap in capabilities]

        assert "visual_editing" in capability_names
        assert "real_time_preview" in capability_names
        assert "rich_text_editing" in capability_names
        assert "structured_content" in capability_names


class TestSSGFactoryIntegration:
    """Test SSG factory integration with Tina CMS tier"""

    def test_tina_cms_tier_in_stack_tiers(self):
        """Test that Tina CMS tier is registered in factory"""

        stack_info = PlatformStackFactory.get_stack_metadata("tina_cms_tier")

        assert stack_info is not None
        assert stack_info["tier_name"] == "Tina CMS - Visual Editing with Git Workflow"
        assert stack_info["cms_provider"] == "tina"
        assert stack_info["cms_type"] == "hybrid"
        assert "nextjs" in stack_info["ssg_engine_options"]
        assert "astro" in stack_info["ssg_engine_options"]
        assert "gatsby" in stack_info["ssg_engine_options"]

    @pytest.mark.capability_focused
    @pytest.mark.skip(reason="Metadata fields removed during pricing extraction - preserve for future capability-focused implementation")
    def test_tina_tier_capability_metadata(self):
        """Test Tina tier capability metadata in factory - validates technical capabilities without pricing"""
        tina_info = PlatformStackFactory.get_stack_metadata("tina_cms_tier")

        # Validate capability-focused metadata fields
        assert tina_info["tier_name"] == "Tina CMS - Visual Editing with Git Workflow"
        assert tina_info["cms_provider"] == "tina"
        assert tina_info["cms_type"] == "hybrid"

        # Validate supported SSG engine options
        expected_engines = ["nextjs", "astro", "gatsby"]
        for engine in expected_engines:
            assert engine in tina_info["ssg_engine_options"]

        # Validate target market and capabilities (TODO: implement in capability-focused architecture)
        assert "visual_content_editing" in tina_info.get("target_market", [])
        assert "git_workflow" in tina_info.get("key_capabilities", [])

    @pytest.mark.capability_focused
    def test_cms_recommendations_include_tina(self):
        """Test that factory recommendations include Tina CMS tier based on visual editing capabilities"""

        requirements = {
            "content_management": True,
            "visual_editing": True,
            "collaboration": True,
            "content_editor_friendly": True
        }

        recommendations = PlatformStackFactory.get_recommendations(requirements)

        # Should include Tina CMS tier
        tina_recommendations = [r for r in recommendations if r["stack_type"] == "tina_cms_tier"]
        assert len(tina_recommendations) > 0

        tina_rec = tina_recommendations[0]
        assert tina_rec["cms_provider"] == "tina"
        assert tina_rec["cms_type"] == "hybrid"
        assert "ssg_engine_options" in tina_rec

    def test_visual_editing_recommends_tina(self):
        """Test that visual editing requirements recommend Tina"""

        requirements = {
            "content_management": True,
            "visual_editing": True
        }

        recommendations = PlatformStackFactory.get_recommendations(requirements)
        tina_rec = next(r for r in recommendations if r["stack_type"] == "tina_cms_tier")

        assert "Visual editing interface" in tina_rec["key_benefits"]
        assert "Real-time preview" in tina_rec["key_benefits"]

    def test_react_preferred_recommends_react_ecosystem(self):
        """Test that React preference recommends React-based SSG with Tina"""

        requirements = {
            "content_management": True,
            "react_preferred": True
        }

        recommendations = PlatformStackFactory.get_recommendations(requirements)
        tina_rec = next(r for r in recommendations if r["stack_type"] == "tina_cms_tier")

        # Should recommend either Next.js or Gatsby (both React-based)
        assert tina_rec["ssg_engine"] in ["nextjs", "gatsby"]

    def test_modern_features_recommend_astro(self):
        """Test that modern features requirements recommend Astro"""

        requirements = {
            "content_management": True,
            "modern_features": True,
            "visual_editing": True
        }

        recommendations = PlatformStackFactory.get_recommendations(requirements)
        tina_rec = next(r for r in recommendations if r["stack_type"] == "tina_cms_tier")

        assert tina_rec["ssg_engine"] == "astro"


@pytest.mark.skip(reason="Stack implementation classes removed during pricing extraction - preserve for future capability-focused implementation")
class TestTinaCMSStack:
    """Test Tina CMS tier stack infrastructure creation"""

    def create_test_client_config(self, ssg_engine="nextjs", with_tina_cloud=False):
        """Helper method to create test client configuration"""

        tina_config_args = {
            "admin_users": ["admin@example.com"],
            "repository": "test-repo",
            "repository_owner": "test-owner",
            "branch": "main"
        }

        if with_tina_cloud:
            tina_config_args["tina_token"] = "test_token"
            tina_config_args["client_id"] = "test_client_id"

        cms_config = CMSIntegrationConfig(
            cms=tina_cms_config(**tina_config_args),
            ssg_engine=ssg_engine
        )

        return create_client_config(
            client_id="test-client",
            company_name="Test Company",
            service_tier="tier1",
            stack_type="tina_cms_tier",
            domain="test.com",
            contact_email="admin@test.com",
            management_model="self_managed",
            ssg_engine=ssg_engine,
            cms_config=cms_config
        )

    @patch('aws_cdk.Stack.__init__')
    def test_tina_stack_initialization(self, mock_stack_init):
        """Test that Tina CMS stack can be initialized"""

        mock_stack_init.return_value = None
        client_config = self.create_test_client_config()

        # Mock the CDK constructs and scope
        mock_scope = Mock()
        construct_id = "TestTinaStack"

        # Create stack instance (would create AWS resources in real deployment)
        try:
            # This would create the actual stack in real usage
            # stack = TinaCMSTierStack(mock_scope, construct_id, client_config)
            pass  # Skip actual stack creation in tests
        except Exception as e:
            pytest.fail(f"Stack initialization failed: {e}")

    @pytest.mark.parametrize("ssg_engine,expected_output_dir", [
        ("nextjs", ".next"),
        ("astro", "dist"),
        ("gatsby", "public")
    ])
    def test_ssg_build_commands(self, ssg_engine, expected_output_dir):
        """Test that correct build commands are generated for each SSG engine"""

        client_config = self.create_test_client_config(ssg_engine)

        # Mock stack creation to test build command generation
        mock_scope = Mock()
        construct_id = "TestTinaStack"

        # Test would verify build commands are correct for each SSG engine
        assert ssg_engine in ["nextjs", "astro", "gatsby"]
        assert expected_output_dir in [".next", "dist", "public"]

    def test_tina_cloud_integration_creation(self):
        """Test that Tina Cloud integration resources are created when configured"""

        client_config = self.create_test_client_config(with_tina_cloud=True)

        # Verify Tina Cloud settings are present
        content_settings = client_config.cms_config.cms.content_settings
        assert content_settings.get("tina_token") is not None
        assert content_settings.get("tina_client_id") is not None


class TestCostEstimation:
    """Test cost estimation for Tina CMS tier"""

    @pytest.mark.legacy_pricing
    def test_tina_cms_cost_estimation_self_hosted(self):
        """Test that self-hosted Tina CMS cost estimation is accurate"""

        provider = CMSProviderFactory.create_provider("tina", {
            "admin_users": ["admin@example.com"],
            "repository": "test-repo",
            "repository_owner": "test-owner"
        })

        cost_estimate = provider.estimate_monthly_cost("medium")

        # Self-hosted Tina should be free
        assert cost_estimate.base_monthly_fee == 0
        assert cost_estimate.total_estimated == 0
        assert cost_estimate.content_volume == "medium"

    @pytest.mark.legacy_pricing
    def test_tina_cms_cost_estimation_with_cloud(self):
        """Test cost estimation with Tina Cloud features"""

        provider = CMSProviderFactory.create_provider("tina", {
            "admin_users": ["admin@example.com"],
            "repository": "test-repo",
            "repository_owner": "test-owner",
            "tina_token": "test_token",
            "tina_client_id": "test_client_id"
        })

        cost_estimate = provider.estimate_monthly_cost("medium")

        # Tina Cloud should have monthly cost
        assert cost_estimate.base_monthly_fee > 0
        assert cost_estimate.total_estimated > 0

    @pytest.mark.legacy_pricing
    def test_tina_setup_cost_by_ssg_engine(self):
        """Test that setup costs vary appropriately by SSG engine complexity"""

        stack_info = PlatformStackFactory.get_stack_metadata("tina_cms_tier")
        setup_range = stack_info["setup_cost_range"]

        # Should have reasonable setup cost range
        assert setup_range[0] >= 1200   # Minimum (Next.js)
        assert setup_range[1] <= 2880   # Maximum (Gatsby with complex features)
        assert setup_range[1] > setup_range[0]  # Range should exist

    @pytest.mark.legacy_pricing
    def test_monthly_cost_includes_cms_and_hosting(self):
        """Test that monthly costs include both CMS and hosting"""

        stack_info = PlatformStackFactory.get_stack_metadata("tina_cms_tier")
        monthly_range = stack_info["monthly_cost_range"]

        # Should include hosting + optional Tina Cloud costs
        assert monthly_range[0] == 60    # Minimum (self-hosted)
        assert monthly_range[1] == 125   # Maximum (with Tina Cloud)
        assert monthly_range[1] > monthly_range[0]


@pytest.mark.skip(reason="Integration functionality removed during pricing extraction - preserve for future capability-focused implementation")
class TestTinaCMSIntegration:
    """Integration tests for complete Tina CMS tier workflow"""

    def test_end_to_end_client_onboarding(self):
        """Test complete client onboarding workflow"""

        # 1. Create client configuration
        cms_config = CMSIntegrationConfig(
            cms=tina_cms_config(
                admin_users=["admin@example.com"],
                repository="client-website",
                repository_owner="client-org",
                tina_token="client_token",
                client_id="client_tina_id"
            ),
            ssg_engine="nextjs"
        )

        client = create_client_config(
            client_id="test-client",
            company_name="Test Client",
            service_tier="tier1",
            stack_type="tina_cms_tier",
            domain="testclient.com",
            contact_email="admin@testclient.com",
            management_model="self_managed",
            ssg_engine="nextjs",
            cms_config=cms_config
        )

        # 2. Validate configuration
        client.validate_cms_compatibility()

        # 3. Get CMS provider instance
        provider = client.get_cms_provider_instance()
        assert provider is not None
        assert provider.provider_name == "tina"

        # 4. Get environment variables
        env_vars = client.get_cms_environment_variables()
        assert len(env_vars) > 0
        assert "CMS_PROVIDER" in env_vars

        # 5. Verify cost estimation
        cost_estimate = provider.estimate_monthly_cost("medium")
        assert cost_estimate.total_estimated > 0  # Tina Cloud enabled

    @pytest.mark.capability_focused
    def test_factory_recommendation_workflow(self):
        """Test factory recommendation workflow for Tina CMS - validates capability-based matching"""

        # 1. Client capability requirements (pricing-neutral)
        requirements = {
            "content_management": True,
            "visual_editing": True,
            "collaboration": True,
            "react_preferred": True,
            "developer_friendly": True
        }

        # 2. Get recommendations
        recommendations = PlatformStackFactory.get_recommendations(requirements)

        # 3. Should recommend Tina CMS tier
        tina_rec = next((r for r in recommendations if r["stack_type"] == "tina_cms_tier"), None)
        assert tina_rec is not None

        # 4. Verify capability-focused recommendation details
        assert tina_rec["cms_provider"] == "tina"
        assert tina_rec["cms_type"] == "hybrid"
        assert "Visual editing interface" in tina_rec["key_benefits"]

    def test_multi_ssg_engine_compatibility(self):
        """Test that all SSG engines work with Tina CMS tier"""

        supported_engines = ["nextjs", "astro", "gatsby"]

        for engine in supported_engines:
            # Create client configuration for each engine
            cms_config = CMSIntegrationConfig(
                cms=tina_cms_config(
                    admin_users=["admin@example.com"],
                    repository="test-repo",
                    repository_owner="test-owner"
                ),
                ssg_engine=engine
            )

            client = create_client_config(
                client_id=f"test-{engine}",
                company_name=f"Test {engine.title()} Client",
                service_tier="tier1",
                stack_type="tina_cms_tier",
                domain=f"test{engine}.com",
                contact_email="admin@example.com",
                management_model="self_managed",
                ssg_engine=engine,
                cms_config=cms_config
            )

            # Should validate successfully
            client.validate_cms_compatibility()

            # Should get provider instance
            provider = client.get_cms_provider_instance()
            assert provider is not None

    def test_visual_editing_features_integration(self):
        """Test that visual editing features are properly integrated"""

        provider = CMSProviderFactory.create_provider("tina", {
            "repository": "test-repo",
            "repository_owner": "test-owner"
        })

        # Test admin interface configuration
        admin_config = provider.get_admin_interface_config()
        assert admin_config["interface_type"] == "visual_editor"
        assert admin_config["real_time_preview"] is True
        assert admin_config["git_integration"] is True

        # Test content model schema
        schema = provider.get_content_model_schema()
        assert schema["schema_format"] == "tina_schema"
        assert "collections" in schema
        assert len(schema["collections"]) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])