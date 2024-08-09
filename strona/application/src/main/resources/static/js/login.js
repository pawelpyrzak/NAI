document.addEventListener("DOMContentLoaded", function () {
    showStep(1);
});

function showStep(step) {
    var steps = document.querySelectorAll(".form-step");

    steps.forEach(function (element) {
        element.classList.remove("active");
    });

    var currentStep = document.getElementById("step" + step);

    if (currentStep) {
        currentStep.classList.add("active");
    }
}

function nextStep(currentStep) {
    showStep(currentStep + 1);
}
