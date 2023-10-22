from abc import ABC
from pydantic import BaseModel, Field

from src.data import config_types


class AbstractHandler(BaseModel, ABC):
    """Abstract handler with functionality which is
    shared by all handlers for the comdirect API."""

    api_config: config_types.ApiConfig = Field(
        default_factory=config_types.ApiConfig.from_config
    )
