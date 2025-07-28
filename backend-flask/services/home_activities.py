from datetime import datetime, timedelta, timezone
from opentelemetry import trace

from lib.db import db

tracer = trace.get_tracer(__name__)  

class HomeActivities:
  @staticmethod
  def run(logger, User=None, public_only=False):
    with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      logger.info('Hello Cloudwatch! from /api/activities/home')
      sql = db.template('activities','home')
      results = db.query_array_json(sql)
      return results