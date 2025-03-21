function toggleNotifications() {
    const notificationBox = document.querySelector('.notification-box');
    if (notificationBox.style.display === 'none') {
        notificationBox.style.display = 'block';
        fetchNotifications();
    } else {
        notificationBox.style.display = 'none';
    }
}

function fetchNotifications() {
    fetch('/api/notifications/all/')
        .then(response => response.json())
        .then(data => {
            const notificationsList = document.getElementById('notifications-list');
            notificationsList.innerHTML = ''; // Czyścimy listę

            data.forEach(notification => {
                const notificationItem = document.createElement('div');
                notificationItem.classList.add('notification-item');

                const title = document.createElement('h3');
                title.textContent = notification.title;
                title.classList.add('notification-title');
                notificationItem.appendChild(title);

                const message = document.createElement('p');
                message.textContent = notification.message;
                message.classList.add('notification-message');
                notificationItem.appendChild(message);

                const createdAt = document.createElement('span');
                createdAt.textContent = timeSince(notification.created_at);
                createdAt.classList.add('notification-created-at');
                notificationItem.appendChild(createdAt);

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'X';
                deleteButton.classList.add('delete-button');
                deleteButton.onclick = function () {
                    deleteNotification(notification.id);
                };
                notificationItem.appendChild(deleteButton);

                notificationsList.appendChild(notificationItem);
            });
        })
        .catch(error => console.error('Błąd pobierania powiadomień:', error));
}



function markAsRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Pobierz token CSRF
        },
    }).then(response => {
        if (response.ok) {
            updateNotificationCount();
            fetchNotifications();
        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateNotificationCount() {
    fetch('/api/notifications/unread-count/')
        .then(response => response.json())
        .then(data => {
            const notificationCount = document.getElementById('notification-count');
            if (data.unread_count > 0) {
                notificationCount.style.display = 'block';
                notificationCount.textContent = data.unread_count;
            } else {
                notificationCount.style.display = 'none';
            }
        })
        .catch(error => console.error('Błąd pobierania liczby nieprzeczytanych powiadomień:', error));
}

function deleteNotification(notificationId) {
    fetch(`/api/notifications/${notificationId}/delete/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Pobranie tokenu CSRF
        },
    })
        .then(response => {
            if (response.ok) {
                // Po usunięciu odświeżamy listę powiadomień i licznik
                fetchNotifications();
                updateNotificationCount();
            } else {
                console.error('Błąd podczas usuwania powiadomienia');
            }
        })
        .catch(error => console.error('Błąd żądania:', error));
}

document.addEventListener('DOMContentLoaded', updateNotificationCount);

function timeSince(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    let interval = Math.floor(seconds / 31536000);

    if (interval >= 1) return interval + " rok(-i) temu";
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) return interval + " miesiąc(-e) temu";
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) return interval + " dzień(-i) temu";
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) return interval + " godzin(-y) temu";
    interval = Math.floor(seconds / 60);
    if (interval >= 1) return interval + " minut(-y) temu";
    return "chwilę temu";
}
