# ==============================================================================
# CONTROLADOR DE VISTAS (principal/views.py)
# Gestiona la lógica de negocio, consultas al ORM y renderizado de plantillas.
# ==============================================================================
# NOTA TÉCNICA PARA EL EQUIPO (GAES - AUDITORÍA DE CALIDAD Y SEGURIDAD):
# 1. Control de Acceso Basado en Roles (RBAC): Se implementaron la función
#    'es_personal_operativo', el decorador '@personal_requerido' y el mixin
#    'PersonalRequeridoMixin' para proteger '/dashboard/', '/gestion/' y '/ventas/'
#    frente a cuentas públicas registradas como 'cliente'.
# 2. Unificación de Validación de Ventas: Se creó el helper '_extraer_datos_venta'
#    para sanear montos con 'Decimal', evitar descuentos mayores al subtotal y
#    prevenir errores 500 tanto en los modales del dashboard como en las vistas CRUD.
# 3. Prevención de Open Redirect: Se agregó '_obtener_redireccion_segura' usando
#    'url_has_allowed_host_and_scheme' de Django para validar el parámetro 'next'.
# 4. Estandarización de Plantillas: Se renombró 'Registro.html' a 'registro.html'
#    en minúsculas para compatibilidad con sistemas operativos Linux/Unix.
# ==============================================================================

import csv
import json
from decimal import Decimal, InvalidOperation
from functools import wraps
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login as auth_login, views as auth_views
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Case, When, Value, IntegerField
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Producto, Categoria, Proveedor, PerfilUsuario, Venta, Cliente
from .forms import ProductoForm, CategoriaForm, ProveedorForm


def es_administrador(user):
    """
    Control de acceso RBAC: Verifica si el usuario autenticado tiene rol de Super Admin
    o rol administrativo en PerfilUsuario.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return perfil is not None and (perfil.rol == 'admin' or getattr(perfil, 'es_admin', False))


def es_personal_operativo(user):
    """
    Control de acceso RBAC: Verifica que el usuario pertenezca al personal interno
    (Super Admin, Bodeguero, Cajero o is_staff=True), impidiendo que clientes públicos
    accedan al panel administrativo o modifiquen el inventario.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    perfil = getattr(user, 'perfil', None)
    return perfil is not None and perfil.rol in ('admin', 'bodeguero', 'cajero')


def personal_requerido(view_func):
    """
    Decorador de seguridad para vistas operativas y del dashboard:
    1. Si el usuario es anónimo, redirige al login (/accounts/login/).
    2. Si el usuario tiene rol 'cliente' sin privilegios de staff, bloquea el acceso
       y lo redirige a la tienda principal con un mensaje informativo.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not es_personal_operativo(request.user):
            messages.error(
                request,
                "Acceso restringido: esta sección es exclusiva para el personal operativo de Al Paso Frutería."
            )
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class PersonalRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin de control de acceso operativo para Vistas Basadas en Clases (CBV)."""

    def test_func(self):
        return es_personal_operativo(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            "Acceso restringido: esta sección es exclusiva para el personal operativo de Al Paso Frutería."
        )
        return redirect('index')


def _extraer_datos_venta(post_data):
    """
    Extrae, sanea y valida los campos numéricos y de estado de una transacción de venta,
    previniendo errores 500 por valores vacíos o malformados.
    """
    id_cliente_raw = post_data.get('id_cliente', '')
    origen_venta = (post_data.get('origen_venta') or 'Tienda Física').strip()
    subtotal_raw = str(post_data.get('subtotal') or '0').strip()
    descuento_raw = str(post_data.get('descuento') or '0').strip()
    total_neto_raw = str(post_data.get('total_neto') or '').strip()
    medio_pago = (post_data.get('medio_pago') or 'Efectivo').strip()
    estado_venta = (post_data.get('estado_venta') or 'Completada').strip()

    try:
        subtotal = max(Decimal('0.00'), Decimal(subtotal_raw)) if subtotal_raw else Decimal('0.00')
    except Exception:
        subtotal = Decimal('0.00')

    try:
        descuento = max(Decimal('0.00'), Decimal(descuento_raw)) if descuento_raw else Decimal('0.00')
    except Exception:
        descuento = Decimal('0.00')

    if descuento > subtotal:
        descuento = subtotal

    try:
        total_neto = Decimal(total_neto_raw) if total_neto_raw else (subtotal - descuento)
        if total_neto < Decimal('0.00'):
            total_neto = Decimal('0.00')
    except Exception:
        total_neto = subtotal - descuento

    cli_id = int(id_cliente_raw) if id_cliente_raw and str(id_cliente_raw).strip().isdigit() else None

    return {
        'id_cliente': cli_id,
        'origen_venta': origen_venta,
        'subtotal': subtotal,
        'descuento': descuento,
        'total_neto': total_neto,
        'medio_pago': medio_pago,
        'estado_venta': estado_venta,
    }


def _obtener_redireccion_segura(request, default_route='lista_ventas'):
    """Valida el parámetro 'next' contra ataques Open Redirect."""
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return default_route


