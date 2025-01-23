document.addEventListener("DOMContentLoaded", function () {
    const postsTab = document.getElementById("posts-tab");
    const filesTab = document.getElementById("files-tab");
    const dynamicContent = document.getElementById("dynamic-content");

    function loadContent(url) {
        fetch(url)
            .then(response => response.text())
            .then(html => {
                dynamicContent.innerHTML = html;
            })
            .catch(error => console.error('Błąd podczas ładowania treści:', error));
    }

    postsTab.addEventListener("click", function () {
        loadContent('/wpisy/'); 
        postsTab.classList.add("active");
        filesTab.classList.remove("active");
    });

    filesTab.addEventListener("click", function () {
        loadContent('/pliki/'); 
        filesTab.classList.add("active");
        postsTab.classList.remove("active");
    });
});