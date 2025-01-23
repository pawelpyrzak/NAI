document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('createReminderModal');
    const closeModalButton = document.getElementById('close-modal');

    if (modal && closeModalButton) {
        // Delegacja zdarzeń dla dynamicznie dodanych elementów
        document.addEventListener('click', function(event) {
            // Otwieranie modala po kliknięciu w przycisk
            if (event.target.closest('.create-reminder-container')) {
                modal.style.display = 'block';
            }

            // Zamknięcie modala po kliknięciu w przycisk zamykania lub poza modalem
            if (event.target === closeModalButton || event.target === modal) {
                modal.style.display = 'none';
            }
        });
    } else {
        console.error('Nie znaleziono wymaganych elementów w DOM');
    }
});