def inicio(request):
    """
    VISTA PRINCIPAL / LANDING PAGE ('/' y '/inicio/')
    -------------------------------------------------
    1. Consulta la base de datos para obtener todos los productos ordenados por su ID.
    2. Utiliza 'select_related('categoria')' para optimizar la consulta SQL (JOIN)
       y evitar problemas de rendimiento (N+1 queries).
    3. Obtiene todas las categorías disponibles para alimentar las tarjetas y filtros.
    4. Envía los datos al contexto para que 'index.html' dibuje dinámicamente las tarjetas.
    """
    # NOTA PARA EL EQUIPO: Al retirar el carrusel duplicado de 'index.html',
    # la portada solo requiere el conteo total de referencias ('total_productos'),
    # optimizando la velocidad de carga inicial con un único COUNT(*) en SQL.
    context = {
        'titulo': 'Al Paso Frutería — Mercado Campesino',
        'total_productos': Producto.objects.count(),
    }
    return render(request, 'principal/index.html', context)


def catalogo_frutas_view(request):
    """
    CATÁLOGO INTERACTIVO DE FRUTAS ('/catalogo-frutas/')
    ----------------------------------------------------
    Renderiza la vitrina especializada de frutas donde el usuario puede
    interactuar con filtros reactivos en vivo, grados Brix (°Brix), origen y precios.
    """
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    context = {
        'titulo': 'Catálogo de Frutas Frescas — Al Paso Frutería',
        'productos': productos,
        'categorias': categorias,
        'total_productos': productos.count(),
    }
    return render(request, 'principal/catalogo_frutas.html', context)


