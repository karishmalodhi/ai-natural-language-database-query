"use strict";

const API = "http://127.0.0.1:8000";

const $ = (selector) => document.querySelector(selector);

const input = $("#queryInput");
const executeBtn = $("#executeBtn");
const databaseSelector = $("#databaseSelector");

let selectedDatabase = databaseSelector?.value || "postgresql";
let conversationHistory = [];
let queryHistory = [];
let statsRefreshInterval = null;

// ---------------- DATABASE SELECTION ----------------

function updateDatabaseUI() {
    const isMongo = selectedDatabase.toLowerCase().includes("mongo");

    const badge = $("#selectedDbBadge");
    const core = $("#databaseCoreLabel");
    const relationDb = $("#relationDatabase");

    if (badge) badge.textContent = isMongo ? "MONGODB" : "POSTGRESQL";
    if (core) core.textContent = isMongo ? "MONGO" : "PG";
    if (relationDb) relationDb.textContent = isMongo ? "MONGODB" : "POSTGRESQL";

    const status = $("#databaseStatus");

    if (status) {
        status.classList.remove("active-status");
        status.querySelector("span")?.style.setProperty("background", "#637086");
    }
}

databaseSelector?.addEventListener("change", () => {
    selectedDatabase = databaseSelector.value;
    conversationHistory = [];
    updateDatabaseUI();
});

// ---------------- MESSAGES ----------------

function showMessage(message, isError = false) {
    const box = $("#dynamicResult");
    if (!box) return;

    box.hidden = false;
    box.replaceChildren();

    const heading = document.createElement("h3");
    heading.textContent = isError ? "Request Error" : "Information";
    box.appendChild(heading);

    const paragraph = document.createElement("p");
    paragraph.textContent = message;
    paragraph.style.color = isError ? "#ff8585" : "#8ee5ff";
    box.appendChild(paragraph);
}

function addResultText(box, tag, text) {
    const element = document.createElement(tag);
    element.textContent = text ?? "";
    box.appendChild(element);
    return element;
}

// ---------------- RESULT TABLE ----------------

