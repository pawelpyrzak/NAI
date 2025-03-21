document.addEventListener("DOMContentLoaded", () => {
    const scrollableContainer = document.querySelector('.project-scrollable');
    const items = document.querySelectorAll('.in-progress-item');

    const handleScroll = () => {
        const containerTop = scrollableContainer.scrollTop;
        const containerHeight = scrollableContainer.offsetHeight;
        const scrollHeight = scrollableContainer.scrollHeight;

        // Sprawdzanie widoczności pierwszego elementu
        const firstItem = items[0];
        const firstItemTop = firstItem.offsetTop - containerTop;
        const firstItemBottom = firstItemTop + firstItem.offsetHeight;

        // Sprawdzanie widoczności ostatniego elementu
        const lastItem = items[items.length - 1];
        const lastItemTop = lastItem.offsetTop - containerTop;
        const lastItemBottom = lastItemTop + lastItem.offsetHeight;

        // Zanikanie pierwszego widocznego elementu
        if (firstItemBottom > 0 && firstItemTop < containerHeight) {
            // Pierwszy element powinien zniknąć, gdy pasek jest w dół
            firstItem.classList.remove('fade');
        } else {
            firstItem.classList.add('fade');
        }

        // Zanikanie ostatniego widocznego elementu
        if (lastItemTop < containerHeight && lastItemBottom > containerHeight) {
            // Ostatni element powinien zniknąć, gdy pasek jest na górze
            lastItem.classList.remove('fade');
        } else {
            lastItem.classList.add('fade');
        }

        // Dla każdego elementu w kontenerze, sprawdzamy, czy jest widoczny
        items.forEach(item => {
            const itemTop = item.offsetTop - containerTop;
            const itemBottom = itemTop + item.offsetHeight;

            // Jeśli element jest w pełni widoczny, usuń efekt fade
            if (itemTop >= 0 && itemBottom <= containerHeight) {
                item.classList.remove('fade');
            } else {
                item.classList.add('fade');
            }
        });
    };

    scrollableContainer.addEventListener('scroll', handleScroll);
    handleScroll(); // Inicjalizacja
});
