 const toggleBtn = document.getElementById("toggle-btn");
    const sidebar = document.getElementById("sidebar");
    const contenido = document.getElementById("contenido");

    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("active");
      contenido.classList.toggle("margen");
    });

    function mostrarFavoritos() {
      const tabla = document.getElementById('tabla-favoritos');
      tabla.scrollIntoView({ behavior: 'smooth' });
    }