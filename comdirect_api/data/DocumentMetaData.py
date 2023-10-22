import typing
import datetime
from pydantic import BaseModel


class DocumentMetaData(BaseModel):
    """Metadata of documents, provided by comdirect"""

    # comdirect description:
    # TRUE, wenn das Dokument in das Archiv verschoben wurde
    archived: bool

    # comdirect description:
    # Datum, an dem das Dokument gelesen wurde
    date_read: typing.Optional[datetime.date]

    # comdirect description:
    # TRUE, wenn das Dokument gelesen wurde
    already_read: bool

    # comdirect description:
    # TRUE, wenn für das Dokument eine Vorschaltseite
    # im HTML-Format verfügbar ist
    predocument_exists: bool

    @classmethod
    def from_dict(cls, input_dict: typing.Dict[str, typing.Any]) -> "DocumentMetaData":
        return DocumentMetaData(
            archived=input_dict["archived"],
            date_read=datetime.date.fromisoformat(input_dict["dateRead"])
            if "dateRead" in input_dict
            else None,
            already_read=input_dict["alreadyRead"],
            predocument_exists=input_dict["predocumentExists"],
        )
