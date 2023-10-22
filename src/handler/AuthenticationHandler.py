import typing
from pydantic import Field
import requests

from src.handler.AbstractHandler import AbstractHandler
from src.data.config_types import Credentials
from src.handler.AuthenticationException import AuthenticationException


class AuthenticationHandler(AbstractHandler):
    """Handles the authentication against the comdirect API"""

    access_token: typing.Optional[str] = Field(default=None)
    refresh_token: typing.Optional[str] = Field(default=None)
    credentials: Credentials = Field(default_factory=Credentials.get_credentials)
    session_identifier: typing.Optional[str] = Field(default=None)

    def authenticate(self) -> None:
        """Authenticate against the comdirect API"""
        self.retrieve_oauth2_token()
        self.retrieve_session_object()

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

    def set_tokens(self, response_json: typing.Dict[str, typing.Any]) -> None:
        """Set the retrieved access and refresh token"""
        self.access_token = response_json["access_token"]
        self.refresh_token = response_json["refresh_token"]
