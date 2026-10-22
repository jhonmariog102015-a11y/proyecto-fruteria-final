/**
 * ==============================================================================
 * CATÁLOGO DE FRUTAS (principal/static/js/catalogo.js)
 * El Paso Frutería — Filtros por chips, búsqueda en vivo y contador reactivo.
 * La gestión de la canasta de compra y WhatsApp es controlada por cart.js.
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    // Referencias DOM para filtrado
    const chips = document.querySelectorAll('.filter-chip');
    const cards = document.querySelectorAll('.fruit-card');
    const searchInput = document.getElementById('fruitSearch');
    const counterElem = document.getElementById('contadorReferencias');
    const clearSearchBtn = document.getElementById('clearSearch');

    let activeFilter = 'all';
    let searchQuery = '';

    // Filtrar catálogo (chips + búsqueda)
    function applyFilters() {
        let visibleCount = 0;

        cards.forEach(card => {
            const cardCat = card.dataset.categoria || '';
            const cardTitle = (card.querySelector('h3')?.textContent || '').toLowerCase();
            const cardOrigin = (card.querySelector('.fruit-origin')?.textContent || '').toLowerCase();

            const matchesCategory = (activeFilter === 'all' || cardCat.split(/\s+/).includes(activeFilter) || cardCat === activeFilter);
            const matchesSearch = searchQuery === '' || 
                                  cardTitle.includes(searchQuery) || 
                                  cardOrigin.includes(searchQuery);

            if (matchesCategory && matchesSearch) {
                card.classList.remove('hidden-card');
                visibleCount++;
            } else {
                card.classList.add('hidden-card');
            }
        });

        // Actualizar contador
        if (counterElem) {
            counterElem.textContent = `MOSTRANDO ${visibleCount} DE ${cards.length} REFERENCIAS`;
        }

        // Mensaje sin resultados
        const noResults = document.getElementById('noResultsMsg');
        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    // Eventos chips
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            activeFilter = chip.dataset.filter || 'all';
            applyFilters();
        });
    });

    // Evento búsqueda
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.trim().toLowerCase();
            if (clearSearchBtn) {
                clearSearchBtn.style.display = searchQuery.length > 0 ? 'flex' : 'none';
            }
            applyFilters();
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            searchQuery = '';
            clearSearchBtn.style.display = 'none';
            searchInput.focus();
            applyFilters();
        });
    }

    // Inicializar filtros
    applyFilters();
});
