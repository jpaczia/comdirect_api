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

    def authenticate(self) -> None:
        """Authenticate against the comdirect API"""
        self.retrieve_oauth2_token()

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

    def set_tokens(self, response_json: typing.Dict[str, typing.Any]) -> None:
        """Set the retrieved access and refresh token"""
        self.access_token = response_json["access_token"]
        self.refresh_token = response_json["refresh_token"]
