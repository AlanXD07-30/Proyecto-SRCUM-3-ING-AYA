let inmueblesGlobal = [];

fetch("http://localhost:8080/java/inmuebles")
  .then(res => res.json())
  .then(data => {

    inmueblesGlobal = data.filter(i => i.tipoOperacion === "ARRIENDO");
    renderizar(inmueblesGlobal);
  });

function renderizar(data) {
  const grid = document.getElementById("gridInmuebles");
  const empty = document.getElementById("emptyState");

  grid.innerHTML = "";

  if (data.length === 0) {
    empty.style.display = "block";
    return;
  } else {
    empty.style.display = "none";
  }

  data.forEach(inmueble => {
    const card = document.createElement("div");
    card.classList.add("card-inmueble");

    card.innerHTML = `
      <div class="card-content">
        <h3>${inmueble.direccion}</h3>
        <p><strong>Barrio:</strong> ${inmueble.barrio || "N/A"}</p>
        <p><strong>Ciudad:</strong> ${inmueble.ciudad || "N/A"}</p>
        <p><strong>Precio:</strong> $${Number(inmueble.precio).toLocaleString()}</p>
        <p><strong>Estado:</strong> ${inmueble.estado}</p>
        <p><strong>Metraje:</strong> ${inmueble.metraje} m²</p>
      </div>
    `;

    grid.appendChild(card);
  });
}


document.getElementById("ciudad").addEventListener("change", function () {
  const ciudadSeleccionada = this.value;

  if (ciudadSeleccionada === "todos") {
    renderizar(inmueblesGlobal);
  } else {
    const filtrados = inmueblesGlobal.filter(
      i => i.ciudad === ciudadSeleccionada
    );
    renderizar(filtrados);
  }
});