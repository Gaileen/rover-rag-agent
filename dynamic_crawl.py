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
        verbose=True,
        enable_stealth=True
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

    js_input_address = f"""
    {js_input_text_filter}
    (() => {{
        const addr_box = document.querySelector('input[data-testid="location-input"]');
        const addr_in = 'Milford, CT, USA';
        js_input_text_filter(addr_box, addr_in);
    }})();
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

    # for booking type, we'll need user to select from options we define in chat
    js_input_booking_type = """
    (() => {
        const booking_type = 'House Sitting';
        const checkbox = document.querySelector(`input[aria-label="${booking_type}"]`);
        checkbox.click();
    })();
    """

    js_input_dog_size = """
    (() => {
        const size = '';
        const checkbox = document.querySelector(`input[aria-label="${size}"]`);
        checkbox.click();
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
        js_code=[js_input_booking_type,
                 js_input_address,
                 js_input_dates,
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
        ## OK SO NEXT STEPS NOW ARE TO FIGURE OUT JS to use user input as address.
        ## and JS TO SELECT more FILTERS (now dates, then check boxes).
        ###################        

async def main():
    await extract_structured_data_using_css_extractor()

if __name__ == "__main__":
    asyncio.run(main())
