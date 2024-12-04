
function openPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'block';
    document.getElementById('blur').style.display = 'block';
}

function closePopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
    document.getElementById('blur').style.display = 'none';
}

let originalBodyOverflow = '';

function enableBlur() {
    originalBodyOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.getElementById('blur').style.display = 'block';
}

function disableBlur() {
    document.body.style.overflow = originalBodyOverflow;
    document.getElementById('blur').style.display = 'none';
}