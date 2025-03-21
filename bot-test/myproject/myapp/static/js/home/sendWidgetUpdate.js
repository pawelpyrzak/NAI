// Pobranie tokena CSRF z ciasteczek
function getCSRFToken() {
    const cookieString = document.cookie.split("; ");
    for (let i = 0; i < cookieString.length; i++) {
        const cookie = cookieString[i];
        if (cookie.startsWith("csrftoken=")) {
            return cookie.split("=")[1];
        }
    }
    return null;
}

// Funkcja pomocnicza zwracająca rozmiar widgetu ("full" lub "small")
function getWidgetSize(widget) {
    let widgetName
    if (widget.id === "task") widgetName = "tasks"
    else widgetName = widget.id;
    const sizePanels = widget.getElementsByClassName(widgetName)
    return sizePanels[0].classList.contains("full") ? "full" : "small";
}

// Funkcja pomocnicza pobierająca pozycję widgetu na podstawie właściwości CSS order dropzone
function getWidgetPosition(widget) {
    const dropzone = widget.closest(".dropzone");
    if (dropzone && dropzone.style.order) {
        return parseInt(dropzone.style.order);
    }
    return 1;
}

// Główna funkcja wysyłająca aktualizację widgetu do backendu
function sendWidgetUpdate(widgetId, position, size) {
    let order= {id: widgetId, position: position, size: size}
    console.log(order)
    fetch("/update-widget-order/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            order: [
                {id: widgetId, position: position, size: size}
            ]
        })
    })
        .then(response => response.json())
        .then(data => console.log("Aktualizacja widgetu wysłana:", data))
        .catch(error => console.error("Błąd aktualizacji widgetu:", error));
}
