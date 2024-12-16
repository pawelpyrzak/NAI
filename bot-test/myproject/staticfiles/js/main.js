function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
}
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = section.style.display === "block" ? "none" : "block";
}

