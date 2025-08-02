from datetime import datetime, timedelta, timezone

from lib.ddb import Ddb
from lib.db import db

from flask import current_app

class MessageGroups:
     def run(cognito_user_id):
        model = {
            'errors': None,
            'data': None
        }
        current_app.logger.info("Entering MessageGroups.run")
        try:
            # Get user UUID
            sql = db.template('users', 'uuid_from_cognito_user_id')
            my_user_uuid = db.query_value(sql, {
                'cognito_user_id': cognito_user_id
            })

            if not my_user_uuid:
                model['errors'] = ['user_not_found']
                return model

            print(f"UUID: {my_user_uuid}")
            current_app.logger.info(my_user_uuid)

            # Get message groups
            ddb = Ddb.client()
            data = Ddb.list_message_groups(ddb, my_user_uuid)
            print("list_message_groups:", data)
            current_app.logger.info(data)

            model['data'] = data
            return model

        except Exception as e:
            print(f"[Error] MessageGroups.run: {str(e)}")
            model['errors'] = ['server_error']
            return model

# from datetime import datetime, timedelta, timezone
# class MessageGroups:
#   def run(cognito_user_id):
#     model = {
#       'errors': None,
#       'data': None
#     }

#     now = datetime.now(timezone.utc).astimezone()
#     results = [
#       {
#         'uuid': '24b95582-9e7b-4e0a-9ad1-639773ab7552',
#         'display_name': 'Andrew Brown',
#         'handle':  'andrewbrown',
#         'created_at': now.isoformat()
#       },
#       {
#         'uuid': '417c360e-c4e6-4fce-873b-d2d71469b4ac',
#         'display_name': 'Worf',
#         'handle':  'worf',
#         'created_at': now.isoformat()
#     }]
#     model['data'] = results
#     return model