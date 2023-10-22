from pydantic import Field

from src.handler.AbstractHandler import AbstractHandler
from src.handler.AuthenticationHandler import AuthenticationHandler


class AuthenticatedAbstractHandler(AbstractHandler):
    """Abstract handler with functionality / properties which is shared by all
    handlers which access parts of the API requiring authentication
    """

    auth_handler: AuthenticationHandler = Field(default_factory=AuthenticationHandler)
