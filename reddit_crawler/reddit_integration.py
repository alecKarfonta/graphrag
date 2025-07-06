#!/usr/bin/env python3
"""
Reddit Integration Module
Processes Reddit content and integrates it into the main GraphRAG system.
"""

import os
import asyncio
import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests
from dataclasses import asdict

from reddit_models import RedditPost, RedditComment

logger = logging.getLogger(__name__)

class RedditIntegrator:
    """Integrates Reddit content into the GraphRAG system."""
    
    def __init__(self):
        self.graphrag_api_url = os.getenv("GRAPHRAG_API_URL", "http://localhost:8000")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "GraphRAG-RedditIntegrator/1.0"
        })
    
    async def ingest_reddit_content(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Ingest Reddit posts and comments into the GraphRAG system."""
        logger.info(f"Starting ingestion of {len(posts)} Reddit posts")
        
        ingestion_results = {
            "posts_processed": 0,
            "comments_processed": 0,
            "entities_extracted": 0,
            "relationships_extracted": 0,
            "errors": [],
            "successful_ingestions": []
        }
        
        for post in posts:
            try:
                # Process post content
                post_result = await self.process_reddit_post(post)
                ingestion_results["posts_processed"] += 1
                ingestion_results["entities_extracted"] += post_result.get("entities", 0)
                ingestion_results["relationships_extracted"] += post_result.get("relationships", 0)
                ingestion_results["successful_ingestions"].append({
                    "type": "post",
                    "id": post.id,
                    "title": post.title,
                    "subreddit": post.subreddit
                })
                
                # Process comments
                if post.comments:
                    for comment in post.comments:
                        try:
                            comment_result = await self.process_reddit_comment(comment, post)
                            ingestion_results["comments_processed"] += 1
                            ingestion_results["entities_extracted"] += comment_result.get("entities", 0)
                            ingestion_results["relationships_extracted"] += comment_result.get("relationships", 0)
                            ingestion_results["successful_ingestions"].append({
                                "type": "comment",
                                "id": comment.id,
                                "parent_post": post.id,
                                "subreddit": post.subreddit
                            })
                        except Exception as e:
                            logger.error(f"Error processing comment {comment.id}: {e}")
                            ingestion_results["errors"].append({
                                "type": "comment",
                                "id": comment.id,
                                "error": str(e)
                            })
                
            except Exception as e:
                logger.error(f"Error processing post {post.id}: {e}")
                ingestion_results["errors"].append({
                    "type": "post",
                    "id": post.id,
                    "error": str(e)
                })
        
        logger.info(f"Ingestion completed. Processed {ingestion_results['posts_processed']} posts and {ingestion_results['comments_processed']} comments")
        return ingestion_results
    
    async def process_reddit_post(self, post: RedditPost) -> Dict[str, Any]:
        """Process a single Reddit post and ingest it into GraphRAG."""
        # Prepare content for ingestion
        content = self.prepare_reddit_content(post)
        
        # Ingest into GraphRAG
        result = await self.ingest_content_to_graphrag(content, post.subreddit)
        
        return result
    
    async def process_reddit_comment(self, comment: RedditComment, parent_post: RedditPost) -> Dict[str, Any]:
        """Process a single Reddit comment and ingest it into GraphRAG."""
        # Prepare content for ingestion
        content = self.prepare_reddit_comment_content(comment, parent_post)
        
        # Ingest into GraphRAG
        result = await self.ingest_content_to_graphrag(content, parent_post.subreddit)
        
        return result
    
    def prepare_reddit_content(self, post: RedditPost) -> str:
        """Prepare Reddit post content for ingestion."""
        content_parts = []
        
        # Add title
        if post.title:
            content_parts.append(f"Title: {post.title}")
        
        # Add main content
        if post.content:
            content_parts.append(f"Content: {post.content}")
        
        # Add metadata
        metadata = [
            f"Author: {post.author}",
            f"Subreddit: r/{post.subreddit}",
            f"Score: {post.score}",
            f"Upvote Ratio: {post.upvote_ratio:.2f}",
            f"Number of Comments: {post.num_comments}",
            f"URL: {post.url}" if post.url else "",
            f"Permalink: https://reddit.com{post.permalink}"
        ]
        
        content_parts.append("Metadata: " + " | ".join(metadata))
        
        return "\n\n".join(content_parts)
    
    def prepare_reddit_comment_content(self, comment: RedditComment, parent_post: RedditPost) -> str:
        """Prepare Reddit comment content for ingestion."""
        content_parts = []
        
        # Add comment body
        if comment.body:
            content_parts.append(f"Comment: {comment.body}")
        
        # Add context about parent post
        content_parts.append(f"Parent Post: {parent_post.title}")
        content_parts.append(f"Subreddit: r/{parent_post.subreddit}")
        
        # Add comment metadata
        metadata = [
            f"Comment Author: {comment.author}",
            f"Comment Score: {comment.score}",
            f"Comment Depth: {comment.depth}",
            f"Parent Post Author: {parent_post.author}",
            f"Parent Post Score: {parent_post.score}"
        ]
        
        content_parts.append("Metadata: " + " | ".join(metadata))
        
        return "\n\n".join(content_parts)
    
    async def ingest_content_to_graphrag(self, content: str, domain: str) -> Dict[str, Any]:
        """Ingest content into the GraphRAG system."""
        try:
            # Create a temporary file for the content
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Upload to ingest-documents endpoint
                with open(temp_file_path, 'rb') as f:
                    files = {'files': ('reddit_content.txt', f, 'text/plain')}
                    data = {
                        'domain': domain,
                        'build_knowledge_graph': 'true'
                    }
                    
                    ingest_response = await self.make_async_request(
                        "POST",
                        f"{self.graphrag_api_url}/ingest-documents",
                        files=files,
                        data=data
                    )
                    
                    if ingest_response.status_code == 200:
                        result = ingest_response.json()
                        return {
                            "entities": 0,  # Will be populated by GraphRAG
                            "relationships": 0,  # Will be populated by GraphRAG
                            "status": "success",
                            "ingested": True
                        }
                    else:
                        logger.error(f"GraphRAG ingestion error: {ingest_response.status_code} - {ingest_response.text}")
                        return {
                            "entities": 0,
                            "relationships": 0,
                            "status": "error",
                            "ingested": False,
                            "error": f"Ingestion error: {ingest_response.status_code}"
                        }
                        
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error ingesting content to GraphRAG: {e}")
            return {
                "entities": 0,
                "relationships": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def make_async_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an async HTTP request."""
        loop = asyncio.get_event_loop()
        
        # Handle file uploads synchronously
        if 'files' in kwargs:
            return await loop.run_in_executor(
                None, 
                lambda: requests.request(method, url, **kwargs)
            )
        else:
            return await loop.run_in_executor(
                None, 
                lambda: self.session.request(method, url, **kwargs)
            )
    
    def create_reddit_summary(self, posts: List[RedditPost]) -> str:
        """Create a summary of Reddit content for analysis."""
        summary_parts = []
        
        # Group by subreddit
        subreddit_groups = {}
        for post in posts:
            if post.subreddit not in subreddit_groups:
                subreddit_groups[post.subreddit] = []
            subreddit_groups[post.subreddit].append(post)
        
        # Create summary for each subreddit
        for subreddit, subreddit_posts in subreddit_groups.items():
            summary_parts.append(f"Subreddit: r/{subreddit}")
            summary_parts.append(f"Number of Posts: {len(subreddit_posts)}")
            
            # Top posts by score
            top_posts = sorted(subreddit_posts, key=lambda p: p.score, reverse=True)[:5]
            summary_parts.append("Top Posts:")
            for post in top_posts:
                summary_parts.append(f"  - {post.title} (Score: {post.score})")
            
            # Total engagement
            total_score = sum(p.score for p in subreddit_posts)
            total_comments = sum(p.num_comments for p in subreddit_posts)
            summary_parts.append(f"Total Engagement: {total_score} upvotes, {total_comments} comments")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def analyze_reddit_trends(self, posts: List[RedditPost]) -> Dict[str, Any]:
        """Analyze trends in Reddit content."""
        analysis = {
            "total_posts": len(posts),
            "subreddits": {},
            "top_authors": {},
            "score_distribution": {
                "high": 0,  # > 100
                "medium": 0,  # 10-100
                "low": 0,  # < 10
                "negative": 0  # < 0
            },
            "content_types": {
                "text_posts": 0,
                "link_posts": 0,
                "image_posts": 0
            }
        }
        
        for post in posts:
            # Subreddit analysis
            if post.subreddit not in analysis["subreddits"]:
                analysis["subreddits"][post.subreddit] = {
                    "count": 0,
                    "total_score": 0,
                    "total_comments": 0
                }
            
            analysis["subreddits"][post.subreddit]["count"] += 1
            analysis["subreddits"][post.subreddit]["total_score"] += post.score
            analysis["subreddits"][post.subreddit]["total_comments"] += post.num_comments
            
            # Author analysis
            if post.author not in analysis["top_authors"]:
                analysis["top_authors"][post.author] = {
                    "posts": 0,
                    "total_score": 0
                }
            
            analysis["top_authors"][post.author]["posts"] += 1
            analysis["top_authors"][post.author]["total_score"] += post.score
            
            # Score distribution
            if post.score > 100:
                analysis["score_distribution"]["high"] += 1
            elif post.score >= 10:
                analysis["score_distribution"]["medium"] += 1
            elif post.score >= 0:
                analysis["score_distribution"]["low"] += 1
            else:
                analysis["score_distribution"]["negative"] += 1
            
            # Content type analysis
            if post.content:
                analysis["content_types"]["text_posts"] += 1
            elif post.url and any(ext in post.url.lower() for ext in ['.jpg', '.png', '.gif', '.jpeg']):
                analysis["content_types"]["image_posts"] += 1
            else:
                analysis["content_types"]["link_posts"] += 1
        
        # Sort top authors by total score
        analysis["top_authors"] = dict(
            sorted(analysis["top_authors"].items(), 
                   key=lambda x: x[1]["total_score"], reverse=True)[:10]
        )
        
        return analysis 