document.addEventListener('DOMContentLoaded', function() {

    const iconContainers = document.querySelectorAll('.calendar-options, .projects-options, .tasks-options, .reminder-options');

    iconContainers.forEach(function(iconContainer) {

        const optionsIcon = iconContainer.querySelector('img');
        const optionsMenu = iconContainer.querySelector('.hidden');
        const resizeSmallButton = iconContainer.querySelector('.resize-small');
        const resizeFullButton = iconContainer.querySelector('.resize-full');
        const section = iconContainer.closest('.calendar, .projects, .tasks, .reminder');

        optionsIcon.addEventListener('click', function(event) {
            optionsMenu.classList.toggle('hidden');
            event.stopPropagation(); 
        });

        document.addEventListener('click', function(event) {
            if (!menu.contains(event.target) && event.target !== icon) {
                menu.classList.add('hidden'); 
            }
        });

        const options = iconContainer.querySelectorAll('.resize-option');
        options.forEach(function(option) {
            option.addEventListener('click', function() {
                menu.classList.add('hidden');
            });
        });

        if (resizeSmallButton) {
            resizeSmallButton.addEventListener('click', function() {
                section.classList.remove('full');
                section.classList.add('small');
            });
        }

        if (resizeFullButton) {
            resizeFullButton.addEventListener('click', function() {
                section.classList.remove('small');
                section.classList.add('full');
            });
        }
    });
});