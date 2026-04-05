const ciudadSelect = document.getElementById("ciudad");
const tipoSelect = document.getElementById("tipo");
const gridInmuebles = document.getElementById("gridInmuebles");
const emptyState = document.getElementById("emptyState");
const mensajeFavorito = document.getElementById("mensaje-favorito");

let inmueblesData = [];


fetch("http://localhost:8080/java/inmuebles")
  .then(res => res.json())
  .then(data => {

    inmueblesData = data.filter(i => i.tipoOperacion === "VENTA");
    renderInmuebles(inmueblesData);
  });

function crearTarjeta(inmueble) {
  const card = document.createElement("article");
  card.className = "card-inmueble";
  card.dataset.ciudad = inmueble.ciudad || "Desconocido";
  card.dataset.tipo = inmueble.tipoOperacion || "Sin tipo";

  card.innerHTML = `
    <img src="${inmueble.imagen || 'https://via.placeholder.com/800x520?text=Imagen+disponible'}">
    <div class="card-body">
      <div class="card-meta">
        <span class="badge">${inmueble.tipoOperacion || 'Tipo'}</span>
        <span class="precio">${formatearPrecio(inmueble.precio)}</span>
      </div>
      <h3>${inmueble.direccion || 'Inmueble'}</h3>
      <p>${inmueble.descripcion || 'Propiedad disponible para venta.'}</p>
      <div class="card-meta">
        <span>${inmueble.ciudad || 'Ciudad'}</span>
        <a href="#" class="btn-moderno">Ver detalle</a>
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
    emptyState.textContent = "No hay propiedades en venta.";
    return;
  }

  const ciudadSeleccionada = ciudadSelect.value;

  const filtrados = items.filter((item) => {
    const coincideCiudad =
      ciudadSeleccionada === "todos" ||
      item.ciudad === ciudadSeleccionada;

    return coincideCiudad;
  });

  if (filtrados.length === 0) {
    emptyState.textContent = "No hay propiedades que coincidan.";
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

ciudadSelect.addEventListener("change", aplicarFiltros);

document.addEventListener("DOMContentLoaded", () => {
  renderInmuebles(inmueblesData);
});