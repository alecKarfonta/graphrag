#!/usr/bin/env python3
"""
Simple HTTP-based Reddit Scraper
Uses requests and BeautifulSoup to scrape Reddit without browser automation.
"""

import requests
import json
import time
import logging
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from reddit_models import RedditPost, RedditComment, CrawlConfig

logger = logging.getLogger(__name__)

class RedditHTTPScraper:
    """Simple HTTP-based Reddit scraper."""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    async def scrape_subreddit(self, subreddit: str, config: CrawlConfig) -> List[RedditPost]:
        """Scrape a subreddit using HTTP requests."""
        posts = []
        
        try:
            # Use Reddit's JSON API
            if config.query:
                # Search within subreddit
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': config.query,
                    'restrict_sr': 'true',
                    'sort': config.sort_by,
                    't': config.time_filter,
                    'limit': config.max_posts
                }
            else:
                # Get posts from subreddit
                sort_mapping = {
                    'hot': 'hot',
                    'new': 'new',
                    'top': 'top',
                    'relevance': 'hot'  # Default to hot for relevance
                }
                sort_type = sort_mapping.get(config.sort_by, 'hot')
                url = f"https://www.reddit.com/r/{subreddit}/{sort_type}.json"
                params = {
                    'limit': config.max_posts,
                    't': config.time_filter if sort_type == 'top' else None
                }
                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}
            
            logger.info(f"Scraping Reddit URL: {url} with params: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                for item in data['data']['children']:
                    if item.get('kind') == 't3':  # Post
                        post_data = item['data']
                        
                        # Skip NSFW content if filtering is enabled
                        if config.filter_nsfw and post_data.get('over_18', False):
                            continue
                        
                        post = RedditPost(
                            id=post_data.get('id', ''),
                            title=post_data.get('title', ''),
                            content=post_data.get('selftext', ''),
                            author=post_data.get('author', '[deleted]'),
                            subreddit=post_data.get('subreddit', subreddit),
                            url=post_data.get('url', ''),
                            score=post_data.get('score', 0),
                            upvote_ratio=post_data.get('upvote_ratio', 0.0),
                            num_comments=post_data.get('num_comments', 0),
                            created_utc=post_data.get('created_utc', 0),
                            is_nsfw=post_data.get('over_18', False),
                            domain=post_data.get('domain', ''),
                            permalink=post_data.get('permalink', '')
                        )
                        
                        posts.append(post)
                        
                        if len(posts) >= config.max_posts:
                            break
            
            logger.info(f"Found {len(posts)} posts from r/{subreddit}")
            
        except Exception as e:
            logger.error(f"Error scraping subreddit {subreddit}: {e}")
        
        return posts
    
    async def scrape_reddit_search(self, config: CrawlConfig) -> List[RedditPost]:
        """Search across all of Reddit using HTTP requests."""
        posts = []
        
        try:
            # Use Reddit's search API
            url = "https://www.reddit.com/search.json"
            params = {
                'q': config.query,
                'sort': config.sort_by,
                't': config.time_filter,
                'limit': config.max_posts
            }
            
            logger.info(f"Searching Reddit: {url} with params: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                for item in data['data']['children']:
                    if item.get('kind') == 't3':  # Post
                        post_data = item['data']
                        
                        # Skip NSFW content if filtering is enabled
                        if config.filter_nsfw and post_data.get('over_18', False):
                            continue
                        
                        post = RedditPost(
                            id=post_data.get('id', ''),
                            title=post_data.get('title', ''),
                            content=post_data.get('selftext', ''),
                            author=post_data.get('author', '[deleted]'),
                            subreddit=post_data.get('subreddit', ''),
                            url=post_data.get('url', ''),
                            score=post_data.get('score', 0),
                            upvote_ratio=post_data.get('upvote_ratio', 0.0),
                            num_comments=post_data.get('num_comments', 0),
                            created_utc=post_data.get('created_utc', 0),
                            is_nsfw=post_data.get('over_18', False),
                            domain=post_data.get('domain', ''),
                            permalink=post_data.get('permalink', '')
                        )
                        
                        posts.append(post)
                        
                        if len(posts) >= config.max_posts:
                            break
            
            logger.info(f"Found {len(posts)} posts from Reddit search")
            
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
        
        return posts
    
    async def get_post_comments(self, post: RedditPost, max_comments: int, depth: int) -> List[RedditComment]:
        """Get comments for a post using HTTP requests."""
        comments = []
        
        try:
            # Use Reddit's JSON API for comments
            url = f"https://www.reddit.com{post.permalink}.json"
            
            logger.info(f"Getting comments from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) >= 2 and 'data' in data[1] and 'children' in data[1]['data']:
                comments_data = data[1]['data']['children']
                comments = self.extract_comments_recursive(comments_data, max_comments, depth, 0)
            
            logger.info(f"Found {len(comments)} comments for post {post.id}")
            
        except Exception as e:
            logger.error(f"Error getting comments for post {post.id}: {e}")
        
        return comments
    
    def extract_comments_recursive(self, comments_data: List[Dict], max_comments: int, 
                                 max_depth: int, current_depth: int) -> List[RedditComment]:
        """Extract comments recursively with depth control."""
        comments = []
        
        if current_depth >= max_depth:
            return comments
        
        for item in comments_data[:max_comments]:
            if item.get('kind') == 't1':  # Comment
                comment_data = item['data']
                
                # Skip deleted comments
                if comment_data.get('body') in ['[deleted]', '[removed]']:
                    continue
                
                comment = RedditComment(
                    id=comment_data.get('id', ''),
                    body=comment_data.get('body', ''),
                    author=comment_data.get('author', '[deleted]'),
                    score=comment_data.get('score', 0),
                    created_utc=comment_data.get('created_utc', 0),
                    parent_id=comment_data.get('parent_id', ''),
                    depth=current_depth
                )
                
                comments.append(comment)
                
                # Get replies if available and within depth limit
                if ('replies' in comment_data and 
                    comment_data['replies'] and 
                    current_depth < max_depth - 1):
                    
                    if isinstance(comment_data['replies'], dict):
                        replies_data = comment_data['replies'].get('data', {}).get('children', [])
                        comment.replies = self.extract_comments_recursive(
                            replies_data, max_comments, max_depth, current_depth + 1
                        )
                
                if len(comments) >= max_comments:
                    break
        
        return comments
    
    def add_delay(self, delay: float):
        """Add delay between requests to be respectful."""
        time.sleep(delay) 