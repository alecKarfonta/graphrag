#!/usr/bin/env python3
"""
Reddit Crawler Service for GraphRAG
Provides Reddit crawling capabilities with configurable depth and integration with the main system.
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from reddit_models import RedditPost, RedditComment, CrawlConfig
from reddit_crawler import RedditCrawler
from reddit_integration import RedditIntegrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reddit Crawler Service",
    description="Reddit crawling service for GraphRAG system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
reddit_crawler = RedditCrawler()
reddit_integrator = RedditIntegrator()

class CrawlRequest(BaseModel):
    """Request model for Reddit crawling."""
    query: str = Field(..., description="Search query or topic")
    subreddits: Optional[List[str]] = Field(default=None, description="Specific subreddits to search")
    sort_by: str = Field(default="relevance", description="Sort by: relevance, hot, top, new, comments")
    time_filter: str = Field(default="month", description="Time filter: hour, day, week, month, year, all")
    max_posts: int = Field(default=50, description="Maximum number of posts to crawl")
    max_comments_per_post: int = Field(default=20, description="Maximum comments per post")
    comment_depth: int = Field(default=2, description="Depth of comment recursion (1-3)")
    include_replies: bool = Field(default=True, description="Include comment replies")
    auto_ingest: bool = Field(default=True, description="Automatically ingest into GraphRAG")
    filter_nsfw: bool = Field(default=True, description="Filter out NSFW content")

class CrawlResponse(BaseModel):
    """Response model for Reddit crawling."""
    crawl_id: str
    status: str
    posts_found: int
    comments_found: int
    total_content_length: int
    estimated_processing_time: str
    ingestion_status: Optional[str] = None

class CrawlStatus(BaseModel):
    """Status model for crawl progress."""
    crawl_id: str
    status: str
    progress: float
    posts_processed: int
    comments_processed: int
    current_post: Optional[str] = None
    error: Optional[str] = None

# Store active crawls
active_crawls: Dict[str, Dict] = {}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Reddit Crawler Service is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_crawls": len(active_crawls),
        "services": {
            "reddit_crawler": "available",
            "reddit_integrator": "available"
        }
    }

@app.post("/crawl", response_model=CrawlResponse)
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Start a Reddit crawl with the specified parameters."""
    try:
        # Generate crawl ID
        crawl_id = f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.query) % 10000}"
        
        # Create crawl configuration
        config = CrawlConfig(
            query=request.query,
            subreddits=request.subreddits,
            sort_by=request.sort_by,
            time_filter=request.time_filter,
            max_posts=request.max_posts,
            max_comments_per_post=request.max_comments_per_post,
            comment_depth=request.comment_depth,
            include_replies=request.include_replies,
            filter_nsfw=request.filter_nsfw
        )
        
        # Initialize crawl status
        active_crawls[crawl_id] = {
            "status": "starting",
            "progress": 0.0,
            "posts_processed": 0,
            "comments_processed": 0,
            "config": config,
            "auto_ingest": request.auto_ingest,
            "start_time": datetime.now()
        }
        
        # Start background crawl task
        background_tasks.add_task(
            execute_crawl,
            crawl_id,
            config,
            request.auto_ingest
        )
        
        # Estimate processing time
        estimated_time = estimate_processing_time(config)
        
        return CrawlResponse(
            crawl_id=crawl_id,
            status="started",
            posts_found=0,  # Will be updated during crawl
            comments_found=0,  # Will be updated during crawl
            total_content_length=0,  # Will be updated during crawl
            estimated_processing_time=estimated_time,
            ingestion_status="pending" if request.auto_ingest else None
        )
        
    except Exception as e:
        logger.error(f"Error starting crawl: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start crawl: {str(e)}")

@app.get("/crawl/{crawl_id}/status", response_model=CrawlStatus)
async def get_crawl_status(crawl_id: str):
    """Get the status of a specific crawl."""
    if crawl_id not in active_crawls:
        raise HTTPException(status_code=404, detail="Crawl not found")
    
    crawl_info = active_crawls[crawl_id]
    
    return CrawlStatus(
        crawl_id=crawl_id,
        status=crawl_info["status"],
        progress=crawl_info["progress"],
        posts_processed=crawl_info["posts_processed"],
        comments_processed=crawl_info["comments_processed"],
        current_post=crawl_info.get("current_post"),
        error=crawl_info.get("error")
    )

