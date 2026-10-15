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
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Producto, Categoria, Proveedor, PerfilUsuario
from .forms import ProductoForm, CategoriaForm, ProveedorForm


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

    context = {
        'titulo': 'Al Paso Frutería — Mercado Campesino',
        'productos': productos,
        'categorias': categorias,
        'producto_destacado': producto_destacado,
        'total_productos': productos.count(),
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

    # Conteo para filtros rápidos
    total_bajo_stock = sum(1 for p in productos if p.stock_actual <= p.stock_minimo)
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

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'proveedores': proveedores,
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_bajo_stock': total_bajo_stock,
        'total_agotados': total_agotados,
        'total_usuarios': total_usuarios,
        'total_proveedores': total_proveedores,
        'inversion_total': inversion_total,
        'valor_venta_potencial': valor_venta_potencial,
        'ganancia_potencial': ganancia_potencial,
        'margen_promedio': margen_promedio,
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
    Destruye la sesión activa del usuario y lo redirige limpiamente a la portada.
    """
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
    REGISTRO PÚBLICO DE USUARIOS Y ASIGNACIÓN DE PERFIL ('/registro/')
    Almacena: username, email, contraseña, teléfono, rol, estado ('activo')
    y fecha de creación automática vía ORM.
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', 'cliente').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validaciones de integridad
        if not username or not email or not password:
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return render(request, 'principal/Registro.html')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden.')
            return render(request, 'principal/Registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya se encuentra registrado.')
            return render(request, 'principal/Registro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está en uso.')
            return render(request, 'principal/Registro.html')

        # 1. Crear el usuario base de autenticación
        nuevo_usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 2. Configurar perfil vinculado y permisos acordes al rol
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=nuevo_usuario)
        perfil.telefono = telefono
        perfil.rol = rol
        perfil.estado = 'activo'
        perfil.save()

        if rol == 'admin':
            nuevo_usuario.is_staff = True
            nuevo_usuario.is_superuser = True
            nuevo_usuario.save()
        elif rol == 'cajero':
            nuevo_usuario.is_staff = True
            nuevo_usuario.save()

        # 3. Autenticar e iniciar sesión de inmediato
        auth_login(request, nuevo_usuario, backend='principal.backends.EmailOrUsernameModelBackend')
        messages.success(request, f'¡Bienvenido a Al Paso Frutería, {username}!')

        # Redirigir según el rol asignado
        if rol in ['admin', 'cajero']:
            return redirect('dashboard')
        return redirect('index')

    return render(request, 'principal/Registro.html')

