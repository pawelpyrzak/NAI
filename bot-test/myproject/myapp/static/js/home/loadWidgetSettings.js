document.addEventListener("DOMContentLoaded", function () {
    fetch("/get-widget-settings/")
        .then(response => response.json())
        .then(data => {
            const widgetSettings = data.widgets; // Tablica obiektów { id, position, size }
            const container = document.querySelector('.widgets');

            // Posortuj widgety według pozycji
            widgetSettings.sort((a, b) => a.position - b.position);

            widgetSettings.forEach(setting => {
                const widget = document.getElementById(setting.id);
                if (!widget) return;

                let dropzone = widget.parentElement;
                let panelClass = "";

                if (dropzone.id === "dropzone6") {
                    panelClass = "last-activity-widget-panel";
                } else if (dropzone.id === "dropzone4") {
                    panelClass = "tasks-widget-panel";
                } else if (/^dropzone[1-5]$/.test(dropzone.id)) {
                    panelClass = widget.id + "-widget-panel";
                } else {
                    console.log("Nieznany dropzone ID: " + dropzone.id);
                    return;
                }

                const widgetPanels = document.getElementsByClassName(panelClass);

                if (setting.position < 1) {
                    dropzone.style.display = "none"; // Ukrywanie zamiast usuwać z DOM
                    console.log(`Ukryto: ${dropzone.id}`);
                    if (widgetPanels.length > 0) {
                        widgetPanels[0].style.display = "block";
                    }
                } else {
                    dropzone.style.display = "flex"; // Zapewniamy, że wyświetla się poprawnie

                    let widgetName = setting.id === "task" ? "tasks" : setting.id;
                    const sizePanels = widget.getElementsByClassName(widgetName);
                    if (sizePanels.length > 0) {
                        sizePanels[0].classList.remove("small", "full");
                        sizePanels[0].classList.add(setting.size);
                    }
                    toggleWidgetSize(setting.id, setting.size);

                    if (widgetPanels.length > 0) {
                        widgetPanels[0].style.display = "none";
                    }

                    // **Ustawianie kolejności za pomocą insertBefore zamiast appendChild**
                    let referenceNode = container.children[setting.position - 1];
                    if (referenceNode) {
                        container.insertBefore(dropzone, referenceNode);
                    } else {
                        container.appendChild(dropzone);
                    }
                }
            });
        })
        .catch(error => console.error("Błąd podczas pobierania ustawień widgetów:", error));
});
