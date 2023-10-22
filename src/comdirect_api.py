from pydantic import BaseModel, Field

from src.handler.DocumentHandler import DocumentHandler


class ComdirectAPI(BaseModel):
    document_handler: DocumentHandler = Field(default_factory=DocumentHandler)

    def process_postbox_documents(self) -> None:
        documents = self.document_handler.get_postbox_content_list()
