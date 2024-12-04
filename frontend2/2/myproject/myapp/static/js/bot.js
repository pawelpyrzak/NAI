document.addEventListener("DOMContentLoaded", () => {
    const bot = document.querySelector("#ai-bot"); // Cały bot
    const drag = document.querySelector("#drag"); // Obrazek do przeciągania

    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    drag.addEventListener("mousedown", (e) => {
        isDragging = true;

        // Obliczamy różnicę między pozycją myszy a pozycją bota
        offsetX = e.clientX - bot.offsetLeft;
        offsetY = e.clientY - bot.offsetTop;

        document.body.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", (e) => {
        if (isDragging) {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const botWidth = bot.offsetWidth;
            const botHeight = bot.offsetHeight;

            // Obliczamy nowe współrzędne
            let newLeft = e.clientX - offsetX;
            let newTop = e.clientY - offsetY;

            // Ograniczamy ruch w poziomie
            if (newLeft < 0) newLeft = 0;
            if (newLeft + botWidth > viewportWidth) newLeft = viewportWidth - botWidth;

            // Ograniczamy ruch w pionie
            if (newTop < 0) newTop = 0;
            if (newTop + botHeight > viewportHeight) newTop = viewportHeight - botHeight;

            // Aktualizujemy pozycję bota (nie obrazka)
            bot.style.left = `${newLeft}px`;
            bot.style.top = `${newTop}px`;
        }
    });

    document.addEventListener("mouseup", () => {
        if (isDragging) {
            isDragging = false;
            document.body.style.cursor = "default";
        }
    });
});
