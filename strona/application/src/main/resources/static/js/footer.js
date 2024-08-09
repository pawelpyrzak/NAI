document.addEventListener("DOMContentLoaded", function () {
    var footer = document.querySelector('.sticky-footer');
    var underlineSpan = document.querySelector('.sticky-footer .underline span');
    var originalAnimation = underlineSpan.style.animation;

    function updateFooterPosition() {
        var bodyHeight = document.body.offsetHeight;
        var windowHeight = window.innerHeight;
        var scrollTop = window.scrollY;

        if (bodyHeight <= windowHeight) {
            footer.style.position = 'fixed';
            underlineSpan.style.animation = 'none';
        } else {
            footer.style.position = 'relative';
            underlineSpan.style.animation = originalAnimation;
        }
    }

    window.addEventListener('scroll', updateFooterPosition);
    window.addEventListener('resize', updateFooterPosition);
});