import typing
import requests

from src.handler.AuthenticatedAbstractHandler import AuthenticatedAbstractHandler
from src.data.Document import Document


class DocumentHandler(AuthenticatedAbstractHandler):
    """Retrieves documents from the comdirect postbox"""

    def get_postbox_content_list(self, query_params: str = "") -> typing.Set[Document]:
        """Get list with documents and corresponding metadata in the PostBox.
        To download a document use the function DocumentHandler.get_document().
        Described in section 9.1.1 in the comdirect API documentation.

        Args:
            query_params (str, optional): Optional query params,
                see postman collection for further details. Defaults to "".

        Returns:
            List[Document]: retrieved documents
        """
        url = f"{self.api_config.api_url}/messages/clients/user/v2/documents/{query_params}"
        response_json = self.general_get_request(url=url, payload={})

        return set([Document.from_dict(v) for v in response_json["values"]])

    def get_all_postbox_contents(self) -> typing.Set[Document]:
        """Load all available documents in postbox"""
        result: typing.Set[Document] = set()

        new_documents = True
        iteration = 0
        while new_documents:
            # retrieve next 1000 documents from the postbox
            tmp_documents = self.get_postbox_content_list(
                query_params=f"?paging-first={iteration}&paging-count=1000"
            )

            # check if any documents are new, some documents are retrieved multiple times
            new_documents = len([doc for doc in tmp_documents if doc not in result]) > 0

            if new_documents:
                # new documents found, i.e. check next page for new documents too
                iteration += 1
                result.update(tmp_documents)

        return result

    def get_document(
        self, document_id: str, document_mime_type: str
    ) -> typing.Tuple[str, bytes]:
        """Get specific document.
        Comment in the comdirect API documentation:
        Unread documents are marked as read after the access via this interface.
        Described in section 9.1.2 in the comdirect API documentation.

        Args:
            document_id (str): Document ID
            document_mime_type (str): Mime type of the requested document

        Returns:
            Tuple[str, bytes]: mime type of the retrieved document,
                               document in bytes representation
        """
        url = f"{self.api_config.api_url}/messages/v2/documents/{document_id}"
        headers = self.get_general_headers()
        headers["Accept"] = document_mime_type
        response = requests.get(url, params={}, headers=headers)

        content_type: str = response.headers["content-type"]
        content: bytes = response.content

        return content_type, content
