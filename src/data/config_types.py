from pydantic import BaseModel, HttpUrl
import json
from getpass import getpass
import typing

from src import file_utils


class ApiConfig(BaseModel):
    """
    API config containing the base API URL and the OAuth URL
    provdided by comdirect.
    """

    api_url: HttpUrl
    oauth_url: HttpUrl

    class Config:
        allow_mutation = False

    @classmethod
    def from_config(cls) -> "ApiConfig":
        """Load an API config from a json file
        Args:
            config_path (str): json file path
        Returns:
            ApiConfig: Loaded ApiConfig
        """
        config_json = file_utils.load_config()

        return ApiConfig(
            api_url=config_json["api_url"], oauth_url=config_json["oauth_url"]
        )


class Credentials(BaseModel):
    """User credentials for the comdirect account."""

    client_id: str
    client_secret: str
    username: str
    password: str
    grant_type: str

    class Config:
        allow_mutation = False

    @classmethod
    def get_credentials(
        cls, credentials_path: typing.Optional[str] = None
    ) -> "Credentials":
        """Load credentials from json file"""
        if credentials_path is None:
            credentials_path = file_utils.get_credentials_path()

        with open(credentials_path, "r", encoding="UTF-8") as credentials_file:
            credentials_data = credentials_file.read()
        credentials_json = json.loads(credentials_data)

        return Credentials(
            client_id=credentials_json["client_id"],
            client_secret=credentials_json["client_secret"],
            grant_type=credentials_json["grant_type"],
            username=input(
                "Username (eight digit 'Zugangsnummer'/Benutzername from comdirect): "
            ),
            password=getpass(),
        )
