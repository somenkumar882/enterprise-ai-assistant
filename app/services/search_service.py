
from app.core.config import settings

# Mock implementation for local development
class MockSearchClient:
    def __init__(self, endpoint, index_name, credential):
        self.endpoint = endpoint
        self.index_name = index_name
        # Initialize with dummy Q&A data
        self.documents = [
            "Who is Prime minister of India? Narendra Modi",
            "What is capital of India? New Delhi",
            "What is the largest country in the world by area? Russia",
            "Who is the current President of the United States? Joe Biden",
            "What is the smallest country in the world? Vatican City",
            "What is the population of India? Approximately 1.4 billion",
            "What is the currency of India? Indian Rupee (INR)",
            "When was India independent? August 15, 1947",
            "What is the national animal of India? Bengal Tiger",
            "What is the national language of India? Hindi"
        ]
    
    def search(self, search_text, top=3):
        # Search through documents for relevant matches
        search_lower = search_text.lower()
        matched_docs = []
        
        for doc in self.documents:
            if search_lower in doc.lower():
                matched_docs.append({"content": doc})
        
        # If no exact matches, return documents that contain any keyword
        if not matched_docs:
            keywords = search_text.lower().split()
            for doc in self.documents:
                doc_lower = doc.lower()
                if any(keyword in doc_lower for keyword in keywords):
                    matched_docs.append({"content": doc})
        
        # Return top N results
        return matched_docs[:top] if matched_docs else [{"content": f"No results found for: {search_text}"}]
    
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
