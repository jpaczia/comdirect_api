import logging

from src import file_utils
from src.comdirect_api import ComdirectAPI


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt=file_utils.get_time_format(),
    )

    comdirect_api = ComdirectAPI()
    comdirect_api.process_postbox_documents()


if __name__ == "__main__":
    main()
