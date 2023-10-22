from pydantic import BaseModel
import datetime
import typing

from src.data.DocumentMetaData import DocumentMetaData
from src import file_utils
from src.data.config_types import DocumentClassificationConfig


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

    def get_document_file_name(self) -> str:
        return file_utils.replace_invalid_chars(
            f"{self.name}.{self.get_file_extension()}"
        )

    def get_file_extension(self) -> str:
        """Get document extension from mime type"""
        ext = self.mime_type.split("/")[1]
        return ext

    def classify(
        self, document_classification_config: DocumentClassificationConfig
    ) -> typing.Tuple[str, str]:
        matched_wkn: str = document_classification_config.unknown_classification
        for wkn in document_classification_config.known_depot_positions:
            if wkn in self.name:
                matched_wkn = wkn
                break

        matched_file_class: str = document_classification_config.unknown_classification
        for known_file_class in document_classification_config.known_file_classes:
            if known_file_class in self.name:
                matched_file_class = known_file_class
                break

        return matched_wkn, matched_file_class

    def skip_download(self, ignored_file_classes: typing.Set[str]) -> bool:
        """Checks if document download should be skipped
        (i.e. docment is an ad or belongs to an ignored file class)."""
        return self.advertisement or any(
            [
                ignored_file_class in self.name
                for ignored_file_class in ignored_file_classes
            ]
        )

    def __hash__(self) -> int:
        return self.document_id.__hash__()
