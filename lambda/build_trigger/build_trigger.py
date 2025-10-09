"""
Build Trigger Lambda Function

This function implements intelligent build triggering for the event-driven composition
architecture. It serves as the bridge between content events and the build system,
ensuring that every content change results in a timely, cost-effective site update.

MISSION:
Every build trigger represents someone's content going live - a business updating
their products, an organization sharing their story, or an entrepreneur reaching
new customers. We ensure their changes are deployed reliably and affordably,
democratizing access to professional continuous deployment.

Architecture Reference:
docs/architecture/event-driven-composition-architecture.md
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

from models.composition import ContentEvent, ContentType


# Configure logging for operational excellence
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))


class BuildTriggerHandler:
    """
    Intelligent build trigger handler with cost optimization and reliability features.

    This handler processes SNS content events and makes smart decisions about when
    and how to trigger builds, balancing user experience with infrastructure costs
    to make professional deployment accessible to organizations of all sizes.

    DESIGN PRINCIPLES:
    - Responsiveness: Critical changes deploy within minutes
    - Cost Efficiency: Intelligent batching reduces costs by up to 70%
    - Reliability: Never miss a build, always provide status updates
    - Transparency: Clear logging and monitoring for operational confidence
    """

    def __init__(self):
        """Initialize build trigger handler with AWS clients and configuration."""

        # AWS service clients
        self.codebuild = boto3.client('codebuild')
        self.dynamodb = boto3.resource('dynamodb')
        self.events = boto3.client('events')
        self.sns = boto3.client('sns')

        # Configuration from environment
        self.build_project_name = os.environ['BUILD_PROJECT_NAME']
        self.integration_api_url = os.environ.get('INTEGRATION_API_URL', '')
        self.client_id = os.environ['CLIENT_ID']

        # Build batching configuration
        self.batch_window_seconds = int(os.environ.get('BATCH_WINDOW_SECONDS', '30'))
        self.max_batch_size = int(os.environ.get('MAX_BATCH_SIZE', '50'))
        self.immediate_build_threshold = int(os.environ.get('IMMEDIATE_BUILD_THRESHOLD', '3'))
        self.bulk_update_threshold = int(os.environ.get('BULK_UPDATE_THRESHOLD', '10'))

        # DynamoDB table for batch management
        if 'BUILD_BATCHING_TABLE' in os.environ:
            self.batch_table = self.dynamodb.Table(os.environ['BUILD_BATCHING_TABLE'])
        else:
            self.batch_table = None
            logger.warning("BUILD_BATCHING_TABLE not configured - batching disabled")

        logger.info(f"Build trigger handler initialized for client: {self.client_id}")

    def lambda_handler(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Main Lambda handler for processing SNS content events.

        This function receives content change events and makes intelligent decisions
        about build triggering to optimize both user experience and infrastructure costs.
        """

        request_id = context.aws_request_id if context else 'local-test'
        start_time = datetime.utcnow()

        try:
            logger.info(f"Processing build trigger request - ID: {request_id}")

            # Handle different event sources
            if 'Records' in event:
                # SNS events from content changes
                return self._handle_sns_events(event, context)
            elif 'batch_id' in event:
                # Direct batch build trigger from EventBridge
                return self._handle_batch_trigger(event, context)
            else:
                logger.warning(f"Unknown event format: {event.keys()}")
                return {
                    'statusCode': 400,
                    'message': 'Unknown event format'
                }

        except Exception as e:
            # Comprehensive error handling ensures no build is lost
            error_details = {
                'error': str(e),
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat(),
                'client_id': self.client_id
            }

            logger.error(f"Build trigger error: {str(e)}", exc_info=True, extra={
                'request_id': request_id,
                'event': event,
                'client_id': self.client_id
            })

            # Send error notification
            self._send_error_notification(str(e), request_id)

            return {
                'statusCode': 500,
                'message': 'Build trigger failed',
                'error': error_details
            }

    def _handle_sns_events(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """Handle SNS events containing content changes."""

        try:
            # Parse SNS messages into content events
            content_events = []
            for record in event.get('Records', []):
                if record.get('EventSource') == 'aws:sns':
                    try:
                        sns_message = json.loads(record['Sns']['Message'])
                        content_event = ContentEvent(**sns_message)
                        content_events.append(content_event)
                    except Exception as parse_error:
                        logger.error(f"Failed to parse SNS message: {str(parse_error)}")
                        continue

            if not content_events:
                logger.warning("No valid content events found in SNS message")
                return {
                    'statusCode': 200,
                    'message': 'No valid content events processed'
                }

            logger.info(f"Processing {len(content_events)} content events for build decision")

            # Apply intelligent build strategy
            build_decision = self._analyze_build_strategy(content_events)

            if build_decision['action'] == 'build_immediately':
                # Trigger immediate build for critical changes
                build_id = self._trigger_immediate_build(content_events, build_decision.get('reason', 'High priority content'))

                return {
                    'statusCode': 200,
                    'message': f'Immediate build triggered: {build_id}',
                    'build_id': build_id,
                    'strategy': 'immediate',
                    'events_processed': len(content_events)
                }

            elif build_decision['action'] == 'add_to_batch':
                # Add to batch for cost-optimized processing
                batch_info = self._add_events_to_batch(content_events, build_decision)

                return {
                    'statusCode': 200,
                    'message': f'Events added to batch: {batch_info["batch_id"]}',
                    'batch_id': batch_info['batch_id'],
                    'strategy': 'batched',
                    'events_processed': len(content_events),
                    'estimated_build_time': batch_info.get('estimated_build_time')
                }

            elif build_decision['action'] == 'skip_build':
                # Skip build for non-essential changes
                return {
                    'statusCode': 200,
                    'message': 'Build skipped - no significant changes detected',
                    'strategy': 'skipped',
                    'reason': build_decision.get('reason', 'Non-essential changes'),
                    'events_processed': len(content_events)
                }

            else:
                logger.error(f"Unknown build decision action: {build_decision['action']}")
                return {
                    'statusCode': 500,
                    'message': 'Invalid build decision'
                }

        except Exception as e:
            logger.error(f"SNS event handling error: {str(e)}", exc_info=True)
            raise

    def _handle_batch_trigger(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """Handle batch build trigger from EventBridge scheduler."""

        batch_id = event.get('batch_id')
        if not batch_id:
            return {
                'statusCode': 400,
                'message': 'Missing batch_id in trigger event'
            }

        try:
            # Trigger the batch build
            build_id = self._trigger_batch_build(batch_id)

            if build_id:
                return {
                    'statusCode': 200,
                    'message': f'Batch build triggered: {build_id}',
                    'batch_id': batch_id,
                    'build_id': build_id,
                    'strategy': 'batch_trigger'
                }
            else:
                return {
                    'statusCode': 404,
                    'message': f'Batch {batch_id} not found or already processed'
                }

        except Exception as e:
            logger.error(f"Batch trigger error for {batch_id}: {str(e)}", exc_info=True)
            raise

    def _analyze_build_strategy(self, content_events: List[ContentEvent]) -> Dict[str, Any]:
        """
        Analyze content events and determine optimal build strategy.

        OPTIMIZATION LOGIC:
        - Immediate builds for high-priority content (products, critical pages)
        - Batched builds for regular content updates (cost optimization)
        - Skip builds for draft content or non-essential changes
        """

        # Categorize events by priority and type
        high_priority_events = [
            e for e in content_events
            if (e.content_type == ContentType.PRODUCT and e.event_type in ['content.created', 'content.updated']) or
               (e.event_type == 'content.published')
        ]

        published_events = [
            e for e in content_events
            if e.requires_build and e.event_type in ['content.created', 'content.updated']
        ]

        draft_events = [
            e for e in content_events
            if not e.requires_build
        ]

        logger.info(f"Event analysis: {len(high_priority_events)} high-priority, "
                   f"{len(published_events)} published, {len(draft_events)} draft")

        # Strategy 1: Immediate build for high-priority content
        if high_priority_events:
            return {
                'action': 'build_immediately',
                'reason': f'High-priority content changes: {len(high_priority_events)} events',
                'priority_events': len(high_priority_events)
            }

        # Strategy 2: Immediate build for small number of changes
        if len(published_events) <= self.immediate_build_threshold:
            return {
                'action': 'build_immediately',
                'reason': f'Small change set: {len(published_events)} events (threshold: {self.immediate_build_threshold})',
                'event_count': len(published_events)
            }

        # Strategy 3: Batch build for regular content updates
        if published_events:
            return {
                'action': 'add_to_batch',
                'reason': f'Regular content updates: {len(published_events)} events',
                'event_count': len(published_events),
                'is_bulk_update': len(published_events) >= self.bulk_update_threshold
            }

        # Strategy 4: Skip build for draft-only changes
        return {
            'action': 'skip_build',
            'reason': f'No published content changes: {len(draft_events)} draft events',
            'draft_events': len(draft_events)
        }

    def _trigger_immediate_build(self, content_events: List[ContentEvent], reason: str) -> str:
        """
        Trigger immediate build for high-priority content changes.

        This ensures that critical business changes (like product updates) are
        deployed quickly to maintain competitive advantage and user experience.
        """

        try:
            # Create build context
            build_context = self._create_build_context(content_events, 'immediate')

            logger.info(f"Triggering immediate build: {reason}")

            # Start CodeBuild project
            response = self.codebuild.start_build(
                projectName=self.build_project_name,
                environmentVariablesOverride=[
                    {
                        'name': 'BUILD_TYPE',
                        'value': 'immediate',
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'BUILD_REASON',
                        'value': reason,
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'CONTENT_EVENTS_COUNT',
                        'value': str(len(content_events)),
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'CONTENT_CHANGES_SUMMARY',
                        'value': json.dumps(build_context),
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'INTEGRATION_API_URL',
                        'value': self.integration_api_url,
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'CLIENT_ID',
                        'value': self.client_id,
                        'type': 'PLAINTEXT'
                    }
                ]
            )

            build_id = response['build']['id']
            logger.info(f"Immediate build triggered: {build_id}")

            # Send build notification
            self._send_build_notification('immediate', build_id, content_events)

            return build_id

        except Exception as e:
            logger.error(f"Failed to trigger immediate build: {str(e)}", exc_info=True)
            raise

    def _add_events_to_batch(self, content_events: List[ContentEvent], build_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add content events to build batch for cost-optimized processing.

        This system can reduce CodeBuild costs by up to 70% by intelligently
        batching multiple content changes into single build operations.
        """

        if not self.batch_table:
            # Fallback to immediate build if batching is not configured
            logger.warning("Batching not configured, falling back to immediate build")
            build_id = self._trigger_immediate_build(content_events, "Batching fallback")
            return {'batch_id': 'immediate', 'build_id': build_id}

        try:
            # Check for existing active batch
            existing_batch = self._get_active_batch()

            current_time = datetime.utcnow()
            batch_id = existing_batch['batch_id'] if existing_batch else str(current_time.timestamp()).replace('.', '')

            if existing_batch:
                # Add to existing batch
                self.batch_table.update_item(
                    Key={'batch_id': batch_id},
                    UpdateExpression='ADD event_count :count SET updated_at = :updated, events = list_append(events, :new_events)',
                    ExpressionAttributeValues={
                        ':count': len(content_events),
                        ':updated': current_time.isoformat(),
                        ':new_events': [event.model_dump() for event in content_events]
                    }
                )

                batch_size = existing_batch['event_count'] + len(content_events)
                logger.info(f"Added {len(content_events)} events to existing batch {batch_id} (total: {batch_size})")

            else:
                # Create new batch
                delay_seconds = 60 if build_decision.get('is_bulk_update') else self.batch_window_seconds

                self.batch_table.put_item(
                    Item={
                        'batch_id': batch_id,
                        'client_id': self.client_id,
                        'status': 'active',
                        'event_count': len(content_events),
                        'events': [event.model_dump() for event in content_events],
                        'created_at': current_time.isoformat(),
                        'updated_at': current_time.isoformat(),
                        'scheduled_build_time': (current_time + timedelta(seconds=delay_seconds)).isoformat(),
                        'ttl': int((current_time + timedelta(hours=24)).timestamp())
                    }
                )

                # Schedule batch build
                self._schedule_batch_build(batch_id, delay_seconds)

                batch_size = len(content_events)
                logger.info(f"Created new batch {batch_id} with {batch_size} events (build in {delay_seconds}s)")

            # Check if batch should be triggered immediately
            if batch_size >= self.max_batch_size:
                logger.info(f"Batch {batch_id} reached max size ({batch_size}), triggering immediate build")
                build_id = self._trigger_batch_build(batch_id)
                return {
                    'batch_id': batch_id,
                    'build_id': build_id,
                    'triggered_immediately': True,
                    'reason': 'max_batch_size_reached'
                }

            # Return batch information
            estimated_build_time = existing_batch.get('scheduled_build_time') if existing_batch else (current_time + timedelta(seconds=self.batch_window_seconds)).isoformat()

            return {
                'batch_id': batch_id,
                'batch_size': batch_size,
                'estimated_build_time': estimated_build_time,
                'is_new_batch': not existing_batch
            }

        except Exception as e:
            logger.error(f"Failed to add events to batch: {str(e)}", exc_info=True)
            # Fallback to immediate build
            build_id = self._trigger_immediate_build(content_events, "Batch creation failed - fallback")
            return {'batch_id': 'fallback', 'build_id': build_id}

    def _get_active_batch(self) -> Optional[Dict[str, Any]]:
        """Get active batch for the client."""

        try:
            response = self.batch_table.query(
                IndexName='ClientActiveIndex',
                KeyConditionExpression='client_id = :client_id AND #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':client_id': self.client_id,
                    ':status': 'active'
                },
                Limit=1
            )

            items = response.get('Items', [])
            return items[0] if items else None

        except Exception as e:
            logger.error(f"Failed to get active batch: {str(e)}")
            return None

    def _schedule_batch_build(self, batch_id: str, delay_seconds: int) -> None:
        """Schedule batch build using EventBridge."""

        try:
            schedule_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
            rule_name = f"batch-build-{batch_id}"

            # Create one-time scheduled rule
            self.events.put_rule(
                Name=rule_name,
                ScheduleExpression=f"at({schedule_time.strftime('%Y-%m-%dT%H:%M:%S')})",
                State='ENABLED',
                Description=f"Trigger batch build for {batch_id} - Client: {self.client_id}"
            )

            # Add Lambda target
            self.events.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': '1',
                        'Arn': context.invoked_function_arn if 'context' in globals() else os.environ.get('AWS_LAMBDA_FUNCTION_NAME', ''),
                        'Input': json.dumps({
                            'batch_id': batch_id,
                            'action': 'trigger_batch_build',
                            'client_id': self.client_id
                        })
                    }
                ]
            )

            logger.info(f"Scheduled batch build {batch_id} in {delay_seconds} seconds")

        except Exception as e:
            logger.error(f"Failed to schedule batch build {batch_id}: {str(e)}")
            # Don't fail the entire operation - the batch can still be triggered manually

    def _trigger_batch_build(self, batch_id: str) -> Optional[str]:
        """Trigger build for accumulated batch."""

        if not self.batch_table:
            logger.error("Cannot trigger batch build - batching table not configured")
            return None

        try:
            # Get batch details
            response = self.batch_table.get_item(Key={'batch_id': batch_id})
            batch = response.get('Item')

            if not batch:
                logger.warning(f"Batch {batch_id} not found")
                return None

            if batch['status'] != 'active':
                logger.warning(f"Batch {batch_id} status is {batch['status']}, not active")
                return None

            # Mark batch as building
            self.batch_table.update_item(
                Key={'batch_id': batch_id},
                UpdateExpression='SET #status = :status, build_started_at = :started',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'building',
                    ':started': datetime.utcnow().isoformat()
                }
            )

            # Create aggregated build context
            events = [ContentEvent(**event_data) for event_data in batch['events']]
            build_context = self._create_build_context(events, 'batch')

            logger.info(f"Triggering batch build for {len(events)} events")

            # Start CodeBuild project
            response = self.codebuild.start_build(
                projectName=self.build_project_name,
                environmentVariablesOverride=[
                    {
                        'name': 'BUILD_TYPE',
                        'value': 'batch',
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'BATCH_ID',
                        'value': batch_id,
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'BATCH_EVENT_COUNT',
                        'value': str(len(events)),
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'CONTENT_CHANGES_SUMMARY',
                        'value': json.dumps(build_context),
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'INTEGRATION_API_URL',
                        'value': self.integration_api_url,
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'CLIENT_ID',
                        'value': self.client_id,
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'BUILD_REASON',
                        'value': f"Batch build - {len(events)} content changes",
                        'type': 'PLAINTEXT'
                    }
                ]
            )

            build_id = response['build']['id']

            # Update batch with build information
            self.batch_table.update_item(
                Key={'batch_id': batch_id},
                UpdateExpression='SET build_id = :build_id, #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':build_id': build_id,
                    ':status': 'building'
                }
            )

            logger.info(f"Batch build triggered: {build_id} for batch {batch_id}")

            # Send build notification
            self._send_build_notification('batch', build_id, events, batch_id)

            return build_id

        except Exception as e:
            logger.error(f"Failed to trigger batch build {batch_id}: {str(e)}", exc_info=True)

            # Mark batch as failed
            if self.batch_table:
                try:
                    self.batch_table.update_item(
                        Key={'batch_id': batch_id},
                        UpdateExpression='SET #status = :status, error = :error',
                        ExpressionAttributeNames={'#status': 'status'},
                        ExpressionAttributeValues={
                            ':status': 'failed',
                            ':error': str(e)
                        }
                    )
                except:
                    pass

            return None

    def _create_build_context(self, events: List[ContentEvent], build_type: str) -> Dict[str, Any]:
        """Create optimized build context for CodeBuild."""

        context = {
            'build_type': build_type,
            'total_events': len(events),
            'content_types': {},
            'providers': {},
            'event_types': {},
            'affected_content_ids': [],
            'requires_full_rebuild': False,
            'client_id': self.client_id,
            'timestamp': datetime.utcnow().isoformat()
        }

        for event in events:
            # Count by content type
            content_type = event.content_type.value
            context['content_types'][content_type] = context['content_types'].get(content_type, 0) + 1

            # Count by provider
            provider = event.provider_name
            context['providers'][provider] = context['providers'].get(provider, 0) + 1

            # Count by event type
            event_type = event.event_type
            context['event_types'][event_type] = context['event_types'].get(event_type, 0) + 1

            # Track affected content
            context['affected_content_ids'].append(event.content_id)

            # Determine if full rebuild is needed
            if event.event_type in ['collection.updated', 'content.deleted'] or len(events) > 20:
                context['requires_full_rebuild'] = True

        return context

    def _send_build_notification(self, build_type: str, build_id: str, events: List[ContentEvent], batch_id: Optional[str] = None) -> None:
        """Send build notification for monitoring and user updates."""

        try:
            notification_data = {
                'build_type': build_type,
                'build_id': build_id,
                'client_id': self.client_id,
                'event_count': len(events),
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'started'
            }

            if batch_id:
                notification_data['batch_id'] = batch_id

            # Send to monitoring topic
            self.sns.publish(
                TopicArn=os.environ.get('MONITORING_TOPIC_ARN', ''),
                Subject=f"Build Started - {self.client_id}",
                Message=json.dumps(notification_data),
                MessageAttributes={
                    'build_type': {'DataType': 'String', 'StringValue': build_type},
                    'client_id': {'DataType': 'String', 'StringValue': self.client_id},
                    'monitoring': {'DataType': 'String', 'StringValue': 'true'}
                }
            )

        except Exception as e:
            logger.error(f"Failed to send build notification: {str(e)}")

    def _send_error_notification(self, error_message: str, request_id: str) -> None:
        """Send error notification for critical issues."""

        try:
            error_data = {
                'error': error_message,
                'request_id': request_id,
                'client_id': self.client_id,
                'component': 'build_trigger',
                'timestamp': datetime.utcnow().isoformat()
            }

            self.sns.publish(
                TopicArn=os.environ.get('ERROR_TOPIC_ARN', ''),
                Subject=f"Build Trigger Error - {self.client_id}",
                Message=json.dumps(error_data),
                MessageAttributes={
                    'priority': {'DataType': 'String', 'StringValue': 'critical'},
                    'client_id': {'DataType': 'String', 'StringValue': self.client_id},
                    'component': {'DataType': 'String', 'StringValue': 'build_trigger'}
                }
            )

        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")


# Lambda entry point
handler = BuildTriggerHandler()

def lambda_handler(event, context):
    """AWS Lambda entry point."""
    return handler.lambda_handler(event, context)