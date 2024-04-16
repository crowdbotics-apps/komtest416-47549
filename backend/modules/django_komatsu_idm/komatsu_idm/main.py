import requests
from datetime import datetime, timedelta
from dev_mykomatsu_sdk import FoundryClient
from dev_mykomatsu_sdk.core.api import UserTokenAuth
import jwt
from cryptography.hazmat.primitives import serialization
import json
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from django.conf import settings


class SDKClient:
    def __init__(self, client_id, client_secret, hostname):
        self._client_id = client_id
        self._client_secret = client_secret
        self.auth_url = f"{hostname}/multipass/api/oauth2/token"
        self._token = None
        self.token_expiry = None
        self.hostname = hostname
        self.client = None

    def request_new_token(self):
        try:
            # Request a new access token using client credentials
            post_data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": "api:read-data",
            }
            response = requests.post(url=self.auth_url, data=post_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error while requesting token: {e}")
            raise

    def authenticate(self):
        try:
            # Authenticate using the obtained access token
            token_data = self.request_new_token()
            self._token = token_data["access_token"]
            expires_in = token_data["expires_in"]
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)
            return self._token
        except Exception as e:
            print(f"Authentication error: {e}")
            raise

    def get_client(self):
        # Retrieve the SDK client, renewing the token if necessary
        if not self._token or datetime.now() > self.token_expiry:
            self.client = FoundryClient(
                auth=UserTokenAuth(hostname=self.hostname, token=self.authenticate()),
                hostname=self.hostname,
            )
        return self.client


class EntraAuth:
    def __init__(self, client_id, client_secret, tenant_id):
        self._client_id = client_id
        self._client_secret = client_secret
        self.tenant_id = tenant_id
        self.auth_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        self.user_url = "https://graph.microsoft.com/v1.0/users"
        self.callback_url = "https://mykomatsuwebapp.azurewebsites.net/my-fleet"
        self.public_key_url = (
            f"https://externalkomatsu.ciamlogin.com/{self.tenant_id}/discovery/keys"
        )
        self._token = None
        self.token_expiry = None

    def authenticate(self):
        try:
            # Authenticate using the obtained access token
            if not self._token or datetime.now() > self.token_expiry:
                token_data = self.request_new_token()
                self._token = token_data["access_token"]
                expires_in = token_data["expires_in"]
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            return self._token
        except Exception as e:
            print(f"Authentication error: {e}")
            raise

    def request_new_token(self):
        try:
            # Request a new access token using client credentials
            data = f"grant_type=client_credentials&client_id={self._client_id}&scope=https://graph.microsoft.com/.default&client_secret={self._client_secret}&redirect_uri={self.callback_url}"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            response = requests.post(url=self.auth_url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error while requesting token: {e}")
            raise

    def email_method_call(self, email, user_id):
        try:
            # Make a request to create an email method for a user
            headers = {
                "Authorization": f"Bearer {self.authenticate()}",
                "Content-Type": "application/json",
            }
            user_payload = {"emailAddress": f"{email}"}
            request_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/emailMethods"
            response = requests.post(request_url, headers=headers, json=user_payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error: {e}")
            print("Response content:", response.text if "response" in locals() else "")
            raise

    def get_public_key(
        self,
    ):
        res = requests.get(self.public_key_url)
        keys = res.json()["keys"]

        token_headers = jwt.get_unverified_header(self.authenticate())
        token_kid = token_headers["kid"]
        public_key = None
        for key in keys:
            if key["kid"] == token_kid:
                public_key = key

        rsa_pem_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(public_key))
        rsa_pem_key_bytes = rsa_pem_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return rsa_pem_key_bytes

    def create_user(self, first_name, last_name, email, principal_name):
        try:
            # Create a new user and call the email_method_call function
            headers = {
                "Authorization": f"Bearer {self.authenticate()}",
                "Content-Type": "application/json",
            }
            user_payload = {
                "accountEnabled": True,
                "displayName": f"{first_name} {last_name}",
                "mailNickname": f"{first_name}",
                "userPrincipalName": f"{principal_name}",
                "passwordProfile": {
                    "forceChangePasswordNextSignIn": True,
                    "forceChangePasswordNextSignInWithMfa": False,
                    "password": "xWwvJ]6NMw+bW",
                },
                "identities": [
                    {
                        "signInType": "emailAddress",
                        "issuer": "externalkomatsu.onmicrosoft.com",
                        "issuerAssignedId": f"{email}",
                    }
                ],
            }
            response = requests.post(self.user_url, headers=headers, json=user_payload)
            response.raise_for_status()
            user_id = response.json()["id"]
            self.email_method_call(email, user_id)
            return user_id
        except requests.RequestException as e:
            print(f"Error: Failed to create user. {e}")
            print("Response content:", response.text if "response" in locals() else "")
            raise


def SendDynamic(sender, recipient_list, dynamic_data):
    """Send a dynamic email to a list of email addresses

    :returns API response code
    :raises Exception e: raises an exception"""

    # create Mail object and populate
    message = Mail(from_email=sender, to_emails=recipient_list)

    # pass custom values for our HTML placeholders
    message.dynamic_template_data = dynamic_data
    message.template_id = settings.SENDGRID_TEMPLATE_ID

    # create our sendgrid client object, pass it our key, then send and return our response objects
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print("Dynamic Messages Sent!")
    except Exception as e:
        print("Error: {0}".format(e))

    return str(response.status_code)


try:
    # Instantiate the EntraAuth and SDKClient classes
    entra_auth = EntraAuth(
        client_id=settings.CLIENT_ID_ENTRA,
        client_secret=settings.CLIENT_SECRET_ENTRA,
        tenant_id=settings.TENANT_ID_ENTRA,
    )

    client = SDKClient(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        hostname=settings.PALANTIR_HOSTNAME,
    )

    # Retrieve the SDK client
    sdk_client = client.get_client

except Exception as e:
    print(f"Error: {e}")
