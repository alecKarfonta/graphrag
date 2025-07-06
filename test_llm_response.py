#!/usr/bin/env python3

import requests
import json

def test_llm_response_generation():
    """Test that LLM response generation is working while entity extraction uses local models."""
    
    print("🧪 Testing LLM Response Generation")
    print("=" * 50)
    
    # Test query that should generate an LLM response
    test_query = "What is the purpose of an engine in a vehicle?"
    
    print(f"📝 Test Query: {test_query}")
    
    try:
        # Test the search endpoint which should use LLM for response generation
        response = requests.post(
            "http://localhost:8000/search",
            data={
                "query": test_query,
                "top_k": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            results = result.get("results", [])
            
            print(f"\n✅ Search successful")
            print(f"📊 Found {len(results)} search results")
            print(f"🤖 LLM Answer: {answer[:200]}...")
            
            if answer and "No relevant information" not in answer:
                print("✅ LLM response generation is working!")
            else:
                print("⚠️ LLM response generation may not be working properly")
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing LLM response: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary: LLM should be working for response generation")

if __name__ == "__main__":
    test_llm_response_generation() 