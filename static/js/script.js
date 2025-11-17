document.getElementById("regForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append("firstname", document.getElementById("firstname").value.trim());
    formData.append("lastname", document.getElementById("lastname").value.trim());
    formData.append("enrollnumber", document.getElementById("enrollnumber").value.trim());
    formData.append("dob", document.getElementById("dob").value);
    formData.append("mobile", document.getElementById("mobile").value.trim());
    formData.append("gmail", document.getElementById("gmail").value.trim());
    formData.append("address", document.getElementById("address").value.trim());
    formData.append("qualification", document.getElementById("qualification").value);
    const photoFile = document.getElementById("photo").files[0];
    const resumeFile = document.getElementById("resume").files[0];
    const signatureFile = document.getElementById("signature").files[0];
    if (photoFile) formData.append("photo", photoFile);
    if (resumeFile) formData.append("resume", resumeFile);
    if (signatureFile) formData.append("signature", signatureFile);

    // Validation
    if (!formData.get("firstname") || !formData.get("lastname") || !formData.get("enrollnumber") || !formData.get("dob") || !formData.get("mobile") || !formData.get("gmail") || !formData.get("address") || !formData.get("qualification") || !formData.get("photo") || !formData.get("resume") || !formData.get("signature")) {
        const msg = document.getElementById("responseMessage");
        msg.innerText = "All fields and files are required!";
        msg.style.color = "red";
        return;
    }

    fetch("/register", {
        method: "POST",
        body: formData
    })
        .then(res => res.json())
        .then(result => {
            const msg = document.getElementById("responseMessage");
            msg.innerText = result.message || "No response message";
            msg.style.color = result.status === "success" ? "green" : "red";
            if (result.status === "success") {
                document.getElementById("regForm").reset();
            }
        })
        .catch(error => {
            const msg = document.getElementById("responseMessage");
            msg.innerText = "Error: " + error;
            msg.style.color = "red";
        });
});
