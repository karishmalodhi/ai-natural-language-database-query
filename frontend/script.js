const input = document.getElementById("queryInput");
const executeBtn = document.getElementById("executeBtn");


// ================================
// DATABASE SELECTOR
// ================================

let selectedDatabase = "postgresql";

const databaseSelector = document.createElement("select");

databaseSelector.id = "databaseSelector";

databaseSelector.innerHTML = `
    <option value="postgresql">PostgreSQL</option>
    <option value="mongodb">MongoDB</option>
`;

databaseSelector.style.marginBottom = "15px";
databaseSelector.style.padding = "10px 14px";
databaseSelector.style.borderRadius = "8px";
databaseSelector.style.background = "#111827";
databaseSelector.style.color = "#ffffff";
databaseSelector.style.border = "1px solid rgba(99, 216, 255, 0.4)";
databaseSelector.style.fontSize = "14px";
databaseSelector.style.cursor = "pointer";

if (input && input.parentElement) {
    input.parentElement.insertBefore(databaseSelector, input);
}

databaseSelector.addEventListener("change", () => {

    selectedDatabase = databaseSelector.value;

    // New database = new conversation context
    conversationHistory = [];

    console.log("Selected Database:", selectedDatabase);

});


// ================================
// CONVERSATION MEMORY
// ================================

let conversationHistory = [];


// ================================
// SUGGESTION BUTTONS
// ================================

const suggestionButtons = document.querySelectorAll(".suggestions button");

suggestionButtons.forEach((button) => {

    button.addEventListener("click", () => {

        input.value = button.innerText;
        input.focus();

    });

});


// ================================
// EXECUTE QUERY
// ================================

executeBtn.addEventListener("click", executeQuery);


// ================================
// ENTER KEY
// ================================

input.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {
        executeQuery();
    }

});


// ================================
// QUERY FUNCTION
// ================================

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

                question: question,

                database: selectedDatabase,

                conversation: conversationHistory

            })

        });


        const data = await response.json();

        console.log("BACKEND RESPONSE:", data);


        if (data.success) {

            executeBtn.innerHTML = "✓ Query Executed";

            console.log("Database:", data.database);
            console.log("Generated Query:", data.query || data.sql);
            console.log("Database Result:", data.results);
            console.log("AI Answer:", data.answer);


            // ================================
            // SAVE FULL CONVERSATION CONTEXT
            // ================================

            conversationHistory.push({

                question: question,

                query: data.query || data.sql || "",

                results: data.results || [],

                answer: data.answer || ""

            });


            // Keep only last 5 conversations
            if (conversationHistory.length > 5) {

                conversationHistory.shift();

            }


            console.log(
                "CONVERSATION HISTORY:",
                conversationHistory
            );


            showQueryResult(data);

            // Clear input for next question
            input.value = "";

        }

        else {

            executeBtn.innerHTML = "✗ Query Failed";

            showError(data.error);

            console.error("Backend Error:", data.error);

        }

    }

    catch (error) {

        executeBtn.innerHTML = "✗ Backend Offline";

        showError("Unable to connect to backend.");

        console.error("CONNECTION ERROR:", error);

    }


    setTimeout(() => {

        executeBtn.innerHTML = originalHTML;
        executeBtn.disabled = false;

    }, 1800);

}


// ================================
// SHOW QUERY RESULT
// ================================

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


    const databaseName =
        data.database === "mongodb"
            ? "MongoDB"
            : "PostgreSQL";


    const generatedQuery =
        data.database === "mongodb"
            ? JSON.stringify(data.query, null, 2)
            : data.sql;


    let resultHTML = `

        <h3>AI Answer</h3>

        <p style="font-size: 20px;">
            ${data.answer || "No answer generated."}
        </p>

        <p>
            <strong>Database:</strong>
            ${databaseName}
        </p>

        <p>
            <strong>Question:</strong>
            ${data.question}
        </p>

        <p>
            <strong>
                ${
                    data.database === "mongodb"
                        ? "Generated MongoDB Query:"
                        : "Generated SQL:"
                }
            </strong>
        </p>

        <pre>${generatedQuery}</pre>

        <p>
            <strong>Database Result:</strong>
        </p>

    `;


    if (data.results && data.results.length > 0) {

        resultHTML += `

            <pre>${JSON.stringify(data.results, null, 2)}</pre>

        `;

    }

    else {

        resultHTML += `

            <p>No data found.</p>

        `;

    }


    resultBox.innerHTML = resultHTML;

}


// ================================
// SHOW ERROR
// ================================

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


// ================================
// START INVESTIGATION
// ================================

const startButton = document.querySelector(".start-btn");


if (startButton) {

    startButton.addEventListener("click", () => {

        input.value = "";
        input.focus();

        conversationHistory = [];

    });

}


// ================================
// DATABASE NODES
// ================================

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


// ================================
// TIMELINE
// ================================

const timelineItems = document.querySelectorAll(".timeline-item");


timelineItems.forEach((item) => {

    item.addEventListener("click", () => {

        timelineItems.forEach((i) => {

            i.classList.remove("active");

        });


        item.classList.add("active");


        const text = item.innerText
            .replace("↓", "")
            .trim();


        if (text !== "NEW QUERY") {

            input.value = text;
            input.focus();

        }

        else {

            input.value = "";
            input.focus();

        }

    });

});


console.log("SCRIPT JS LOADED");