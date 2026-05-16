
from app.core.config import settings

# Mock implementation for local development
class MockAzureOpenAI:
    def __init__(self, api_key, azure_endpoint, api_version):
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        self.embeddings = self.Embeddings()
    
    class Embeddings:
        def create(self, model, input):
            return type('obj', (object,), {
                'data': [type('obj', (object,), {
                    'embedding': [0.1] * 1536
                })()]
            })()

try:
    if settings.OPENAI_API_KEY.startswith("mock"):
        client = MockAzureOpenAI(
            api_key=settings.OPENAI_API_KEY,
            azure_endpoint=settings.OPENAI_ENDPOINT,
            api_version="2024-02-01"
        )
    else:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=settings.OPENAI_API_KEY,
            azure_endpoint=settings.OPENAI_ENDPOINT,
            api_version="2024-02-01"
        )
except Exception as e:
    print(f"Warning: Could not initialize Azure OpenAI client: {e}. Using mock client.")
    client = MockAzureOpenAI(
        api_key=settings.OPENAI_API_KEY,
        azure_endpoint=settings.OPENAI_ENDPOINT,
        api_version="2024-02-01"
    )

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
