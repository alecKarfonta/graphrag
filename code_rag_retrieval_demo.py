#!/usr/bin/env python3
"""
Code RAG Retrieval Demonstration
Shows how Code RAG can search and retrieve code entities.
"""

import sys
sys.path.append('/home/alec/git/graphrag')

from code_rag.parsers.python_parser import PythonParser
from code_rag.search.search_engine import CodeSearchEngine
import tempfile
import os

# Sample e-commerce code to demonstrate retrieval
SAMPLE_CODE = '''
"""E-commerce order processing system."""

from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import hashlib

class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Product:
    """Product in the e-commerce system."""
    
    def __init__(self, product_id: str, name: str, price: float, category: str):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.created_at = datetime.now()
    
    def calculate_tax(self, tax_rate: float) -> float:
        """Calculate tax amount for the product."""
        return self.price * tax_rate
    
    def apply_discount(self, discount_percent: float) -> float:
        """Apply discount and return new price."""
        discount_amount = self.price * (discount_percent / 100)
        return self.price - discount_amount
    
    def get_display_info(self) -> Dict[str, str]:
        """Get product information for display."""
        return {
            'id': self.product_id,
            'name': self.name,
            'price': f'${self.price:.2f}',
            'category': self.category
        }

class Customer:
    """Customer in the system."""
    
    def __init__(self, customer_id: str, email: str, name: str):
        self.customer_id = customer_id
        self.email = email
        self.name = name
        self.order_history: List[str] = []
    
    def add_order_to_history(self, order_id: str) -> None:
        """Add order to customer's history."""
        self.order_history.append(order_id)
    
    def get_order_count(self) -> int:
        """Get total number of orders."""
        return len(self.order_history)

class Order:
    """Order in the e-commerce system."""
    
    def __init__(self, order_id: str, customer: Customer):
        self.order_id = order_id
        self.customer = customer
        self.products: List[Product] = []
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.total_amount = 0.0
    
    def add_product(self, product: Product, quantity: int = 1) -> None:
        """Add product to the order."""
        for _ in range(quantity):
            self.products.append(product)
        self.calculate_total()
    
    def remove_product(self, product_id: str) -> bool:
        """Remove product from order."""
        for i, product in enumerate(self.products):
            if product.product_id == product_id:
                del self.products[i]
                self.calculate_total()
                return True
        return False
    
    def calculate_total(self) -> float:
        """Calculate total order amount."""
        self.total_amount = sum(product.price for product in self.products)
        return self.total_amount
    
    def apply_coupon(self, coupon_code: str, discount_percent: float) -> bool:
        """Apply coupon discount to order."""
        if self.validate_coupon(coupon_code):
            discount = self.total_amount * (discount_percent / 100)
            self.total_amount -= discount
            return True
        return False
    
    def validate_coupon(self, coupon_code: str) -> bool:
        """Validate coupon code."""
        valid_coupons = ['SAVE10', 'WELCOME20', 'LOYAL15']
        return coupon_code in valid_coupons
    
    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status."""
        self.status = new_status

class PaymentProcessor:
    """Handles payment processing."""
    
    def __init__(self):
        self.processed_payments = {}
    
    def process_payment(self, order: Order, payment_method: str) -> bool:
        """Process payment for an order."""
        payment_id = self.generate_payment_id(order.order_id)
        
        if self.validate_payment_method(payment_method):
            self.processed_payments[payment_id] = {
                'order_id': order.order_id,
                'amount': order.total_amount,
                'method': payment_method,
                'timestamp': datetime.now()
            }
            return True
        return False
    
    def generate_payment_id(self, order_id: str) -> str:
        """Generate unique payment ID."""
        return hashlib.md5(f'{order_id}_{datetime.now()}'.encode()).hexdigest()
    
    def validate_payment_method(self, method: str) -> bool:
        """Validate payment method."""
        valid_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
        return method in valid_methods
    
    def get_payment_history(self, order_id: str) -> Optional[Dict]:
        """Get payment history for an order."""
        for payment_id, payment_info in self.processed_payments.items():
            if payment_info['order_id'] == order_id:
                return payment_info
        return None

class OrderManager:
    """Manages orders and orchestrates the order process."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.customers: Dict[str, Customer] = {}
        self.payment_processor = PaymentProcessor()
        self.order_counter = 0
    
    def create_customer(self, email: str, name: str) -> Customer:
        """Create a new customer."""
        customer_id = f'CUST_{len(self.customers) + 1:04d}'
        customer = Customer(customer_id, email, name)
        self.customers[customer_id] = customer
        return customer
    
    def create_order(self, customer_id: str) -> Optional[Order]:
        """Create a new order for a customer."""
        customer = self.customers.get(customer_id)
        if not customer:
            return None
        
        self.order_counter += 1
        order_id = f'ORD_{self.order_counter:06d}'
        order = Order(order_id, customer)
        self.orders[order_id] = order
        customer.add_order_to_history(order_id)
        return order
    
    def process_order(self, order_id: str, payment_method: str) -> bool:
        """Process an order with payment."""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        if self.payment_processor.process_payment(order, payment_method):
            order.update_status(OrderStatus.PROCESSING)
            return True
        return False
    
    def ship_order(self, order_id: str) -> bool:
        """Mark order as shipped."""
        order = self.orders.get(order_id)
        if order and order.status == OrderStatus.PROCESSING:
            order.update_status(OrderStatus.SHIPPED)
            return True
        return False
    
    def get_order_analytics(self) -> Dict[str, int]:
        """Get analytics about orders."""
        analytics = {
            'total_orders': len(self.orders),
            'pending_orders': 0,
            'processing_orders': 0,
            'shipped_orders': 0,
            'delivered_orders': 0
        }
        
        for order in self.orders.values():
            if order.status == OrderStatus.PENDING:
                analytics['pending_orders'] += 1
            elif order.status == OrderStatus.PROCESSING:
                analytics['processing_orders'] += 1
            elif order.status == OrderStatus.SHIPPED:
                analytics['shipped_orders'] += 1
            elif order.status == OrderStatus.DELIVERED:
                analytics['delivered_orders'] += 1
        
        return analytics
'''


