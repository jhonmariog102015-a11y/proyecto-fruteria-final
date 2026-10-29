/**
 * ==============================================================================
 * CARRITO UNIVERSAL Y SISTEMA DE TOASTS (principal/static/js/cart.js)
 * El Paso Frutería — Gestión de Canasta, LocalStorage y Checkout a WhatsApp
 * ==============================================================================
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'el_paso_frutas_cart';
    const WHATSAPP_PHONE = '573001234567';

    // Estado en memoria
    let cart = [];

    // Cargar desde LocalStorage de forma segura
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            cart = JSON.parse(stored);
        }
    } catch (e) {
        cart = [];
    }

    function saveCart() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
        } catch (e) {
            console.error('Error guardando carrito:', e);
        }
        updateCartUI();
    }

    function getCartCount() {
        return cart.reduce((total, item) => total + (item.cantidad || 1), 0);
    }

    function getCartTotal() {
        return cart.reduce((total, item) => total + (item.precio * (item.cantidad || 1)), 0);
    }

    // Mostrar Notificación Flotante Toast
    window.showToast = function (mensaje, actionText, actionCallback) {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = 'toast-alert';

        let actionBtnHtml = '';
        if (actionText && typeof actionCallback === 'function') {
            actionBtnHtml = `<button type="button" class="toast-action-btn">${actionText}</button>`;
        }

        toast.innerHTML = `
            <div class="toast-icon">✓</div>
            <div class="toast-text">${mensaje}</div>
            ${actionBtnHtml}
        `;

        if (actionText && typeof actionCallback === 'function') {
            const btn = toast.querySelector('.toast-action-btn');
            if (btn) {
                btn.addEventListener('click', () => {
                    actionCallback();
                    removeToast(toast);
                });
            }
        }

        container.appendChild(toast);

        // Auto remover tras 3.5 segundos
        const timer = setTimeout(() => {
            removeToast(toast);
        }, 3500);

        function removeToast(el) {
            clearTimeout(timer);
            el.classList.add('hiding');
            setTimeout(() => {
                if (el.parentElement) el.parentElement.removeChild(el);
            }, 300);
        }
    };

    // Apertura y Cierre del Drawer
    window.openCartDrawer = function () {
        const drawer = document.getElementById('cartDrawer');
        const overlay = document.getElementById('cartOverlay');
        if (drawer) drawer.classList.add('open');
        if (overlay) overlay.classList.add('open');
        renderCartItems();
    };

    window.closeCartDrawer = function () {
        const drawer = document.getElementById('cartDrawer');
        const overlay = document.getElementById('cartOverlay');
        if (drawer) drawer.classList.remove('open');
        if (overlay) overlay.classList.remove('open');
    };

    // Agregar Producto al Carrito
    window.addToCart = function (producto) {
        if (!producto || !producto.id) return;

        const id = String(producto.id);
        const existing = cart.find(item => String(item.id) === id);

        if (existing) {
            existing.cantidad = (existing.cantidad || 1) + 1;
        } else {
            cart.push({
                id: id,
                nombre: producto.nombre || 'Fruta Fresca',
                precio: parseFloat(producto.precio) || 0,
                unidad: producto.unidad || 'kg',
                imagen: producto.imagen || '',
                cantidad: 1
            });
        }

        saveCart();

        // Mostrar confirmación mediante Toast
        window.showToast(`¡${producto.nombre} agregado a la canasta!`, 'Ver Canasta', () => {
            window.openCartDrawer();
        });
    };

    // Modificar cantidad
    window.changeCartQty = function (id, delta) {
        const idStr = String(id);
        const item = cart.find(p => String(p.id) === idStr);
        if (!item) return;

        item.cantidad = (item.cantidad || 1) + delta;
        if (item.cantidad <= 0) {
            cart = cart.filter(p => String(p.id) !== idStr);
        }

        saveCart();
        renderCartItems();
    };

    // Eliminar producto
    window.removeFromCart = function (id) {
        const idStr = String(id);
        cart = cart.filter(p => String(p.id) !== idStr);
        saveCart();
        renderCartItems();
    };

    // Renderizar Elementos dentro del Drawer
    function renderCartItems() {
        const list = document.getElementById('cartItemsList');
        const emptyMsg = document.getElementById('cartEmptyMessage');
        const totalAmount = document.getElementById('cartTotalAmount');
        const btnWhatsapp = document.getElementById('btnSendWhatsapp');

        if (!list) return;

        list.innerHTML = '';

        if (cart.length === 0) {
            if (emptyMsg) emptyMsg.style.display = 'block';
            if (totalAmount) totalAmount.textContent = '$0';
            if (btnWhatsapp) {
                btnWhatsapp.classList.add('disabled');
                btnWhatsapp.disabled = true;
            }
            return;
        }

        if (emptyMsg) emptyMsg.style.display = 'none';

        const total = getCartTotal();
        if (totalAmount) {
            totalAmount.textContent = '$' + Math.round(total).toLocaleString('es-CO');
        }

        if (btnWhatsapp) {
            btnWhatsapp.classList.remove('disabled');
            btnWhatsapp.disabled = false;
        }

        cart.forEach(item => {
            const subtotal = item.precio * (item.cantidad || 1);
            const initial = (item.nombre || 'F').charAt(0).toUpperCase();

            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item';
            itemDiv.innerHTML = `
                <div class="cart-item-visual">
                    ${item.imagen ? `<img src="${item.imagen}" alt="${item.nombre}">` : initial}
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.nombre}</div>
                    <div class="cart-item-unit">$${Math.round(item.precio).toLocaleString('es-CO')} / ${item.unidad || 'kg'}</div>
                </div>
                <div class="cart-item-controls">
                    <button type="button" class="qty-btn" onclick="window.changeCartQty('${item.id}', -1)">-</button>
                    <span class="qty-val">${item.cantidad || 1}</span>
                    <button type="button" class="qty-btn" onclick="window.changeCartQty('${item.id}', 1)">+</button>
                </div>
                <div class="cart-item-subtotal">$${Math.round(subtotal).toLocaleString('es-CO')}</div>
                <button type="button" class="cart-item-remove" onclick="window.removeFromCart('${item.id}')" title="Quitar">✕</button>
            `;
            list.appendChild(itemDiv);
        });
    }

    // Actualizar Contadores en la Barra de Navegación y Barra Móvil
    function updateCartUI() {
        const badge = document.getElementById('cartBadge');
        const count = getCartCount();
        const total = getCartTotal();

        if (badge) {
            badge.textContent = count;
            badge.style.display = 'inline-flex';
        }

        // Barra flotante inferior fija para dispositivos móviles
        const mobileBar = document.getElementById('mobileCartBar');
        const mobileCount = document.getElementById('mobileCartCount');
        const mobileTotal = document.getElementById('mobileCartTotal');

        if (mobileBar) {
            if (count > 0) {
                mobileBar.classList.add('visible');
                if (mobileCount) mobileCount.textContent = count;
                if (mobileTotal) mobileTotal.textContent = '$' + Math.round(total).toLocaleString('es-CO');
            } else {
                mobileBar.classList.remove('visible');
            }
        }

        renderCartItems();
    }

    // Envío del Pedido a WhatsApp
    function setupWhatsappCheckout() {
        const btn = document.getElementById('btnSendWhatsapp');
        if (!btn) return;

        btn.addEventListener('click', () => {
            if (cart.length === 0) return;

            const total = getCartTotal();
            let lineas = [];
            lineas.push('¡Hola, Al Paso Frutería! Deseo realizar el siguiente pedido campesino:');
            lineas.push('');

            cart.forEach((item, index) => {
                const sub = Math.round(item.precio * (item.cantidad || 1)).toLocaleString('es-CO');
                lineas.push(`${index + 1}. ${item.nombre} x ${item.cantidad} ${item.unidad || 'kg'} — $${sub}`);
            });

            lineas.push('');
            lineas.push(`Total Estimado: $${Math.round(total).toLocaleString('es-CO')} COP`);
            lineas.push('¿Tienen disponibilidad para envío hoy? ¡Gracias!');

            const textoCodificado = encodeURIComponent(lineas.join('\n'));
            const urlWa = `https://wa.me/${WHATSAPP_PHONE}?text=${textoCodificado}`;
            window.open(urlWa, '_blank');
        });
    }

    // Inicialización al cargar el DOM
    document.addEventListener('DOMContentLoaded', () => {
        updateCartUI();
        setupWhatsappCheckout();

        // Botón abrir carrito
        const btnToggle = document.getElementById('cartToggleBtn');
        if (btnToggle) {
            btnToggle.addEventListener('click', (e) => {
                e.preventDefault();
                window.openCartDrawer();
            });
        }

        // Botón cerrar carrito y overlay
        const btnClose = document.getElementById('closeCartBtn');
        if (btnClose) {
            btnClose.addEventListener('click', window.closeCartDrawer);
        }

        const overlay = document.getElementById('cartOverlay');
        if (overlay) {
            overlay.addEventListener('click', window.closeCartDrawer);
        }

        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                window.closeCartDrawer();
            }
        });

        // Escuchar clics en botones de agregar en toda la página
        // 1. Carrusel de la landing page (index.html)
        document.addEventListener('click', (e) => {
            const btnCarousel = e.target.closest('.btn-add-fruit');
            if (btnCarousel) {
                e.preventDefault();
                const card = btnCarousel.closest('.carousel-card');
                if (card) {
                    const id = btnCarousel.dataset.id || card.dataset.id;
                    const nombre = btnCarousel.dataset.nombre || card.querySelector('h3')?.textContent.trim() || 'Fruta Fresca';
                    const priceEl = card.querySelector('.carousel-price.price-oferta, .carousel-price, .card-price-value');
                    const precioRaw = priceEl ? priceEl.textContent.replace(/[^0-9]/g, '') : '0';
                    const precio = parseFloat(precioRaw) || 0;
                    const unitEl = card.querySelector('.carousel-unit, .card-price-unit');
                    const unidad = unitEl ? unitEl.textContent.replace(/desde\s*\/\s*|\//gi, '').trim() : 'kg';
                    const imagen = card.querySelector('img')?.src || '';

                    window.addToCart({ id, nombre, precio, unidad, imagen });
                }
                return;
            }

            // 2. Tarjetas de catálogo (catalogo_frutas.html)
            const btnCatalog = e.target.closest('.add-btn');
            if (btnCatalog) {
                e.preventDefault();
                const card = btnCatalog.closest('.fruit-card');
                if (card) {
                    const id = card.dataset.id;
                    const nombre = card.querySelector('h3')?.textContent.trim();
                    const precioRaw = card.querySelector('.price-val')?.textContent.replace(/[^0-9]/g, '');
                    const precio = parseFloat(precioRaw) || 0;
                    const unidad = card.querySelector('.price-unit')?.textContent.replace(/desde\s*\/\s*/i, '').trim() || 'kg';
                    const imagen = card.querySelector('img')?.src || '';

                    window.addToCart({ id, nombre, precio, unidad, imagen });
                }
            }
        });
    });

})();
