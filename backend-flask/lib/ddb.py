
import os
import uuid
from datetime import datetime, timezone

import boto3
import botocore.exceptions
from flask import current_app


# -----------------------------
# DynamoDB Helper / Data Layer
# -----------------------------
class Ddb:
    TABLE_NAME = "cruddur-messages"

    @staticmethod
    def client():
        endpoint_url = os.getenv("DYNAMODB_ENDPOINT")
        attrs = {'endpoint_url': endpoint_url} if endpoint_url else {}
        return boto3.client("dynamodb", **attrs)

    @staticmethod
    def list_message_groups(client, my_user_uuid, limit=20):
        """
        Returns the message group metadata rows for this user (most recent first).
        """
        try:
            response = client.query(
                TableName=Ddb.TABLE_NAME,
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={
                    ":pk": {"S": f"GRP#{my_user_uuid}"}
                },
                ScanIndexForward=False,  # newest first
                Limit=limit,
                ReturnConsumedCapacity="TOTAL"
            )

            items = response.get("Items", [])
            results = []
            for item in items:
                results.append({
                    "uuid": item.get("message_group_uuid", {}).get("S", ""),
                    "display_name": item.get("user_display_name", {}).get("S", ""),
                    "handle": item.get("user_handle", {}).get("S", ""),
                    "message": item.get("message", {}).get("S", ""),
                    "created_at": item.get("sk", {}).get("S", "")
                })
            return results

        except client.exceptions.ResourceNotFoundException:
            current_app.logger.error("DynamoDB table not found")
            return []
        except Exception as e:
            current_app.logger.exception("Error listing message groups")
            raise

    @staticmethod
    def list_messages(client, message_group_uuid, limit=100, chronological=True):
        """
        Returns the messages in a given group, ordered by created_at.
        """
        try:
            response = client.query(
                TableName=Ddb.TABLE_NAME,
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={
                    ":pk": {"S": f"MSG#{message_group_uuid}"}
                },
                ScanIndexForward=chronological,  # True = oldest first
                Limit=limit
            )
            items = response.get("Items", [])
            results = []
            for item in items:
                results.append({
                    "uuid": item.get("message_uuid", {}).get("S"),  # may be absent if legacy
                    "display_name": item.get("user_display_name", {}).get("S", ""),
                    "handle": item.get("user_handle", {}).get("S", ""),
                    "message": item.get("message", {}).get("S", ""),
                    "created_at": item.get("sk", {}).get("S", "")
                })
            return results
        except Exception as e:
            current_app.logger.exception("Error listing messages")
            raise

    # @staticmethod
    # def _update_group_metadata(client, message_group_uuid, participant_uuid, other_uuid,
    #                            other_display_name, other_handle, latest_message, last_message_at):
    #     """
    #     Updates (or creates) a GRP#<participant_uuid> item to reflect newest snippet.
    #     """
    #     # Overwrite sk and message to reflect latest
    #     client.put_item(
    #         TableName=Ddb.TABLE_NAME,
    #         Item={
    #             "pk": {"S": f"GRP#{participant_uuid}"},
    #             "sk": {"S": last_message_at},
    #             "message_group_uuid": {"S": message_group_uuid},
    #             "message": {"S": latest_message},
    #             "user_uuid": {"S": other_uuid},
    #             "user_display_name": {"S": other_display_name},
    #             "user_handle": {"S": other_handle}
    #         }
    #     )

    # @staticmethod
    # def create_message_group(
    #     client,
    #     initial_message,
    #     my_user_uuid,
    #     my_user_display_name,
    #     my_user_handle,
    #     other_user_uuid,
    #     other_user_display_name,
    #     other_user_handle
    # ):
    #     """
    #     Atomically creates group metadata for both participants and the initial chat message.
    #     """
    #     message_group_uuid = str(uuid.uuid4())
    #     message_uuid = str(uuid.uuid4())
    #     now_iso = datetime.now(timezone.utc).astimezone().isoformat()

    #     my_message_group_item = {
    #         "pk": {"S": f"GRP#{my_user_uuid}"},
    #         "sk": {"S": now_iso},
    #         "message_group_uuid": {"S": message_group_uuid},
    #         "message": {"S": initial_message},
    #         "user_uuid": {"S": other_user_uuid},
    #         "user_display_name": {"S": other_user_display_name},
    #         "user_handle": {"S": other_user_handle}
    #     }

    #     other_message_group_item = {
    #         "pk": {"S": f"GRP#{other_user_uuid}"},
    #         "sk": {"S": now_iso},
    #         "message_group_uuid": {"S": message_group_uuid},
    #         "message": {"S": initial_message},
    #         "user_uuid": {"S": my_user_uuid},
    #         "user_display_name": {"S": my_user_display_name},
    #         "user_handle": {"S": my_user_handle}
    #     }

    #     initial_chat_message = {
    #         "pk": {"S": f"MSG#{message_group_uuid}"},
    #         "sk": {"S": now_iso},
    #         "message_group_uuid": {"S": message_group_uuid},
    #         "message": {"S": initial_message},
    #         "message_uuid": {"S": message_uuid},
    #         "user_uuid": {"S": my_user_uuid},
    #         "user_display_name": {"S": my_user_display_name},
    #         "user_handle": {"S": my_user_handle}
    #     }

    #     transact_items = [
    #         {"Put": {"TableName": Ddb.TABLE_NAME, "Item": my_message_group_item}},
    #         {"Put": {"TableName": Ddb.TABLE_NAME, "Item": other_message_group_item}},
    #         {"Put": {"TableName": Ddb.TABLE_NAME, "Item": initial_chat_message}}
    #     ]

    #     try:
    #         client.transact_write_items(TransactItems=transact_items)
    #         return {
    #             "message_group_uuid": message_group_uuid,
    #             "last_message_at": now_iso
    #         }
    #     except botocore.exceptions.ClientError:
    #         current_app.logger.exception("Failed to create message group transactionally")
    #         raise

    # @staticmethod
    # def create_message(
    #     client,
    #     message_group_uuid,
    #     message,
    #     my_user_uuid,
    #     my_user_display_name,
    #     my_user_handle,
    #     other_user_uuid,
    #     other_user_display_name,
    #     other_user_handle
    # ):
    #     """
    #     Inserts a new chat message and updates both participants' group metadata to reflect latest.
    #     """
    #     now_iso = datetime.now(timezone.utc).astimezone().isoformat()
    #     message_uuid = str(uuid.uuid4())

    #     # Put the chat message
    #     message_item = {
    #         "pk": {"S": f"MSG#{message_group_uuid}"},
    #         "sk": {"S": now_iso},
    #         "message_group_uuid": {"S": message_group_uuid},
    #         "message": {"S": message},
    #         "message_uuid": {"S": message_uuid},
    #         "user_uuid": {"S": my_user_uuid},
    #         "user_display_name": {"S": my_user_display_name},
    #         "user_handle": {"S": my_user_handle}
    #     }

    #     try:
    #         client.put_item(TableName=Ddb.TABLE_NAME, Item=message_item)
    #     except Exception:
    #         current_app.logger.exception("Failed to put chat message")
    #         raise

    #     # Update both participants' group metadata so their last snippet is current.
    #     # Assume the conversation participants are my_user and other_user; reverse roles.
    #     try:
    #         Ddb._update_group_metadata(
    #             client=client,
    #             message_group_uuid=message_group_uuid,
    #             participant_uuid=my_user_uuid,
    #             other_uuid=other_user_uuid,
    #             other_display_name=other_user_display_name,
    #             other_handle=other_user_handle,
    #             latest_message=message,
    #             last_message_at=now_iso
    #         )
    #         Ddb._update_group_metadata(
    #             client=client,
    #             message_group_uuid=message_group_uuid,
    #             participant_uuid=other_user_uuid,
    #             other_uuid=my_user_uuid,
    #             other_display_name=my_user_display_name,
    #             other_handle=my_user_handle,
    #             latest_message=message,
    #             last_message_at=now_iso
    #         )
    #     except Exception:
    #         current_app.logger.exception("Failed to update group metadata after new message")
    #         raise

    #     return {
    #         "message_group_uuid": message_group_uuid,
    #         "uuid": my_user_uuid,
    #         "display_name": my_user_display_name,
    #         "handle": my_user_handle,
    #         "message": message,
    #         "created_at": now_iso
    #     }

    def create_message(client,message_group_uuid, message, my_user_uuid, my_user_display_name, my_user_handle):
        now = datetime.now(timezone.utc).astimezone().isoformat()
        created_at = now
        message_uuid = str(uuid.uuid4())

        record = {
        'pk':   {'S': f"MSG#{message_group_uuid}"},
        'sk':   {'S': created_at },
        'message': {'S': message},
        'message_uuid': {'S': message_uuid},
        'user_uuid': {'S': my_user_uuid},
        'user_display_name': {'S': my_user_display_name},
        'user_handle': {'S': my_user_handle}
        }
        # insert the record into the table
        table_name = 'cruddur-messages'
        response = client.put_item(
        TableName=table_name,
        Item=record
        )
        # print the response
        print(response)
        return {
        'message_group_uuid': message_group_uuid,
        'uuid': my_user_uuid,
        'display_name': my_user_display_name,
        'handle':  my_user_handle,
        'message': message,
        'created_at': created_at
        }
    def create_message_group(client, message,my_user_uuid, my_user_display_name, my_user_handle, other_user_uuid, other_user_display_name, other_user_handle):
        print('== create_message_group.1')
        table_name = 'cruddur-messages'

        message_group_uuid = str(uuid.uuid4())
        message_uuid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).astimezone().isoformat()
        last_message_at = now
        created_at = now
        print('== create_message_group.2')

        my_message_group = {
        'pk': {'S': f"GRP#{my_user_uuid}"},
        'sk': {'S': last_message_at},
        'message_group_uuid': {'S': message_group_uuid},
        'message': {'S': message},
        'user_uuid': {'S': other_user_uuid},
        'user_display_name': {'S': other_user_display_name},
        'user_handle':  {'S': other_user_handle}
        }

