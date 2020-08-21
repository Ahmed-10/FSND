import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'koffee-shop.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'


# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
'''
to get the header from the request
    and raise an AuthError if no header is present
to split bearer and the token
    and raise an AuthError if the header is malformed
return the token part of the header
'''


def get_token_auth_header():
    '''
    obtain the access token from Authorization header
    '''
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
            }, 401)

    token = auth_header.split(' ')

    if len(token) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
            }, 401)

    elif len(token) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
            }, 401)

    elif token[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
            }, 401)

    return token[1]


'''
check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    if permissions are not included in the payload
        it raises an AuthError
    if the requested permission string is not in the payload permissions array
        it raises an AuthError

    return true otherwise
'''


def check_permissions(permission, payload):
    '''check the 'permissions' key in the payload'''
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'permissions should be included'
            }, 401)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission Not found'
            }, 401)

    return True


'''
verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload
'''


def verify_decode_jwt(token):
    json_url = urlopen('https://' + AUTH0_DOMAIN + '/.well-known/jwks.json')
    jwks = json.loads(json_url.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
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
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. check the audience.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


'''
@requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    get the token using the get_token_auth_header method
    decode the jwt using the verify_decode_jwt method
    icheck the requested permission using the check_permissions method
    return the decorator which passes the payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            if (check_permissions(permission, payload)):
                return f(payload, *args, **kwargs)
            else:
                raise AuthError({
                    'code': 'unauthorized',
                    'description': 'Permission Not found'
                    }, 401)

        return wrapper
    return requires_auth_decorator
