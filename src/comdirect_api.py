from pydantic import BaseModel, Field
import os
from tqdm import tqdm

from src.handler.DocumentHandler import DocumentHandler
from src.data.Document import Document
from src import file_utils
from src.data.config_types import DocumentClassificationConfig


class ComdirectAPI(BaseModel):
    document_classification_config: DocumentClassificationConfig = Field(
        default_factory=DocumentClassificationConfig.from_config
    )
    document_handler: DocumentHandler = Field(default_factory=DocumentHandler)
    output_dir: str = Field(default_factory=file_utils.get_output_dir)

    def process_postbox_documents(self) -> None:
        documents = self.document_handler.get_all_postbox_contents()

        for doc in tqdm(documents, desc="Process documents in postbox"):
            self.process_document(doc)

    def process_document(self, document: Document) -> None:
        """Download document from the postbox if it's new and no ad.
        Skip documents which have been downloaded already."""
        if document.skip_download(
            self.document_classification_config.ignored_file_classes
        ):
            return

        doc_name = document.get_document_file_name()
        (
            matched_wkn,
            matched_file_class,
        ) = document.classify(self.document_classification_config)
        doc_path = file_utils.replace_invalid_chars(
            os.path.join(
                self.output_dir,
                matched_wkn,
                matched_file_class,
                doc_name,
            )
        )

        if os.path.exists(doc_path):
            # skip files which already have been downloaded
            return

        _, document_content = self.document_handler.get_document(
            document_id=document.document_id, document_mime_type=document.mime_type
        )
        file_utils.save_pdf(content=document_content, pdf_path=doc_path)
