document.addEventListener("DOMContentLoaded", function () {
    // Funkcja ustawiająca datę
    function setFormattedDate() {
        const dateElement = document.getElementById("formattedDate");

        if (!dateElement) {
            console.error("Element z ID 'formattedDate' nie istnieje w DOM.");
            return;
        }

        const today = new Date();

        // Formatowanie daty
        try {
            const formattedDate = new Intl.DateTimeFormat('pl-PL', {
                weekday: 'long',  // Pełna nazwa dnia
                day: '2-digit',   // Dwucyfrowy dzień
                month: 'long',    // Pełna nazwa miesiąca
                year: 'numeric'   // Rok
            }).format(today);

            // Ustawienie daty w elemencie
            dateElement.textContent =
                formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
        } catch (error) {
            console.error("Błąd podczas formatowania daty:", error);
        }
    }

    // Wywołanie funkcji
    setFormattedDate();
});
