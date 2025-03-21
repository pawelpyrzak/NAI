document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.widgets');

    const sortable = new Sortable(container, {
        animation: 150,
        ghostClass: 'ghost',
        chosenClass: 'chosen',
        dragClass: 'dragging',
        fallbackOnBody: false,
        forceFallback: true,
        onStart: function (evt) {
            const widget = evt.item;
            widget.style.opacity = 0;
        },
        onEnd: function (evt) {
            const widget = evt.item;
            widget.style.opacity = 1;
            updateOrder(container);
        },
        onMove: function (evt) {
            // opcjonalnie...
        }
    });


    // Inne funkcjonalności, np. automatyczne przewijanie
    const scrollSpeed = 20;
    document.addEventListener('mousemove', (e) => {
        const mouseY = e.clientY;
        const halfWindowHeight = window.innerHeight / 10;
        if (mouseY < halfWindowHeight) {
            window.scrollBy(0, -scrollSpeed);
        } else if (mouseY > halfWindowHeight) {
            window.scrollBy(0, scrollSpeed);
        }
    });
});
 function updateOrder(container) {
        const order = [];
        container.querySelectorAll('.widget').forEach((widget, index) => {
            // Jeżeli widget jest ukryty (np. po usunięciu), ustawiamy pozycję na 0
            const pos = (widget.style.display === "none") ? 0 : index + 1;
            const size = getWidgetSize(widget);
            console.log(size);
            order.push({ id: widget.id, position: pos, size: size });
        });
        console.log('Nowa kolejność:', order);
        fetch('/update-widget-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ order: order })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Dane zostały zaktualizowane:', data);
        })
        .catch(error => {
            console.error('Błąd podczas wysyłania danych:', error);
        });
    }
