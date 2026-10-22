// ==============================================================================
// NOTIFICACIONES TOAST / SWEETALERT2 PARA MENSAJES DJANGO (Guía 4)
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
    const contenedor = document.getElementById("mensajes-django");
    if (!contenedor || typeof Swal === "undefined") {
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
                confirmButtonColor: "#15803d",
            });
        }
    });
});
