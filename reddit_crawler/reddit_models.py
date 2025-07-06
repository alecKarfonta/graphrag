#!/usr/bin/env python3
"""
Reddit Data Models
Data classes for Reddit posts and comments.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RedditComment:
    """Data class for Reddit comment information."""
    id: str
    body: str
    author: str
    score: int
    created_utc: float
    parent_id: str
    depth: int
    replies: Optional[List['RedditComment']] = None

@dataclass
class RedditPost:
    """Data class for Reddit post information."""
    id: str
    title: str
    content: str
    author: str
    subreddit: str
    url: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: float
    is_nsfw: bool
    domain: str
    permalink: str
    comments: Optional[List[RedditComment]] = None

@dataclass
class CrawlConfig:
    """Configuration for Reddit crawling."""
    query: str
    subreddits: Optional[List[str]] = None
    sort_by: str = "relevance"  # relevance, hot, top, new, comments
    time_filter: str = "month"  # hour, day, week, month, year, all
    max_posts: int = 50
    max_comments_per_post: int = 20
    comment_depth: int = 2  # Depth of comment recursion (1-3)
    include_replies: bool = True
    filter_nsfw: bool = True
    use_api: bool = True  # Use Reddit API if available, fallback to browser
    delay_between_requests: float = 1.0  # Delay between requests to be respectful 