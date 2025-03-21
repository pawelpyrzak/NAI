document.addEventListener("DOMContentLoaded", function () {
    const statisticsOptionsSelect = document.getElementById("statistics-options-select");
    const completedTasksElement = document.querySelector(".completed-tasks .quantity-of-tasks h2");
    const toDoTasksElement = document.querySelector(".to-do .quantity-of-tasks h2");

    function loadStatistics(period) {
        fetch(`/load-user-statistics/?period=${period}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                completedTasksElement.textContent = data.completed_tasks;
                toDoTasksElement.textContent = data.to_do_tasks;
            })
            .catch(error => {
                console.error("Błąd podczas ładowania statystyk:", error);
                completedTasksElement.textContent = "-";
                toDoTasksElement.textContent = "-";
            });
    }

    statisticsOptionsSelect.addEventListener("change", function () {
        const selectedPeriod = this.value;
        completedTasksElement.textContent = "Ładowanie...";
        toDoTasksElement.textContent = "Ładowanie...";
        loadStatistics(selectedPeriod);
    });

    loadStatistics('today');
});
