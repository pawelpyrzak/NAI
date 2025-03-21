document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('reminderDoneModal');
    const closeModalButton = document.getElementById('close-modal');

    if (modal && closeModalButton) {
        document.addEventListener('click', function(event) {
            if (event.target.closest('.reminder-list-container')) {
                modal.style.display = 'block';
            }
            if (event.target === closeModalButton || event.target === modal) {
                modal.style.display = 'none';
            }
        });
    } else {
        console.error('Nie znaleziono wymaganych elementów w DOM');
    }
});
