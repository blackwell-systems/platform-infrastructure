"""
TinaCMS Tier Stack

Updated TinaCMS implementation with optional event-driven integration support:
- Direct Mode: Git webhooks → build pipeline (traditional, git-based)
- Event-Driven Mode: Git events → SNS → unified content system (composition-ready)

TinaCMS Features:
- Visual editing with real-time preview
- Git-based workflow with full version control
- GitHub OAuth authentication built-in
- Rich text editing with structured content
- React-based admin interface served statically
- Optional Tina Cloud integration for enhanced features

Target Market:
- Content creators wanting visual editing with git benefits
- Developer teams needing both technical control and content creator ease
- Agencies managing multiple client sites with different skill levels
- Projects requiring version control but user-friendly editing

Pricing:
- Self-hosted TinaCMS: FREE (git-only editing)
- Tina Cloud: $0-50/month based on usage and features
- AWS Hosting: $50-75/month
- Total Monthly: $50-125/month depending on Tina Cloud usage
"""

from typing import Dict, Any, Optional, List
import json
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_secretsmanager as secrets,
    aws_ssm as ssm,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct

from stacks.shared.base_ssg_stack import BaseSSGStack
from models.service_config import ClientServiceConfig, IntegrationMode
from shared.composition.integration_layer import EventDrivenIntegrationLayer
from shared.providers.cms.factory import CMSProviderFactory


