document.addEventListener("DOMContentLoaded", function () {
    var navbar = document.querySelector('.navbar');
    var aboutSection = document.getElementById('about');

    function updateNavbarPosition() {
        var scrollPosition = window.scrollY;
        var sectionTop = aboutSection.offsetTop;

        if (scrollPosition >= sectionTop) {
            navbar.classList.add('show');
        } else {
            navbar.classList.remove('show');
        }
    }

    window.addEventListener('scroll', updateNavbarPosition);
    window.addEventListener('resize', updateNavbarPosition);
});
