import os
import sys
import json
import asyncio
import requests
from xml.etree import ElementTree
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from openai import AsyncOpenAI
from supabase import create_client, Client

load_dotenv()

# Initialize OpenAI and Supabase clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# supabase: Client = create_client(
#     os.getenv("SUPABASE_URL"),
#     os.getenv("SUPABASE_SERVICE_KEY")
# )


# 1. Build an array of URLs of relevant sitters we need to crawl.
# 2. Crawl these URLs in parallel:
    # a. Process text into chunks (use additional LLM agents if needed).
    # b. Store into supabase.
# 3. [create the RAG agent]


# 1a.
async def crawl_recursive_batch(start_urls, max_depth=3, max_concurrent=10):
    

# 1.
def get_urls() -> List[str]:
    # TODO: set up required search variables to filter on (for testing)
    test_in_pet = "dog"
    test_in_petamt = "1"
    test_in_startdate = ""
    test_in_enddate = ""
    test_in_locatiom = "Milford, CT"
    test_in_other_optional = []


    """Get sitter URLs from Rover based on user input."""
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

# 2.
async def crawl_parallel(urls: List[str], max_concurrent: int = 5):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    

async def main():
    # Get relevant sitter URLs from Rover
    urls = get_urls()
    if not urls:
        print("No URLs found to crawl")
        return
    
    print(f"Found {len(urls)} URLs to crawl")
    await crawl_parallel(urls)

if __name__ == "__main__":
    asyncio.run(main())