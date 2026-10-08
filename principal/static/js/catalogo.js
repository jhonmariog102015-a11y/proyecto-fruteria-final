/**
 * CATÁLOGO COMPLETO DE FRUTAS - EL PASO FRUTERÍA (DISEÑO 4)
 * Manejo de filtros por pestañas, búsqueda en vivo, contador y carrito con WhatsApp
 */

document.addEventListener('DOMContentLoaded', () => {
    // Referencias DOM
    const catalogNavToggle = document.getElementById('catalogNavToggle');
    const catalogNavLinks = document.getElementById('catalogNavLinks');
    const chips = document.querySelectorAll('.filter-chip');
    const cards = document.querySelectorAll('.fruit-card');
    const searchInput = document.getElementById('fruitSearch');
    const counterElem = document.getElementById('contadorReferencias');
    const clearSearchBtn = document.getElementById('clearSearch');
    const cartToggleBtn = document.getElementById('cartToggleBtn');
    const cartDrawer = document.getElementById('cartDrawer');
    const closeCartBtn = document.getElementById('closeCartBtn');
    const cartOverlay = document.getElementById('cartOverlay');
    const cartItemsContainer = document.getElementById('cartItemsList');
    const cartBadge = document.getElementById('cartBadge');
    const cartTotalAmount = document.getElementById('cartTotalAmount');
    const btnSendWhatsapp = document.getElementById('btnSendWhatsapp');
    const cartEmptyMsg = document.getElementById('cartEmptyMessage');

    if (catalogNavToggle && catalogNavLinks) {
        const setNavOpen = (isOpen) => {
            catalogNavToggle.classList.toggle('open', isOpen);
            catalogNavLinks.classList.toggle('active-menu', isOpen);
            catalogNavToggle.setAttribute('aria-expanded', String(isOpen));
            catalogNavToggle.setAttribute('aria-label', isOpen ? 'Cerrar menú' : 'Abrir menú');
        };

        catalogNavToggle.addEventListener('click', () => {
            setNavOpen(catalogNavToggle.getAttribute('aria-expanded') !== 'true');
        });

        catalogNavLinks.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => setNavOpen(false));
        });

        document.addEventListener('keydown', event => {
            if (event.key === 'Escape') setNavOpen(false);
        });

        document.addEventListener('click', event => {
            if (!catalogNavToggle.contains(event.target) && !catalogNavLinks.contains(event.target)) {
                setNavOpen(false);
            }
        });
    }

    let activeFilter = 'all';
    let searchQuery = '';
    let cart = [];

    // Cargar carrito previo de localStorage si existe
    try {
        const saved = localStorage.getItem('el_paso_frutas_cart');
        if (saved) cart = JSON.parse(saved);
    } catch(e) {}

    // Filtrar catálogo (chips + búsqueda)
    function applyFilters() {
        let visibleCount = 0;

        cards.forEach(card => {
            const cardCat = card.dataset.categoria || '';
            const cardTitle = (card.querySelector('h3')?.textContent || '').toLowerCase();
            const cardOrigin = (card.querySelector('.fruit-origin')?.textContent || '').toLowerCase();

            const matchesCategory = (activeFilter === 'all' || cardCat === activeFilter);
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

    // Carrito de compras
    function saveCart() {
        try {
            localStorage.setItem('el_paso_frutas_cart', JSON.stringify(cart));
        } catch(e) {}
        updateCartUI();
    }

    function parsePrice(priceStr) {
        if (!priceStr) return 0;
        const clean = priceStr.replace(/[^0-9]/g, '');
        return parseInt(clean, 10) || 0;
    }

    function addToCart(fruit) {
        const existing = cart.find(item => item.id === fruit.id);
        if (existing) {
            existing.qty += 1;
        } else {
            cart.push({ ...fruit, qty: 1 });
        }
        saveCart();
        showToast(`🧺 Agregado: <b>${fruit.name}</b> a tu canasta`);
    }

    function updateQty(id, change) {
        const item = cart.find(i => i.id === id);
        if (!item) return;
        item.qty += change;
        if (item.qty <= 0) {
            cart = cart.filter(i => i.id !== id);
        }
        saveCart();
    }

    function removeFromCart(id) {
        cart = cart.filter(i => i.id !== id);
        saveCart();
    }

    function updateCartUI() {
        const totalItems = cart.reduce((acc, i) => acc + i.qty, 0);
        const totalPrice = cart.reduce((acc, i) => acc + (i.priceNum * i.qty), 0);

        if (cartBadge) {
            cartBadge.textContent = totalItems;
            cartBadge.style.display = totalItems > 0 ? 'inline-flex' : 'none';
        }

        if (cartTotalAmount) {
            cartTotalAmount.textContent = `$${totalPrice.toLocaleString('es-CO')}`;
        }

        if (!cartItemsContainer) return;

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '';
            if (cartEmptyMsg) cartEmptyMsg.style.display = 'block';
            if (btnSendWhatsapp) btnSendWhatsapp.classList.add('disabled');
            return;
        }

        if (cartEmptyMsg) cartEmptyMsg.style.display = 'none';
        if (btnSendWhatsapp) btnSendWhatsapp.classList.remove('disabled');

        cartItemsContainer.innerHTML = cart.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-emoji">${item.emoji}</div>
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-unit">${item.priceStr} • ${item.unit}</div>
                </div>
                <div class="cart-item-controls">
                    <button class="qty-btn btn-minus" data-id="${item.id}">−</button>
                    <span class="qty-val">${item.qty}</span>
                    <button class="qty-btn btn-plus" data-id="${item.id}">+</button>
                </div>
                <div class="cart-item-subtotal">$${(item.priceNum * item.qty).toLocaleString('es-CO')}</div>
                <button class="cart-item-remove" data-id="${item.id}" title="Eliminar">✕</button>
            </div>
        `).join('');

        // Eventos en controles de cantidad y eliminar
        cartItemsContainer.querySelectorAll('.btn-minus').forEach(b => {
            b.addEventListener('click', () => updateQty(b.dataset.id, -1));
        });
        cartItemsContainer.querySelectorAll('.btn-plus').forEach(b => {
            b.addEventListener('click', () => updateQty(b.dataset.id, 1));
        });
        cartItemsContainer.querySelectorAll('.cart-item-remove').forEach(b => {
            b.addEventListener('click', () => removeFromCart(b.dataset.id));
        });
    }

    // Conectar botones "+" de las tarjetas del catálogo
    cards.forEach(card => {
        const addBtn = card.querySelector('.add-btn');
        if (!addBtn) return;

        addBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = card.dataset.id || card.querySelector('h3')?.textContent.trim();
            const name = card.querySelector('h3')?.textContent.trim() || 'Fruta';
            const priceStr = card.querySelector('.price-val')?.textContent.trim() || '$0';
            const unit = card.querySelector('.price-unit')?.textContent.trim() || '';
            const emoji = card.querySelector('.fruit-card-emoji')?.textContent.trim() || '🍊';
            const priceNum = parsePrice(priceStr);

            addToCart({ id, name, priceStr, unit, emoji, priceNum });

            // Micro-animación en botón
            addBtn.classList.add('added');
            setTimeout(() => addBtn.classList.remove('added'), 600);
        });
    });

    // Abrir / Cerrar Drawer del carrito
    function openCart() {
        if (cartDrawer && cartOverlay) {
            cartDrawer.classList.add('open');
            cartOverlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeCart() {
        if (cartDrawer && cartOverlay) {
            cartDrawer.classList.remove('open');
            cartOverlay.classList.remove('open');
            document.body.style.overflow = '';
        }
    }

    if (cartToggleBtn) cartToggleBtn.addEventListener('click', openCart);
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCart);

    // Enviar pedido por WhatsApp
    if (btnSendWhatsapp) {
        btnSendWhatsapp.addEventListener('click', (e) => {
            if (cart.length === 0) {
                e.preventDefault();
                showToast('⚠️ Tu canasta está vacía. Selecciona frutas primero.');
                return;
            }

            const totalPrice = cart.reduce((acc, i) => acc + (i.priceNum * i.qty), 0);
            let message = `*¡Hola El Paso Frutería! Deseo realizar el siguiente pedido de frutas frescas:*\n\n`;

            cart.forEach((item, index) => {
                const sub = (item.priceNum * item.qty).toLocaleString('es-CO');
                message += `${index + 1}. ${item.emoji} *${item.name}* x ${item.qty} ${item.unit} — $${sub}\n`;
            });

            message += `\n*TOTAL ESTIMADO:* $${totalPrice.toLocaleString('es-CO')}\n`;
            message += `📍 *Ciudad:* Sogamoso, Boyacá\n`;
            message += `_Pedido generado desde el catálogo online de frutas de El Paso Frutería._`;

            const encoded = encodeURIComponent(message);
            const waUrl = `https://api.whatsapp.com/send?phone=573001234567&text=${encoded}`;
            window.open(waUrl, '_blank');
        });
    }

    // Toast flotante
    function showToast(message) {
        let toast = document.getElementById('fruitToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'fruitToast';
            toast.className = 'fruit-toast';
            document.body.appendChild(toast);
        }
        toast.innerHTML = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 2600);
    }

    // Inicializar
    applyFilters();
    updateCartUI();
});
