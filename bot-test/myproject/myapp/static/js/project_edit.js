document.addEventListener("DOMContentLoaded", function() {
    const editButton = document.querySelector(".edit-project");
    const taskDescription = document.querySelector(".project-description");
    const editForm = document.querySelector(".edit-project-form");
    const cancelButton = document.querySelector(".cancel-edit-button");

    editButton.addEventListener("click", function() {
        taskDescription.style.display = "none";
        editForm.style.display = "block";
    });

    cancelButton.addEventListener("click", function() {
        editForm.style.display = "none";
        taskDescription.style.display = "block";
    });
});