@personal_requerido
def dashboard_view(request):
    """
    PANEL ADMINISTRATIVO PRIVADO ('/dashboard/')
    --------------------------------------------
    Gestión integral del negocio:
    - Métricas en tiempo real (productos, ofertas, usuarios, categorías).
    - Métricas financieras (inversión total, valor comercial, margen estimado).
    - Inventario con edición y creación directa sin salir del dashboard.
    - Categorización del catálogo en vivo.
    """
    User = get_user_model()

    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.annotate(num_productos=Count('productos')).order_by('nombre')
    total_productos = productos.count()
    total_ofertas = productos.filter(en_oferta=True).count()
    total_usuarios = User.objects.count()

    # Conteo y lista para alertas de inventario
    productos_bajo_stock = [p for p in productos if p.stock_actual <= p.stock_minimo]
    total_bajo_stock = len(productos_bajo_stock)
    total_agotados = sum(1 for p in productos if p.stock_actual <= 0 or p.estado == 'Agotado')

    # Métricas financieras del catálogo
    inversion_total = sum(p.costo_compra * p.stock_actual for p in productos)
    valor_venta_potencial = sum(p.precio_efectivo * p.stock_actual for p in productos)
    ganancia_potencial = valor_venta_potencial - inversion_total
    margen_promedio = round((ganancia_potencial / inversion_total * 100), 1) if inversion_total > 0 else Decimal('0.0')

    # Datos para gráficos analíticos (Chart.js)
    chart_cat_labels = [cat.nombre for cat in categorias if cat.num_productos > 0]
    chart_cat_data = [cat.num_productos for cat in categorias if cat.num_productos > 0]

    # Top productos para comparativa de precios y costo
    top_prods = list(productos[:7])
    chart_prod_labels = [p.nombre for p in top_prods]
    chart_prod_costos = [float(p.costo_compra) for p in top_prods]
    chart_prod_precios = [float(p.precio_efectivo) for p in top_prods]
    chart_prod_margenes = [float(p.margen_ganancia) for p in top_prods]

    # Proveedores y productores aliados (Métricas de Abastecimiento)
    proveedores = Proveedor.objects.all().order_by('razon_social')
    total_proveedores = proveedores.count()
    total_prov_activos = proveedores.filter(estado='Activo').count()
    total_prov_inactivos = total_proveedores - total_prov_activos
    total_prov_con_telefono = proveedores.exclude(telefono__isnull=True).exclude(telefono='').count()

    # Sincronización preventiva de perfiles para cuentas sin perfil vinculado
    for u in User.objects.filter(perfil__isnull=True):
        rol_def = 'admin' if u.is_superuser else ('bodeguero' if u.is_staff else 'cliente')
        PerfilUsuario.objects.get_or_create(
            usuario=u,
            defaults={'rol': rol_def, 'estado': 'activo'}
        )

    # Obtener única y exclusivamente los REGISTROS ACTIVOS del personal operativo ordenados por ROLES:
    # Jerarquía requerida: 1. Super Admin, 2. Bodeguero, 3. Cajero
    perfiles_usuarios = PerfilUsuario.objects.select_related('usuario').filter(
        estado='activo',
        usuario__is_active=True
    ).exclude(
        rol='cliente',
        usuario__is_superuser=False
    ).annotate(
        orden_rol=Case(
            When(usuario__is_superuser=True, then=Value(1)),
            When(rol='admin', then=Value(1)),
            When(rol='bodeguero', then=Value(2)),
            When(rol='cajero', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('orden_rol', 'usuario__username')

    # Métricas específicas del equipo de cuentas activas por rol
    total_activos = perfiles_usuarios.count()
    total_superadmins = perfiles_usuarios.filter(orden_rol=1).count()
    total_bodegueros = perfiles_usuarios.filter(orden_rol=2).count()
    total_cajeros = perfiles_usuarios.filter(orden_rol=3).count()
    total_staff = perfiles_usuarios.filter(usuario__is_staff=True).count()

    # Métricas y listado de Ventas para el panel de gestión
    ventas = Venta.objects.select_related('id_usuario_cajero').all().order_by('-fecha_venta')
    total_ventas_count = ventas.count()
    total_ventas_ingresos = sum(v.total_neto for v in ventas)
    hoy = timezone.now().date()
    ventas_hoy = [v for v in ventas if v.fecha_venta and v.fecha_venta.date() == hoy]
    ventas_hoy_count = len(ventas_hoy)
    ventas_hoy_ingresos = sum(v.total_neto for v in ventas_hoy)
    ticket_promedio = round(total_ventas_ingresos / total_ventas_count, 2) if total_ventas_count > 0 else Decimal('0.00')

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'proveedores': proveedores,
        'perfiles_usuarios': perfiles_usuarios,
        'ventas': ventas,
        'clientes': Cliente.objects.all(),
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_bajo_stock': total_bajo_stock,
        'productos_bajo_stock': productos_bajo_stock,
        'total_agotados': total_agotados,
        'total_usuarios': total_usuarios,
        'total_proveedores': total_proveedores,
        'total_prov_activos': total_prov_activos,
        'total_prov_inactivos': total_prov_inactivos,
        'total_prov_con_telefono': total_prov_con_telefono,
        'total_activos': total_activos,
        'total_superadmins': total_superadmins,
        'total_bodegueros': total_bodegueros,
        'total_cajeros': total_cajeros,
        'total_admins': total_activos,
        'total_admins_activos': total_activos,
        'total_staff': total_staff,
        'total_ventas_count': total_ventas_count,
        'total_ventas_ingresos': total_ventas_ingresos,
        'ventas_hoy_count': ventas_hoy_count,
        'ventas_hoy_ingresos': ventas_hoy_ingresos,
        'ticket_promedio': ticket_promedio,
        'inversion_total': inversion_total,
        'inversion_total_cop': f"{int(inversion_total):,}".replace(",", "."),
        'valor_venta_potencial': valor_venta_potencial,
        'ganancia_potencial': ganancia_potencial,
        'margen_promedio': margen_promedio,
        'es_admin': es_administrador(request.user),
        'chart_cat_labels': chart_cat_labels,
        'chart_cat_data': chart_cat_data,
        'chart_prod_labels': chart_prod_labels,
        'chart_prod_costos': chart_prod_costos,
        'chart_prod_precios': chart_prod_precios,
        'chart_prod_margenes': chart_prod_margenes,
    })


@personal_requerido
def crear_producto_dashboard(request):
    """
    CREACIÓN DIRECTA DE PRODUCTOS DESDE EL DASHBOARD CON VALIDACIÓN FORMULARIA
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            prod = form.save()
            messages.success(request, f"¡Producto '{prod.nombre}' creado exitosamente en el catálogo!")
        else:
            errores = [f"{err}" for lista in form.errors.values() for err in lista]
            messages.error(request, f"Error al crear el producto: {' '.join(errores)}")

    return redirect('dashboard')


@personal_requerido
def editar_producto_dashboard(request, id_producto):
    """
    EDICIÓN RÁPIDA DE PRECIOS, COSTOS, OFERTAS Y STOCK DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=id_producto)
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"¡Producto '{producto.nombre}' actualizado con éxito!")
        else:
            errores = [f"{err}" for lista in form.errors.values() for err in lista]
            messages.error(request, f"Error al actualizar el producto: {' '.join(errores)}")

    return redirect('dashboard')


@personal_requerido
def eliminar_producto_dashboard(request, id_producto):
    """
    ELIMINACIÓN DE PRODUCTO DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=id_producto)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"El producto '{nombre}' fue eliminado del catálogo.")
    return redirect('dashboard')


@personal_requerido
def crear_categoria_dashboard(request):
    """
    CREACIÓN DE CATEGORÍA DESDE EL DASHBOARD CON VALIDACIÓN
    """
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"¡Categoría '{cat.nombre}' creada exitosamente!")
        else:
            errores = [f"{err}" for lista in form.errors.values() for err in lista]
            messages.error(request, f"Error al crear la categoría: {' '.join(errores)}")
    return redirect('dashboard')


@personal_requerido
def eliminar_categoria_dashboard(request, id_categoria):
    """
    ELIMINACIÓN DE CATEGORÍA DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, pk=id_categoria)
        if categoria.productos.exists():
            messages.warning(request, f"No se puede eliminar '{categoria.nombre}' porque contiene productos asociados.")
        else:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f"Categoría '{nombre}' eliminada con éxito.")
    return redirect('dashboard')


# ==============================================================================
# CRUD REGISTROS Y ROLES (VISTAS BASADAS EN FUNCIONES - FBV)
# Listar (en dashboard_view), Crear, Editar (get_object_or_404) y Eliminar (POST)
# ==============================================================================

