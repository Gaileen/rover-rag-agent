import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher
from crawl4ai import JsonCssExtractionStrategy

js_init_search_filter = (Path(__file__).parent / "js-scripts/input_init_search_filters.js").read_text()
js_click_search = (Path(__file__).parent / "js-scripts/click_search.js").read_text()
# js_other_filter = (Path(__file__).parent / "js-scripts/input_other_filters.js").read_text()

async def extract_urls():
    
    # define the CSS schema needed for crawler to get the sitter URLs to collect
    results_card_schema = {
        "name": "Rover Search Results",
        "baseSelector": "div[data-testid='search-result-card']",
        "fields": [
            {
                "name": "sitter_name",
                "selector": "span[itemprop='name']",
                "type": "text",
            },
            {
                "name": "sitter_url",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
        ],
    }

    # Set up browser config--controls browser behavior.
    browser_config = BrowserConfig(
        headless=False,             # show UI
        java_script_enabled=True,   # enable js to execute on the page (js-rendering, etc.)
        verbose=True,
        enable_stealth=True
    )

    # Set up crawler config--controls how each crawl runs.
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(results_card_schema),
        js_code=[
            #TODO Test crawl scraping w/ other filters applied (other than booking type + address)  
                js_init_search_filter,
                #  js_input_dates,
                js_click_search
                 ], # JS injection happens before Crawl4AI waits for network idle, but after page started loading
        capture_console_messages=True,
        log_console=True,
        capture_network_requests=True,
        exclude_all_images=True, # this may be couterintuitive w/ networkidle
        wait_until="networkidle" # ensure a webpage is fully loaded before crawler proceeds extracting (does not affect JS injection)
        # scan_full_page
    )

    # AsyncWebCrawler, an asynchronous web crawler.
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.rover.com/", config=crawler_config
        )

        if result.success:
            sitters = json.loads(result.extracted_content)
            print("✅ Crawl finished, checking extracted content")
            print(f"Successfully extracted {len(sitters)} sitters of first search results page.")
            return [sitter.get("sitter_url") for sitter in sitters if sitter.get("sitter_url")]

        else:
            print(f"Crawl failed: {result.error_message}")


async def batch_crawl(urls: List[str], max_concurrent: int = 10) -> List[Dict[str,Any]]:
    """
    Process multiple URLs with intelligent rate limiting and resource monitoring using arun_many().
    """
    browser_config = BrowserConfig(headless=True, verbose=False)
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(urls=urls, config=crawl_config, dispatcher=dispatcher)
        return [{'url': r.url, 'markdown': r.markdown} for r in results if r.success and r.markdown]


async def main():
    # Get URLs from first page of search results
    sitter_urls = await extract_urls()
    print("URLs:", sitter_urls) 

    # Get crawl results from URLs collected
    crawl_results = asyncio.run(batch_crawl(sitter_urls, max_concurrent=args.max_concurrent))

    # Chunk and collect metadata
    #TODO. need to understand batch_crawl first

if __name__ == "__main__":
    asyncio.run(main())
