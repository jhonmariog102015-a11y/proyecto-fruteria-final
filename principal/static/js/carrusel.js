/**
 * ==============================================================================
 * CARRUSEL DE FRUTAS CON PESTAÑAS Y CONTROL TÁCTIL (carrusel.js)
 * Maneja la interacción en el cliente: filtrado reactivo, navegación suave,
 * arrastre táctil (swipe/drag), indicadores de puntos (dots) y notificaciones toast.
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    // --------------------------------------------------------------------------
    // 1. SELECCIÓN DE ELEMENTOS DEL DOM
    // --------------------------------------------------------------------------
    const track = document.getElementById('fruitCarouselTrack');       // Contenedor desplazable
    const prevBtn = document.getElementById('carouselPrev');           // Flecha retroceder
    const nextBtn = document.getElementById('carouselNext');           // Flecha avanzar
    const tabs = document.querySelectorAll('.carousel-tab');           // Botones de filtro de categorías
    const dotsContainer = document.getElementById('carouselDots');     // Contenedor de puntos indicadores
    const cards = Array.from(track ? track.querySelectorAll('.carousel-card') : []); // Tarjetas de frutas

    // Si el carrusel no existe en la página o no hay productos, detenemos la ejecución
    if (!track || cards.length === 0) return;

    let activeFilter = 'all'; // Filtro seleccionado ('all', 'citricos', 'tropicales', etc.)

    // --------------------------------------------------------------------------
    // 2. GENERACIÓN DINÁMICA DE INDICADORES (DOTS)
    // --------------------------------------------------------------------------
    function updateDots() {
        if (!dotsContainer) return;
        dotsContainer.innerHTML = '';
        
        // Filtramos solo las tarjetas que están visibles según la pestaña activa
        const visibleCards = cards.filter(c => !c.classList.contains('hidden-carousel-card'));
        const totalSlides = Math.ceil(visibleCards.length / getCardsPerView());

        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('button');
            dot.className = `carousel-dot ${i === 0 ? 'active' : ''}`;
            dot.setAttribute('aria-label', `Ir al slide ${i + 1}`);
            
            // Evento: al hacer clic en un punto, desliza exactamente a esa página de tarjetas
            dot.addEventListener('click', () => {
                const cardWidth = visibleCards[0]?.offsetWidth || 280;
                const gap = 24; // Espacio entre tarjetas en píxeles
                const scrollAmount = i * (cardWidth + gap) * getCardsPerView();
                track.scrollTo({ left: scrollAmount, behavior: 'smooth' });
                setActiveDot(i);
            });
            dotsContainer.appendChild(dot);
        }
    }

    // Calcula cuántas tarjetas caben en pantalla según el ancho de la ventana
    function getCardsPerView() {
        const width = window.innerWidth;
        if (width < 640) return 1;    // Móviles
        if (width < 992) return 2;    // Tablets
        if (width < 1280) return 3;   // Portátiles
        return 4;                     // Pantallas de escritorio anchas
    }

    // Marca visualmente el punto (dot) activo
    function setActiveDot(index) {
        if (!dotsContainer) return;
        const dots = dotsContainer.querySelectorAll('.carousel-dot');
        dots.forEach((dot, idx) => {
            dot.classList.toggle('active', idx === index);
        });
    }

    // --------------------------------------------------------------------------
    // 3. NAVEGACIÓN MEDIANTE BOTONES DE FLECHA (PREV / NEXT)
    // --------------------------------------------------------------------------
    function scrollCarousel(direction) {
        const visibleCards = cards.filter(c => !c.classList.contains('hidden-carousel-card'));
        if (visibleCards.length === 0) return;
        
        const cardWidth = visibleCards[0].offsetWidth;
        const gap = 24;
        const step = (cardWidth + gap) * Math.max(1, Math.floor(getCardsPerView() / 1.5));
        
        track.scrollBy({
            left: direction * step,
            behavior: 'smooth'
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => scrollCarousel(-1)); // Desplaza a la izquierda
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', () => scrollCarousel(1));  // Desplaza a la derecha
    }

    // --------------------------------------------------------------------------
    // 4. ACTUALIZACIÓN AUTOMÁTICA DE DOTS AL HACER SCROLL (DEBOUNCE)
    // --------------------------------------------------------------------------
    let scrollTimeout;
    track.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const visibleCards = cards.filter(c => !c.classList.contains('hidden-carousel-card'));
            if (visibleCards.length === 0) return;
            const cardWidth = visibleCards[0].offsetWidth;
            const gap = 24;
            const currentIndex = Math.round(track.scrollLeft / ((cardWidth + gap) * getCardsPerView()));
            setActiveDot(currentIndex);
        }, 100);
    });

    // --------------------------------------------------------------------------
    // 5. FILTRADO REACTIVO POR PESTAÑAS (TABS)
    // --------------------------------------------------------------------------
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Activa visualmente la pestaña seleccionada
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            activeFilter = tab.dataset.filter || 'all';

            // Oculta o muestra tarjetas aplicando animación CSS 'fadeInUp'
            cards.forEach(card => {
                const cardCat = (card.dataset.categoria || '').trim();
                const match = activeFilter === 'all' || cardCat.split(/\s+/).includes(activeFilter) || cardCat === activeFilter;
                
                if (match) {
                    card.classList.remove('hidden-carousel-card');
                    card.style.animation = 'fadeInUp 0.4s ease forwards';
                } else {
                    card.classList.add('hidden-carousel-card');
                }
            });

            // Resetea la posición del scroll al inicio y recalcula los puntos
            track.scrollTo({ left: 0, behavior: 'smooth' });
            updateDots();
        });
    });

    // --------------------------------------------------------------------------
    // 6. ARRASTRE CON EL MOUSE (DRAG & SWIPE TÁCTIL)
    // --------------------------------------------------------------------------
    let isDown = false;
    let startX;
    let scrollLeft;

    track.addEventListener('mousedown', (e) => {
        isDown = true;
        track.classList.add('dragging');
        startX = e.pageX - track.offsetLeft;
        scrollLeft = track.scrollLeft;
    });

    track.addEventListener('mouseleave', () => {
        isDown = false;
        track.classList.remove('dragging');
    });

    track.addEventListener('mouseup', () => {
        isDown = false;
        track.classList.remove('dragging');
    });

    track.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - track.offsetLeft;
        const walk = (x - startX) * 1.5; // Multiplicador de velocidad de arrastre
        track.scrollLeft = scrollLeft - walk;
    });

    // --------------------------------------------------------------------------
    // 7. BOTÓN RÁPIDO DE AÑADIR PRODUCTO Y NOTIFICACIÓN TOAST
    // --------------------------------------------------------------------------
    const addBtns = document.querySelectorAll('.carousel-card .btn-add-fruit');
    addBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const fruitName = btn.dataset.nombre || 'Fruta fresca';
            btn.classList.add('added');
            
            showToast(`🛒 "${fruitName}" agregado a tu lista de compra`);
            
            setTimeout(() => {
                btn.classList.remove('added');
            }, 1200);
        });
    });

    // Muestra una notificación flotante estilo Toast en pantalla
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
        }, 2800);
    }

    // Recalcula los puntos cuando el usuario cambia el tamaño de la ventana
    window.addEventListener('resize', () => {
        updateDots();
    });

    // Inicialización al cargar la página
    updateDots();
});