@login_required
def crear_usuario_dashboard(request):
    """
    CRUD REGISTROS Y ROLES: CREACIÓN DE USUARIO DESDE EL DASHBOARD (FBV)
    Crea la cuenta en auth.User y su PerfilUsuario vinculado con rol jerárquico.
    Acción restringida exclusivamente a usuarios con rol de Administrador.
    """
    if not es_administrador(request.user):
        messages.error(request, 'Acceso denegado: Únicamente los administradores tienen permiso para registrar nuevos usuarios.')
        return redirect('/dashboard/#usuarios')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', 'cajero').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validaciones de integridad
        if not username or not email or not password:
            messages.error(request, 'El nombre de usuario, correo electrónico y contraseña son obligatorios.')
            return redirect('/dashboard/#usuarios')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden.')
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya está registrado.")
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"El correo electrónico '{email}' ya se encuentra en uso.")
            return redirect('/dashboard/#usuarios')

        if rol not in ['admin', 'bodeguero', 'cajero']:
            rol = 'cajero'

        es_super = (rol == 'admin')
        nuevo_usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=es_super
        )

        perfil, _ = PerfilUsuario.objects.update_or_create(
            usuario=nuevo_usuario,
            defaults={
                'telefono': telefono,
                'rol': rol,
                'estado': 'activo'
            }
        )

        rol_nombre = perfil.nombre_rol
        messages.success(request, f"¡Usuario '{username}' registrado exitosamente con rol de {rol_nombre}!")

    return redirect('/dashboard/#usuarios')


@login_required
def editar_usuario_dashboard(request, user_id):
    """
    CRUD REGISTROS Y ROLES: EDICIÓN DE USUARIO Y ROL (FBV CON get_object_or_404)
    Actualiza datos de autenticación (User) y perfil operativo (PerfilUsuario).
    Acción restringida exclusivamente a usuarios con rol de Administrador.
    """
    if not es_administrador(request.user):
        messages.error(request, 'Acceso denegado: Únicamente los administradores tienen permiso para modificar usuarios y roles.')
        return redirect('/dashboard/#usuarios')

    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', '').strip().lower()
        estado = request.POST.get('estado', 'activo').strip().lower()
        nueva_password = request.POST.get('nueva_password', '').strip()

        if not username or not email:
            messages.error(request, 'El nombre de usuario y correo electrónico no pueden estar vacíos.')
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(username=username).exclude(pk=target_user.pk).exists():
            messages.error(request, f"El nombre de usuario '{username}' ya pertenece a otra cuenta.")
            return redirect('/dashboard/#usuarios')

        if User.objects.filter(email=email).exclude(pk=target_user.pk).exists():
            messages.error(request, f"El correo electrónico '{email}' ya está registrado en otra cuenta.")
            return redirect('/dashboard/#usuarios')

        if rol not in ['admin', 'bodeguero', 'cajero']:
            rol = getattr(getattr(target_user, 'perfil', None), 'rol', 'cajero')

        if estado not in ['activo', 'inactivo']:
            estado = 'activo'

        # Prevenir desactivación o pérdida de privilegios del usuario en sesión
        if request.user.pk == target_user.pk:
            if estado == 'inactivo':
                messages.error(request, 'No puedes desactivar tu propia cuenta mientras estás en sesión activa.')
                return redirect('/dashboard/#usuarios')
            if rol != 'admin' and target_user.is_superuser:
                messages.warning(request, 'No puedes degradar tu propio rol de Super Admin en sesión.')
                rol = 'admin'

        target_user.username = username
        target_user.first_name = first_name
        target_user.last_name = last_name
        target_user.email = email

        if rol == 'admin':
            target_user.is_superuser = True
            target_user.is_staff = True
        else:
            target_user.is_superuser = False
            target_user.is_staff = True

        target_user.is_active = (estado != 'inactivo')

        if nueva_password:
            target_user.set_password(nueva_password)

        target_user.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=target_user)
        perfil.rol = rol
        perfil.estado = estado
        perfil.telefono = telefono
        perfil.save()

        messages.success(request, f"¡Usuario '{target_user.username}' y rol '{perfil.nombre_rol}' actualizados exitosamente!")

    return redirect('/dashboard/#usuarios')


@login_required
def eliminar_usuario_dashboard(request, user_id):
    """
    CRUD REGISTROS Y ROLES: ELIMINACIÓN DEFINITIVA CON CONFIRMACIÓN POST (FBV CON get_object_or_404)
    Exige petición POST obligatoria para eliminar un usuario y su perfil asociado.
    Acción restringida exclusivamente a usuarios con rol de Administrador.
    """
    if not es_administrador(request.user):
        messages.error(request, 'Acceso denegado: Únicamente los administradores tienen permiso para eliminar usuarios del sistema.')
        return redirect('/dashboard/#usuarios')

    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)

        # Prevenir que el usuario elimine su propia cuenta
        if request.user.pk == target_user.pk:
            messages.error(request, 'Acción no permitida: no puedes eliminar tu propia cuenta de administrador en sesión.')
            return redirect('/dashboard/#usuarios')

        nombre_eliminado = target_user.username
        target_user.delete()
        messages.success(request, f"El usuario '{nombre_eliminado}' y su rol han sido eliminados correctamente.")
    else:
        messages.warning(request, 'La eliminación de usuarios requiere confirmación mediante petición POST.')

    return redirect('/dashboard/#usuarios')


