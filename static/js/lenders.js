const lenders = document.getElementsByClassName("lender-row");
let offcanvas_toggle = document.getElementById("toggle_offcanvas");
let active_lender = null;



for(let i = 0; i < lenders.length; i++){
    lenders[i].addEventListener("click", function(e){
        console.log(this)
        console.log(this.querySelector("#title").innerHTML);
        show_offcanvas(this);
    })
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
            console.log(html)
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

document.getElementById('create_outreach').addEventListener('submit', function(e) {
    e.preventDefault();

    var selectedLenders = [];
    document.querySelectorAll('.lender-select:checked').forEach(function(checkbox) {
        selectedLenders.push(checkbox.value);
    });

    // Join the array into a string
    this.querySelector("#lenders").value = selectedLenders.join(',');

    this.submit();
});
