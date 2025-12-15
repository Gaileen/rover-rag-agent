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
        verbose=True
    )

    ### test js function vars: to move this into a separate js script for code cleanup

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
    # Set the address value into the address input box.
    # Create a new KeyboardEvent for the 'Enter' key.
    # Dispatch the event on the target element.
    js_input_search = """
    (() => {
        const addr_box = document.querySelector('input[data-testid="location-input"]');
        const addr_in = 'Milford, CT, USA';
        addr_box.focus();
        
        const setter = Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            'value'
        ).set;
        setter.call(addr_box, addr_in);

        addr_box.dispatchEvent(new Event('input', { bubbles: true }));
        
        addr_box.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            bubbles: true
        }));
        addr_box.dispatchEvent(new KeyboardEvent('keyup', {
            key: 'Enter',
            code: 'Enter',
            bubbles: true
        }));

        addr_box.blur();
    })();
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
        js_code=[js_input_search,
                 js_hit_search], # JS injection happens before Crawl4AI waits for network idle, but after page started loading
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
        ## OK SO NEXT STEPS NOW ARE TO FIGURE OUT JS TO SELECT FILTERS (start w/ location, then check boxes).
        ## then if time, figure out how to use user input to select filters.
        ###################        

async def main():
    await extract_structured_data_using_css_extractor()

if __name__ == "__main__":
    asyncio.run(main())