@app.get("/crawl/{crawl_id}/results")
async def get_crawl_results(crawl_id: str):
    """Get the results of a completed crawl."""
    if crawl_id not in active_crawls:
        raise HTTPException(status_code=404, detail="Crawl not found")
    
    crawl_info = active_crawls[crawl_id]
    
    if crawl_info["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Crawl not completed yet")
    
    return {
        "crawl_id": crawl_id,
        "status": crawl_info["status"],
        "results": crawl_info.get("results", []),
        "statistics": crawl_info.get("statistics", {}),
        "ingestion_status": crawl_info.get("ingestion_status")
    }

@app.delete("/crawl/{crawl_id}")
async def cancel_crawl(crawl_id: str):
    """Cancel an active crawl."""
    if crawl_id not in active_crawls:
        raise HTTPException(status_code=404, detail="Crawl not found")
    
    crawl_info = active_crawls[crawl_id]
    if crawl_info["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed crawl")
    
    crawl_info["status"] = "cancelled"
    crawl_info["error"] = "Cancelled by user"
    
    return {"message": "Crawl cancelled successfully"}

@app.get("/crawls")
async def list_crawls():
    """List all crawls (active and completed)."""
    return {
        "crawls": [
            {
                "crawl_id": crawl_id,
                "status": info["status"],
                "query": info["config"].query,
                "start_time": info["start_time"].isoformat(),
                "progress": info["progress"]
            }
            for crawl_id, info in active_crawls.items()
        ]
    }

async def execute_crawl(crawl_id: str, config: CrawlConfig, auto_ingest: bool):
    """Execute the Reddit crawl in the background."""
    try:
        crawl_info = active_crawls[crawl_id]
        crawl_info["status"] = "crawling"
        
        # Execute the crawl
        results = await reddit_crawler.crawl_reddit(config, progress_callback=lambda p, c: update_progress(crawl_id, p, c))
        
        # Update crawl info with results
        crawl_info["results"] = results
        crawl_info["status"] = "completed"
        crawl_info["progress"] = 100.0
        
        # Auto-ingest if requested
        if auto_ingest and results:
            try:
                crawl_info["status"] = "ingesting"
                ingestion_result = await reddit_integrator.ingest_reddit_content(results)
                crawl_info["ingestion_status"] = "completed"
                crawl_info["ingestion_result"] = ingestion_result
            except Exception as e:
                logger.error(f"Error during ingestion: {e}")
                crawl_info["ingestion_status"] = "failed"
                crawl_info["ingestion_error"] = str(e)
        
        crawl_info["status"] = "completed"
        
    except Exception as e:
        logger.error(f"Error during crawl {crawl_id}: {e}")
        crawl_info = active_crawls[crawl_id]
        crawl_info["status"] = "failed"
        crawl_info["error"] = str(e)

def update_progress(crawl_id: str, posts_processed: int, comments_processed: int):
    """Update crawl progress."""
    if crawl_id in active_crawls:
        crawl_info = active_crawls[crawl_id]
        config = crawl_info["config"]
        
        # Calculate progress based on posts processed
        progress = min(100.0, (posts_processed / config.max_posts) * 100)
        
        crawl_info["progress"] = progress
        crawl_info["posts_processed"] = posts_processed
        crawl_info["comments_processed"] = comments_processed

def estimate_processing_time(config: CrawlConfig) -> str:
    """Estimate processing time based on configuration."""
    base_time_per_post = 30  # seconds
    time_per_comment = 5  # seconds
    
    estimated_seconds = (
        config.max_posts * base_time_per_post +
        config.max_posts * config.max_comments_per_post * time_per_comment
    )
    
    if estimated_seconds < 60:
        return f"{estimated_seconds} seconds"
    elif estimated_seconds < 3600:
        minutes = estimated_seconds // 60
        return f"{minutes} minutes"
    else:
        hours = estimated_seconds // 3600
        minutes = (estimated_seconds % 3600) // 60
        return f"{hours}h {minutes}m"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003) 