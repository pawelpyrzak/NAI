document.addEventListener('DOMContentLoaded', function () {
    console.log('Strona załadowana, inicjalizacja...');

    // Pobranie elementów
    const items = document.querySelectorAll('.in-progress-item, .at-risk-item, .completed-item, .pending-item');  // Dodano .pending-item
    const detailsPanel = document.querySelector('.details-panel');
    const layout = document.querySelector('.layout');
    const closeButton = document.querySelector('.close-panel');

    let activeItem = null; // Przechowywanie aktualnie wybranego elementu

    // Weryfikacja obecności elementów
    if (!detailsPanel || !layout || !closeButton || !items.length) {
        console.error('Brak wymaganych elementów: .in-progress-item, .at-risk-item, .completed-item, .pending-item, .details-panel, .layout lub .close-panel');
        return;
    }

    function populateDetailsPanel(projectData) {
        detailsPanel.querySelector('.start-date p').textContent = projectData.startDate;
        detailsPanel.querySelector('.deadline p').textContent = projectData.deadline;
        detailsPanel.querySelector('.project-status p').textContent = projectData.status;
        detailsPanel.querySelector('.priority p').textContent = projectData.priority;
        detailsPanel.querySelector('.days-left p').textContent = projectData.daysLeft + " dni";
        detailsPanel.querySelector('.progress-info p').textContent = projectData.progres + "%";
        detailsPanel.querySelector('.created-tasks p').textContent = projectData.createdTasks;
        detailsPanel.querySelector('.completed-tasks p').textContent = projectData.completedTasks;
        detailsPanel.querySelector('.tasks-in-progress p').textContent = projectData.taskInProgress;
        console.log(projectData.project_url);
        detailsPanel.querySelector('.upcoming-tasks p').textContent = projectData.upcomingTasks;
        if (projectData.daysLeft < 0) {
            let day = projectData.daysLeft * (-1)
            detailsPanel.querySelector('.days-left h2').textContent = "Opóźnienie";
            detailsPanel.querySelector('.days-left p').textContent = day + " dni";
        } else {
            detailsPanel.querySelector('.days-left h2').textContent = "Pozostało dni";
            detailsPanel.querySelector('.days-left p').textContent = projectData.daysLeft + " dni";
        }

        var progressBar = document.getElementById('progress-bar');
        var progressWidth = Math.min(100, projectData.progress);
        progressBar.style.width = progressWidth + '%';

        const managerContainer = detailsPanel.querySelector('.pm-avatar');
        managerContainer.innerHTML = '';
        detailsPanel.querySelector('.pm-details h2').textContent = projectData.managerName;
        const img = document.createElement('img');
        img.src = projectData.managerImg;
        img.alt = "img"
        detailsPanel.querySelector('.project-url-button').addEventListener('click', function () {
            window.location.href = projectData.project_url;
        });

        managerContainer.appendChild(img);
    }

    // Funkcja otwierająca panel
    function openDetailsPanel(item) {
        console.log('Kliknięto element');
        detailsPanel.classList.add('active');  // Pokazanie panelu
        layout.classList.add('details-active');  // Dodanie klasy do layoutu
        const projectData = item.dataset;

        populateDetailsPanel({
            startDate: projectData.startDate || 'Brak daty',
            deadline: projectData.deadline || 'Brak terminu',
            status: projectData.status || 'Brak statusu',
            priority: projectData.priority || 'Brak priorytetu',
            daysLeft: projectData.daysLeft || 'Nieokreślone',
            managerName: projectData.managerName || 'Menadżer',
            managerImg: projectData.managerImg || "{% static 'images/person1.jpg' %}",
            progres: projectData.progres || 0,
            createdTasks: projectData.createdTasks || 0,
            completedTasks: projectData.completedTasks || 0,
            taskInProgress: projectData.taskInProgress || 0,
            upcomingTasks: projectData.upcomingTasks || 0,
            participants: projectData.participants,
            project_url: projectData.project_url,
        });
        // Resetowanie poprzednio wybranego elementu
        if (activeItem) {
            activeItem.classList.remove('selected');
        }

        // Oznaczenie aktualnie wybranego elementu
        activeItem = item;
        activeItem.classList.add('selected');

        console.log('Panel został otwarty, element zaznaczony');
    }

    // Funkcja zamykająca panel
    function closeDetailsPanel() {
        console.log('Kliknięto przycisk zamknięcia panelu');
        detailsPanel.classList.remove('active');  // Ukrycie panelu
        layout.classList.remove('details-active');  // Usunięcie klasy z layoutu

        // Resetowanie zaznaczenia aktywnego elementu
        if (activeItem) {
            activeItem.classList.remove('selected');
            activeItem = null;
        }

        console.log('Panel został zamknięty, element odznaczony');
    }

    // Dodanie nasłuchiwania na każdy element (.in-progress-item, .at-risk-item, .completed-item, .pending-item)
    items.forEach(item => {
        item.addEventListener('click', function () {
            openDetailsPanel(item);
        });
    });

    // Nasłuchiwanie na przycisk zamykający
    closeButton.addEventListener('click', closeDetailsPanel);

    // Nasłuchiwanie na kliknięcie w tło layoutu
    layout.addEventListener('click', function (e) {
        // Jeśli kliknięto poza .details-panel
        if (!detailsPanel.contains(e.target) && !e.target.closest('.in-progress-item') && !e.target.closest('.at-risk-item') && !e.target.closest('.completed-item') && !e.target.closest('.pending-item')) {
            closeDetailsPanel();
        }
    });

    // Zapobieganie zamknięciu panelu, gdy kliknięto w sam panel
    detailsPanel.addEventListener('click', function (e) {
        e.stopPropagation(); // Zatrzymanie propagacji zdarzenia kliknięcia
    });
});
