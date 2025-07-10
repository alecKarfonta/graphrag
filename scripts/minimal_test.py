import requests
import os

BASE_URL = "http://localhost:8000"

def ingest_sample_data():
    """Ingest sample data to populate the knowledge graph."""
    print("Ingesting sample data...")
    file_path = "sample_text.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975.")
    
    with open(file_path, "rb") as f:
        try:
            response = requests.post(
                f"{BASE_URL}/ingest-documents",
                files={"files": (os.path.basename(file_path), f, "text/plain")},
                data={"document_type": "text"},
                timeout=300,  # Increased timeout
            )
            response.raise_for_status()
            print("✅ Sample data ingested successfully.")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error ingesting data: {e}")

if __name__ == "__main__":
    ingest_sample_data() 