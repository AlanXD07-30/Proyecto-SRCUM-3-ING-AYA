const ciudadSelect = document.getElementById("ciudad");
  const tipoSelect = document.getElementById("tipo");
  const inmuebles = document.querySelectorAll(".card-inmueble");

  function filtrar() {
    const ciudadSeleccionada = ciudadSelect.value;
    const tipoSeleccionado = tipoSelect.value;

    console.log("Filtrando por Ciudad:", ciudadSeleccionada); // Para ver qué seleccionaste

    inmuebles.forEach((inmueble) => {
      const ciudadInmueble = inmueble.getAttribute("data-ciudad");
      const tipoInmueble = inmueble.getAttribute("data-tipo");

      const coincideCiudad = ciudadSeleccionada === "todos" || ciudadSeleccionada === ciudadInmueble;
      const coincideTipo = tipoSeleccionado === "todos" || tipoSeleccionado === tipoInmueble;

      if (coincideCiudad && coincideTipo) {
        inmueble.style.display = "flex"; // Se muestra
      } else {
        console.log("Ocultando inmueble de:", ciudadInmueble); // Para confirmar que entra aquí
        inmueble.style.display = "none"; // Se oculta
      }
    });
  }

  ciudadSelect.addEventListener("change", filtrar);
  tipoSelect.addEventListener("change", filtrar);