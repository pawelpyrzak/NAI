const currentYear = [[${year}]];
const currentMonth = [[${month}]];

function navigate(offset) {
    let month = currentMonth + offset;
    let year = currentYear;

    if (month < 1) {
        month = 12;
        year -= 1;
    } else if (month > 12) {
        month = 1;
        year += 1;
    }

    window.location.href = `/calendar?year=${year}&month=${month}`;
}

function navigateToCurrent() {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;

    window.location.href = `/calendar?year=${year}&month=${month}`;
}

function navigateToSelectedDate() {
    const selectedDate = document.getElementById('datePicker').value;
    if (selectedDate) {
        const [year, month] = selectedDate.split('-');
        window.location.href = `/calendar?year=${year}&month=${month}`;
    }
}
function openPopup(element) {
    document.getElementById('popup-task-name').textContent = element.getAttribute('data-task-name');
    document.getElementById('popup-task-description').textContent = element.getAttribute('data-task-description');
    document.getElementById('popup-task-date').textContent = element.getAttribute('data-task-date');
    document.getElementById('popup-task-status').textContent = element.getAttribute('data-task-status');
    document.getElementById('popup-task-user').textContent = element.getAttribute('data-task-user');
    document.getElementById('popup-task-priority').textContent = element.getAttribute('data-task-priority');


    // Show popup
    document.getElementById('popup').style.display = 'block';
}

function closePopup() {
    // Hide popup
    document.getElementById('popup').style.display = 'none';
}