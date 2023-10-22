from pydantic import BaseModel
import datetime
import typing

from src.data.DocumentMetaData import DocumentMetaData


class Document(BaseModel):
    """Documents which can be retrieved from the comdirect postbox."""

    # comdirect description:
    # UUID des Dokuments
    document_id: str

    # comdirect description:
    # Betreff/Titel des Dokuments
    name: str

    # comdirect description:
    # Eingangsdatum/Erstellungsdatum
    date_creation: datetime.date

    # comdirect description:
    # MimeType des Dokuments
    mime_type: str

    # comdirect description:
    # TRUE, wenn ein Dokument löschbar ist
    deleteable: bool

    # comdirect description:
    # TRUE, wenn es sich bei dem Dokument um Werbung handelt
    advertisement: bool

    # comdirect description:
    # Metadaten zum Dokument
    document_metadata: DocumentMetaData

    # comdirect description:
    # no description available, found in the API response
    category_id: int

    @classmethod
    def from_dict(cls, input_dict: typing.Dict[str, typing.Any]) -> "Document":
        return Document(
            document_id=input_dict["documentId"],
            name=input_dict["name"],
            date_creation=datetime.date.fromisoformat(input_dict["dateCreation"]),
            mime_type=input_dict["mimeType"],
            deleteable=input_dict["deletable"],
            advertisement=input_dict["advertisement"],
            document_metadata=DocumentMetaData.from_dict(
                input_dict["documentMetaData"]
            ),
            category_id=input_dict["categoryId"],
        )
