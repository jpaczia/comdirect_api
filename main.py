from src.comdirect_api import ComdirectAPI


def main() -> None:
    comdirect_api = ComdirectAPI()
    comdirect_api.document_handler.auth_handler.authenticate()


if __name__ == "__main__":
    main()
