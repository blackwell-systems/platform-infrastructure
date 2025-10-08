"""
Snipcart E-commerce Stack - Flexible SSG Engine Support

This stack demonstrates the e-commerce provider flexibility architecture:

TRANSFORMATION ACHIEVED:
- Before: Only Eleventy + Snipcart (hardcoded pairing)
- After: Hugo/Eleventy/Astro/Gatsby + Snipcart (client choice within provider tier)

BUSINESS BENEFITS:
- Same monthly cost ($85-125) serves multiple technical comfort levels
- Client chooses Snipcart tier for features/budget, then SSG for technical preference
- Revenue optimization through appropriate complexity alignment

CLIENT CHOICE EXAMPLES:
- Technical client: Hugo + Snipcart (fast builds, performance)
- Intermediate client: Eleventy + Snipcart (balanced complexity)
- Modern client: Astro + Snipcart (component islands, modern features)
- Advanced client: Gatsby + Snipcart (React ecosystem, GraphQL)
"""

from typing import Dict, Optional
from constructs import Construct
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ssm as ssm,
    CfnParameter
)

from stacks.shared.base_ecommerce_stack import BaseEcommerceStack


class SnipcartEcommerceStack(BaseEcommerceStack):
    """
    Snipcart e-commerce stack supporting multiple SSG engines.

    Compatible SSG Engines: Hugo, Eleventy, Astro, Gatsby
    E-commerce Features: Simple setup, 2% transaction fee, $29-99/month
    Monthly Cost: $85-125 (hosting + e-commerce)
    Setup Cost: $960-2,640 (varies by SSG complexity)

    This stack enables clients to:
    1. Choose Snipcart tier for budget-friendly e-commerce features
    2. Select their preferred SSG engine based on technical comfort
    3. Get optimized templates for their specific SSG/Snipcart combination
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        ssg_engine: str = "eleventy",  # Client configurable - not hardcoded!
        store_name: Optional[str] = None,
        currency: str = "USD",
        snipcart_mode: str = "live",  # "test" or "live"
        **kwargs
    ):
        # Validate that selected SSG engine is compatible with Snipcart
        # This validation is handled by BaseEcommerceStack

        super().__init__(
            scope, construct_id, client_id, domain,
            ecommerce_provider="snipcart",
            ssg_engine=ssg_engine,  # Pass through client choice
            store_name=store_name,
            currency=currency,
            **kwargs
        )

        self.snipcart_mode = snipcart_mode

        # Add Snipcart-specific infrastructure
        self._setup_snipcart_integration()
        self._setup_snipcart_webhooks()
        self._create_snipcart_parameters()

    def _setup_snipcart_integration(self) -> None:
        """Set up Snipcart specific infrastructure and configuration"""

        # Base Snipcart configuration
        snipcart_vars = {
            "SNIPCART_ENABLED": "true",
            "SNIPCART_VERSION": "3.7.1",
            "SNIPCART_MODE": self.snipcart_mode,
            "SNIPCART_CURRENCY": self.currency,
            "SNIPCART_STORE_NAME": self.store_name
        }

        # SSG-specific Snipcart configuration
        ssg_specific_vars = self._get_ssg_specific_snipcart_config()
        snipcart_vars.update(ssg_specific_vars)

        self.add_environment_variables(snipcart_vars)

    def _get_ssg_specific_snipcart_config(self) -> Dict[str, str]:
        """
        Get SSG-specific Snipcart configuration.

        This allows Snipcart to integrate optimally with different SSG engines
        while maintaining consistent e-commerce functionality.
        """
        ssg_engine = self.ssg_config.ssg_engine

        ssg_configs = {
            "eleventy": {
                "SNIPCART_TEMPLATES_PATH": "src/_includes/snipcart",
                "PRODUCT_DATA_PATH": "src/_data/products.json",
                "ELEVENTY_SNIPCART_INTEGRATION": "true",
                "BUILD_COMMAND_OVERRIDE": "npx @11ty/eleventy"
            },
            "astro": {
                "SNIPCART_COMPONENTS_PATH": "src/components/snipcart",
                "PRODUCT_DATA_PATH": "src/data/products.json",
                "ASTRO_SNIPCART_INTEGRATION": "true",
                "ASTRO_ECOMMERCE_ISLANDS": "true",
                "BUILD_COMMAND_OVERRIDE": "npm run build"
            },
            "hugo": {
                "SNIPCART_LAYOUTS_PATH": "layouts/snipcart",
                "PRODUCT_DATA_PATH": "data/products.yaml",
                "HUGO_SNIPCART_INTEGRATION": "true",
                "BUILD_COMMAND_OVERRIDE": "hugo --minify"
            },
            "gatsby": {
                "SNIPCART_COMPONENTS_PATH": "src/components/snipcart",
                "PRODUCT_GRAPHQL_TYPE": "SnipcartProduct",
                "GATSBY_SNIPCART_INTEGRATION": "true",
                "BUILD_COMMAND_OVERRIDE": "npm run build"
            }
        }

        return ssg_configs.get(ssg_engine, {})

    def _setup_snipcart_webhooks(self) -> None:
        """Set up Snipcart-specific webhook processing"""

        # Snipcart webhook processor (extends base webhook infrastructure)
        self.snipcart_webhook_processor = lambda_.Function(
            self,
            "SnipcartWebhookProcessor",
            function_name=f"{self.ssg_config.client_id}-snipcart-webhook-processor",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="snipcart_webhook.handler",
            code=lambda_.Code.from_asset("lambda/snipcart-webhook"),
            environment={
                "ORDERS_TABLE": self.orders_table.table_name,
                "SNIPCART_MODE": self.snipcart_mode,
                "STORE_NAME": self.store_name,
                "SSG_ENGINE": self.ssg_config.ssg_engine,
                "NOTIFICATION_FUNCTION": self.notification_processor.function_name
            }
        )

        # Grant permissions
        self.orders_table.grant_read_write_data(self.snipcart_webhook_processor)
        self.notification_processor.grant_invoke(self.snipcart_webhook_processor)

        # Add Snipcart webhook endpoint to API Gateway
        snipcart_resource = self.webhook_api.root.add_resource("snipcart")

        # Snipcart webhook integration
        snipcart_integration = lambda_.LambdaIntegration(
            self.snipcart_webhook_processor,
            request_templates={
                "application/json": '{"statusCode": "200"}'
            }
        )

        # Snipcart webhook endpoints
        snipcart_resource.add_method("POST", snipcart_integration)  # Order events

        # Add specific Snipcart event endpoints
        order_events = snipcart_resource.add_resource("order")
        order_events.add_method("POST", snipcart_integration)

        customer_events = snipcart_resource.add_resource("customer")
        customer_events.add_method("POST", snipcart_integration)

    def _create_snipcart_parameters(self) -> None:
        """Create CDK parameters for Snipcart configuration"""

        # Snipcart API keys (stored in Parameter Store)
        self.snipcart_api_key_param = CfnParameter(
            self,
            "SnipcartApiKey",
            type="String",
            description="Snipcart API key for live mode",
            no_echo=True,
            default=f"/snipcart/{self.ssg_config.client_id}/api-key"
        )

        self.snipcart_test_api_key_param = CfnParameter(
            self,
            "SnipcartTestApiKey",
            type="String",
            description="Snipcart API key for test mode",
            no_echo=True,
            default=f"/snipcart/{self.ssg_config.client_id}/test-api-key"
        )

        self.snipcart_webhook_secret_param = CfnParameter(
            self,
            "SnipcartWebhookSecret",
            type="String",
            description="Snipcart webhook secret for validation",
            no_echo=True,
            default=f"/snipcart/{self.ssg_config.client_id}/webhook-secret"
        )

        # Add parameter references to environment variables
        additional_vars = {
            "SNIPCART_API_KEY": self.snipcart_api_key_param.value_as_string,
            "SNIPCART_TEST_API_KEY": self.snipcart_test_api_key_param.value_as_string,
            "SNIPCART_WEBHOOK_SECRET": self.snipcart_webhook_secret_param.value_as_string
        }

        self.add_environment_variables(additional_vars)

    def get_snipcart_integration_guide(self) -> Dict[str, str]:
        """
        Get SSG-specific integration guide for Snipcart.

        This provides developers with clear instructions for integrating
        Snipcart with their chosen SSG engine.
        """
        ssg_engine = self.ssg_config.ssg_engine

        integration_guides = {
            "eleventy": {
                "setup_instructions": "Add Snipcart script to base template, configure data files",
                "template_location": "src/_includes/snipcart/",
                "data_format": "JSON",
                "build_integration": "Eleventy data cascade with Snipcart product data",
                "example_product": """
                {
                  "id": "product-1",
                  "name": "Example Product",
                  "price": 29.99,
                  "data-item-id": "product-1",
                  "data-item-price": "29.99",
                  "data-item-name": "Example Product"
                }
                """
            },
            "astro": {
                "setup_instructions": "Use Astro components for Snipcart integration, leverage islands",
                "template_location": "src/components/snipcart/",
                "data_format": "JSON",
                "build_integration": "Astro component islands for cart functionality",
                "example_product": """
                <SnipcartProduct
                  id="product-1"
                  name="Example Product"
                  price={29.99}
                  client:load
                />
                """
            },
            "hugo": {
                "setup_instructions": "Use Hugo partials and data files for Snipcart integration",
                "template_location": "layouts/snipcart/",
                "data_format": "YAML",
                "build_integration": "Hugo data templates with Snipcart product generation",
                "example_product": """
                - id: product-1
                  name: Example Product
                  price: 29.99
                  data_item_id: product-1
                  data_item_price: "29.99"
                  data_item_name: Example Product
                """
            },
            "gatsby": {
                "setup_instructions": "Use Gatsby GraphQL and React components for Snipcart",
                "template_location": "src/components/snipcart/",
                "data_format": "GraphQL",
                "build_integration": "GraphQL product queries with Snipcart React components",
                "example_product": """
                query SnipcartProducts {
                  allSnipcartProduct {
                    nodes {
                      id
                      name
                      price
                      dataItemId
                      dataItemPrice
                      dataItemName
                    }
                  }
                }
                """
            }
        }

        return integration_guides.get(ssg_engine, {})

    @property
    def snipcart_outputs(self) -> Dict[str, str]:
        """Snipcart-specific outputs for client integration"""
        base_outputs = self.ecommerce_outputs

        snipcart_outputs = {
            **base_outputs,
            "snipcart_mode": self.snipcart_mode,
            "snipcart_webhook_url": f"{self.webhook_api.url}snipcart",
            "snipcart_order_webhook_url": f"{self.webhook_api.url}snipcart/order",
            "snipcart_customer_webhook_url": f"{self.webhook_api.url}snipcart/customer",
            "integration_guide": str(self.get_snipcart_integration_guide()),
            "template_variant": self.ssg_config.template_variant,
            "ssg_engine_choice": self.ssg_config.ssg_engine
        }

        return snipcart_outputs