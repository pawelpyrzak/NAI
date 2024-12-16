document.addEventListener("DOMContentLoaded", function () {
    const showLoginButton = document.getElementById("login-btn");
    const popup = document.querySelector(".popup");
    const closeBtn = document.querySelector(".popup .close-btn");

    let isOpen = false;

    showLoginButton.addEventListener("click", function () {
        if (!isOpen) {
            // Ustalanie pozycji na środku pionowo i poziomo
            const windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
            const windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;

            const topPosition = Math.max(0, (windowHeight - popup.offsetHeight) / 2) + 120; // Przesunięcie w dół o 50px
            const leftPosition = Math.max(0, (windowWidth - popup.offsetWidth) / 2) + 190; // Przesunięcie w prawo o 50px

            popup.style.top = `${topPosition}px`;
            popup.style.left = `${leftPosition}px`;

            popup.classList.add("active");
            isOpen = true;
        }
    });

    closeBtn.addEventListener("click", function () {
        popup.style.transition = "top 200ms ease-in-out";
        popup.style.top = "-100%";


        setTimeout(function () {
            popup.style.transition = "";
            popup.classList.remove("active");
            isOpen = false;
        }, 200);
    });
});