@personal_requerido
def exportar_inventario_csv(request):
    """
    EXPORTACIÓN DE INVENTARIO COMPATIBLE CON MICROSOFT EXCEL (UTF-8-SIG)
    Genera un archivo CSV delimitado por punto y coma con costos, precios y existencias.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    fecha_str = timezone.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="inventario_el_paso_{fecha_str}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID Producto',
        'Nombre del Producto',
        'Categoría',
        'Costo Compra ($ COP)',
        'Precio Venta Regular ($ COP)',
        'En Oferta',
        'Precio Promocional ($ COP)',
        'Precio Efectivo ($ COP)',
        'Margen Ganancia ($ COP)',
        'Porcentaje Margen (%)',
        'Stock Actual',
        'Stock Mínimo',
        'Unidad de Medida',
        'Estado',
        'Origen / Cosecha',
        'Inversión Total Lote ($ COP)',
        'Valor Comercial Lote ($ COP)'
    ])

    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    for p in productos:
        inversion_prod = float(p.costo_compra * p.stock_actual)
        venta_prod = float(p.precio_efectivo * p.stock_actual)
        writer.writerow([
            p.id_producto,
            p.nombre,
            p.categoria.nombre if p.categoria else 'General',
            f"{p.costo_compra:.2f}",
            f"{p.precio_venta_unitario:.2f}",
            'Sí' if p.en_oferta else 'No',
            f"{p.precio_oferta:.2f}" if p.precio_oferta else '',
            f"{p.precio_efectivo:.2f}",
            f"{p.margen_ganancia:.2f}",
            f"{p.porcentaje_margen:.1f}%",
            f"{p.stock_actual:.3f}",
            f"{p.stock_minimo:.3f}",
            p.unidad_medida,
            p.estado,
            p.origen,
            f"{inversion_prod:.2f}",
            f"{venta_prod:.2f}"
        ])

    return response


@personal_requerido
def crear_proveedor_dashboard(request):
    """
    REGISTRO DE NUEVO PROVEEDOR AGRÍCOLA DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            prov = form.save()
            messages.success(request, f"¡Proveedor '{prov.razon_social}' registrado con éxito!")
        else:
            errores = [f"{err}" for lista in form.errors.values() for err in lista]
            messages.error(request, f"Error al registrar el proveedor: {' '.join(errores)}")
    return redirect('dashboard')


@personal_requerido
def editar_proveedor_dashboard(request, id_proveedor):
    """
    EDICIÓN DE PROVEEDOR AGRÍCOLA EXISTENTE
    """
    if request.method == 'POST':
        proveedor = get_object_or_404(Proveedor, pk=id_proveedor)
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            prov = form.save()
            messages.success(request, f"¡Proveedor '{prov.razon_social}' actualizado con éxito!")
        else:
            errores = [f"{err}" for lista in form.errors.values() for err in lista]
            messages.error(request, f"Error al actualizar el proveedor: {' '.join(errores)}")
    return redirect('dashboard')


@personal_requerido
def eliminar_proveedor_dashboard(request, id_proveedor):
    """
    ELIMINACIÓN DE PROVEEDOR AGRÍCOLA
    """
    if request.method == 'POST':
        proveedor = get_object_or_404(Proveedor, pk=id_proveedor)
        razon = proveedor.razon_social
        proveedor.delete()
        messages.success(request, f"El proveedor '{razon}' fue eliminado exitosamente.")
    return redirect('dashboard')


@personal_requerido
def crear_venta_dashboard(request):
    """
    CRUD VENTAS: REGISTRO DE NUEVA TRANSACCIÓN DESDE EL DASHBOARD (MODAL / VENTANA)
    """
    if request.method == 'POST':
        datos = _extraer_datos_venta(request.POST)
        nueva_venta = Venta.objects.create(
            id_usuario_cajero=request.user,
            **datos
        )
        messages.success(request, f"¡Venta #VTA-{nueva_venta.id_venta} registrada exitosamente por ${nueva_venta.total_neto:,.2f} COP!")

    return redirect('/dashboard/#ventas')


@personal_requerido
def editar_venta_dashboard(request, id_venta):
    """
    CRUD VENTAS: MODIFICACIÓN DE VENTA DESDE EL DASHBOARD (MODAL / VENTANA)
    """
    venta = get_object_or_404(Venta, pk=id_venta)
    if request.method == 'POST':
        datos = _extraer_datos_venta(request.POST)
        for campo, valor in datos.items():
            setattr(venta, campo, valor)
        venta.save()

        messages.success(request, f"¡Venta #VTA-{venta.id_venta} actualizada exitosamente!")

    return redirect('/dashboard/#ventas')


@personal_requerido
def eliminar_venta_dashboard(request, id_venta):
    """
    CRUD VENTAS: ELIMINACIÓN DE VENTA DESDE EL DASHBOARD (MODAL / VENTANA POST)
    """
    if request.method == 'POST':
        venta = get_object_or_404(Venta, pk=id_venta)
        num_venta = venta.id_venta
        venta.delete()
        messages.success(request, f"La venta #VTA-{num_venta} fue eliminada del sistema.")
    else:
        messages.warning(request, "La eliminación de venta requiere confirmación POST.")

    return redirect('/dashboard/#ventas')


