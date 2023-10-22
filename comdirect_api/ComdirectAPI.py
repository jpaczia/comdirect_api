from pydantic import BaseModel, Field
import os
from tqdm import tqdm
import logging
import typing

from src.handler.DocumentHandler import DocumentHandler
from src.data.Document import Document
from src import file_utils
from src.data.config_types import DocumentClassificationConfig


class ComdirectAPI(BaseModel):
    """Takes care of all the interaction with the Comdirect handlers."""

    document_classification_config: DocumentClassificationConfig = Field(
        default_factory=DocumentClassificationConfig.from_config
    )
    document_handler: DocumentHandler = Field(default_factory=DocumentHandler)
    output_dir: str = Field(default_factory=file_utils.get_output_dir)

    def process_postbox_documents(self) -> None:
        """Process all documents in the postbox"""
        documents = self.document_handler.get_all_postbox_contents()

        unmatched_file_names: typing.List[str] = []
        saved_files: typing.List[str] = []
        for doc in tqdm(documents, desc="Process documents in postbox"):
            doc_path, unmatched = self.process_document(doc)
            if doc_path is not None:
                saved_files.append(doc_path)
            if unmatched:
                unmatched_file_names.append(doc.name)

        if len(saved_files) > 0:
            # print all unmatched files in case of new names or similar cases
            print("\n\n\n")
            print("#########################################################")
            logging.info("Saved files:")
            for saved_file in saved_files:
                logging.info(saved_file)

        if len(unmatched_file_names) > 0:
            # print all unmatched files in case of new names or similar cases
            print("\n\n\n")
            print("#########################################################")
            logging.info("Unmatched files:\n")
            for saved_file in unmatched_file_names:
                logging.info(saved_file)

    def process_document(
        self, document: Document
    ) -> typing.Tuple[typing.Optional[str], bool]:
        """Download document from the postbox if it's new and no ad.
        Skip documents which have been downloaded already."""
        if document.skip_download(
            self.document_classification_config.ignored_file_classes
        ):
            return None, False

        (
            matched_wkn,
            matched_file_class,
        ) = document.classify(self.document_classification_config)
        doc_path = file_utils.replace_invalid_chars(
            os.path.join(
                self.output_dir,
                matched_wkn,
                matched_file_class,
                document.get_document_file_name(),
            )
        )

        if os.path.exists(doc_path):
            # skip files which already have been downloaded
            return None, False

        _, document_content = self.document_handler.get_document(
            document_id=document.document_id, document_mime_type=document.mime_type
        )
        file_utils.save_pdf(content=document_content, pdf_path=doc_path)

        return doc_path, self.document_classification_config.unknown_classification in [
            matched_wkn,
            matched_file_class,
        ]
