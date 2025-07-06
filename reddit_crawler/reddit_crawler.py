#!/usr/bin/env python3
"""
Reddit Crawler Module
Provides Reddit crawling capabilities with both API and browser-based approaches.
"""

import os
import asyncio
import logging
import time
import re
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import json

import requests
import praw
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from reddit_models import RedditPost, RedditComment, CrawlConfig
from reddit_http_scraper import RedditHTTPScraper

logger = logging.getLogger(__name__)

class RedditCrawler:
    """Reddit crawler with both API and browser-based approaches."""
    
    def __init__(self):
        self.reddit_api = None
        self.browser = None
        self.http_scraper = RedditHTTPScraper()
        self.ua = UserAgent()
        self.setup_reddit_api()
        self.setup_browser()
    
    def setup_reddit_api(self):
        """Setup Reddit API client if credentials are available."""
        try:
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            user_agent = os.getenv("REDDIT_USER_AGENT", "GraphRAG-RedditCrawler/1.0")
            
            if client_id and client_secret:
                self.reddit_api = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                logger.info("Reddit API client initialized successfully")
            else:
                logger.warning("Reddit API credentials not found, will use browser-based crawling")
        except Exception as e:
            logger.error(f"Failed to setup Reddit API: {e}")
            self.reddit_api = None
    
    def setup_browser(self):
        """Setup browser for web scraping."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to handle driver installation
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Browser setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            self.browser = None
    
    async def crawl_reddit(self, config: CrawlConfig, progress_callback: Optional[Callable] = None) -> List[RedditPost]:
        """Main method to crawl Reddit based on configuration."""
        logger.info(f"Starting Reddit crawl for query: {config.query}")
        
        posts = []
        posts_processed = 0
        
        try:
            if config.subreddits:
                # Crawl specific subreddits
                for subreddit in config.subreddits:
                    subreddit_posts = await self.crawl_subreddit(
                        subreddit, config, progress_callback, posts_processed
                    )
                    posts.extend(subreddit_posts)
                    posts_processed += len(subreddit_posts)
                    
                    if len(posts) >= config.max_posts:
                        break
            else:
                # Search across all subreddits
                posts = await self.search_reddit(config, progress_callback)
            
            # Filter and limit results
            posts = self.filter_posts(posts, config)
            posts = posts[:config.max_posts]
            
            # Process comments for each post
            for i, post in enumerate(posts):
                if progress_callback:
                    progress_callback(i + 1, 0)
                
                post.comments = await self.get_post_comments(
                    post, config.max_comments_per_post, config.comment_depth, config.include_replies
                )
                
                # Add delay to be respectful
                await asyncio.sleep(config.delay_between_requests)
            
            logger.info(f"Crawl completed. Found {len(posts)} posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error during Reddit crawl: {e}")
            raise
    
    async def crawl_subreddit(self, subreddit: str, config: CrawlConfig, 
                            progress_callback: Optional[Callable], posts_processed: int) -> List[RedditPost]:
        """Crawl a specific subreddit."""
        logger.info(f"Crawling subreddit: r/{subreddit}")
        
        if self.reddit_api and config.use_api:
            return await self.crawl_subreddit_api(subreddit, config)
        else:
            return await self.crawl_subreddit_browser(subreddit, config)
    
    async def crawl_subreddit_api(self, subreddit: str, config: CrawlConfig) -> List[RedditPost]:
        """Crawl subreddit using Reddit API."""
        posts = []
        
        try:
            subreddit_obj = self.reddit_api.subreddit(subreddit)
            
            # Get posts based on sort method
            if config.sort_by == "hot":
                subreddit_posts = subreddit_obj.hot(limit=config.max_posts)
            elif config.sort_by == "top":
                subreddit_posts = subreddit_obj.top(time_filter=config.time_filter, limit=config.max_posts)
            elif config.sort_by == "new":
                subreddit_posts = subreddit_obj.new(limit=config.max_posts)
            else:  # relevance (search)
                subreddit_posts = subreddit_obj.search(config.query, sort=config.sort_by, 
                                                     time_filter=config.time_filter, limit=config.max_posts)
            
            for submission in subreddit_posts:
                try:
                    post = RedditPost(
                        id=submission.id,
                        title=submission.title,
                        content=submission.selftext,
                        author=str(submission.author) if submission.author else "[deleted]",
                        subreddit=submission.subreddit.display_name,
                        url=submission.url,
                        score=submission.score,
                        upvote_ratio=submission.upvote_ratio,
                        num_comments=submission.num_comments,
                        created_utc=submission.created_utc,
                        is_nsfw=submission.over_18,
                        domain=submission.domain,
                        permalink=submission.permalink
                    )
                    
                    if not config.filter_nsfw or not post.is_nsfw:
                        posts.append(post)
                        
                except Exception as e:
                    logger.warning(f"Error processing post {submission.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error crawling subreddit {subreddit} with API: {e}")
        
        return posts
    
    async def crawl_subreddit_browser(self, subreddit: str, config: CrawlConfig) -> List[RedditPost]:
        """Crawl subreddit using browser automation."""
        posts = []
        
        if not self.browser:
            logger.warning("Browser not available, using HTTP scraper as fallback")
            return await self.http_scraper.scrape_subreddit(subreddit, config)
        
        try:
            # Construct Reddit URL
            if config.query:
                url = f"https://www.reddit.com/r/{subreddit}/search/?q={config.query}&restrict_sr=1&sort={config.sort_by}&t={config.time_filter}"
            else:
                url = f"https://www.reddit.com/r/{subreddit}/{config.sort_by}/"
            
            self.browser.get(url)
            
            # Wait for content to load
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='post-container']"))
            )
            
            # Scroll to load more posts
            self.scroll_to_load_posts(config.max_posts)
            
            # Extract posts
            post_elements = self.browser.find_elements(By.CSS_SELECTOR, "[data-testid='post-container']")
            
            for element in post_elements[:config.max_posts]:
                try:
                    post = self.extract_post_from_element(element, subreddit)
                    if post and (not config.filter_nsfw or not post.is_nsfw):
                        posts.append(post)
                except Exception as e:
                    logger.warning(f"Error extracting post: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error crawling subreddit {subreddit} with browser: {e}")
            # Fallback to HTTP scraper
            logger.info("Falling back to HTTP scraper")
            return await self.http_scraper.scrape_subreddit(subreddit, config)
        
        return posts
    
    async def search_reddit(self, config: CrawlConfig, progress_callback: Optional[Callable]) -> List[RedditPost]:
        """Search across all of Reddit."""
        posts = []
        
        if self.reddit_api and config.use_api:
            try:
                # Search across all subreddits
                search_results = self.reddit_api.subreddit("all").search(
                    config.query, sort=config.sort_by, time_filter=config.time_filter, limit=config.max_posts
                )
                
                for submission in search_results:
                    try:
                        post = RedditPost(
                            id=submission.id,
                            title=submission.title,
                            content=submission.selftext,
                            author=str(submission.author) if submission.author else "[deleted]",
                            subreddit=submission.subreddit.display_name,
                            url=submission.url,
                            score=submission.score,
                            upvote_ratio=submission.upvote_ratio,
                            num_comments=submission.num_comments,
                            created_utc=submission.created_utc,
                            is_nsfw=submission.over_18,
                            domain=submission.domain,
                            permalink=submission.permalink
                        )
                        
                        if not config.filter_nsfw or not post.is_nsfw:
                            posts.append(post)
                            
                    except Exception as e:
                        logger.warning(f"Error processing search result: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error searching Reddit with API: {e}")
        
        # Fallback to HTTP scraper if API failed or not available
        if not posts:
            logger.info("Using HTTP scraper for Reddit search")
            posts = await self.http_scraper.scrape_reddit_search(config)
        
        return posts
    
    async def get_post_comments(self, post: RedditPost, max_comments: int, 
                               depth: int, include_replies: bool) -> List[RedditComment]:
        """Get comments for a specific post with depth control."""
        comments = []
        
        try:
            if self.reddit_api and post.permalink:
                # Use API to get comments
                submission = self.reddit_api.submission(url=f"https://reddit.com{post.permalink}")
                submission.comment_sort = "top"  # Sort by top comments
                submission.comments.replace_more(limit=0)  # Remove "load more comments" links
                
                comments = self.extract_comments_recursive(
                    submission.comments, max_comments, depth, include_replies
                )
            else:
                # Use HTTP scraper as fallback
                logger.info("Using HTTP scraper for comments")
                comments = await self.http_scraper.get_post_comments(post, max_comments, depth)
                
        except Exception as e:
            logger.error(f"Error getting comments for post {post.id}: {e}")
            # Fallback to HTTP scraper
            try:
                logger.info("Falling back to HTTP scraper for comments")
                comments = await self.http_scraper.get_post_comments(post, max_comments, depth)
            except Exception as e2:
                logger.error(f"HTTP scraper also failed: {e2}")
        
        return comments
    
    def extract_comments_recursive(self, comment_forest, max_comments: int, 
                                 depth: int, include_replies: bool, current_depth: int = 0) -> List[RedditComment]:
        """Extract comments recursively with depth control."""
        comments = []
        
        if current_depth >= depth:
            return comments
        
        for comment in comment_forest[:max_comments]:
            try:
                reddit_comment = RedditComment(
                    id=comment.id,
                    body=comment.body,
                    author=str(comment.author) if comment.author else "[deleted]",
                    score=comment.score,
                    created_utc=comment.created_utc,
                    parent_id=comment.parent_id,
                    depth=current_depth
                )
                
                comments.append(reddit_comment)
                
                # Recursively get replies if requested
                if include_replies and comment.replies and current_depth < depth:
                    reddit_comment.replies = self.extract_comments_recursive(
                        comment.replies, max_comments, depth, include_replies, current_depth + 1
                    )
                    
            except Exception as e:
                logger.warning(f"Error extracting comment: {e}")
                continue
        
        return comments
    
    def extract_post_from_element(self, element, subreddit: str) -> Optional[RedditPost]:
        """Extract post data from browser element."""
        try:
            # Extract post data from DOM element
            title_element = element.find_element(By.CSS_SELECTOR, "h3")
            title = title_element.text if title_element else ""
            
            # Try to get post content
            content = ""
            try:
                content_element = element.find_element(By.CSS_SELECTOR, "[data-testid='post-content']")
                content = content_element.text
            except NoSuchElementException:
                pass
            
            # Extract other metadata
            author = element.find_element(By.CSS_SELECTOR, "[data-testid='post-author']").text
            score = int(element.find_element(By.CSS_SELECTOR, "[data-testid='post-score']").text)
            
            return RedditPost(
                id=element.get_attribute("data-post-id"),
                title=title,
                content=content,
                author=author,
                subreddit=subreddit,
                url="",  # Will be constructed
                score=score,
                upvote_ratio=0.0,
                num_comments=0,
                created_utc=time.time(),
                is_nsfw=False,
                domain="reddit.com",
                permalink=""
            )
            
        except Exception as e:
            logger.warning(f"Error extracting post from element: {e}")
            return None
    
    def scroll_to_load_posts(self, max_posts: int):
        """Scroll to load more posts."""
        posts_loaded = 0
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        
        while posts_loaded < max_posts:
            # Scroll down
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(2)
            
            # Check if new content was loaded
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            
            last_height = new_height
            posts_loaded = len(self.browser.find_elements(By.CSS_SELECTOR, "[data-testid='post-container']"))
    
    def filter_posts(self, posts: List[RedditPost], config: CrawlConfig) -> List[RedditPost]:
        """Filter posts based on configuration."""
        filtered_posts = []
        
        for post in posts:
            # Filter NSFW content
            if config.filter_nsfw and post.is_nsfw:
                continue
            
            # Filter low-quality posts (very low scores)
            if post.score < -10:
                continue
            
            # Filter empty posts
            if not post.title.strip() and not post.content.strip():
                continue
            
            filtered_posts.append(post)
        
        return filtered_posts
    
    def cleanup(self):
        """Cleanup resources."""
        if self.browser:
            self.browser.quit()
            self.browser = None 