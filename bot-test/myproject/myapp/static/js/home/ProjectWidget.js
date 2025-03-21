document.addEventListener("DOMContentLoaded", function () {
    const projectOptionsSelect = document.getElementById("project-options-select");
    const projectBoard = document.getElementById("dynamic-project-board");
    function changeContent(view){
        fetch(`/load-project-content/${view}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                projectBoard.innerHTML = data.html;
            })
            .catch(error => {
                console.error("Błąd podczas ładowania projektów:", error);
                projectBoard.innerHTML = '<p>Wystąpił błąd podczas ładowania projektów. Spróbuj ponownie później.</p>';
            });
    }
    projectOptionsSelect.addEventListener("change", function () {
        const status = this.value;
        projectBoard.innerHTML = '<p>Ładowanie projektów...</p>';
        changeContent(status);
    });
    changeContent('pending');

});
