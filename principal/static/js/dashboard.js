/**
 * ============================================================================
 * CONTROLADOR INTERACTIVO DEL DASHBOARD (principal/static/js/dashboard.js)
 * ============================================================================
 * NOTA TÉCNICA PARA EL EQUIPO (GAES):
 * Este archivo centraliza toda la lógica JavaScript que antes estaba incrustada
 * dentro de <script> en 'dashboard.html' (~650 líneas), siguiendo las buenas
 * prácticas de separación de responsabilidades (HTML semántico vs lógica JS)
 * y permitiendo que el navegador almacene el script en caché.
 *
 * Módulos incluidos:
 * 1. Modales CRUD de Productos y cálculo en vivo de márgenes de ganancia.
 * 2. Modales CRUD de Categorías y Proveedores Agrícolas.
 * 3. Modales CRUD de Usuarios y Roles (RBAC).
 * 4. Modales CRUD de Ventas y calculadora rápida de frutas por peso.
 * 5. Navegación SPA por pestañas (#resumen, #inventario, #ventas, #proveedores, #usuarios).
 * 6. Filtros combinados en vivo y buscador contextual.
 * 7. Inicialización segura de gráficos ejecutivos con Chart.js.
 * ============================================================================
 */

// ============================================================================
// 1. MODALES DE PRODUCTOS Y CÁLCULO DE MÁRGENES
// ============================================================================
function abrirModalNuevoProducto() {
  document.getElementById('modalNuevoProducto').classList.add('open');
  document.getElementById('nuevo_nombre').focus();
}

function cerrarModalNuevoProducto() {
  document.getElementById('modalNuevoProducto').classList.remove('open');
}

function toggleOfertaNuevo() {
  const chk = document.getElementById('nuevo_en_oferta');
  const wrap = document.getElementById('wrapOfertaNuevo');
  wrap.style.display = chk.checked ? 'block' : 'none';
  if (!chk.checked) {
    document.getElementById('nuevo_precio_oferta').value = '';
  }
  calcularMargenNuevo();
}

function calcularMargenNuevo() {
  const costo = parseFloat(document.getElementById('nuevo_costo').value) || 0;
  const precio = parseFloat(document.getElementById('nuevo_precio').value) || 0;
  const enOferta = document.getElementById('nuevo_en_oferta').checked;
  const precioOferta = parseFloat(document.getElementById('nuevo_precio_oferta').value) || 0;

  const precioEfectivo = (enOferta && precioOferta > 0) ? precioOferta : precio;
  const ganancia = precioEfectivo - costo;
  const margenPorcentaje = costo > 0 ? ((ganancia / costo) * 100).toFixed(1) : '0.0';

  const valBox = document.getElementById('calcValNuevo');
  valBox.textContent = `+$${Math.round(ganancia).toLocaleString('es-CO')} COP (${margenPorcentaje}%)`;
  valBox.style.color = ganancia >= 0 ? '#15803d' : '#dc2626';
}

function abrirModalEditar(btn) {
  const id = btn.getAttribute('data-id');
  const nombre = btn.getAttribute('data-nombre');
  const catId = btn.getAttribute('data-categoria');
  const costo = btn.getAttribute('data-costo');
  const precio = btn.getAttribute('data-precio');
  const enOferta = btn.getAttribute('data-oferta') === 'true';
  const precioOferta = btn.getAttribute('data-precio-oferta');
  const stock = btn.getAttribute('data-stock');
  const stockMin = btn.getAttribute('data-stock-min');
  const unidad = btn.getAttribute('data-unidad');
  const origen = btn.getAttribute('data-origen');
  const imagen = btn.getAttribute('data-imagen');
  const estado = btn.getAttribute('data-estado');

  document.getElementById('formEditarProducto').action = `/dashboard/producto/${id}/editar/`;

  document.getElementById('edit_nombre').value = nombre || '';
  document.getElementById('edit_categoria').value = catId || '';
  document.getElementById('edit_costo').value = costo || '';
  document.getElementById('edit_precio').value = precio || '';
  document.getElementById('edit_stock').value = stock || '';
  document.getElementById('edit_stock_min').value = stockMin || '';
  document.getElementById('edit_unidad').value = unidad || 'kg';
  document.getElementById('edit_origen').value = origen || '';
  document.getElementById('edit_imagen').value = imagen || '';
  document.getElementById('edit_estado').value = estado || 'Disponible';

  const chkOferta = document.getElementById('edit_en_oferta');
  chkOferta.checked = enOferta;
  document.getElementById('wrapOfertaEditar').style.display = enOferta ? 'block' : 'none';
  document.getElementById('edit_precio_oferta').value = precioOferta || '';

  calcularMargenEditar();
  document.getElementById('modalEditarProducto').classList.add('open');
}

function cerrarModalEditar() {
  document.getElementById('modalEditarProducto').classList.remove('open');
}

function toggleOfertaEditar() {
  const chk = document.getElementById('edit_en_oferta');
  const wrap = document.getElementById('wrapOfertaEditar');
  wrap.style.display = chk.checked ? 'block' : 'none';
  if (!chk.checked) {
    document.getElementById('edit_precio_oferta').value = '';
  }
  calcularMargenEditar();
}

function calcularMargenEditar() {
  const costo = parseFloat(document.getElementById('edit_costo').value) || 0;
  const precio = parseFloat(document.getElementById('edit_precio').value) || 0;
  const enOferta = document.getElementById('edit_en_oferta').checked;
  const precioOferta = parseFloat(document.getElementById('edit_precio_oferta').value) || 0;

  const precioEfectivo = (enOferta && precioOferta > 0) ? precioOferta : precio;
  const ganancia = precioEfectivo - costo;
  const margenPorcentaje = costo > 0 ? ((ganancia / costo) * 100).toFixed(1) : '0.0';

  const valBox = document.getElementById('calcValEditar');
  valBox.textContent = `+$${Math.round(ganancia).toLocaleString('es-CO')} COP (${margenPorcentaje}%)`;
  valBox.style.color = ganancia >= 0 ? '#15803d' : '#dc2626';
}

function abrirModalEliminar(btn) {
  const id = btn.getAttribute('data-id');
  const nombre = btn.getAttribute('data-nombre');
  document.getElementById('formEliminarProducto').action = `/dashboard/producto/${id}/eliminar/`;
  document.getElementById('eliminarNombreProducto').textContent = `"${nombre}"`;
  document.getElementById('modalEliminarProducto').classList.add('open');
}

function cerrarModalEliminar() {
  document.getElementById('modalEliminarProducto').classList.remove('open');
}

// ============================================================================
// 2. MODALES DE CATEGORÍAS Y PROVEEDORES AGRÍCOLAS
// ============================================================================
function abrirModalNuevaCategoria() {
  document.getElementById('modalNuevaCategoria').classList.add('open');
  document.getElementById('cat_nombre').focus();
}

function cerrarModalNuevaCategoria() {
  document.getElementById('modalNuevaCategoria').classList.remove('open');
}

function abrirModalNuevoProveedor() {
  document.getElementById('modalNuevoProveedor').classList.add('open');
  const input = document.getElementById('nuevo_prov_razon');
  if (input) input.focus();
}

function cerrarModalNuevoProveedor() {
  document.getElementById('modalNuevoProveedor').classList.remove('open');
}

