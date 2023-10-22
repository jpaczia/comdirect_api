from pydantic import BaseModel, Field

from src.handler.DocumentHandler import DocumentHandler


class ComdirectAPI(BaseModel):
    document_handler: DocumentHandler = Field(default_factory=DocumentHandler)
