const input = document.getElementById("queryInput");
const executeBtn = document.getElementById("executeBtn");


// SUGGESTION BUTTONS
const suggestionButtons = document.querySelectorAll(".suggestions button");

suggestionButtons.forEach((button) => {
    button.addEventListener("click", () => {
        input.value = button.innerText;
        input.focus();
    });
});


// EXECUTE QUERY
executeBtn.addEventListener("click", executeQuery);


// ENTER KEY
input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        executeQuery();
    }
});


// QUERY FUNCTION
// QUERY FUNCTION
async function executeQuery() {

    const question = input.value.trim();

    if (!question) {
        input.focus();
        return;
    }

    const originalHTML = executeBtn.innerHTML;

    executeBtn.innerHTML = "Processing...";
    executeBtn.disabled = true;

    try {

        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        console.log("BACKEND RESPONSE:", data);

        if (data.success) {

            executeBtn.innerHTML = "✓ Query Executed";

            console.log("Generated SQL:", data.sql);
            console.log("Database Result:", data.results);

            // Show result in webpage
            showQueryResult(data);

        } else {

            executeBtn.innerHTML = "✗ Query Failed";

            showError(data.error);
            console.error("Backend Error:", data.error);
        }

    } catch (error) {

        executeBtn.innerHTML = "✗ Backend Offline";

        showError("Unable to connect to backend.");
        console.error("CONNECTION ERROR:", error);
    }

    setTimeout(() => {
        executeBtn.innerHTML = originalHTML;
        executeBtn.disabled = false;
    }, 1800);
}
// SHOW QUERY RESULT
function showQueryResult(data) {

    let resultBox = document.getElementById("dynamicResult");

    if (!resultBox) {

        resultBox = document.createElement("div");
        resultBox.id = "dynamicResult";

        resultBox.style.marginTop = "25px";
        resultBox.style.padding = "20px";
        resultBox.style.border = "1px solid rgba(99, 216, 255, 0.3)";
        resultBox.style.borderRadius = "12px";
        resultBox.style.background = "rgba(10, 20, 30, 0.8)";

        executeBtn.parentElement.appendChild(resultBox);
    }

    let resultHTML = `
        <h3>Query Result</h3>

        <p>
            <strong>Question:</strong>
            ${data.question}
        </p>

        <p>
            <strong>Generated SQL:</strong>
        </p>

        <pre>${data.sql}</pre>

        <p>
            <strong>Database Result:</strong>
        </p>
    `;

    if (data.results && data.results.length > 0) {
        resultHTML += `
            <pre>${JSON.stringify(data.results, null, 2)}</pre>
        `;
    } else {
        resultHTML += `<p>No data found.</p>`;
    }

    resultBox.innerHTML = resultHTML;
}


// SHOW ERROR
function showError(message) {

    let resultBox = document.getElementById("dynamicResult");

    if (!resultBox) {

        resultBox = document.createElement("div");
        resultBox.id = "dynamicResult";

        resultBox.style.marginTop = "25px";
        resultBox.style.padding = "20px";
        resultBox.style.border = "1px solid rgba(255, 80, 80, 0.4)";
        resultBox.style.borderRadius = "12px";
        resultBox.style.background = "rgba(30, 10, 10, 0.8)";

        executeBtn.parentElement.appendChild(resultBox);
    }

    resultBox.innerHTML = `
        <h3>Query Error</h3>
        <p>${message}</p>
    `;
}

// START INVESTIGATION
const startButton = document.querySelector(".start-btn");

if (startButton) {
    startButton.addEventListener("click", () => {
        input.value = "";
        input.focus();
    });
}


// DATABASE NODES
const nodes = document.querySelectorAll(".table-node");

nodes.forEach((node) => {

    node.addEventListener("mouseenter", () => {
        node.style.borderColor = "#63d8ff";
        node.style.color = "#8ee5ff";
        node.style.boxShadow = "0 0 18px rgba(83, 205, 244, 0.18)";
    });

    node.addEventListener("mouseleave", () => {
        node.style.borderColor = "";
        node.style.color = "";
        node.style.boxShadow = "";
    });

});


console.log("SCRIPT JS LOADED");

const timelineItems = document.querySelectorAll(".timeline-item");

timelineItems.forEach((item) => {

    item.addEventListener("click", () => {

        // Remove active from all
        timelineItems.forEach((i) => {
            i.classList.remove("active");
        });

        // Add active to clicked item
        item.classList.add("active");

        // Put timeline text into input
        const text = item.innerText
            .replace("↓", "")
            .trim();

        if (text !== "NEW QUERY") {
            input.value = text;
            input.focus();
        } else {
            input.value = "";
            input.focus();
        }

    });

});