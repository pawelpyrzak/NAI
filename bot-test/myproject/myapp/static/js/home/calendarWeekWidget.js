document.addEventListener('DOMContentLoaded', function () {
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnToday = document.getElementById('btn-today');
    const calendarDate = document.getElementById('calendar-date');
    const calendarBody = document.getElementById('calendar-body');
    const selectedDay = document.getElementById('selected-day');
    const selectedWeekday = document.getElementById('selected-weekday');
    const selectedMonth = document.getElementById('selected-month');

    let currentDate = new Date();
    let selectedDate = null; 
    let todayElement = null; 

    function formatDate(date) {
        const weekdayOptions = { weekday: 'long' };
        const dayOptions = { day: 'numeric' };
        const monthOptions = { month: 'long' };

        const weekday = date.toLocaleDateString('pl-PL', weekdayOptions); 
        const day = date.toLocaleDateString('pl-PL', dayOptions); 
        const month = date.toLocaleDateString('pl-PL', monthOptions); 

        return { weekday, day, month }; 
    }

    function renderMonth(date) {
        let firstDayOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
        let lastDayOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);

        let startDay = firstDayOfMonth.getDay(); 
        let daysInMonth = lastDayOfMonth.getDate(); 

        let monthDays = [];
        for (let i = 1 - startDay; i <= daysInMonth; i++) {
            let day = new Date(date.getFullYear(), date.getMonth(), i);
            monthDays.push(day);
        }

        let daysHtml = '';
        for (let i = 0; i < monthDays.length; i++) {
            if (i % 7 === 0) {
                daysHtml += '<tr>';
            }

            let isToday = monthDays[i].toDateString() === new Date().toDateString(); 
            let todayClass = isToday ? ' today' : '';

            let isOtherMonth = monthDays[i].getMonth() !== date.getMonth(); 
            let otherMonthClass = isOtherMonth ? ' other-month' : '';

            daysHtml += `<td class="calendar-day${otherMonthClass}" data-date="${monthDays[i].toDateString()}">
                            <span class="day-text${todayClass}">${monthDays[i].getDate()}</span>
                         </td>`;
            if (i % 7 === 6) {
                daysHtml += '</tr>';
            }
        }
        calendarBody.innerHTML = daysHtml;

        calendarDate.textContent = `${date.toLocaleString('default', { month: 'long' })} ${date.getFullYear()}`;

        if (!todayElement) {
            todayElement = document.querySelector('.calendar-day .day-text.today');
        }
    }

    function updateSelectedDate(date) {
        const { weekday, day, month } = formatDate(date);

        selectedDay.textContent = day;
        selectedWeekday.textContent = weekday;
        selectedMonth.textContent = month;
    }

    function selectDate(event) {
        const clickedDate = new Date(event.target.closest('td').getAttribute('data-date')); 

        if (selectedDate && selectedDate.toDateString() === clickedDate.toDateString()) {
            return;
        }

        const previouslySelected = document.querySelector('.day-text.selected');
        if (previouslySelected) {
            previouslySelected.classList.remove('selected');
        }

        event.target.classList.add('selected');
        selectedDate = clickedDate; 

        updateSelectedDate(clickedDate);

        if (todayElement) {
            todayElement.classList.remove('today');
        }

        todayElement = document.querySelector('.calendar-day .day-text.today');
    }

    btnPrev.addEventListener('click', function () {
        currentDate.setMonth(currentDate.getMonth() - 1); 
        renderMonth(new Date(currentDate));
    });

    btnNext.addEventListener('click', function () {
        currentDate.setMonth(currentDate.getMonth() + 1); 
        renderMonth(new Date(currentDate));
    });

    btnToday.addEventListener('click', function () {
        currentDate = new Date(); 
        renderMonth(new Date(currentDate)); 
        updateSelectedDate(currentDate); 

        const previouslySelected = document.querySelector('.day-text.selected');
        if (previouslySelected) {
            previouslySelected.classList.remove('selected');
        }

        const todayCell = document.querySelector('.calendar-day .day-text.today');
        if (todayCell) {
            todayCell.classList.add('selected');
        }

        selectedDate = new Date(); 
    });

    renderMonth(currentDate);
    updateSelectedDate(currentDate); 

    calendarBody.addEventListener('click', function(event) {
        if (event.target.classList.contains('day-text')) {
            selectDate(event); 
        }
    });
});