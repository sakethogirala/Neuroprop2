
    var dropzones = document.getElementsByClassName("dropzone");
    console.log(dropzones);

    for (let i = 0; i < dropzones.length; i++) {
        console.log("Initializing Dropzone");

        let dropzone = new Dropzone(dropzones[i], {
            addedfile: file => {
                console.log(file);
            },
            acceptedFiles: "application/pdf, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, text/csv"
        });


        dropzone.on("sending", function (file, xhr, formData) {
            console.log("File sending");
            document.getElementById("document-upload").style.display = "none";
            document.getElementById("document-loading").style.display = "block";
            formData.append("document_type_pk", "{{ current_document_type.pk }}");

        });
        dropzone.on("success", function (file, response) {
            // Refresh the page
            console.log(file);
            console.log(response)
            if (response.status == "success") {
                window.location.reload();
                // document.getElementById("document-loading-text").innerHTML = "Analyzing file...";
                // file_check(response.document_pk);
            }
        });
        console.log("Dropzone initialized: ", dropzone);
    }
