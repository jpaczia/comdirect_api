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


def get_output_dir() -> str:
    """Retrieve output directory from config file"""
    config_json = load_config()

    if not (
        os.path.exists(config_json["output_dir"])
        and os.path.isdir(config_json["output_dir"])
    ):
        raise RuntimeError(
            """Output directory in config file doesn't exist.
            Please reconfigure path to the output directy
            and run the script again."""
        )
    return config_json["output_dir"]


def replace_invalid_chars(pdf_path_input: str) -> str:
    """Replace invalid chars in file name"""

    # special cases which need to be handled before anything else
    pdf_path_preprocessed = pdf_path_input.replace("-/", "-")

    # normal cases
    pdf_dir = os.path.dirname(pdf_path_preprocessed)
    pdf_file_name = os.path.basename(pdf_path_preprocessed).split("/")[-1]

    invalid_chars = '/<>:"\\|?*'
    for invalid_char in invalid_chars:
        pdf_file_name = pdf_file_name.replace(invalid_char, " ")

    pdf_file_name = " ".join(pdf_file_name.split())
    pdf_path_output = os.path.join(pdf_dir, pdf_file_name)
    return pdf_path_output


def save_pdf(content: bytes, pdf_path: str) -> None:
    """
    Save bytestream as pdf file
    Args:
        content (bytes): pdf file as bytestream
        pdf_path (str): path of pdf file
    """
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(content)


def get_time_format() -> str:
    return load_config()["time_format"]
