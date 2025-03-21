document.addEventListener("DOMContentLoaded", initializeDayView);

function initializeDayView() {
    const calendarBody = document.getElementById("calendar-body");
    const calendarTitle = document.getElementById("calendar-title");

    let currentDate = new Date();

    async function renderDay(date) {
        // Wyczyść istniejącą zawartość
        calendarBody.innerHTML = "";

        // Ustaw tytuł na aktualną datę
        calendarTitle.textContent = formatDate(date);

        // Pobranie zadań i wydarzeń
        const tasks = await fetchTasks();
        const events = await fetchEvents();

        // Tworzenie tabeli z podziałem na godziny (00:00 - 23:00)
        for (let hour = 0; hour < 24; hour++) {
            const row = document.createElement("tr");

            const timeCell = document.createElement("td");
            timeCell.textContent = `${hour}:00`;
            timeCell.classList.add("time-cell");
            row.appendChild(timeCell);

            const eventCell = document.createElement("td");
            eventCell.classList.add("event-cell");
            eventCell.style.display = "flex";
            eventCell.style.flexDirection = "column";

            const currentDateStr = date.toISOString().split("T")[0];
            let hasContent = false;

            // Dodawanie zadań do odpowiednich godzin
            tasks.forEach(task => {
                const startDate = new Date(task.start_date);
                const dueDate = new Date(task.due_date);
                if (date.toDateString() === startDate.toDateString()) {
                    if (hour >= 8) {
                        const taskDiv = document.createElement("div");
                        taskDiv.textContent = task.title;
                        taskDiv.classList.add("task");
                        taskDiv.style.backgroundColor = getColorByTitle(task.title);
                        taskDiv.style.color = "#fff";
                        taskDiv.style.marginBottom = "5px";
                        eventCell.appendChild(taskDiv);
                        hasContent = true;
                    }
                } else if (date > startDate && date < dueDate) {
                    const taskDiv = document.createElement("div");
                    taskDiv.textContent = task.title;
                    taskDiv.classList.add("task");
                    taskDiv.style.backgroundColor = getColorByTitle(task.title);
                    taskDiv.style.color = "#fff";
                    taskDiv.style.marginBottom = "5px";
                    eventCell.appendChild(taskDiv);
                    hasContent = true;
                } else if (date.toDateString() === dueDate.toDateString()) {
                    if (hour <= 16) {
                        const taskDiv = document.createElement("div");
                        taskDiv.textContent = task.title;
                        taskDiv.classList.add("task");
                        taskDiv.style.backgroundColor = getColorByTitle(task.title);
                        taskDiv.style.color = "#fff";
                        taskDiv.style.marginBottom = "5px";
                        eventCell.appendChild(taskDiv);
                        hasContent = true;
                    }
                }
            });

            // Dodawanie wydarzeń do odpowiednich godzin
            events.forEach(event => {
                const eventStartDate = new Date(event.start_date);
                const eventEndDate = new Date(event.end_date);
                if (
                    currentDateStr === eventStartDate.toISOString().split("T")[0] &&
                    eventStartDate.getHours() <= hour && eventEndDate.getHours() >= hour
                ) {
                    const eventDiv = document.createElement("div");
                    eventDiv.textContent = `🔔 ${event.name}`;
                    eventDiv.classList.add("event");
                    eventDiv.style.backgroundColor = getColorByTitle(event.name);
                    eventDiv.style.color = "#fff";
                    eventDiv.style.marginBottom = "5px";
                    eventCell.appendChild(eventDiv);
                    hasContent = true;
                }
            });

            if (!hasContent) {
                eventCell.textContent = "";
            }

            row.appendChild(eventCell);
            calendarBody.appendChild(row);
        }
    }

    // Formatowanie daty w formacie "DD.MM.YYYY"
    function formatDate(date) {
        const day = String(date.getDate()).padStart(2, "0");
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    // Zmienia dzień i renderuje kalendarz
    function changeDay(direction) {
        currentDate.setDate(currentDate.getDate() + direction);
        renderDay(currentDate);
    }

    // Przechodzi do dzisiejszego dnia
    function goToToday() {
        currentDate = new Date();
        renderDay(currentDate);
    }

    // Dodajemy funkcjonalności do przycisków
    document.getElementById("btn-prev").addEventListener("click", () => changeDay(-1));
    document.getElementById("btn-next").addEventListener("click", () => changeDay(1));
    document.getElementById("btn-today").addEventListener("click", goToToday);
    document.getElementById("view-selector").addEventListener("change", function () {
        const selectedView = this.value;
        loadView(selectedView);
    });

    renderDay(currentDate);
}