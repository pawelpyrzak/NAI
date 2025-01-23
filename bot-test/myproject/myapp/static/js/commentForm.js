document.addEventListener('DOMContentLoaded', function() {
    const formButtonContainer = document.querySelector('.form-button-container');
    const cancelButton = document.querySelector('.cancel-button');
    const commentForm = document.querySelector('.comment-form');

    const replyCancelButton = document.querySelectorAll('.reply-cancel-button');
    const replyFormContainers = document.querySelectorAll('.reply-form-container');
    const replyButtonContainers = document.querySelectorAll('.reply-button-container');

    window.expandTextarea = function(textarea) {

        textarea.style.height = '120px';  
        textarea.style.borderRadius = '25px'; 

        const formButtonContainer = textarea.closest('form').querySelector('.form-button-container');
        if (formButtonContainer) {
            formButtonContainer.style.display = 'flex';
            setTimeout(function() {
                formButtonContainer.style.opacity = '1';
            }, 10);
        }

        const replyButtonContainer = textarea.closest('.reply-form-container')?.querySelector('.reply-button-container');
        if (replyButtonContainer) {
            replyButtonContainer.style.display = 'flex';
            setTimeout(function() {
                replyButtonContainer.style.opacity = '1';
            }, 10);
        }
    };

    window.resetCommentForm = function() {
        const textarea = commentForm.querySelector('textarea');

        textarea.value = '';
        textarea.style.height = '35px';
        commentForm.style.marginBottom = '0';  
        textarea.style.border = '1px solid #424244';
        textarea.style.borderRadius = '50px';

        formButtonContainer.style.opacity = '0';
        setTimeout(function() {
            formButtonContainer.style.display = 'none';
        }, 200);
    };

    window.resetReplyForm = function(button) {
        const replyForm = button.closest('.reply-form-container');
        const replyTextarea = replyForm.querySelector('textarea');

        replyTextarea.value = '';
        replyTextarea.style.height = '35px';
        replyTextarea.style.border = '1px solid #424244';  
        replyTextarea.style.borderRadius = '50px';

        const replyButtonContainer = replyForm.querySelector('.reply-button-container');
        if (replyButtonContainer) {
            replyButtonContainer.style.opacity = '0';
            setTimeout(function() {
                replyButtonContainer.style.display = 'none';
            }, 200);
        }

        replyForm.classList.add('hidden');
        replyForm.style.marginBottom = '0';  
    };

    const textarea = commentForm.querySelector('textarea');
    if (textarea) {
        textarea.addEventListener('focus', function() {
            textarea.style.height = '120px';
            commentForm.style.marginBottom = '60px';  
            textarea.style.borderRadius = '25px';

            formButtonContainer.style.display = 'flex';
            setTimeout(function() {
                formButtonContainer.style.opacity = '1';
            }, 10);
        });
    }

    replyFormContainers.forEach((form, index) => {
        const replyTextarea = form.querySelector('textarea');
        if (replyTextarea) {
            replyTextarea.addEventListener('focus', function() {
                replyTextarea.style.height = '120px';
                form.style.marginBottom = '60px';  
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

    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            resetCommentForm();  
        });
    }

    if (replyCancelButton.length > 0) {
        replyCancelButton.forEach(function(button) {
            button.addEventListener('click', function() {
                resetReplyForm(button);  
            });
        });
    }
});