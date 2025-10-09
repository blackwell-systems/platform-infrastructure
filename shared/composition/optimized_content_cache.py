"""
Optimized Content Cache

This module implements optimized DynamoDB operations using GSI queries
instead of expensive table scans, and adds event filtering to reduce
Lambda invocations and improve overall system performance.

Addresses the DynamoDB schema efficiency and event filtering optimization
recommendations from the event-driven composition architecture review.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging
import json
from dataclasses import dataclass

from models.composition import UnifiedContent, ContentEvent, ContentType


logger = logging.getLogger(__name__)


@dataclass
class ContentQuery:
    """Optimized content query parameters"""
    client_id: str
    content_type: Optional[ContentType] = None
    provider_name: Optional[str] = None
    status: Optional[str] = None
    limit: int = 100
    last_updated_after: Optional[datetime] = None


@dataclass
class QueryResult:
    """Query result with pagination support"""
    items: List[Dict[str, Any]]
    count: int
    last_evaluated_key: Optional[Dict[str, Any]] = None
    query_stats: Optional[Dict[str, Any]] = None


class OptimizedContentCache:
    """
    Optimized content cache using GSI queries instead of table scans
    for better performance and cost efficiency.
    """

    def __init__(self, table_name: str, region_name: str = 'us-east-1'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

        # GSI names
        self.CLIENT_CONTENT_TYPE_INDEX = "ClientContentTypeIndex"
        self.PROVIDER_UPDATE_INDEX = "ProviderUpdateIndex"
        self.STATUS_UPDATE_INDEX = "StatusUpdateIndex"  # New GSI for status queries

    def put_content(self, content: UnifiedContent, client_id: str) -> bool:
        """
        Store unified content with optimized indexing structure.

        Args:
            content: UnifiedContent object to store
            client_id: Client identifier

        Returns:
            True if stored successfully, False otherwise
        """

        try:
            # Prepare item with optimized key structure
            item = {
                # Primary keys
                'content_id': content.id,
                'content_type_provider': f"{content.content_type.value}#{content.provider_name}",

                # GSI keys for efficient querying
                'client_id': client_id,
                'content_type': content.content_type.value,
                'provider_name': content.provider_name,
                'status': content.status.value,
                'updated_at': content.updated_at.isoformat(),

                # Additional indexed fields
                'created_at': content.created_at.isoformat(),
                'synced_at': content.synced_at.isoformat(),

                # TTL for automatic cleanup (30 days)
                'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp()),

                # Full content data
                'data': content.model_dump(),

                # Search optimization fields
                'title_lower': content.title.lower(),
                'tags': content.tags,
                'has_price': content.price is not None,
                'is_published': content.status.value == 'published'
            }

            # Store item
            self.table.put_item(Item=item)

            logger.info(f"Stored content {content.id} for client {client_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store content {content.id}: {str(e)}")
            return False

    def query_content_optimized(self, query: ContentQuery) -> QueryResult:
        """
        Query content using optimized GSI queries instead of table scans.

        Args:
            query: ContentQuery parameters

        Returns:
            QueryResult with items and metadata
        """

        try:
            # Choose optimal query strategy based on parameters
            if query.content_type and query.provider_name:
                return self._query_by_content_type_provider(query)
            elif query.content_type:
                return self._query_by_content_type(query)
            elif query.provider_name:
                return self._query_by_provider(query)
            else:
                return self._query_by_client(query)

        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return QueryResult(items=[], count=0, query_stats={'error': str(e)})

    def _query_by_content_type_provider(self, query: ContentQuery) -> QueryResult:
        """
        Most efficient query: client_id + content_type + provider_name.
        Uses ClientContentTypeIndex with filter expression for provider.
        """

        key_condition = Key('client_id').eq(query.client_id) & Key('content_type').eq(query.content_type.value)

        filter_expression = Attr('provider_name').eq(query.provider_name)

        if query.status:
            filter_expression = filter_expression & Attr('status').eq(query.status)

        if query.last_updated_after:
            filter_expression = filter_expression & Attr('updated_at').gte(query.last_updated_after.isoformat())

        response = self.table.query(
            IndexName=self.CLIENT_CONTENT_TYPE_INDEX,
            KeyConditionExpression=key_condition,
            FilterExpression=filter_expression,
            Limit=query.limit
        )

        return QueryResult(
            items=[item['data'] for item in response['Items']],
            count=response['Count'],
            last_evaluated_key=response.get('LastEvaluatedKey'),
            query_stats={
                'consumed_capacity': response.get('ConsumedCapacity'),
                'query_type': 'content_type_provider_gsi'
            }
        )

    def _query_by_content_type(self, query: ContentQuery) -> QueryResult:
        """
        Query by client_id and content_type using ClientContentTypeIndex.
        More efficient than table scan.
        """

        key_condition = Key('client_id').eq(query.client_id) & Key('content_type').eq(query.content_type.value)

        filter_expression = None
        if query.status:
            filter_expression = Attr('status').eq(query.status)

        if query.last_updated_after:
            condition = Attr('updated_at').gte(query.last_updated_after.isoformat())
            filter_expression = condition if filter_expression is None else filter_expression & condition

        query_params = {
            'IndexName': self.CLIENT_CONTENT_TYPE_INDEX,
            'KeyConditionExpression': key_condition,
            'Limit': query.limit
        }

        if filter_expression:
            query_params['FilterExpression'] = filter_expression

        response = self.table.query(**query_params)

        return QueryResult(
            items=[item['data'] for item in response['Items']],
            count=response['Count'],
            last_evaluated_key=response.get('LastEvaluatedKey'),
            query_stats={
                'consumed_capacity': response.get('ConsumedCapacity'),
                'query_type': 'content_type_gsi'
            }
        )

    def _query_by_provider(self, query: ContentQuery) -> QueryResult:
        """
        Query by provider_name using ProviderUpdateIndex.
        Efficient for provider-specific queries.
        """

        key_condition = Key('provider_name').eq(query.provider_name)

        filter_expression = Attr('client_id').eq(query.client_id)

        if query.status:
            filter_expression = filter_expression & Attr('status').eq(query.status)

        if query.last_updated_after:
            key_condition = key_condition & Key('updated_at').gte(query.last_updated_after.isoformat())

        response = self.table.query(
            IndexName=self.PROVIDER_UPDATE_INDEX,
            KeyConditionExpression=key_condition,
            FilterExpression=filter_expression,
            Limit=query.limit
        )

        return QueryResult(
            items=[item['data'] for item in response['Items']],
            count=response['Count'],
            last_evaluated_key=response.get('LastEvaluatedKey'),
            query_stats={
                'consumed_capacity': response.get('ConsumedCapacity'),
                'query_type': 'provider_gsi'
            }
        )

    def _query_by_client(self, query: ContentQuery) -> QueryResult:
        """
        Fallback query by client_id only.
        Less efficient but still better than full table scan.
        """

        key_condition = Key('client_id').eq(query.client_id)

        filter_expression = None
        if query.status:
            filter_expression = Attr('status').eq(query.status)

        if query.last_updated_after:
            condition = Attr('updated_at').gte(query.last_updated_after.isoformat())
            filter_expression = condition if filter_expression is None else filter_expression & condition

        query_params = {
            'IndexName': self.CLIENT_CONTENT_TYPE_INDEX,
            'KeyConditionExpression': key_condition,
            'Limit': query.limit
        }

        if filter_expression:
            query_params['FilterExpression'] = filter_expression

        response = self.table.query(**query_params)

        return QueryResult(
            items=[item['data'] for item in response['Items']],
            count=response['Count'],
            last_evaluated_key=response.get('LastEvaluatedKey'),
            query_stats={
                'consumed_capacity': response.get('ConsumedCapacity'),
                'query_type': 'client_gsi'
            }
        )

    def get_content_by_id(self, content_id: str, content_type_provider: str) -> Optional[Dict[str, Any]]:
        """
        Get specific content by ID using primary key lookup.
        Most efficient single-item query.

        Args:
            content_id: Content identifier
            content_type_provider: Composite key "content_type#provider"

        Returns:
            Content data or None if not found
        """

        try:
            response = self.table.get_item(
                Key={
                    'content_id': content_id,
                    'content_type_provider': content_type_provider
                }
            )

            if 'Item' in response:
                return response['Item']['data']

            return None

        except Exception as e:
            logger.error(f"Failed to get content {content_id}: {str(e)}")
            return None

    def batch_get_content(self, content_refs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """
        Batch get multiple content items efficiently.

        Args:
            content_refs: List of (content_id, content_type_provider) tuples

        Returns:
            List of content data dictionaries
        """

        try:
            # Prepare batch request keys
            request_keys = [
                {
                    'content_id': content_id,
                    'content_type_provider': content_type_provider
                }
                for content_id, content_type_provider in content_refs
            ]

            # Batch get items (max 100 items per request)
            items = []
            for i in range(0, len(request_keys), 100):
                batch_keys = request_keys[i:i+100]

                response = self.dynamodb.batch_get_item(
                    RequestItems={
                        self.table_name: {
                            'Keys': batch_keys
                        }
                    }
                )

                batch_items = response.get('Responses', {}).get(self.table_name, [])
                items.extend([item['data'] for item in batch_items])

            return items

        except Exception as e:
            logger.error(f"Batch get failed: {str(e)}")
            return []

    def delete_content(self, content_id: str, content_type_provider: str) -> bool:
        """
        Delete content by ID.

        Args:
            content_id: Content identifier
            content_type_provider: Composite key "content_type#provider"

        Returns:
            True if deleted successfully, False otherwise
        """

        try:
            self.table.delete_item(
                Key={
                    'content_id': content_id,
                    'content_type_provider': content_type_provider
                }
            )

            logger.info(f"Deleted content {content_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete content {content_id}: {str(e)}")
            return False

    def get_cache_statistics(self, client_id: str) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring and optimization.

        Args:
            client_id: Client identifier

        Returns:
            Dictionary with cache statistics
        """

        try:
            # Query for basic statistics using GSI
            response = self.table.query(
                IndexName=self.CLIENT_CONTENT_TYPE_INDEX,
                KeyConditionExpression=Key('client_id').eq(client_id),
                Select='COUNT'
            )

            total_items = response['Count']

            # Get content type breakdown
            content_types = {}
            for content_type in ['product', 'article', 'page', 'collection']:
                response = self.table.query(
                    IndexName=self.CLIENT_CONTENT_TYPE_INDEX,
                    KeyConditionExpression=Key('client_id').eq(client_id) & Key('content_type').eq(content_type),
                    Select='COUNT'
                )
                content_types[content_type] = response['Count']

            return {
                'client_id': client_id,
                'total_items': total_items,
                'content_types': content_types,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get cache statistics: {str(e)}")
            return {'error': str(e)}


class EventFilteringSystem:
    """
    Event filtering system to reduce redundant Lambda invocations
    and improve system efficiency.
    """

    def __init__(self):
        self.sns = boto3.client('sns')

    def publish_filtered_event(
        self,
        topic_arn: str,
        event: ContentEvent,
        environment: str = 'prod'
    ) -> str:
        """
        Publish event with message attributes for filtering.

        Args:
            topic_arn: SNS topic ARN
            event: ContentEvent to publish
            environment: Environment context

        Returns:
            Message ID
        """

        # Enhanced message attributes for filtering
        message_attributes = {
            'event_type': {'DataType': 'String', 'StringValue': event.event_type},
            'content_type': {'DataType': 'String', 'StringValue': event.content_type.value},
            'provider_name': {'DataType': 'String', 'StringValue': event.provider_name},
            'client_id': {'DataType': 'String', 'StringValue': event.client_id},
            'environment': {'DataType': 'String', 'StringValue': environment},
            'requires_build': {'DataType': 'String', 'StringValue': str(event.requires_build).lower()},
            'priority': {'DataType': 'String', 'StringValue': self._calculate_event_priority(event)},
            'batch_eligible': {'DataType': 'String', 'StringValue': str(self._is_batch_eligible(event)).lower()}
        }

        # Add provider-specific attributes
        if event.provider_name.startswith('shopify'):
            message_attributes['ecommerce_platform'] = {'DataType': 'String', 'StringValue': 'shopify'}
        elif event.provider_name in ['snipcart', 'foxy']:
            message_attributes['ecommerce_platform'] = {'DataType': 'String', 'StringValue': 'third_party'}

        # Add schema versioning for future-proofing
        event_data = event.model_dump()
        event_data["schema_version"] = "1.0"

        response = self.sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(event_data),
            MessageAttributes=message_attributes
        )

        return response['MessageId']

    def _calculate_event_priority(self, event: ContentEvent) -> str:
        """Calculate event priority for filtering and processing order"""

        # High priority: Published content changes, product updates
        if event.event_type in ['content.created', 'content.updated'] and event.content_type == ContentType.PRODUCT:
            return 'high'

        # Medium priority: Other content changes
        if event.event_type in ['content.created', 'content.updated']:
            return 'medium'

        # Low priority: Inventory updates, deletions
        return 'low'

    def _is_batch_eligible(self, event: ContentEvent) -> bool:
        """Determine if event is eligible for batching"""

        # Batch eligible: Inventory updates, bulk content changes
        batch_eligible_events = ['inventory.updated', 'content.updated']
        return event.event_type in batch_eligible_events

    def create_filtered_subscription(
        self,
        topic_arn: str,
        endpoint_arn: str,
        filter_policy: Dict[str, Any],
        subscription_name: str
    ) -> str:
        """
        Create SNS subscription with message filtering.

        Args:
            topic_arn: SNS topic ARN
            endpoint_arn: Lambda function ARN or other endpoint
            filter_policy: SNS filter policy
            subscription_name: Name for the subscription

        Returns:
            Subscription ARN
        """

        response = self.sns.subscribe(
            TopicArn=topic_arn,
            Protocol='lambda',
            Endpoint=endpoint_arn,
            Attributes={
                'FilterPolicy': json.dumps(filter_policy),
                'FilterPolicyScope': 'MessageAttributes'
            }
        )

        logger.info(f"Created filtered subscription {subscription_name}: {response['SubscriptionArn']}")
        return response['SubscriptionArn']


# Example filter policies for different use cases
BUILD_TRIGGER_FILTER_POLICY = {
    "requires_build": ["true"],
    "environment": ["prod", "staging"],
    "priority": ["high", "medium"]
}

MONITORING_FILTER_POLICY = {
    "event_type": ["content.created", "content.updated", "content.deleted"],
    "environment": ["prod"]
}

SHOPIFY_SPECIFIC_FILTER_POLICY = {
    "ecommerce_platform": ["shopify"],
    "requires_build": ["true"]
}


# Usage example
def optimized_lambda_handler(event, context):
    """
    Example optimized Lambda handler
    """

    # Initialize optimized cache
    cache = OptimizedContentCache(table_name=os.environ['CONTENT_CACHE_TABLE'])

    # Query content efficiently using GSI
    query = ContentQuery(
        client_id=os.environ['CLIENT_ID'],
        content_type=ContentType.PRODUCT,
        provider_name='shopify_basic',
        limit=50
    )

    result = cache.query_content_optimized(query)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'content_count': result.count,
            'query_stats': result.query_stats,
            'items': result.items[:5]  # Return first 5 items as example
        })
    }