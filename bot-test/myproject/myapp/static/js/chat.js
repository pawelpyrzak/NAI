document.addEventListener("DOMContentLoaded", function () {
    const chatHeader = document.getElementById("chat-header");
    const chatContent = document.getElementById("chat-content");
    const chatInput = document.getElementById("chat-input");
    const chatSend = document.getElementById("chat-send");
    const messagesDiv = document.getElementById("messages");
    const voiceButton = document.getElementById("voice-btn");
    const recordingIndicator = document.getElementById("recording-indicator");
    const recordingTimer = document.getElementById("recording-timer");

    let recognition;
    let timerInterval;
    let recordingStartTime;

    const AUTO_CLEAR_TIME_MS = 60 * 60 * 1000;

    const chatHistory = JSON.parse(localStorage.getItem("chatHistory") || "[]");
    if (chatHistory.length === 0) {
        addMessage("Bot", "Witaj! Dostępne komendy: !help, !remind, !clear");
    }
    loadChatHistory();

    chatHeader.addEventListener("click", () => {
        chatContent.style.display = chatContent.style.display === "none" ? "block" : "none";
    });

    function removeHtmlTags(input) {
        return input.replace(/<[^>]*>/g, '');
    }

    chatSend.addEventListener("click", () => {
        const rawMessage = chatInput.value.trim();
        let sanitizedMessage = DOMPurify.sanitize(rawMessage)
        const message = normalizeText(removeHtmlTags(sanitizedMessage));

        if (message) {
            addMessage("Ty", rawMessage);
            chatInput.value = "";

            if (message === "!clear") {
                clearChatHistory();
                // return;
            }

            fetch("/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({message}),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.response !== "" && data.response !== undefined && data.response !== null) {
                        addMessage("Bot", data.response);
                    }
                })
                .catch((error) => {
                    console.error("Błąd:", error);
                });
        }
    });

    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'pl-PL';
        recognition.interimResults = false;

        voiceButton.addEventListener("mousedown", startRecording);
        voiceButton.addEventListener("mouseup", stopRecording);
        voiceButton.addEventListener("mouseleave", stopRecording); // Na wypadek wyjścia z przycisku

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value += transcript;
        };

        recognition.onerror = (event) => {
            console.error("Błąd rozpoznawania mowy:", event.error);
            alert('Nie udało się rozpoznać mowy. Spróbuj ponownie.');
        };

        recognition.onend = () => {
            stopRecordingUI();
        };
    } else {
        alert('Twoja przeglądarka nie obsługuje rozpoznawania mowy.');
    }

    function addMessage(sender, message) {
        const messageDiv = document.createElement("div");
        const senderElement = document.createElement("strong");
        senderElement.textContent = `${sender}: `;
        messageDiv.appendChild(senderElement);

        // Użycie DOMPurify do oczyszczenia wiadomości HTML
        const safeMessage = DOMPurify.sanitize(message); // Sanityzacja HTML

        const messageElement = document.createElement("span");
        messageElement.innerHTML = safeMessage; // Wstawienie oczyszczonego HTML
        messageDiv.appendChild(messageElement);

        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        saveChatHistory();
    }

    function saveChatHistory() {
        const messages = Array.from(messagesDiv.children).map(
            (message) => message.innerHTML
        );
        const now = Date.now();
        localStorage.setItem("chatHistory", JSON.stringify(messages));
        localStorage.setItem("chatTimestamp", now.toString());
    }

    function loadChatHistory() {
        const chatHistory = JSON.parse(localStorage.getItem("chatHistory") || "[]");
        const timestamp = parseInt(localStorage.getItem("chatTimestamp") || "0", 10);
        const now = Date.now();

        if (timestamp && now - timestamp > AUTO_CLEAR_TIME_MS) {
            clearChatHistory();
            return;
        }

        chatHistory.forEach((messageHTML) => {
            const messageDiv = document.createElement("div");
            messageDiv.innerHTML = messageHTML;
            messagesDiv.appendChild(messageDiv);
        });
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function clearChatHistory() {
        localStorage.removeItem("chatHistory");
        localStorage.removeItem("chatTimestamp");
        messagesDiv.innerHTML = "";
        addMessage("Bot", "Dostępne komendy: !help, !remind, !clear");
    }

    function normalizeText(text) {
        return text
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase();
    }

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }

    function startRecording() {
        recognition.start();
        startRecordingUI();
    }

    function stopRecording() {
        recognition.stop();
    }

    function startRecordingUI() {
        recordingIndicator.style.display = "inline-block";
        recordingTimer.style.display = "inline-block";
        recordingStartTime = Date.now();

        timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
            recordingTimer.textContent = `${elapsed}s`;
        }, 1000);
    }

    function stopRecordingUI() {
        clearInterval(timerInterval);
        recordingIndicator.style.display = "none";
        recordingTimer.style.display = "none";
        recordingTimer.textContent = "0s";
    }
});