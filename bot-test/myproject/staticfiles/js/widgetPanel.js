document.addEventListener('DOMContentLoaded', function () {
    const addWidgetButton = document.querySelector('.more-widgets'); // Przycisk Dodaj widget
    const widgetPanel = document.querySelector('.widget-panel'); // Panel widgetów
    const layout = document.querySelector('.layout'); // Layout główny
    const closeButton = document.querySelector('.close-panel'); // Przycisk zamykający panel

    if (!addWidgetButton || !widgetPanel || !layout || !closeButton) {
        console.error('Brak wymaganych elementów: .more-widgets, .widget-panel, .layout, .close-panel');
        return;
    }

    // Otwieranie panelu
    function openWidgetPanel() {
        widgetPanel.classList.add('active'); // Pokazanie panelu
        layout.classList.add('widgets-active'); // Dodanie klasy do layoutu
    }

    // Zamknięcie panelu
    function closeWidgetPanel() {
        widgetPanel.classList.remove('active'); // Ukrycie panelu
        layout.classList.remove('widgets-active'); // Usunięcie klasy z layoutu
    }

    // Nasłuchiwanie na przycisk otwierający
    addWidgetButton.addEventListener('click', openWidgetPanel);

    // Nasłuchiwanie na przycisk zamykający
    closeButton.addEventListener('click', closeWidgetPanel);

    // Opcjonalnie: zamykanie po kliknięciu w tło
    layout.addEventListener('click', function (e) {
        if (!widgetPanel.contains(e.target) && !addWidgetButton.contains(e.target)) {
            closeWidgetPanel();
        }
    });

    widgetPanel.addEventListener('click', function (e) {
        e.stopPropagation(); // Zapobieganie zamknięciu podczas klikania w panel
    });
});