function abrirModalEditarProveedor(btn) {
  const id = btn.getAttribute('data-id');
  document.getElementById('formEditarProveedor').action = `/dashboard/proveedor/${id}/editar/`;
  document.getElementById('edit_prov_razon').value = btn.getAttribute('data-razon') || '';
  document.getElementById('edit_prov_nit').value = btn.getAttribute('data-nit') || '';
  document.getElementById('edit_prov_contacto').value = btn.getAttribute('data-contacto') || '';
  document.getElementById('edit_prov_telefono').value = btn.getAttribute('data-telefono') || '';
  document.getElementById('edit_prov_email').value = btn.getAttribute('data-email') || '';
  document.getElementById('edit_prov_calif').value = btn.getAttribute('data-calificacion') || '5.0';
  document.getElementById('edit_prov_estado').value = btn.getAttribute('data-estado') || 'Activo';
  document.getElementById('modalEditarProveedor').classList.add('open');
}

function cerrarModalEditarProveedor() {
  document.getElementById('modalEditarProveedor').classList.remove('open');
}

function abrirModalEliminarProveedor(btn) {
  const id = btn.getAttribute('data-id');
  document.getElementById('formEliminarProveedor').action = `/dashboard/proveedor/${id}/eliminar/`;
  document.getElementById('eliminarRazonProveedor').textContent = `"${btn.getAttribute('data-razon')}"`;
  document.getElementById('modalEliminarProveedor').classList.add('open');
}

function cerrarModalEliminarProveedor() {
  document.getElementById('modalEliminarProveedor').classList.remove('open');
}

// ============================================================================
// 3. MODALES DE USUARIOS Y ROLES (RBAC)
// ============================================================================
function abrirModalNuevoUsuario() {
  const modal = document.getElementById('modalNuevoUsuario');
  if (modal) {
    modal.classList.add('open');
    const input = document.getElementById('nuevo_usu_username');
    if (input) input.focus();
  }
}

function cerrarModalNuevoUsuario() {
  const modal = document.getElementById('modalNuevoUsuario');
  if (modal) modal.classList.remove('open');
}

function abrirModalEditarUsuario(btn) {
  const id = btn.getAttribute('data-id');
  const username = btn.getAttribute('data-username');
  const firstname = btn.getAttribute('data-firstname');
  const lastname = btn.getAttribute('data-lastname');
  const email = btn.getAttribute('data-email');
  const telefono = btn.getAttribute('data-telefono');
  const rol = btn.getAttribute('data-rol');
  const estado = btn.getAttribute('data-estado');

  document.getElementById('formEditarUsuario').action = `/dashboard/usuario/${id}/editar/`;
  document.getElementById('edit_usu_username').value = username || '';
  document.getElementById('edit_usu_firstname').value = firstname || '';
  document.getElementById('edit_usu_lastname').value = lastname || '';
  document.getElementById('edit_usu_email').value = email || '';
  document.getElementById('edit_usu_telefono').value = telefono || '';
  document.getElementById('edit_usu_rol').value = rol || 'cajero';
  document.getElementById('edit_usu_estado').value = estado || 'activo';
  document.getElementById('edit_usu_password').value = '';

  document.getElementById('modalEditarUsuario').classList.add('open');
}

function cerrarModalEditarUsuario() {
  const modal = document.getElementById('modalEditarUsuario');
  if (modal) modal.classList.remove('open');
}

function abrirModalEliminarUsuario(btn) {
  const id = btn.getAttribute('data-id');
  const username = btn.getAttribute('data-username');
  const rol = btn.getAttribute('data-rol');

  document.getElementById('formEliminarUsuario').action = `/dashboard/usuario/${id}/eliminar/`;
  document.getElementById('eliminarNombreUsuario').textContent = `@${username}`;
  document.getElementById('eliminarRolUsuario').textContent = `Rol asignado: ${rol ? rol.toUpperCase() : 'USUARIO'}`;

  document.getElementById('modalEliminarUsuario').classList.add('open');
}

function cerrarModalEliminarUsuario() {
  const modal = document.getElementById('modalEliminarUsuario');
  if (modal) modal.classList.remove('open');
}

// ============================================================================
// 4. MODALES DE VENTAS Y CALCULADORA DE FRUTAS POR PESO
// ============================================================================
function abrirModalNuevaVenta() {
  const modal = document.getElementById('modalNuevaVenta');
  if (modal) {
    modal.classList.add('open');
    recalcularTotalesNuevaVenta();
  }
}

function cerrarModalNuevaVenta() {
  const modal = document.getElementById('modalNuevaVenta');
  if (modal) modal.classList.remove('open');
}

function recalcularTotalesNuevaVenta() {
  const sub = parseFloat(document.getElementById('nueva_venta_subtotal').value) || 0;
  let desc = parseFloat(document.getElementById('nueva_venta_descuento').value) || 0;
  if (desc > sub) {
    desc = sub;
    document.getElementById('nueva_venta_descuento').value = desc.toFixed(2);
  }
  const total = Math.max(0, sub - desc);
  document.getElementById('nueva_venta_total').value = total.toFixed(2);
  document.getElementById('nv_lbl_total').textContent = '$' + total.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + ' COP';
}

function sumarFrutaNuevaVenta() {
  const sel = document.getElementById('nv_sel_fruta');
  const precio = parseFloat(sel.options[sel.selectedIndex]?.getAttribute('data-precio')) || 0;
  const cant = parseFloat(document.getElementById('nv_cant_fruta').value) || 0;
  if (precio > 0 && cant > 0) {
    const monto = precio * cant;
    let sub = parseFloat(document.getElementById('nueva_venta_subtotal').value) || 0;
    sub += monto;
    document.getElementById('nueva_venta_subtotal').value = sub.toFixed(2);
    recalcularTotalesNuevaVenta();
  }
}

function abrirModalEditarVenta(btn) {
  const id = btn.getAttribute('data-id');
  const cliente = btn.getAttribute('data-cliente') || '';
  const origen = btn.getAttribute('data-origen') || 'Tienda Física';
  const medio = btn.getAttribute('data-medio') || 'Efectivo';
  const subtotal = parseFloat(btn.getAttribute('data-subtotal')) || 0;
  const descuento = parseFloat(btn.getAttribute('data-descuento')) || 0;
  const total = parseFloat(btn.getAttribute('data-total')) || 0;
  const estado = btn.getAttribute('data-estado') || 'Completada';

  document.getElementById('formEditarVenta').action = `/dashboard/venta/${id}/editar/`;
  document.getElementById('lblEditarIdVenta').textContent = `#VTA-${id}`;
  document.getElementById('edit_venta_origen').value = origen;
  document.getElementById('edit_venta_cliente').value = cliente;
  document.getElementById('edit_venta_medio').value = medio;
  document.getElementById('edit_venta_estado').value = estado;
  document.getElementById('edit_venta_subtotal').value = subtotal.toFixed(2);
  document.getElementById('edit_venta_descuento').value = descuento.toFixed(2);
  document.getElementById('edit_venta_total').value = total.toFixed(2);
  document.getElementById('edit_lbl_total').textContent = '$' + total.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + ' COP';

  const modal = document.getElementById('modalEditarVenta');
  if (modal) modal.classList.add('open');
}

function cerrarModalEditarVenta() {
  const modal = document.getElementById('modalEditarVenta');
  if (modal) modal.classList.remove('open');
}

function recalcularTotalesEditarVenta() {
  const sub = parseFloat(document.getElementById('edit_venta_subtotal').value) || 0;
  let desc = parseFloat(document.getElementById('edit_venta_descuento').value) || 0;
  if (desc > sub) {
    desc = sub;
    document.getElementById('edit_venta_descuento').value = desc.toFixed(2);
  }
  const total = Math.max(0, sub - desc);
  document.getElementById('edit_venta_total').value = total.toFixed(2);
  document.getElementById('edit_lbl_total').textContent = '$' + total.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + ' COP';
}

