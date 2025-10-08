"""
Snipcart E-commerce Provider

Concrete implementation of the EcommerceProvider interface for Snipcart.
Handles Snipcart-specific integration including webhook processing,
order notifications, and JavaScript snippet configuration.

Snipcart Details:
- JavaScript-based e-commerce solution
- Monthly cost: $29-99 based on transaction volume
- Transaction fee: 2.0% of sales
- Integration: JavaScript snippet + data attributes
- Features: Cart, checkout, inventory, digital products, subscriptions
- Setup complexity: Low (estimated 3 hours)
"""

from typing import Dict, Any, List
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ses as ses,
    aws_iam as iam,
    Duration,
)

from .base_provider import EcommerceProvider, EcommerceProviderConfig


class SnipcartProvider(EcommerceProvider):
    """
    Snipcart e-commerce provider implementation.

    Provides JavaScript-based e-commerce functionality with minimal
    backend requirements. Ideal for small businesses and simple stores.

    Key Features:
    - Client-side cart and checkout
    - Order webhook processing via Lambda
    - Email notifications via SES
    - Support for digital products and subscriptions
    - PCI-compliant payment processing
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize Snipcart provider with configuration validation"""
        super().__init__("snipcart", config)
        self.validate_configuration()

    def get_environment_variables(self) -> Dict[str, str]:
        """Get Snipcart-specific environment variables"""
        return {
            # Core Snipcart configuration
            "SNIPCART_API_KEY": "${SNIPCART_API_KEY}",  # CDK parameter
            "SNIPCART_ENV": self.config.get("mode", "live"),  # live or test

            # Store configuration
            "STORE_NAME": self.config.get("store_name", "Online Store"),
            "STORE_CURRENCY": self.config.get("currency", "USD"),

            # E-commerce optimizations
            "SITE_TYPE": "ecommerce",
            "ELEVENTY_PRODUCTION": "true",
            "NODE_ENV": "production",

            # Snipcart-specific features
            "SNIPCART_INCREMENTAL_BUILDS": "true",  # Faster product updates
            "SNIPCART_WEBHOOK_ENABLED": "true",
            "SNIPCART_GOOGLE_ANALYTICS": "true",  # Enable GA e-commerce tracking

            # Analytics integration
            "GOOGLE_ANALYTICS_ID": "${GOOGLE_ANALYTICS_ID}",  # CDK parameter
            "GOOGLE_ANALYTICS_ECOMMERCE": "true",
            "FACEBOOK_PIXEL_ID": "${FACEBOOK_PIXEL_ID}",  # CDK parameter
            "SNIPCART_CONVERSION_TRACKING": "true",

            # Performance monitoring
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "TRACK_CART_ABANDONMENT": "true"
        }

    def setup_infrastructure(self, stack) -> None:
        """Set up Snipcart-specific AWS infrastructure"""
        self._setup_order_notification_system(stack)
        self._setup_webhook_processing(stack)

    def _setup_order_notification_system(self, stack) -> None:
        """Set up SES for order email notifications"""
        # Create SES configuration set for order notifications
        self.notification_config = ses.CfnConfigurationSet(
            stack,
            "SnipcartNotificationConfigSet",
            name=f"{stack.ssg_config.client_id}-snipcart-notifications"
        )

    def _setup_webhook_processing(self, stack) -> None:
        """Set up Lambda function for processing Snipcart webhooks"""
        # Create Lambda function for Snipcart webhook processing
        self.order_processor = lambda_.Function(
            stack,
            "SnipcartOrderProcessor",
            function_name=f"{stack.ssg_config.client_id}-snipcart-order-processor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="snipcart_webhook.handler",
            code=lambda_.Code.from_inline(self._get_webhook_lambda_code()),
            environment={
                "NOTIFICATION_FROM_EMAIL": f"orders@{self._get_root_domain(stack)}",
                "NOTIFICATION_TO_EMAIL": "${NOTIFICATION_EMAIL}",  # CDK parameter
                "STORE_NAME": self.config.get("store_name", "Online Store"),
                "SNIPCART_WEBHOOK_SECRET": "${SNIPCART_WEBHOOK_SECRET}",  # CDK parameter
            },
            timeout=Duration.seconds(30),
            memory_size=256
        )

        # Grant SES permissions to the Lambda function
        self.order_processor.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ses:SendEmail",
                    "ses:SendRawEmail"
                ],
                resources=[
                    f"arn:aws:ses:{stack.region}:{stack.account}:identity/*"
                ]
            )
        )

        # Store the Lambda function reference for stack access
        stack.snipcart_order_processor = self.order_processor

    def _get_webhook_lambda_code(self) -> str:
        """Get the Lambda function code for Snipcart webhook processing"""
        return """
import json
import boto3
import os
import hmac
import hashlib
from datetime import datetime

def handler(event, context):
    '''
    Process Snipcart webhook for order notifications.

    Snipcart sends webhook data when orders are placed, updated, or completed.
    This function validates the webhook signature and sends email notifications.
    '''

    try:
        # Validate webhook signature (security)
        signature = event.get('headers', {}).get('x-snipcart-signature', '')
        body = event.get('body', '')

        if not _validate_signature(body, signature):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid webhook signature'})
            }

        # Parse Snipcart webhook data
        webhook_data = json.loads(body)
        order_data = webhook_data.get('content', {})
        event_name = webhook_data.get('eventName', 'unknown')

        # Extract order information
        order_id = order_data.get('token', 'unknown')
        customer_email = order_data.get('email', 'unknown')
        total_price = order_data.get('finalGrandTotal', 0)
        currency = order_data.get('currency', 'USD')

        # Send notification email using SES
        _send_order_notification(order_id, customer_email, total_price, currency, event_name)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Order notification processed successfully'})
        }

    except Exception as e:
        print(f"Error processing Snipcart webhook: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Failed to process webhook'})
        }

def _validate_signature(body, signature):
    '''Validate Snipcart webhook signature for security'''
    webhook_secret = os.environ.get('SNIPCART_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return True  # Skip validation if no secret configured

    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

def _send_order_notification(order_id, customer_email, total_price, currency, event_name):
    '''Send order notification email via SES'''
    ses_client = boto3.client('ses')

    subject = f"New Order #{order_id} - {os.environ['STORE_NAME']}"
    body_text = f'''
New order received!

Order Details:
- Order ID: {order_id}
- Customer: {customer_email}
- Total: {currency} {total_price:.2f}
- Event: {event_name}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check your Snipcart dashboard for complete order details:
https://app.snipcart.com/dashboard/orders

Thank you for using Snipcart!
    '''

    ses_client.send_email(
        Source=os.environ['NOTIFICATION_FROM_EMAIL'],
        Destination={'ToAddresses': [os.environ['NOTIFICATION_TO_EMAIL']]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body_text}}
        }
    )
        """

    def _get_root_domain(self, stack) -> str:
        """Extract root domain from stack configuration"""
        domain_parts = stack.ssg_config.domain.split('.')
        if len(domain_parts) >= 2:
            return '.'.join(domain_parts[-2:])
        return stack.ssg_config.domain

    def get_configuration_metadata(self) -> Dict[str, Any]:
        """Get Snipcart configuration metadata"""
        return {
            "provider": "snipcart",
            "integration_method": "javascript_snippet",
            "setup_complexity": "low",
            "estimated_setup_hours": 3.0,

            # Cost structure
            "monthly_cost_range": [29, 99],  # Snipcart subscription tiers
            "transaction_fee_percent": 2.0,
            "additional_aws_costs": "$10-25/month",  # Lambda + SES

            # Features
            "features": ["cart", "checkout", "inventory", "digital_products", "subscriptions"],
            "payment_methods": ["credit_cards", "paypal", "apple_pay", "google_pay"],
            "supported_currencies": ["USD", "CAD", "EUR", "GBP", "AUD", "CHF", "DKK", "NOK", "SEK"],

            # Technical capabilities
            "supports_webhooks": True,
            "supports_subscriptions": True,
            "supports_digital_products": True,
            "pci_compliant": True,
            "ssl_required": True,

            # Integration requirements
            "required_environment_vars": [
                "SNIPCART_API_KEY",  # From Snipcart dashboard
                "NOTIFICATION_EMAIL",  # For order notifications
                "SNIPCART_WEBHOOK_SECRET",  # For webhook security
            ],
            "optional_environment_vars": [
                "GOOGLE_ANALYTICS_ID",  # For e-commerce tracking
                "FACEBOOK_PIXEL_ID",  # For conversion tracking
            ],

            # Documentation and resources
            "documentation_url": "https://docs.snipcart.com/v3/",
            "dashboard_url": "https://app.snipcart.com/dashboard",
            "template_repo": "https://github.com/your-templates/eleventy-snipcart-store",
            "demo_url": "https://demo.yourservices.com/eleventy-snipcart"
        }

    def get_required_aws_services(self) -> List[str]:
        """Get AWS services required by Snipcart integration"""
        return ["Lambda", "SES"]  # For order processing and notifications

    def validate_configuration(self) -> bool:
        """Validate Snipcart provider configuration"""
        # Validate required configuration fields
        required_fields = []  # Snipcart is very flexible, minimal requirements

        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required Snipcart configuration: {field}")

        # Validate currency if specified
        currency = self.config.get("currency", "USD")
        supported_currencies = self.get_configuration_metadata()["supported_currencies"]
        if currency not in supported_currencies:
            raise ValueError(f"Unsupported currency '{currency}'. Supported: {supported_currencies}")

        # Validate mode
        mode = self.config.get("mode", "live")
        if mode not in ["live", "test"]:
            raise ValueError(f"Invalid Snipcart mode '{mode}'. Must be 'live' or 'test'")

        return True

    def get_webhook_endpoint_name(self) -> str:
        """Get Snipcart webhook endpoint name"""
        return "snipcart-webhook"

    def get_client_integration_guide(self) -> Dict[str, Any]:
        """
        Get step-by-step integration guide for clients.

        Returns detailed instructions for setting up Snipcart
        with this infrastructure stack.
        """
        return {
            "title": "Snipcart Integration Setup Guide",
            "steps": [
                {
                    "step": 1,
                    "title": "Create Snipcart Account",
                    "description": "Sign up at https://app.snipcart.com/register",
                    "action": "Create account and verify email"
                },
                {
                    "step": 2,
                    "title": "Get API Keys",
                    "description": "Copy your API keys from the Snipcart dashboard",
                    "action": "Navigate to Account > API Keys",
                    "required_values": ["Public API Key", "Secret API Key"]
                },
                {
                    "step": 3,
                    "title": "Configure CDK Parameters",
                    "description": "Set the required CDK parameters for deployment",
                    "parameters": {
                        "SNIPCART_API_KEY": "Your Snipcart public API key",
                        "NOTIFICATION_EMAIL": "Email for order notifications",
                        "SNIPCART_WEBHOOK_SECRET": "Optional webhook secret for security"
                    }
                },
                {
                    "step": 4,
                    "title": "Deploy Infrastructure",
                    "description": "Deploy the CDK stack with Snipcart integration",
                    "action": "Run: cdk deploy YourStackName"
                },
                {
                    "step": 5,
                    "title": "Configure Webhooks",
                    "description": "Set up webhooks in Snipcart dashboard",
                    "webhook_url": "https://your-domain.com/api/snipcart-webhook",
                    "events": ["order.completed", "order.status.changed"]
                }
            ],
            "testing": {
                "test_mode": "Set mode: 'test' in configuration",
                "test_card": "4242 4242 4242 4242 (Visa)",
                "verification": "Place test order and verify email notification"
            },
            "costs": {
                "setup_fee": "$0",
                "monthly_minimum": "$29",
                "transaction_fee": "2.0%",
                "aws_costs": "$10-25/month"
            }
        }