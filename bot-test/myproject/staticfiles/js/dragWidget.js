document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.widgets');
    const homeContainer = document.querySelector('.home-container');

    const sortable = new Sortable(container, {
        animation: 150,
        ghostClass: 'ghost',
        chosenClass: 'chosen',
        dragClass: 'dragging',
        restrict: 'parent', // Ogranicza przeciąganie do rodzica
        onStart: function (evt) {
            // Ukrywamy przeciągany widget
            const widget = evt.item;
            widget.style.opacity = 0;
        },
        onEnd: function (evt) {
            // Po zakończeniu przeciągania przywracamy widget
            const widget = evt.item;
            widget.style.opacity = 1;
            updateOrder(container); // Zaktualizuj kolejność po zakończeniu przeciągania
        },
        onMove: function (evt) {
            // Możesz dodać dodatkową logikę, jeśli chcesz
        }
    });

    // Obsługa usuwania widgetów
    const deleteButtons = document.querySelectorAll('.delete-widget');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const widgetToDelete = event.target.closest('.widget'); // Wybieramy widget do usunięcia
            if (widgetToDelete) {
                const parent = widgetToDelete.parentElement;

                // Usuwamy widget z DOM
                widgetToDelete.remove();

                // Pozwalamy na ponowne rozmieszczenie widgetów
                const widgets = parent.querySelectorAll('.widget');
                widgets.forEach((widget, index) => {
                    widget.style.order = index; // Przywracamy porządek
                });

                // Zaktualizuj kolejność po usunięciu widgetu
                updateOrder(container);
            }
        });
    });

    // Funkcja do aktualizowania kolejności widgetów
    function updateOrder(container) {
        const order = [];
        container.querySelectorAll('.widget').forEach((widget, index) => {
            order.push({ id: widget.id, position: index + 1 });
        });
        console.log('Nowa kolejność:', order);
    }
});
