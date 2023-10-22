from src.comdirect_api import ComdirectAPI


def main() -> None:
    comdirect_api = ComdirectAPI()
    comdirect_api.process_postbox_documents()


if __name__ == "__main__":
    main()