function abrirModalEliminarVenta(btn) {
  const id = btn.getAttribute('data-id');
  const total = parseFloat(btn.getAttribute('data-total')) || 0;
  const cajero = btn.getAttribute('data-cajero') || '';

  document.getElementById('formEliminarVenta').action = `/dashboard/venta/${id}/eliminar/`;
  document.getElementById('eliminarIdVenta').textContent = `#VTA-${id}`;
  document.getElementById('eliminarTotalVenta').textContent = `Total Neto: $${total.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} COP • Cajero: ${cajero}`;

  const modal = document.getElementById('modalEliminarVenta');
  if (modal) modal.classList.add('open');
}

function cerrarModalEliminarVenta() {
  const modal = document.getElementById('modalEliminarVenta');
  if (modal) modal.classList.remove('open');
}

// ============================================================================
// 5. NAVEGACIÓN SPA DE SECCIONES Y FILTROS COMBINADOS EN VIVO
// ============================================================================
let filtroEstadoActual = 'todos';

function filtrarPorEstado(tipo, btn) {
  filtroEstadoActual = tipo;
  document.querySelectorAll('.quick-filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  aplicarFiltrosCombinados();
}

function mostrarSeccion(seccionId, navEl) {
  const secKey = seccionId.replace('seccion-', '');

  document.querySelectorAll('.dashboard-section').forEach(sec => {
    sec.classList.remove('active');
    sec.style.display = 'none';
  });

  const secDestino = document.getElementById('seccion-' + secKey);
  if (secDestino) {
    secDestino.classList.add('active');
    secDestino.style.display = 'block';
  }

  document.querySelectorAll('.navigation a[data-section]').forEach(link => {
    link.classList.remove('active');
    link.removeAttribute('aria-current');
  });

  const navActivo = navEl || document.querySelector(`.navigation a[data-section="${secKey}"]`);
  if (navActivo) {
    navActivo.classList.add('active');
    navActivo.setAttribute('aria-current', 'page');
  }

  const breadcrumb = document.getElementById('topbarBreadcrumb');
  const inputBuscar = document.getElementById('inputBuscarProducto');
  if (secKey === 'resumen') {
    if (breadcrumb) breadcrumb.innerHTML = '» &nbsp; Al Paso Frutería • <strong>Resumen Ejecutivo y Alertas de Inventario</strong>';
    if (inputBuscar) inputBuscar.placeholder = 'Buscar en el catálogo...';
  } else if (secKey === 'inventario') {
    if (breadcrumb) breadcrumb.innerHTML = '» &nbsp; Al Paso Frutería • <strong>Catálogo e Inventario en Tiempo Real</strong>';
    if (inputBuscar) inputBuscar.placeholder = 'Buscar producto o categoría...';
  } else if (secKey === 'ventas') {
    if (breadcrumb) breadcrumb.innerHTML = '» &nbsp; Al Paso Frutería • <strong>Gestión y Control de Ventas</strong>';
    if (inputBuscar) inputBuscar.placeholder = 'Buscar venta por ID, cajero, medio de pago...';
  } else if (secKey === 'proveedores') {
    if (breadcrumb) breadcrumb.innerHTML = '» &nbsp; Al Paso Frutería • <strong>Directorio de Productores y Proveedores</strong>';
    if (inputBuscar) inputBuscar.placeholder = 'Buscar razón social, NIT o contacto...';
  } else if (secKey === 'usuarios') {
    if (breadcrumb) breadcrumb.innerHTML = '» &nbsp; Al Paso Frutería • <strong>Administradores del Sistema y Roles</strong>';
    if (inputBuscar) inputBuscar.placeholder = 'Buscar administrador o email...';
  }

  const mainContainer = document.querySelector('.main');
  if (mainContainer) {
    mainContainer.scrollTo({ top: 0, behavior: 'smooth' });
  }

  if (history.replaceState) {
    history.replaceState(null, null, '#' + secKey);
  }
}

// ============================================================================
// 5.1. BUSCADOR GLOBAL INTELIGENTE (SIN ACENTOS) Y FILTROS DE RESUMEN / TABLAS
// ============================================================================
// NOTA TÉCNICA PARA EL EQUIPO (GAES):
// 1. Se implementó 'normalizarTexto()' para que la búsqueda funcione con o sin
//    tildes/diacríticos (ej. buscar "pina" o "piña", "citricos" o "cítricos").
// 2. Ahora 'ejecutarBusquedaActiva()' filtra en vivo también dentro de la pestaña
//    '#resumen' (tablas de rentabilidad por producto, tabla de ganancias por ventas
//    y gráfica Chart.js de márgenes), además de desplegar un menú rápido de
//    resultados ('#globalSearchDropdown') con acceso directo a cada registro.
// 3. Se agregó 'filtrarGananciasPeriodo(periodo)' para consultar las ganancias
//    netas reales por Día (Hoy), Mes, Año, General (Histórico) y Catálogo Bodega,
//    actualizando tarjetas KPI, tablas y gráficas simultáneamente.
// 4. Se integró 'sincronizarEstadoTiempoReal()' mediante polling ligero cada 3s
//    contra '/api/estado-tiempo-real/' para reflejar cualquier cambio de pedido
//    o venta en tiempo real para todos los usuarios conectados.
// ============================================================================

let periodoGananciaActual = 'general';
let modoGraficaIzquierda = 'categorias';
let chartCategoriasInstance = null;
let chartMargenesInstance = null;

// Estado reactivo en memoria sincronizado con el backend
let estadoDashboard = {
  catLabels: [],
  catData: [],
  productosResumen: [],
  gananciasPeriodos: {},
  ventasJson: [],
  ultimaFirma: ''
};

function normalizarTexto(texto) {
  return String(texto || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

function formatearCOP(valor) {
  return '$' + Math.round(Number(valor) || 0).toLocaleString('es-CO');
}

function ejecutarBusquedaActiva() {
  const input = document.getElementById('inputBuscarProducto');
  const terminoRaw = input ? input.value.trim() : '';
  const termino = normalizarTexto(terminoRaw);

  const secUsuarios = document.getElementById('seccion-usuarios');
  const secProveedores = document.getElementById('seccion-proveedores');
  const secVentas = document.getElementById('seccion-ventas');
  const secInventario = document.getElementById('seccion-inventario');

  const esUsuarios = secUsuarios && secUsuarios.classList.contains('active');
  const esProveedores = secProveedores && secProveedores.classList.contains('active');
  const esVentas = secVentas && secVentas.classList.contains('active');
  const esInventario = secInventario && secInventario.classList.contains('active');

  // Sincronizar siempre el filtro de inventario y de resumen en segundo plano
  aplicarFiltrosCombinados(termino);
  filtrarSeccionResumenEnVivo(termino);

  if (esUsuarios) {
    const inputUsu = document.getElementById('inputBuscarUsuario');
    if (inputUsu) inputUsu.value = terminoRaw;
    filtrarTablaUsuarios(termino);
  } else if (esVentas) {
    const inputVta = document.getElementById('inputBuscarVenta');
    if (inputVta) inputVta.value = terminoRaw;
    filtrarTablaVentas(termino);
  } else if (esProveedores) {
    filtrarTablaProveedores(termino);
  } else if (!esInventario) {
    // Estamos en #resumen: además de filtrar las tablas y gráficas de #resumen,
    // mostramos el dropdown rápido para saltar o editar directamente si desea.
  }

  renderizarDropdownBusquedaGlobal(terminoRaw, termino);
}

function renderizarDropdownBusquedaGlobal(terminoRaw, terminoNorm) {
  const dropdown = document.getElementById('globalSearchDropdown');
  if (!dropdown) return;

  if (!terminoNorm || terminoNorm.length < 1) {
    dropdown.classList.remove('open');
    dropdown.innerHTML = '';
    return;
  }

  const prodsCoincidentes = (estadoDashboard.productosResumen || []).filter(p => {
    const base = normalizarTexto(`${p.nombre} ${p.categoria} ${p.estado}`);
    return base.includes(terminoNorm);
  }).slice(0, 6);

  const ventasCoincidentes = (estadoDashboard.ventasJson || []).filter(v => {
    const base = normalizarTexto(`venta #vta-${v.id_venta} ${v.id_venta} ${v.cajero} ${v.origen_venta} ${v.medio_pago} ${v.estado_venta}`);
    return base.includes(terminoNorm);
  }).slice(0, 4);

  if (prodsCoincidentes.length === 0 && ventasCoincidentes.length === 0) {
    dropdown.innerHTML = `
      <div class="global-search-empty">
        No se encontraron coincidencias para "<strong>${terminoRaw}</strong>" en productos ni ventas.
      </div>
    `;
    dropdown.classList.add('open');
    return;
  }

  let html = '';

  if (prodsCoincidentes.length > 0) {
    html += `<div class="global-search-header"><span>Frutas en Catálogo (${prodsCoincidentes.length})</span><span>Ganancia / Precio</span></div>`;
    prodsCoincidentes.forEach(p => {
      html += `
        <div class="global-search-item" onclick="irAProductoDesdeBusqueda(${p.id})">
          <div class="global-search-item-info">
            <strong>${p.nombre} <span class="badge-cat" style="font-size:0.68rem; padding:1px 6px;">${p.categoria}</span></strong>
            <small>Stock: ${Math.round(p.stock_actual)} ${p.unidad_medida} • Costo: ${formatearCOP(p.costo_compra)} • Ganancia stock: +${formatearCOP(p.ganancia_stock)}</small>
          </div>
          <div class="global-search-item-meta">
            <span class="price">${formatearCOP(p.precio_efectivo)}/${p.unidad_medida}</span>
            <span class="profit">+${formatearCOP(p.margen_unitario)} (${p.porcentaje_margen.toFixed(1)}%)</span>
          </div>
        </div>
      `;
    });
  }

  if (ventasCoincidentes.length > 0) {
    html += `<div class="global-search-header"><span>Ventas Registradas (${ventasCoincidentes.length})</span><span>Total / Ganancia</span></div>`;
    ventasCoincidentes.forEach(v => {
      html += `
        <div class="global-search-item" onclick="irAVentaDesdeBusqueda(${v.id_venta})">
          <div class="global-search-item-info">
            <strong>#VTA-${v.id_venta} • ${v.origen_venta}</strong>
            <small>${v.fecha_str} ${v.hora_str} • Cajero: ${v.cajero} (${v.medio_pago})</small>
          </div>
          <div class="global-search-item-meta">
            <span class="price">${formatearCOP(v.total_neto)}</span>
            <span class="profit">+${formatearCOP(v.ganancia_estimada)} ganancia</span>
          </div>
        </div>
      `;
    });
  }

  dropdown.innerHTML = html;
  dropdown.classList.add('open');
}

function irAProductoDesdeBusqueda(idProducto) {
  const dropdown = document.getElementById('globalSearchDropdown');
  if (dropdown) dropdown.classList.remove('open');

  const secResumen = document.getElementById('seccion-resumen');
  if (secResumen && secResumen.classList.contains('active')) {
    const filaResumen = document.querySelector(`#tablaRentabilidadProductosBody tr[data-id="${idProducto}"]`);
    if (filaResumen) {
      filaResumen.scrollIntoView({ behavior: 'smooth', block: 'center' });
      filaResumen.style.backgroundColor = '#dcfce7';
      setTimeout(() => { filaResumen.style.backgroundColor = ''; }, 1800);
      return;
    }
  }

  mostrarSeccion('inventario');
  setTimeout(() => {
    const btnEdit = document.querySelector(`#tablaProductosBody button.btn-action-edit[data-id="${idProducto}"]`);
    if (btnEdit) {
      const fila = btnEdit.closest('tr');
      if (fila) {
        fila.scrollIntoView({ behavior: 'smooth', block: 'center' });
        fila.style.backgroundColor = '#dcfce7';
        setTimeout(() => { fila.style.backgroundColor = ''; }, 1800);
      }
    }
  }, 150);
}

function irAVentaDesdeBusqueda(idVenta) {
  const dropdown = document.getElementById('globalSearchDropdown');
  if (dropdown) dropdown.classList.remove('open');
  mostrarSeccion('ventas');
  setTimeout(() => {
    const fila = document.querySelector(`#tablaVentasBody tr[data-id="${idVenta}"]`);
    if (fila) {
      fila.scrollIntoView({ behavior: 'smooth', block: 'center' });
      fila.style.backgroundColor = '#dcfce7';
      setTimeout(() => { fila.style.backgroundColor = ''; }, 1800);
    }
  }, 150);
}

// Cerrar el dropdown de búsqueda al hacer clic fuera
document.addEventListener('click', function(e) {
  const dropdown = document.getElementById('globalSearchDropdown');
  const searchWrap = e.target.closest('.header-actions');
  if (dropdown && !searchWrap) {
    dropdown.classList.remove('open');
  }
});

// Filtrar en vivo las tablas y gráficas de la sección #resumen
function filtrarSeccionResumenEnVivo(terminoNorm) {
  const term = terminoNorm !== undefined
    ? terminoNorm
    : normalizarTexto(document.getElementById('inputBuscarProducto')?.value || '');

  // 1. Filtrar Tabla de Rentabilidad Real por Producto
  const filasProd = document.querySelectorAll('#tablaRentabilidadProductosBody tr.fila-resumen-producto');
  let invSum = 0;
  let vtaSum = 0;
  let ganSum = 0;
  let visiblesCount = 0;

  filasProd.forEach(fila => {
    const texto = normalizarTexto(fila.getAttribute('data-busqueda') || fila.textContent);
    const visible = !term || texto.includes(term);
    fila.style.display = visible ? '' : 'none';
    if (visible) {
      visiblesCount++;
      const idProd = parseInt(fila.getAttribute('data-id'), 10);
      const pObj = (estadoDashboard.productosResumen || []).find(item => item.id === idProd);
      if (pObj) {
        invSum += Number(pObj.inversion_stock) || 0;
        vtaSum += Number(pObj.venta_stock) || 0;
        ganSum += Number(pObj.ganancia_stock) || 0;
      }
    }
  });

  const lblConteo = document.getElementById('lblConteoProductosResumen');
  if (lblConteo) lblConteo.textContent = `${visiblesCount} referencias visibles`;
  const tfootLabel = document.getElementById('tfootProdLabel');
  if (tfootLabel) tfootLabel.textContent = `TOTALES DE PRODUCTOS FILTRADOS (${visiblesCount} productos):`;
  const tfootInv = document.getElementById('tfootProdInversion');
  if (tfootInv) tfootInv.textContent = `${formatearCOP(invSum)} COP`;
  const tfootVta = document.getElementById('tfootProdVenta');
  if (tfootVta) tfootVta.textContent = `${formatearCOP(vtaSum)} COP`;
  const tfootGan = document.getElementById('tfootProdGanancia');
  if (tfootGan) tfootGan.textContent = `+${formatearCOP(ganSum)} COP`;

  // 2. Actualizar la Gráfica de Rentabilidad por Producto según la búsqueda
  actualizarGraficaMargenesProductos(term);

  // 3. Filtrar Tabla de Ganancias por Ventas combinando período + término buscado
  aplicarFiltroTablaGananciasVentas(periodoGananciaActual, term);
}

// ============================================================================
// 5.2. FILTRO DE GANANCIAS EN GENERAL (DÍA, MES, AÑO, GENERAL, CATÁLOGO)
// ============================================================================
function filtrarGananciasPeriodo(periodo, btn) {
  periodoGananciaActual = periodo || 'general';

  document.querySelectorAll('.profit-period-btn').forEach(b => b.classList.remove('active'));
  const btnActivo = btn || document.querySelector(`.profit-period-btn[data-periodo="${periodoGananciaActual}"]`);
  if (btnActivo) btnActivo.classList.add('active');

  const periodosData = estadoDashboard.gananciasPeriodos || {};
  const info = periodosData[periodoGananciaActual] || {
    ingresos: 0,
    costo: 0,
    ganancia: 0,
    margen_pct: 0,
    ventas_count: 0,
    label: 'Período Seleccionado'
  };

  const titulos = {
    dia: 'Ganancia Neta de Hoy (Día)',
    mes: 'Ganancia Neta del Mes Actual',
    anio: 'Ganancia Neta del Año Actual',
    general: 'Ganancia Neta General (Todo lo Vendido)',
    catalogo: 'Ganancia Proyectada en Bodega (Catálogo)'
  };

  const badge = document.getElementById('badgePeriodoActivo');
  if (badge) badge.textContent = info.label || titulos[periodoGananciaActual];

  const lblTitle = document.getElementById('lblProfitBoxTitle');
  if (lblTitle) lblTitle.textContent = titulos[periodoGananciaActual] || 'Ganancia Neta';

  const valGanancia = document.getElementById('valFiltroGanancia');
  if (valGanancia) valGanancia.textContent = `+${formatearCOP(info.ganancia)} COP`;

  const subGanancia = document.getElementById('subFiltroGanancia');
  if (subGanancia) {
    subGanancia.innerHTML = `Utilidad limpia descontando costos • Rentabilidad: <strong>${Number(info.margen_pct || 0).toFixed(1)}%</strong>`;
  }

  const valIngresos = document.getElementById('valFiltroIngresos');
  if (valIngresos) valIngresos.textContent = `${formatearCOP(info.ingresos)} COP`;

  const valCostos = document.getElementById('valFiltroCostos');
  if (valCostos) valCostos.textContent = `${formatearCOP(info.costo)} COP`;

  const valCount = document.getElementById('valFiltroCount');
  if (valCount) {
    valCount.textContent = periodoGananciaActual === 'catalogo'
      ? `${info.ventas_count} referencias`
      : `${info.ventas_count} ventas`;
  }

  // Filtrar la tabla de ganancias por ventas según el período elegido
  const term = normalizarTexto(document.getElementById('inputBuscarProducto')?.value || '');
  aplicarFiltroTablaGananciasVentas(periodoGananciaActual, term);

  // Actualizar las gráficas para reflejar el período seleccionado
  if (periodoGananciaActual === 'dia' || periodoGananciaActual === 'mes' || periodoGananciaActual === 'anio') {
    cambiarModoGraficaIzquierda('periodos');
  } else if (periodoGananciaActual === 'catalogo') {
    cambiarModoGraficaIzquierda('categorias');
  } else {
    actualizarGraficaIzquierda();
  }
  actualizarGraficaMargenesProductos(term);
}

function aplicarFiltroTablaGananciasVentas(periodo, terminoNorm) {
  const filas = document.querySelectorAll('#tablaGananciasVentasBody tr.fila-resumen-venta');
  const term = terminoNorm !== undefined ? terminoNorm : '';

  let sumaIngresos = 0;
  let sumaCostos = 0;
  let sumaGanancia = 0;
  let countVentas = 0;

  filas.forEach(fila => {
    const esHoy = fila.getAttribute('data-es-hoy') === '1';
    const esMes = fila.getAttribute('data-es-mes') === '1';
    const esAnio = fila.getAttribute('data-es-anio') === '1';
    const esAnulada = fila.getAttribute('data-anulada') === '1';
    const texto = normalizarTexto(fila.getAttribute('data-busqueda') || fila.textContent);

    let cumplePeriodo = true;
    if (periodo === 'dia') cumplePeriodo = esHoy;
    else if (periodo === 'mes') cumplePeriodo = esMes;
    else if (periodo === 'anio') cumplePeriodo = esAnio;
    // 'general' y 'catalogo' muestran todas las ventas registradas en la tabla de ventas

    const cumpleBusqueda = !term || texto.includes(term);
    const mostrar = cumplePeriodo && cumpleBusqueda;
    fila.style.display = mostrar ? '' : 'none';

    if (mostrar && !esAnulada) {
      countVentas++;
      sumaIngresos += parseFloat(fila.getAttribute('data-ingreso')) || 0;
      sumaCostos += parseFloat(fila.getAttribute('data-costo')) || 0;
      sumaGanancia += parseFloat(fila.getAttribute('data-ganancia')) || 0;
    }
  });

  const nombresPeriodo = {
    dia: 'Hoy (Día Actual)',
    mes: 'Este Mes',
    anio: 'Este Año',
    general: 'General (Todas las Ventas)',
    catalogo: 'General (Todas las Ventas)'
  };

  const lblTabla = document.getElementById('lblTablaVentasPeriodo');
  if (lblTabla) lblTabla.textContent = `Período: ${nombresPeriodo[periodo] || 'General'} (${countVentas} activas)`;

  const tfootLbl = document.getElementById('tfootVentasLabel');
  if (tfootLbl) tfootLbl.textContent = `TOTAL ACUMULADO DEL PERÍODO (${countVentas} ventas válidas):`;

  const tfootIng = document.getElementById('tfootVentasIngresos');
  if (tfootIng) tfootIng.textContent = `${formatearCOP(sumaIngresos)} COP`;

  const tfootCos = document.getElementById('tfootVentasCosto');
  if (tfootCos) tfootCos.textContent = `${formatearCOP(sumaCostos)} COP`;

  const tfootGan = document.getElementById('tfootVentasGanancia');
  if (tfootGan) tfootGan.textContent = `+${formatearCOP(sumaGanancia)} COP`;

  const margenPct = sumaIngresos > 0 ? ((sumaGanancia / sumaIngresos) * 100).toFixed(1) : '0.0';
  const tfootMar = document.getElementById('tfootVentasMargen');
  if (tfootMar) tfootMar.textContent = `${margenPct}%`;
}

function filtrarTablaProveedores(terminoDirecto) {
  const input = document.getElementById('inputBuscarProducto');
  const termino = terminoDirecto !== undefined ? normalizarTexto(terminoDirecto) : normalizarTexto(input ? input.value : '');
  const filas = document.querySelectorAll('#seccion-proveedores tbody tr');

  filas.forEach(fila => {
    const texto = normalizarTexto(fila.textContent);
    fila.style.display = texto.includes(termino) ? '' : 'none';
  });
}

function filtrarTablaUsuarios(terminoDirecto) {
  const input = document.getElementById('inputBuscarUsuario');
  const termino = terminoDirecto !== undefined ? normalizarTexto(terminoDirecto) : normalizarTexto(input ? input.value : '');
  const filas = document.querySelectorAll('#tablaUsuariosBody tr.fila-usuario');

  filas.forEach(fila => {
    const busquedaTexto = normalizarTexto(fila.getAttribute('data-busqueda') || fila.textContent);
    fila.style.display = busquedaTexto.includes(termino) ? '' : 'none';
  });
}

function filtrarTablaVentas(terminoDirecto) {
  const input = document.getElementById('inputBuscarVenta');
  const termino = terminoDirecto !== undefined ? normalizarTexto(terminoDirecto) : normalizarTexto(input ? input.value : '');
  const filas = document.querySelectorAll('#tablaVentasBody tr.fila-venta');

  filas.forEach(fila => {
    const busquedaTexto = normalizarTexto(fila.getAttribute('data-busqueda') || fila.textContent);
    fila.style.display = busquedaTexto.includes(termino) ? '' : 'none';
  });
}

function filtrarPorRol(filtro, btn) {
  document.querySelectorAll('.btn-role-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const filas = document.querySelectorAll('#tablaUsuariosBody tr.fila-usuario');
  const filtroNorm = normalizarTexto(filtro);
  filas.forEach(fila => {
    const busquedaTexto = normalizarTexto(fila.getAttribute('data-busqueda') || '');
    if (filtroNorm === 'todos') {
      fila.style.display = '';
    } else {
      fila.style.display = busquedaTexto.includes(filtroNorm) ? '' : 'none';
    }
  });
}

function sincronizarSeccionUrl() {
  const hash = (window.location.hash || '').replace('#', '').trim();
  const seccionesValidas = ['resumen', 'inventario', 'ventas', 'proveedores', 'usuarios'];
  if (seccionesValidas.includes(hash)) {
    mostrarSeccion(hash);
  } else {
    mostrarSeccion('resumen');
  }
}

window.addEventListener('DOMContentLoaded', sincronizarSeccionUrl);
window.addEventListener('hashchange', sincronizarSeccionUrl);

function filtrarTablaProductos() {
  aplicarFiltrosCombinados();
}

function aplicarFiltrosCombinados(terminoDirecto) {
  const termino = terminoDirecto !== undefined
    ? terminoDirecto
    : normalizarTexto(document.getElementById('inputBuscarProducto')?.value || '');
  const filas = document.querySelectorAll('#tablaProductosBody tr.fila-producto');

  filas.forEach(fila => {
    const busquedaTexto = normalizarTexto(fila.getAttribute('data-busqueda') || fila.textContent);
    const coincideTexto = !termino || busquedaTexto.includes(termino);

    let coincideEstado = true;
    if (filtroEstadoActual === 'oferta') {
      coincideEstado = fila.getAttribute('data-oferta') === '1';
    } else if (filtroEstadoActual === 'bajo_stock') {
      coincideEstado = fila.getAttribute('data-bajo-stock') === '1';
    } else if (filtroEstadoActual === 'agotado') {
      coincideEstado = fila.getAttribute('data-agotado') === '1';
    }

    fila.style.display = (coincideTexto && coincideEstado) ? '' : 'none';
  });
}

// ============================================================================
// 6. CIERRE GLOBAL DE MODALES (TECLA ESCAPE Y CLIC EN OVERLAY)
// ============================================================================
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    cerrarModalNuevoProducto();
    cerrarModalEditar();
    cerrarModalEliminar();
    cerrarModalNuevaCategoria();
    cerrarModalNuevoProveedor();
    cerrarModalEditarProveedor();
    cerrarModalEliminarProveedor();
    cerrarModalNuevoUsuario();
    cerrarModalEditarUsuario();
    cerrarModalEliminarUsuario();
    cerrarModalNuevaVenta();
    cerrarModalEditarVenta();
    cerrarModalEliminarVenta();
    const dropdown = document.getElementById('globalSearchDropdown');
    if (dropdown) dropdown.classList.remove('open');
  }
});

// ============================================================================
// 7. GRÁFICOS INTERACTIVOS (CHART.JS) Y SINCRONIZACIÓN EN TIEMPO REAL
// ============================================================================
function cambiarModoGraficaIzquierda(modo) {
  modoGraficaIzquierda = modo;
  const btnCat = document.getElementById('btnChartModoCat');
  const btnPer = document.getElementById('btnChartModoPer');
  if (btnCat) btnCat.classList.toggle('active', modo === 'categorias');
  if (btnPer) btnPer.classList.toggle('active', modo === 'periodos');
  actualizarGraficaIzquierda();
}

function actualizarGraficaIzquierda() {
  const ctxCat = document.getElementById('chartCategorias');
  if (!ctxCat || typeof Chart === 'undefined') return;

  if (chartCategoriasInstance) {
    chartCategoriasInstance.destroy();
    chartCategoriasInstance = null;
  }

  const tituloEl = document.getElementById('chartIzqTitulo');
  const subEl = document.getElementById('chartIzqSub');

  if (modoGraficaIzquierda === 'periodos') {
    if (tituloEl) tituloEl.textContent = 'Ganancias Reales por Período (Día, Mes, Año y General)';
    if (subEl) subEl.textContent = 'Comparativa de Ingresos Vendidos vs Costos vs Ganancia Neta ($ COP)';

    const gp = estadoDashboard.gananciasPeriodos || {};
    const labels = ['Hoy (Día)', 'Este Mes', 'Este Año', 'General (Total)'];
    const keys = ['dia', 'mes', 'anio', 'general'];
    const dataIngresos = keys.map(k => Math.round(gp[k]?.ingresos || 0));
    const dataCostos = keys.map(k => Math.round(gp[k]?.costo || 0));
    const dataGanancias = keys.map(k => Math.round(gp[k]?.ganancia || 0));

    chartCategoriasInstance = new Chart(ctxCat, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Total Vendido',
            data: dataIngresos,
            backgroundColor: '#3b82f6',
            borderRadius: 6
          },
          {
            label: 'Costo Mercancía',
            data: dataCostos,
            backgroundColor: '#94a3b8',
            borderRadius: 6
          },
          {
            label: 'Ganancia Neta',
            data: dataGanancias,
            backgroundColor: '#10b981',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" } }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return ` ${context.dataset.label}: $${Number(context.raw).toLocaleString('es-CO')} COP`;
              }
            }
          }
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            grid: { color: '#f1f5f9' },
            ticks: {
              callback: function(value) {
                return '$' + Number(value).toLocaleString('es-CO');
              }
            }
          }
        }
      }
    });
  } else {
    if (tituloEl) tituloEl.textContent = 'Distribución por Categorías';
    if (subEl) subEl.textContent = 'Volumen de productos clasificados por grupo taxonómico';

    const coloresCategorias = [
      '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
    ];

    chartCategoriasInstance = new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: estadoDashboard.catLabels,
        datasets: [{
          data: estadoDashboard.catData,
          backgroundColor: coloresCategorias.slice(0, estadoDashboard.catLabels.length),
          borderColor: '#ffffff',
          borderWidth: 2,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" },
              padding: 8
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return ` ${context.label}: ${context.raw} productos`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }
}

function actualizarGraficaMargenesProductos(terminoNorm) {
  const ctxMargenes = document.getElementById('chartMargenes');
  if (!ctxMargenes || typeof Chart === 'undefined') return;

  const term = terminoNorm !== undefined
    ? terminoNorm
    : normalizarTexto(document.getElementById('inputBuscarProducto')?.value || '');

  const listaFiltrada = (estadoDashboard.productosResumen || []).filter(p => {
    if (!term) return true;
    return normalizarTexto(`${p.nombre} ${p.categoria}`).includes(term);
  });

  const labels = listaFiltrada.map(p => p.nombre);
  const costos = listaFiltrada.map(p => p.costo_compra);
  const precios = listaFiltrada.map(p => p.precio_efectivo);
  const margenes = listaFiltrada.map(p => p.margen_unitario);

  const badgeEl = document.getElementById('chartDerBadge');
  if (badgeEl) {
    badgeEl.textContent = `${listaFiltrada.length} productos reales`;
  }

  if (chartMargenesInstance) {
    chartMargenesInstance.data.labels = labels;
    chartMargenesInstance.data.datasets[0].data = costos;
    chartMargenesInstance.data.datasets[1].data = precios;
    chartMargenesInstance.data.datasets[2].data = margenes;
    chartMargenesInstance.update();
    return;
  }

  chartMargenesInstance = new Chart(ctxMargenes, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Costo Compra',
          data: costos,
          backgroundColor: '#94a3b8',
          borderRadius: 5
        },
        {
          label: 'Precio Venta Vigente',
          data: precios,
          backgroundColor: '#10b981',
          borderRadius: 5
        },
        {
          label: 'Ganancia Unitaria',
          data: margenes,
          backgroundColor: '#0284c7',
          borderRadius: 5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            boxWidth: 12,
            font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" },
            padding: 10
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: $${Number(context.raw).toLocaleString('es-CO')} COP`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            font: { size: 10, family: "'Plus Jakarta Sans', sans-serif" },
            maxRotation: 45,
            minRotation: 0
          }
        },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: {
            font: { size: 10, family: "'Plus Jakarta Sans', sans-serif" },
            callback: function(value) {
              return '$' + Number(value).toLocaleString('es-CO');
            }
          }
        }
      }
    }
  });
}

// Re-renderizar dinámicamente las filas de ventas cuando llega una actualización en tiempo real
function renderizarTablasVentasTiempoReal(ventas) {
  const tbodyVentas = document.getElementById('tablaVentasBody');
  const tbodyResumenVentas = document.getElementById('tablaGananciasVentasBody');

  if (tbodyVentas) {
    if (!ventas || ventas.length === 0) {
      tbodyVentas.innerHTML = `
        <tr>
          <td class="empty-products" colspan="10">
            No hay ventas registradas aún. ¡Haz clic en "+ Nueva Venta" para registrar la primera!
          </td>
        </tr>
      `;
    } else {
      tbodyVentas.innerHTML = ventas.map(v => {
        const badgeEstado = (v.estado_venta === 'Completada' || !v.estado_venta)
          ? '<span class="badge-status badge-status-activo">Completada</span>'
          : (v.estado_venta === 'Pendiente'
            ? '<span class="badge-status" style="background: #fef3c7; color: #92400e; border: 1px solid #fde68a;">Pendiente</span>'
            : `<span class="badge-status badge-status-inactivo">${v.estado_venta}</span>`);

        const badgeGanancia = v.estado_venta === 'Anulada'
          ? '<span class="badge-normal">$0 COP</span>'
          : `<span class="badge-margen">+${formatearCOP(v.ganancia_estimada)} COP</span>`;

        const clienteHtml = v.id_cliente
          ? `<div style="font-size: 0.75rem; color: #64748b;">Cliente ID: #${v.id_cliente}</div>`
          : '';

        const busquedaAttr = `venta #vta-${v.id_venta} ${v.cajero} ${v.medio_pago} ${v.origen_venta} ${v.estado_venta}`.toLowerCase();

        return `
          <tr class="fila-venta" data-id="${v.id_venta}" data-busqueda="${busquedaAttr}">
            <td><strong style="color: #059669;">#VTA-${v.id_venta}</strong></td>
            <td><strong>${v.cajero}</strong>${clienteHtml}</td>
            <td>
              <div>${v.fecha_str}</div>
              <small style="color: #64748b; font-size: 0.75rem;">${v.hora_str}</small>
            </td>
            <td>
              <span style="font-size: 0.8rem; background: #f1f5f9; padding: 3px 8px; border-radius: 6px; border: 1px solid #e2e8f0;">
                ${v.origen_venta}
              </span>
            </td>
            <td><span style="font-size: 0.8rem; font-weight: 600;">${v.medio_pago}</span></td>
            <td style="text-align: right; font-weight: 500;">$${Number(v.subtotal).toFixed(2)}</td>
            <td style="text-align: right; font-weight: 700; color: #059669; font-size: 0.95rem;">$${Number(v.total_neto).toFixed(2)} COP</td>
            <td style="text-align: right;">${badgeGanancia}</td>
            <td style="text-align: center;">${badgeEstado}</td>
            <td style="text-align: center; white-space: nowrap;">
              <a href="/dashboard/venta/${v.id_venta}/recibo/" target="_blank" rel="noopener"
                style="margin-right: 6px; display: inline-block; text-decoration: none; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 5px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;"
                title="Abrir comprobante imprimible de la venta">
                🖨️ Recibo
              </a>
              <button type="button" class="btn-action-edit"
                data-id="${v.id_venta}"
                data-cliente="${v.id_cliente || ''}"
                data-origen="${v.origen_venta}"
                data-medio="${v.medio_pago}"
                data-subtotal="${v.subtotal}"
                data-descuento="${v.descuento}"
                data-total="${v.total_neto}"
                data-estado="${v.estado_venta}"
                onclick="abrirModalEditarVenta(this)"
                style="margin-right: 6px; cursor: pointer; border: none; background: #f1f5f9; color: #1e293b; padding: 5px 12px; border-radius: 6px; font-weight: 600; font-size: 0.82rem;"
                title="Modificar venta">
                Editar
              </button>
              <button type="button" class="btn-action-delete"
                data-id="${v.id_venta}"
                data-total="${v.total_neto}"
                data-cajero="${v.cajero}"
                onclick="abrirModalEliminarVenta(this)"
                style="color: #dc2626; background: #fef2f2; border: 1px solid #fee2e2; cursor: pointer; padding: 5px 12px; border-radius: 6px; font-weight: 600; font-size: 0.82rem;"
                title="Eliminar venta del sistema">
                Eliminar
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }
  }

  if (tbodyResumenVentas) {
    if (!ventas || ventas.length === 0) {
      tbodyResumenVentas.innerHTML = `
        <tr id="filaSinVentasResumen">
          <td colspan="8" class="empty-products">No hay ventas registradas para este período.</td>
        </tr>
      `;
    } else {
      tbodyResumenVentas.innerHTML = ventas.map(v => {
        const badgeEstado = (v.estado_venta === 'Completada' || !v.estado_venta)
          ? '<span class="badge-status badge-status-activo">Completada</span>'
          : (v.estado_venta === 'Pendiente'
            ? '<span class="badge-status" style="background: #fef3c7; color: #92400e; border: 1px solid #fde68a;">Pendiente</span>'
            : `<span class="badge-status badge-status-inactivo">${v.estado_venta}</span>`);

        const badgeGanancia = v.estado_venta === 'Anulada'
          ? '<span class="badge-normal">$0 COP (Anulada)</span>'
          : `<span class="badge-margen">+${formatearCOP(v.ganancia_estimada)} COP</span>`;

        const clienteHtml = v.id_cliente
          ? `<div style="font-size: 0.73rem; color: #64748b;">Cliente #${v.id_cliente}</div>`
          : '';

        const busquedaAttr = `venta #vta-${v.id_venta} ${v.cajero} ${v.origen_venta} ${v.medio_pago} ${v.estado_venta}`.toLowerCase();

        return `
          <tr class="fila-resumen-venta"
              data-id="${v.id_venta}"
              data-es-hoy="${v.es_hoy ? '1' : '0'}"
              data-es-mes="${v.es_mes ? '1' : '0'}"
              data-es-anio="${v.es_anio ? '1' : '0'}"
              data-anulada="${v.estado_venta === 'Anulada' ? '1' : '0'}"
              data-ingreso="${v.total_neto}"
              data-costo="${v.costo_estimado}"
              data-ganancia="${v.ganancia_estimada}"
              data-busqueda="${busquedaAttr}">
            <td><strong style="color: #059669;">#VTA-${v.id_venta}</strong></td>
            <td>
              <div>${v.fecha_str}</div>
              <small style="color: #64748b; font-size: 0.74rem;">${v.hora_str}</small>
            </td>
            <td><strong>${v.cajero}</strong>${clienteHtml}</td>
            <td>
              <span class="badge-cat">${v.origen_venta}</span>
              <small style="display: block; color: #64748b; font-size: 0.73rem; margin-top: 2px;">${v.medio_pago}</small>
            </td>
            <td style="text-align: right; font-weight: 600; color: #1e293b;">${formatearCOP(v.total_neto)} COP</td>
            <td style="text-align: right; color: #64748b;">${formatearCOP(v.costo_estimado)} COP</td>
            <td style="text-align: right;">${badgeGanancia}</td>
            <td style="text-align: center;">${badgeEstado}</td>
          </tr>
        `;
      }).join('');
    }
  }
}

