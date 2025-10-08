"""
Eleventy Marketing Stack

High-volume Tier 1 service for static marketing sites.
Targets: Individual professionals, small businesses
Management: Developer-managed ($75-100/month)
"""

from constructs import Construct
from aws_cdk import aws_codebuild as codebuild

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.ssg_engines import StaticSiteConfig


class EleventyMarketingStack(BaseSSGStack):
    """
    Static marketing sites using Eleventy SSG.

    Features:
    - Fast builds with Eleventy
    - Optimized for marketing content
    - Developer-managed content updates
    - Cost-optimized infrastructure
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        **kwargs
    ):
        # Create SSG configuration
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine="eleventy",
            template_variant="business_modern",
            performance_tier="optimized"
        )

        super().__init__(scope, construct_id, ssg_config, **kwargs)

        # Add marketing-specific configurations
        self._setup_marketing_features()

    def _setup_marketing_features(self) -> None:
        """Add marketing-specific features"""

        # Add marketing-specific environment variables
        marketing_vars = {
            "SITE_TYPE": "marketing",
            "ELEVENTY_PRODUCTION": "true",
            "NODE_ENV": "production"
        }

        self.add_environment_variables(marketing_vars)

        # Set up source (GitHub integration)
        # This would integrate with your template repositories
        # For now, this is a placeholder for the GitHub integration
        self._setup_github_source()

        # Add SEO and analytics setup
        self._setup_analytics_integration()

    def _setup_github_source(self) -> None:
        """Set up GitHub source integration"""
        # TODO: Implement GitHub source integration
        # This will connect to your template repositories
        # Example: https://github.com/your-templates/eleventy-business-modern
        pass

    def _setup_analytics_integration(self) -> None:
        """Set up analytics and SEO tracking"""
        # Add environment variables for analytics
        analytics_vars = {
            "GOOGLE_ANALYTICS_ID": "${GOOGLE_ANALYTICS_ID}",  # CDK parameter
            "FACEBOOK_PIXEL_ID": "${FACEBOOK_PIXEL_ID}",      # CDK parameter
        }
        self.add_environment_variables(analytics_vars)