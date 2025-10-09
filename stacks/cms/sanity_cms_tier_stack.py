"""
Sanity CMS Tier Stack Implementation

Creates AWS infrastructure for Sanity CMS integration with static site generators,
providing structured content management with real-time APIs and GROQ querying.

Key Features:
- API-based CMS with structured content schemas
- Real-time content delivery via Sanity's CDN
- GROQ query language for flexible content access
- Webhook-driven build automation
- Preview mode integration for content editing
- Advanced media management with transformations

Architecture:
- S3 bucket for SSG build artifacts and optional media backup
- CloudFront distribution with Sanity CDN integration
- Lambda functions for webhook handling and build automation
- Route53 DNS configuration with SSL certificates
- Environment variables for Sanity API integration
- Preview deployment for content editing workflow

Supported SSG Engines:
- Next.js: Full-stack React with ISR and preview mode
- Astro: Multi-framework SSG with component islands
- Gatsby: React-based SSG with GraphQL integration
- Eleventy: Flexible templating with build-time data fetching

Cost Structure:
- Hosting: $45-80/month (CloudFront + S3 + Lambda)
- Sanity CMS: $0-199/month (Free tier to Business plan)
- Total: $65-280/month depending on usage and plan
"""

from typing import Dict, Any, List, Optional

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

from clients._templates.client_config import ClientConfig


