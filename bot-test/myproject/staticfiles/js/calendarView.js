document.addEventListener("DOMContentLoaded", function () {
    const viewSelector = document.getElementById("view-selector");
    const calendarContent = document.querySelector(".calendar-content");

    // Funkcja ładująca widok
   function loadView(viewName) {
    let viewPath = `/calendar/${viewName.replace(/^\/|\/$/g, '')}/`;  // Usuwa nadmiarowe slashe na początku i końcu
    console.log("Generated path:", viewPath);

    fetch(viewPath)
        .then((response) => {
            console.log('Response status:', response.status);  // Logujemy status odpowiedzi
            if (!response.ok) {
                throw new Error(`Nie udało się załadować widoku. Status: ${response.status}`);
            }
            return response.text();
        })
        .then((html) => {
            calendarContent.innerHTML = html;
        })
        .catch((error) => {
            console.error("Błąd ładowania widoku:", error);
            calendarContent.innerHTML =
                "<p>Błąd ładowania widoku. Spróbuj ponownie później.</p>";
        });
}


    // Obsługa zmiany widoku
    viewSelector.addEventListener("change", function () {
        const selectedView = viewSelector.value;
        loadView(selectedView);
    });
});
