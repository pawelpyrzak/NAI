document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.project-nav a');
    const contentDiv = document.querySelector('.projects-content');

    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const page = link.getAttribute('data-page');  

            console.log("Kliknięto w: " + page);  

            loadContent(page);
        });
    });

    function loadContent(page) {
        console.log("Ładowanie treści dla: " + page);  

        let url = '';  

        if (page === 'tablica') {
            url = '/projects/board';  
        } else if (page === 'lista') {
            url = '/projects/lista';  
        } else if (page === 'kalendarz') {
            url = '/projects/kalendarz';  
        }

        fetch(url)
            .then(response => response.text())
            .then(data => {
                contentDiv.innerHTML = data;  
            })
            .catch(error => {
                console.error('Błąd ładowania treści:', error);
            });
    }
});