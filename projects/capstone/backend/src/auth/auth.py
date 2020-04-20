import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'dev-coffeeshop.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'musicbox'
AUTH0_CLIENT_ID = 'jaWXBTv6q2Wb3dpdd2PT9h9JXbZAnDJR'

# AuthError Exception
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    auth_header = request.headers.get('authorization', 'None')
    token = None
    if not auth_header:
        raise AuthError({
            'description': 'No Authorization header supplied',
            'code': 'UNAUTHORIZED'
        }, 401)
    parts = auth_header.split()
    # 0 is the auth type, 1 is the token
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'description': 'Authorization method must be Bearer',
            'code': 'INVALID_AUTH_METHOD'
        }, 401)
    if len(parts) > 1 and parts[1] is not None:
        token = parts[1]
    return token


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'INVALID_CLAIMS',
            'description': 'No permissions in JWT token'
            }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'FORBIDDEN',
            'description': f'User does not have permission for \
                             this operation. Required: ${permission}'
            }, 401)
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'INVALID_HEADER',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'TOKEN_EXPIRED',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'INVALID_CLAIMS',
                'description': 'Incorrect claims. Please, \
                                check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'INVALID_HEADER',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'INVALID_HEADER',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError:
                abort(401)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator