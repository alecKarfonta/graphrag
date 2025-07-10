#!/usr/bin/env python3
"""
Demo script showing Code RAG + GraphRAG integration.
This demonstrates the complete workflow from code submission to unified search.
"""

import requests
import json
import time
import tempfile
import os
from pathlib import Path

# Configuration
GRAPHRAG_URL = "http://localhost:8000"
CODE_RAG_URL = "http://localhost:8003"

# Sample code to submit
SAMPLE_CODE = '''
"""
E-commerce order processing system.
"""

import datetime
from typing import List, Dict, Optional
from enum import Enum

class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Product:
    """Represents a product in the system."""
    
    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.created_at = datetime.datetime.now()
    
    def update_stock(self, quantity: int) -> bool:
        """Update product stock."""
        if self.stock + quantity >= 0:
            self.stock += quantity
            return True
        return False
    
    def get_total_value(self) -> float:
        """Calculate total value of stock."""
        return self.price * self.stock

class Order:
    """Represents an order in the system."""
    
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.products: List[Product] = []
        self.status = OrderStatus.PENDING
        self.created_at = datetime.datetime.now()
        self.total_amount = 0.0
    
    def add_product(self, product: Product, quantity: int) -> bool:
        """Add a product to the order."""
        if product.stock >= quantity:
            self.products.append(product)
            product.update_stock(-quantity)
            self.total_amount += product.price * quantity
            return True
        return False
    
    def calculate_total(self) -> float:
        """Calculate total order amount."""
        total = sum(product.price for product in self.products)
        return total
    
    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status."""
        self.status = new_status
        print(f"Order {self.order_id} status updated to {new_status.value}")

class OrderProcessor:
    """Processes orders and manages inventory."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.products: Dict[str, Product] = {}
        self.processed_count = 0
    
    def add_product(self, product: Product) -> None:
        """Add a product to inventory."""
        self.products[product.product_id] = product
        print(f"Added product: {product.name}")
    
    def create_order(self, order_id: str, customer_id: str) -> Order:
        """Create a new order."""
        order = Order(order_id, customer_id)
        self.orders[order_id] = order
        return order
    
    def process_order(self, order_id: str) -> bool:
        """Process an order."""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        if order.status == OrderStatus.PENDING:
            order.update_status(OrderStatus.PROCESSING)
            self.processed_count += 1
            return True
        return False
    
    def get_order_analytics(self) -> Dict[str, int]:
        """Get order analytics."""
        analytics = {
            "total_orders": len(self.orders),
            "processed_orders": self.processed_count,
            "pending_orders": sum(1 for order in self.orders.values() 
                                if order.status == OrderStatus.PENDING)
        }
        return analytics

def create_sample_data() -> OrderProcessor:
    """Create sample e-commerce data."""
    processor = OrderProcessor()
    
    # Add products
    products = [
        Product("P001", "Laptop", 999.99, 50),
        Product("P002", "Mouse", 29.99, 100),
        Product("P003", "Keyboard", 79.99, 75)
    ]
    
    for product in products:
        processor.add_product(product)
    
    # Create orders
    order1 = processor.create_order("ORD001", "CUST001")
    order1.add_product(products[0], 1)  # Laptop
    order1.add_product(products[1], 2)  # 2 Mice
    
    order2 = processor.create_order("ORD002", "CUST002")
    order2.add_product(products[2], 1)  # Keyboard
    
    return processor

if __name__ == "__main__":
    # Create sample data
    processor = create_sample_data()
    
    # Process some orders
    processor.process_order("ORD001")
    
    # Get analytics
    analytics = processor.get_order_analytics()
    print(f"Analytics: {analytics}")
'''


def check_services():
    """Check if both services are running."""
    print("🔍 Checking service availability...")
    
    # Check GraphRAG
    try:
        response = requests.get(f"{GRAPHRAG_URL}/health", timeout=5)
        graphrag_status = response.status_code == 200
        print(f"  GraphRAG: {'✅ Available' if graphrag_status else '❌ Not available'}")
    except:
        graphrag_status = False
        print("  GraphRAG: ❌ Not available")
    
    # Check Code RAG
    try:
        response = requests.get(f"{CODE_RAG_URL}/health", timeout=5)
        code_rag_status = response.status_code == 200
        print(f"  Code RAG: {'✅ Available' if code_rag_status else '❌ Not available'}")
    except:
        code_rag_status = False
        print("  Code RAG: ❌ Not available")
    
    return graphrag_status, code_rag_status


