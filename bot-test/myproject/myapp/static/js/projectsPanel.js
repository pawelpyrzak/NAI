document.addEventListener('DOMContentLoaded', function () {
    console.log('Strona załadowana, inicjalizacja...');

    const items = document.querySelectorAll('.in-progress-item, .at-risk-item, .completed-item, .pending-item');  
    const detailsPanel = document.querySelector('.details-panel');
    const layout = document.querySelector('.layout');
    const closeButton = document.querySelector('.close-panel');

    let activeItem = null; 

    if (!detailsPanel || !layout || !closeButton || !items.length) {
        console.error('Brak wymaganych elementów: .in-progress-item, .at-risk-item, .completed-item, .pending-item, .details-panel, .layout lub .close-panel');
        return;
    }

    function openDetailsPanel(item) {
        console.log('Kliknięto element');
        detailsPanel.classList.add('active');  
        layout.classList.add('details-active');  

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

        if (!detailsPanel.contains(e.target) && !e.target.closest('.in-progress-item') && !e.target.closest('.at-risk-item') && !e.target.closest('.completed-item') && !e.target.closest('.pending-item')) {
            closeDetailsPanel();
        }
    });

    detailsPanel.addEventListener('click', function (e) {
        e.stopPropagation(); 
    });
});