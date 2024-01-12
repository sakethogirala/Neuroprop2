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


// function change_data(lender){
//     console.log(lender);
//     document.getElementById("offcanvas-title").innerHTML = lender.querySelector("#title").innerHTML;
//     document.getElementById("contact-details").innerHTML = lender.getAttribute("contact");

//     // New code to handle additional attributes
//     document.getElementById("max-loan").innerHTML = lender.getAttribute("max_loan");
//     document.getElementById("min-loan").innerHTML = lender.getAttribute("min_loan");
//     document.getElementById("max-ltv").innerHTML = lender.getAttribute("max_ltv");
//     document.getElementById("lender-property-types").innerHTML = lender.getAttribute("property_types");
//     document.getElementById("lender-states").innerHTML = lender.getAttribute("states");
//     console.log("testing ", lender.querySelector("#test"));
// }

// Rest of your JavaScript code...

document.getElementById("close-offcanvas").addEventListener("click", (e)=>{
    active_lender = null;
})

function scrollToAddNote() {
    // Get the element
    var addNoteSection = document.getElementById("add-note-section");

    // Scroll to the add note section
    addNoteSection.scrollIntoView({ behavior: 'smooth' });
}
