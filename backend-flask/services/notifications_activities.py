from aws_xray_sdk.core import xray_recorder
from datetime import datetime, timedelta, timezone

class NotificationsActivities:
    @staticmethod
    def run():
        try:
            now = datetime.now(timezone.utc).astimezone()
            results = [{
                'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
                'handle':  'coco',
                'message': 'I am white unicorn',
                'created_at': (now - timedelta(days=2)).isoformat(),
                'expires_at': (now + timedelta(days=5)).isoformat(),
                'likes_count': 5,
                'replies_count': 1,
                'reposts_count': 0,
                'replies': [{
                    'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
                    'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
                    'handle':  'worf',
                    'message': 'this post has no honor!',
                    'likes_count': 0,
                    'replies_count': 0,
                    'reposts_count': 0,
                    'created_at': (now - timedelta(days=2)).isoformat()
                }],
            }]

            # ✅ Just use a subsegment
            with xray_recorder.in_subsegment('mock-data') as subsegment:
                meta = {
                    "now": now.isoformat(),
                    "results-size": len(results)
                }
                subsegment.put_metadata('data-meta', meta, 'notifications-activities')

            return results

        except Exception as e:
            raise e
