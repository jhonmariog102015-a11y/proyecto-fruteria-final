/**
 * ==============================================================================
 * CATÁLOGO DE FRUTAS (principal/static/js/catalogo.js)
 * Al Paso Frutería — Filtros por chips, búsqueda en vivo, lectura de parámetros
 * URL (?categoria=..., ?filtro=ofertas, ?q=...) y contador reactivo.
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

    // Leer parámetros URL (para navegación directa desde menú navbar o tarjetas)
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const urlCat = urlParams.get('categoria');
        const urlFiltro = urlParams.get('filtro');
        const urlQ = urlParams.get('q');

        if (urlFiltro === 'ofertas') {
            const ofertaChip = document.querySelector('.filter-chip[data-filter="ofertas"]');
            if (ofertaChip) {
                chips.forEach(c => c.classList.remove('active'));
                ofertaChip.classList.add('active');
                activeFilter = 'ofertas';
            }
        } else if (urlCat) {
            const catClean = urlCat.trim().toLowerCase();
            if (catClean === 'frutas' || catClean === 'frutas-y-verduras') {
                const todasChip = document.querySelector('.filter-chip[data-filter="all"]');
                if (todasChip) {
                    chips.forEach(c => c.classList.remove('active'));
                    todasChip.classList.add('active');
                    activeFilter = 'all';
                }
            } else {
                const catChip = document.querySelector(`.filter-chip[data-filter="${catClean}"]`);
                if (catChip) {
                    chips.forEach(c => c.classList.remove('active'));
                    catChip.classList.add('active');
                    activeFilter = catClean;
                } else {
                    chips.forEach(c => c.classList.remove('active'));
                    activeFilter = catClean;
                }
            }
        }

        if (urlQ && searchInput) {
            searchInput.value = urlQ;
            searchQuery = urlQ.trim().toLowerCase();
            if (clearSearchBtn) clearSearchBtn.style.display = 'flex';
        }
    } catch (e) {
        console.error('Error parseando parámetros URL:', e);
    }

    // Inicializar filtros
    applyFilters();
});
