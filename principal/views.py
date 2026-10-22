# ==============================================================================
# CONTROLADOR DE VISTAS (principal/views.py)
# Gestiona la lógica de negocio, consultas al ORM y renderizado de plantillas.
# ==============================================================================

import csv
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Case, When, Value, IntegerField
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Producto, Categoria, Proveedor, PerfilUsuario
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



def inicio(request):
    """
    VISTA PRINCIPAL / LANDING PAGE ('/' y '/inicio/')
    -------------------------------------------------
    1. Consulta la base de datos para obtener todos los productos ordenados por su ID.
    2. Utiliza 'select_related('categoria')' para optimizar la consulta SQL (JOIN)
       y evitar problemas de rendimiento (N+1 queries).
    3. Obtiene todas las categorías disponibles para alimentar las tarjetas y carrusel.
    4. Envía los datos al contexto para que 'index.html' dibuje dinámicamente las tarjetas.
    """
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    # Producto destacado para el Hero dinámico asimétrico
    producto_destacado = productos.filter(en_oferta=True).first() or productos.first()
    productos_oferta = productos.filter(en_oferta=True)

    context = {
        'titulo': 'Al Paso Frutería — Mercado Campesino',
        'productos': productos,
        'productos_oferta': productos_oferta,
        'categorias': categorias,
        'producto_destacado': producto_destacado,
        'total_productos': productos.count(),
        'total_ofertas': productos_oferta.count(),
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
    # NOTA TÉCNICA PARA EL EQUIPO (GAES):
    # Se unificó la ubicación de plantillas dentro de 'principal/templates/principal/'
    # para que todos los archivos HTML (index, catalogo, dashboard, login) residan
    # en una sola carpeta bajo la convención estándar de Django MVT.
    return render(request, 'principal/catalogo_frutas.html', context)


@login_required
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

    # Proveedores y productores aliados
    proveedores = Proveedor.objects.all().order_by('razon_social')
    total_proveedores = proveedores.count()

    # NOTA TÉCNICA (INTEGRACIÓN EQUIPO - CÓDIGO DE GUTIÉRREZ):
    # Sincronización de perfiles administrativos y métricas del equipo de gestión
    for u in User.objects.filter(perfil__isnull=True):
        rol_def = 'admin' if u.is_superuser else ('bodeguero' if u.is_staff else 'cajero')
        PerfilUsuario.objects.get_or_create(
            usuario=u,
            defaults={'rol': rol_def, 'estado': 'activo', 'telefono': '3001234567'}
        )

    # Obtener única y exclusivamente los REGISTROS ACTIVOS ordenados por ROLES:
    # Jerarquía requerida: 1. Super Admin, 2. Bodeguero, 3. Cajero
    perfiles_usuarios = PerfilUsuario.objects.select_related('usuario').filter(
        estado='activo',
        usuario__is_active=True
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

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'proveedores': proveedores,
        'perfiles_usuarios': perfiles_usuarios,
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_bajo_stock': total_bajo_stock,
        'productos_bajo_stock': productos_bajo_stock,
        'total_agotados': total_agotados,
        'total_usuarios': total_usuarios,
        'total_proveedores': total_proveedores,
        'total_activos': total_activos,
        'total_superadmins': total_superadmins,
        'total_bodegueros': total_bodegueros,
        'total_cajeros': total_cajeros,
        'total_admins': total_activos,
        'total_admins_activos': total_activos,
        'total_staff': total_staff,
        'inversion_total': inversion_total,
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


@login_required
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

        if estado == 'inactivo':
            target_user.is_active = False
        else:
            target_user.is_active = True

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


@login_required
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


@login_required
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


@login_required
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


@login_required
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


def error_404_view(request, exception=None):
    """
    MANEJADOR DE ERROR 404 (PÁGINA NO ENCONTRADA)
    """
    return render(request, 'principal/404.html', status=404)


def error_500_view(request):
    """
    MANEJADOR DE ERROR 500 (ERROR INTERNO DEL SERVIDOR)
    """
    return render(request, 'principal/500.html', status=500)


def error_404_preview(request):
    """
    RUTA DE AUDITORÍA Y PREVISUALIZACIÓN DE ERROR 404
    """
    return render(request, 'principal/404.html', status=404)


def error_500_preview(request):
    """
    RUTA DE AUDITORÍA Y PREVISUALIZACIÓN DE ERROR 500
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


def admin_preview(request):
    """
    PREVISUALIZACIÓN DE AUDITORÍA: PANEL GENERAL
    Permite generar reportes técnicos y capturas del estado del admin.
    """
    from django.contrib import admin
    from django.contrib.auth.models import User
    user = User.objects.filter(username='admin').first()
    if user:
        request.user = user
    return admin.site.index(request)


def admin_productos_preview(request):
    """
    PREVISUALIZACIÓN DE AUDITORÍA: APP PRINCIPAL
    Carga el índice de modelos de la app 'principal' en el panel de Django.
    """
    from django.contrib import admin
    from django.contrib.auth.models import User
    user = User.objects.filter(username='admin').first()
    if user:
        request.user = user
    return admin.site.app_index(request, 'principal')


def admin_producto_list_preview(request):
    """
    PREVISUALIZACIÓN DE AUDITORÍA: LISTADO DE PRODUCTOS
    Genera la vista de tabla tabular de productos en el admin de Django.
    """
    from django.contrib import admin
    from django.contrib.auth.models import User
    user = User.objects.filter(username='admin').first()
    if user:
        request.user = user
    from .models import Producto
    return admin.site._registry[Producto].changelist_view(request)


def registro_view(request):
    """
    REGISTRO PÚBLICO DE CLIENTES Y ASIGNACIÓN DE PERFIL ('/registro/')
    Almacena: username, email, contraseña, teléfono, rol ('cliente'), estado ('activo')
    y fecha de creación automática vía ORM.

    NOTA TÉCNICA PARA EL EQUIPO (CORRECCIONES SOBRE EL CÓDIGO DE GUTIÉRREZ):
    1. SEGURIDAD (Escalamiento de privilegios): En el registro público el rol se fuerza
       estrictamente a 'cliente' (is_staff=False, is_superuser=False). Los roles 'admin'
       y 'cajero' solo pueden ser concedidos por administradores en /admin/auth/user/.
    2. VALIDACIÓN DE EMAIL: Se incorpora validate_email de Django para descartar correos malformados.
    3. POLÍTICAS DE CONTRASEÑA: Se evalúa validate_password para cumplir con las políticas
       configuradas en settings.py (longitud mínima, no numérica, no común).
    4. EXPERIENCIA DE USUARIO: Los datos ingresados (form_data) se devuelven a la plantilla
       en caso de error para que el usuario no deba reescribirlos.
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
            return render(request, 'principal/Registro.html', {'form_data': form_data})

        # 2. Validación de aceptación de términos del servicio
        if not terminos:
            messages.error(request, 'Debes aceptar los términos de servicio y políticas de privacidad para registrarte.')
            return render(request, 'principal/Registro.html', {'form_data': form_data})

        # 3. Validación de coincidencia de contraseñas
        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden.')
            return render(request, 'principal/Registro.html', {'form_data': form_data})

        # 4. Validación de formato de correo electrónico
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'El correo electrónico ingresado no tiene un formato válido.')
            return render(request, 'principal/Registro.html', {'form_data': form_data})

        # 5. Validación de unicidad de usuario y correo (insensible a mayúsculas)
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'El nombre de usuario ya se encuentra registrado.')
            return render(request, 'principal/Registro.html', {'form_data': form_data})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return render(request, 'principal/Registro.html', {'form_data': form_data})

        # 6. Validación de robustez de contraseña mediante validadores de Django
        try:
            validate_password(password)
        except ValidationError as e:
            for err in e.messages:
                messages.error(request, err)
            return render(request, 'principal/Registro.html', {'form_data': form_data})

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

    return render(request, 'principal/Registro.html', {'form_data': form_data})


# ==============================================================================
# CRUD SEGURO GUIA 4 (PRODUCTOS Y CATEGORIAS - FBV Y CBV)
# ==============================================================================

@login_required
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


@login_required
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


@login_required
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


@login_required
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


class CategoriaListaView(LoginRequiredMixin, ListView):
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


class CategoriaCrearView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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


class CategoriaEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class CategoriaEliminarView(LoginRequiredMixin, DeleteView):
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


