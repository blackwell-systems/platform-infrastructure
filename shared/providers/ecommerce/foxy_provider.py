"""
Foxy.io E-commerce Provider

Concrete implementation of the EcommerceProvider interface for Foxy.io.
Handles Foxy.io-specific integration including webhook processing,
order notifications, subscription management, and API configuration.

Foxy.io Details:
- API-based e-commerce solution with hosted cart and checkout
- Monthly cost: $75-300 based on transaction volume and features
- Transaction fee: 1.5% of sales
- Integration: JavaScript + webhook API
- Features: Cart, checkout, inventory, subscriptions, customer portal, advanced shipping
- Setup complexity: High (estimated 6 hours)
"""

from typing import Dict, Any, List
from aws_cdk import (
    aws_lambda as lambda_,
    aws_ses as ses,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Duration,
)

from .base_provider import EcommerceProvider, EcommerceProviderConfig


class FoxyProvider(EcommerceProvider):
    """
    Foxy.io e-commerce provider implementation.

    Provides API-based e-commerce functionality with advanced features
    for growing businesses and complex e-commerce requirements.

    Key Features:
    - Hosted cart and checkout with API integration
    - Advanced subscription management
    - Customer portal and account management
    - Multi-currency and international shipping
    - Advanced webhook processing via Lambda
    - Email notifications via SES
    - PCI-compliant payment processing
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize Foxy.io provider with configuration validation"""
        super().__init__("foxy", config)
        self.validate_configuration()

    def get_environment_variables(self) -> Dict[str, str]:
        """Get Foxy.io-specific environment variables"""
        return {
            # Core Foxy.io configuration
            "FOXY_STORE_DOMAIN": "${FOXY_STORE_DOMAIN}",  # CDK parameter
            "FOXY_API_KEY": "${FOXY_API_KEY}",  # CDK parameter
            "FOXY_CLIENT_SECRET": "${FOXY_CLIENT_SECRET}",  # CDK parameter

            # Store configuration
            "STORE_NAME": self.config.get("store_name", "Online Store"),
            "STORE_CURRENCY": self.config.get("currency", "USD"),
            "FOXY_ENV": self.config.get("mode", "live"),  # live or sandbox

            # Advanced features
            "FOXY_SUBSCRIPTIONS_ENABLED": str(self.config.get("subscription_products", False)).lower(),
            "FOXY_CUSTOMER_PORTAL_ENABLED": str(self.config.get("customer_accounts", True)).lower(),
            "FOXY_MULTI_CURRENCY_ENABLED": str(self.config.get("multi_currency", False)).lower(),

            # E-commerce optimizations
            "SITE_TYPE": "ecommerce",
            "NODE_ENV": "production",
            "FOXY_PRODUCTION": "true",

            # Foxy.io-specific features
            "FOXY_WEBHOOK_ENABLED": "true",
            "FOXY_CART_INTEGRATION": "advanced",  # Advanced cart features
            "FOXY_CHECKOUT_TYPE": "hosted",  # Hosted checkout

            # Analytics integration
            "GOOGLE_ANALYTICS_ID": "${GOOGLE_ANALYTICS_ID}",  # CDK parameter
            "GOOGLE_ANALYTICS_ECOMMERCE": "true",
            "FACEBOOK_PIXEL_ID": "${FACEBOOK_PIXEL_ID}",  # CDK parameter
            "FOXY_CONVERSION_TRACKING": "true",

            # Performance monitoring
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "TRACK_CART_ABANDONMENT": "true",
            "FOXY_ADVANCED_ANALYTICS": "true",

            # Tax and shipping
            "FOXY_TAX_CALCULATION": str(self.config.get("tax_calculation", False)).lower(),
            "FOXY_ADVANCED_SHIPPING": str(self.config.get("advanced_shipping", True)).lower(),
        }

    def setup_infrastructure(self, stack) -> None:
        """Set up Foxy.io-specific AWS infrastructure"""
        self._setup_order_notification_system(stack)
        self._setup_webhook_processing(stack)
        self._setup_api_gateway(stack)

    def _setup_order_notification_system(self, stack) -> None:
        """Set up SES for order email notifications"""
        # Create SES configuration set for order notifications
        self.notification_config = ses.CfnConfigurationSet(
            stack,
            "FoxyNotificationConfigSet",
            name=f"{stack.ssg_config.client_id}-foxy-notifications"
        )

    def _setup_webhook_processing(self, stack) -> None:
        """Set up Lambda function for processing Foxy.io webhooks"""
        # Create Lambda function for Foxy.io webhook processing
        self.order_processor = lambda_.Function(
            stack,
            "FoxyOrderProcessor",
            function_name=f"{stack.ssg_config.client_id}-foxy-order-processor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="foxy_webhook.handler",
            code=lambda_.Code.from_inline(self._get_webhook_lambda_code()),
            environment={
                "NOTIFICATION_FROM_EMAIL": f"orders@{self._get_root_domain(stack)}",
                "NOTIFICATION_TO_EMAIL": "${NOTIFICATION_EMAIL}",  # CDK parameter
                "STORE_NAME": self.config.get("store_name", "Online Store"),
                "FOXY_WEBHOOK_SECRET": "${FOXY_WEBHOOK_SECRET}",  # CDK parameter
                "FOXY_API_KEY": "${FOXY_API_KEY}",  # CDK parameter
            },
            timeout=Duration.seconds(60),  # Longer timeout for complex processing
            memory_size=512  # More memory for advanced features
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
        stack.foxy_order_processor = self.order_processor

    def _setup_api_gateway(self, stack) -> None:
        """Set up API Gateway for Foxy.io webhook endpoints"""
        # Create API Gateway for webhook endpoints
        self.webhook_api = apigateway.RestApi(
            stack,
            "FoxyWebhookAPI",
            rest_api_name=f"{stack.ssg_config.client_id}-foxy-webhooks",
            description="API Gateway for Foxy.io webhook processing"
        )

        # Create webhook resource and method
        webhook_resource = self.webhook_api.root.add_resource("foxy-webhook")
        webhook_integration = apigateway.LambdaIntegration(self.order_processor)
        webhook_resource.add_method("POST", webhook_integration)

        # Store API Gateway reference for stack access
        stack.foxy_webhook_api = self.webhook_api

    def _get_webhook_lambda_code(self) -> str:
        """Get the Lambda function code for Foxy.io webhook processing"""
        return """
import json
import boto3
import os
import hmac
import hashlib
import requests
from datetime import datetime

def handler(event, context):
    '''
    Process Foxy.io webhook for order and subscription notifications.

    Foxy.io sends webhook data for orders, subscriptions, customer updates,
    and other events. This function validates the webhook signature and
    processes the event accordingly.
    '''

    try:
        # Validate webhook signature (security)
        signature = event.get('headers', {}).get('foxy-webhook-signature', '')
        body = event.get('body', '')

        if not _validate_signature(body, signature):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid webhook signature'})
            }

        # Parse Foxy.io webhook data
        webhook_data = json.loads(body)

        # Extract event information
        resource_type = webhook_data.get('_embedded', {}).get('resource_type', 'unknown')
        event_resource = webhook_data.get('_embedded', {}).get('resource', {})

        # Process different types of events
        if resource_type == 'transaction':
            _process_order_event(event_resource)
        elif resource_type == 'subscription':
            _process_subscription_event(event_resource)
        elif resource_type == 'customer':
            _process_customer_event(event_resource)
        else:
            print(f"Unhandled resource type: {resource_type}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Webhook processed successfully'})
        }

    except Exception as e:
        print(f"Error processing Foxy.io webhook: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Failed to process webhook'})
        }

def _validate_signature(body, signature):
    '''Validate Foxy.io webhook signature for security'''
    webhook_secret = os.environ.get('FOXY_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return True  # Skip validation if no secret configured

    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

def _process_order_event(transaction_data):
    '''Process order/transaction events'''
    transaction_id = transaction_data.get('id', 'unknown')
    customer_email = transaction_data.get('customer_email', 'unknown')
    total_order = transaction_data.get('total_order', 0)
    currency_code = transaction_data.get('currency_code', 'USD')

    # Send order notification
    _send_order_notification(transaction_id, customer_email, total_order, currency_code, 'order')

def _process_subscription_event(subscription_data):
    '''Process subscription events'''
    subscription_id = subscription_data.get('id', 'unknown')
    customer_email = subscription_data.get('customer_email', 'unknown')
    next_transaction_date = subscription_data.get('next_transaction_date', 'unknown')

    # Send subscription notification
    _send_subscription_notification(subscription_id, customer_email, next_transaction_date)

def _process_customer_event(customer_data):
    '''Process customer events (account creation, updates, etc.)'''
    customer_id = customer_data.get('id', 'unknown')
    customer_email = customer_data.get('email', 'unknown')

    print(f"Customer event processed for customer {customer_id}: {customer_email}")

def _send_order_notification(order_id, customer_email, total_price, currency, event_type):
    '''Send order notification email via SES'''
    ses_client = boto3.client('ses')

    subject = f"New Order #{order_id} - {os.environ['STORE_NAME']}"
    body_text = f'''
New order received via Foxy.io!

Order Details:
- Order ID: {order_id}
- Customer: {customer_email}
- Total: {currency} {total_price:.2f}
- Event Type: {event_type}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check your Foxy.io admin panel for complete order details.

Advanced features active:
- Customer portal enabled
- Subscription management available
- Multi-currency support configured

Thank you for using Foxy.io!
    '''

    ses_client.send_email(
        Source=os.environ['NOTIFICATION_FROM_EMAIL'],
        Destination={'ToAddresses': [os.environ['NOTIFICATION_TO_EMAIL']]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body_text}}
        }
    )

def _send_subscription_notification(subscription_id, customer_email, next_date):
    '''Send subscription notification email via SES'''
    ses_client = boto3.client('ses')

    subject = f"Subscription Update #{subscription_id} - {os.environ['STORE_NAME']}"
    body_text = f'''
Subscription event received via Foxy.io!

Subscription Details:
- Subscription ID: {subscription_id}
- Customer: {customer_email}
- Next Transaction: {next_date}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check your Foxy.io admin panel for complete subscription details.

Thank you for using Foxy.io advanced features!
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
        """Get Foxy.io configuration metadata"""
        return {
            "provider": "foxy",
            "integration_method": "javascript_api",
            "setup_complexity": "high",
            "estimated_setup_hours": 6.0,

            # Cost structure
            "monthly_cost_range": [75, 300],  # Foxy.io subscription tiers
            "transaction_fee_percent": 1.5,
            "additional_aws_costs": "$20-40/month",  # Lambda + SES + API Gateway

            # Features
            "features": [
                "cart", "checkout", "inventory", "subscriptions", "customer_portal",
                "multi_currency", "advanced_shipping", "tax_calculation", "webhooks"
            ],
            "payment_methods": [
                "credit_cards", "paypal", "apple_pay", "google_pay", "stripe", "square"
            ],
            "supported_currencies": [
                "USD", "CAD", "EUR", "GBP", "AUD", "CHF", "DKK", "NOK", "SEK",
                "JPY", "NZD", "PLN", "CZK", "HUF", "BGN", "RON", "HRK"
            ],

            # Technical capabilities
            "supports_webhooks": True,
            "supports_subscriptions": True,
            "supports_digital_products": True,
            "supports_customer_portal": True,
            "supports_multi_currency": True,
            "supports_advanced_shipping": True,
            "supports_tax_calculation": True,
            "pci_compliant": True,
            "ssl_required": True,
            "api_access": True,

            # Integration requirements
            "required_environment_vars": [
                "FOXY_STORE_DOMAIN",  # From Foxy.io dashboard
                "FOXY_API_KEY",  # From Foxy.io dashboard
                "FOXY_CLIENT_SECRET",  # From Foxy.io dashboard
                "NOTIFICATION_EMAIL",  # For order notifications
                "FOXY_WEBHOOK_SECRET",  # For webhook security
            ],
            "optional_environment_vars": [
                "GOOGLE_ANALYTICS_ID",  # For e-commerce tracking
                "FACEBOOK_PIXEL_ID",  # For conversion tracking
            ],

            # Documentation and resources
            "documentation_url": "https://wiki.foxycart.com/",
            "api_documentation": "https://api.foxycart.com/docs",
            "dashboard_url": "https://admin.foxycart.com/",
            "template_repo": "https://github.com/your-templates/astro-foxy-store",
            "demo_url": "https://demo.yourservices.com/astro-foxy"
        }

    def get_required_aws_services(self) -> List[str]:
        """Get AWS services required by Foxy.io integration"""
        return ["Lambda", "SES", "API Gateway"]  # More services for advanced features

    def validate_configuration(self) -> bool:
        """Validate Foxy.io provider configuration"""
        # Validate required configuration fields for advanced features
        if self.config.get("subscription_products", False):
            # Additional validation for subscription features
            pass

        if self.config.get("multi_currency", False):
            # Validate currency settings
            currency = self.config.get("currency", "USD")
            supported_currencies = self.get_configuration_metadata()["supported_currencies"]
            if currency not in supported_currencies:
                raise ValueError(f"Unsupported currency '{currency}'. Supported: {supported_currencies}")

        # Validate mode
        mode = self.config.get("mode", "live")
        if mode not in ["live", "sandbox"]:
            raise ValueError(f"Invalid Foxy.io mode '{mode}'. Must be 'live' or 'sandbox'")

        return True

    def get_webhook_endpoint_name(self) -> str:
        """Get Foxy.io webhook endpoint name"""
        return "foxy-webhook"

    def get_client_integration_guide(self) -> Dict[str, Any]:
        """
        Get step-by-step integration guide for clients.

        Returns detailed instructions for setting up Foxy.io
        with this infrastructure stack.
        """
        return {
            "title": "Foxy.io Advanced E-commerce Integration Setup Guide",
            "steps": [
                {
                    "step": 1,
                    "title": "Create Foxy.io Account",
                    "description": "Sign up at https://www.foxycart.com/signup",
                    "action": "Create account and choose subscription plan"
                },
                {
                    "step": 2,
                    "title": "Configure Store Settings",
                    "description": "Set up your store domain and basic settings",
                    "action": "Navigate to Store Configuration in admin panel",
                    "required_values": ["Store Domain", "Currency", "Language"]
                },
                {
                    "step": 3,
                    "title": "Get API Credentials",
                    "description": "Generate API keys from the Foxy.io dashboard",
                    "action": "Navigate to Integrations > API",
                    "required_values": ["Client ID", "Client Secret", "Refresh Token"]
                },
                {
                    "step": 4,
                    "title": "Configure CDK Parameters",
                    "description": "Set the required CDK parameters for deployment",
                    "parameters": {
                        "FOXY_STORE_DOMAIN": "Your Foxy.io store domain",
                        "FOXY_API_KEY": "Your Foxy.io API key",
                        "FOXY_CLIENT_SECRET": "Your Foxy.io client secret",
                        "NOTIFICATION_EMAIL": "Email for order notifications",
                        "FOXY_WEBHOOK_SECRET": "Webhook secret for security"
                    }
                },
                {
                    "step": 5,
                    "title": "Deploy Infrastructure",
                    "description": "Deploy the CDK stack with Foxy.io integration",
                    "action": "Run: cdk deploy YourStackName"
                },
                {
                    "step": 6,
                    "title": "Configure Webhooks",
                    "description": "Set up webhooks in Foxy.io admin panel",
                    "webhook_url": "https://your-domain.com/api/foxy-webhook",
                    "events": [
                        "transaction/created",
                        "transaction/updated",
                        "subscription/created",
                        "subscription/updated",
                        "customer/created"
                    ]
                },
                {
                    "step": 7,
                    "title": "Enable Advanced Features",
                    "description": "Configure subscriptions, customer portal, multi-currency",
                    "action": "Enable features in Foxy.io admin panel as needed"
                }
            ],
            "testing": {
                "test_mode": "Set mode: 'sandbox' in configuration",
                "test_card": "4242 4242 4242 4242 (Visa)",
                "verification": "Place test order and verify webhook processing and email notifications"
            },
            "costs": {
                "setup_fee": "$0",
                "monthly_minimum": "$75",
                "transaction_fee": "1.5%",
                "aws_costs": "$20-40/month",
                "advanced_features": "Included in monthly fee"
            },
            "advanced_features": {
                "subscriptions": "Recurring billing with customer portal",
                "multi_currency": "Support for 17+ currencies",
                "customer_portal": "Self-service account management",
                "advanced_shipping": "Complex shipping rules and zones",
                "tax_calculation": "Automated tax calculation",
                "api_access": "Full REST API for custom integrations"
            }
        }