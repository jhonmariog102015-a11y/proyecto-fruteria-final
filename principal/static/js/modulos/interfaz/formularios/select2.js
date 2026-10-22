// ==============================================================================
// INICIALIZACIÓN DE SELECT2 CON TEMA BOOTSTRAP 5 (Guía 4)
// ==============================================================================
$(function () {
    if ($.fn.select2) {
        $("form select").select2({
            theme: "bootstrap-5",
            width: "100%",
        });
    }
});