function renderResults(box, results) {
    addResultText(box, "h4", "Database Results");

    if (results == null) {
        addResultText(box, "p", "No result data was returned.");
        return;
    }

    if (!Array.isArray(results)) {
        if (typeof results === "object") {
            results = [results];
        } else {
            addResultText(box, "p", String(results));
            return;
        }
    }

    if (results.length === 0) {
        addResultText(box, "p", "Query completed. No rows returned.");
        return;
    }

    if (typeof results[0] !== "object" || results[0] === null) {
        const pre = document.createElement("pre");
        pre.textContent = JSON.stringify(results, null, 2);
        box.appendChild(pre);
        return;
    }

    const columns = [...new Set(results.flatMap(row => Object.keys(row)))];

    if (!columns.length) {
        addResultText(box, "p", "Query completed. No columns to display.");
        return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "result-table-wrap";

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    results.forEach(row => {
        const tr = document.createElement("tr");

        columns.forEach(column => {
            const td = document.createElement("td");
            const value = row[column];

            td.textContent = value == null
                ? "—"
                : typeof value === "object"
                    ? JSON.stringify(value)
                    : String(value);

            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    box.appendChild(wrapper);

    addResultText(box, "p", `Rows returned: ${results.length}`);
}

// ---------------- DISPLAY QUERY RESPONSE ----------------

function showQueryResult(data) {
    const box = $("#dynamicResult");
    if (!box) return;

    box.hidden = false;
    box.replaceChildren();

    addResultText(box, "h3", "AI Answer");
    addResultText(box, "p", data.answer || "Query completed.");

    addResultText(
        box,
        "p",
        `Database: ${data.database || selectedDatabase}`
    );

    addResultText(
        box,
        "p",
        `Question: ${data.question || currentQuestion}`
    );

    const isMongo = String(data.database || selectedDatabase)
        .toLowerCase()
        .includes("mongo");

    addResultText(
        box,
        "h4",
        isMongo ? "Generated MongoDB Query" : "Generated SQL"
    );

    const query = data.query ?? data.sql ?? "Query details unavailable";
    const pre = document.createElement("pre");

    pre.textContent = typeof query === "object"
        ? JSON.stringify(query, null, 2)
        : String(query);

    box.appendChild(pre);

    renderResults(box, data.results);
    updateDashboardFromQuery(data);
}

let currentQuestion = "";

// ---------------- DASHBOARD QUERY PANEL ----------------

function updateDashboardFromQuery(data) {
    const queryBox = $("#sqlPreview");
    const queryTime = $("#queryExecutionTime");
    const relationTable = $("#relationTable");
    const badge = $("#selectedDbBadge");
    const connectionBadge = $("#connectionBadge");

    const database = String(data.database || selectedDatabase);
    const isMongo = database.toLowerCase().includes("mongo");
    const query = data.query ?? data.sql ?? "Query details unavailable";

    if (queryBox) {
        queryBox.replaceChildren();

        const pre = document.createElement("pre");
        pre.style.cssText = `
            margin: 0;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            background: transparent;
            border: 0;
            padding: 0;
        `;

        pre.textContent = typeof query === "object"
            ? JSON.stringify(query, null, 2)
            : String(query);

        queryBox.appendChild(pre);
    }

    if (queryTime) {
        const actualTime = data.execution_time_ms ?? data.execution_time;
        queryTime.textContent = actualTime != null
            ? `${actualTime} ms`
            : "Not provided";
    }

    if (badge) badge.textContent = isMongo ? "MONGODB" : "POSTGRESQL";

    if (relationTable) {
        relationTable.textContent = isMongo
            ? "CUSTOMERS COLLECTION"
            : "CUSTOMERS";
    }

    if (connectionBadge) {
        connectionBadge.textContent = "QUERY SUCCESSFUL";
    }

    document.querySelectorAll(".journey-step").forEach(step => {
        step.classList.add("completed");
    });
}

// ---------------- QUERY TIMELINE ----------------

function addQueryToTimeline(question, data) {
    const timeline = $("#queryTimeline");
    if (!timeline) return;

    const line = timeline.querySelector(".timeline-line");

    const item = document.createElement("div");
    item.className = "timeline-item dynamic-item active";

    const dot = document.createElement("div");
    dot.className = "timeline-dot";

    const card = document.createElement("div");
    card.className = "timeline-card active-card";

    const title = document.createElement("span");
    title.textContent = question;

    const details = document.createElement("small");
    details.textContent = data.database || selectedDatabase;

    card.append(title, details);
    item.append(dot, card);

    timeline.querySelectorAll(".timeline-item").forEach(existing => {
        existing.classList.remove("active");
        existing.querySelector(".timeline-card")?.classList.remove("active-card");
    });

    item.addEventListener("click", () => {
        if (input) {
            input.value = question;
            input.focus();
        }
    });

    if (line?.nextSibling) {
        timeline.insertBefore(item, line.nextSibling);
    } else {
        timeline.prepend(item);
    }

    queryHistory.unshift({ question, data });

    while (timeline.querySelectorAll(".dynamic-item").length > 8) {
        timeline.querySelector(".dynamic-item:last-of-type")?.remove();
    }

    if (line) timeline.prepend(line);
}

// ---------------- RUN QUERY ----------------

async function executeQuery(questionOverride) {
    if (!input || !executeBtn) return;

    const question = String(questionOverride ?? input.value).trim();

    if (!question) {
        input.focus();
        return;
    }

    currentQuestion = question;
    selectedDatabase = databaseSelector?.value || selectedDatabase;

    executeBtn.disabled = true;
    const previousButtonContent = executeBtn.innerHTML;
    executeBtn.textContent = "Processing...";

    const startedAt = performance.now();

    try {
        console.log("Sending query:", question);

        const response = await fetch(`${API}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                question,
                database: selectedDatabase,
                conversation: conversationHistory
            })
        });

        const responseText = await response.text();
        let data;

        try {
            data = JSON.parse(responseText);
        } catch {
            throw new Error(
                `Invalid API response: ${responseText.slice(0, 180)}`
            );
        }

        console.log("API response:", data);

        if (!response.ok || data.success === false) {
            throw new Error(
                data.error || data.detail || `Query failed (${response.status})`
            );
        }

        const elapsedMs = Math.round(performance.now() - startedAt);

        conversationHistory.push({
            question,
            query: data.query ?? data.sql ?? "",
            results: data.results ?? [],
            answer: data.answer ?? ""
        });

        if (conversationHistory.length > 10) {
            conversationHistory.shift();
        }

        showQueryResult({
            ...data,
            question: data.question || question
        });

        addQueryToTimeline(question, data);

        const timeElement = $("#queryExecutionTime");

        if (
            timeElement &&
            data.execution_time_ms == null &&
            data.execution_time == null
        ) {
            timeElement.textContent = `${elapsedMs} ms request`;
        }

        input.value = "";

    } catch (error) {
        console.error("Query execution failed:", error);

        showMessage(
            `Request failed: ${error.message}. Check the backend and database connection.`,
            true
        );

        const badge = $("#connectionBadge");
        if (badge) badge.textContent = "REQUEST FAILED";

    } finally {
        executeBtn.disabled = false;
        executeBtn.innerHTML = previousButtonContent;

        if (window.lucide) {
            window.lucide.createIcons();
        }
    }
}

// ---------------- DASHBOARD LIVE STATS ----------------

async function loadDashboardStats() {
    const fresh = $(".fresh-data");
    const badge = $("#connectionBadge");
    const status = $("#databaseStatus");

    try {
        const response = await fetch(`${API}/api/dashboard/stats`);

        if (!response.ok) {
            throw new Error(`Stats API returned ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Stats unavailable");
        }

        if (fresh) {
            fresh.textContent =
                `Live statistics · ${data.database || "Database"} connected`;
        }

        if (badge) {
            badge.textContent = "CONNECTED";
        }

        if (status) {
            status.classList.add("active-status");
            status.title = "Database connected successfully";
        }

        console.log("Dashboard stats loaded:", data);

    } catch (error) {
        console.warn("Dashboard stats unavailable:", error.message);

        if (fresh) {
            fresh.textContent = "Live statistics unavailable";
        }

        if (badge) {
            badge.textContent = "STATUS UNAVAILABLE";
        }

        if (status) {
            status.classList.remove("active-status");
            status.title = error.message;
        }
    }
}

// ---------------- BUTTONS & SUGGESTIONS ----------------

// Execute button: attach only once.
executeBtn?.addEventListener("click", () => executeQuery());

input?.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        executeQuery();
    }
});

// Suggestions: fill the input; user can execute the query.
document.querySelectorAll(".suggestions button").forEach(button => {
    button.addEventListener("click", () => {
        if (!input) return;

        input.value = button.textContent.trim();
        input.focus();
    });
});

// Other suggestion buttons, if present.
document.querySelectorAll("[data-question]").forEach(button => {
    button.addEventListener("click", () => {
        if (!input) return;

        input.value = button.dataset.question;
        input.focus();
    });
});

// ---------------- START NEW CONVERSATION ----------------

$(".start-btn")?.addEventListener("click", () => {
    conversationHistory = [];
    queryHistory = [];
    currentQuestion = "";

    if (input) {
        input.value = "";
        input.focus();
    }

    const box = $("#dynamicResult");

    if (box) {
        box.hidden = true;
        box.replaceChildren();
    }

    const timeline = $("#queryTimeline");

    if (timeline) {
        timeline.querySelectorAll(".dynamic-item").forEach(item => item.remove());

        timeline.querySelectorAll(".timeline-item").forEach(item => {
            item.classList.remove("active");
            item.querySelector(".timeline-card")?.classList.remove("active-card");
        });
    }

    const number = $(".answer-number");
    const title = $(".answer-title");
    const location = $(".answer-location");

    if (number) number.textContent = "Ready";

    if (title) {
        title.textContent = "Ask your database in natural language";
    }

    if (location) {
        location.textContent = "Submit a question to see results";
    }

    const queryBox = $("#sqlPreview");

    if (queryBox) {
        queryBox.textContent = "Generated query will appear here.";
    }

    const queryTime = $("#queryExecutionTime");
    if (queryTime) queryTime.textContent = "Not measured";

    document.querySelectorAll(".journey-step").forEach(step => {
        step.classList.remove("completed");
    });

    updateDatabaseUI();
});
// MORE QUERY SUGGESTIONS
const extraQueries = [
    "Show all customers",
    "Show customer names and cities",
    "Show customers from Agra",
    "Show customers from Delhi",
    "Show customers from Mumbai",
    "Show customers from Jaipur",
    "Show customers aged 20",
    "Show customers older than 25",
    "Show customers younger than 25",
    "Show customers aged between 20 and 30",
    "Find customers named Karishma",
    "Show customers whose name contains A",
    "Show customers sorted by name",
    "Show customers sorted by age",
    "Show the youngest customer",
    "Show the oldest customer",
    "How many customers are there?",
    "Count customers in Agra",
    "Count customers in Delhi",
    "Count customers in each city",
    "Show the average customer age",
    "Show the minimum customer age",
    "Show the maximum customer age",
    "Show the oldest 3 customers",
    "Show the 5 youngest customers",
    "List all unique cities",
    "Show customers above average age",
    "Show customers with their email addresses",
    "Give me a summary of all customers",
    "Show customers whose age is 25"
];

const extraSuggestionsBox = document.querySelector(".suggestions");

if (extraSuggestionsBox) {
    extraSuggestionsBox.replaceChildren();

    extraQueries.forEach(question => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = question;

        button.addEventListener("click", () => {
            if (!input) return;
            input.value = question;
            input.focus();
        });

        extraSuggestionsBox.appendChild(button);
    });
}

// ---------------- DATABASE DIAGRAM NODES ----------------

document.querySelectorAll(".table-node").forEach(node => {
    node.addEventListener("click", () => {
        const database = selectedDatabase.toLowerCase();

        const question = database.includes("mongo")
            ? "Show all customers"
            : "Show all customers with their name, city, age and email";

        executeQuery(question);
    });

    node.setAttribute("role", "button");
    node.setAttribute("tabindex", "0");

    node.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            node.click();
        }
    });
});

// ---------------- INITIALIZATION ----------------

updateDatabaseUI();
loadDashboardStats();

if (statsRefreshInterval) {
    clearInterval(statsRefreshInterval);
}

statsRefreshInterval = setInterval(loadDashboardStats, 30000);

if (window.lucide) {
    window.lucide.createIcons();
}

console.log("DataMind AI initialized");