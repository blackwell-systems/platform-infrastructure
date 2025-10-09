"""
Tina CMS Dual-Mode Stack

Updated Tina CMS implementation demonstrating dual-mode integration support:
- Direct Mode: Traditional direct provider integration
- Event-Driven Mode: SNS + DynamoDB event composition architecture

Shows how to implement optional event-layer integration in existing stacks.
"""

from typing import Dict, Any, Optional
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from models.service_config import ClientServiceConfig, IntegrationMode
from shared.providers.cms.factory import CMSProviderFactory
from shared.composition.integration_layer import EventDrivenIntegrationLayer


class TinaCMSDualModeStack(BaseSSGStack):
    """
    Dual-Mode Tina CMS Stack Implementation

    Supports both integration modes:
    - Direct: Traditional provider integration (simple, lower latency)
    - Event-Driven: Compositional architecture (scalable, allows CMS + E-commerce)

    The integration mode is specified in the client configuration and affects
    how the stack handles content updates, webhooks, and cross-provider sync.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientServiceConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, client_config, **kwargs)

        # Validate configuration
        self._validate_tina_cms_config()

        # Initialize providers and integration
        self.cms_provider = self._initialize_cms_provider()
        self.integration_mode = client_config.service_integration.integration_mode

        # Create infrastructure based on integration mode
        if self.integration_mode == IntegrationMode.DIRECT:
            self._create_direct_mode_infrastructure()
        else:
            self._create_event_driven_infrastructure()

        # Create common infrastructure (both modes need these)
        self._create_common_infrastructure()

    def _validate_tina_cms_config(self) -> None:
        """Validate Tina CMS configuration"""
        service_config = self.client_config.service_integration

        if not service_config.cms_config:
            raise ValueError("Tina CMS tier requires cms_config")

        if service_config.cms_config.provider != "tina":
            raise ValueError(f"Expected Tina CMS provider, got {service_config.cms_config.provider}")

        # Validate Tina-specific settings
        settings = service_config.cms_config.settings
        required = ["repository", "repository_owner"]
        for setting in required:
            if not settings.get(setting):
                raise ValueError(f"Tina CMS requires '{setting}' in settings")

        # Validate SSG compatibility
        supported_engines = ["nextjs", "astro", "gatsby", "nuxt"]
        if service_config.ssg_engine not in supported_engines:
            raise ValueError(f"Tina CMS supports: {supported_engines}, got: {service_config.ssg_engine}")

    def _initialize_cms_provider(self):
        """Initialize CMS provider instance"""
        cms_config = self.client_config.service_integration.cms_config
        return CMSProviderFactory.create_provider(
            cms_config.provider,
            cms_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Simple webhook → Lambda → CodeBuild pipeline
        self.webhook_handler = self._create_direct_webhook_handler()
        self.build_trigger = self._create_direct_build_trigger()

        # Direct CMS integration
        self._create_tina_admin_api()
        self._create_tina_auth_integration()

        # Output direct mode endpoints
        CfnOutput(
            self,
            "CMSAdminUrl",
            value=f"https://{self.distribution.distribution_domain_name}/admin",
            description="Tina CMS admin interface URL"
        )

        CfnOutput(
            self,
            "IntegrationMode",
            value="direct",
            description="CMS integration mode"
        )

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Use existing integration layer
        self.integration_layer = EventDrivenIntegrationLayer(
            self,
            "IntegrationLayer",
            client_config=self.client_config
        )

        # Event-driven CMS integration
        self._create_event_driven_cms_integration()
        self._create_unified_content_api()

        # Connect CMS provider to event system
        self._connect_cms_to_event_system()

        # Output event-driven endpoints
        CfnOutput(
            self,
            "ContentEventsTopicArn",
            value=self.integration_layer.content_events_topic.topic_arn,
            description="SNS topic for content events"
        )

        CfnOutput(
            self,
            "IntegrationApiUrl",
            value=self.integration_layer.integration_api.url,
            description="Integration API endpoint"
        )

        CfnOutput(
            self,
            "IntegrationMode",
            value="event_driven",
            description="CMS integration mode"
        )

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_build_pipeline()
        self._create_monitoring()

        # Common outputs
        CfnOutput(
            self,
            "SiteUrl",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="Published site URL"
        )

    def _create_direct_webhook_handler(self) -> lambda_.Function:
        """Create webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "TinaWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="webhook_handler.main",
            code=lambda_.Code.from_inline("""
import json
import boto3

def main(event, context):
    '''Handle Tina CMS webhook in direct mode'''

    # Parse webhook payload
    body = json.loads(event['body'])

    # Trigger build directly
    codebuild = boto3.client('codebuild')

    response = codebuild.start_build(
        projectName=os.environ['BUILD_PROJECT_NAME']
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Build triggered', 'buildId': response['build']['id']})
    }
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-tina-build"
            },
            timeout=Duration.seconds(30)
        )

    def _create_direct_build_trigger(self) -> codebuild.Project:
        """Create build trigger for direct mode"""

        return codebuild.Project(
            self,
            "TinaDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-tina-build",
            source=codebuild.Source.git_hub(
                owner=self.cms_provider.settings["repository_owner"],
                repo=self.cms_provider.settings["repository"],
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH)
                ]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                compute_type=codebuild.ComputeType.SMALL
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_cms_integration(self) -> None:
        """Create event-driven CMS integration"""

        # CMS Event Processor
        self.cms_event_processor = lambda_.Function(
            self,
            "CMSEventProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="cms_event_processor.main",
            code=lambda_.Code.from_inline("""
import json
import boto3

def main(event, context):
    '''Process CMS events and publish to unified content system'''

    sns = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')

    # Parse CMS webhook
    cms_event = json.loads(event['body'])

    # Transform to unified content event
    unified_event = {
        'event_type': 'content_updated',
        'provider': 'tina',
        'content_id': cms_event.get('id'),
        'content_type': cms_event.get('content_type', 'unknown'),
        'timestamp': cms_event.get('updated_at'),
        'data': cms_event
    }

    # Store in unified content table
    table = dynamodb.Table(os.environ['CONTENT_TABLE_NAME'])
    table.put_item(Item=unified_event)

    # Publish event
    sns.publish(
        TopicArn=os.environ['CONTENT_EVENTS_TOPIC_ARN'],
        Message=json.dumps(unified_event),
        Subject=f"CMS Content Updated: {unified_event['content_id']}"
    )

    return {'statusCode': 200, 'body': json.dumps({'message': 'Event processed'})}
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn
            },
            timeout=Duration.seconds(30)
        )

        # Grant permissions
        self.integration_layer.content_events_topic.grant_publish(self.cms_event_processor)

    def _create_unified_content_api(self) -> None:
        """
        Unified content API is provided by the existing integration layer.
        This method is kept for consistency but delegates to the existing system.
        """
        # The integration layer already provides unified content access
        # No additional API needed - use integration_layer.integration_api
        pass

    def _connect_cms_to_event_system(self) -> None:
        """Connect CMS provider webhooks to event system"""

        # Create API Gateway for CMS webhooks
        webhook_api = apigateway.RestApi(
            self,
            "CMSWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-cms-webhooks"
        )

        # Add CMS webhook endpoint
        cms_resource = webhook_api.root.add_resource("cms")
        tina_resource = cms_resource.add_resource("tina")

        tina_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.cms_event_processor)
        )

        # Output webhook URL for Tina configuration
        CfnOutput(
            self,
            "TinaCMSWebhookUrl",
            value=f"{webhook_api.url}cms/tina",
            description="Webhook URL to configure in Tina CMS"
        )

    def _create_tina_admin_api(self) -> None:
        """Create Tina admin API (direct mode)"""
        # Implementation would create Tina admin interface resources
        pass

    def _create_tina_auth_integration(self) -> None:
        """Create Tina authentication integration (direct mode)"""
        # Implementation would set up GitHub OAuth for Tina
        pass

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Implementation would create S3 buckets for content and media
        pass

    def _create_build_pipeline(self) -> None:
        """Create build pipeline (both modes)"""
        # Implementation would create CodeBuild project for SSG compilation
        pass

    def _create_monitoring(self) -> None:
        """Create monitoring and logging (both modes)"""
        # Implementation would create CloudWatch dashboards and alarms
        pass

    def _get_direct_mode_buildspec(self) -> codebuild.BuildSpec:
        """Get buildspec for direct mode builds"""
        ssg_engine = self.client_config.service_integration.ssg_engine

        if ssg_engine == "nextjs":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": [
                            "npm run build",
                            "npm run export"
                        ]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "out"
                }
            })

        elif ssg_engine == "astro":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": ["npm run build"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "dist"
                }
            })

        else:  # gatsby
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": ["npm ci"]
                    },
                    "build": {
                        "commands": ["gatsby build"]
                    }
                },
                "artifacts": {
                    "files": ["**/*"],
                    "base-directory": "public"
                }
            })

    def _create_custom_infrastructure(self) -> None:
        """Required implementation from BaseSSGStack"""
        # Infrastructure creation is handled by mode-specific methods
        pass

    def get_integration_outputs(self) -> Dict[str, Any]:
        """Get integration-specific outputs"""
        outputs = {
            "integration_mode": self.integration_mode.value,
            "cms_provider": "tina",
            "ssg_engine": self.client_config.service_integration.ssg_engine
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            outputs.update({
                "supports_composition": True,
                "content_events_topic": self.integration_layer.content_events_topic.topic_arn,
                "integration_api_url": self.integration_layer.integration_api.url
            })
        else:
            outputs.update({
                "supports_composition": False,
                "direct_webhook_url": f"https://{self.distribution.distribution_domain_name}/webhook"
            })

        return outputs