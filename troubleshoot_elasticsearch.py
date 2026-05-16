#!/usr/bin/env python
"""
Elasticsearch Connection Troubleshooting Script
Tests Elasticsearch connection and provides diagnostic information
"""

import sys
import socket
import time
from urllib.request import urlopen
from urllib.error import URLError

# Use ASCII-compatible symbols for Windows
CHECK = "[OK]"
CROSS = "[ERROR]"

def check_port_open(host, port, timeout=3):
    """Check if a port is open on a host"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    except Exception as e:
        print(f"Error checking port: {e}")
        return False
    finally:
        sock.close()

def check_elasticsearch_connection():
    """Test Elasticsearch connection"""
    from app.core.config import settings
    
    host = settings.ELASTICSEARCH_HOST
    port = settings.ELASTICSEARCH_PORT
    username = settings.ELASTICSEARCH_USERNAME
    password = settings.ELASTICSEARCH_PASSWORD
    
    print("=" * 60)
    print("ELASTICSEARCH CONNECTION TROUBLESHOOTING")
    print("=" * 60)
    
    print(f"\n1. Connection Parameters:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Username: {username}")
    print(f"   Index: {settings.ELASTICSEARCH_INDEX}")
    
    # Check if host is reachable
    print(f"\n2. Checking if host {host}:{port} is reachable...")
    if check_port_open(host, port):
        print(f"   {CHECK} Port {port} is open on {host}")
    else:
        print(f"   {CROSS} Port {port} is NOT open on {host}")
        print(f"\n   SOLUTION:")
        print(f"   - Make sure Elasticsearch is running")
        print(f"   - If using Docker: docker-compose up elasticsearch")
        print(f"   - Check if {host}:{port} is the correct address")
        return False
    
    # Try to connect with HTTP
    print(f"\n3. Attempting HTTP connection to Elasticsearch...")
    url = f"http://{host}:{port}"
    try:
        response = urlopen(url, timeout=5)
        print(f"   {CHECK} HTTP connection successful")
        print(f"   Server response: {response.status}")
    except URLError as e:
        print(f"   {CROSS} HTTP connection failed: {e}")
        
    # Try Elasticsearch Python client
    print(f"\n4. Testing Elasticsearch Python client...")
    try:
        from elasticsearch import Elasticsearch
        
        scheme = "http" if host == "localhost" or host.startswith("127.") else "https"
        es_url = f"{scheme}://{host}:{port}"
        
        print(f"   Connecting to: {es_url}")
        client = Elasticsearch(
            [es_url],
            basic_auth=(username, password) if username and password else None,
            verify_certs=False,
            request_timeout=10
        )
        
        if client.ping():
            print(f"   {CHECK} Elasticsearch client ping successful!")
            
            # Get cluster info
            info = client.info()
            print(f"\n5. Elasticsearch Cluster Information:")
            print(f"   Version: {info['version']['number']}")
            print(f"   Cluster: {info['cluster_name']}")
            
            # List indexes
            print(f"\n6. Existing Indexes:")
            indices = client.indices.list()
            for index_name in indices:
                try:
                    count = client.count(index=index_name)
                    print(f"   - {index_name}: {count['count']} documents")
                except:
                    print(f"   - {index_name}")
            
            return True
        else:
            print(f"   {CROSS} Elasticsearch client ping failed")
            return False
            
    except Exception as e:
        print(f"   {CROSS} Error: {e}")
        print(f"\n   SOLUTIONS:")
        print(f"   - Check if Elasticsearch container is running")
        print(f"   - Verify connection parameters in .env file")
        print(f"   - Check Elasticsearch logs: docker logs <container_name>")
        return False

def test_mock_client():
    """Test if mock client is working as fallback"""
    print(f"\n7. Testing Mock Search Client (Fallback)...")
    try:
        from app.services.search_service import MockSearchClient
        from app.core.config import settings
        
        mock = MockSearchClient(
            endpoint=settings.SEARCH_ENDPOINT,
            index_name=settings.SEARCH_INDEX,
            credential=None
        )
        
        results = mock.search("India")
        print(f"   {CHECK} Mock client working")
        print(f"   Sample search result: {results[0] if results else 'No results'}")
        return True
    except Exception as e:
        print(f"   {CROSS} Mock client failed: {e}")
        return False

def main():
    """Run all diagnostics"""
    try:
        # Check basic connectivity
        es_connected = check_elasticsearch_connection()
        
        # Test mock client
        test_mock_client()
        
        print("\n" + "=" * 60)
        if es_connected:
            print("{} ELASTICSEARCH IS WORKING CORRECTLY".format(CHECK))
            print("\nYou can now:")
            print("  - Start the FastAPI server: uvicorn app.main:app --reload")
            print("  - Make requests to: http://localhost:8000/api/ask")
        else:
            print("{} ELASTICSEARCH CONNECTION FAILED".format(CROSS))
            print("\nFallback Options:")
            print("  1. Start Docker Compose: docker-compose up --build")
            print("  2. Or use Azure Search by configuring SEARCH_ENDPOINT")
            print("  3. Or continue with mock search (local development only)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
