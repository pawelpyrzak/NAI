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

        }
    });

    function updateOrder(container) {
        const order = [];
        container.querySelectorAll('.widget').forEach((widget, index) => {
            order.push({ id: widget.id, position: index + 1 });
        });
        console.log('Nowa kolejność:', order);
    }

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