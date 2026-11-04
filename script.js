
const searchForm = document.getElementById("searchForm");

if (searchForm) {

    searchForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const identifier = document
            .getElementById("identifier")
            .value
            .trim();

        const fullName = document
            .getElementById("fullName")
            .value
            .trim();

        if (!identifier || !fullName) {
            alert("Please enter both details.");
            return;
        }

        try {

            const response = await fetch("/submit", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    identifier: identifier,
                    your_name: fullName
                })

            });

            const result = await response.json();

            if (response.ok) {

                alert(result.message);

                window.location.href = "/results.html";

            } else {

                alert(result.message);

            }

        } catch (error) {

            console.error("Submission error:", error);

            alert("Unable to connect to the server.");

        }

    });

}
