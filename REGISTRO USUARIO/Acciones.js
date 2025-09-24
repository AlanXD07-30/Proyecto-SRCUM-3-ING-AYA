/* MENSAJE DE DATOS APROBADOS  */
  function mostrarAlerta(event){
    event.preventDefault();

    Swal.fire({
      toast: true,                // Se convierte en notificación flotante
      position: 'top-end',        // Arriba a la derecha (puedes cambiar: 'top', 'bottom-end', etc.)
      icon: 'success',
      title: 'Datos cargados correctamente',
      text: 'Gracias por tu tiempo',
      showConfirmButton: false,   // Oculta el botón "Aceptar"
      timer: 3000,                // Desaparece en 3 segundos
      timerProgressBar: true,
      customClass: {
        popup: 'swal-popup'
      }
    });

    // Reset del formulario
    event.target.form.reset();
  }


/* MENSAJE DE DATOS FALTANTES */

  function mostrarAlerta(event) {
    event.preventDefault();

    const form = event.target.form || event.target.closest("form");
    const inputs = form.querySelectorAll("input[required]");
    let valido = true;

    inputs.forEach(input => {
      if (!input.value.trim()) {
        valido = false;
      }
    });

    if (!valido) {
      Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'error',
        title: 'Por favor completa todos los campos',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        customClass: {
          popup: 'swal-popup'
        }
      });
      return; // no continúa
    }

    // Si pasa la validación -> éxito
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Datos cargados correctamente',
      text: 'Gracias por tu tiempo',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      customClass: {
        popup: 'swal-popup'
      }
    });

    form.reset();
  }

