const ciudadSelect = document.getElementById("ciudad");
const tipoSelect = document.getElementById("tipo");
const gridInmuebles = document.getElementById("gridInmuebles");
const emptyState = document.getElementById("emptyState");
const mensajeFavorito = document.getElementById("mensaje-favorito");

let inmueblesData = [];

function crearTarjeta(inmueble) {
  const card = document.createElement("article");
  card.className = "card-inmueble";
  card.dataset.ciudad = inmueble.ciudad || "Desconocido";
  card.dataset.tipo = inmueble.tipo || "Sin tipo";

  card.innerHTML = `
    <img src="${inmueble.imagen || 'https://via.placeholder.com/800x520?text=Imagen+disponible'}" alt="${inmueble.titulo || 'Inmueble'}">
    <div class="card-body">
      <div class="card-meta">
        <span class="badge">${inmueble.tipo || 'Tipo'}</span>
        <span class="precio">${formatearPrecio(inmueble.precio)}</span>
      </div>
      <h3>${inmueble.titulo || 'Título del inmueble'}</h3>
      <p>${inmueble.descripcion || 'Descripción breve del inmueble disponible para arriendo.'}</p>
      <div class="card-meta">
        <span>${inmueble.ciudad || 'Ciudad'}</span>
        <a href="${inmueble.url || '#'}" class="btn-moderno">Ver detalle</a>
      </div>
    </div>
  `;

  const favorito = document.createElement("button");
  favorito.type = "button";
  favorito.className = "estrella";
  favorito.title = "Agregar a favoritos";
  favorito.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleFavorito(favorito);
  });

  card.appendChild(favorito);
  return card;
}

function formatearPrecio(valor) {
  if (!valor) return "Precio disponible";
  const numero = Number(valor.toString().replace(/[^0-9.-]+/g, ""));
  return Number.isNaN(numero) ? valor : `COP ${numero.toLocaleString("es-CO")}`;
}

function renderInmuebles(items) {
  gridInmuebles.innerHTML = "";

  if (!items || items.length === 0) {
    emptyState.style.display = "block";
    return;
  }

  const ciudadSeleccionada = ciudadSelect.value;
  const tipoSeleccionado = tipoSelect.value;

  const filtrados = items.filter((item) => {
    const coincideCiudad = ciudadSeleccionada === "todos" || item.ciudad === ciudadSeleccionada;
    const coincideTipo = tipoSeleccionado === "todos" || item.tipo === tipoSeleccionado;
    return coincideCiudad && coincideTipo;
  });

  if (filtrados.length === 0) {
    emptyState.textContent = "No hay propiedades que coincidan con los filtros seleccionados.";
    emptyState.style.display = "block";
    return;
  }

  emptyState.style.display = "none";
  filtrados.forEach((inmueble) => {
    gridInmuebles.appendChild(crearTarjeta(inmueble));
  });
}

function aplicarFiltros() {
  renderInmuebles(inmueblesData);
}

function toggleFavorito(elemento) {
  elemento.classList.toggle("activo");
  mensajeFavorito.style.display = "block";
  setTimeout(() => {
    mensajeFavorito.style.display = "none";
  }, 2200);
}

function confirmarAccion(event) {
  const regresar = confirm("¿Deseas volver a la página de inicio?");
  if (!regresar) {
    event.preventDefault();
  }
}

ciudadSelect.addEventListener("change", aplicarFiltros);
tipoSelect.addEventListener("change", aplicarFiltros);

document.addEventListener("DOMContentLoaded", () => {
  renderInmuebles(inmueblesData);
});

window.INMUEBLES = {
  setItems(items) {
    inmueblesData = Array.isArray(items) ? items : [];
    renderInmuebles(inmueblesData);
  },
  applyFilters: aplicarFiltros,
};
