// CAMBIO GUÍA 4: activa DataTables con traducción oficial al español.
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".tabla-datos").forEach((tabla) => {
        new DataTable(tabla, {
            language: {
                url: "https://cdn.datatables.net/plug-ins/2.3.4/i18n/es-ES.json",
            },
        });
    });
});
