
from app.core.config import settings
from elasticsearch import Elasticsearch

# Elasticsearch client implementation
class ElasticsearchClient:
    def __init__(self, host, port, username, password, index_name):
        self.index_name = index_name
        try:
            # Determine scheme based on host
            scheme = "http" if host == "localhost" or host.startswith("127.") else "https"
            
            # Build connection URL
            url = f"{scheme}://{host}:{port}"
            print(f"Attempting to connect to Elasticsearch at {url}...")
            
            # Initialize Elasticsearch client
            self.client = Elasticsearch(
                [url],
                basic_auth=(username, password) if username and password else None,
                verify_certs=False,
                request_timeout=10
            )
            
            # Test connection with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if self.client.ping():
                        print(f"Connected to Elasticsearch at {url}")
                        # Create index if it doesn't exist
                        self._create_index_if_not_exists()
                        return
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Connection attempt {attempt + 1} failed: {e}. Retrying...")
                        import time
                        time.sleep(1)
                    else:
                        raise Exception(f"Failed to ping Elasticsearch after {max_retries} attempts: {e}")
            
            raise Exception("Failed to ping Elasticsearch")
        except Exception as e:
            raise Exception(f"Failed to connect to Elasticsearch: {e}")
    
    def _create_index_if_not_exists(self):
        """Create indexes with basic settings if they don't exist"""
        try:
            # Create documents index
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
            
            # Create queries index for storing responses
            queries_index = f"{self.index_name}-queries"
            if not self.client.indices.exists(index=queries_index):
                self.client.indices.create(
                    index=queries_index,
                    body={
                        "settings": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0
                        },
                        "mappings": {
                            "properties": {
                                "query": {"type": "text"},
                                "answer": {"type": "text"},
                                "sources": {
                                    "type": "text"  # Store sources as text array
                                },
                                "timestamp": {"type": "date"},
                                "source_count": {"type": "integer"}
                            }
                        }
                    }
                )
                print(f"Created index: {queries_index}")
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
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

def store_query_response(query, answer, sources):
    """Store query, answer, and sources in Elasticsearch"""
    try:
        from datetime import datetime
        
        # Ensure sources is a list of strings
        if not isinstance(sources, list):
            sources = [sources]
        
        document = {
            "query": query,
            "answer": answer,
            "sources": sources,  # Store as array of strings
            "timestamp": datetime.utcnow().isoformat(),
            "source_count": len(sources)
        }
        
        if isinstance(client, ElasticsearchClient):
            # Store in a separate queries index
            response = client.client.index(
                index=f"{settings.ELASTICSEARCH_INDEX}-queries",
                document=document
            )
            client.client.indices.refresh(index=f"{settings.ELASTICSEARCH_INDEX}-queries")
            return response.get("_id", None)
        else:
            print("Warning: Response storage only supported with Elasticsearch")
            return None
    except Exception as e:
        print(f"Error storing query response: {e}")
        return None

def retrieve_query_responses(query_text=None, limit=10):
    """Retrieve stored query responses from Elasticsearch"""
    try:
        if isinstance(client, ElasticsearchClient):
            index_name = f"{settings.ELASTICSEARCH_INDEX}-queries"
            
            if query_text:
                # Search for similar queries
                response = client.client.search(
                    index=index_name,
                    body={
                        "query": {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["query", "answer"]
                            }
                        },
                        "size": limit,
                        "sort": [{"timestamp": {"order": "desc"}}]
                    }
                )
            else:
                # Get latest responses
                response = client.client.search(
                    index=index_name,
                    body={
                        "query": {"match_all": {}},
                        "size": limit,
                        "sort": [{"timestamp": {"order": "desc"}}]
                    }
                )
            
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                source["id"] = hit["_id"]
                results.append(source)
            
            return results
        else:
            print("Warning: Response retrieval only supported with Elasticsearch")
            return []
    except Exception as e:
        print(f"Error retrieving query responses: {e}")
        return []

def get_query_response_by_id(response_id):
    """Retrieve a specific stored query response by ID"""
    try:
        if isinstance(client, ElasticsearchClient):
            response = client.client.get(
                index=f"{settings.ELASTICSEARCH_INDEX}-queries",
                id=response_id
            )
            return {**response["_source"], "id": response["_id"]}
        else:
            return None
    except Exception as e:
        print(f"Error retrieving response: {e}")
        return None

def check_cached_response(query):
    """Check if a similar query already has a cached response"""
    try:
        if isinstance(client, ElasticsearchClient):
            index_name = f"{settings.ELASTICSEARCH_INDEX}-queries"
            
            response = client.client.search(
                index=index_name,
                body={
                    "query": {
                        "match": {
                            "query": {
                                "query": query,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    "size": 1,
                    "sort": [{"timestamp": {"order": "desc"}}]
                }
            )
            
            if response["hits"]["hits"]:
                hit = response["hits"]["hits"][0]
                return {**hit["_source"], "id": hit["_id"]}
            return None
        else:
            return None
    except Exception as e:
        print(f"Error checking cache: {e}")
        return None
