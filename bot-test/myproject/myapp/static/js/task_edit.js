document.addEventListener("DOMContentLoaded", function() {
    const editButton = document.querySelector(".edit-task");
    const taskDescription = document.querySelector(".task-description");
    const editForm = document.querySelector(".edit-task-form");
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
