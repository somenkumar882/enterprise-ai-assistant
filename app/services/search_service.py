
from app.core.config import settings
from elasticsearch import Elasticsearch

# Elasticsearch client implementation
class ElasticsearchClient:
    def __init__(self, host, port, username, password, index_name):
        self.index_name = index_name
        try:
            self.client = Elasticsearch(
                hosts=[{"host": host, "port": port, "scheme": "https"}],
                basic_auth=(username, password),
                verify_certs=False,
                ssl_show_warn=False
            )
            # Test connection
            if self.client.ping():
                print(f"Connected to Elasticsearch at {host}:{port}")
                # Create index if it doesn't exist
                self._create_index_if_not_exists()
            else:
                raise Exception("Failed to ping Elasticsearch")
        except Exception as e:
            raise Exception(f"Failed to connect to Elasticsearch: {e}")
    
    def _create_index_if_not_exists(self):
        """Create index with basic settings if it doesn't exist"""
        try:
            if not self.client.indices.exists(index=self.index_name):
                self.client.indices.create(
                    index=self.index_name,
                    body={
                        "settings": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0
                        },
                        "mappings": {
                            "properties": {
                                "content": {"type": "text"},
                                "timestamp": {"type": "date"}
                            }
                        }
                    }
                )
                print(f"Created index: {self.index_name}")
        except Exception as e:
            print(f"Warning: Could not create index: {e}")
    
    def search(self, search_text, top=3):
        """Search documents in Elasticsearch"""
        try:
            response = self.client.search(
                index=self.index_name,
                body={
                    "query": {
                        "multi_match": {
                            "query": search_text,
                            "fields": ["content"]
                        }
                    },
                    "size": top
                }
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({"content": hit["_source"]["content"]})
            
            return results if results else [{"content": f"No results found for: {search_text}"}]
        except Exception as e:
            print(f"Search error: {e}")
            return [{"content": f"Error searching: {str(e)}"}]
    
    def upload_documents(self, documents):
        """Upload documents to Elasticsearch"""
        try:
            for i, doc in enumerate(documents):
                self.client.index(
                    index=self.index_name,
                    document={"content": doc}
                )
            # Refresh index to make documents searchable
            self.client.indices.refresh(index=self.index_name)
            return documents
        except Exception as e:
            print(f"Upload error: {e}")
            return []

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
            "What is the national language of India? Hindi",
            "What is the capital of France? Paris",
            "What is the largest ocean on Earth? Pacific Ocean",
            "Who wrote Hamlet? William Shakespeare",
            "What is the speed of light? Approximately 299,792 kilometers per second",
            "What is the chemical symbol for water? H2O"
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
    # Try to initialize Elasticsearch client first
    client = ElasticsearchClient(
        host=settings.ELASTICSEARCH_HOST,
        port=settings.ELASTICSEARCH_PORT,
        username=settings.ELASTICSEARCH_USERNAME,
        password=settings.ELASTICSEARCH_PASSWORD,
        index_name=settings.ELASTICSEARCH_INDEX
    )
    print("Using Elasticsearch client")
except Exception as es_error:
    print(f"Elasticsearch initialization failed: {es_error}. Trying Azure Search...")
    try:
        if settings.SEARCH_ENDPOINT.startswith("http://localhost"):
            client = MockSearchClient(
                endpoint=settings.SEARCH_ENDPOINT,
                index_name=settings.SEARCH_INDEX,
                credential=None
            )
            print("Using Mock Search client")
        else:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            client = SearchClient(
                endpoint=settings.SEARCH_ENDPOINT,
                index_name=settings.SEARCH_INDEX,
                credential=AzureKeyCredential(settings.SEARCH_KEY)
            )
            print("Using Azure Search client")
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
