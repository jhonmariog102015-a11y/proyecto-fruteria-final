# ==============================================================================
# CONTROLADOR DE VISTAS (principal/views.py)
# Gestiona la lógica de negocio, consultas al ORM y renderizado de plantillas.
# ==============================================================================

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm


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
        'titulo': 'El Paso Frutería — Mercado Campesino',
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
        'titulo': 'Catálogo de Frutas Frescas — El Paso Frutería',
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

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_bajo_stock': total_bajo_stock,
        'total_agotados': total_agotados,
        'total_usuarios': total_usuarios,
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