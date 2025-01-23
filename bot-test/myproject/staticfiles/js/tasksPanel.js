document.addEventListener('DOMContentLoaded', function () {
    console.log('Strona załadowana, inicjalizacja...');

    // Pobranie elementów
    const items = document.querySelectorAll('.today-item, .tommorow-item, .this-week-item, .overdue-item');  // Dodano .pending-item
    const detailsPanel = document.querySelector('.details-panel');
    const layout = document.querySelector('.layout');
    const closeButton = document.querySelector('.close-panel');

    let activeItem = null; // Przechowywanie aktualnie wybranego elementu

    // Weryfikacja obecności elementów
    if (!detailsPanel || !layout || !closeButton || !items.length) {
        console.error('Brak wymaganych elementów: .today-item, .tommorow-item, .this-week-item, .overdue-item');
        return;
    }

    // Funkcja otwierająca panel
    function openDetailsPanel(item) {
        console.log('Kliknięto element');
        detailsPanel.classList.add('active');  // Pokazanie panelu
        layout.classList.add('details-active');  // Dodanie klasy do layoutu

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
        if (!detailsPanel.contains(e.target) && !e.target.closest('.today-item') && !e.target.closest('.this-week-item') && !e.target.closest('.overdue-item') && !e.target.closest('.tommorow-item')) {
            closeDetailsPanel();
        }
    });

    // Zapobieganie zamknięciu panelu, gdy kliknięto w sam panel
    detailsPanel.addEventListener('click', function (e) {
        e.stopPropagation(); // Zatrzymanie propagacji zdarzenia kliknięcia
    });
});
