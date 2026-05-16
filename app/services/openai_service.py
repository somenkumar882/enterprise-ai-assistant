
from app.core.config import settings

# Mock implementation for local development
class MockAzureOpenAI:
    def __init__(self, api_key, azure_endpoint, api_version):
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        self.chat = self.Chat()
        self.embeddings = self.Embeddings()
    
    class Chat:
        def __init__(self):
            self.completions = self.Completions()
        
        class Completions:
            def create(self, model, messages, temperature):
                return type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {
                            'content': f"Mock response to: {messages[0]['content']}"
                        })()
                    })()]
                })()
    
    class Embeddings:
        def create(self, model, input):
            # Return a mock embedding vector (1536 dimensions for GPT models)
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

def generate_answer(query, context):
    prompt = f"Answer based only on context:\n{context}\nQuestion: {query}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content
