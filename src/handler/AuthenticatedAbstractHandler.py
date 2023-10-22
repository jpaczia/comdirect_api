from pydantic import Field
import requests
import typing

from src.handler.AbstractHandler import AbstractHandler
from src.handler.AuthenticationHandler import AuthenticationHandler
from src.handler.AuthenticationException import AuthenticationException


class AuthenticatedAbstractHandler(AbstractHandler):
    """Abstract handler with functionality / properties which is shared by all
    handlers which access parts of the API requiring authentication
    """

    auth_handler: AuthenticationHandler = Field(default_factory=AuthenticationHandler)

    def get_general_headers(self) -> typing.Dict[str, typing.Any]:
        """General headers for a API request.
        Returns:
            Dict[str, Any]: general headers
        """
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_handler.get_access_token()}",
            "x-http-request-info": str(
                {
                    "clientRequestId": {
                        "sessionId": self.session_id,
                        "requestId": AbstractHandler.generate_request_id(),
                    }
                }
            ),
        }

    def general_get_request(
        self,
        url: str,
        payload: typing.Dict[str, typing.Any],
    ) -> typing.Dict[str, typing.Any]:
        """General get request against the comdirect API.
        Args:
            url (str): api url
            payload (Dict[str, Any]): payload of the request
        Raises:
            AuthenticationException: Raised if the authentication fails
        Returns:
            Dict[str, Any]: json representation of the API response.
        """
        headers = self.get_general_headers()
        response = requests.get(url, params=payload, headers=headers)

        if response.status_code != 200:
            raise AuthenticationException(response.headers["x-http-response-info"])

        return response.json()