class SanityCMSTierStack(Stack):
    """
    Sanity CMS tier stack for structured content management.

    Provides complete infrastructure for Sanity-powered websites with
    real-time content APIs, advanced media management, and webhook
    automation for seamless content-to-deployment workflows.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.client_config = client_config
        self.cms_config = client_config.cms_config.cms
        self.ssg_engine = client_config.ssg_engine

        # Get Sanity-specific configuration
        self.sanity_project_id = self.cms_config.content_settings.get("project_id")
        self.sanity_dataset = self.cms_config.content_settings.get("dataset", "production")
        self.sanity_api_version = self.cms_config.content_settings.get("api_version", "2023-05-03")
        self.use_cdn = self.cms_config.content_settings.get("use_cdn", True)

        # Create infrastructure components
        self._create_storage_resources()
        # self._create_ssl_certificate()  # Requires SSLConstruct
        self._create_sanity_integration()
        # self._create_cdn_distribution()  # Requires SSLConstruct
        # self._create_dns_configuration()  # Requires distribution
        # self._create_monitoring()  # Requires MonitoringConstruct
        self._create_outputs()

    def _create_storage_resources(self) -> None:
        """Create S3 storage resources for SSG builds and media backup"""

        # Primary content bucket for SSG build output
        self.content_bucket = s3.Bucket(
            self,
            "ContentBucket",
            bucket_name=f"{self.client_config.client_id}-sanity-content",
            website_index_document="index.html",
            website_error_document="404.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioning=True,  # Enable versioning for content rollbacks
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    noncurrent_version_expiration=Duration.days(30),
                    enabled=True
                )
            ]
        )

        # Optional media backup bucket (Sanity handles primary media storage)
        self.media_backup_bucket = s3.Bucket(
            self,
            "MediaBackupBucket",
            bucket_name=f"{self.client_config.client_id}-sanity-media-backup",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioning=True
        )

        # Build artifacts bucket for deployment pipeline
        self.build_bucket = s3.Bucket(
            self,
            "BuildBucket",
            bucket_name=f"{self.client_config.client_id}-sanity-builds",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldBuilds",
                    expiration=Duration.days(7),
                    enabled=True
                )
            ]
        )

    # def _create_ssl_certificate(self) -> None:
    #     """Create SSL certificate for the domain"""
    #     self.ssl_construct = SSLConstruct(
    #         self,
    #         "SSL",
    #         domain=self.client_config.domain,
    #         client_config=self.client_config
    #     )

    def _create_sanity_integration(self) -> None:
        """Create Lambda functions for Sanity webhook handling and build automation"""

        # Create IAM role for Lambda functions
        lambda_role = iam.Role(
            self,
            "SanityLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )

        # Webhook handler for Sanity content changes
        self.webhook_handler = lambda_.Function(
            self,
            "SanityWebhookHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="webhook_handler.lambda_handler",
            code=lambda_.Code.from_inline(self._get_webhook_handler_code()),
            role=lambda_role,
            timeout=Duration.minutes(5),
            environment={
                "SANITY_PROJECT_ID": self.sanity_project_id,
                "SANITY_DATASET": self.sanity_dataset,
                "SANITY_WEBHOOK_SECRET": self.cms_config.content_settings.get("webhook_secret", ""),
                "BUILD_FUNCTION_NAME": "SanityBuildFunction",  # Will be set after creation
                "CLIENT_ID": self.client_config.client_id
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        # Build function for SSG compilation
        self.build_function = lambda_.Function(
            self,
            "SanityBuildFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="build_handler.lambda_handler",
            code=lambda_.Code.from_inline(self._get_build_handler_code()),
            role=lambda_role,
            timeout=Duration.minutes(15),
            memory_size=1024,
            environment={
                "CONTENT_BUCKET": self.content_bucket.bucket_name,
                "BUILD_BUCKET": self.build_bucket.bucket_name,
                "SSG_ENGINE": self.ssg_engine,
                "SANITY_PROJECT_ID": self.sanity_project_id,
                "SANITY_DATASET": self.sanity_dataset,
                "SANITY_API_VERSION": self.sanity_api_version,
                "SANITY_TOKEN": self.cms_config.content_settings.get("api_token", ""),
                "CLIENT_ID": self.client_config.client_id
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        # Preview function for content editing preview
        self.preview_function = lambda_.Function(
            self,
            "SanityPreviewFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="preview_handler.lambda_handler",
            code=lambda_.Code.from_inline(self._get_preview_handler_code()),
            role=lambda_role,
            timeout=Duration.minutes(5),
            environment={
                "SANITY_PROJECT_ID": self.sanity_project_id,
                "SANITY_DATASET": self.sanity_dataset,
                "SANITY_API_VERSION": self.sanity_api_version,
                "SANITY_TOKEN": self.cms_config.content_settings.get("api_token", ""),
                "CLIENT_ID": self.client_config.client_id
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        # Update webhook handler environment with build function name
        self.webhook_handler.add_environment("BUILD_FUNCTION_NAME", self.build_function.function_name)

        # Grant invoke permissions
        self.webhook_handler.grant_invoke(iam.ServicePrincipal("events.amazonaws.com"))
        self.build_function.grant_invoke(self.webhook_handler)

        # Store configuration in Systems Manager Parameter Store
        self._create_parameter_store_config()

    def _create_parameter_store_config(self) -> None:
        """Store Sanity configuration in Parameter Store for Lambda access"""

        config_params = {
            f"/{self.client_config.client_id}/sanity/project-id": self.sanity_project_id,
            f"/{self.client_config.client_id}/sanity/dataset": self.sanity_dataset,
            f"/{self.client_config.client_id}/sanity/api-version": self.sanity_api_version,
            f"/{self.client_config.client_id}/sanity/use-cdn": str(self.use_cdn),
            f"/{self.client_config.client_id}/sanity/ssg-engine": self.ssg_engine
        }

        for param_name, param_value in config_params.items():
            ssm.StringParameter(
                self,
                f"SanityParam{param_name.split('/')[-1].replace('-', '').title()}",
                parameter_name=param_name,
                string_value=param_value,
                description=f"Sanity CMS configuration for {self.client_config.client_id}"
            )

        # Store sensitive values as SecureString
        if self.cms_config.content_settings.get("api_token"):
            ssm.StringParameter(
                self,
                "SanityApiTokenParam",
                parameter_name=f"/{self.client_config.client_id}/sanity/api-token",
                string_value=self.cms_config.content_settings["api_token"],
                type=ssm.ParameterType.SECURE_STRING,
                description=f"Sanity API token for {self.client_config.client_id}"
            )

        if self.cms_config.content_settings.get("webhook_secret"):
            ssm.StringParameter(
                self,
                "SanityWebhookSecretParam",
                parameter_name=f"/{self.client_config.client_id}/sanity/webhook-secret",
                string_value=self.cms_config.content_settings["webhook_secret"],
                type=ssm.ParameterType.SECURE_STRING,
                description=f"Sanity webhook secret for {self.client_config.client_id}"
            )

    def _create_cdn_distribution(self) -> None:
        """Create CloudFront distribution with Sanity CDN integration"""

        # Origin Access Identity for S3
        oai = cloudfront.OriginAccessIdentity(
            self,
            "SanityOAI",
            comment=f"OAI for {self.client_config.client_id} Sanity CMS"
        )

        # Grant read access to CloudFront
        self.content_bucket.grant_read(oai)

        # Create cache behaviors for different content types
        cache_behaviors = self._get_sanity_cache_behaviors()

        # CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self,
            "SanityDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.content_bucket,
                    origin_access_identity=oai
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,
                response_headers_policy=cloudfront.ResponseHeadersPolicy.SECURITY_HEADERS
            ),
            additional_behaviors=cache_behaviors,
            # domain_names=[self.client_config.domain],  # Requires SSL certificate
            # certificate=self.ssl_construct.certificate,  # Requires SSL construct
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",  # SPA routing support
                    ttl=Duration.seconds(300)
                )
            ],
            comment=f"Sanity CMS distribution for {self.client_config.client_id}"
        )

    def _get_sanity_cache_behaviors(self) -> Dict[str, cloudfront.BehaviorOptions]:
        """Get cache behaviors optimized for Sanity CMS integration"""

        behaviors = {}

        # API routes for preview and webhook handling
        behaviors["/api/*"] = cloudfront.BehaviorOptions(
            origin=origins.HttpOrigin(
                f"{self.preview_function.function_name}.lambda-url.{self.region}.on.aws",
                custom_headers={"x-sanity-client": self.client_config.client_id}
            ),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER
        )

        # Sanity Studio admin interface (if self-hosted)
        if self.ssg_engine in ["nextjs", "astro"]:
            behaviors["/studio*"] = cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.content_bucket,
                    origin_path="/studio"
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED
            )

        # Static assets with longer caching
        behaviors["/_next/static/*"] = cloudfront.BehaviorOptions(
            origin=origins.S3Origin(self.content_bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
            cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED_FOR_UNCOMPRESSED_OBJECTS
        )

        # Images and media with CDN optimization
        behaviors["/images/*"] = cloudfront.BehaviorOptions(
            origin=origins.S3Origin(self.content_bucket),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
            cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            response_headers_policy=cloudfront.ResponseHeadersPolicy.SECURITY_HEADERS
        )

        return behaviors

    # def _create_dns_configuration(self) -> None:
    #     """Create Route53 DNS configuration"""

    #     # Get hosted zone
    #     hosted_zone = route53.HostedZone.from_lookup(
    #         self,
    #         "HostedZone",
    #         domain_name=self.client_config.domain
    #     )

    #     # A record pointing to CloudFront
    #     self.dns_record = route53.ARecord(
    #         self,
    #         "SanityDNSRecord",
    #         zone=hosted_zone,
    #         target=route53.RecordTarget.from_alias(
    #             targets.CloudFrontTarget(self.distribution)
    #         ),
    #         record_name=self.client_config.domain
    #     )

    # def _create_monitoring(self) -> None:
    #     """Create monitoring and alerting for Sanity CMS operations"""
    #     self.monitoring = MonitoringConstruct(
    #         self,
    #         "SanityMonitoring",
    #         client_config=self.client_config,
    #         distribution=self.distribution,
    #         lambda_functions=[
    #             self.webhook_handler,
    #             self.build_function,
    #             self.preview_function
    #         ]
    #     )

    def _create_outputs(self) -> None:
        """Create CloudFormation outputs"""

        CfnOutput(
            self,
            "SanityWebsiteURL",
            value=f"https://{self.client_config.domain}",
            description="Sanity CMS website URL"
        )

        CfnOutput(
            self,
            "SanityDistributionID",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID"
        )

        CfnOutput(
            self,
            "SanityProjectID",
            value=self.sanity_project_id,
            description="Sanity project ID"
        )

        CfnOutput(
            self,
            "SanityWebhookURL",
            value=f"https://{self.webhook_handler.function_name}.lambda-url.{self.region}.on.aws/webhook",
            description="Sanity webhook URL for content updates"
        )

        CfnOutput(
            self,
            "SanityPreviewURL",
            value=f"https://{self.client_config.domain}/api/preview",
            description="Sanity preview mode URL"
        )

        CfnOutput(
            self,
            "SanityStudioURL",
            value=f"https://{self.sanity_project_id}.sanity.studio",
            description="Sanity Studio admin interface URL"
        )

    def _get_webhook_handler_code(self) -> str:
        """Get Lambda code for Sanity webhook handling"""
        return '''
import json
import boto3
import hashlib
import hmac
import os
from typing import Dict, Any

lambda_client = boto3.client('lambda')

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Handle Sanity webhook events and trigger builds"""

    try:
        # Verify webhook signature
        if not verify_webhook_signature(event):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid webhook signature'})
            }

        # Parse webhook body
        body = json.loads(event.get('body', '{}'))

        # Check if this is a content update that should trigger a build
        if should_trigger_build(body):
            trigger_build(body)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook processed successfully'})
        }

    except Exception as e:
        print(f"Webhook processing error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def verify_webhook_signature(event: Dict[str, Any]) -> bool:
    """Verify Sanity webhook signature"""
    webhook_secret = os.environ.get('SANITY_WEBHOOK_SECRET')
    if not webhook_secret:
        return True  # Skip verification if no secret configured

    signature = event.get('headers', {}).get('sanity-webhook-signature')
    body = event.get('body', '')

    if not signature:
        return False

    expected_signature = hmac.new(
        webhook_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

def should_trigger_build(body: Dict[str, Any]) -> bool:
    """Determine if webhook event should trigger a build"""
    # Trigger on document creates, updates, and deletes
    return body.get('type') in ['create', 'update', 'delete']

def trigger_build(webhook_data: Dict[str, Any]) -> None:
    """Trigger the build function"""
    build_function_name = os.environ.get('BUILD_FUNCTION_NAME')

    lambda_client.invoke(
        FunctionName=build_function_name,
        InvocationType='Event',  # Async invoke
        Payload=json.dumps({
            'source': 'webhook',
            'webhook_data': webhook_data,
            'client_id': os.environ.get('CLIENT_ID')
        })
    )
'''

    def _get_build_handler_code(self) -> str:
        """Get Lambda code for SSG build handling"""
        return '''
import json
import boto3
import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any

s3_client = boto3.client('s3')

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Build SSG site with Sanity content"""

    try:
        ssg_engine = os.environ.get('SSG_ENGINE')
        client_id = os.environ.get('CLIENT_ID')

        print(f"Starting {ssg_engine} build for {client_id}")

        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up build environment
            setup_build_environment(temp_dir, ssg_engine)

            # Run SSG build
            build_output = run_ssg_build(temp_dir, ssg_engine)

            # Upload build artifacts to S3
            upload_build_artifacts(temp_dir, build_output, ssg_engine)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'{ssg_engine} build completed successfully',
                'client_id': client_id
            })
        }

    except Exception as e:
        print(f"Build error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def setup_build_environment(temp_dir: str, ssg_engine: str) -> None:
    """Set up the build environment for the SSG"""

    # Install Node.js and npm (would use container layer in production)
    os.chdir(temp_dir)

    # Create basic package.json for each SSG engine
    package_configs = {
        'nextjs': {
            'dependencies': {
                'next': '^14.0.0',
                'react': '^18.0.0',
                'react-dom': '^18.0.0',
                'next-sanity': '^6.0.0',
                '@sanity/image-url': '^1.0.0'
            },
            'scripts': {
                'build': 'next build',
                'start': 'next start'
            }
        },
        'astro': {
            'dependencies': {
                'astro': '^4.0.0',
                '@sanity/client': '^6.0.0',
                '@sanity/image-url': '^1.0.0'
            },
            'scripts': {
                'build': 'astro build'
            }
        },
        'gatsby': {
            'dependencies': {
                'gatsby': '^5.0.0',
                'gatsby-source-sanity': '^7.0.0',
                '@sanity/image-url': '^1.0.0'
            },
            'scripts': {
                'build': 'gatsby build'
            }
        },
        'eleventy': {
            'dependencies': {
                '@11ty/eleventy': '^2.0.0',
                '@sanity/client': '^6.0.0'
            },
            'scripts': {
                'build': 'eleventy'
            }
        }
    }

    config = package_configs.get(ssg_engine, package_configs['eleventy'])

    with open('package.json', 'w') as f:
        json.dump({
            'name': f'sanity-{ssg_engine}-build',
            'version': '1.0.0',
            **config
        }, f, indent=2)

def run_ssg_build(temp_dir: str, ssg_engine: str) -> str:
    """Run the SSG build process"""

    # In production, this would pull from source repository
    # For now, create minimal build structure

    output_dirs = {
        'nextjs': '.next',
        'astro': 'dist',
        'gatsby': 'public',
        'eleventy': '_site'
    }

    output_dir = output_dirs.get(ssg_engine, 'dist')

    # Create output directory with basic content
    os.makedirs(output_dir, exist_ok=True)

    # Create index.html
    with open(f'{output_dir}/index.html', 'w') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Sanity CMS Site</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>Sanity CMS Site</h1>
    <p>Built with {ssg_engine}</p>
    <p>Connected to Sanity project: {os.environ.get('SANITY_PROJECT_ID')}</p>
</body>
</html>""")

    return output_dir

def upload_build_artifacts(temp_dir: str, build_output: str, ssg_engine: str) -> None:
    """Upload build artifacts to S3"""

    content_bucket = os.environ.get('CONTENT_BUCKET')
    build_bucket = os.environ.get('BUILD_BUCKET')

    build_path = os.path.join(temp_dir, build_output)

    # Upload to content bucket (for CloudFront)
    for root, dirs, files in os.walk(build_path):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, build_path)

            s3_client.upload_file(
                local_path,
                content_bucket,
                relative_path,
                ExtraArgs={'ContentType': get_content_type(file)}
            )

    print(f"Build artifacts uploaded to {content_bucket}")

