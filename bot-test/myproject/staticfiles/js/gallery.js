function openModal(imageSrc, imageAlt) {
    document.getElementById('modalImage').src = imageSrc;
    document.getElementById('modalImage').alt = imageAlt;
    document.getElementById('myModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}

window.onclick = function (event) {
    if (event.target === document.getElementById('myModal')) {
        closeModal();
    }
};