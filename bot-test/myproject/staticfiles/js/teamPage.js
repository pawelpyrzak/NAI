document.addEventListener("DOMContentLoaded", function () {
    const postsTab = document.getElementById("posts-tab");
    const filesTab = document.getElementById("files-tab");
    const dynamicContent = document.getElementById("dynamic-content");

    // Funkcja do załadowania nowej zawartości
    function loadContent(url) {
        fetch(url)
            .then(response => response.text())
            .then(html => {
                dynamicContent.innerHTML = html;
            })
            .catch(error => console.error('Błąd podczas ładowania treści:', error));
    }

    // Obsługa kliknięć w zakładki
    postsTab.addEventListener("click", function () {
        loadContent('/wpisy/'); // Ustaw ścieżkę do widoku Django
        postsTab.classList.add("active");
        filesTab.classList.remove("active");
    });

    filesTab.addEventListener("click", function () {
        loadContent('/pliki/'); // Ustaw ścieżkę do widoku Django
        filesTab.classList.add("active");
        postsTab.classList.remove("active");
    });
});
