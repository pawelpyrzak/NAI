document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");
    const chatContent = document.querySelector(".chat-content");

    // Pobierz token CSRF z meta tagu
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    sendButton.addEventListener("click", async () => {
        const message = inputField.value.trim();
        if (message !== "") {
            // Tworzenie nowego elementu wiadomości użytkownika
            const userMessage = document.createElement("div");
            userMessage.classList.add("user-messages");
            userMessage.innerHTML = `
                <div class="user-avatar"></div>
                <div class="outgoing-msg">
                    <div class="outgoing-chats-msg">${message}</div>
                </div>
            `;
            
            // Dodanie wiadomości do sekcji czatu
            chatContent.appendChild(userMessage);

            // Czyszczenie pola tekstowego
            inputField.value = "";

            // Automatyczne przewinięcie na dół
            chatContent.scrollTop = chatContent.scrollHeight;

            // Wyślij wiadomość do backendu (Django)
            try {
                const response = await fetch("/chat/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",  // Zmieniamy na application/json
                        "X-CSRFToken": csrfToken  // Dodaj token CSRF
                    },
                    body: JSON.stringify({ message: message })  // Wysyłamy dane w formacie JSON
                });

                const data = await response.json();
                console.log("Response from server:", data);  // Dodaj print do konsoli, aby sprawdzić odpowiedź
                if (data.response) {
                    // Dodaj odpowiedź bota do czatu
                    const botMessage = document.createElement("div");
                    botMessage.classList.add("bot-messages");
                    botMessage.innerHTML = `
                        <div class="bot-avatar"></div>
                        <div class="received-msg">
                            <div class="received-msg-inbox">${data.response}</div>
                        </div>
                    `;
                    chatContent.appendChild(botMessage);

                    // Automatyczne przewinięcie na dół
                    chatContent.scrollTop = chatContent.scrollHeight;
                } else {
                    console.error("Błąd: Brak odpowiedzi od bota");
                }
            } catch (error) {
                console.error("Błąd podczas komunikacji z botem:", error);
            }
        }
    });

    // Opcjonalnie: obsługa wysyłania wiadomości klawiszem Enter
    inputField.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendButton.click();
        }
    });
});
