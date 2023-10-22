import typing
import os
import json


def get_project_dir() -> str:
    project_dir: str = os.path.dirname(os.path.dirname(__file__))
    while "src" in project_dir:
        project_dir = os.path.dirname(project_dir)

    return project_dir


def load_config(config_path: typing.Optional[str] = None):
    if config_path is None:
        config_path = os.path.join(get_project_dir(), "config.json")
    with open(config_path, "r", encoding="UTF-8") as config_file:
        config_data = config_file.read()
    return json.loads(config_data)


def get_credentials_path() -> str:
    """Retrieve path to file with credentials from config file"""
    config_json = load_config()

    if not os.path.exists(config_json["credentials_path"]):
        raise RuntimeError(
            """Credentials file with path in config file doesn't exist.
            Please reconfigure path to the credentials file
            and run the script again."""
        )
    return config_json["credentials_path"]


def get_time_format() -> str:
    return load_config()["time_format"]
