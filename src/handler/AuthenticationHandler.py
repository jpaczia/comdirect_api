import typing
from pydantic import Field
import requests
import json
import datetime

from src.handler.AbstractHandler import AbstractHandler
from src.data.config_types import Credentials
from src.handler.AuthenticationException import AuthenticationException


class AuthenticationHandler(AbstractHandler):
    """Handles the authentication against the comdirect API"""

    access_token: typing.Optional[str] = Field(default=None)
    refresh_token: typing.Optional[str] = Field(default=None)
    credentials: Credentials = Field(default_factory=Credentials.get_credentials)
    session_identifier: typing.Optional[str] = Field(default=None)
    challenge_id: typing.Optional[str] = Field(default=None)

    def authenticate(self) -> None:
        """Authenticate against the comdirect API"""
        self.retrieve_oauth2_token()
        self.retrieve_session_object()
        self.request_tan()

        # Wait until user has verified that the TAN challenge has been solved.
        # If the TAN challenge has not been solved the authentication process fails.
        input(
            (
                f"{datetime.datetime.now().strftime(self.time_format)}: "
                + "Activating the session. Confirm that the TAN challenge was solved with ENTER..."
            )
        )

        self.activate_session_tan()
        self.oauth2_cd_secondary_flow()

    def retrieve_oauth2_token(self) -> None:
        """Retrieve an OAuth2 authentication token,
        which is used to request the creation of the session TAN from the comdirect API.
        First step in the authentication process.
        Raises:
            AuthenticationException: Raised if the authentication fails.
        """
        oauth2_url = f"{self.api_config.oauth_url}/oauth/token"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = self.credentials.dict()

        response = requests.post(url=oauth2_url, headers=headers, data=payload)
        if response.status_code != 200:
            raise AuthenticationException(response.headers["x-http-response-info"])

        self.set_tokens(response_json=response.json())

    def retrieve_session_object(self):
        """Retrieve the session object which is required to request the session TAN later on.
        Second step in the authentication process.
        Raises:
            AuthenticationException: Raised if the authentication fails.
        """

        session_url = f"{self.api_config.api_url}/session/clients/user/v1/sessions"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "x-http-request-info": str(
                {
                    "clientRequestId": {
                        "sessionId": self.session_id,
                        "requestId": AbstractHandler.generate_request_id(),
                    }
                }
            ),
        }

        response = requests.get(url=session_url, headers=headers, data={})
        if response.status_code != 200:
            raise AuthenticationException(response.headers["x-http-response-info"])

        response_json = response.json()[0]
        self.session_identifier = response_json["identifier"]

    def request_tan(self) -> None:
        """Request a TAN challenge for the session object from the previous step.
        Third step in the authentication process.
        Raises:
            AuthenticationException: Raised if the authentication fails.
        """

        tan_url = f"{self.api_config.api_url}/session/clients/user/v1/sessions/{self.session_identifier}/validate"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "x-http-request-info": str(
                {
                    "clientRequestId": {
                        "sessionId": self.session_id,
                        "requestId": AbstractHandler.generate_request_id(),
                    }
                }
            ),
            "Content-Type": "application/json",
        }
        payload = json.dumps(
            {
                "identifier": f"{self.session_identifier}",
                "sessionTanActive": True,
                "activated2FA": True,
            }
        )

        response = requests.post(url=tan_url, headers=headers, data=payload)
        if response.status_code != 201:
            raise AuthenticationException(response.headers["x-http-response-info"])

        response_json = json.loads(response.headers["x-once-authentication-info"])
        self.challenge_id = response_json["id"]

    def activate_session_tan(self) -> None:
        """Activate the previously retrieved session TAN.
        Fourth step in the authentication process.
        Raises:
            AuthenticationException: Raised if the authentication fails.
        """

        activation_url = f"{self.api_config.api_url}/session/clients/user/v1/sessions/{self.session_identifier}"
        clientRequestId = {
            "clientRequestId": {
                "sessionId": self.session_identifier,
                "requestId": AbstractHandler.generate_request_id(),
            }
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "x-http-request-info": str(clientRequestId),
            "Content-Type": "application/json",
            "x-once-authentication-info": json.dumps({"id": self.challenge_id}),
        }
        payload = json.dumps(
            {
                "identifier": f"{self.session_identifier}",
                "sessionTanActive": True,
                "activated2FA": True,
            }
        )

        response = requests.patch(url=activation_url, headers=headers, data=payload)
        if response.status_code != 200:
            raise AuthenticationException(response.headers["x-http-response-info"])

    def oauth2_cd_secondary_flow(self) -> None:
        """comdirect specific OAuth2 authentication flow "cd_secondary".
        This authentication flow is a mix of the "client-credentials"-flow
        and the "resource-owner-password-credentials"-flow.
        This allows to issue an access-token which entitles
        to use the banking- and brokerage-interfaces of the comdirect API.
        Fifth (last) step in the authentication process.
        Raises:
            AuthenticationException: Raised if the authentication fails.
        """

        url = f"{self.api_config.oauth_url}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        payload = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "grant_type": "cd_secondary",
            "token": self.access_token,
        }

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code != 200:
            raise AuthenticationException(response.headers["x-http-response-info"])

        self.set_tokens(response_json=response.json())

    def set_tokens(self, response_json: typing.Dict[str, typing.Any]) -> None:
        """Set the retrieved access and refresh token"""
        self.access_token = response_json["access_token"]
        self.refresh_token = response_json["refresh_token"]
