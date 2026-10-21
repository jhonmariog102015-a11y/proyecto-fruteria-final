// ==============================================================================
// MENÚ DE NAVEGACIÓN RESPONSIVO PARA LA TIENDA (Guía 4)
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
    const botonMenu = document.getElementById("hamburgerBtn");
    const enlacesNavegacion = document.querySelector(".nav-links");

    if (botonMenu && enlacesNavegacion) {
        botonMenu.addEventListener("click", () => {
            const estaAbierto = botonMenu.classList.toggle("open");
            enlacesNavegacion.classList.toggle("active-menu", estaAbierto);
            botonMenu.setAttribute("aria-expanded", String(estaAbierto));
        });

        document.querySelectorAll(".nav-link").forEach((enlace) => {
            enlace.addEventListener("click", () => {
                botonMenu.classList.remove("open");
                enlacesNavegacion.classList.remove("active-menu");
                botonMenu.setAttribute("aria-expanded", "false");
            });
        });
    }
});
