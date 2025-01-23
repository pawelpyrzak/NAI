document.addEventListener('DOMContentLoaded', function() {
    // Pobieramy wszystkie elementy, które mają opcje
    const iconContainers = document.querySelectorAll('.calendar-options, .projects-options, .tasks-options, .reminder-options');

    iconContainers.forEach(function(iconContainer) {
        // Pobieramy elementy specyficzne dla danej sekcji
        const optionsIcon = iconContainer.querySelector('img');
        const optionsMenu = iconContainer.querySelector('.hidden');
        const resizeSmallButton = iconContainer.querySelector('.resize-small');
        const resizeFullButton = iconContainer.querySelector('.resize-full');
        const section = iconContainer.closest('.calendar, .projects, .tasks, .reminder');

        // Funkcja do wyświetlania menu
        optionsIcon.addEventListener('click', function(event) {
            optionsMenu.classList.toggle('hidden');
            event.stopPropagation(); // Zapobiega zamknięciu menu po kliknięciu na ikonę
        });

        // Zamknięcie menu po kliknięciu gdziekolwiek poza menu i ikoną
        document.addEventListener('click', function(event) {
            if (!menu.contains(event.target) && event.target !== icon) {
                menu.classList.add('hidden'); // Ukrywa menu, jeśli klikniesz poza nie
            }
        });

        // Zamknięcie menu po kliknięciu jednej z opcji
        const options = iconContainer.querySelectorAll('.resize-option');
        options.forEach(function(option) {
            option.addEventListener('click', function() {
                menu.classList.add('hidden');
            });
        });

        // Funkcja do zmniejszania sekcji
        if (resizeSmallButton) {
            resizeSmallButton.addEventListener('click', function() {
                section.classList.remove('full');
                section.classList.add('small');
            });
        }

        // Funkcja do powiększania sekcji
        if (resizeFullButton) {
            resizeFullButton.addEventListener('click', function() {
                section.classList.remove('small');
                section.classList.add('full');
            });
        }
    });
});
