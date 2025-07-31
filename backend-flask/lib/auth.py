import json
import requests
from jose import jwt
from flask import request, jsonify
from functools import wraps
import os

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Constants
COGNITO_REGION = "ap-south-1"
USER_POOL_ID = os.environ.get("AWS_USER_POOL_ID")
APP_CLIENT_ID = os.environ.get("AWS_USER_POOLS_WEB_CLIENT_ID")
COGNITO_KEYS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"


def get_jwks():
    try:
        logger.debug("APP ID")
        logger.debug(APP_CLIENT_ID)
        res = requests.get(COGNITO_KEYS_URL)
        jwks = res.json()
        if "keys" not in jwks:
            raise ValueError(f"No 'keys' in JWK response: {jwks}")
        return jwks["keys"]
    except Exception as e:
        print("Error fetching JWKs:", e)
        return []

def get_token_auth_header():
    """Extracts the Access Token from the Authorization Header"""
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise Exception("Authorization header is expected")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise Exception("Authorization header must start with Bearer")
    elif len(parts) == 1:
        raise Exception("Token not found")
    elif len(parts) > 2:
        raise Exception("Authorization header must be Bearer token")

    return parts[1]


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        if not token:
            return jsonify({"message": "Missing or invalid Authorization header"}), 401  # ✅ safe exit

        try:
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in get_jwks():
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }

            if not rsa_key:
                return jsonify({"message": "No matching key found"}), 401

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=APP_CLIENT_ID,
                issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}"
            )

            request.user = payload
            return f(*args, **kwargs)

        except Exception as e:
            print("Auth error:", e)
            return jsonify({"message": "Unauthorized"}), 401

    return decorated

def try_get_current_user():
    """Returns user payload if token is valid, otherwise None."""
    token = request.headers.get("Authorization", None)
    if not token:
        return None

    try:
        token = token.split(" ")[1]  # Remove "Bearer"
        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}
        for key in get_jwks():
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        if not rsa_key:
            return None

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}"
        )

        return payload
    except Exception as e:
        logger.debug(f"Auth optional decode failed: {e}")
        return None
