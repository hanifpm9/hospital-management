document.addEventListener("DOMContentLoaded", function () {
    document.querySelector("#searchbar").addEventListener("keyup", function () {
        let query = this.value;
        fetch(`/api/patient-search/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                let resultsDiv = document.getElementById("search-results");
                resultsDiv.innerHTML = "";
                data.forEach(patient => {
                    let div = document.createElement("div");
                    div.innerHTML = patient.name;
                    resultsDiv.appendChild(div);
                });
            });
    });
});
