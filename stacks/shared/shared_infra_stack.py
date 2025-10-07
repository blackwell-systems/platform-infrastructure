"""
Shared Infrastructure Stack

Provides operational infrastructure shared across all hosted clients:
- Business domain management (Route53)
- Centralized operational monitoring with comprehensive stack variant tracking
- Cost allocation and tagging foundation with tier-specific tracking
- Tier-based cost alarms and anomaly detection
- Basic security and compliance baselines

Supports comprehensive service delivery model:
- Tier 1 (Essential): 11 hosted-only stacks ($360-3,000 setup | $0-150/month)
- Tier 2 (Professional): 7 hosted-only stacks ($2,400-9,600 setup | $50-400/month)
- Tier 3 Dual-Delivery: 5 stacks offering both hosted solutions AND consulting templates
- Tier 3 Migration Support: 7 specialized migration stacks (40% of revenue)
- Tier 3 Consulting Templates: 4 template-only delivery stacks

Total: 30 stack variants supported across all service delivery models that use shared infrastructure.

This is NOT for client workloads - it's for running the web services business efficiently.
"""

from typing import Any, Dict

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    Tags,
)
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_route53 as route53,
)
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import (
    aws_sns as sns,
)

from constructs import Construct


class SharedInfraStack(Stack):
    """
    Shared infrastructure for web services business operations.
    
    Contains resources shared across all clients for:
    - Operational monitoring and alerting
    - Business domain management
    - Cost allocation foundation
    - Security and compliance baselines
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Business configuration
        self.business_domain = "yourwebservices.com"  # Replace with actual business domain
        self.notification_email = "ops@yourwebservices.com"  # Replace with actual email

        # Create shared resources
        self._create_business_dns()
        self._create_operational_notifications()
        self._create_operational_monitoring()
        self._create_stack_variant_tracking()
        self._create_cost_allocation_foundation()
        self._create_tier_cost_tracking()
        self._create_shared_storage()

        # Apply business tags to all resources
        self._apply_shared_tags()

    def _create_business_dns(self) -> None:
        """Create hosted zone for business domain management."""
        self.business_hosted_zone = route53.HostedZone(
            self,
            "BusinessHostedZone",
            zone_name=self.business_domain,
            comment=f"Business domain for {self.business_domain} - client DNS management"
        )

        # Export hosted zone for use by client stacks
        self.business_hosted_zone.node.add_metadata("export", True)

    def _create_operational_notifications(self) -> None:
        """Create SNS topics for operational alerts and notifications."""

        # Critical operational alerts (outages, security issues)
        self.critical_alerts_topic = sns.Topic(
            self,
            "CriticalAlertsTopic",
            topic_name="web-services-critical-alerts",
            display_name="Web Services Critical Alerts"
        )

        # Business notifications (new clients, billing, etc.)
        self.business_notifications_topic = sns.Topic(
            self,
            "BusinessNotificationsTopic",
            topic_name="web-services-business-notifications",
            display_name="Web Services Business Notifications"
        )

        # Cost and billing alerts
        self.cost_alerts_topic = sns.Topic(
            self,
            "CostAlertsTopic",
            topic_name="web-services-cost-alerts",
            display_name="Web Services Cost Alerts"
        )

        # Subscribe email to all topics
        for topic in [self.critical_alerts_topic, self.business_notifications_topic, self.cost_alerts_topic]:
            topic.add_subscription(sns.EmailSubscription(self.notification_email))

    def _create_operational_monitoring(self) -> None:
        """Create centralized operational monitoring dashboard."""

        self.operational_dashboard = cloudwatch.Dashboard(
            self,
            "OperationalDashboard",
            dashboard_name="WebServicesOperations",
            period_override=cloudwatch.PeriodOverride.AUTO,
            start="-PT24H",  # Last 24 hours
        )

        # Add basic business metrics widgets (will be populated as clients are added)
        self.operational_dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown="# Web Services Infrastructure Operations\n\n" +
                        "## Business Metrics\n" +
                        "- Active Clients: Will be populated from client deployments\n" +
                        "- Infrastructure Health: Monitoring across all client stacks\n" +
                        "- Cost Allocation: Real-time cost tracking by client\n\n" +
                        f"**Business Domain**: {self.business_domain}\n" +
                        f"**Operational Alerts**: {self.notification_email}",
                width=24,
                height=6
            )
        )

    def _create_stack_variant_tracking(self) -> None:
        """Create infrastructure to track deployed stack variants by tier."""

        # Add stack variant metadata to operational dashboard
        self.operational_dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown="## Stack Deployment Tracking\n\n" +
                        "### Tier 1 (Essential): $360-3,000 setup | $0-150/month\n" +
                        "- **Static Sites**: `eleventy_marketing_stack`, `astro_portfolio_stack`, `jekyll_github_stack`\n" +
                        "- **Static + CMS**: `eleventy_decap_cms_stack`, `astro_tina_cms_stack`, `astro_sanity_stack`, `gatsby_contentful_stack`\n" +
                        "- **Featured**: `astro_template_basic_stack` - Modern performance with flexibility\n" +
                        "- **E-commerce**: `eleventy_snipcart_stack`, `astro_foxy_stack`\n" +
                        "- **Shopify**: `shopify_standard_dns_stack` - DNS-only setup\n\n" +
                        "### Tier 2 (Professional): $2,400-9,600 setup | $50-400/month\n" +
                        "- **Advanced CMS**: `astro_advanced_cms_stack`, `gatsby_headless_cms_stack`\n" +
                        "- **Professional Frameworks**: `nextjs_professional_headless_cms_stack`, `nuxtjs_professional_headless_cms_stack`\n" +
                        "- **WordPress**: `wordpress_lightsail_stack`, `wordpress_ecs_professional_stack`\n" +
                        "- **Enhanced Shopify**: `shopify_aws_basic_integration_stack`\n\n" +
                        "### Tier 3 Dual-Delivery (Hosted OR Templates): Flexible delivery models\n" +
                        "- **Advanced Shopify**: `shopify_advanced_aws_integration_stack`\n" +
                        "- **Performance Commerce**: `headless_shopify_custom_frontend_stack`\n" +
                        "- **AWS Native**: `amplify_custom_development_stack`\n" +
                        "- **Python Solutions**: `fastapi_pydantic_api_stack`, `fastapi_react_vue_stack`\n\n" +
                        "### Tier 3 Migration Support (40% revenue): All platform migrations\n" +
                        "- **Assessment**: `migration_assessment_stack` - Planning and analysis\n" +
                        "- **E-commerce**: `magento_migration_stack`, `prestashop_migration_stack`, `opencart_migration_stack`\n" +
                        "- **CMS**: `wordpress_migration_stack`, `legacy_cms_migration_stack`\n" +
                        "- **Custom**: `custom_platform_migration_stack`",
                width=12,
                height=15
            ),
            cloudwatch.TextWidget(
                markdown="## Cost Allocation by Tier\n\n" +
                        "### Tier Pricing Ranges\n" +
                        "- **Tier 1**: $360-3,000 setup | $0-150/month\n" +
                        "- **Tier 2**: $2,400-9,600 setup | $50-400/month\n" +
                        "- **Tier 3**: $6,000+ setup | $250+/month\n\n" +
                        "### AWS Cost Targets\n" +
                        "- **Tier 1**: Max $150/month AWS costs\n" +
                        "- **Tier 2**: Max $400/month AWS costs\n" +
                        "- **Tier 3**: Max $2,000/month AWS costs\n\n" +
                        "### Client Tagging Strategy\n" +
                        "```\n" +
                        "Client: {client-id}\n" +
                        "ServiceTier: tier1|tier2|tier3\n" +
                        "StackType: {variant_name}\n" +
                        "Environment: prod|staging|dev\n" +
                        "```\n\n" +
                        "**Cost Tracking**: Automated via tags and billing APIs",
                width=12,
                height=12
            )
        )

    def _create_cost_allocation_foundation(self) -> None:
        """Create foundation for cost allocation and billing automation."""

        # IAM role for cost allocation and billing automation
        self.cost_allocation_role = iam.Role(
            self,
            "CostAllocationRole",
            role_name="WebServices-CostAllocation-Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSBillingReadOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("ResourceGroupsandTagEditorReadOnlyAccess")
            ],
            description="Role for cost allocation and billing automation across client infrastructure"
        )

        # Basic cost alarm for overall AWS spending
        cloudwatch.Alarm(
            self,
            "HighCostAlarm",
            alarm_name="WebServices-HighCostAlarm",
            alarm_description="Alert when overall AWS costs are unusually high",
            metric=cloudwatch.Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={"Currency": "USD"},
                statistic="Maximum",
                period=Duration.hours(6)
            ),
            threshold=1000,  # Alert if estimated monthly charges exceed $1000
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        ).add_alarm_action(
            cloudwatch.SnsAction(self.cost_alerts_topic)
        )

    def _create_tier_cost_tracking(self) -> None:
        """Create tier-specific cost tracking alarms based on service pricing."""

        # Tier-specific cost thresholds based on your pricing model
        tier_thresholds = {
            "tier1": 150,   # Max monthly: $150 (matches Tier 1 pricing)
            "tier2": 400,   # Max monthly: $400 (matches Tier 2 pricing)
            "tier3": 2000   # Max monthly: $2000 (enterprise buffer for all tier3 services)
        }

        tier_descriptions = {
            "tier1": "Essential Solutions - Template-based services",
            "tier2": "Professional Solutions - Custom development",
            "tier3": "Enterprise Solutions - Dual-delivery, consultation, and migration services"
        }

        # Create tier-specific cost alarms
        for tier, threshold in tier_thresholds.items():
            # Individual tier cost alarm
            tier_alarm = cloudwatch.Alarm(
                self,
                f"Tier{tier.capitalize()}CostAlarm",
                alarm_name=f"WebServices-{tier.capitalize()}-CostAlarm",
                alarm_description=f"Alert when {tier_descriptions[tier]} clients exceed ${threshold}/month threshold",
                metric=cloudwatch.Metric(
                    namespace="AWS/Billing",
                    metric_name="EstimatedCharges",
                    dimensions_map={
                        "Currency": "USD",
                        "LinkedAccount": self.account
                    },
                    statistic="Maximum",
                    period=Duration.hours(6)
                ),
                threshold=threshold,
                evaluation_periods=1,
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
            )
            tier_alarm.add_alarm_action(cloudwatch.SnsAction(self.cost_alerts_topic))

            # Per-client cost anomaly detection for higher tiers
            if tier in ["tier2", "tier3"]:
                anomaly_threshold = threshold * 0.5  # Alert at 50% of tier max

                cloudwatch.Alarm(
                    self,
                    f"Tier{tier.capitalize()}CostAnomalyAlarm",
                    alarm_name=f"WebServices-{tier.capitalize()}-CostAnomaly",
                    alarm_description=f"Detect cost anomalies for {tier_descriptions[tier]} (>${int(anomaly_threshold)} threshold)",
                    metric=cloudwatch.Metric(
                        namespace="AWS/Billing",
                        metric_name="EstimatedCharges",
                        dimensions_map={
                            "Currency": "USD",
                            "LinkedAccount": self.account
                        },
                        statistic="Average",
                        period=Duration.hours(12)
                    ),
                    threshold=anomaly_threshold,
                    evaluation_periods=2,
                    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
                ).add_alarm_action(cloudwatch.SnsAction(self.business_notifications_topic))

        # Overall business cost protection alarm
        cloudwatch.Alarm(
            self,
            "BusinessTotalCostAlarm",
            alarm_name="WebServices-BusinessTotal-CostAlarm",
            alarm_description="Alert when total business AWS costs exceed operational budget",
            metric=cloudwatch.Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={"Currency": "USD"},
                statistic="Maximum",
                period=Duration.hours(6)
            ),
            threshold=5000,  # Total business budget protection
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        ).add_alarm_action(cloudwatch.SnsAction(self.critical_alerts_topic))

    def _create_shared_storage(self) -> None:
        """Create shared storage for operational data and backups."""

        # Operational data bucket (deployment artifacts, client configs, etc.)
        self.operational_bucket = s3.Bucket(
            self,
            "OperationalBucket",
            bucket_name=f"web-services-operations-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="OperationalDataLifecycle",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ],
                    expiration=Duration.days(2555)  # 7 years retention for business records
                )
            ],
            removal_policy=RemovalPolicy.RETAIN
        )

        # Cross-client backup coordination bucket
        self.backup_coordination_bucket = s3.Bucket(
            self,
            "BackupCoordinationBucket",
            bucket_name=f"web-services-backups-{self.account}-{self.region}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="BackupRetention",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.DEEP_ARCHIVE,
                            transition_after=Duration.days(365)
                        )
                    ]
                )
            ],
            removal_policy=RemovalPolicy.RETAIN
        )

    def _apply_shared_tags(self) -> None:
        """Apply business-wide tags to all shared resources."""

        shared_tags = {
            "BusinessUnit": "WebServices",
            "Environment": "Shared",
            "CostCenter": "Operations",
            "ManagedBy": "CDK",
            "Purpose": "SharedInfrastructure",
            "BackupRequired": "Yes",
            "Compliance": "Business",
            # Comprehensive service delivery model support
            "StackVariantSupport": "30-Variants-SharedInfra",
            "ServiceDeliveryModels": "Hosted-DualDelivery-Consultation-Migration",
            "TierSupport": "T1-T2-T3",
            "ClientIsolation": "IAM-Tags",
            "CostAllocation": "Automated",
            "ServiceTiers": "Essential-Professional-Enterprise",
            "StackTypes": "Static-CMS-Framework-Commerce-Migration",
            "BillingModel": "Client-Tier-DeliveryModel-Based",
            "RevenueStreams": "Hosted-Migration",
            "MigrationSupport": "40-Percent-Revenue",
            "DualDeliveryEnabled": "Hosted-Mode-Only"
        }

        for key, value in shared_tags.items():
            Tags.of(self).add(key, value)

    @property
    def exports(self) -> Dict[str, Any]:
        """Export key resources for use by other stacks."""
        return {
            "business_hosted_zone_id": self.business_hosted_zone.hosted_zone_id,
            "business_hosted_zone_name": self.business_hosted_zone.zone_name,
            "critical_alerts_topic_arn": self.critical_alerts_topic.topic_arn,
            "business_notifications_topic_arn": self.business_notifications_topic.topic_arn,
            "cost_alerts_topic_arn": self.cost_alerts_topic.topic_arn,
            "operational_bucket_name": self.operational_bucket.bucket_name,
            "backup_coordination_bucket_name": self.backup_coordination_bucket.bucket_name,
            "cost_allocation_role_arn": self.cost_allocation_role.role_arn,
            "operational_dashboard_url": f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name=WebServicesOperations",
            # NEW: Tier-specific resources for client stacks
            "tier_cost_thresholds": {
                "tier1": 150,
                "tier2": 400,
                "tier3": 2000
            },
            "supported_stack_variants": [
                # Tier 1 Hosted-Only Stacks
                "eleventy_marketing_stack",
                "astro_portfolio_stack",
                "jekyll_github_stack",
                "eleventy_decap_cms_stack",
                "astro_tina_cms_stack",
                "astro_sanity_stack",
                "gatsby_contentful_stack",
                "astro_template_basic_stack",
                "eleventy_snipcart_stack",
                "astro_foxy_stack",
                "shopify_standard_dns_stack",

                # Tier 2 Hosted-Only Stacks
                "astro_advanced_cms_stack",
                "gatsby_headless_cms_stack",
                "nextjs_professional_headless_cms_stack",
                "nuxtjs_professional_headless_cms_stack",
                "wordpress_lightsail_stack",
                "wordpress_ecs_professional_stack",
                "shopify_aws_basic_integration_stack",

                # Tier 3 Dual-Delivery Stacks (Hosted OR Templates)
                "shopify_advanced_aws_integration_stack",
                "headless_shopify_custom_frontend_stack",
                "amplify_custom_development_stack",
                "fastapi_pydantic_api_stack",
                "fastapi_react_vue_stack",

                # Tier 3 Migration Support Stacks
                "migration_assessment_stack",
                "magento_migration_stack",
                "prestashop_migration_stack",
                "opencart_migration_stack",
                "wordpress_migration_stack",
                "legacy_cms_migration_stack",
                "custom_platform_migration_stack"
            ],
            "client_tagging_template": {
                "Client": "{client-id}",
                "ServiceTier": "{tier1|tier2|tier3}",
                "StackType": "{variant_name}",
                "Environment": "{prod|staging|dev}",
                "BillingGroup": "{client-id}-{environment}",
                "CostCenter": "{client-id}",
                "ManagedBy": "CDK"
            }
        }