@personal_requerido
def exportar_ventas_csv(request):
    """
    EXPORTACIÓN DE HISTORIAL DE VENTAS A CSV (COMPATIBLE CON EXCEL)
    ---------------------------------------------------------------
    Genera un archivo descargable con codificación UTF-8 con BOM y delimitador ';'
    para auditoría contable y cierre de caja diario/mensual.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    fecha_str = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="ventas_al_paso_{fecha_str}.csv"'
    response.write('﻿')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID Venta',
        'Fecha y Hora',
        'Cajero Responsable',
        'Cliente',
        'Canal / Origen',
        'Medio de Pago',
        'Subtotal (COP)',
        'Descuento (COP)',
        'Total Neto (COP)',
        'Estado',
    ])

    ventas = Venta.objects.select_related('id_usuario_cajero').order_by('-fecha_venta')
    for v in ventas:
        fecha_local = timezone.localtime(v.fecha_venta).strftime('%Y-%m-%d %H:%M') if v.fecha_venta else ''
        cajero_nombre = v.id_usuario_cajero.username if v.id_usuario_cajero else 'Sistema'
        cliente_str = str(v.cliente) if v.cliente else (f'Cliente #{v.id_cliente}' if v.id_cliente else 'Consumidor Final')
        descuento_val = v.descuento or Decimal('0.00')
        writer.writerow([
            f'#VTA-{v.id_venta}',
            fecha_local,
            cajero_nombre,
            cliente_str,
            v.origen_venta,
            v.medio_pago,
            f'{v.subtotal:.2f}',
            f'{descuento_val:.2f}',
            f'{v.total_neto:.2f}',
            v.estado_venta,
        ])

    return response


@personal_requerido
def recibo_venta_view(request, id_venta):
    """
    COMPROBANTE / TIRILLA DE VENTA IMPRIMIBLE
    -----------------------------------------
    Renderiza un comprobante limpio con logotipo oficial listo para impresión
    térmica o guardado en PDF desde el navegador.
    """
    venta = get_object_or_404(
        Venta.objects.select_related('id_usuario_cajero'),
        pk=id_venta,
    )
    return render(request, 'principal/ventas/recibo_venta.html', {'venta': venta})


def registrar_pedido_whatsapp(request):
    """
    ENDPOINT API: REGISTRO AUTOMÁTICO DE PEDIDOS DEL CARRITO WHATSAPP
    -----------------------------------------------------------------
    Conecta el carrito web ('cart.js') con el módulo 'Gestión de Ventas' (#ventas)
    del Dashboard. Cuando el cliente presiona 'Enviar pedido por WhatsApp', se
    crea automáticamente una Venta con origen 'WhatsApp' y estado 'Pendiente'.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, TypeError):
        payload = {}

    items = payload.get('items') or []
    total_raw = payload.get('total', 0)

    try:
        monto = Decimal(str(total_raw))
    except (InvalidOperation, ValueError, TypeError):
        monto = Decimal('0.00')

    if monto <= Decimal('0.00') and isinstance(items, list):
        acumulado = Decimal('0.00')
        for item in items:
            if isinstance(item, dict):
                try:
                    precio = Decimal(str(item.get('precio', 0)))
                    cantidad = Decimal(str(item.get('cantidad', 1)))
                    if precio > 0 and cantidad > 0:
                        acumulado += precio * cantidad
                except (InvalidOperation, ValueError, TypeError):
                    continue
        monto = acumulado

    if monto <= Decimal('0.00'):
        return JsonResponse({'ok': False, 'error': 'Monto de pedido inválido.'}, status=400)

    # Determinar usuario responsable para el registro contable
    if request.user.is_authenticated:
        cajero = request.user
    else:
        cajero = (
            User.objects.filter(is_active=True, is_superuser=True).order_by('id').first()
            or User.objects.filter(is_active=True).order_by('id').first()
        )

    if not cajero:
        return JsonResponse({'ok': False, 'error': 'No hay cajero disponible.'}, status=503)

    nueva_venta = Venta.objects.create(
        id_usuario_cajero=cajero,
        origen_venta='WhatsApp',
        medio_pago='Transferencia',
        subtotal=monto,
        descuento=Decimal('0.00'),
        total_neto=monto,
        estado_venta='Pendiente',
    )
    return JsonResponse({
        'ok': True,
        'id_venta': nueva_venta.id_venta,
        'codigo': f'#VTA-{nueva_venta.id_venta}',
    }, status=201)


