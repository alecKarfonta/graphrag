#!/usr/bin/env python3
"""
Test script for Reddit Crawler Service
Tests all endpoints and functionality of the Reddit crawler.
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
REDDIT_CRAWLER_URL = "http://localhost:8003"
GRAPHRAG_API_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{REDDIT_CRAWLER_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_start_crawl():
    """Test starting a Reddit crawl."""
    print("\n🔍 Testing crawl start...")
    
    crawl_request = {
        "query": "artificial intelligence",
        "subreddits": ["MachineLearning", "artificial"],
        "sort_by": "relevance",
        "time_filter": "month",
        "max_posts": 5,
        "max_comments_per_post": 3,
        "comment_depth": 2,
        "include_replies": True,
        "auto_ingest": True,
        "filter_nsfw": True
    }
    
    try:
        response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crawl started successfully: {data}")
            return data.get("crawl_id")
        else:
            print(f"❌ Crawl start failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Crawl start error: {e}")
        return None

def test_crawl_status(crawl_id: str):
    """Test getting crawl status."""
    print(f"\n🔍 Testing crawl status for {crawl_id}...")
    
    try:
        response = requests.get(f"{REDDIT_CRAWLER_URL}/crawl/{crawl_id}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crawl status: {data}")
            return data
        else:
            print(f"❌ Crawl status failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Crawl status error: {e}")
        return None

def test_list_crawls():
    """Test listing all crawls."""
    print("\n🔍 Testing crawl listing...")
    
    try:
        response = requests.get(f"{REDDIT_CRAWLER_URL}/crawls")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crawl listing: {data}")
            return data
        else:
            print(f"❌ Crawl listing failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Crawl listing error: {e}")
        return None

def test_crawl_results(crawl_id: str):
    """Test getting crawl results."""
    print(f"\n🔍 Testing crawl results for {crawl_id}...")
    
    try:
        response = requests.get(f"{REDDIT_CRAWLER_URL}/crawl/{crawl_id}/results")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crawl results: {data}")
            return data
        else:
            print(f"❌ Crawl results failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Crawl results error: {e}")
        return None

def test_browser_based_crawl():
    """Test browser-based crawling (fallback when API is not available)."""
    print("\n🔍 Testing browser-based crawl...")
    
    crawl_request = {
        "query": "python programming",
        "subreddits": ["Python"],
        "sort_by": "hot",
        "time_filter": "week",
        "max_posts": 3,
        "max_comments_per_post": 2,
        "comment_depth": 1,
        "include_replies": False,
        "auto_ingest": False,  # Don't auto-ingest for testing
        "filter_nsfw": True
    }
    
    try:
        response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Browser-based crawl started: {data}")
            return data.get("crawl_id")
        else:
            print(f"❌ Browser-based crawl failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Browser-based crawl error: {e}")
        return None

def test_search_across_all_subreddits():
    """Test searching across all subreddits."""
    print("\n🔍 Testing search across all subreddits...")
    
    crawl_request = {
        "query": "machine learning",
        "sort_by": "relevance",
        "time_filter": "month",
        "max_posts": 3,
        "max_comments_per_post": 2,
        "comment_depth": 1,
        "include_replies": True,
        "auto_ingest": False,
        "filter_nsfw": True
    }
    
    try:
        response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cross-subreddit search started: {data}")
            return data.get("crawl_id")
        else:
            print(f"❌ Cross-subreddit search failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Cross-subreddit search error: {e}")
        return None

def test_different_sort_methods():
    """Test different sort methods."""
    print("\n🔍 Testing different sort methods...")
    
    sort_methods = ["hot", "top", "new", "relevance"]
    crawl_ids = []
    
    for sort_method in sort_methods:
        print(f"Testing sort method: {sort_method}")
        crawl_request = {
            "query": "programming",
            "subreddits": ["programming"],
            "sort_by": sort_method,
            "time_filter": "week",
            "max_posts": 2,
            "max_comments_per_post": 1,
            "comment_depth": 1,
            "include_replies": False,
            "auto_ingest": False,
            "filter_nsfw": True
        }
        
        try:
            response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
            if response.status_code == 200:
                data = response.json()
                crawl_id = data.get("crawl_id")
                crawl_ids.append(crawl_id)
                print(f"✅ {sort_method} crawl started: {crawl_id}")
            else:
                print(f"❌ {sort_method} crawl failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {sort_method} crawl error: {e}")
    
    return crawl_ids

def test_time_filters():
    """Test different time filters."""
    print("\n🔍 Testing different time filters...")
    
    time_filters = ["hour", "day", "week", "month", "year"]
    crawl_ids = []
    
    for time_filter in time_filters:
        print(f"Testing time filter: {time_filter}")
        crawl_request = {
            "query": "technology",
            "subreddits": ["technology"],
            "sort_by": "top",
            "time_filter": time_filter,
            "max_posts": 2,
            "max_comments_per_post": 1,
            "comment_depth": 1,
            "include_replies": False,
            "auto_ingest": False,
            "filter_nsfw": True
        }
        
        try:
            response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
            if response.status_code == 200:
                data = response.json()
                crawl_id = data.get("crawl_id")
                crawl_ids.append(crawl_id)
                print(f"✅ {time_filter} crawl started: {crawl_id}")
            else:
                print(f"❌ {time_filter} crawl failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {time_filter} crawl error: {e}")
    
    return crawl_ids

def test_comment_depth_limits():
    """Test different comment depth limits."""
    print("\n🔍 Testing comment depth limits...")
    
    depths = [1, 2, 3]
    crawl_ids = []
    
    for depth in depths:
        print(f"Testing comment depth: {depth}")
        crawl_request = {
            "query": "discussion",
            "subreddits": ["AskReddit"],
            "sort_by": "hot",
            "time_filter": "day",
            "max_posts": 2,
            "max_comments_per_post": 3,
            "comment_depth": depth,
            "include_replies": True,
            "auto_ingest": False,
            "filter_nsfw": True
        }
        
        try:
            response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
            if response.status_code == 200:
                data = response.json()
                crawl_id = data.get("crawl_id")
                crawl_ids.append(crawl_id)
                print(f"✅ Depth {depth} crawl started: {crawl_id}")
            else:
                print(f"❌ Depth {depth} crawl failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Depth {depth} crawl error: {e}")
    
    return crawl_ids

def wait_for_crawl_completion(crawl_id: str, timeout: int = 300):
    """Wait for a crawl to complete."""
    print(f"\n⏳ Waiting for crawl {crawl_id} to complete...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = test_crawl_status(crawl_id)
        if status and status.get("status") in ["completed", "failed"]:
            print(f"✅ Crawl {crawl_id} completed with status: {status.get('status')}")
            return status
        time.sleep(10)
    
    print(f"⏰ Timeout waiting for crawl {crawl_id}")
    return None

def test_graphrag_integration():
    """Test integration with GraphRAG system."""
    print("\n🔍 Testing GraphRAG integration...")
    
    # Test if GraphRAG API is available
    try:
        response = requests.get(f"{GRAPHRAG_API_URL}/health")
        if response.status_code == 200:
            print("✅ GraphRAG API is available")
        else:
            print("❌ GraphRAG API is not available")
            return False
    except Exception as e:
        print(f"❌ GraphRAG API error: {e}")
        return False
    
    # Test a crawl with auto-ingestion
    crawl_request = {
        "query": "artificial intelligence",
        "subreddits": ["MachineLearning"],
        "sort_by": "relevance",
        "time_filter": "week",
        "max_posts": 2,
        "max_comments_per_post": 2,
        "comment_depth": 1,
        "include_replies": True,
        "auto_ingest": True,
        "filter_nsfw": True
    }
    
    try:
        response = requests.post(f"{REDDIT_CRAWLER_URL}/crawl", json=crawl_request)
        if response.status_code == 200:
            data = response.json()
            crawl_id = data.get("crawl_id")
            print(f"✅ Integration crawl started: {crawl_id}")
            
            # Wait for completion
            final_status = wait_for_crawl_completion(crawl_id, timeout=180)
            if final_status and final_status.get("status") == "completed":
                print("✅ GraphRAG integration test completed successfully")
                return True
            else:
                print("❌ GraphRAG integration test failed")
                return False
        else:
            print(f"❌ Integration crawl failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Integration crawl error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Reddit Crawler Service Tests")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test basic crawl functionality
    crawl_id = test_start_crawl()
    if crawl_id:
        # Wait for completion and get results
        final_status = wait_for_crawl_completion(crawl_id)
        if final_status:
            test_crawl_results(crawl_id)
    
    # Test browser-based crawling
    browser_crawl_id = test_browser_based_crawl()
    if browser_crawl_id:
        wait_for_crawl_completion(browser_crawl_id)
    
    # Test cross-subreddit search
    search_crawl_id = test_search_across_all_subreddits()
    if search_crawl_id:
        wait_for_crawl_completion(search_crawl_id)
    
    # Test different sort methods
    sort_crawl_ids = test_different_sort_methods()
    for crawl_id in sort_crawl_ids:
        if crawl_id:
            wait_for_crawl_completion(crawl_id)
    
    # Test different time filters
    time_crawl_ids = test_different_sort_methods()
    for crawl_id in time_crawl_ids:
        if crawl_id:
            wait_for_crawl_completion(crawl_id)
    
    # Test comment depth limits
    depth_crawl_ids = test_comment_depth_limits()
    for crawl_id in depth_crawl_ids:
        if crawl_id:
            wait_for_crawl_completion(crawl_id)
    
    # Test GraphRAG integration
    test_graphrag_integration()
    
    # List all crawls
    test_list_crawls()
    
    print("\n" + "=" * 50)
    print("✅ Reddit Crawler Service Tests Completed")

if __name__ == "__main__":
    main() 