import boto3
import os
import sys
import uuid
from datetime import datetime, timezone
import botocore.exceptions

class Ddb:
    @staticmethod
    def client():
        endpoint_url = os.getenv("DYNAMODB_ENDPOINT")
        attrs = {'endpoint_url': endpoint_url} if endpoint_url else {}
        return boto3.client('dynamodb', **attrs)


    @staticmethod
    def list_message_groups(client, my_user_uuid, limit=20):
        try:
            # Consider using current month instead of year for more relevant messages
            current_time = datetime.now(timezone.utc)
            time_prefix = current_time.strftime('%Y-%m')  # Year-month format
            
            query_params = {
                'TableName': 'cruddur-messages',
                'KeyConditionExpression': 'pk = :pk AND begins_with(sk, :time_prefix)',
                'ScanIndexForward': False,
                'Limit': limit,
                'ExpressionAttributeValues': {
                    ':time_prefix': {'S': time_prefix},
                    ':pk': {'S': f"GRP#{my_user_uuid}"}
                },
                'ReturnConsumedCapacity': 'TOTAL'
            }
            
            print('query-params:', query_params)
            response = client.query(**query_params)
            print('consumed capacity:', response.get('ConsumedCapacity'))
            
            items = response.get('Items', [])
            results = []
            
            for item in items:
                results.append({
                    'uuid': item.get('message_group_uuid', {}).get('S', ''),
                    'display_name': item.get('user_display_name', {}).get('S', ''),
                    'handle': item.get('user_handle', {}).get('S', ''),
                    'message': item.get('message', {}).get('S', ''),
                    'created_at': item['sk']['S']  # Assuming sk always exists
                })
                
            return results
            
        except client.exceptions.ResourceNotFoundException:
            print("Error: Table not found")
            return []
        except Exception as e:
            print(f"DynamoDB query error: {str(e)}")
            raise

    @staticmethod
    def list_messages(client, message_group_uuid, limit=100):
        year_prefix = str(datetime.now().year)
        table_name = 'cruddur-messages'

        query_params = {
            'TableName': table_name,
            'KeyConditionExpression': 'pk = :pk AND begins_with(sk, :year)',
            'ScanIndexForward': True,  # earliest first
            'Limit': limit,
            'ExpressionAttributeValues': {
                ':year': {'S': year_prefix},
                ':pk': {'S': f"MSG#{message_group_uuid}"}
            }
        }

        response = client.query(**query_params)
        items = response.get('Items', [])

        results = []
        for item in items:
            created_at = item.get('sk', {}).get('S')
            results.append({
                'uuid': item.get('message_uuid', {}).get('S'),
                'display_name': item.get('user_display_name', {}).get('S'),
                'handle': item.get('user_handle', {}).get('S'),
                'message': item.get('message', {}).get('S'),
                'created_at': created_at
            })
        return results

    @staticmethod
    def create_message(client, message_group_uuid, message, my_user_uuid, my_user_display_name, my_user_handle):
        now_iso = datetime.now(timezone.utc).astimezone().isoformat()
        message_uuid = str(uuid.uuid4())
        table_name = 'cruddur-messages'

        record = {
            'pk':   {'S': f"MSG#{message_group_uuid}"},
            'sk':   {'S': now_iso},
            'message': {'S': message},
            'message_uuid': {'S': message_uuid},
            'user_uuid': {'S': my_user_uuid},
            'user_display_name': {'S': my_user_display_name},
            'user_handle': {'S': my_user_handle}
        }

        print("🔍 Putting message item:", record)
        response = client.put_item(
            TableName=table_name,
            Item=record
        )
        print("✅ put_item response:", response)
        return {
            'message_group_uuid': message_group_uuid,
            'uuid': my_user_uuid,
            'display_name': my_user_display_name,
            'handle': my_user_handle,
            'message': message,
            'created_at': now_iso
        }

    @staticmethod
    def create_message_group(
        client,
        initial_message,
        my_user_uuid,
        my_user_display_name,
        my_user_handle,
        other_user_uuid,
        other_user_display_name,
        other_user_handle
    ):
        """
        Atomically creates:
          * message group metadata for both participants
          * initial message in the group
        """
        table_name = 'cruddur-messages'
        message_group_uuid = str(uuid.uuid4())
        message_uuid = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).astimezone().isoformat()

        print("== create_message_group start")
        my_message_group_item = {
            'pk': {'S': f"GRP#{my_user_uuid}"},
            'sk': {'S': now_iso},
            'message_group_uuid': {'S': message_group_uuid},
            'message': {'S': initial_message},
            'user_uuid': {'S': other_user_uuid},
            'user_display_name': {'S': other_user_display_name},
            'user_handle': {'S': other_user_handle}
        }

        other_message_group_item = {
            'pk': {'S': f"GRP#{other_user_uuid}"},
            'sk': {'S': now_iso},
            'message_group_uuid': {'S': message_group_uuid},
            'message': {'S': initial_message},
            'user_uuid': {'S': my_user_uuid},
            'user_display_name': {'S': my_user_display_name},
            'user_handle': {'S': my_user_handle}
        }

        initial_chat_message = {
            'pk': {'S': f"MSG#{message_group_uuid}"},
            'sk': {'S': now_iso},
            'message_group_uuid': {'S': message_group_uuid},
            'message': {'S': initial_message},
            'message_uuid': {'S': message_uuid},
            'user_uuid': {'S': my_user_uuid},
            'user_display_name': {'S': my_user_display_name},
            'user_handle': {'S': my_user_handle}
        }

        transact_items = [
            {'Put': {'TableName': table_name, 'Item': my_message_group_item}},
            {'Put': {'TableName': table_name, 'Item': other_message_group_item}},
            {'Put': {'TableName': table_name, 'Item': initial_chat_message}}
        ]

        try:
            print("== create_message_group executing transaction")
            client.transact_write_items(TransactItems=transact_items)
            return {
                'message_group_uuid': message_group_uuid,
                'last_message_at': now_iso
            }
        except botocore.exceptions.ClientError as e:
            print("== create_message_group error")
            print(e)
            raise
