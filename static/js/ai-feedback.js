let feedback_btns = document.getElementsByClassName("btn-ai-feedback");
let pollingIntervals = {};
let documents = document.getElementsByClassName("document")



for (let i = 0; i < documents.length; i++) {
    let document_element = documents[i];
    let document_pk = document_element.getAttribute("document_pk");
    
    if (document_element.getAttribute("checked") == "False") {
        // document_element.querySelector("#document-status").style.display = "none";
        // document_element.querySelector("#document-loading").style.display = "block";
        document_element.querySelector("#loading-warning").style.display = "block";
        poll_document(document_element);
        pollingIntervals[document_pk] = setInterval(poll_document, 10000, document_element);
    }
}


function poll_document(document_element) {
    let document_pk = document_element.getAttribute("document_pk");
    let endpoint = document.getElementById("document-upload").getAttribute("endpoint");
    fetch(endpoint + "?document_pk=" + document_pk)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status == "success") {
                console.log("success");
                clearInterval(pollingIntervals[document_pk]); // Use the stored interval ID to stop polling
                delete pollingIntervals[document_pk]; // Optionally, remove the entry from the map
                window.location.reload();
                
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("something went wrong please try re-uploading this file or choosing a different file.")
            clearInterval(pollingIntervals[document_pk]); // Optionally, stop polling on error
            delete pollingIntervals[document_pk]; // Optionally, remove the entry from the map
            document_element.querySelector("#delete-document-link").click()
        });
}

// for (let i = 0; i < feedback_btns.length; i++) {
//     feedback_btns[i].addEventListener("click", function(e) {
//         console.log("clicked");
//         let element = this.parentElement;
//         let endpoint = this.getAttribute("endpoint");
//         element.innerHTML = `
//         <div class="d-flex justify-content-center">
//         <div class="spinner-border text-primary" role="status"></div>
//         </div>
//         `;
//         // Define the polling function
//         function poll() {
//             console.log("polling...");
//             fetch(endpoint)
//                 .then(response => response.json())
//                 .then(data => {
//                     if (data.status == "success") {
//                         console.log(data); // Process your data here
//                         element.innerHTML = `
//                         <h5 class="text-primary float-start mt-3">Smart Feedback</h5>
//                         <div class="ribbon-content">
//                             ${data.message}
//                         </div>
//                         `;
//                         clearInterval(pollingInterval); // Stop polling
//                     }
//                 })
//                 .catch(error => {
//                     console.error('Error:', error);
//                     // clearInterval(pollingInterval); // Stop polling on error
//                 });
//         }

//         // Poll immediately
//         poll();

//         // Set up the interval for subsequent polling
//         let pollingInterval = setInterval(poll, 5000); // Poll every 5 seconds
//     });
// }


// function file_check(document_pk){
//     console.log("polling...");
//     poll_file_check(document_pk);
//     let pollingInterval = setInterval(poll_file_check, 5000, document_pk); 
// }
