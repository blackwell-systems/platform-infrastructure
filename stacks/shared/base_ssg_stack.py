"""
===============================================================================
Base Static Site Generator (SSG) Infrastructure Stack
===============================================================================

This module defines the foundational AWS CDK stack used by all Static Site
Generator (SSG) deployments. It provides the shared infrastructure components
and integration logic that enable automated site builds, hosting, and delivery
through AWS services.

Key Responsibilities:
- Provision core hosting infrastructure (S3 + CloudFront + Route53 + ACM)
- Integrate AWS CodeBuild for SSG engine compilation and deployment
- Apply consistent tagging and environment metadata across all resources
- Manage domain setup, SSL certificate validation, and DNS routing
- Enforce caching, cost, and performance strategies based on the SSG engine
- Provide extension hooks for higher-tier stacks (marketing, e-commerce, etc.)

Integration Model:
- Consumes a validated StaticSiteConfig (from ssg_engines.py)
- Uses the associated SSGEngineConfig to generate CodeBuild buildspecs
- Deploys S3 content and CloudFront distributions according to hosting pattern
- Exposes standard outputs for downstream integrations or CI/CD pipelines

Intended Usage:
- Subclassed by specific product or client stacks (e.g., EleventyMarketingStack)
- Serves as the common infrastructure foundation for the entire SSG ecosystem

Author:  Dayna Blackwell
Created: 2025
License: Proprietary / Internal Use Only
===============================================================================
"""


from typing import Dict, Any, Optional
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

from shared.ssg import StaticSiteConfig, SSGEngineConfig


class BaseSSGStack(Stack):
    """
    Base class for all SSG-based stacks.

    Handles common infrastructure patterns and integrates with the SSG engine system.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ssg_config: StaticSiteConfig,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.ssg_config = ssg_config
        self.engine_config = ssg_config.get_ssg_config()

        # Apply consistent tagging from SSG configuration
        for key, value in ssg_config.to_aws_tags().items():
            self.node.add_metadata(key, value)

        # Create infrastructure components
        self._create_hosting_infrastructure()
        self._create_build_infrastructure()
        self._create_domain_infrastructure()

    def _create_hosting_infrastructure(self) -> None:
        """Create S3 bucket and CloudFront distribution for hosting"""

        # Content bucket with tier-appropriate settings
        self.content_bucket = s3.Bucket(
            self,
            "ContentBucket",
            bucket_name=f"{self.ssg_config.client_id}-{self.engine_config.engine_name}-content",
            website_index_document="index.html",
            website_error_document="404.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # For dev/test environments
            auto_delete_objects=True,
        )

        # Origin Access Identity for CloudFront
        self.oai = cloudfront.OriginAccessIdentity(
            self,
            "OriginAccessIdentity",
            comment=f"OAI for {self.ssg_config.client_id} SSG site"
        )

        # Grant CloudFront read access
        self.content_bucket.grant_read(self.oai)

        # CloudFront distribution with SSG-optimized settings
        self.distribution = cloudfront.CloudFrontWebDistribution(
            self,
            "CDNDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=self.content_bucket,
                        origin_access_identity=self.oai
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                            compress=True,
                            allowed_methods=cloudfront.CloudFrontAllowedMethods.GET_HEAD,
                            cached_methods=cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD,
                            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                            default_ttl=self._get_cache_duration(),
                            max_ttl=Duration.days(365),
                            min_ttl=Duration.seconds(0)
                        )
                    ]
                )
            ],
            comment=f"CDN for {self.ssg_config.client_id} ({self.engine_config.engine_name})",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Cost optimization
            enable_logging=True,
            default_root_object="index.html",
            error_configurations=[
                cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=404,
                    response_code=404,
                    response_page_path="/404.html"
                )
            ]
        )

    def _create_build_infrastructure(self) -> None:
        """Create CodeBuild project using SSG engine configuration"""

        # Get buildspec from SSG engine
        buildspec = self.engine_config.get_buildspec()

        # Add S3 sync to buildspec
        buildspec["phases"]["post_build"] = {
            "commands": [
                f"aws s3 sync {self.engine_config.output_directory}/ s3://{self.content_bucket.bucket_name}/ --delete",
                f"aws cloudfront create-invalidation --distribution-id {self.distribution.distribution_id} --paths '/*'"
            ]
        }

        # Create build project
        self.build_project = codebuild.Project(
            self,
            "BuildProject",
            project_name=f"{self.ssg_config.client_id}-{self.engine_config.engine_name}-build",
            environment=self.engine_config.get_codebuild_environment(),
            build_spec=codebuild.BuildSpec.from_object(buildspec),
            # Source will be added by specific stack implementations
        )

        # Grant permissions
        self.content_bucket.grant_read_write(self.build_project)
        self.distribution.grant_create_invalidation(self.build_project)

    def _create_domain_infrastructure(self) -> None:
        """Create Route53 records and SSL certificate"""

        # Look up hosted zone (assumes shared infrastructure created it)
        self.hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=self._get_root_domain()
        )

        # Create SSL certificate
        self.certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name=self.ssg_config.domain,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )

        # Add certificate to CloudFront (requires recreation)
        # Note: This is simplified - in practice you'd create distribution with certificate

        # Create DNS records
        route53.ARecord(
            self,
            "ARecord",
            zone=self.hosted_zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(self.distribution)
            ),
            record_name=self._get_subdomain() or ""
        )

    def _get_cache_duration(self) -> Duration:
        """Get cache duration based on SSG engine characteristics"""
        performance_mapping = {
            "hugo": Duration.hours(6),    # Hugo builds are very fast
            "eleventy": Duration.hours(12), # Fast builds
            "astro": Duration.hours(24),   # Good build performance
            "gatsby": Duration.hours(48),  # Slower builds, cache longer
            "nextjs": Duration.hours(24),  # Variable build time
            "nuxt": Duration.hours(24),    # Variable build time
            "jekyll": Duration.hours(12)   # Moderate build time
        }

        return performance_mapping.get(
            self.engine_config.engine_name,
            Duration.hours(24)  # Default
        )

    def _get_root_domain(self) -> str:
        """Extract root domain from client domain"""
        # Simple implementation - enhance as needed
        parts = self.ssg_config.domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return self.ssg_config.domain

    def _get_subdomain(self) -> Optional[str]:
        """Extract subdomain if present"""
        parts = self.ssg_config.domain.split('.')
        if len(parts) > 2:
            return '.'.join(parts[:-2])
        return None

    def add_environment_variables(self, variables: Dict[str, str]) -> None:
        """Add environment variables to build project"""
        for key, value in variables.items():
            self.build_project.add_environment_variable(key, codebuild.BuildEnvironmentVariable(value=value))

    @property
    def outputs(self) -> Dict[str, Any]:
        """Key outputs for client use"""
        return {
            "content_bucket_name": self.content_bucket.bucket_name,
            "distribution_id": self.distribution.distribution_id,
            "distribution_domain": self.distribution.distribution_domain_name,
            "build_project_name": self.build_project.project_name,
            "site_domain": self.ssg_config.domain
        }