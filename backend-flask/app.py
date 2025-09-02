from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os

from lib.auth import requires_auth, try_get_current_user

from services.users_short import *
from services.home_activities import *
from services.notifications_activities import *
from services.user_activities import *
from services.create_activity import *
from services.create_reply import *
from services.search_activities import *
from services.message_groups import *
from services.messages import *
from services.create_message import *
from services.show_activity import *
from services.update_profile import *

# HoneyComb import
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Cloud logs

import watchtower
import logging
from time import strftime

# Configuring Logger to Use CloudWatch
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group="cruddur")
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)
LOGGER.info("App started")

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# AWS X-ray-----------
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service="backend-flask", dynamic_naming=xray_url)

# RoolBAr--------------

import rollbar
import rollbar.contrib.flask
from flask import got_request_exception


app = Flask(__name__)

@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200


rollbar_access_token = os.getenv("ROLLBAR_ACCESS_TOKEN")

# Roll bar
with app.app_context():
    """init rollbar module"""
    rollbar.init(
        # access token
        rollbar_access_token,
        # environment name - any string, like 'production' or 'development'
        "flasktest",
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False,
    )

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

# @app.before_first_request
# def init_rollbar():
#     """init rollbar module"""
#     rollbar.init(
#         # access token
#         rollbar_access_token,
#         # environment name
#         'production',
#         # server root directory, makes tracebacks prettier
#         root=os.path.dirname(os.path.realpath(__file__)),
#         # flask already sets up logging
#         allow_logging_basic_config=False)

#     # send exceptions from `app` to rollbar, using flask's signal system.
#     got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.route("/rollbar/test")
def rollbar_test():
    rollbar.report_message("Hello World!", "warning")
    return "Hello World!"


XRayMiddleware(app, xray_recorder)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


frontend = os.getenv("FRONTEND_URL")
backend = os.getenv("BACKEND_URL")
print(frontend)
print(backend)

origins = [frontend, backend]
CORS(
    app,
    resources={r"/api/*": {"origins": origins}},
    supports_credentials=True,
    headers=["Content-Type", "Authorization"],
    expose_headers=["Authorization"],
    methods="OPTIONS,GET,HEAD,POST",
)


# CloudLogs
@app.after_request
def after_request(response):
    timestamp = strftime("[%Y-%b-%d %H:%M]")
    LOGGER.error(
        "%s %s %s %s %s %s",
        timestamp,
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status,
    )

    origin = request.headers.get("Origin")
    LOGGER.info(f"CORS Request Origin: {origin}")
    return response


# @app.route("/api/message_groups", methods=['GET'])
# @requires_auth
# def data_message_groups():
#     user_payload = getattr(request, "user", None)  # set by decorator
#     if not user_payload:
#         return jsonify({"message": "Unauthorized"}), 401
#     cognito_sub = user_payload.get("sub")  # the user's UUID in Cognito
#     handle = user_payload.get("custom:handle")
#     model = MessageGroups.run(cognito_user_id=cognito_sub)
#     if model.get('errors'):
#         return model['errors'], 422
#     return model['data'], 200


@app.route("/api/message_groups", methods=["GET"])
@requires_auth
def data_message_groups():
    try:
        user_payload = getattr(request, "user", None)
        if not user_payload:
            return (
                jsonify(
                    {
                        "error": "missing_user",
                        "message": "User information not found in token",
                    }
                ),
                422,
            )

        cognito_sub = user_payload.get("sub")
        if not cognito_sub:
            return (
                jsonify(
                    {
                        "error": "invalid_token",
                        "message": "Token missing required claims (sub)",
                    }
                ),
                422,
            )
        model = MessageGroups.run(cognito_user_id=cognito_sub)
        if model.get("errors"):
            return (
                jsonify({"error": "validation_error", "details": model["errors"]}),
                422,
            )

        return jsonify(model["data"]), 200

    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500


@app.route("/api/messages/<string:message_group_uuid>", methods=["GET"])
@requires_auth
def data_messages(message_group_uuid):
    user_payload = getattr(request, "user", None)  # set by decorator
    app.logger.info("message_group_uuid")
    app.logger.info(message_group_uuid)
    if not user_payload:
        return jsonify({"message": "Unauthorized"}), 401
    cognito_sub = user_payload.get("sub")  # the user's UUID in Cognito
    handle = user_payload.get("custom:handle")
    model = Messages.run(
        cognito_user_id=cognito_sub, message_group_uuid=message_group_uuid
    )
    if model["errors"] is not None:
        return model["errors"], 422
    else:
        return model["data"], 200




