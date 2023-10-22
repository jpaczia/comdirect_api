from pydantic import BaseModel, HttpUrl
import json
from getpass import getpass
import typing
from collections import Counter

from src import file_utils


def ensure_no_duplicates(elements: typing.List[str]) -> None:
    duplicates: typing.List[str] = [k for k, v in Counter(elements).items() if v > 1]

    if len(duplicates) > 0:
        raise ValueError(f"Duplicates in config: {', '.join(duplicates)}")


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


class DocumentClassificationConfig(BaseModel):
    """Config for classifying documents"""

    known_file_classes: typing.Set[str]
    ignored_file_classes: typing.Set[str]
    unknown_classification: str
    known_depot_positions: typing.Set[str]

    class Config:
        allow_mutation = False

    @classmethod
    def from_config(
        cls, config_path: typing.Optional[str] = None
    ) -> "DocumentClassificationConfig":
        """Load document classification config from json file"""
        config_json = file_utils.load_config(config_path)
        file_classes = config_json["file_classes"]

        # ensure there are no duplicates in the config to keep it short
        ensure_no_duplicates(file_classes["known"])
        ensure_no_duplicates(file_classes["ignored"])
        ensure_no_duplicates(config_json["depot_positions"])

        # ensure there's no overlap between the file classes
        # "known" and "ignored" in the config
        file_class_overlap: typing.Set[str] = set.intersection(
            set(file_classes["known"]), set(file_classes["ignored"])
        )
        if len(file_class_overlap) > 0:
            raise ValueError(
                "Overlap between the file classes 'known' and 'ignored' in the config file'."
                f"The following elements are in both lists: {', '.join(list(file_class_overlap))}"
            )

        return DocumentClassificationConfig(
            known_file_classes=set(file_classes["known"]),
            ignored_file_classes=set(file_classes["ignored"]),
            unknown_classification=file_classes["unknown"],
            known_depot_positions=set(config_json["depot_positions"]),
        )
