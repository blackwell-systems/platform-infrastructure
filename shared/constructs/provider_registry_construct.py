"""
Provider Metadata Registry Construct

This construct creates the core infrastructure for the Provider Metadata Registry:
- S3 bucket for JSON metadata storage with versioning
- CloudFront distribution for global edge caching
- Basic IAM role for CI/CD pipeline access

MVP Implementation: Focused on core functionality without advanced features.
Advanced monitoring, replication, and fine-tuned IAM will be added post-MVP.
"""

from typing import Dict, Any

from aws_cdk import (
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct


class ProviderRegistryConstruct(Construct):
    """
    Provider Metadata Registry infrastructure construct.

    Creates S3 + CloudFront architecture for globally distributed
    provider and stack metadata serving with sub-100ms response times.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create core registry infrastructure
        self._create_registry_bucket()
        self._create_cloudfront_distribution()
        self._create_deployment_role()

        # Output key endpoints for client configuration
        self._create_outputs()

    def _create_registry_bucket(self) -> None:
        """Create S3 bucket for provider metadata registry."""

        self.registry_bucket = s3.Bucket(
            self,
            "RegistryBucket",
            bucket_name="blackwell-provider-registry-105249142972",  # Global unique name with account ID

            # Core functionality
            versioned=True,  # Enable rollback capability
            encryption=s3.BucketEncryption.S3_MANAGED,  # Default encryption

            # Public read access for CloudFront
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),

            # CORS configuration for direct client access if needed
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3600
                )
            ],

            # Basic lifecycle rule (keep simple for MVP)
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="RegistryDataRetention",
                    enabled=True,
                    # Keep current versions indefinitely
                    # Transition old versions to cheaper storage
                    noncurrent_version_transitions=[
                        s3.NoncurrentVersionTransition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        s3.NoncurrentVersionTransition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ],
                    # Delete old versions after 1 year
                    noncurrent_version_expiration=Duration.days(365)
                )
            ],

            # Retain bucket in production
            removal_policy=RemovalPolicy.RETAIN
        )

        # Add bucket notification for cache invalidation (future enhancement)
        # Skip for MVP - will add when we implement automated invalidation

    def _create_cloudfront_distribution(self) -> None:
        """Create CloudFront distribution for global edge caching."""

        # Create origin access identity for secure S3 access
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self,
            "RegistryOAI",
            comment="Provider Registry Origin Access Identity"
        )

        # Grant CloudFront read access to S3 bucket
        self.registry_bucket.grant_read(origin_access_identity)

        self.cloudfront_distribution = cloudfront.Distribution(
            self,
            "RegistryDistribution",

            # S3 origin configuration
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    bucket=self.registry_bucket,
                    origin_access_identity=origin_access_identity
                ),

                # Optimize for JSON file serving
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,

                # Caching configuration optimized for registry
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,

                # Compress JSON responses
                compress=True
            ),

            # Additional cache behaviors for different file types
            additional_behaviors={
                # Manifest file - shorter cache for more frequent updates
                "manifest.json": cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(
                        bucket=self.registry_bucket,
                        origin_access_identity=origin_access_identity
                    ),
                    cache_policy=cloudfront.CachePolicy(
                        self,
                        "ManifestCachePolicy",
                        cache_policy_name="RegistryManifestCaching",
                        comment="Shorter cache TTL for manifest.json",
                        default_ttl=Duration.minutes(5),  # 5-minute cache
                        max_ttl=Duration.hours(1),
                        min_ttl=Duration.seconds(0),
                        # Enable caching based on query strings for versioning
                        query_string_behavior=cloudfront.CacheQueryStringBehavior.all()
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    compress=True
                ),

                # Provider and stack files - longer cache
                "providers/*": cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(
                        bucket=self.registry_bucket,
                        origin_access_identity=origin_access_identity
                    ),
                    cache_policy=cloudfront.CachePolicy(
                        self,
                        "ProviderCachePolicy",
                        cache_policy_name="RegistryProviderCaching",
                        comment="Optimized caching for provider metadata",
                        default_ttl=Duration.hours(1),  # 1-hour cache
                        max_ttl=Duration.days(1),
                        min_ttl=Duration.seconds(0)
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    compress=True
                ),

                "stacks/*": cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(
                        bucket=self.registry_bucket,
                        origin_access_identity=origin_access_identity
                    ),
                    cache_policy=cloudfront.CachePolicy(
                        self,
                        "StackCachePolicy",
                        cache_policy_name="RegistryStackCaching",
                        comment="Optimized caching for stack metadata",
                        default_ttl=Duration.hours(1),  # 1-hour cache
                        max_ttl=Duration.days(1),
                        min_ttl=Duration.seconds(0)
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    compress=True
                )
            },

            # Basic configuration
            comment="Provider Metadata Registry - Global Distribution",
            default_root_object="manifest.json",

            # Enable for all edge locations
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,

            # Basic error handling (custom pages can be added later)
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    ttl=Duration.minutes(5),  # Don't cache 404s for long
                    response_http_status=404,
                    response_page_path="/manifest.json"  # Fallback to manifest
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    ttl=Duration.minutes(5),
                    response_http_status=404,  # Treat 403 as 404 for security
                    response_page_path="/manifest.json"
                )
            ]
        )

    def _create_deployment_role(self) -> None:
        """Create IAM role for CI/CD pipeline deployments."""

        self.deployment_role = iam.Role(
            self,
            "RegistryDeploymentRole",
            role_name="ProviderRegistry-Deployment-Role",
            assumed_by=iam.CompositePrincipal(
                # Allow manual deployment from EC2/Lambda for MVP
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("lambda.amazonaws.com")
            ),
            description="Role for deploying Provider Registry data to S3 and invalidating CloudFront cache"
        )

        # Grant S3 permissions for registry bucket
        self.registry_bucket.grant_read_write(self.deployment_role)

        # Grant CloudFront invalidation permissions
        self.deployment_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudfront:CreateInvalidation",
                    "cloudfront:GetInvalidation",
                    "cloudfront:ListInvalidations"
                ],
                resources=[f"arn:aws:cloudfront::*:distribution/{self.cloudfront_distribution.distribution_id}"]
            )
        )

        # Grant basic CloudWatch permissions for monitoring
        self.deployment_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudwatch:PutMetricData"
                ],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "cloudwatch:namespace": "ProviderRegistry"
                    }
                }
            )
        )

    def _create_outputs(self) -> None:
        """Create CloudFormation outputs for client configuration."""

        # Primary registry URL for client configuration
        CfnOutput(
            self,
            "RegistryUrl",
            value=f"https://{self.cloudfront_distribution.distribution_domain_name}",
            description="Provider Registry CloudFront URL for client configuration",
            export_name="ProviderRegistryUrl"
        )

        # S3 bucket name for CI/CD deployment
        CfnOutput(
            self,
            "RegistryBucketName",
            value=self.registry_bucket.bucket_name,
            description="S3 bucket name for registry data deployment",
            export_name="ProviderRegistryBucketName"
        )

        # CloudFront distribution ID for cache invalidation
        CfnOutput(
            self,
            "RegistryDistributionId",
            value=self.cloudfront_distribution.distribution_id,
            description="CloudFront distribution ID for cache invalidation",
            export_name="ProviderRegistryDistributionId"
        )

        # Deployment role ARN for CI/CD configuration
        CfnOutput(
            self,
            "DeploymentRoleArn",
            value=self.deployment_role.role_arn,
            description="IAM role ARN for registry deployment access",
            export_name="ProviderRegistryDeploymentRoleArn"
        )

    @property
    def registry_url(self) -> str:
        """Get the registry CloudFront URL."""
        return f"https://{self.cloudfront_distribution.distribution_domain_name}"

    @property
    def bucket_name(self) -> str:
        """Get the registry S3 bucket name."""
        return self.registry_bucket.bucket_name

    @property
    def distribution_id(self) -> str:
        """Get the CloudFront distribution ID."""
        return self.cloudfront_distribution.distribution_id

    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information for CI/CD configuration."""
        return {
            "registry_url": self.registry_url,
            "bucket_name": self.bucket_name,
            "distribution_id": self.distribution_id,
            "deployment_role_arn": self.deployment_role.role_arn,
            "cost_estimate_monthly": 10,  # Estimated monthly cost in USD
            "performance_target": "< 100ms global response time"
        }