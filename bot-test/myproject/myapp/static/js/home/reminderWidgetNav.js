document.addEventListener("DOMContentLoaded", function() {
    const todayLink = document.getElementById('today-link');
    const tomorrowLink = document.getElementById('tomorrow-link');
    const weekLink = document.getElementById('week-link');
    const allLink = document.getElementById('all-link');

    const reminderContent = document.getElementById('reminder-content');

    function changeContent(view) {
        fetch(`/load-reminder-content/${view}/`)
            .then(response => response.json())
            .then(data => {
                reminderContent.innerHTML = data.html; 
            })
            .catch(error => {
                console.error('Error loading content:', error);
            });

        document.querySelectorAll('.reminder-nav a').forEach(link => link.classList.remove('active'));

        document.getElementById(view + '-link').classList.add('active');
    }

    changeContent('today');

    todayLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('today');
    });

    tomorrowLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('tomorrow');
    });

    weekLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('week');
    });

    allLink.addEventListener('click', function(event) {
        event.preventDefault();
        changeContent('all');
    });
});