class CustomLoginView(auth_views.LoginView):
    """
    VISTA DE INICIO DE SESIÓN CON REDIRECCIÓN INTELIGENTE POR ROL
    -------------------------------------------------------------
    NOTA TÉCNICA PARA EL EQUIPO (GAES):
    Evita que los usuarios con rol 'cliente' sean enviados a '/dashboard/' tras
    iniciar sesión (lo que antes les mostraba una alerta de 'Acceso restringido').
    - Personal operativo (Superadmin, Admin, Bodeguero, Cajero) -> '/dashboard/'
    - Clientes de la tienda ('cliente') -> '/' (Portada de la tienda)
    """
    template_name = 'principal/login.html'

    def get_default_redirect_url(self):
        user = self.request.user
        if user.is_authenticated and es_personal_operativo(user):
            return str(reverse_lazy('dashboard'))
        if user.is_authenticated:
            nombre = user.first_name or user.username
            messages.success(self.request, f'¡Bienvenido de nuevo a Al Paso Frutería, {nombre}!')
        return str(reverse_lazy('index'))


def error_404_view(request, exception=None):
    """
    MANEJADOR DE ERROR 404 (PÁGINA NO ENCONTRADA Y PREVISUALIZACIÓN)
    """
    return render(request, 'principal/404.html', status=404)


def error_500_view(request):
    """
    MANEJADOR DE ERROR 500 (ERROR INTERNO DEL SERVIDOR Y PREVISUALIZACIÓN)
    """
    return render(request, 'principal/500.html', status=500)


def logout_view(request):
    """
    CIERRE DE SESIÓN SEGURO ('/accounts/logout/')
    ---------------------------------------------
    Exige petición POST con token CSRF para prevenir desautenticación forzada.
    Destruye la sesión activa del usuario y lo redirige limpiamente a la portada.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    logout(request)
    return redirect('index')

def registro_view(request):
    """
    REGISTRO PÚBLICO DE CLIENTES Y ASIGNACIÓN DE PERFIL ('/registro/')
    Almacena: username, email, contraseña, teléfono, rol ('cliente'), estado ('activo')
    y fecha de creación automática vía ORM.
    """
    if request.user.is_authenticated:
        return redirect('index')

    form_data = {}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        terminos = request.POST.get('terms')

        form_data = {
            'username': username,
            'email': email,
            'telefono': telefono,
        }

        # 1. Validaciones de presencia de campos obligatorios
        if not username or not email or not password:
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return render(request, 'principal/registro.html', {'form_data': form_data})

        # 2. Validación de aceptación de términos del servicio
        if not terminos:
            messages.error(request, 'Debes aceptar los términos de servicio y políticas de privacidad para registrarte.')
            return render(request, 'principal/registro.html', {'form_data': form_data})

        # 3. Validación de coincidencia de contraseñas
        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden.')
            return render(request, 'principal/registro.html', {'form_data': form_data})

        # 4. Validación de formato de correo electrónico
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'El correo electrónico ingresado no tiene un formato válido.')
            return render(request, 'principal/registro.html', {'form_data': form_data})

        # 5. Validación de unicidad de usuario y correo (insensible a mayúsculas)
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'El nombre de usuario ya se encuentra registrado.')
            return render(request, 'principal/registro.html', {'form_data': form_data})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return render(request, 'principal/registro.html', {'form_data': form_data})

        # 6. Validación de robustez de contraseña mediante validadores de Django
        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, 'principal/registro.html', {'form_data': form_data})

        # 7. Crear el usuario base de autenticación con rol 'cliente' seguro
        nuevo_usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        nuevo_usuario.is_staff = False
        nuevo_usuario.is_superuser = False
        nuevo_usuario.save()

        # 8. Configurar perfil vinculado de cliente
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=nuevo_usuario)
        perfil.telefono = telefono
        perfil.rol = 'cliente'
        perfil.estado = 'activo'
        perfil.save()

        # 9. Iniciar sesión automáticamente y redirigir
        auth_login(request, nuevo_usuario, backend='principal.backends.EmailOrUsernameModelBackend')
        messages.success(request, f'¡Bienvenido a Al Paso Frutería, {username}!')
        return redirect('index')

    return render(request, 'principal/registro.html', {'form_data': form_data})


# ==============================================================================
# CRUD SEGURO GUIA 4 (PRODUCTOS Y CATEGORIAS - FBV Y CBV)
# ==============================================================================

@personal_requerido
def producto_listar(request):
    """
    Lista todos los productos del catálogo ordenados alfabéticamente (FBV).
    """
    productos = Producto.objects.select_related("categoria").order_by("nombre")
    return render(
        request,
        "principal/productos/lista.html",
        {"productos": productos, "titulo": "Gestion de productos"},
    )


@personal_requerido
def producto_crear(request):
    """
    Crea un nuevo producto mediante formulario validado (FBV).
    """
    datos = request.POST if request.method == "POST" else None
    formulario = ProductoForm(datos)
    if request.method == "POST":
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "El producto se creo correctamente.")
            return redirect("principal:producto_listar")
        messages.error(request, "Revisa los errores del formulario.")
    return render(
        request,
        "principal/productos/formulario.html",
        {"formulario": formulario, "titulo": "Crear producto"},
    )


@personal_requerido
def producto_editar(request, pk):
    """
    Actualiza la información de un producto existente (FBV).
    """
    producto = get_object_or_404(Producto, pk=pk)
    datos = request.POST if request.method == "POST" else None
    formulario = ProductoForm(datos, instance=producto)
    if request.method == "POST":
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "El producto se actualizo correctamente.")
            return redirect("principal:producto_listar")
        messages.error(request, "Revisa los errores del formulario.")
    return render(
        request,
        "principal/productos/formulario.html",
        {
            "formulario": formulario,
            "producto": producto,
            "titulo": "Editar producto",
        },
    )


@personal_requerido
def producto_eliminar(request, pk):
    """
    Elimina un producto previa confirmación y petición POST segura (FBV).
    """
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "El producto se elimino correctamente.")
        return redirect("principal:producto_listar")
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(
        request,
        "principal/productos/confirmar_eliminar.html",
        {"objeto": producto, "titulo": "Eliminar producto"},
    )


class CategoriaListaView(PersonalRequeridoMixin, ListView):
    """
    Vista basada en clases para listar categorías ordenadas por nombre (CBV).
    """
    model = Categoria
    template_name = "principal/categorias/lista.html"
    context_object_name = "categorias"
    ordering = ["nombre"]

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Gestion de categorias"
        return contexto


class CategoriaCrearView(PersonalRequeridoMixin, SuccessMessageMixin, CreateView):
    """
    Vista basada en clases para registrar una nueva categoría (CBV).
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = "principal/categorias/formulario.html"
    success_url = reverse_lazy("principal:categoria_listar")
    success_message = "La categoria «%(nombre)s» se creo correctamente."

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Crear categoria"
        return contexto


