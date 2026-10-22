/**
 * ==============================================================================
 * SISTEMA DE FRUTAS FAVORITAS Y CONTROLES DEL NAVBAR (favoritos.js)
 * Al Paso Frutería — Gestión de Favoritos (LocalStorage), Lupa y Usuario
 * ==============================================================================
 */

(function () {
    'use strict';

    const FAV_STORAGE_KEY = 'al_paso_frutas_favoritas';

    // 1. Cargar favoritos desde LocalStorage
    function getFavorites() {
        try {
            const raw = localStorage.getItem(FAV_STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    function saveFavorites(favs) {
        try {
            localStorage.setItem(FAV_STORAGE_KEY, JSON.stringify(favs));
        } catch (e) {
            console.error('Error guardando favoritos:', e);
        }
        updateFavoritesUI();
    }

    function isFavorite(id) {
        const strId = String(id);
        const favs = getFavorites();
        return favs.some(item => String(item.id) === strId);
    }

    window.toggleFavorite = function (fruitData) {
        if (!fruitData || !fruitData.id) return;
        const strId = String(fruitData.id);
        let favs = getFavorites();
        const existingIdx = favs.findIndex(item => String(item.id) === strId);

        if (existingIdx >= 0) {
            favs.splice(existingIdx, 1);
            saveFavorites(favs);
            if (window.showToast) {
                window.showToast(`Quitaste "${fruitData.nombre || 'Fruta'}" de tus favoritos`);
            }
        } else {
            favs.push({
                id: strId,
                nombre: fruitData.nombre || 'Fruta Fresca',
                precio: fruitData.precio || '0',
                imagen: fruitData.imagen || '',
                unidad: fruitData.unidad || 'kg',
                origen: fruitData.origen || 'Boyacá'
            });
            saveFavorites(favs);
            if (window.showToast) {
                window.showToast(`❤️ ¡"${fruitData.nombre || 'Fruta'}" guardada en tus favoritas!`, 'Ver Favoritos', () => {
                    if (window.openFavDrawer) window.openFavDrawer();
                });
            }
        }
    };

    // 2. Actualizar UI de Favoritos (Badges y botones en tarjetas)
    function updateFavoritesUI() {
        const favs = getFavorites();
        const favBadge = document.getElementById('favBadge');
        if (favBadge) {
            favBadge.textContent = favs.length;
        }

        // Actualizar estados visuales de los corazones en las tarjetas
        document.querySelectorAll('.btn-card-fav').forEach(btn => {
            const id = btn.dataset.id;
            if (id && isFavorite(id)) {
                btn.classList.add('is-fav');
                btn.setAttribute('aria-label', 'Quitar de favoritos');
                btn.setAttribute('title', 'Quitar de favoritos');
            } else {
                btn.classList.remove('is-fav');
                btn.setAttribute('aria-label', 'Agregar a favoritos');
                btn.setAttribute('title', 'Agregar a favoritos');
            }
        });

        renderFavItems();
    }

    // 3. Renderizar Lista en el Drawer de Favoritos
    function renderFavItems() {
        const list = document.getElementById('favItemsList');
        const emptyState = document.getElementById('favEmptyState');
        if (!list) return;

        const favs = getFavorites();
        list.innerHTML = '';

        if (favs.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        favs.forEach(fruit => {
            const item = document.createElement('div');
            item.className = 'fav-item-row';
            item.innerHTML = `
                <div class="fav-item-img">
                    <img src="${fruit.imagen || 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=200&auto=format&fit=crop'}" alt="${fruit.nombre}">
                </div>
                <div class="fav-item-details">
                    <h4>${fruit.nombre}</h4>
                    <span class="fav-item-price">$${parseFloat(fruit.precio || 0).toLocaleString('es-CO')} / ${fruit.unidad || 'kg'}</span>
                    <small class="fav-item-origin">📍 ${fruit.origen || 'Cosecha Boyacá'}</small>
                </div>
                <div class="fav-item-actions">
                    <button type="button" class="btn-fav-add-cart" data-id="${fruit.id}" data-nombre="${fruit.nombre}" data-precio="${fruit.precio}" data-imagen="${fruit.imagen}" data-unidad="${fruit.unidad}" title="Añadir a mi canasta">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
                        <span>Pedir</span>
                    </button>
                    <button type="button" class="btn-fav-remove" data-id="${fruit.id}" title="Eliminar de favoritos" aria-label="Eliminar">✕</button>
                </div>
            `;
            list.appendChild(item);
        });
    }

    // 4. Control del Drawer de Favoritos
    window.openFavDrawer = function () {
        const drawer = document.getElementById('favDrawer');
        const overlay = document.getElementById('favOverlay');
        if (drawer) drawer.classList.add('open');
        if (overlay) overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    };

    window.closeFavDrawer = function () {
        const drawer = document.getElementById('favDrawer');
        const overlay = document.getElementById('favOverlay');
        if (drawer) drawer.classList.remove('open');
        if (overlay) overlay.classList.remove('open');
        document.body.style.overflow = '';
    };

    // 5. Inicialización de eventos al cargar el DOM
    document.addEventListener('DOMContentLoaded', () => {
        updateFavoritesUI();

        // Botón abrir drawer de favoritos
        const favToggleBtn = document.getElementById('favToggleBtn');
        if (favToggleBtn) {
            favToggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                window.openFavDrawer();
            });
        }

        // Botón cerrar drawer de favoritos
        const closeFavBtn = document.getElementById('closeFavBtn');
        if (closeFavBtn) {
            closeFavBtn.addEventListener('click', window.closeFavDrawer);
        }

        const favOverlay = document.getElementById('favOverlay');
        if (favOverlay) {
            favOverlay.addEventListener('click', window.closeFavDrawer);
        }

        // Clics globales (Delegación)
        document.addEventListener('click', (e) => {
            // Corazón en tarjeta de frutas
            const btnFav = e.target.closest('.btn-card-fav');
            if (btnFav) {
                e.preventDefault();
                e.stopPropagation();
                const fruitData = {
                    id: btnFav.dataset.id,
                    nombre: btnFav.dataset.nombre,
                    precio: btnFav.dataset.precio,
                    imagen: btnFav.dataset.imagen,
                    unidad: btnFav.dataset.unidad,
                    origen: btnFav.dataset.origen
                };
                window.toggleFavorite(fruitData);
                return;
            }

            // Añadir al pedido desde el drawer de favoritos
            const btnAddFav = e.target.closest('.btn-fav-add-cart');
            if (btnAddFav) {
                e.preventDefault();
                if (window.addToCart) {
                    window.addToCart({
                        id: btnAddFav.dataset.id,
                        nombre: btnAddFav.dataset.nombre,
                        precio: parseFloat(btnAddFav.dataset.precio) || 0,
                        imagen: btnAddFav.dataset.imagen,
                        unidad: btnAddFav.dataset.unidad || 'kg'
                    });
                }
                return;
            }

            // Quitar de favoritos desde el drawer
            const btnRemoveFav = e.target.closest('.btn-fav-remove');
            if (btnRemoveFav) {
                e.preventDefault();
                const id = btnRemoveFav.dataset.id;
                let favs = getFavorites().filter(item => String(item.id) !== String(id));
                saveFavorites(favs);
                return;
            }

            // Popover de Usuario (Hombre)
            const userTrigger = e.target.closest('#navUserTrigger');
            const userWrap = document.getElementById('navUserWrap');
            if (userTrigger && userWrap) {
                if (userTrigger.tagName.toLowerCase() === 'button' || window.innerWidth <= 992) {
                    e.preventDefault();
                    e.stopPropagation();
                    userWrap.classList.toggle('active');
                }
            } else if (!e.target.closest('#navUserWrap')) {
                const uWrap = document.getElementById('navUserWrap');
                if (uWrap) uWrap.classList.remove('active');
            }
        });

        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                window.closeFavDrawer();
                const userWrap = document.getElementById('navUserWrap');
                if (userWrap) userWrap.classList.remove('active');
            }
        });
    });
})();
