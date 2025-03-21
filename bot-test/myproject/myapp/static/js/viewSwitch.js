document.addEventListener("DOMContentLoaded", function () {
    const navClasses = [".project-nav", ".task-nav"]; // Lista klas nawigacyjnych

    navClasses.forEach(navClass => {
        const links = document.querySelectorAll(`${navClass} a`);
        const sections = document.querySelectorAll("section");

        links.forEach(link => {
            link.addEventListener("click", function (event) {
                event.preventDefault(); // Zapobiega przeładowaniu strony

                const targetId = this.getAttribute("data-target");

                sections.forEach(section => {
                    section.style.display = "none";
                });

                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.style.display = "block";
                }
            });
        });
    });
});
