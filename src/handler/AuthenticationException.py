import json


class AuthenticationException(Exception):
    """Exception raised if the authentication fails."""

    def __init__(self, response_info: str) -> None:
        """Initialize the AuthenticationException with severity, key and message info
        retrieved from the comdirect API.

        Args:
            response_info (str): Info retrieved from the comdirect API.
        """
        msg_dict = json.loads(response_info)["messages"][0]
        self.severity: str = msg_dict["severity"]
        self.key: str = msg_dict["key"]
        self.msg: str = msg_dict["message"]

        self.msg_dict = msg_dict
        super().__init__(self.severity, self.key, self.msg)

    def __str__(self) -> str:
        """Return string representation of the AuthenticationException."""
        return f"[{self.severity}] {self.key}: {self.msg}"