def demonstrate_code_rag_retrieval():
    """Demonstrate Code RAG's retrieval capabilities."""
    print('🔍 Code RAG Retrieval Demonstration')
    print('=' * 50)
    
    # Step 1: Parse the code
    print('STEP 1: Parsing Code with Code RAG')
    print('-' * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_CODE)
        temp_file = f.name
    
    try:
        parser = PythonParser()
        parse_result = parser.parse_file(temp_file)
        
        print(f'✅ Parsed successfully!')
        print(f'  📊 Entities: {len(parse_result.entities)}')
        print(f'  🔗 Relationships: {len(parse_result.relationships)}')
        
        # Show entity breakdown
        entity_types = {}
        for entity in parse_result.entities:
            entity_type = entity.entity_type.value
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print(f'  📋 Entity breakdown:')
        for entity_type, count in entity_types.items():
            print(f'    - {entity_type}: {count}')
        
        # Step 2: Create search engine and index entities
        print('\nSTEP 2: Creating Search Index')
        print('-' * 40)
        
        search_engine = CodeSearchEngine()
        
        # Index all entities
        for entity in parse_result.entities:
            search_engine.add_entity(entity)
        
        print(f'✅ Indexed {len(parse_result.entities)} entities')
        
        # Step 3: Demonstrate semantic search
        print('\nSTEP 3: Semantic Search Demonstrations')
        print('-' * 40)
        
        semantic_queries = [
            'payment processing functionality',
            'calculate total amount',
            'order status management',
            'product discount calculation',
            'customer order history',
            'coupon validation logic'
        ]
        
        for query in semantic_queries:
            print(f'\n🔍 Query: "{query}"')
            
            semantic_results = search_engine.semantic_search(query, top_k=3)
            print(f'  📊 Found {len(semantic_results)} semantic results:')
            
            for i, result in enumerate(semantic_results):
                entity = result['entity']
                score = result['score']
                print(f'    {i+1}. {entity.name} ({entity.entity_type.value}) - Score: {score:.3f}')
                if hasattr(entity, 'docstring') and entity.docstring:
                    print(f'       📝 {entity.docstring}')
                if hasattr(entity, 'line_start') and hasattr(entity, 'line_end'):
                    print(f'       📍 Lines {entity.line_start}-{entity.line_end}')
        
        # Step 4: Demonstrate keyword search
        print('\n\nSTEP 4: Keyword Search Demonstrations')
        print('-' * 40)
        
        keyword_queries = [
            ['payment', 'process'],
            ['order', 'total'],
            ['customer', 'email'],
            ['product', 'price'],
            ['validate', 'coupon']
        ]
        
        for keywords in keyword_queries:
            print(f'\n🔤 Keywords: {keywords}')
            
            keyword_results = search_engine.keyword_search(keywords, top_k=3)
            print(f'  📊 Found {len(keyword_results)} keyword results:')
            
            for i, result in enumerate(keyword_results):
                entity = result['entity']
                score = result['score']
                print(f'    {i+1}. {entity.name} ({entity.entity_type.value}) - Score: {score:.3f}')
        
        # Step 5: Demonstrate type-based search
        print('\n\nSTEP 5: Type-Based Search')
        print('-' * 40)
        
        # Search by entity type
        class_entities = search_engine.search_by_type('class')
        print(f'\n📋 Found {len(class_entities)} classes:')
        for entity in class_entities:
            print(f'  - {entity.name}')
            if hasattr(entity, 'docstring') and entity.docstring:
                print(f'    📝 {entity.docstring}')
        
        function_entities = search_engine.search_by_type('function')
        print(f'\n🔧 Found {len(function_entities)} functions:')
        for entity in function_entities[:8]:  # Show first 8
            print(f'  - {entity.name}')
            if hasattr(entity, 'parameters') and entity.parameters:
                params = ', '.join([f"{p.get('name', '')}: {p.get('type', 'Any')}" for p in entity.parameters])
                print(f'    🔧 Parameters: {params}')
            if hasattr(entity, 'return_type') and entity.return_type:
                print(f'    ↩️  Returns: {entity.return_type}')
        
        # Step 6: Demonstrate advanced search patterns
        print('\n\nSTEP 6: Advanced Search Patterns')
        print('-' * 40)
        
        # Find payment-related functions
        payment_functions = []
        for entity in parse_result.entities:
            if (entity.entity_type.value == 'function' and 
                ('payment' in entity.name.lower() or 
                 (hasattr(entity, 'docstring') and entity.docstring and 'payment' in entity.docstring.lower()))):
                payment_functions.append(entity)
        
        print(f'\n💳 Found {len(payment_functions)} payment-related functions:')
        for func in payment_functions:
            print(f'  - {func.name}')
            if hasattr(func, 'docstring') and func.docstring:
                print(f'    📝 {func.docstring}')
        
        # Find functions that return boolean
        bool_functions = []
        for entity in parse_result.entities:
            if (entity.entity_type.value == 'function' and 
                hasattr(entity, 'return_type') and entity.return_type == 'bool'):
                bool_functions.append(entity)
        
        print(f'\n✅ Found {len(bool_functions)} functions returning bool:')
        for func in bool_functions:
            print(f'  - {func.name} -> {func.return_type}')
            if hasattr(func, 'docstring') and func.docstring:
                print(f'    📝 {func.docstring}')
        
        # Step 7: Demonstrate relationship search
        print('\n\nSTEP 7: Relationship Analysis')
        print('-' * 40)
        
        if parse_result.relationships:
            print(f'🔗 Found {len(parse_result.relationships)} relationships:')
            for rel in parse_result.relationships:
                print(f'  - {rel.source_entity_id} --[{rel.relationship_type.value}]--> {rel.target_entity_id}')
                if rel.context:
                    print(f'    💬 Context: {rel.context}')
        else:
            print('🔗 No relationships found in this code sample')
        
        print('\n' + '=' * 50)
        print('🎉 CODE RAG RETRIEVAL DEMONSTRATION COMPLETE!')
        print('=' * 50)
        print('\n✅ Demonstrated capabilities:')
        print('  🔍 Semantic search - finds relevant code by meaning')
        print('  🔤 Keyword search - finds code by exact terms')
        print('  📋 Type-based search - filter by entity types (class, function, etc.)')
        print('  🔧 Signature search - find functions by parameters and return types')
        print('  📊 Scoring system - ranks results by relevance')
        print('  🔗 Relationship analysis - understand code connections')
        print('\n🎯 Code RAG provides powerful, multi-modal code retrieval!')
        
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    demonstrate_code_rag_retrieval() 