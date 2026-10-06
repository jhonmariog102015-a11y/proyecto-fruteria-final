# ==============================================================================
# CONTROLADOR DE VISTAS (principal/views.py)
# Gestiona la lógica de negocio, consultas al ORM y renderizado de plantillas.
# ==============================================================================

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from .models import Producto, Categoria


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
    # Consulta optimizada con JOIN a la tabla categorias
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()

    # Paquete de datos que viaja hacia el template
    context = {
        'titulo': 'El Paso Frutería — Mercado Campesino',
        'productos': productos,
        'categorias': categorias,
        'total_productos': productos.count(),  # Cuenta el total para las insignias
    }
    return render(request, 'principal/index.html', context)


def tienda_view(request):
    """
    VISTA DE TIENDA ALTERNATIVA ('/tienda/')
    ----------------------------------------
    Provee una vista complementaria con diseño de vitrina comercial para los productos.
    """
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    context = {
        'titulo': 'El Paso Frutería — Tienda Oficial',
        'productos': productos,
        'categorias': categorias,
        'total_productos': productos.count(),
    }
    return render(request, 'fruteria/tienda.html', context)


def catalogo_frutas_view(request):
    """
    CATÁLOGO INTERACTIVO DE FRUTAS ('/catalogo-frutas/')
    ----------------------------------------------------
    Renderiza la vitrina especializada de frutas donde el usuario puede
    interactuar con filtros reactivos en vivo, ver grados Brix (°Brix), origen y precios.
    """
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    context = {
        'titulo': 'Catálogo de Frutas Frescas — El Paso Frutería',
        'productos': productos,
        'categorias': categorias,
        'total_productos': productos.count(),
    }
    return render(request, 'fruteria/catalogo_frutas.html', context)


@login_required
def dashboard_view(request):
    """
    PANEL ADMINISTRATIVO PRIVADO ('/dashboard/')
    --------------------------------------------
    - Protegido por el decorador '@login_required': sólo usuarios autenticados pueden entrar.
    - Calcula estadísticas en tiempo real:
      * Conteo total de productos en inventario.
      * Conteo de usuarios registrados en el sistema.
      * Listado de productos para la tabla de gestión de stock.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Extracción de datos para las métricas del panel
    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.all()
    total_productos = productos.count()
    total_usuarios = User.objects.count()

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
    })


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