"""
Custom JWT middleware to put JWT data in request 
so it's available anywhere in views or templates.
"""
from django.conf import settings
import jwt


# This needs to be Entra secret key
jwt_secret_key = settings.CLIENT_SECRET_ENTRA
client_id = settings.CLIENT_ID_ENTRA
tenant_id = settings.TENANT_ID_ENTRA

# Test sandbox that gets test user from entra and returns the JSON data fields.
# https://sb-sample1app.azurewebsites.net/


class JwtMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Get HTTP_AUTHORIZATION bearer token string, decode it, and add data to request for use.
        """
        http_auth_string = request.META.get("HTTP_AUTHORIZATION", None)
        request.jwt_data = get_jwt_data(http_auth_string)
        return self.get_response(request)


def get_jwt_data(http_auth_string):
    token_data = {}

    try:
        token_string = http_auth_string.split()[1]
        token_data = decode_token(token_string)
        token_data["token_string"] = token_string
        print("Decoded JWT successfully")
    except Exception as ex:
        print(f"Error decoding JWT ({http_auth_string}), error: {ex}")

    return token_data


def decode_token(token):
    """
    Take inbound token string, decode, and return it.
    """
    issuer = "https://sts.windows.net/{tenant_id}/".format(tenant_id=tenant_id)
    decoded = jwt.decode(
        token,
        # public_key,
        jwt_secret_key,
        verify=True,
        options={"verify_signature": False},
        algorithms=["RS256"],
        audience=[client_id],
        issuer=issuer,
    )

    return decoded
