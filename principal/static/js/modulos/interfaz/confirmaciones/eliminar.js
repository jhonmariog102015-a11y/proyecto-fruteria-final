// ==============================================================================
// CONFIRMACIÓN DE ELIMINACIÓN CON SWEETALERT2 (Guía 4)
// Confirma el borrado antes de enviar el formulario POST con CSRF.
// ==============================================================================
document.addEventListener("click", async (evento) => {
    const boton = evento.target.closest(".js-confirmar-eliminacion");
    if (!boton) {
        return;
    }

    const formulario = document.getElementById(boton.dataset.formEliminar);
    if (!formulario) {
        return;
    }

    const resultado = await Swal.fire({
        title: "¿Confirmas la eliminación?",
        text: `Se eliminará: ${boton.dataset.nombre}.`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#dc3545",
    });

    if (resultado.isConfirmed) {
        formulario.requestSubmit();
    }
});