// Polling en tiempo real cada 3 segundos para mantener sincronizado el Dashboard
async function sincronizarEstadoTiempoReal() {
  try {
    const resp = await fetch('/api/estado-tiempo-real/', {
      headers: { 'Accept': 'application/json' },
      cache: 'no-store'
    });
    if (!resp.ok) return;
    const data = await resp.json();
    if (!data || !data.ok) return;

    const firmaNueva = JSON.stringify({
      v: data.ventas,
      gp: data.ganancias_periodos,
      rk: data.resumen_kpis,
      pr: (data.productos_resumen || []).map(p => [p.id, p.precio_efectivo, p.stock_actual, p.estado])
    });

    if (estadoDashboard.ultimaFirma && estadoDashboard.ultimaFirma === firmaNueva) {
      return;
    }
    estadoDashboard.ultimaFirma = firmaNueva;

    // Actualizar memoria
    if (data.ganancias_periodos) estadoDashboard.gananciasPeriodos = data.ganancias_periodos;
    if (data.productos_resumen) estadoDashboard.productosResumen = data.productos_resumen;
    if (data.ventas) estadoDashboard.ventasJson = data.ventas;

    // Actualizar KPIs de #seccion-ventas
    if (data.ventas_kpis) {
      const vk = data.ventas_kpis;
      const elRec = document.getElementById('kpiVentasRecaudado');
      if (elRec) elRec.textContent = formatearCOP(vk.total_ventas_ingresos);
      const elCnt = document.getElementById('kpiVentasCount');
      if (elCnt) elCnt.textContent = vk.total_ventas_count;
      const elHoyCnt = document.getElementById('kpiVentasHoyCount');
      if (elHoyCnt) elHoyCnt.textContent = vk.ventas_hoy_count;
      const elHoyIng = document.getElementById('kpiVentasHoyIngresos');
      if (elHoyIng) elHoyIng.textContent = formatearCOP(vk.ventas_hoy_ingresos);
      const elTkt = document.getElementById('kpiVentasTicket');
      if (elTkt) elTkt.textContent = formatearCOP(vk.ticket_promedio);
      const elBadgeCnt = document.getElementById('badgeTotalVentasCount');
      if (elBadgeCnt) elBadgeCnt.textContent = `Total: ${vk.total_ventas_count} ventas`;
    }

    // Actualizar KPIs de #seccion-resumen
    if (data.resumen_kpis) {
      const rk = data.resumen_kpis;
      const elTotProd = document.getElementById('kpiTotalProductos');
      if (elTotProd) elTotProd.textContent = rk.total_productos;
      const elTotOf = document.getElementById('kpiTotalOfertas');
      if (elTotOf) elTotOf.textContent = rk.total_ofertas;
      const elInv = document.getElementById('kpiInversionTotal');
      if (elInv) elInv.textContent = formatearCOP(rk.inversion_total);
      const elGan = document.getElementById('kpiGananciaPotencial');
      if (elGan) elGan.textContent = '+' + formatearCOP(rk.ganancia_potencial);
      const elMar = document.getElementById('kpiMargenPromedio');
      if (elMar) elMar.textContent = `${Number(rk.margen_promedio).toFixed(1)}%`;

      const finInv = document.getElementById('finanzasInversionVal');
      if (finInv) finInv.textContent = `${formatearCOP(rk.inversion_total)} COP`;
      const finVta = document.getElementById('finanzasVentaVal');
      if (finVta) finVta.textContent = `${formatearCOP(rk.valor_venta_potencial)} COP`;
      const finGan = document.getElementById('finanzasGananciaVal');
      if (finGan) finGan.textContent = `+${formatearCOP(rk.ganancia_potencial)} COP`;
      const finPill = document.getElementById('finanzasMargenPill');
      if (finPill) finPill.textContent = `Margen Real: ${Number(rk.margen_promedio).toFixed(1)}%`;
    }

    if (data.ganancias_periodos) {
      const finRealVentas = document.getElementById('finanzasGananciaRealVentas');
      if (finRealVentas) {
        finRealVentas.textContent = `+${formatearCOP(data.ganancias_periodos.dia?.ganancia || 0)} hoy / +${formatearCOP(data.ganancias_periodos.general?.ganancia || 0)} total`;
      }
    }

    // Re-renderizar tablas de ventas y re-aplicar filtros activos sin perder búsqueda
    if (data.ventas) {
      renderizarTablasVentasTiempoReal(data.ventas);
      const termVta = normalizarTexto(document.getElementById('inputBuscarVenta')?.value || '');
      if (termVta) filtrarTablaVentas(termVta);
    }

    filtrarGananciasPeriodo(periodoGananciaActual);
  } catch (err) {
    // Silencioso ante desconexiones momentáneas
  }
}

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.dash-modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function(e) {
      if (e.target === this) {
        this.classList.remove('open');
      }
    });
  });

  // Inicializar datos desde JSON Script
  const parseJsonSafe = (id, fallback) => {
    const el = document.getElementById(id);
    if (!el) return fallback;
    try { return JSON.parse(el.textContent); } catch (e) { return fallback; }
  };

  estadoDashboard.catLabels = parseJsonSafe('data-cat-labels', []);
  estadoDashboard.catData = parseJsonSafe('data-cat-data', []);
  estadoDashboard.productosResumen = parseJsonSafe('data-productos-resumen', []);
  estadoDashboard.gananciasPeriodos = parseJsonSafe('data-ganancias-periodos', {});
  estadoDashboard.ventasJson = parseJsonSafe('data-ventas-json', []);

  try {
    actualizarGraficaIzquierda();
    actualizarGraficaMargenesProductos('');
    filtrarGananciasPeriodo('general');
  } catch (err) {
    console.error('Error al inicializar analítica del Dashboard:', err);
  }

  // Iniciar sincronización en tiempo real cada 3 segundos
  setInterval(sincronizarEstadoTiempoReal, 3000);
});
