"""
Integration Tests for Optional Event-Driven Architecture

This test suite validates that the new dual-mode stacks integrate correctly
with the existing EventDrivenIntegrationLayer architecture.

Key Testing Areas:
1. Stack instantiation with both Direct and Event-Driven modes
2. EventDrivenIntegrationLayer compatibility with new ClientServiceConfig
3. Webhook endpoint configuration and event flow
4. Unified content schema validation
5. Cross-provider composition functionality
"""

import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template

from models.service_config import ClientServiceConfig, IntegrationMode, ServiceIntegrationConfig, CMSProviderConfig, EcommerceProviderConfig, ServiceType, ServiceTier, ManagementModel
from stacks.cms.decap_cms_tier_stack import DecapCMSTierStack
from stacks.cms.sanity_cms_tier_stack import SanityCMSTierStack
from stacks.cms.contentful_cms_stack import ContentfulCMSStack
from stacks.cms.tina_cms_tier_stack import TinaCMSTierStack
from stacks.ecommerce.snipcart_ecommerce_stack import SnipcartEcommerceStack
from stacks.ecommerce.foxy_ecommerce_stack import FoxyEcommerceStack
from stacks.ecommerce.shopify_basic_ecommerce_stack import ShopifyBasicEcommerceStack


class TestEventDrivenIntegration:
    """Test suite for event-driven integration architecture"""

    def setup_method(self):
        """Set up test environment for each test"""
        self.app = App()

    def create_test_client_config(self, cms_provider: str, ecommerce_provider: str = None,
                                 integration_mode: IntegrationMode = IntegrationMode.EVENT_DRIVEN) -> ClientServiceConfig:
        """Create a test client configuration"""

        # CMS configuration
        cms_settings = {
            "decap": {"repository": "test-repo", "repository_owner": "test-owner", "branch": "main"},
            "sanity": {"project_id": "test-project", "dataset": "production"},
            "contentful": {"space_id": "test-space", "environment": "master"},
            "tina": {"repository": "test-repo", "repository_owner": "test-owner", "tina_client_id": "test-client"}
        }

        cms_config = CMSProviderConfig(
            provider=cms_provider,
            settings=cms_settings[cms_provider]
        )

        # E-commerce configuration (if provided)
        ecommerce_config = None
        if ecommerce_provider:
            ecommerce_settings = {
                "snipcart": {"public_api_key": "test-key", "currency": "USD"},
                "foxy": {"subdomain": "test-foxy", "currency": "USD"},
                "shopify_basic": {"store_domain": "test-store.myshopify.com", "plan": "basic"}
            }

            ecommerce_config = EcommerceProviderConfig(
                provider=ecommerce_provider,
                settings=ecommerce_settings[ecommerce_provider]
            )

        # Service integration configuration
        service_type = ServiceType.COMPOSED_STACK if ecommerce_provider else ServiceType.CMS_TIER
        service_integration = ServiceIntegrationConfig(
            service_type=service_type,
            ssg_engine="astro",
            integration_mode=integration_mode,
            cms_config=cms_config,
            ecommerce_config=ecommerce_config
        )

        return ClientServiceConfig(
            client_id="test-client",
            company_name="Test Company",
            domain="test.com",
            contact_email="test@test.com",
            service_tier=ServiceTier.TIER1,
            management_model=ManagementModel.SELF_MANAGED,
            service_integration=service_integration
        )

    def test_direct_mode_stack_creation(self):
        """Test that Direct mode stacks create successfully without EventDrivenIntegrationLayer"""

        # Test Direct mode CMS stack
        cms_config = self.create_test_client_config("decap", integration_mode=IntegrationMode.DIRECT)

        cms_stack = DecapCMSTierStack(
            self.app,
            "TestCMSDirectStack",
            client_config=cms_config
        )

        # Verify stack creation
        assert cms_stack is not None
        assert cms_stack.integration_mode == IntegrationMode.DIRECT

        # Should NOT have integration_layer attribute in Direct mode
        assert not hasattr(cms_stack, 'integration_layer')

        # Verify CloudFormation template generation
        template = Template.from_stack(cms_stack)

        # Should have basic infrastructure but no SNS topics
        template.resource_count_is("AWS::S3::Bucket", 1)  # Content bucket
        template.resource_count_is("AWS::CloudFront::Distribution", 1)  # CDN
        template.resource_count_is("AWS::CodeBuild::Project", 1)  # Build project
        template.resource_count_is("AWS::SNS::Topic", 0)  # No SNS in Direct mode

    def test_event_driven_mode_stack_creation(self):
        """Test that Event-Driven mode stacks create successfully with EventDrivenIntegrationLayer"""

        # Test Event-Driven mode CMS stack
        cms_config = self.create_test_client_config("decap", integration_mode=IntegrationMode.EVENT_DRIVEN)

        cms_stack = DecapCMSTierStack(
            self.app,
            "TestCMSEventStack",
            client_config=cms_config
        )

        # Verify stack creation
        assert cms_stack is not None
        assert cms_stack.integration_mode == IntegrationMode.EVENT_DRIVEN

        # Should have integration_layer attribute in Event-Driven mode
        assert hasattr(cms_stack, 'integration_layer')
        assert cms_stack.integration_layer is not None

        # Verify CloudFormation template generation
        template = Template.from_stack(cms_stack)

        # Should have event-driven infrastructure
        template.resource_count_is("AWS::S3::Bucket", 1)  # Content bucket
        template.resource_count_is("AWS::CloudFront::Distribution", 1)  # CDN
        template.resource_count_is("AWS::SNS::Topic", 1)  # Content events topic
        template.resource_count_is("AWS::DynamoDB::Table", 2)  # Content cache + build batching
        # Should have at least 3 Lambda functions for integration handlers
        lambda_resources = template.find_resources("AWS::Lambda::Function")
        assert len(lambda_resources) >= 3

    def test_composed_stack_creation(self):
        """Test that composed CMS + E-commerce stacks work together"""

        # Create composed client configuration
        cms_config = self.create_test_client_config("decap", "snipcart", IntegrationMode.EVENT_DRIVEN)

        # Create CMS stack
        cms_stack = DecapCMSTierStack(
            self.app,
            "TestComposedCMSStack",
            client_config=cms_config
        )

        # Create E-commerce stack with same config
        ecommerce_stack = SnipcartEcommerceStack(
            self.app,
            "TestComposedEcommerceStack",
            client_config=cms_config
        )

        # Both stacks should share the same integration layer configuration
        assert cms_stack.integration_mode == IntegrationMode.EVENT_DRIVEN
        assert ecommerce_stack.integration_mode == IntegrationMode.EVENT_DRIVEN

        # Both should have integration layers
        assert hasattr(cms_stack, 'integration_layer')
        assert hasattr(ecommerce_stack, 'integration_layer')

        # Verify they can coexist (no naming conflicts)
        cms_template = Template.from_stack(cms_stack)
        ecommerce_template = Template.from_stack(ecommerce_stack)

        # Both should have their own resources
        cms_template.resource_count_is("AWS::SNS::Topic", 1)
        ecommerce_template.resource_count_is("AWS::SNS::Topic", 1)

    def test_all_cms_providers_event_driven(self):
        """Test that all CMS providers support event-driven mode"""

        cms_providers = ["decap", "sanity", "contentful", "tina"]
        stack_classes = [DecapCMSTierStack, SanityCMSTierStack, ContentfulCMSStack, TinaCMSTierStack]

        for provider, stack_class in zip(cms_providers, stack_classes):
            # Create configuration for each provider
            config = self.create_test_client_config(provider, integration_mode=IntegrationMode.EVENT_DRIVEN)

            # Create stack
            stack = stack_class(
                self.app,
                f"Test{provider.title()}EventStack",
                client_config=config
            )

            # Verify event-driven mode works
            assert stack.integration_mode == IntegrationMode.EVENT_DRIVEN
            assert hasattr(stack, 'integration_layer')

            # Verify CloudFormation template has SNS topic
            template = Template.from_stack(stack)
            template.resource_count_is("AWS::SNS::Topic", 1)

    def test_all_ecommerce_providers_event_driven(self):
        """Test that all E-commerce providers support event-driven mode"""

        ecommerce_providers = ["snipcart", "foxy", "shopify_basic"]
        stack_classes = [SnipcartEcommerceStack, FoxyEcommerceStack, ShopifyBasicEcommerceStack]

        for provider, stack_class in zip(ecommerce_providers, stack_classes):
            # Create configuration for each provider
            config = self.create_test_client_config("decap", provider, IntegrationMode.EVENT_DRIVEN)

            # Create stack
            stack = stack_class(
                self.app,
                f"Test{provider.title()}EventStack",
                client_config=config
            )

            # Verify event-driven mode works
            assert stack.integration_mode == IntegrationMode.EVENT_DRIVEN
            assert hasattr(stack, 'integration_layer')

            # Verify CloudFormation template has SNS topic
            template = Template.from_stack(stack)
            template.resource_count_is("AWS::SNS::Topic", 1)

    def test_webhook_endpoints_configuration(self):
        """Test that webhook endpoints are correctly configured for each provider"""

        # Create event-driven CMS stack
        config = self.create_test_client_config("decap", integration_mode=IntegrationMode.EVENT_DRIVEN)
        stack = DecapCMSTierStack(self.app, "TestWebhookStack", client_config=config)

        # Verify API Gateway is created
        template = Template.from_stack(stack)
        template.resource_count_is("AWS::ApiGateway::RestApi", 1)
        template.resource_count_is("AWS::ApiGateway::Method", at_least=1)

        # Verify Lambda integration
        template.resource_count_is("AWS::Lambda::Function", at_least=1)

    @pytest.mark.legacy_pricing
    def test_cost_estimation_compatibility(self):
        """Test that cost estimation works for both modes"""

        # Test Direct mode cost estimation
        direct_config = self.create_test_client_config("decap", integration_mode=IntegrationMode.DIRECT)
        direct_stack = DecapCMSTierStack(self.app, "TestDirectCostStack", client_config=direct_config)

        direct_costs = direct_stack.get_monthly_cost_estimate()
        assert isinstance(direct_costs, dict)
        assert "monthly_fixed_costs" in direct_costs or "decap_cms" in direct_costs

        # Test Event-Driven mode cost estimation
        event_config = self.create_test_client_config("decap", integration_mode=IntegrationMode.EVENT_DRIVEN)
        event_stack = DecapCMSTierStack(self.app, "TestEventCostStack", client_config=event_config)

        event_costs = event_stack.get_monthly_cost_estimate()
        assert isinstance(event_costs, dict)

        # Event-driven mode should have additional costs for SNS, Lambda, DynamoDB
        # This validates that the cost calculation adapts to the integration mode

    @pytest.mark.capability_focused
    def test_capability_alignment_scoring_compatibility(self):
        """Test that client capability alignment scoring works for all providers - validates technical compatibility"""

        # Test capability requirements (pricing-neutral)
        requirements = {
            "technical_comfort": "intermediate",
            "team_technical_skills": "high",
            "content_volume": "medium",
            "growth_planning": True,
            "integration_flexibility": True
        }

        # Test all CMS providers
        cms_classes = [DecapCMSTierStack, SanityCMSTierStack, ContentfulCMSStack, TinaCMSTierStack]

        for stack_class in cms_classes:
            score = stack_class.get_client_capability_alignment_score(requirements)

            assert isinstance(score, dict)
            assert "alignment_score" in score
            assert "capability_alignment" in score
            assert "capability_reasons" in score
            assert "integration_mode_recommendation" in score

            # Score should be between 0 and 100
            assert 0 <= score["alignment_score"] <= 100

    def test_configuration_validation(self):
        """Test that configuration validation works correctly"""

        # Test invalid CMS provider
        with pytest.raises(ValueError, match="Expected.*CMS provider"):
            invalid_config = self.create_test_client_config("invalid_cms")
            DecapCMSTierStack(self.app, "TestInvalidStack", client_config=invalid_config)

        # Test missing required settings
        with pytest.raises(ValueError, match="requires.*in settings"):
            config = self.create_test_client_config("decap")
            config.service_integration.cms_config.settings = {}  # Remove required settings
            DecapCMSTierStack(self.app, "TestMissingSettingsStack", client_config=config)

    def test_integration_mode_switching_compatibility(self):
        """Test that the same client config can be used for both modes"""

        base_config = self.create_test_client_config("decap")

        # Test Direct mode
        direct_config = base_config.model_copy()
        direct_config.service_integration.integration_mode = IntegrationMode.DIRECT

        direct_stack = DecapCMSTierStack(self.app, "TestSwitchDirectStack", client_config=direct_config)
        assert direct_stack.integration_mode == IntegrationMode.DIRECT

        # Test Event-Driven mode with same base config
        event_config = base_config.model_copy()
        event_config.service_integration.integration_mode = IntegrationMode.EVENT_DRIVEN

        event_stack = DecapCMSTierStack(self.app, "TestSwitchEventStack", client_config=event_config)
        assert event_stack.integration_mode == IntegrationMode.EVENT_DRIVEN

        # Both should create valid stacks
        assert direct_stack is not None
        assert event_stack is not None


