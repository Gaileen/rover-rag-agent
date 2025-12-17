import asyncio
import json
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy

js_init_search_filter = (Path(__file__).parent / "js-scripts/input_init_search_filters.js").read_text()
js_click_search = (Path(__file__).parent / "js-scripts/click_search.js").read_text()
# js_other_filter = (Path(__file__).parent / "js-scripts/input_other_filters.js").read_text()

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

    # 1) js function that enters user input () into the search box
    # Set the address value into the address input box.
    # Create a new KeyboardEvent for the 'Enter' key.
    # Dispatch the event on the target element.

    js_input_text_filter = """
    function js_input_text_filter(container, text_in) {
        container.focus();
        
        const setter = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            'value'
        ).set;
        setter.call(container, text_in);

        container.dispatchEvent(new Event('input', { bubbles: true }));
        
        container.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            bubbles: true
        }));
        container.dispatchEvent(new KeyboardEvent('keyup', {
            key: 'Enter',
            code: 'Enter',
            bubbles: true
        }));

        container.blur();
    }
    """

    # search results list names not always accurate for? 
    # const dropoff_in = '12/16/2025';
    # const pickup_in = '12/18/2025';
    js_input_dates = f"""
    {js_input_text_filter}
    (() => {{
        const dropoff_box = document.querySelector('input[placeholder="Drop off"]');
        const pickup_box = document.querySelector('input[placeholder="Pick up"]');
        const dropoff_in = '12/26/2025';
        const pickup_in = '12/28/2025';
        js_input_text_filter(dropoff_box, dropoff_in);
        js_input_text_filter(pickup_box, pickup_in);
    }})();
    """

    # search results list names not always accurate for? Giant dog
    js_input_dog_size = """
    (() => {
        const size = 'Giant (101+ to  lbs)';
        const checkbox = document.querySelector(`input[aria-label="${size}"]`);
        checkbox.click();
    })();
    """

    # Set up crawler config--controls how each crawl runs.
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(results_card_schema),
        js_code=[js_init_search_filter,
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
            print("Raw extracted content:", result.extracted_content) 
            print(f"Successfully extracted {len(sitters)} sitters of first search results page.")

        else:
            print(f"Crawl failed: {result.error_message}")

        ##################
        ## OK SO NEXT STEPS NOW ARE TO 
        ## Figure out why resulting sitter names from terminal not always == what I see in actual browser.
        ###################        

async def main():
    await extract_structured_data_using_css_extractor()

if __name__ == "__main__":
    asyncio.run(main())
