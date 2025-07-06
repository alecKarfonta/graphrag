#!/usr/bin/env python3
"""
Domain Filters Test for Knowledge Graph View
Tests domain filtering functionality for knowledge graph visualization.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_domain_filters():
    """Test domain filtering functionality for knowledge graph view."""
    print("🚀 Starting Domain Filters Test for Knowledge Graph View...")
    print("=" * 80)
    
    # Test 1: Get available domains
    print("🔍 Test 1: Get Available Domains")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-graph/domains")
        
        if response.status_code == 200:
            result = response.json()
            domains = result.get("domains", [])
            count = result.get("count", 0)
            
            print(f"   ✅ Available domains: {domains}")
            print(f"   📊 Total domains: {count}")
            
            if domains:
                print(f"   📋 Sample domains: {domains[:3]}")
            else:
                print("   ⚠️  No domains found - may need to ingest documents first")
                
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 2: Get domain statistics
    print("🔍 Test 2: Get Domain Statistics")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-graph/domain-stats")
        
        if response.status_code == 200:
            result = response.json()
            domain_stats = result
            
            print(f"   ✅ Domain statistics retrieved")
            print(f"   📊 Domains with stats: {len(domain_stats)}")
            
            for domain, stats in domain_stats.items():
                nodes = stats.get("nodes", 0)
                edges = stats.get("edges", 0)
                print(f"   📋 {domain}: {nodes} nodes, {edges} edges")
                
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 3: Get filtered graph statistics by domain
    print("🔍 Test 3: Get Filtered Graph Statistics by Domain")
    try:
        # First get available domains
        domains_response = requests.get(f"{BASE_URL}/knowledge-graph/domains")
        if domains_response.status_code == 200:
            domains = domains_response.json().get("domains", [])
            
            if domains:
                # Test with first available domain
                test_domain = domains[0]
                response = requests.get(f"{BASE_URL}/knowledge-graph/stats?domain={test_domain}")
                
                if response.status_code == 200:
                    result = response.json()
                    nodes = result.get("nodes", 0)
                    edges = result.get("edges", 0)
                    filtered = result.get("filtered", False)
                    
                    print(f"   ✅ Filtered stats for domain '{test_domain}':")
                    print(f"   📊 Nodes: {nodes}")
                    print(f"   📊 Edges: {edges}")
                    print(f"   📊 Filtered: {filtered}")
                    
                else:
                    print(f"   ❌ Failed - HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("   ⚠️  No domains available for testing")
        else:
            print(f"   ❌ Failed to get domains - HTTP {domains_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 4: Export filtered graph by domain
    print("🔍 Test 4: Export Filtered Graph by Domain")
    try:
        # First get available domains
        domains_response = requests.get(f"{BASE_URL}/knowledge-graph/domains")
        if domains_response.status_code == 200:
            domains = domains_response.json().get("domains", [])
            
            if domains:
                # Test with first available domain
                test_domain = domains[0]
                response = requests.get(f"{BASE_URL}/knowledge-graph/export?domain={test_domain}")
                
                if response.status_code == 200:
                    result = response.json()
                    nodes = result.get("nodes", [])
                    edges = result.get("edges", [])
                    domain = result.get("domain", "")
                    filtered = result.get("filtered", False)
                    
                    print(f"   ✅ Exported graph for domain '{domain}':")
                    print(f"   📊 Nodes exported: {len(nodes)}")
                    print(f"   📊 Edges exported: {len(edges)}")
                    print(f"   📊 Filtered: {filtered}")
                    
                    # Show sample nodes
                    if nodes:
                        sample_nodes = [node.get("label", "") for node in nodes[:3]]
                        print(f"   📋 Sample nodes: {sample_nodes}")
                    
                else:
                    print(f"   ❌ Failed - HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("   ⚠️  No domains available for testing")
        else:
            print(f"   ❌ Failed to get domains - HTTP {domains_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 5: Compare filtered vs unfiltered stats
    print("🔍 Test 5: Compare Filtered vs Unfiltered Stats")
    try:
        # Get unfiltered stats
        unfiltered_response = requests.get(f"{BASE_URL}/knowledge-graph/stats")
        filtered_response = None
        
        if unfiltered_response.status_code == 200:
            unfiltered_stats = unfiltered_response.json()
            unfiltered_nodes = unfiltered_stats.get("nodes", 0)
            unfiltered_edges = unfiltered_stats.get("edges", 0)
            
            print(f"   📊 Unfiltered stats: {unfiltered_nodes} nodes, {unfiltered_edges} edges")
            
            # Get available domains for comparison
            domains_response = requests.get(f"{BASE_URL}/knowledge-graph/domains")
            if domains_response.status_code == 200:
                domains = domains_response.json().get("domains", [])
                
                if domains:
                    # Compare with first domain
                    test_domain = domains[0]
                    filtered_response = requests.get(f"{BASE_URL}/knowledge-graph/stats?domain={test_domain}")
                    
                    if filtered_response.status_code == 200:
                        filtered_stats = filtered_response.json()
                        filtered_nodes = filtered_stats.get("nodes", 0)
                        filtered_edges = filtered_stats.get("edges", 0)
                        
                        print(f"   📊 Filtered stats ({test_domain}): {filtered_nodes} nodes, {filtered_edges} edges")
                        
                        # Calculate reduction
                        if unfiltered_nodes > 0:
                            node_reduction = ((unfiltered_nodes - filtered_nodes) / unfiltered_nodes) * 100
                            print(f"   📊 Node reduction: {node_reduction:.1f}%")
                        
                        if unfiltered_edges > 0:
                            edge_reduction = ((unfiltered_edges - filtered_edges) / unfiltered_edges) * 100
                            print(f"   📊 Edge reduction: {edge_reduction:.1f}%")
                    else:
                        print(f"   ❌ Failed to get filtered stats - HTTP {filtered_response.status_code}")
                else:
                    print("   ⚠️  No domains available for comparison")
            else:
                print(f"   ❌ Failed to get domains - HTTP {domains_response.status_code}")
        else:
            print(f"   ❌ Failed to get unfiltered stats - HTTP {unfiltered_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 6: System health check
    print("🔍 Test 6: System Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            
            print(f"   ✅ System health: {status}")
            
            # Check component status
            components = result.get("components", {})
            for component, status in components.items():
                print(f"   📊 {component}: {status}")
            
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    print("=" * 80)
    print("✅ Domain Filters Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_domain_filters() 