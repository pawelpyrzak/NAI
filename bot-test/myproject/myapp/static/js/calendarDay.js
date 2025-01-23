document.addEventListener("DOMContentLoaded", initializeDayView);

function initializeDayView() {
    const calendarBody = document.getElementById("calendar-body");
    const calendarTitle = document.getElementById("calendar-title");

    let currentDate = new Date();

    async function renderDay(date) {

        calendarBody.innerHTML = "";

        calendarTitle.textContent = formatDate(date);

        const tasks = await fetchTasks();
        const events = await fetchEvents();

        const currentDateStr = date.toISOString().split("T")[0];
        const dayTasks = tasks.filter(task => {
            const startDate = new Date(task.start_date).toISOString().split("T")[0];
            const dueDate = new Date(task.due_date).toISOString().split("T")[0];
            return currentDateStr >= startDate && currentDateStr <= dueDate;
        });

        const dayEvents = events.filter(event => {
            const startDate = new Date(event.start_date).toISOString().split("T")[0];
            const endDate = new Date(event.end_date).toISOString().split("T")[0];
            return currentDateStr >= startDate && currentDateStr <= endDate;
        });

        if (dayTasks.length > 0) {
            const taskSection = document.createElement("td");
            taskSection.classList.add("day");
            taskSection.innerHTML = `<h3>Zadania</h3>`;
            dayTasks.forEach(task => {
                const taskDiv = document.createElement("div");
                taskDiv.textContent = task.title;
                taskDiv.classList.add("day");
                taskDiv.style.backgroundColor = getColorByTitle(task.title);
                taskDiv.style.color = "#fff";
                taskSection.appendChild(taskDiv);
            });
            calendarBody.appendChild(taskSection);
        }

        if (dayEvents.length > 0) {
            const eventSection = document.createElement("td");
            eventSection.classList.add("day");
            eventSection.innerHTML = `<h3>Wydarzenia</h3>`;
            dayEvents.forEach(event => {
                const eventDiv = document.createElement("div");
                eventDiv.textContent = `🔔 ${event.name}`;
                eventDiv.classList.add("day");
                eventDiv.style.backgroundColor = getColorByTitle(event.name);
                eventDiv.style.color = "#fff";
                eventSection.appendChild(eventDiv);
            });
            calendarBody.appendChild(eventSection);
        }

        if (dayTasks.length === 0 && dayEvents.length === 0) {
            const emptyMessage = document.createElement("p");
            emptyMessage.textContent = "Brak zadań i wydarzeń na dziś.";
            emptyMessage.classList.add("empty-message");
            calendarBody.appendChild(emptyMessage);
        }
    }

    function formatDate(date) {
        const day = String(date.getDate()).padStart(2, "0");
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    function changeDay(direction) {
        currentDate.setDate(currentDate.getDate() + direction);
        renderDay(currentDate);
    }

    function goToCurrentDay() {
        currentDate = new Date();
        renderDay(currentDate);
    }

    document.getElementById("btn-prev").addEventListener("click", () => changeDay(-1));
    document.getElementById("btn-next").addEventListener("click", () => changeDay(1));
    document.getElementById("btn-today").addEventListener("click", goToCurrentDay);
    document.getElementById("view-selector").addEventListener("change", function () {
        const selectedView = this.value;
        loadView(selectedView);
    });

    renderDay(currentDate);
}