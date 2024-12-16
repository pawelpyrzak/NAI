function toggleNotifications() {
    const panel = document.querySelector('.notification-box');
    panel.style.display = panel.style.display === 'none' || panel.style.display === '' ? 'block' : 'none';
}