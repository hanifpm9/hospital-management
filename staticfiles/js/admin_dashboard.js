document.addEventListener("DOMContentLoaded", function () {
    var ctx = document.getElementById("myChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{
                label: "Total Patients",
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: "rgba(54, 162, 235, 0.5)",
            }]
        }
    });
});