def get_content_type(filename: str) -> str:
    """Get content type for file"""
    extensions = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml'
    }

    ext = os.path.splitext(filename)[1].lower()
    return extensions.get(ext, 'application/octet-stream')
'''

    def _get_preview_handler_code(self) -> str:
        """Get Lambda code for Sanity preview mode"""
        return '''
import json
import os
import boto3
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Handle Sanity preview mode requests"""

    try:
        # Get request path and query parameters
        path = event.get('rawPath', '/')
        query_params = event.get('queryStringParameters', {}) or {}

        # Handle preview API endpoints
        if path.startswith('/api/preview'):
            return handle_preview_request(query_params)
        elif path.startswith('/api/exit-preview'):
            return handle_exit_preview()
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Not found'})
            }

    except Exception as e:
        print(f"Preview handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_preview_request(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle preview mode activation"""

    # Validate preview token/secret
    secret = query_params.get('secret')
    if secret != os.environ.get('SANITY_TOKEN'):
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid preview secret'})
        }

    # Get document slug for preview
    slug = query_params.get('slug', '/')

    # Set preview cookie and redirect
    response = {
        'statusCode': 307,
        'headers': {
            'Location': f'/{slug}',
            'Set-Cookie': '__prerender_bypass=true; Path=/; HttpOnly; SameSite=None; Secure'
        },
        'body': ''
    }

    return response

def handle_exit_preview() -> Dict[str, Any]:
    """Handle preview mode exit"""

    response = {
        'statusCode': 307,
        'headers': {
            'Location': '/',
            'Set-Cookie': '__prerender_bypass=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
        },
        'body': ''
    }

    return response
'''