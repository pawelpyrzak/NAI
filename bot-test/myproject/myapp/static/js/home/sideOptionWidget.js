document.addEventListener("DOMContentLoaded", function () {

    function resizeWidget(buttonData) {
        const widget = document.querySelector(buttonData.widgetSelector);
        if (widget) {
            console.log(widget);
            console.log("classes: " + widget.classList.length);
            widget.classList.remove("small", "full");
            widget.classList.add(buttonData.size);            // Wysyłamy aktualizację dla widgetu z nowym rozmiarem
            toggleWidgetSize(widget.classList[0],buttonData.size)
            sendWidgetUpdate(widget.classList[0], getWidgetPosition(widget), buttonData.size);
            console.log("send resize" + widget.classList[0] + buttonData.size);

        }
        const menu = document.getElementById(buttonData.widgetSelector.replace(".", "-options-menu"));
        closeMenu(menu);
    }

    function closeMenu(menu) {
        if (menu) {
            menu.classList.add("hidden");
        }
    }

    function openMenu(menu) {
        if (menu) {
            menu.classList.remove("hidden");
        }
    }

    const resizeButtons = [
        {buttonId: "calendar-resize-small", size: "small", widgetSelector: ".calendar"},
        {buttonId: "reminder-resize-small", size: "small", widgetSelector: ".reminder"},
        {buttonId: "projects-resize-small", size: "small", widgetSelector: ".projects"},
        {buttonId: "tasks-resize-small", size: "small", widgetSelector: ".task"},
        {buttonId: "teams-resize-small", size: "small", widgetSelector: ".teams"},
        {buttonId: "activity-resize-small", size: "small", widgetSelector: ".activity"},
    ];

    resizeButtons.forEach(function (buttonData) {
        const resizeButton = document.getElementById(buttonData.buttonId);
        if (resizeButton) {
            resizeButton.addEventListener("click", () => {
                resizeWidget(buttonData)
            });
        }
    });

    const resizeFullButtons = [
        {buttonId: "calendar-resize-full", size: "full", widgetSelector: ".calendar"},
        {buttonId: "reminder-resize-full", size: "full", widgetSelector: ".reminder"},
        {buttonId: "projects-resize-full", size: "full", widgetSelector: ".projects"},
        {buttonId: "tasks-resize-full", size: "full", widgetSelector: ".task"},
        {buttonId: "teams-resize-full", size: "full", widgetSelector: ".teams"},
        {buttonId: "activity-resize-full", size: "full", widgetSelector: ".activity"},
    ];

    resizeFullButtons.forEach(function (buttonData) {
        const resizeButton = document.getElementById(buttonData.buttonId);
        if (resizeButton) {
            resizeButton.addEventListener("click", () => {
                resizeWidget(buttonData)
            });
        }
    });


    const menuIcons = [
        {iconId: "calendar-options-icon", menuId: "calendar-options-menu"},
        {iconId: "reminder-options-icon", menuId: "reminder-options-menu"},
        {iconId: "projects-options-icon", menuId: "projects-options-menu"},
        {iconId: "tasks-options-icon", menuId: "tasks-options-menu"},
        {iconId: "teams-options-icon", menuId: "teams-options-menu"},
        {iconId: "activity-options-icon", menuId: "activity-options-menu"},
    ];

    menuIcons.forEach(function (iconData) {
        const icon = document.getElementById(iconData.iconId);
        const menu = document.getElementById(iconData.menuId);

        if (icon) {
            icon.addEventListener("click", function (event) {
                if (menu.classList.contains("hidden")) {
                    openMenu(menu);
                } else {
                    closeMenu(menu);
                }
                event.stopPropagation();
            });
        }

        document.addEventListener("click", function (event) {
            if (!menu.contains(event.target) && event.target !== icon) {
                closeMenu(menu);
            }
        });

        const menuOptions = menu.querySelectorAll("li");
        menuOptions.forEach(function (option) {
            option.addEventListener("click", function () {
                closeMenu(menu);
            });
        });
    });

    const deleteButtons = [
        {buttonId: "calendar-delete-widget", dropzoneId: "dropzone1"},
        {buttonId: "reminder-delete-widget", dropzoneId: "dropzone2"},
        {buttonId: "projects-delete-widget", dropzoneId: "dropzone3"},
        {buttonId: "tasks-delete-widget", dropzoneId: "dropzone4"},
        {buttonId: "teams-delete-widget", dropzoneId: "dropzone5"},
        {buttonId: "activity-delete-widget", dropzoneId: "dropzone6"},
    ];

    deleteButtons.forEach(function (buttonData) {
        const deleteButton = document.getElementById(buttonData.buttonId);
        if (deleteButton) {
            deleteButton.addEventListener("click", function () {
                const dropzone = document.getElementById(buttonData.dropzoneId);
                if (dropzone) {
                    dropzone.classList.add("fade-out");
                    setTimeout(() => {
                        dropzone.style.display = "none";
                        // Jeśli widget został ukryty, wysyłamy aktualizację (position = 0)
                        const widget = dropzone.querySelector(".widget");
                        if (widget) {
                            sendWidgetUpdate(widget.id, 0, getWidgetSize(widget));
                        }
                    }, 240);
                }

                let panelClass = "";

                switch (buttonData.dropzoneId) {
                    case "dropzone1":
                        panelClass = "calendar-widget-panel";
                        break;
                    case "dropzone2":
                        panelClass = "reminder-widget-panel";
                        break;
                    case "dropzone3":
                        panelClass = "projects-widget-panel";
                        break;
                    case "dropzone4":
                        panelClass = "tasks-widget-panel";
                        break;
                    case "dropzone5":
                        panelClass = "teams-widget-panel";
                        break;
                    case "dropzone6":
                        panelClass = "last-activity-widget-panel";
                        break;
                    default:
                        console.log("Nieznany dropzone ID");
                }

                if (panelClass) {
                    const widgetPanels = document.getElementsByClassName(panelClass);
                    if (widgetPanels.length > 0) {
                        widgetPanels[0].style.display = 'block';
                    } else {
                        console.log("Nie znaleziono panelu: " + panelClass);
                    }
                }

                const menu = document.getElementById(buttonData.dropzoneId.replace("dropzone", "") + "-options-menu");
                closeMenu(menu);
            });
        }
    });
});
function toggleWidgetSize(name,size) {
    switch (size) {
        case "small":
            document.getElementById(getButtonId(name, "full")).style.display = "block";
            document.getElementById(getButtonId(name, "small")).style.display = "none";
            break;
        case "full":
            document.getElementById(getButtonId(name, "full")).style.display = "none";
            document.getElementById(getButtonId(name, "small")).style.display = "block";
            break;
        default:
            console.warn("Nieznany rozmiar widgetu: ", widget.size);
    }
}

function getButtonId(widgetSelector, size) {
    const mapping = {
        "calendar": "calendar-resize-",
        "reminder": "reminder-resize-",
        "projects": "projects-resize-",
        "task": "tasks-resize-",
        "teams": "teams-resize-",
        "activity": "activity-resize-"
    };
    return mapping[widgetSelector] + size;
}