"""
Base SSG Stack

Abstract base class for all Static Site Generator stacks.
Provides common infrastructure patterns and utilities for SSG deployments
with S3, CloudFront, and build pipeline integration.

Key Features:
- Standardized S3 + CloudFront setup
- Build pipeline integration with CodeBuild
- Environment variable management
- Cost optimization patterns
- Security best practices

Usage:
    class MySSGStack(BaseSSGStack):
        def __init__(self, scope, construct_id, client_config, **kwargs):
            super().__init__(scope, construct_id, client_config, **kwargs)
            self._create_custom_infrastructure()
"""

from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional, List
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_iam as iam,
    aws_route53 as route53,
    aws_certificatemanager as acm,
    CfnOutput,
    Duration,
    RemovalPolicy
)
from constructs import Construct


class StackABCMeta(ABCMeta, type(Stack)):
    """Metaclass that combines Stack and ABC metaclasses"""
    pass


class BaseSSGStack(Stack, metaclass=StackABCMeta):
    """
    Abstract base class for all SSG stack implementations.

    Provides common infrastructure patterns while allowing
    concrete implementations to customize build processes,
    CMS integration, and deployment strategies.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.client_config = client_config

        # Common infrastructure components (initialized by subclasses)
        self.content_bucket: Optional[s3.Bucket] = None
        self.distribution: Optional[cloudfront.CloudFrontWebDistribution] = None
        self.domain_name: Optional[str] = None

        # Build infrastructure
        self.build_role: Optional[iam.Role] = None

        # Apply standard tags
        self._apply_standard_tags()

    def _apply_standard_tags(self) -> None:
        """Apply standard tags from client configuration"""
        tags = self.client_config.tags
        for key, value in tags.items():
            self.tags.set_tag(key, value)

    def create_content_bucket(
        self,
        bucket_name: Optional[str] = None,
        website_hosting: bool = True
    ) -> s3.Bucket:
        """
        Create S3 bucket for static content hosting.

        Args:
            bucket_name: Custom bucket name (defaults to client resource prefix)
            website_hosting: Enable static website hosting

        Returns:
            S3 Bucket instance
        """
        if not bucket_name:
            bucket_name = f"{self.client_config.resource_prefix}-content"

        bucket_props = {
            "bucket_name": bucket_name,
            "public_read_access": True,
            "removal_policy": RemovalPolicy.DESTROY,
            "auto_delete_objects": True,
            "block_public_access": s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            )
        }

        if website_hosting:
            bucket_props.update({
                "website_index_document": "index.html",
                "website_error_document": "404.html"
            })

        self.content_bucket = s3.Bucket(self, "ContentBucket", **bucket_props)

        return self.content_bucket

    def create_cloudfront_distribution(
        self,
        origin_bucket: s3.Bucket,
        custom_domain: Optional[str] = None,
        certificate_arn: Optional[str] = None
    ) -> cloudfront.CloudFrontWebDistribution:
        """
        Create CloudFront distribution for global content delivery.

        Args:
            origin_bucket: S3 bucket to serve content from
            custom_domain: Custom domain name for the distribution
            certificate_arn: SSL certificate ARN for custom domain

        Returns:
            CloudFront distribution instance
        """

        # Basic behavior configuration
        default_behavior = cloudfront.Behavior(
            is_default_behavior=True,
            allowed_methods=cloudfront.CloudFrontAllowedMethods.GET_HEAD_OPTIONS,
            cached_methods=cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD_OPTIONS,
            compress=True,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            default_ttl=Duration.hours(24),
            max_ttl=Duration.days(365),
            forwarded_values=cloudfront.CfnDistribution.ForwardedValuesProperty(
                query_string=False,
                cookies=cloudfront.CfnDistribution.CookiesProperty(forward="none")
            )
        )

        # Distribution configuration
        distribution_props = {
            "origin_configs": [
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=origin_bucket
                    ),
                    behaviors=[default_behavior]
                )
            ],
            "comment": f"Distribution for {self.client_config.client_id}",
            "price_class": cloudfront.PriceClass.PRICE_CLASS_100,  # Cost optimization
            "enabled": True,
            "default_root_object": "index.html"
        }

        # Add custom domain configuration if provided
        if custom_domain and certificate_arn:
            distribution_props.update({
                "viewer_certificate": cloudfront.ViewerCertificate.from_acm_certificate(
                    acm.Certificate.from_certificate_arn(
                        self, "SSLCertificate", certificate_arn
                    ),
                    aliases=[custom_domain]
                )
            })
            self.domain_name = custom_domain

        self.distribution = cloudfront.CloudFrontWebDistribution(
            self, "ContentDistribution",
            **distribution_props
        )

        return self.distribution

    def create_build_role(self, additional_policies: Optional[List[iam.PolicyStatement]] = None) -> iam.Role:
        """
        Create IAM role for build processes.

        Args:
            additional_policies: Additional policy statements to attach

        Returns:
            IAM Role for build processes
        """
        self.build_role = iam.Role(
            self, "BuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
            ]
        )

        # Grant basic S3 permissions if content bucket exists
        if self.content_bucket:
            self.content_bucket.grant_read_write(self.build_role)

        # Grant CloudFront invalidation permissions if distribution exists
        if self.distribution:
            self.build_role.add_to_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["cloudfront:CreateInvalidation"],
                    resources=[f"arn:aws:cloudfront::{self.account}:distribution/{self.distribution.distribution_id}"]
                )
            )

        # Add additional policies if provided
        if additional_policies:
            for policy in additional_policies:
                self.build_role.add_to_policy(policy)

        return self.build_role

    def get_website_url(self) -> str:
        """Get the website URL (custom domain or CloudFront domain)"""
        if self.domain_name:
            return f"https://{self.domain_name}"
        elif self.distribution:
            return f"https://{self.distribution.distribution_domain_name}"
        else:
            raise ValueError("No distribution configured")

    def create_standard_outputs(self) -> None:
        """Create standard CloudFormation outputs"""

        # Website URL
        CfnOutput(
            self, "WebsiteURL",
            value=self.get_website_url(),
            description="Website URL"
        )

        # CloudFront distribution ID
        if self.distribution:
            CfnOutput(
                self, "DistributionId",
                value=self.distribution.distribution_id,
                description="CloudFront distribution ID"
            )

        # S3 bucket name
        if self.content_bucket:
            CfnOutput(
                self, "ContentBucket",
                value=self.content_bucket.bucket_name,
                description="S3 content bucket name"
            )

        # Client information
        CfnOutput(
            self, "ClientId",
            value=self.client_config.client_id,
            description="Client identifier"
        )

        CfnOutput(
            self, "ServiceTier",
            value=self.client_config.service_tier,
            description="Service tier"
        )

        CfnOutput(
            self, "StackType",
            value=self.client_config.stack_type,
            description="Stack type"
        )

    def get_standard_environment_variables(self) -> Dict[str, str]:
        """Get standard environment variables for build processes"""
        env_vars = {
            "CLIENT_ID": self.client_config.client_id,
            "SERVICE_TIER": self.client_config.service_tier,
            "STACK_TYPE": self.client_config.stack_type,
            "ENVIRONMENT": self.client_config.environment,
        }

        if self.content_bucket:
            env_vars["BUCKET_NAME"] = self.content_bucket.bucket_name

        if self.distribution:
            env_vars["DISTRIBUTION_ID"] = self.distribution.distribution_id

        if self.client_config.ssg_engine:
            env_vars["SSG_ENGINE"] = self.client_config.ssg_engine

        return env_vars

    def estimate_monthly_cost(self) -> Dict[str, float]:
        """
        Estimate monthly AWS costs for this stack.

        Returns:
            Dictionary with cost estimates by service
        """
        # Base cost estimates (USD/month)
        costs = {
            "s3_storage": 5.0,        # ~100GB at $0.05/GB
            "s3_requests": 2.0,       # Standard request charges
            "cloudfront": 8.0,        # ~100GB transfer at $0.085/GB
            "codebuild": 3.0,         # ~10 builds/month at $0.005/minute
            "route53": 0.50,          # If using custom domain
            "certificate": 0.0,       # ACM certificates are free
        }

        # Adjust based on service tier
        if self.client_config.service_tier == "tier1":
            # Reduce estimates for tier1 (lower usage expected)
            for key in costs:
                costs[key] *= 0.6
        elif self.client_config.service_tier == "tier3":
            # Increase estimates for tier3 (higher usage expected)
            for key in costs:
                costs[key] *= 1.5

        costs["total"] = sum(costs.values())
        return costs

    @abstractmethod
    def _create_custom_infrastructure(self) -> None:
        """
        Create stack-specific infrastructure.

        This method must be implemented by concrete stack classes
        to define their specific infrastructure requirements.
        """
        pass