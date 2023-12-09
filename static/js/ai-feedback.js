let feedback_btns = document.getElementsByClassName("btn-ai-feedback");

for (let i = 0; i < feedback_btns.length; i++) {
    feedback_btns[i].addEventListener("click", function(e) {
        console.log("clicked");
        let element = this.parentElement;
        let endpoint = this.getAttribute("endpoint");
        element.innerHTML = `
        <div class="d-flex justify-content-center">
        <div class="spinner-border text-primary" role="status"></div>
        </div>
        `;
        // Define the polling function
        function poll() {
            console.log("polling...");
            fetch(endpoint)
                .then(response => response.json())
                .then(data => {
                    if (data.status == "success") {
                        console.log(data); // Process your data here
                        element.innerHTML = `
                        <h5 class="text-primary float-start mt-3">Smart Feedback</h5>
                        <div class="ribbon-content">
                            ${data.message}
                        </div>
                        `;
                        clearInterval(pollingInterval); // Stop polling
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    clearInterval(pollingInterval); // Stop polling on error
                });
        }

        // Poll immediately
        poll();

        // Set up the interval for subsequent polling
        let pollingInterval = setInterval(poll, 5000); // Poll every 5 seconds
    });
}
