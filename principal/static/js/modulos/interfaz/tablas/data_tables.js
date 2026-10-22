// ==============================================================================
// INICIALIZACIÓN DE DATATABLES CON TRADUCCIÓN AL ESPAÑOL (Guía 4)
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
    if (typeof DataTable !== "undefined") {
        document.querySelectorAll(".tabla-datos").forEach((tabla) => {
            new DataTable(tabla, {
                language: {
                    url: "https://cdn.datatables.net/plug-ins/2.1.8/i18n/es-ES.json",
                },
                pageLength: 10,
                responsive: true,
            });
        });
    }
});
