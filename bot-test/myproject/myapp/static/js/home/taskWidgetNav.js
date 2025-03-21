document.addEventListener("DOMContentLoaded", function() {

    const toDoLink = document.getElementById('to-do');
    const inProgressLink = document.getElementById('in-progress');
    const overdueLink = document.getElementById('overdue');
    const completedLink = document.getElementById('completed');

    const taskContent = document.getElementById('task-content');

    const createReminderModal = document.getElementById('createReminderModal');
    const closeModalButton = document.getElementById('close-modal');
    const openModalButton = document.querySelector('.create-reminder-container');

    function changeContent(view) {
        fetch(`/load-task-content/${view}/`)
            .then(response => response.json())
            .then(data => {
                taskContent.innerHTML = data.html; 
            })
            .catch(error => {
                console.error('Error loading content:', error);
            });

        document.querySelectorAll('.task-nav a').forEach(link => link.classList.remove('active'));

        document.getElementById(view).classList.add('active');
    }

    changeContent('to-do');

    toDoLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('to-do');
    });

    inProgressLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('in-progress');
    });

    overdueLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('overdue');
    });

    completedLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('completed');
    });

    if (openModalButton && createReminderModal && closeModalButton) {
        openModalButton.addEventListener('click', function() {
            createReminderModal.style.display = 'block';  
        });

        closeModalButton.addEventListener('click', function() {
            createReminderModal.style.display = 'none';  
        });

        window.addEventListener('click', function(event) {
            if (event.target === createReminderModal) {
                createReminderModal.style.display = 'none';  
            }
        });
    } else {
        console.error('Nie znaleziono wymaganych elementów w DOM dla modala');
    }
});