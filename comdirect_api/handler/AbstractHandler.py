from abc import ABC
from pydantic import BaseModel, Field
import typing
import time
import uuid

from src.data import config_types
from src import file_utils


def get_session_id() -> str:
    """Get session uuid"""
    return str(uuid.uuid4())


class AbstractHandler(BaseModel, ABC):
    """Abstract handler with functionality which is
    shared by all handlers for the comdirect API."""

    api_config: config_types.ApiConfig = Field(
        default_factory=config_types.ApiConfig.from_config
    )
    time_format: str = file_utils.get_time_format()

    session_id: typing.Optional[str] = Field(default_factory=get_session_id)

    @classmethod
    def generate_request_id(cls) -> str:
        """Returns a request id with 9 characters."""
        return str(round(time.time() * 1000))[-9:]
