document.addEventListener('DOMContentLoaded', function() {
    updateProgressBar(0);
});

// Funkcja do aktualizacji paska postępu
function updateProgressBar(progress) {
    var progressBar = document.getElementById('progress-bar');

    // Upewniamy się, że wartość postępu nie przekroczy 100%
    var progressWidth = Math.min(200, 100+progress);

    // Ustawienie szerokości paska postępu
    progressBar.style.left = 100 + '%';
}