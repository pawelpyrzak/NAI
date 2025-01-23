document.addEventListener("DOMContentLoaded", function () {
    const calendarBody = document.getElementById("calendar-body");
    const calendarDate = document.getElementById("calendar-date");

    let currentDate = new Date();

    function renderCalendar(date) {
        // Wyczyść istniejącą zawartość
        calendarBody.innerHTML = "";

        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDayOfWeek = new Date(year, month, 1).getDay() || 7; // Pierwszy dzień miesiąca (1 = poniedziałek)
        const daysInMonth = new Date(year, month + 1, 0).getDate(); // Ilość dni w miesiącu
        const daysInPrevMonth = new Date(year, month, 0).getDate(); // Ilość dni w poprzednim miesiącu
        const rows = 6; // Zawsze 6 rzędów w kalendarzu
        let currentDay = 1;

        // Ustawienie tytułu miesiąca i roku
        calendarDate.textContent = `${getMonthName(month)} ${year}`;

        for (let i = 0; i < rows; i++) {
            const row = document.createElement("tr");

            for (let j = 1; j <= 7; j++) {
                const cell = document.createElement("td");

                // Wypełnienie pustych komórek dniami z poprzedniego miesiąca
                if (i === 0 && j < firstDayOfWeek) {
                    const prevMonthDay = daysInPrevMonth - (firstDayOfWeek - j) + 1;
                    cell.textContent = prevMonthDay;
                    cell.classList.add("empty", "other-month");
                }
                // Wypełnienie komórek dniami z bieżącego miesiąca
                else if (currentDay <= daysInMonth) {
                    cell.textContent = currentDay;
                    cell.classList.add("day");
                    currentDay++;
                }
                // Wypełnienie pustych komórek dniami z następnego miesiąca
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

    // Dodajemy funkcjonalności do przycisków
    document.getElementById("btn-prev").addEventListener("click", () => changeMonth(-1));
    document.getElementById("btn-next").addEventListener("click", () => changeMonth(1));
    document.getElementById("btn-today").addEventListener("click", goToCurrentMonth);

    // Pierwsze renderowanie kalendarza
    renderCalendar(currentDate);
});
