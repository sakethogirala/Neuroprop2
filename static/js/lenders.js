let lenders = document.getElementsByClassName("lender-row");
let offcanvas_toggle = document.getElementById("toggle_offcanvas");
let active_lender = null;
let checkboxes = document.querySelectorAll('.lender-row .lender-select');

resetLenderTable();

function resetLenderTable(){
    for(let i = 0; i < lenders.length; i++){
        lenders[i].addEventListener("click", function(e){
            show_offcanvas(this);
        })
    }
    for(let i = 0; i < checkboxes.length; i++){
        checkboxes[i].addEventListener("click", function(e){
            e.stopPropagation();
        })
    }

}


function show_offcanvas(lender){
    if(active_lender == lender){
        offcanvas_toggle.click();
        active_lender = null;
        return;
    }
    if(!active_lender){
        offcanvas_toggle.click();
    }
    active_lender = lender;
    change_data(lender);
}

function change_data(lender){
    let lender_pk = lender.getAttribute('lender_pk');
    let endpoint = lender.getAttribute("endpoint")

    fetch(`${endpoint}?lender_pk=${lender_pk}`)
        .then(response => response.text())
        .then(html => {
            // Insert the fetched HTML into the offcanvas body
            document.getElementById("offcanvas-body").innerHTML = html;
        })
        .catch(error => console.error('Error:', error));
}



document.getElementById("close-offcanvas").addEventListener("click", (e)=>{
    active_lender = null;
})

function scrollToAddNote() {
    // Get the element
    var addNoteSection = document.getElementById("add-note-section");

    // Scroll to the add note section
    addNoteSection.scrollIntoView({ behavior: 'smooth' });
}


document.getElementById('create-outreach-btn').addEventListener('click', function(e) {
    let modalElement = document.getElementById('create-outreach-modal')
    var selectedLenders = [];
    document.querySelectorAll('.lender-select:checked').forEach(function(checkbox) {
        selectedLenders.push(checkbox.value);
    });
    if(selectedLenders.length == 0){
        return alert("Please select lenders.")
    }
    modalElement.querySelector("#lender-count").innerHTML = selectedLenders.length;
    modalElement.querySelector("#lenders").value = selectedLenders.join(',');
    var myModal = new bootstrap.Modal(modalElement);
    myModal.show(); 
});

let lender_search_endpoint = document.getElementById("lender-search-endpoint").value;
let lendersTable = document.getElementById("lenders-table")
    const inputFields = document.querySelectorAll('#name, #loan_amount');
    inputFields.forEach(field => field.addEventListener('keyup', function() {
        console.log("input ")
        performSearch();
    }));
    const searchFields = document.querySelectorAll('#state, #property_type');
    searchFields.forEach(field => field.addEventListener('change', function() {
        console.log("select ")
        performSearch();
    }));

    function performSearch() {
        let name = document.getElementById('name').value;
        let loanAmount = document.getElementById('loan_amount').value;
        let state = document.getElementById('state').value;
        let propertyType = document.getElementById('property_type').value;
        
        fetch(`${lender_search_endpoint}?name=${name}&loan_amount=${loanAmount}&state=${state}&property_type=${propertyType}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            lendersTable.innerHTML = data.html;
            resetLenderTable();
        });
    }