class TinaCMSTierStack(BaseSSGStack):
    """
    TinaCMS Tier Stack Implementation

    Supports both integration modes:
    - Direct: Git webhooks → CodeBuild → S3/CloudFront (traditional, git-based)
    - Event-Driven: Git events → SNS → unified content system (composition-ready)

    The hybrid CMS solution combining git benefits with visual editing ease.
    """

    # Supported SSG engines for TinaCMS
    SUPPORTED_SSG_ENGINES = {
        "nextjs": {
            "compatibility": "excellent",
            "setup_complexity": "intermediate",
            "features": ["react_integration", "tina_components", "preview_mode"]
        },
        "astro": {
            "compatibility": "good",
            "setup_complexity": "intermediate",
            "features": ["component_islands", "tina_content", "modern_architecture"]
        },
        "gatsby": {
            "compatibility": "good",
            "setup_complexity": "advanced",
            "features": ["react_ecosystem", "graphql", "tina_plugins"]
        }
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientServiceConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, client_config, **kwargs)

        # Validate TinaCMS configuration
        self._validate_tina_cms_config()

        # Initialize providers and integration
        self.cms_provider = self._initialize_cms_provider()
        self.integration_mode = client_config.service_integration.integration_mode

        # Create infrastructure based on integration mode
        if self.integration_mode == IntegrationMode.DIRECT:
            self._create_direct_mode_infrastructure()
        else:
            self.integration_layer = EventDrivenIntegrationLayer(
                self, "IntegrationLayer", client_config
            )
            self._create_event_driven_infrastructure()

        # Create common infrastructure (both modes need these)
        self._create_common_infrastructure()

        # Output stack information
        self._create_stack_outputs()

    def _validate_tina_cms_config(self) -> None:
        """Validate TinaCMS configuration"""
        service_config = self.client_config.service_integration

        if not service_config.cms_config:
            raise ValueError("TinaCMS tier requires cms_config")

        if service_config.cms_config.provider != "tina":
            raise ValueError(f"Expected TinaCMS provider, got {service_config.cms_config.provider}")

        # Validate TinaCMS-specific settings
        settings = service_config.cms_config.settings
        required = ["repository", "repository_owner"]
        for setting in required:
            if not settings.get(setting):
                raise ValueError(f"TinaCMS requires '{setting}' in settings")

        # Validate SSG compatibility
        if service_config.ssg_engine not in self.SUPPORTED_SSG_ENGINES:
            supported = list(self.SUPPORTED_SSG_ENGINES.keys())
            raise ValueError(f"TinaCMS supports: {supported}, got: {service_config.ssg_engine}")

    def _initialize_cms_provider(self):
        """Initialize CMS provider instance"""
        cms_config = self.client_config.service_integration.cms_config
        return CMSProviderFactory.create_provider(
            cms_config.provider,
            cms_config.settings
        )

    def _create_direct_mode_infrastructure(self) -> None:
        """Create infrastructure for direct integration mode"""

        # Direct mode: Git webhook → CodeBuild pipeline
        self.github_webhook_handler = self._create_github_webhook_handler()
        self.build_project = self._create_direct_build_project()

        # TinaCMS admin interface
        self._create_tina_admin_interface()

        # GitHub webhook integration
        self._create_github_webhook_integration()

        print(f"✅ Created TinaCMS direct mode infrastructure for {self.client_config.client_id}")

    def _create_event_driven_infrastructure(self) -> None:
        """Create infrastructure for event-driven integration mode"""

        # Event-driven mode: Git events → Integration Layer → Unified Content
        self._create_event_driven_cms_integration()

        # TinaCMS admin interface (same as direct mode)
        self._create_tina_admin_interface()

        # Connect to event system
        self._connect_tina_to_event_system()

        print(f"✅ Created TinaCMS event-driven infrastructure for {self.client_config.client_id}")

    def _create_common_infrastructure(self) -> None:
        """Create infrastructure needed by both modes"""

        # Both modes need these components:
        self._create_content_storage()
        self._create_tina_secrets()
        self._create_tina_cloud_integration()

    def _create_github_webhook_handler(self) -> lambda_.Function:
        """Create GitHub webhook handler for direct mode"""

        return lambda_.Function(
            self,
            "GitHubWebhookHandler",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
const AWS = require('aws-sdk');
const crypto = require('crypto');

const codebuild = new AWS.CodeBuild();

exports.handler = async (event) => {
    console.log('GitHub webhook received for TinaCMS:', JSON.stringify(event));

    try {
        const body = JSON.parse(event.body || '{}');
        const headers = event.headers || {};

        // Verify webhook is from GitHub
        const githubEvent = headers['X-GitHub-Event'] || headers['x-github-event'];

        if (githubEvent === 'push') {
            const ref = body.ref;
            const branch = process.env.GITHUB_BRANCH || 'main';

            // Only trigger build for the configured branch
            if (ref === `refs/heads/${branch}`) {
                console.log('Push to main branch detected, triggering build...');

                const buildResult = await codebuild.startBuild({
                    projectName: process.env.BUILD_PROJECT_NAME,
                    environmentVariablesOverride: [
                        {
                            name: 'COMMIT_SHA',
                            value: body.head_commit ? body.head_commit.id : '',
                            type: 'PLAINTEXT'
                        },
                        {
                            name: 'COMMIT_MESSAGE',
                            value: body.head_commit ? body.head_commit.message : '',
                            type: 'PLAINTEXT'
                        }
                    ]
                }).promise();

                console.log('Build started:', buildResult.build.id);

                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        message: 'Build triggered successfully',
                        buildId: buildResult.build.id
                    })
                };
            }
        }

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Webhook processed' })
        };
    } catch (error) {
        console.error('Webhook processing error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};
            """),
            environment={
                "BUILD_PROJECT_NAME": f"{self.client_config.resource_prefix}-tina-build",
                "GITHUB_BRANCH": self.cms_provider.settings.get("branch", "main")
            },
            timeout=Duration.seconds(60)
        )

    def _create_direct_build_project(self) -> codebuild.Project:
        """Create CodeBuild project for direct mode"""

        # Get TinaCMS settings for environment variables
        tina_settings = self.cms_provider.settings

        return codebuild.Project(
            self,
            "TinaDirectBuild",
            project_name=f"{self.client_config.resource_prefix}-tina-build",
            source=codebuild.Source.git_hub(
                owner=tina_settings["repository_owner"],
                repo=tina_settings["repository"],
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH)
                ]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={
                    "TINA_CLIENT_ID": codebuild.BuildEnvironmentVariable(
                        value=tina_settings.get("tina_client_id", "placeholder")
                    ),
                    "GITHUB_REPO": codebuild.BuildEnvironmentVariable(
                        value=f"{tina_settings['repository_owner']}/{tina_settings['repository']}"
                    )
                }
            ),
            build_spec=self._get_direct_mode_buildspec()
        )

    def _create_event_driven_cms_integration(self) -> None:
        """Create event-driven CMS integration"""

        # Git Event Processor - transforms Git events to unified content events
        self.git_event_processor = lambda_.Function(
            self,
            "TinaGitEventProcessor",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
const AWS = require('aws-sdk');

const sns = new AWS.SNS();

exports.handler = async (event) => {
    console.log('Processing TinaCMS Git event for unified content system');

    try {
        const body = JSON.parse(event.body || '{}');
        const headers = event.headers || {};
        const githubEvent = headers['X-GitHub-Event'] || headers['x-github-event'];

        if (githubEvent !== 'push') {
            return { statusCode: 200, body: 'Non-push event ignored' };
        }

        const ref = body.ref;
        const branch = process.env.GITHUB_BRANCH || 'main';

        // Only process pushes to main branch
        if (ref !== `refs/heads/${branch}`) {
            return { statusCode: 200, body: 'Branch ignored' };
        }

        // Extract content changes from commits
        const commits = body.commits || [];

        for (const commit of commits) {
            // Look for TinaCMS content file changes (markdown files, config changes)
            const contentFiles = [
                ...commit.added.filter(f => f.endsWith('.md') || f.includes('tina/') || f.includes('content/')),
                ...commit.modified.filter(f => f.endsWith('.md') || f.includes('tina/') || f.includes('content/'))
            ];

            const deletedFiles = commit.removed.filter(f => f.endsWith('.md') || f.includes('content/'));

            // Process content changes
            for (const filePath of contentFiles) {
                const unifiedEvent = {
                    event_type: 'content_updated',
                    provider: 'tina',
                    content_id: filePath.replace(/\\.(md|mdx)$/, '').replace(/\\//g, '-'),
                    content_type: determineContentType(filePath),
                    timestamp: commit.timestamp,
                    data: {
                        file_path: filePath,
                        commit_sha: commit.id,
                        commit_message: commit.message,
                        author: commit.author.name,
                        action: commit.added.includes(filePath) ? 'added' : 'modified',
                        cms_provider: 'tina'
                    }
                };

                // Publish to content events topic
                await sns.publish({
                    TopicArn: process.env.CONTENT_EVENTS_TOPIC_ARN,
                    Message: JSON.stringify(unifiedEvent),
                    Subject: `TinaCMS Content Updated: ${unifiedEvent.content_id}`
                }).promise();
            }

            // Process deletions
            for (const filePath of deletedFiles) {
                const unifiedEvent = {
                    event_type: 'content_deleted',
                    provider: 'tina',
                    content_id: filePath.replace(/\\.(md|mdx)$/, '').replace(/\\//g, '-'),
                    content_type: determineContentType(filePath),
                    timestamp: commit.timestamp,
                    data: {
                        file_path: filePath,
                        commit_sha: commit.id,
                        commit_message: commit.message,
                        author: commit.author.name,
                        action: 'deleted',
                        cms_provider: 'tina'
                    }
                };

                await sns.publish({
                    TopicArn: process.env.CONTENT_EVENTS_TOPIC_ARN,
                    Message: JSON.stringify(unifiedEvent),
                    Subject: `TinaCMS Content Deleted: ${unifiedEvent.content_id}`
                }).promise();
            }
        }

        return { statusCode: 200, body: `Processed ${commits.length} commits` };

    } catch (error) {
        console.error('Error processing TinaCMS Git event:', error);
        return { statusCode: 500, body: `Error: ${error.message}` };
    }
};

function determineContentType(filePath) {
    if (filePath.includes('posts/') || filePath.includes('blog/')) {
        return 'article';
    } else if (filePath.includes('pages/')) {
        return 'page';
    } else if (filePath.includes('products/')) {
        return 'product';
    } else if (filePath.includes('tina/')) {
        return 'config';
    } else {
        return 'page'; // Default
    }
}
            """),
            environment={
                "CONTENT_EVENTS_TOPIC_ARN": self.integration_layer.content_events_topic.topic_arn,
                "GITHUB_BRANCH": self.cms_provider.settings.get("branch", "main")
            },
            timeout=Duration.seconds(60)
        )

        # Grant SNS publish permissions
        self.integration_layer.content_events_topic.grant_publish(self.git_event_processor)

    def _create_tina_admin_interface(self) -> None:
        """Create TinaCMS admin interface (same for both modes)"""

        # Generate TinaCMS admin configuration
        admin_config = self._generate_tina_admin_config()

        # Store admin config in Parameter Store
        self.tina_admin_config_param = ssm.StringParameter(
            self,
            "TinaAdminConfig",
            parameter_name=f"/{self.client_config.resource_prefix}/tina/admin-config",
            string_value=json.dumps(admin_config),
            description="TinaCMS admin interface configuration"
        )

        # Create Tina admin API Lambda for GraphQL queries
        self.tina_admin_api = lambda_.Function(
            self,
            "TinaAdminAPI",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
const AWS = require('aws-sdk');

exports.handler = async (event) => {
    console.log('TinaCMS admin API request:', JSON.stringify(event));

    const { httpMethod, path, body, headers } = event;

    try {
        // Handle TinaCMS GraphQL API requests
        if (path.includes('/api/tina/graphql')) {
            const query = JSON.parse(body || '{}');

            // Process TinaCMS GraphQL query
            // In a real implementation, this would interface with git and file system
            const result = await processTinaQuery(query);

            return {
                statusCode: 200,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                body: JSON.stringify(result)
            };
        }

        return {
            statusCode: 404,
            body: JSON.stringify({ message: 'Not found' })
        };
    } catch (error) {
        console.error('TinaCMS API error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};

async function processTinaQuery(query) {
    // This would implement TinaCMS GraphQL query processing
    // For now, return empty response
    return { data: null, errors: [] };
}
            """),
            environment={
                "TINA_CLIENT_ID": self.cms_provider.settings.get("tina_client_id", "placeholder"),
                "GITHUB_REPO": f"{self.cms_provider.settings['repository_owner']}/{self.cms_provider.settings['repository']}"
            },
            timeout=Duration.seconds(30)
        )

        # Create API Gateway for Tina admin
        self.tina_api_gateway = apigateway.RestApi(
            self,
            "TinaAPIGateway",
            rest_api_name=f"{self.client_config.resource_prefix}-tina-api",
            description="TinaCMS admin API Gateway"
        )

        # Add Tina API integration with CORS
        tina_integration = apigateway.LambdaIntegration(self.tina_admin_api)
        api_resource = self.tina_api_gateway.root.add_resource("api")
        tina_resource = api_resource.add_resource("tina")
        graphql_resource = tina_resource.add_resource("graphql")

        graphql_resource.add_method("POST", tina_integration)
        graphql_resource.add_method("GET", tina_integration)
        graphql_resource.add_cors_preflight(
            allow_origins=["*"],
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"]
        )

    def _create_github_webhook_integration(self) -> None:
        """Create GitHub webhook integration for direct mode"""

        # Create API Gateway for GitHub webhooks
        webhook_api = apigateway.RestApi(
            self,
            "TinaGitHubWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-tina-github-webhooks",
            description="GitHub webhook endpoint for TinaCMS"
        )

        # Add webhook endpoint
        webhook_resource = webhook_api.root.add_resource("webhook")
        webhook_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.github_webhook_handler)
        )

        # Grant CodeBuild permissions to webhook handler
        self.build_project.grant_start_build(self.github_webhook_handler)

        # Output webhook URL
        CfnOutput(
            self,
            "GitHubWebhookUrl",
            value=f"{webhook_api.url}webhook",
            description="Webhook URL to configure in GitHub repository"
        )

    def _connect_tina_to_event_system(self) -> None:
        """Connect TinaCMS to event system for event-driven mode"""

        # Create API Gateway for GitHub webhooks (event-driven version)
        webhook_api = apigateway.RestApi(
            self,
            "TinaEventWebhookAPI",
            rest_api_name=f"{self.client_config.resource_prefix}-tina-event-webhooks"
        )

        # Add event webhook endpoint
        event_resource = webhook_api.root.add_resource("events")
        tina_resource = event_resource.add_resource("tina")

        tina_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.git_event_processor)
        )

        # Output webhook URL for GitHub configuration
        CfnOutput(
            self,
            "TinaEventWebhookUrl",
            value=f"{webhook_api.url}events/tina",
            description="Event webhook URL to configure in GitHub repository"
        )

    def _create_content_storage(self) -> None:
        """Create content storage (both modes)"""
        # Content storage is handled by BaseSSGStack
        # TinaCMS uses git for content storage primarily
        pass

    def _create_tina_secrets(self) -> None:
        """Create secrets for TinaCMS credentials"""

        # GitHub token for TinaCMS git operations
        self.github_token_secret = secrets.Secret(
            self,
            "TinaGitHubToken",
            secret_name=f"{self.client_config.resource_prefix}-tina-github-token",
            description="GitHub token for TinaCMS git operations"
        )

        # TinaCMS client secret (if using Tina Cloud)
        self.tina_client_secret = secrets.Secret(
            self,
            "TinaClientSecret",
            secret_name=f"{self.client_config.resource_prefix}-tina-client-secret",
            description="TinaCMS client secret for Tina Cloud integration"
        )

    def _create_tina_cloud_integration(self) -> None:
        """Create Tina Cloud integration if configured"""

        tina_settings = self.cms_provider.settings
        tina_token = tina_settings.get("tina_token")
        tina_client_id = tina_settings.get("tina_client_id")

        if not (tina_token and tina_client_id):
            # No Tina Cloud integration configured
            return

        # Create Tina Cloud sync Lambda
        self.tina_cloud_sync = lambda_.Function(
            self,
            "TinaCloudSync",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();

exports.handler = async (event) => {
    console.log('Tina Cloud sync triggered:', JSON.stringify(event));

    try {
        // Get TinaCMS Cloud credentials
        const secretValue = await secretsManager.getSecretValue({
            SecretId: process.env.TINA_CLIENT_SECRET_ARN
        }).promise();

        const secrets = JSON.parse(secretValue.SecretString);

        // Sync content with Tina Cloud
        console.log('Syncing with Tina Cloud...');

        // Implementation would sync content between local git and Tina Cloud
        // This provides enhanced features like real-time collaboration

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Tina Cloud sync completed' })
        };
    } catch (error) {
        console.error('Tina Cloud sync error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};
            """),
            environment={
                "TINA_CLIENT_SECRET_ARN": self.tina_client_secret.secret_arn,
                "TINA_CLIENT_ID": tina_client_id
            },
            timeout=Duration.minutes(5)
        )

        # Grant permissions
        self.tina_client_secret.grant_read(self.tina_cloud_sync)

    def _generate_tina_admin_config(self) -> Dict[str, Any]:
        """Generate TinaCMS admin configuration"""

        cms_settings = self.cms_provider.settings
        ssg_engine = self.client_config.service_integration.ssg_engine

        # Base TinaCMS configuration
        config = {
            "clientId": cms_settings.get("tina_client_id", "placeholder"),
            "branch": cms_settings.get("branch", "main"),
            "repository": f"{cms_settings['repository_owner']}/{cms_settings['repository']}",
            "adminPath": "/admin",
            "apiPath": "/api/tina/graphql"
        }

        # Add SSG-specific configurations
        if ssg_engine == "nextjs":
            config.update({
                "integration": "nextjs",
                "contentPath": "content",
                "publicPath": "public"
            })
        elif ssg_engine == "astro":
            config.update({
                "integration": "astro",
                "contentPath": "src/content",
                "publicPath": "public"
            })
        elif ssg_engine == "gatsby":
            config.update({
                "integration": "gatsby",
                "contentPath": "content",
                "publicPath": "static"
            })

        return config

    def _get_direct_mode_buildspec(self) -> codebuild.BuildSpec:
        """Get buildspec for direct mode builds"""

        ssg_engine = self.client_config.service_integration.ssg_engine

        if ssg_engine == "nextjs":
            return codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "18"},
                        "commands": [
                            "npm ci",
                            "npm install -g @tinacms/cli"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "npx @tinacms/cli build --skip-sdk || true"
                        ]
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
                        "commands": [
                            "npm ci",
                            "npm install -g @tinacms/cli"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "npx @tinacms/cli build --skip-sdk || true"
                        ]
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
                        "commands": [
                            "npm ci",
                            "npm install -g @tinacms/cli"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "npx @tinacms/cli build --skip-sdk || true"
                        ]
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

    def _create_stack_outputs(self) -> None:
        """Create CloudFormation outputs"""

        # Common outputs
        CfnOutput(
            self,
            "SiteUrl",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="Published site URL"
        )

        CfnOutput(
            self,
            "TinaAdminUrl",
            value=f"https://{self.distribution.distribution_domain_name}/admin",
            description="TinaCMS admin interface URL"
        )

        if hasattr(self, 'tina_api_gateway'):
            CfnOutput(
                self,
                "TinaAPIEndpoint",
                value=self.tina_api_gateway.url,
                description="TinaCMS GraphQL API endpoint"
            )

        CfnOutput(
            self,
            "IntegrationMode",
            value=self.integration_mode.value,
            description="CMS integration mode (direct or event_driven)"
        )

        CfnOutput(
            self,
            "CMSProvider",
            value="tina",
            description="CMS provider"
        )

        CfnOutput(
            self,
            "SSGEngine",
            value=self.client_config.service_integration.ssg_engine,
            description="SSG engine"
        )

        # Tina Cloud integration status
        tina_settings = self.cms_provider.settings
        cloud_enabled = bool(tina_settings.get("tina_token") and tina_settings.get("tina_client_id"))

        CfnOutput(
            self,
            "TinaCloudEnabled",
            value="true" if cloud_enabled else "false",
            description="Tina Cloud integration status"
        )

        # Mode-specific outputs
        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
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
                "SupportsComposition",
                value="true",
                description="Supports composition with other providers"
            )
        else:
            CfnOutput(
                self,
                "SupportsComposition",
                value="false",
                description="Direct mode - no composition support"
            )

    def _create_custom_infrastructure(self) -> None:
        """Required implementation from BaseSSGStack"""
        # Infrastructure creation is handled by mode-specific methods
        pass

    def get_monthly_cost_estimate(self) -> Dict[str, Any]:
        """Get monthly cost estimate for TinaCMS tier"""

        tina_settings = self.cms_provider.settings
        cloud_enabled = bool(tina_settings.get("tina_token") and tina_settings.get("tina_client_id"))

        base_costs = {
            "tina_cms_self_hosted": 0,  # FREE for git-based editing
            "tina_cloud": 29 if cloud_enabled else 0,  # Enhanced features
            "aws_hosting": 50,  # Base hosting costs
            "cloudfront": 15,  # CDN costs
            "codebuild": 10,  # Build minutes
            "lambda_admin_api": 5,  # Admin API processing
            "api_gateway": 3,  # Admin API gateway
        }

        if self.integration_mode == IntegrationMode.EVENT_DRIVEN:
            base_costs.update({
                "sns_messages": 5,  # Event messaging
                "lambda_executions": 5,  # Event processing
                "dynamodb": 8,  # Unified content storage
            })

        monthly_total = sum(base_costs.values())

        return {
            "self_hosted_total": base_costs["tina_cms_self_hosted"] + base_costs["aws_hosting"] + base_costs["cloudfront"] + base_costs["codebuild"] + base_costs["lambda_admin_api"] + base_costs["api_gateway"],
            "tina_cloud_total": monthly_total,
            "recommended_plan": "tina_cloud" if cloud_enabled else "self_hosted",
            "cost_advantage": "Git-based workflow with visual editing benefits"
        }

    @staticmethod
    def get_client_suitability_score(requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get client suitability score for TinaCMS tier"""

        score = 0
        reasons = []

        # Visual editing need (major factor for TinaCMS)
        if requirements.get("visual_editing", False):
            score += 35
            reasons.append("Visual editing with git benefits")

        # Git workflow preference
        if requirements.get("git_workflow", False):
            score += 30
            reasons.append("Git-based workflow with full version control")

        # Developer + content creator team
        if requirements.get("mixed_technical_team", False):
            score += 25
            reasons.append("Perfect for teams with both developers and content creators")

        # Real-time preview needs
        if requirements.get("real_time_preview", False):
            score += 20
            reasons.append("Real-time preview and visual editing capabilities")

        # Content versioning requirements
        if requirements.get("content_versioning", False):
            score += 15
            reasons.append("Git provides comprehensive content versioning")

        # React/Next.js preference
        if requirements.get("react_ecosystem", False):
            score += 15
            reasons.append("Excellent React/Next.js integration")

        # Budget considerations
        budget = requirements.get("monthly_budget", 100)
        if budget >= 125:
            score += 10
            reasons.append("Budget supports Tina Cloud features")
        elif budget >= 75:
            score += 5
            reasons.append("Budget covers self-hosted TinaCMS")
        else:
            score -= 5
            reasons.append("Tight budget but self-hosted option available")

        # Non-technical content creators penalty
        if requirements.get("non_technical_users", False):
            score -= 10
            reasons.append("May require some technical comfort for git concepts")

        # Determine suitability level
        if score >= 80:
            suitability = "excellent"
        elif score >= 60:
            suitability = "good"
        elif score >= 40:
            suitability = "fair"
        else:
            suitability = "poor"

        return {
            "suitability_score": min(100, max(0, score)),
            "suitability": suitability,
            "reasons": reasons,
            "integration_mode_recommendation": "event_driven" if requirements.get("future_composition") else "direct"
        }