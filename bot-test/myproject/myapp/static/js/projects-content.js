document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.project-nav a');
    const contentDiv = document.querySelector('.projects-content');

    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const page = link.getAttribute('data-page');  // Pobierz atrybut data-page

            console.log("Kliknięto w: " + page);  // Dodaj logowanie

            loadContent(page);
        });
    });

    function loadContent(page) {
        console.log("Ładowanie treści dla: " + page);  // Dodaj logowanie

        let url = '';  // Zmienna do przechowywania URL

        if (page === 'tablica') {
            url = '/projects/board';  // URL dla Tablica
        } else if (page === 'lista') {
            url = '/projects/lista';  // Dodaj URL dla Lista
        } else if (page === 'kalendarz') {
            url = '/projects/kalendarz';  // Dodaj URL dla Kalendarz
        }

        // Wykonaj żądanie fetch dla dynamicznego ładowania treści
        fetch(url)
            .then(response => response.text())
            .then(data => {
                contentDiv.innerHTML = data;  // Załaduj treść do div .projects-content
            })
            .catch(error => {
                console.error('Błąd ładowania treści:', error);
            });
    }
});
