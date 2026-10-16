// CAMBIO GUÍA 4: muestra los mensajes de Django mediante SweetAlert2.
document.addEventListener("DOMContentLoaded", () => {
    const contenedor = document.getElementById("mensajes-django");
    if (!contenedor) {
        return;
    }

    const iconos = {
        success: "success",
        error: "error",
        warning: "warning",
        info: "info",
    };

    contenedor.querySelectorAll("[data-tag]").forEach((elemento) => {
        const tag = elemento.dataset.tag.split(" ")[0];
        const icon = iconos[tag];
        if (icon) {
            Swal.fire({
                icon,
                text: elemento.dataset.text,
                confirmButtonText: "Aceptar",
            });
        }
    });
});