def submit_code_to_graphrag(code_content: str, filename: str = "ecommerce.py"):
    """Submit code to GraphRAG via hybrid processing."""
    print(f"\n📤 Submitting code to GraphRAG (hybrid processing)...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_content)
        temp_file = f.name
    
    try:
        # Submit via hybrid processing endpoint
        with open(temp_file, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            data = {'domain': 'code'}
            
            response = requests.post(
                f"{GRAPHRAG_URL}/hybrid/process",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code submitted successfully!")
            print(f"  File type: {result.get('file_type', 'unknown')}")
            print(f"  Language: {result.get('language', 'unknown')}")
            print(f"  Hybrid processing: {result.get('hybrid_processing', False)}")
            
            # Show Code RAG processing result
            if result.get('code_rag_processing'):
                code_rag_result = result['code_rag_processing']
                print(f"  Code RAG routed: {code_rag_result.get('routed', False)}")
                if code_rag_result.get('code_rag_result'):
                    crag_result = code_rag_result['code_rag_result']
                    print(f"  Entities extracted: {len(crag_result.get('entities', []))}")
                    print(f"  Relationships extracted: {len(crag_result.get('relationships', []))}")
            
            return result
        else:
            print(f"❌ Failed to submit code: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    finally:
        # Clean up
        os.unlink(temp_file)


def analyze_code_with_code_rag(code_content: str, filename: str = "ecommerce.py"):
    """Analyze code directly with Code RAG."""
    print(f"\n🔍 Analyzing code with Code RAG directly...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_content)
        temp_file = f.name
    
    try:
        # Analyze with Code RAG
        response = requests.post(
            f"{CODE_RAG_URL}/analyze",
            json={
                "file_path": temp_file,
                "project_name": "ecommerce_demo"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code RAG analysis successful!")
            print(f"  Language: {result.get('language', 'unknown')}")
            print(f"  Entities found: {len(result.get('entities', []))}")
            print(f"  Relationships found: {len(result.get('relationships', []))}")
            
            # Show detailed entities
            print("\n📋 Entities extracted by Code RAG:")
            for i, entity in enumerate(result.get('entities', [])[:10]):  # Show first 10
                print(f"  {i+1}. {entity.get('name', 'Unknown')} ({entity.get('entity_type', 'unknown')})")
                if entity.get('docstring'):
                    print(f"     Description: {entity['docstring'][:60]}...")
                if entity.get('line_start') and entity.get('line_end'):
                    print(f"     Lines: {entity['line_start']}-{entity['line_end']}")
            
            # Show relationships
            if result.get('relationships'):
                print("\n🔗 Relationships extracted by Code RAG:")
                for i, rel in enumerate(result.get('relationships', [])[:5]):  # Show first 5
                    print(f"  {i+1}. {rel.get('source_entity_id', 'Unknown')} -> {rel.get('relationship_type', 'unknown')} -> {rel.get('target_entity_id', 'Unknown')}")
            
            return result
        else:
            print(f"❌ Code RAG analysis failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    finally:
        # Clean up
        os.unlink(temp_file)


def search_code_in_graphrag(query: str):
    """Search for code in GraphRAG."""
    print(f"\n🔍 Searching GraphRAG for: '{query}'")
    
    try:
        response = requests.post(
            f"{GRAPHRAG_URL}/search",
            json={
                "query": query,
                "top_k": 5
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result.get('results', []))} results")
            
            for i, search_result in enumerate(result.get('results', [])[:3]):  # Show first 3
                print(f"\n  Result {i+1}:")
                print(f"    Content: {search_result.get('content', '')[:100]}...")
                print(f"    Source: {search_result.get('source', 'unknown')}")
                print(f"    Score: {search_result.get('score', 0):.3f}")
                print(f"    Type: {search_result.get('result_type', 'unknown')}")
            
            return result
        else:
            print(f"❌ Search failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None


def demo_integration():
    """Run the complete integration demo."""
    print("🚀 Code RAG + GraphRAG Integration Demo")
    print("=" * 50)
    
    # Step 1: Check services
    graphrag_ok, code_rag_ok = check_services()
    
    if not graphrag_ok:
        print("\n❌ GraphRAG is not available. Please start it first:")
        print("  cd backend && python main.py")
        return
    
    if not code_rag_ok:
        print("\n❌ Code RAG is not available. Please start it first:")
        print("  cd code_rag && python -m uvicorn api.main:app --port 8003")
        return
    
    print("\n✅ Both services are available!")
    
    # Step 2: Submit code to GraphRAG (hybrid processing)
    hybrid_result = submit_code_to_graphrag(SAMPLE_CODE)
    
    # Step 3: Analyze code directly with Code RAG
    code_rag_result = analyze_code_with_code_rag(SAMPLE_CODE)
    
    # Step 4: Wait a moment for indexing
    print("\n⏳ Waiting for indexing...")
    time.sleep(3)
    
    # Step 5: Search for code in GraphRAG
    search_queries = [
        "order processing system",
        "Product class methods",
        "order status enumeration",
        "inventory management"
    ]
    
    for query in search_queries:
        search_code_in_graphrag(query)
    
    print("\n🎉 Integration demo completed!")
    print("\nSummary:")
    print(f"  - Code submitted to GraphRAG: {'✅' if hybrid_result else '❌'}")
    print(f"  - Code analyzed by Code RAG: {'✅' if code_rag_result else '❌'}")
    print(f"  - Entities extracted: {len(code_rag_result.get('entities', [])) if code_rag_result else 0}")
    print(f"  - Relationships extracted: {len(code_rag_result.get('relationships', [])) if code_rag_result else 0}")
    print("  - Search queries executed: 4")


if __name__ == "__main__":
    demo_integration() 