document.addEventListener("DOMContentLoaded", () => {
    const scrollableContainer = document.querySelector('.project-scrollable');
    const items = document.querySelectorAll('.in-progress-item');

    const handleScroll = () => {
        const containerTop = scrollableContainer.scrollTop;
        const containerHeight = scrollableContainer.offsetHeight;
        const scrollHeight = scrollableContainer.scrollHeight;

        const firstItem = items[0];
        const firstItemTop = firstItem.offsetTop - containerTop;
        const firstItemBottom = firstItemTop + firstItem.offsetHeight;

        const lastItem = items[items.length - 1];
        const lastItemTop = lastItem.offsetTop - containerTop;
        const lastItemBottom = lastItemTop + lastItem.offsetHeight;

        if (firstItemBottom > 0 && firstItemTop < containerHeight) {

            firstItem.classList.remove('fade');
        } else {
            firstItem.classList.add('fade');
        }

        if (lastItemTop < containerHeight && lastItemBottom > containerHeight) {

            lastItem.classList.remove('fade');
        } else {
            lastItem.classList.add('fade');
        }

        items.forEach(item => {
            const itemTop = item.offsetTop - containerTop;
            const itemBottom = itemTop + item.offsetHeight;

            if (itemTop >= 0 && itemBottom <= containerHeight) {
                item.classList.remove('fade');
            } else {
                item.classList.add('fade');
            }
        });
    };

    scrollableContainer.addEventListener('scroll', handleScroll);
    handleScroll(); 
});