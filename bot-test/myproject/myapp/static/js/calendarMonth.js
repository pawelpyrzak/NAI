document.addEventListener("DOMContentLoaded", initializeMonthView);

function initializeMonthView() {

    const calendarBody = document.getElementById("calendar-body");
    const calendarTitle = document.getElementById("calendar-title");

    let currentDate = new Date();

    async function renderCalendar(date) {

        calendarBody.innerHTML = "";

        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDayOfWeek = new Date(year, month, 1).getDay() || 7; 
        const daysInMonth = new Date(year, month + 1, 0).getDate(); 
        const daysInPrevMonth = new Date(year, month, 0).getDate(); 
        const rows = 6; 
        let currentDay = 1;
        const tasks = await fetchTasks();
        const events = await fetchEvents();

        calendarTitle.textContent = `${getMonthName(month)} ${year}`;

        for (let i = 0; i < rows; i++) {
            const row = document.createElement("tr");

            for (let j = 1; j <= 7; j++) {
                const cell = document.createElement("td");

                if (i === 0 && j < firstDayOfWeek) {
                    const prevMonthDay = daysInPrevMonth - (firstDayOfWeek - j) + 1;
                    cell.textContent = prevMonthDay;
                    cell.classList.add("empty", "other-month");
                }

                else if (currentDay <= daysInMonth) {
                    cell.textContent = currentDay;
                    cell.classList.add("day");
                    const currentDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(currentDay).padStart(2, "0")}`;

                    const dayTasks = tasks.filter(task => {
                        const startDate = new Date(task.start_date);
                        const dueDate = new Date(task.due_date);
                        const currentDate = new Date(currentDateStr);
                        return currentDate >= startDate && currentDate <= dueDate;
                    });

                    if (dayTasks.length > 0) {
                        dayTasks.forEach(task => {
                            const taskDiv = document.createElement("div");
                            taskDiv.textContent = task.title;
                            taskDiv.classList.add("task");
                            taskDiv.style.backgroundColor = getColorByTitle(task.title);
                            taskDiv.style.color = "#fff";

                            cell.appendChild(taskDiv);
                        });
                    }

                    const dayEvents = events.filter(event => {
                        const startDate = new Date(event.start_date).toISOString().split("T")[0];
                        const endDate = new Date(event.end_date).toISOString().split("T")[0];
                        const currentDate = currentDateStr
                        return currentDate >= startDate && currentDate <= endDate;
                    });
                    dayEvents.forEach(event => {
                        const eventDiv = document.createElement("div");
                        eventDiv.textContent = `🔔 ${event.name}`;
                        eventDiv.classList.add("event");
                        eventDiv.style.backgroundColor = getColorByTitle(event.name);
                        eventDiv.style.color = "#fff";
                        cell.appendChild(eventDiv);
                    });

                    currentDay++;
                }

                else {
                    const nextMonthDay = currentDay - daysInMonth;
                    cell.textContent = nextMonthDay;
                    cell.classList.add("empty", "other-month");
                    currentDay++;
                }

                row.appendChild(cell);
            }

            calendarBody.appendChild(row);
        }
    }

    function getMonthName(monthIndex) {
        const months = [
            "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
            "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
        ];
        return months[monthIndex];
    }

    function changeMonth(direction) {
        currentDate.setMonth(currentDate.getMonth() + direction);
        renderCalendar(currentDate);
    }

    function goToCurrentMonth() {
        currentDate = new Date();
        renderCalendar(currentDate);
    }

    document.getElementById("btn-prev").addEventListener("click", () => changeMonth(-1));
    document.getElementById("btn-next").addEventListener("click", () => changeMonth(1));
    document.getElementById("btn-today").addEventListener("click", goToCurrentMonth);
    document.getElementById("view-selector").addEventListener("change", function () {
        const selectedView = this.value; 
        loadView(selectedView); 
    })

    renderCalendar(currentDate);
}