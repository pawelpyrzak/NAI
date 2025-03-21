document.addEventListener('DOMContentLoaded', function() {
    const formButtonContainer = document.querySelector('.form-button-container');
    const cancelButton = document.querySelector('.cancel-button');
    const commentForm = document.querySelector('.comment-form');

    const replyCancelButton = document.querySelectorAll('.reply-cancel-button');
    const replyFormContainers = document.querySelectorAll('.reply-form-container');
    const replyButtonContainers = document.querySelectorAll('.reply-button-container');

    // Funkcja do powiększania textarea i wyświetlania przycisków
    window.expandTextarea = function(textarea) {
        // Powiększamy dokładnie ten textarea
        textarea.style.height = '120px';  // Zmieniamy wysokość
        textarea.style.borderRadius = '25px'; // Zaokrąglamy krawędzie

        // Wyświetlanie przycisków
        const formButtonContainer = textarea.closest('form').querySelector('.form-button-container');
        if (formButtonContainer) {
            formButtonContainer.style.display = 'flex';
            setTimeout(function() {
                formButtonContainer.style.opacity = '1';
            }, 10);
        }

        // Jeśli to textarea odpowiedzi, to pokazujemy przyciski odpowiedzi
        const replyButtonContainer = textarea.closest('.reply-form-container')?.querySelector('.reply-button-container');
        if (replyButtonContainer) {
            replyButtonContainer.style.display = 'flex';
            setTimeout(function() {
                replyButtonContainer.style.opacity = '1';
            }, 10);
        }
    };

    // Funkcja do resetowania formularza komentarza
    window.resetCommentForm = function() {
        const textarea = commentForm.querySelector('textarea');

        // Resetowanie formularza
        textarea.value = '';
        textarea.style.height = '35px';
        commentForm.style.marginBottom = '0';  // Przywracamy domyślną odległość między formularzem a innymi elementami
        textarea.style.border = '1px solid #424244';
        textarea.style.borderRadius = '50px';

        formButtonContainer.style.opacity = '0';
        setTimeout(function() {
            formButtonContainer.style.display = 'none';
        }, 200);
    };

    // Funkcja do resetowania formularza odpowiedzi
    window.resetReplyForm = function(button) {
        const replyForm = button.closest('.reply-form-container');
        const replyTextarea = replyForm.querySelector('textarea');

        // Resetowanie formularza odpowiedzi
        replyTextarea.value = '';
        replyTextarea.style.height = '35px';
        replyTextarea.style.border = '1px solid #424244';  // Przywrócenie standardowego obramowania
        replyTextarea.style.borderRadius = '50px';

        // Ukrywanie przycisków odpowiedzi
        const replyButtonContainer = replyForm.querySelector('.reply-button-container');
        if (replyButtonContainer) {
            replyButtonContainer.style.opacity = '0';
            setTimeout(function() {
                replyButtonContainer.style.display = 'none';
            }, 200);
        }

        // Ukrycie formularza odpowiedzi
        replyForm.classList.add('hidden');
        replyForm.style.marginBottom = '0';  // Przywrócenie domyślnej przestrzeni po ukryciu formularza odpowiedzi
    };

    // Obsługuje wyświetlanie formularza komentarza po kliknięciu
    const textarea = commentForm.querySelector('textarea');
    if (textarea) {
        textarea.addEventListener('focus', function() {
            textarea.style.height = '120px';
            commentForm.style.marginBottom = '60px';  // Zwiększamy odległość między formularzem a komentarzami
            textarea.style.borderRadius = '25px';

            formButtonContainer.style.display = 'flex';
            setTimeout(function() {
                formButtonContainer.style.opacity = '1';
            }, 10);
        });
    }

    // Obsługuje wyświetlanie formularza odpowiedzi po kliknięciu
    replyFormContainers.forEach((form, index) => {
        const replyTextarea = form.querySelector('textarea');
        if (replyTextarea) {
            replyTextarea.addEventListener('focus', function() {
                replyTextarea.style.height = '120px';
                form.style.marginBottom = '60px';  // Zwiększamy odległość między formularzem a odpowiedziami
                replyTextarea.style.borderRadius = '25px';

                const replyButtonContainer = replyButtonContainers[index];
                if (replyButtonContainer) {
                    replyButtonContainer.style.display = 'flex';
                    setTimeout(function() {
                        replyButtonContainer.style.opacity = '1';
                    }, 10);
                }
            });
        }
    });

    // Obsługuje kliknięcie przycisku "Anuluj" w formularzu komentarza
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            resetCommentForm();  // Resetowanie formularza komentarza
        });
    }

    // Obsługuje kliknięcie przycisku "Anuluj" w formularzu odpowiedzi
    if (replyCancelButton.length > 0) {
        replyCancelButton.forEach(function(button) {
            button.addEventListener('click', function() {
                resetReplyForm(button);  // Resetowanie formularza odpowiedzi
            });
        });
    }
});
