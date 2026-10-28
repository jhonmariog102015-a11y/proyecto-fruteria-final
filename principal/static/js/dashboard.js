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

function ejecutarBusquedaActiva() {
  const termino = (document.getElementById('inputBuscarProducto').value || '').toLowerCase().trim();
  const secUsuarios = document.getElementById('seccion-usuarios');
  const secProveedores = document.getElementById('seccion-proveedores');
  const secVentas = document.getElementById('seccion-ventas');
  const esUsuarios = secUsuarios && secUsuarios.classList.contains('active');
  const esProveedores = secProveedores && secProveedores.classList.contains('active');
  const esVentas = secVentas && secVentas.classList.contains('active');

  if (esUsuarios) {
    const inputUsu = document.getElementById('inputBuscarUsuario');
    if (inputUsu) inputUsu.value = termino;
    filtrarTablaUsuarios(termino);
  } else if (esVentas) {
    const inputVta = document.getElementById('inputBuscarVenta');
    if (inputVta) inputVta.value = termino;
    filtrarTablaVentas(termino);
  } else if (esProveedores) {
    filtrarTablaProveedores(termino);
  } else {
    filtrarTablaProductos();
  }
}

function filtrarTablaProveedores(terminoDirecto) {
  const input = document.getElementById('inputBuscarProducto');
  const termino = terminoDirecto !== undefined ? terminoDirecto : (input ? input.value.toLowerCase().trim() : '');
  const filas = document.querySelectorAll('#seccion-proveedores tbody tr');

  filas.forEach(fila => {
    const texto = fila.textContent.toLowerCase();
    fila.style.display = texto.includes(termino) ? '' : 'none';
  });
}

function filtrarTablaUsuarios(terminoDirecto) {
  const input = document.getElementById('inputBuscarUsuario');
  const termino = terminoDirecto !== undefined ? terminoDirecto : (input ? input.value.toLowerCase().trim() : '');
  const filas = document.querySelectorAll('#tablaUsuariosBody tr.fila-usuario');

  filas.forEach(fila => {
    const busquedaTexto = fila.getAttribute('data-busqueda') || '';
    fila.style.display = busquedaTexto.includes(termino) ? '' : 'none';
  });
}

function filtrarTablaVentas(terminoDirecto) {
  const input = document.getElementById('inputBuscarVenta');
  const termino = terminoDirecto !== undefined ? terminoDirecto : (input ? input.value.toLowerCase().trim() : '');
  const filas = document.querySelectorAll('#tablaVentasBody tr.fila-venta');

  filas.forEach(fila => {
    const busquedaTexto = fila.getAttribute('data-busqueda') || '';
    fila.style.display = busquedaTexto.includes(termino) ? '' : 'none';
  });
}

function filtrarPorRol(filtro, btn) {
  document.querySelectorAll('.btn-role-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const filas = document.querySelectorAll('#tablaUsuariosBody tr.fila-usuario');
  filas.forEach(fila => {
    const busquedaTexto = (fila.getAttribute('data-busqueda') || '').toLowerCase();
    if (filtro === 'todos') {
      fila.style.display = '';
    } else {
      fila.style.display = busquedaTexto.includes(filtro.toLowerCase()) ? '' : 'none';
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

function aplicarFiltrosCombinados() {
  const termino = (document.getElementById('inputBuscarProducto').value || '').toLowerCase().trim();
  const filas = document.querySelectorAll('#tablaProductosBody tr.fila-producto');

  filas.forEach(fila => {
    const busquedaTexto = fila.getAttribute('data-busqueda') || '';
    const coincideTexto = busquedaTexto.includes(termino);

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
  }
});

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.dash-modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function(e) {
      if (e.target === this) {
        this.classList.remove('open');
      }
    });
  });

  // ==========================================================================
  // 7. INICIALIZACIÓN DE GRÁFICOS EJECUTIVOS CON CHART.JS
  // ==========================================================================
  try {
    const parseJsonSafe = (id, fallback) => {
      const el = document.getElementById(id);
      if (!el) return fallback;
      try { return JSON.parse(el.textContent); } catch (e) { return fallback; }
    };

    const catLabels = parseJsonSafe('data-cat-labels', []);
    const catData = parseJsonSafe('data-cat-data', []);
    const prodLabels = parseJsonSafe('data-prod-labels', []);
    const prodCostos = parseJsonSafe('data-prod-costos', []);
    const prodPrecios = parseJsonSafe('data-prod-precios', []);
    const prodMargenes = parseJsonSafe('data-prod-margenes', []);

    const coloresCategorias = [
      '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
    ];

    const ctxCat = document.getElementById('chartCategorias');
    if (ctxCat && catLabels.length > 0 && typeof Chart !== 'undefined') {
      new Chart(ctxCat, {
        type: 'doughnut',
        data: {
          labels: catLabels,
          datasets: [{
            data: catData,
            backgroundColor: coloresCategorias.slice(0, catLabels.length),
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

    const ctxMargenes = document.getElementById('chartMargenes');
    if (ctxMargenes && prodLabels.length > 0 && typeof Chart !== 'undefined') {
      new Chart(ctxMargenes, {
        type: 'bar',
        data: {
          labels: prodLabels,
          datasets: [
            {
              label: 'Costo Compra',
              data: prodCostos,
              backgroundColor: '#94a3b8',
              borderRadius: 6
            },
            {
              label: 'Precio Venta',
              data: prodPrecios,
              backgroundColor: '#10b981',
              borderRadius: 6
            },
            {
              label: 'Margen Bruto',
              data: prodMargenes,
              backgroundColor: '#0284c7',
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
              ticks: { font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" } }
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
  } catch (err) {
    console.error('Error al inicializar Chart.js:', err);
  }
});
