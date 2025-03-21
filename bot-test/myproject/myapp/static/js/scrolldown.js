document.addEventListener('DOMContentLoaded', function () {
    var scrollBtn = document.getElementById('scroll-btn');

    scrollBtn.addEventListener('click', function () {
        document.getElementById('about').scrollIntoView({ behavior: 'smooth' });
    });

    window.addEventListener('scroll', function () {
        var aboutSection = document.getElementById('about');
        var scrollPercentage = (window.scrollY / aboutSection.offsetHeight) * 100;

        if (scrollPercentage >= 20) {
            scrollBtn.style.opacity = '0';
        } else {
            scrollBtn.style.opacity = '1';
        }
    });
});
