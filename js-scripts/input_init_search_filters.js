// Inputs the search filters shown on Home page.
 
(() => {
    function input_text_filter(container, text_in) {
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
    
    function input_address() {
        const addr_box = document.querySelector('input[data-testid="location-input"]');
        const addr_in = 'Milford, CT, USA';
        input_text_filter(addr_box, addr_in);
    };
    
    // for booking type, we'll need user to select from options we define in chat
    function input_booking_type() {
        const booking_type = 'House Sitting';
        const checkbox = document.querySelector(`input[aria-label="${booking_type}"]`);
        checkbox.click();
    }

    // Size Input Options:
    // Small (0 to 15 lbs),
    // Medium (16 to 40 lbs),
    // Large (41 to 100 lbs),
    // Giant (101+ to  lbs)
    // function input_dog_size() {
    //     const size = 'Giant (101+ to  lbs)';
    //     const checkbox = document.querySelector(`input[aria-label="${size}"]`);
    //     checkbox.click();
    // }

    input_address();
    input_booking_type();
    // input_dog_size();
})();