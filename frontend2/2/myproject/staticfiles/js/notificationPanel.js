function toggleNotificationPanel() {
    const panel = document.getElementById("notificationPanel");
    panel.classList.toggle("show"); // Dodaje/usuwa klasę "show" przy kliknięciu
}

document.getElementById("not").addEventListener("click", toggleNotificationPanel);