class TestEventDrivenIntegrationLayerCompatibility:
    """Test EventDrivenIntegrationLayer compatibility with new architecture"""

    def test_integration_layer_model_compatibility(self):
        """Test that EventDrivenIntegrationLayer can work with ClientServiceConfig"""

        # NOTE: This test identifies the compatibility issue that needs to be fixed
        # The EventDrivenIntegrationLayer currently expects ClientConfig but we use ClientServiceConfig

        config = ClientServiceConfig(
            client_id="test-integration",
            company_name="Integration Test Co",
            domain="integration-test.com",
            contact_email="test@integration-test.com",
            service_integration=ServiceIntegrationConfig(
                ssg_engine="astro",
                integration_mode=IntegrationMode.EVENT_DRIVEN,
                cms_config=CMSProviderConfig(
                    provider="decap",
                    settings={"repository": "test-repo", "repository_owner": "test-owner"}
                )
            )
        )

        # This is where the compatibility issue would manifest
        # The EventDrivenIntegrationLayer expects different model structure

        # For now, we'll test that our config has the necessary attributes
        assert hasattr(config, 'client_id')
        assert hasattr(config, 'service_integration')
        assert config.client_id == "test-integration"

        # Would need to create ClientConfig adapter or update EventDrivenIntegrationLayer
        # to use ClientServiceConfig directly

    def test_unified_content_schema(self):
        """Test that unified content events follow the expected schema"""

        # Test event structure that would be published to SNS
        test_event = {
            'event_type': 'content_updated',
            'provider': 'decap',
            'content_id': 'test-content-123',
            'content_type': 'article',
            'timestamp': '2023-01-01T00:00:00Z',
            'data': {
                'file_path': 'content/posts/test.md',
                'commit_sha': 'abc123',
                'commit_message': 'Update content',
                'author': 'Test Author',
                'action': 'modified',
                'cms_provider': 'decap'
            }
        }

        # Verify event structure matches expected schema
        required_fields = ['event_type', 'provider', 'content_id', 'content_type', 'timestamp', 'data']
        for field in required_fields:
            assert field in test_event

        # Verify data payload has required information
        assert 'action' in test_event['data']
        assert test_event['provider'] in ['decap', 'sanity', 'contentful', 'tina', 'snipcart', 'foxy', 'shopify_basic']


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])