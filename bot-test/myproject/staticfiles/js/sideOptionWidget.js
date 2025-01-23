document.addEventListener("DOMContentLoaded", function () {
    // Pobieramy wszystkie elementy menu
    const allMenus = document.querySelectorAll(".hidden");

    // Funkcja do zamknięcia wszystkich menu
    function closeAllMenus() {
        allMenus.forEach(function (menu) {
            menu.classList.add("hidden");
        });
    }

    // Obsługuje otwieranie/zamykanie menu przypomnień
    const reminderIcon = document.getElementById("reminder-options-icon");
    const reminderMenu = document.getElementById("reminder-options-menu");
    const reminderResizeSmall = document.getElementById("reminder-resize-small");
    const reminderResizeFull = document.getElementById("reminder-resize-full");
    const reminder = document.querySelector(".reminder");

    reminderIcon.addEventListener("click", function (event) {
        closeAllMenus(); // Zamykamy wszystkie menu przed otwarciem nowego
        reminderMenu.classList.toggle("hidden");
        event.stopPropagation();
    });

    // Funkcja do zamknięcia menu po kliknięciu w opcję
    function closeMenuOnOptionClick(menu) {
        menu.classList.add("hidden");
    }

    // Funkcje do zmiany rozmiaru sekcji
    reminderResizeSmall.addEventListener("click", function () {
        reminder.classList.remove("full");
        reminder.classList.add("small");
        closeMenuOnOptionClick(reminderMenu);
    });

    reminderResizeFull.addEventListener("click", function () {
        reminder.classList.remove("small");
        reminder.classList.add("full");
        closeMenuOnOptionClick(reminderMenu);
    });

    // Zamknięcie menu po kliknięciu poza nie
    document.addEventListener("click", function (event) {
        if (!reminderMenu.contains(event.target) && event.target !== reminderIcon) {
            reminderMenu.classList.add("hidden");
        }
    });

    // Obsługuje otwieranie/zamykanie menu dla innych sekcji (np. dla kalendarza, projektów, zadań)
    const iconContainers = document.querySelectorAll(".calendar-options, .projects-options, .tasks-options");

    iconContainers.forEach(function (iconContainer) {
        const menu = iconContainer.querySelector(".hidden");
        const icon = iconContainer.querySelector("img");
        const resizeSmallButton = iconContainer.querySelector(".resize-option");
        const resizeFullButton = iconContainer.querySelector(".resize-option");

        icon.addEventListener("click", function (event) {
            closeAllMenus(); // Zamykamy wszystkie menu przed otwarciem nowego
            menu.classList.toggle("hidden");
            event.stopPropagation();
        });

        // Funkcje do zmiany rozmiaru sekcji (kalendarza, projektów, zadań)
        if (resizeSmallButton) {
            resizeSmallButton.addEventListener("click", function () {
                iconContainer.closest(".calendar, .projects, .tasks").classList.remove("full");
                iconContainer.closest(".calendar, .projects, .tasks").classList.add("small");
                closeMenuOnOptionClick(menu);
            });
        }

        if (resizeFullButton) {
            resizeFullButton.addEventListener("click", function () {
                iconContainer.closest(".calendar, .projects, .tasks").classList.remove("small");
                iconContainer.closest(".calendar, .projects, .tasks").classList.add("full");
                closeMenuOnOptionClick(menu);
            });
        }

        // Zamknięcie menu po kliknięciu poza nim
        document.addEventListener("click", function (event) {
            if (!menu.contains(event.target) && event.target !== icon) {
                menu.classList.add("hidden");
            }
        });
    });

    // Kalendarz
    const calendarIcon = document.getElementById("calendar-options-icon");
    const calendarMenu = document.getElementById("calendar-options-menu");
    const calendarResizeSmall = document.getElementById("calendar-resize-small");
    const calendarResizeFull = document.getElementById("calendar-resize-full");
    const calendar = document.querySelector(".calendar");
    const fullContent = document.querySelector(".calendar.full-content");

    calendarIcon.addEventListener("click", function () {
        closeAllMenus(); // Zamykamy wszystkie menu przed otwarciem nowego
        calendarMenu.classList.toggle("hidden");
    });

    calendarResizeSmall.addEventListener("click", function () {
        calendar.classList.remove("full");
        calendar.classList.add("small");
        fullContent.classList.add("hidden");
        closeMenuOnOptionClick(calendarMenu);
    });

    calendarResizeFull.addEventListener("click", function () {
        calendar.classList.remove("small");
        calendar.classList.add("full");
        fullContent.classList.remove("hidden");
        closeMenuOnOptionClick(calendarMenu);
    });

    // Projekty
    const projectsIcon = document.getElementById("projects-options-icon");
    const projectsMenu = document.getElementById("projects-options-menu");
    const projectsResizeSmall = document.getElementById("projects-resize-small");
    const projectsResizeFull = document.getElementById("projects-resize-full");
    const projects = document.querySelector(".projects");

    projectsIcon.addEventListener("click", function () {
        closeAllMenus(); // Zamykamy wszystkie menu przed otwarciem nowego
        projectsMenu.classList.toggle("hidden");
    });

    projectsResizeSmall.addEventListener("click", function () {
        projects.classList.remove("full");
        projects.classList.add("small");
        closeMenuOnOptionClick(projectsMenu);
    });

    projectsResizeFull.addEventListener("click", function () {
        projects.classList.remove("small");
        projects.classList.add("full");
        closeMenuOnOptionClick(projectsMenu);
    });

    // Zadania
    const tasksIcon = document.getElementById("tasks-options-icon");
    const tasksMenu = document.getElementById("tasks-options-menu");
    const tasksResizeSmall = document.getElementById("tasks-resize-small");
    const tasksResizeFull = document.getElementById("tasks-resize-full");
    const tasks = document.querySelector(".tasks");

    tasksIcon.addEventListener("click", function () {
        closeAllMenus(); // Zamykamy wszystkie menu przed otwarciem nowego
        tasksMenu.classList.toggle("hidden");
    });

    tasksResizeSmall.addEventListener("click", function () {
        tasks.classList.remove("full");
        tasks.classList.add("small");
        closeMenuOnOptionClick(tasksMenu);
    });

    tasksResizeFull.addEventListener("click", function () {
        tasks.classList.remove("small");
        tasks.classList.add("full");
        closeMenuOnOptionClick(tasksMenu);
    });

});
