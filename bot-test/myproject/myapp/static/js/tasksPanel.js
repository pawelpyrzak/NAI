document.addEventListener('DOMContentLoaded', function () {
    console.log('Strona załadowana, inicjalizacja...');

    const items = document.querySelectorAll('.today-item, .tommorow-item, .this-week-item, .overdue-item');
    const detailsPanel = document.querySelector('.details-panel');
    const layout = document.querySelector('.layout');
    const closeButton = document.querySelector('.close-panel');

    let activeItem = null;

    if (!detailsPanel || !layout || !closeButton || !items.length) {
        console.error('Brak wymaganych elementów: .today-item, .tommorow-item, .this-week-item, .overdue-item');
        return;
    }

    function populateDetailsPanel(taskData) {
        detailsPanel.querySelector('.start-date p').textContent = taskData.startDate;
        detailsPanel.querySelector('.deadline p').textContent = taskData.deadline;
        detailsPanel.querySelector('.task-status p').textContent = taskData.status;
        detailsPanel.querySelector('.priority p').textContent = taskData.priority;
        if (taskData.daysLeft < 0) {
            let day = taskData.daysLeft * (-1)
            detailsPanel.querySelector('.days-left h2').textContent = "Opóźnienie";
            detailsPanel.querySelector('.days-left p').textContent = day + " dni";
        } else {
            detailsPanel.querySelector('.days-left h2').textContent = "Pozostało dni";
            detailsPanel.querySelector('.days-left p').textContent = taskData.daysLeft + " dni";
        }
        const managerContainer = detailsPanel.querySelector('.pm-avatar');
        managerContainer.innerHTML = '';
        detailsPanel.querySelector('.pm-details h2').textContent = taskData.managerName;
        const img = document.createElement('img');
        img.src = taskData.managerImg;
        img.alt = "img"
        detailsPanel.querySelector('.task-url-button').addEventListener('click', function () {
            window.location.href = taskData.task_url;
        });
        managerContainer.appendChild(img);
    }

    function openDetailsPanel(item) {
        console.log('Kliknięto element');
        detailsPanel.classList.add('active');
        layout.classList.add('details-active');
        const taskData = item.dataset;

        populateDetailsPanel({
            startDate: taskData.startDate || 'Brak daty',
            deadline: taskData.deadline || 'Brak terminu',
            status: taskData.status || 'Brak statusu',
            priority: taskData.priority || 'Brak priorytetu',
            daysLeft: taskData.daysLeft || 'Nieokreślone',
            managerName: taskData.managerName || 'Menadżer',
            managerImg: taskData.managerImg || "../static/images/person1.jpg",
            task_url: taskData.task_url,

        });


        if (activeItem) {
            activeItem.classList.remove('selected');
        }


        activeItem = item;
        activeItem.classList.add('selected');

        console.log('Panel został otwarty, element zaznaczony');
    }

    function closeDetailsPanel() {
        console.log('Kliknięto przycisk zamknięcia panelu');
        detailsPanel.classList.remove('active');
        layout.classList.remove('details-active');

        if (activeItem) {
            activeItem.classList.remove('selected');
            activeItem = null;
        }

        console.log('Panel został zamknięty, element odznaczony');
    }

    items.forEach(item => {
        item.addEventListener('click', function () {
            openDetailsPanel(item);
        });
    });

    closeButton.addEventListener('click', closeDetailsPanel);

    layout.addEventListener('click', function (e) {
        if (!detailsPanel.contains(e.target) && !e.target.closest('.today-item') && !e.target.closest('.this-week-item') && !e.target.closest('.overdue-item') && !e.target.closest('.tommorow-item')) {
            closeDetailsPanel();
        }
    });

    detailsPanel.addEventListener('click', function (e) {
        e.stopPropagation();
    });
});
