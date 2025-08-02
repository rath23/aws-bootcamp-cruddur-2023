from datetime import datetime, timedelta, timezone

from lib.ddb import Ddb
from lib.db import db

from flask import current_app

# class MessageGroups:
#      def run(cognito_user_id):
#         model = {
#             'errors': None,
#             'data': None
#         }
#         current_app.logger.info("Entering MessageGroups.run")
#         try:
#             # Get user UUID
#             sql = db.template('users', 'uuid_from_cognito_user_id')
#             my_user_uuid = db.query_value(sql, {
#                 'cognito_user_id': cognito_user_id
#             })

#             if not my_user_uuid:
#                 model['errors'] = ['user_not_found']
#                 return model

#             print(f"UUID: {my_user_uuid}")
#             current_app.logger.info(my_user_uuid)

#             # Get message groups
#             ddb = Ddb.client()
#             data = Ddb.list_message_groups(ddb, my_user_uuid)
#             print("list_message_groups:", data)
#             current_app.logger.info(data)

#             model['data'] = data
#             return model

#         except Exception as e:
#             print(f"[Error] MessageGroups.run: {str(e)}")
#             model['errors'] = ['server_error']
#             return model

class MessageGroups:
    @staticmethod
    def run(cognito_user_id):
        model = {"errors": None, "data": None}
        current_app.logger.info("Entering MessageGroups.run")
        try:
            # 1. Resolve the user's UUID from Cognito ID
            sql = db.template("users", "uuid_from_cognito_user_id")
            my_user_uuid = db.query_value(sql, {"cognito_user_id": cognito_user_id})

            if not my_user_uuid:
                model["errors"] = ["user_not_found"]
                return model

            # 2. List the message groups (conversation summaries) for this user
            ddb = Ddb.client()
            data = Ddb.list_message_groups(ddb, my_user_uuid)
            model["data"] = data
            return model

        except Exception as e:
            current_app.logger.exception(f"[Error] MessageGroups.run: {e}")
            model["errors"] = ["server_error"]
            return model
