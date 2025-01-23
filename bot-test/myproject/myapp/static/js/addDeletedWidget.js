function restoreWidget() {

    const addButton = document.querySelector(".calendar-widget-panel .add-panel-widget");
    const addButtonReminder = document.querySelector(".reminder-widget-panel .add-panel-widget");
    const addButtonTasks = document.querySelector(".tasks-widget-panel .add-panel-widget");
    const addButtonProjects = document.querySelector(".projects-widget-panel .add-panel-widget");
    const addButtonTeams = document.querySelector(".teams-widget-panel .add-panel-widget");
    const addButtonLastActivity = document.querySelector(".last-activity-widget-panel .add-panel-widget");

    function addWidgetToDropzone(buttonData, dropzoneId, panelClass) {
        const addButton = document.querySelector(buttonData);

        if (addButton) {
            addButton.addEventListener("click", function() {
                const dropzone = document.getElementById(dropzoneId); 
                if (dropzone) {
                    dropzone.style.display = "block"; 
                    dropzone.classList.remove("fade-out"); 

                    const widgetsContainer = document.querySelector(".widgets");
                    widgetsContainer.appendChild(dropzone); 
                }

                const widgetPanel = document.querySelector(panelClass);
                if (widgetPanel) {
                    widgetPanel.style.display = "none"; 
                }
            });
        }
    }

    addWidgetToDropzone(".calendar-widget-panel .add-panel-widget", "dropzone1", ".calendar-widget-panel");
    addWidgetToDropzone(".reminder-widget-panel .add-panel-widget", "dropzone2", ".reminder-widget-panel");
    addWidgetToDropzone(".tasks-widget-panel .add-panel-widget", "dropzone3", ".tasks-widget-panel");
    addWidgetToDropzone(".projects-widget-panel .add-panel-widget", "dropzone4", ".projects-widget-panel");
    addWidgetToDropzone(".teams-widget-panel .add-panel-widget", "dropzone5", ".teams-widget-panel");
    addWidgetToDropzone(".last-activity-widget-panel .add-panel-widget", "dropzone6", ".last-activity-widget-panel");
}

document.addEventListener("DOMContentLoaded", function() {
    restoreWidget(); 
});