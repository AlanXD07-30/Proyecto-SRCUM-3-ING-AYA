function alertaInmueble(event) { 
    const swalWithBootstrapButtons = Swal.mixin({
  customClass: {
    confirmButton: "btn btn-success",
    cancelButton: "btn btn-danger"
  },
  buttonsStyling: false
});
swalWithBootstrapButtons.fire({
  title: "Quieres volver a atras?",
  icon: "warning",
  showCancelButton: true,
  confirmButtonText: "Si",
  cancelButtonText: "No",
  reverseButtons: true
}).then((result) => {
  if (result.isConfirmed) {
    swalWithBootstrapButtons.fire({
      title: "Deleted!",
      text: "Your file has been deleted.",
      icon: "success"
    });
  } 
});
}




  function confirmarSobreNosotros(event) {
    event.preventDefault(); 
    Swal.fire({
  title: "Quieres ver mas Sobre Nosotros?",
  text: "Puedes ver mas sobre nosotros!",
  icon: "warning",
  showCancelButton: true,
  confirmButtonColor: "#3085d6",
  cancelButtonColor: "#d33",
  confirmButtonText: "Confirmar"
})
.then((result) => {
      if (result.isConfirmed) {
        window.location.href = "../SOBRE NOSOTROS/sobrenosotros.html";
      }
    });
  }



  function confirmarInmuebles(event) {
    event.preventDefault(); 
    Swal.fire({
  title: "Quieres ver nuestros Inmuebles?",
  text: "Puedes ver nuestros Inmuebles!",
  icon: "warning",
  showCancelButton: true,
  confirmButtonColor: "#3b82f6",
  cancelButtonColor: "#d33",
  confirmButtonText: "Confirmar"
})
.then((result) => {
      if (result.isConfirmed) {
        window.location.href = "../SECCIÓN DE INMUEBLES/inmuebles.html";
      }
    });
  }



  function confirmarNosotros(event) {
    event.preventDefault(); 
    Swal.fire({
  title: "Quieres ver como Contactarnos?",
  text: "Puedes ver como contactarnos!",
  icon: "warning",
  showCancelButton: true,
  confirmButtonColor: "#3085d6",
  cancelButtonColor: "#d33",
  confirmButtonText: "Confirmar"
})
.then((result) => {
      if (result.isConfirmed) {
        window.location.href = "../CONTACTANOS/contactanos.html";
      }
    });
  }