class CategoriaEditarView(PersonalRequeridoMixin, SuccessMessageMixin, UpdateView):
    """
    Vista basada en clases para editar una categoría existente (CBV).
    """
    model = Categoria
    form_class = CategoriaForm
    template_name = "principal/categorias/formulario.html"
    success_url = reverse_lazy("principal:categoria_listar")
    success_message = "La categoria «%(nombre)s» se actualizo correctamente."

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Editar categoria"
        return contexto


class CategoriaEliminarView(PersonalRequeridoMixin, DeleteView):
    """
    Vista basada en clases para eliminar una categoría previa confirmación (CBV).
    """
    model = Categoria
    template_name = "principal/categorias/confirmar_eliminar.html"
    success_url = reverse_lazy("principal:categoria_listar")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Eliminar categoria"
        return contexto

    def form_valid(self, form):
        messages.success(self.request, "La categoria se elimino correctamente.")
        return super().form_valid(form)


# ==============================================================================
# MÓDULO DE GESTIÓN DE VENTAS (PUNTO DE VENTA Y FACTURACIÓN)
# ==============================================================================

@personal_requerido
def lista_ventas(request):
    """
    1. LISTADO DE VENTAS: Muestra el historial completo de ventas con métricas clave.
    """
    ventas = Venta.objects.select_related('id_usuario_cajero').all().order_by('-fecha_venta')
    total_ingresos = sum(v.total_neto for v in ventas)
    hoy = timezone.now().date()
    ventas_hoy = [v for v in ventas if v.fecha_venta and v.fecha_venta.date() == hoy]
    ventas_hoy_ingresos = sum(v.total_neto for v in ventas_hoy)

    return render(request, 'principal/ventas/lista_ventas.html', {
        'ventas': ventas,
        'total_ingresos': total_ingresos,
        'total_ventas': ventas.count(),
        'ventas_hoy_count': len(ventas_hoy),
        'ventas_hoy_ingresos': ventas_hoy_ingresos,
        'titulo': 'Gestión de Ventas'
    })


@personal_requerido
def crear_venta(request):
    """
    2. CREAR VENTA: Formulario completo con validación segura de tipos numéricos.
    """
    if request.method == 'POST':
        datos = _extraer_datos_venta(request.POST)
        Venta.objects.create(
            id_usuario_cajero=request.user,
            **datos
        )
        messages.success(request, "Venta registrada con éxito.")
        return redirect(_obtener_redireccion_segura(request, 'lista_ventas'))

    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    return render(request, 'principal/ventas/venta_form.html', {
        'clientes': clientes,
        'productos': productos,
        'titulo': 'Registrar Nueva Venta'
    })


@personal_requerido
def editar_venta(request, pk):
    """
    3. EDITAR VENTA: Actualiza una transacción existente con validación numérica segura.
    """
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        datos = _extraer_datos_venta(request.POST)
        for campo, valor in datos.items():
            setattr(venta, campo, valor)
        venta.save()

        messages.success(request, f"Venta #{venta.id_venta} actualizada exitosamente.")
        return redirect(_obtener_redireccion_segura(request, 'lista_ventas'))

    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    return render(request, 'principal/ventas/venta_form.html', {
        'venta': venta,
        'clientes': clientes,
        'productos': productos,
        'titulo': f'Editar Venta #{venta.id_venta}'
    })


@personal_requerido
def eliminar_venta(request, pk):
    """
    4. ELIMINAR VENTA: Muestra pantalla de confirmación y borra el registro de la BD.
    """
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        num_venta = venta.id_venta
        venta.delete()
        messages.success(request, f"La venta #{num_venta} fue eliminada del sistema.")
        return redirect(_obtener_redireccion_segura(request, 'lista_ventas'))

    return render(request, 'principal/ventas/venta_confirm_delete.html', {
        'venta': venta,
        'titulo': f'Confirmar Eliminación de Venta #{venta.id_venta}'
    })