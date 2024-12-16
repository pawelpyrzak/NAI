function toggleNotificationPopup() {
    const popup = document.getElementById("notificationPopup");
    if (popup.style.display === "flex") {
        popup.style.display = "none";
    } else {
        popup.style.display = "flex";
    }
}

document.getElementById("not").addEventListener("click", toggleNotificationPopup);