@app.route("/api/messages", methods=['POST', 'OPTIONS'])
@cross_origin()
@requires_auth
def data_create_message():
    message_group_uuid   = request.json.get('message_group_uuid',None)
    user_receiver_handle = request.json.get('handle',None)
    message = request.json['message']

    if not message:
        return jsonify({"errors": ["message_required"]}), 400

    user_payload = getattr(request, "user", None)
    if not user_payload:
        return jsonify({"errors": ["unauthenticated"]}), 401

    app.logger.debug("authenticated user payload: %s", user_payload)
    cognito_user_id = user_payload.get("sub")

    try:
        if message_group_uuid is None:
            if not user_receiver_handle:
                return jsonify({"errors": ["receiver_handle_required"]}), 400
            model = CreateMessage.run(
                mode="create",
                message=message,
                cognito_user_id=cognito_user_id,
                user_receiver_handle=user_receiver_handle
            )
        else:
            model = CreateMessage.run(
                mode="update",
                message=message,
                message_group_uuid=message_group_uuid,
                cognito_user_id=cognito_user_id
            )

        if model.get("errors"):
            return jsonify({"errors": model["errors"]}), 422
        return jsonify(model["data"]), 200

    except Exception:  # later narrow to specific error types if needed
        app.logger.exception("Error in creating message")
        return jsonify({"errors": ["server_error"]}), 500




@app.route("/api/activities/home", methods=["GET"])
@xray_recorder.capture("activities_home")
def data_home():
    user = try_get_current_user()
    if user:
        # Authenticated user: return full data
        data = HomeActivities.run(logger=LOGGER, User=user)
    else:
        # Unauthenticated user: return limited data
        data = HomeActivities.run(logger=LOGGER, User=None, public_only=True)
    return data, 200


@app.route("/api/activities/notifications", methods=["GET"])
@xray_recorder.capture("activities_notifications")
def data_notifications():
    data = NotificationsActivities.run()
    return data, 200


@app.route("/api/activities/@<string:handle>", methods=["GET"])
def data_handle(handle):
    model = UserActivities.run(handle)
    if model["errors"] is not None:
        return model["errors"], 422
    else:
        return model["data"], 200


@app.route("/api/activities/search", methods=["GET"])
def data_search():
    term = request.args.get("term")
    model = SearchActivities.run(term)
    if model["errors"] is not None:
        return model["errors"], 422
    else:
        return model["data"], 200
    return


@app.route("/api/activities", methods=["POST", "OPTIONS"])
@cross_origin()
@requires_auth
def data_activities():
    user_handle = request.json["user_handle"]
    message = request.json["message"]
    ttl = request.json["ttl"]
    model = CreateActivity.run(message, user_handle, ttl)
    if model["errors"] is not None:
        return model["errors"], 422
    else:
        return model["data"], 200
    return


@app.route("/api/activities/<string:activity_uuid>/reply", methods=["POST", "OPTIONS"])
@cross_origin()
@requires_auth
def data_activities_reply(activity_uuid):
    user_payload = getattr(request, "user", None)
    cognito_user_id = user_payload.get("sub")
    message = request.json["message"]
    model = CreateReply.run(message, cognito_user_id, activity_uuid)
    if model["errors"] is not None:
        return model["errors"], 422
    else:
        return model["data"], 200
    return

@app.route("/api/users/@<string:handle>/short", methods=['GET'])
def data_users_short(handle):
  data = UsersShort.run(handle)
  return data, 200


@app.route("/api/profile/update", methods=['POST','OPTIONS'])
@cross_origin()
@requires_auth
def data_update_profile():
  bio          = request.json.get('bio',None)
  display_name = request.json.get('display_name',None)
  try:
    user_payload = getattr(request, "user", None)
    cognito_user_id = user_payload.get("sub")
    UpdateProfile.run(
      cognito_user_id=cognito_user_id,
      bio=bio,
      display_name=display_name
    )
    if model['errors'] is not None:
      return model['errors'], 422
    else:
      return model['data'], 200
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    return {}, 401

@app.route("/api/activities/@<string:handle>/status/<string:activity_uuid>", methods=['GET'])
def data_show_activity(handle,activity_uuid):
    data = ShowActivity.run(activity_uuid)
    return data, 200    

if __name__ == "__main__":
    app.run(debug=True)
