# import json
# import requests
# from jose import jwt
# from flask import request, jsonify
# from functools import wraps
# import os

# import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


# Constants
COGNITO_REGION = os.environ.get("COGNITO_REGION")
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
        logger.debug("token")
        logger.debug(token)
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
                print("No matching RSA key found for token.")
                return jsonify({"message": "Unauthorized"}), 401

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

# import jwt
# from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
# import requests
# import json
# from functools import wraps
# from flask import request, jsonify

# class CognitoJWTValidator:
#     def __init__(self, region, user_pool_id, app_client_id):
#         self.region = region
#         self.user_pool_id = user_pool_id
#         self.app_client_id = app_client_id
#         self.jwks_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
#         self.jwks_keys = None

#     def get_jwks_keys(self):
#         """Fetch and cache JWKS keys from Cognito"""
#         if self.jwks_keys is None:
#             response = requests.get(self.jwks_url)
#             self.jwks_keys = response.json()['keys']
#         return self.jwks_keys

#     def verify_token(self, token):
#         """
#         Verify Cognito JWT token and return decoded claims if valid
#         """
#         try:
#             # Get the key ID (kid) from the token header
#             header = jwt.get_unverified_header(token)
#             kid = header['kid']
            
#             # Find the matching key in JWKS
#             keys = self.get_jwks_keys()
#             key = next((k for k in keys if k['kid'] == kid), None)
            
#             if not key:
#                 raise InvalidTokenError('Public key not found in JWKS')
            
#             # Construct the public key
#             public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            
#             # Verify the token
#             claims = jwt.decode(
#                 token,
#                 public_key,
#                 algorithms=['RS256'],
#                 audience=self.app_client_id,
#                 issuer=f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}'
#             )
            
#             return claims
            
#         except ExpiredSignatureError:
#             raise InvalidTokenError('Token has expired')
#         except Exception as e:
#             raise InvalidTokenError(f'Invalid token: {str(e)}')

#     def jwt_required(self, f):
#         """
#         Decorator to protect routes with Cognito JWT authentication
#         """
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             auth_header = request.headers.get('Authorization')
#             if not auth_header:
#                 return jsonify({'error': 'Authorization header is missing'}), 401
                
#             try:
#                 # Extract token from "Bearer <token>"
#                 token = auth_header.split()[1]
#                 claims = self.verify_token(token)
#                 # Add claims to the request context for use in the route
#                 request.claims = claims
#             except InvalidTokenError as e:
#                 return jsonify({'error': str(e)}), 401
#             except Exception as e:
#                 return jsonify({'error': 'Invalid authorization header'}), 401
                
#             return f(*args, **kwargs)
#         return decorated_function