import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

async def extract_structured_data_using_css_extractor():
    
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
                # "selector": "a .SearchResultCard__MemberProfileAnchor-sc-doe1cb-0",
                "selector": "> a",
                "type": "attribute",
                "attribute": "href"
            },
        ],
    }

    # Set up browser config--controls browser behavior.
    browser_config = BrowserConfig(
        headless=False,             # show UI
        java_script_enabled=True   # enable js to execute on the page (js-rendering, etc.)
    )

    ### test js function vars

    js_hit_search = """
    (() => {
        const search_btn = document.querySelector('button[data-testid="search-box-submit"]');
        search_btn.click();
    })();
    """
    
    js_close_modal = """
    (() => {
        const modal_btn = document.querySelector('button[aria-label="Dismiss modal"]');
        if (modal_btn) {
            modal_btn.click();
            console.log("MODAL close button clicked successfully");
        } else {
            console.warn("MODAL close button not found");
        }
    })();
    """
    ### test js function vars end

    # 1) js function that enters user input () into the search box
    js_enter_search = """
    
    """

    # 2) js function that inputs # of dogs/puppies/cats, -> hit 'Next' btn, ->
    # hit 'Search Now' btn; all in the modal pop-up that occurs on browser.
    js_modal = """
    """
    # Now we can collect the urls of each sitter on this page (first page for now).


    # Set up crawler config--controls how each crawl runs.
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(results_card_schema),
        js_code=[js_hit_search],
        capture_console_messages=True,
        log_console=True,
        capture_network_requests=True,
        wait_until="networkidle"
    )

    # AsyncWebCrawler, an asynchronous web crawler.
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.rover.com/", config=crawler_config
        )

        sitters = json.loads(result.extracted_content)
        print("✅ Crawl finished, checking extracted content")
        print("Raw extracted content:", result.extracted_content[:500], "...")  # first 500 chars
        print(f"Successfully extracted {len(sitters)} sitters of first search results page.")

async def main():
    await extract_structured_data_using_css_extractor()

if __name__ == "__main__":
    asyncio.run(main())
