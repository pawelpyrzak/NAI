let widgetList = {
    calendar: false, 
    reminder: false,
    tasks: false,
    projects: false,
    teams: false,
    lastActivity: false 
};

const widgetBackgroundImages = {
    calendar: '../static/images/Kalendarz.png',
    reminder: '../static/images/Przypomnienia.png',
    tasks: '../static/images/Zadania.png',
    projects: '../static/images/Projekty.png',
    teams: '../static/images/Zespoly.png',
    lastActivity: '../static/images/aktywnosc.png'
};

function renderAvailableWidgets() {
    const widgetListContainer = document.getElementById("widget-list");
    widgetListContainer.innerHTML = ''; 

    for (let widget in widgetList) {
        if (!widgetList[widget]) { 
            widgetListContainer.innerHTML += `
                <div class="${widget}-panel" id="add-${widget}" style="background-image: url('${widgetBackgroundImages[widget]}'); background-size: cover; background-position: center; background-repeat: no-repeat;">
                    <div class="panel-header">
                        <h2>${capitalizeFirstLetter(widget)}</h2>
                        <div class="add-widget-button" onclick="addWidget('${widget}')">
                            <img src="../static/images/plus (1).svg">
                            <span>Dodaj</span>
                        </div>
                    </div>
                </div>
            `;
        }
    }
}

function addWidget(widgetType) {
    if (widgetList[widgetType]) return; 

    let widgetContainer = document.getElementById('widgets-container');
    let widgetHTML = `
        <div class="widget" id="${widgetType}-widget" style="background-image: url('${widgetBackgroundImages[widgetType]}'); background-size: cover; background-position: center; background-repeat: no-repeat;">
            <h2>${capitalizeFirstLetter(widgetType)}</h2>
            <div class="delete-widget" onclick="deleteWidget('${widgetType}')">Usuń</div>
        </div>
    `;
    widgetContainer.innerHTML += widgetHTML; 
    widgetList[widgetType] = true; 

    renderAvailableWidgets();
}

function deleteWidget(widgetType) {

    let widget = document.getElementById(`${widgetType}-widget`);
    if (widget) {
        widget.remove();
    }

    widgetList[widgetType] = false; 

    renderAvailableWidgets();
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

renderAvailableWidgets();