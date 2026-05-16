
from app.core.config import settings

# Mock implementation for local development
class MockSearchClient:
    def __init__(self, endpoint, index_name, credential):
        self.endpoint = endpoint
        self.index_name = index_name
        self.documents = []
    
    def search(self, search_text, top=3):
        # Return mock search results
        return [
            {"content": f"Mock document 1 about {search_text}"},
            {"content": f"Mock document 2 about {search_text}"},
            {"content": f"Mock document 3 about {search_text}"}
        ]
    
    def upload_documents(self, documents):
        self.documents.extend(documents)
        return documents

try:
    if settings.SEARCH_ENDPOINT.startswith("http://localhost"):
        client = MockSearchClient(
            endpoint=settings.SEARCH_ENDPOINT,
            index_name=settings.SEARCH_INDEX,
            credential=None
        )
    else:
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        client = SearchClient(
            endpoint=settings.SEARCH_ENDPOINT,
            index_name=settings.SEARCH_INDEX,
            credential=AzureKeyCredential(settings.SEARCH_KEY)
        )
except Exception as e:
    print(f"Warning: Could not initialize Azure Search client: {e}. Using mock client.")
    client = MockSearchClient(
        endpoint=settings.SEARCH_ENDPOINT,
        index_name=settings.SEARCH_INDEX,
        credential=None
    )

def search_documents(query):
    results = client.search(search_text=query, top=3)
    docs = []
    for r in results:
        docs.append(r["content"])
    return docs
