import requests
import os
import time

BASE_URL = "http://api:8000"

def ingest_sample_data():
    """Ingest sample data to populate the knowledge graph."""
    print("Ingesting sample data...")
    file_path = "sample_text.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.")
    
    with open(file_path, "rb") as f:
        for i in range(5):
            try:
                response = requests.post(
                    f"{BASE_URL}/ingest-documents",
                    files={"files": (os.path.basename(file_path), f, "text/plain")},
                    data={"domain": "technology", "build_knowledge_graph": "true"}
                )
                if response.status_code == 200:
                    print("   ✅ Sample data ingested successfully.")
                    return
                else:
                    print(f"   Attempt {i+1}: Failed to ingest sample data - HTTP {response.status_code}")
            except requests.exceptions.ConnectionError as e:
                print(f"   Attempt {i+1}: Could not connect to API: {e}")
            
            if i < 4:
                print("   Retrying in 5 seconds...")
                time.sleep(5)

        print("   ❌ Failed to ingest sample data after multiple attempts.")


if __name__ == "__main__":
    ingest_sample_data() 