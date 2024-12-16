document.addEventListener("DOMContentLoaded", function () {
    const calendarBody = document.getElementById("calendar-body");
    const calendarTitle = document.getElementById("calendar-title");
    const currentUser = document.getElementById("current-user").value;

    let currentDate = new Date();

    // Funkcja do pobierania zadań
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

    // Funkcja renderowania kalendarza
    async function renderCalendar(date) {
        // Wyczyść istniejącą zawartość
        calendarBody.innerHTML = "";

        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDayOfWeek = new Date(year, month, 1).getDay() || 7; // Pierwszy dzień miesiąca (1 = poniedziałek)
        const daysInMonth = new Date(year, month + 1, 0).getDate(); // Ilość dni w miesiącu
        const daysInPrevMonth = new Date(year, month, 0).getDate(); // Ilość dni w poprzednim miesiącu
        const rows = 6; // Zawsze 6 rzędów w kalendarzu
        let currentDay = 1;

        // Pobieramy zadania z API
        const tasks = await fetchTasks();

        const userTasks = tasks.filter(task => task.assignee && task.assignee.toLowerCase() === currentUser.toLowerCase());

        // Ustawienie tytułu miesiąca i roku
        calendarTitle.textContent = `${getMonthName(month)} ${year}`;

        for (let i = 0; i < rows; i++) {
            const row = document.createElement("tr");

            for (let j = 1; j <= 7; j++) {
                const cell = document.createElement("td");

                if (i === 0 && j < firstDayOfWeek) {
                    const prevMonthDay = daysInPrevMonth - (firstDayOfWeek - j) + 1;
                    cell.textContent = prevMonthDay;
                    cell.classList.add("empty", "other-month");
                } else if (currentDay <= daysInMonth) {
                    cell.textContent = currentDay;
                    cell.classList.add("day");

                    // Sprawdź, czy są zadania dla tego dnia
                    const currentDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(currentDay).padStart(2, "0")}`;
                    const dayTasks = userTasks.filter(task => {
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

                            // Ustawienie koloru na podstawie ID lub tytułu zadania
                            taskDiv.style.backgroundColor = getTaskColor(task.title); // Możesz użyć task.id, jeśli dostępne
                            taskDiv.style.color = "#fff"; // Ustawienie białego tekstu dla kontrastu

                            cell.appendChild(taskDiv);
                        });
                    }


                    currentDay++;
                } else {
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


    // Zwraca nazwę miesiąca na podstawie indeksu
    function getMonthName(monthIndex) {
        const months = [
            "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
            "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
        ];
        return months[monthIndex];
    }

    // Zmienia miesiąc i renderuje kalendarz
    function changeMonth(direction) {
        currentDate.setMonth(currentDate.getMonth() + direction);
        renderCalendar(currentDate);
    }

    // Przechodzi do obecnego miesiąca
    function goToCurrentMonth() {
        currentDate = new Date();
        renderCalendar(currentDate);
    }

    function getTaskColor(taskId) {
        const hash = Array.from(taskId)
            .reduce((acc, char) => acc + char.charCodeAt(0), 0); // Sumowanie kodów ASCII znaków
        let hue = hash % 360;

        // Wykluczenie zieleni (90–150 stopni w HSL)
        if (hue >= 90 && hue <= 150) {
            hue = (hue + 60) % 360; // Przesuwamy na inny zakres
        }

        return `hsl(${hue}, 70%, 60%)`; // Generowanie koloru w formacie HSL
    }

    // Dodajemy funkcjonalności do przycisków
    document.getElementById("btn-prev").addEventListener("click", () => changeMonth(-1));
    document.getElementById("btn-next").addEventListener("click", () => changeMonth(1));
    document.getElementById("btn-today").addEventListener("click", goToCurrentMonth);

    // Pierwsze renderowanie kalendarza
    renderCalendar(currentDate);
});
