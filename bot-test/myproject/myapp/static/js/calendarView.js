function loadView(viewName) {
    const calendarContent = document.querySelector(".calendar-content");

    let viewPath = `/calendar/${viewName.replace(/^\/|\/$/g, '')}`;
    console.log("Generated path:", viewPath);

    fetch(viewPath)
        .then((response) => {
            console.log('Response status:', response.status);  
            if (!response.ok) {
                throw new Error(`Nie udało się załadować widoku. Status: ${response.status}`);
            }
            return response.text();
        })
        .then((html) => {
            calendarContent.innerHTML = html;
            if (viewName === "month") {
                initializeMonthView();
            } else if (viewName === "week") {
                initializeWeekView();
            } else if (viewName === "day") {
                initializeDayView();
            }
        })
        .catch((error) => {
            console.error("Błąd ładowania widoku:", error);
            calendarContent.innerHTML =
                "<p>Błąd ładowania widoku. Spróbuj ponownie później.</p>";
        });
}

async function fetchTasks() {
    try {
        const response = await fetch("/api/tasks/");
        if (!response.ok) {
            throw new Error("Failed to fetch tasks");
        }
        const tasks = await response.json();
        return tasks;
    } catch (error) {
        console.error("Error fetching tasks:", error);
        return [];
    }
}

async function fetchEvents() {
    try {
        const response = await fetch("/api/events/");
        if (!response.ok) {
            throw new Error("Failed to fetch events");
        }
        const events = await response.json();
        return events;
    } catch (error) {
        console.error("Error fetching events:", error);
        return [];
    }
}
function getColorByTitle(title) {
    const hash = Array.from(title).reduce((acc, char) => acc + char.charCodeAt(0), 0);
    let hue = hash+60 % 360;
    return `hsl(${hue}, 70%, 60%)`;

}