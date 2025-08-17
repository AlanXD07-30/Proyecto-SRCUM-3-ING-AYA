// script.js

// Seleccionar botón y sidebar
const toggleBtn = document.getElementById('toggleBtn');
const sidebar = document.getElementById('sidebar');

// Alternar clase "collapsed"
toggleBtn.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
});