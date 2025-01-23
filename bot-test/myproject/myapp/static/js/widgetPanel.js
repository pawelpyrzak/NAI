document.addEventListener('DOMContentLoaded', function () {
    const addWidgetButton = document.querySelector('.more-widgets'); 
    const widgetPanel = document.querySelector('.widget-panel'); 
    const layout = document.querySelector('.layout'); 
    const closeButton = document.querySelector('.close-panel'); 

    if (!addWidgetButton || !widgetPanel || !layout || !closeButton) {
        console.error('Brak wymaganych elementów: .more-widgets, .widget-panel, .layout, .close-panel');
        return;
    }

    function openWidgetPanel() {
        widgetPanel.classList.add('active'); 
        layout.classList.add('widgets-active'); 
    }

    function closeWidgetPanel() {
        widgetPanel.classList.remove('active'); 
        layout.classList.remove('widgets-active'); 
    }

    addWidgetButton.addEventListener('click', openWidgetPanel);

    closeButton.addEventListener('click', closeWidgetPanel);

    layout.addEventListener('click', function (e) {
        if (!widgetPanel.contains(e.target) && !addWidgetButton.contains(e.target)) {
            closeWidgetPanel();
        }
    });

    widgetPanel.addEventListener('click', function (e) {
        e.stopPropagation(); 
    });
});