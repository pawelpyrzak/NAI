document.addEventListener("scroll", function() {
    var scrolled = window.scrollY;

    // Adjust the background-position based on the scroll position
    document.getElementById("parallax").style.backgroundPosition = "center " + (scrolled * 0.5) + "px";
    document.getElementById("parallax2").style.backgroundPosition = "center " + (scrolled * 0.5) + "px";
    document.getElementById("parallax3").style.backgroundPosition = "center " + (scrolled * 0.5) + "px";
});