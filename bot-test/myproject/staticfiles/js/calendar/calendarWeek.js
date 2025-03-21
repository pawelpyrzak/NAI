document.addEventListener("DOMContentLoaded", initializeWeekView);

function initializeWeekView() {
    const calendarBody = document.getElementById("calendar-body");
    const calendarTitle = document.getElementById("calendar-title");

    let currentDate = new Date();

    async function renderWeek(date) {
        // Wyczyść istniejącą zawartość
        calendarBody.innerHTML = "";

        // Znajdź pierwszy dzień tygodnia (poniedziałek)
        const startOfWeek = new Date(date);
        startOfWeek.setDate(startOfWeek.getDate() - (startOfWeek.getDay() || 7) + 1);

        // Ustaw tytuł na zakres dat tygodnia
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(endOfWeek.getDate() + 6);
        calendarTitle.textContent = `${formatDate(startOfWeek)} - ${formatDate(endOfWeek)}`;

        // Pobranie zadań i wydarzeń
        const tasks = await fetchTasks();
        const events = await fetchEvents();

        // Tworzenie jednego wiersza na tydzień
        const row = document.createElement("tr");

        for (let i = 0; i < 7; i++) {
            const cell = document.createElement("td");
            const currentDay = new Date(startOfWeek);
            currentDay.setDate(currentDay.getDate() + i);

            cell.textContent = currentDay.getDate();
            cell.classList.add("day");

            // Dodaj klasy, jeśli dzień jest z innego miesiąca
            if (currentDay.getMonth() !== date.getMonth()) {
                cell.classList.add("other-month");
            }

            const currentDateStr = currentDay.toISOString().split("T")[0];

            // Dodawanie zadań do komórki
            const dayTasks = tasks.filter(task => {
                const startDate = new Date(task.start_date);
                const dueDate = new Date(task.due_date);
                return currentDay >= startDate && currentDay <= dueDate;
            });

            dayTasks.forEach(task => {
                const taskDiv = document.createElement("div");
                taskDiv.textContent = task.title;
                taskDiv.classList.add("task");
                taskDiv.style.backgroundColor = getColorByTitle(task.title);
                taskDiv.style.color = "#fff";
                cell.appendChild(taskDiv);
            });

            // Dodawanie wydarzeń do komórki
            const dayEvents = events.filter(event => {
                const startDate = new Date(event.start_date).toISOString().split("T")[0];
                const endDate = new Date(event.end_date).toISOString().split("T")[0];
                return currentDateStr >= startDate && currentDateStr <= endDate;
            });

            dayEvents.forEach(event => {
                const eventDiv = document.createElement("div");
                eventDiv.textContent = `🔔 ${event.name}`;
                eventDiv.classList.add("event");
                eventDiv.style.backgroundColor = getColorByTitle(event.name);
                eventDiv.style.color = "#fff";
                cell.appendChild(eventDiv);
            });

            row.appendChild(cell);
        }

        calendarBody.appendChild(row);
    }

    // Formatowanie daty w formacie "DD.MM"
    function formatDate(date) {
        const day = String(date.getDate()).padStart(2, "0");
        const month = String(date.getMonth() + 1).padStart(2, "0");
        return `${day}.${month}`;
    }

    // Zmienia tydzień i renderuje kalendarz
    function changeWeek(direction) {
        currentDate.setDate(currentDate.getDate() + direction * 7);
        renderWeek(currentDate);
    }

    // Przechodzi do obecnego tygodnia
    function goToCurrentWeek() {
        currentDate = new Date();
        renderWeek(currentDate);
    }

    // Dodajemy funkcjonalności do przycisków
    document.getElementById("btn-prev").addEventListener("click", () => changeWeek(-1));
    document.getElementById("btn-next").addEventListener("click", () => changeWeek(1));
    document.getElementById("btn-today").addEventListener("click", goToCurrentWeek);
    document.getElementById("view-selector").addEventListener("change", function () {
        const selectedView = this.value;
        loadView(selectedView);
    });

    renderWeek(currentDate);
}