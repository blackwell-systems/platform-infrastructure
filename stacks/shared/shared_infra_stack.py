"""
Shared Infrastructure Stack

Provides operational infrastructure shared across all clients:
- Business domain management (Route53)
- Centralized operational monitoring
- Cost allocation and tagging foundation
- Basic security and compliance baselines

This is NOT for client workloads - it's for running the web services business.
"""

from aws_cdk import (
    Stack,
    Tags,
    aws_route53 as route53,
    aws_sns as sns,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_s3 as s3,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
from typing import Dict, Any


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
        self._create_cost_allocation_foundation()
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
            "Compliance": "Business"
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
            "operational_dashboard_url": f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name=WebServicesOperations"
        }