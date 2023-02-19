function summarizeOnChange(inputId, resultsDivId, outputDivId) {
    const input_elem = document.getElementById(inputId);
    const results_elem = document.getElementById(resultsDivId);
    const output_elem = document.getElementById(outputDivId);

    console.log("input: " + input_elem, "results: " + results_elem);
    let timeoutId;

    function handleChange() {
        // Clear any previous timeouts
        clearTimeout(timeoutId);

        // Delay execution of the summarize function by 500ms to give the results time to load
        timeoutId = setTimeout(() => {
            console.log("Summarizing...");
            summarize(input_elem, results_elem, output_elem);
        }, 777); // FIXME: hopefully this is long enough to load the results
    }

    // Watch for changes to the results element using MutationObserver
    const observer = new MutationObserver(handleChange);
    observer.observe(results_elem, { childList: true, subtree: true });
}

function summarize(input_elem, results_elem, output_elem) {
    const text_results = results_elem.textContent;
    const q = input_elem.value

    const payload = {
        q: q,
        text_results: text_results,
    };

    // SSE is a class defined in sse.js
    // Should be imported in the HTML file before this script
    const eventSource = new SSE("summary", { method: 'POST', payload: JSON.stringify(payload) });

    eventSource.onmessage = function (event) {
        if (!event.data || event.data == "[DONE]") {
            eventSource.close();
            return;
        }
        const result = JSON.parse(event.data);
        output_elem.innerHTML += result['choices'][0]['text'];
        return;
    };
    eventSource.stream();
}
