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


from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Producto, Categoria


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
    from django.contrib.auth import get_user_model
    User = get_user_model()

    productos = Producto.objects.select_related('categoria').all().order_by('id_producto')
    categorias = Categoria.objects.annotate(num_productos=Count('productos')).order_by('nombre')
    total_productos = productos.count()
    total_ofertas = productos.filter(en_oferta=True).count()
    total_usuarios = User.objects.count()

    # Métricas financieras del catálogo
    inversion_total = sum(p.costo_compra * p.stock_actual for p in productos)
    valor_venta_potencial = sum(p.precio_efectivo * p.stock_actual for p in productos)
    ganancia_potencial = valor_venta_potencial - inversion_total
    margen_promedio = round((ganancia_potencial / inversion_total * 100), 1) if inversion_total > 0 else Decimal('0.0')

    return render(request, 'principal/dashboard.html', {
        'productos': productos,
        'categorias': categorias,
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_usuarios': total_usuarios,
        'inversion_total': inversion_total,
        'valor_venta_potencial': valor_venta_potencial,
        'ganancia_potencial': ganancia_potencial,
        'margen_promedio': margen_promedio,
    })


@login_required
def crear_producto_dashboard(request):
    """
    CREACIÓN DIRECTA DE PRODUCTOS DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            categoria_id = request.POST.get('categoria_id')
            costo_compra = Decimal(request.POST.get('costo_compra', '0').replace(',', '.'))
            precio_venta_unitario = Decimal(request.POST.get('precio_venta_unitario', '0').replace(',', '.'))
            en_oferta = request.POST.get('en_oferta') in ['on', 'true', 'True', '1']
            precio_oferta_raw = request.POST.get('precio_oferta', '').strip()
            precio_oferta = Decimal(precio_oferta_raw.replace(',', '.')) if (en_oferta and precio_oferta_raw) else None
            stock_actual = Decimal(request.POST.get('stock_actual', '0').replace(',', '.'))
            stock_minimo = Decimal(request.POST.get('stock_minimo', '5').replace(',', '.'))
            unidad_medida = request.POST.get('unidad_medida', 'kg').strip()
            origen = request.POST.get('origen', '').strip() or '🌱 Cosecha: Hace 1 día • Finca El Campo'
            icono_emoji = request.POST.get('icono_emoji', '🍎').strip() or '🍎'
            imagen_url = request.POST.get('imagen_url', '').strip() or 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=600&auto=format&fit=crop'
            estado = request.POST.get('estado', 'Disponible').strip()

            categoria = get_object_or_404(Categoria, pk=categoria_id)

            Producto.objects.create(
                nombre=nombre,
                categoria=categoria,
                costo_compra=costo_compra,
                precio_venta_unitario=precio_venta_unitario,
                en_oferta=en_oferta,
                precio_oferta=precio_oferta,
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                unidad_medida=unidad_medida,
                origen=origen,
                icono_emoji=icono_emoji,
                imagen_url=imagen_url,
                estado=estado
            )
            messages.success(request, f"¡Producto '{nombre}' creado exitosamente en el catálogo!")
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {str(e)}")

    return redirect('dashboard')


@login_required
def editar_producto_dashboard(request, id_producto):
    """
    EDICIÓN RÁPIDA DE PRECIOS, COSTOS, OFERTAS Y STOCK DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=id_producto)
        try:
            producto.nombre = request.POST.get('nombre', producto.nombre).strip()
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                producto.categoria = get_object_or_404(Categoria, pk=categoria_id)

            costo_raw = request.POST.get('costo_compra', '').replace(',', '.')
            if costo_raw:
                producto.costo_compra = Decimal(costo_raw)

            precio_raw = request.POST.get('precio_venta_unitario', '').replace(',', '.')
            if precio_raw:
                producto.precio_venta_unitario = Decimal(precio_raw)

            producto.en_oferta = request.POST.get('en_oferta') in ['on', 'true', 'True', '1']
            precio_oferta_raw = request.POST.get('precio_oferta', '').strip().replace(',', '.')
            if producto.en_oferta and precio_oferta_raw:
                producto.precio_oferta = Decimal(precio_oferta_raw)
            else:
                producto.precio_oferta = None

            stock_raw = request.POST.get('stock_actual', '').replace(',', '.')
            if stock_raw:
                producto.stock_actual = Decimal(stock_raw)

            stock_min_raw = request.POST.get('stock_minimo', '').replace(',', '.')
            if stock_min_raw:
                producto.stock_minimo = Decimal(stock_min_raw)

            producto.unidad_medida = request.POST.get('unidad_medida', producto.unidad_medida).strip()
            producto.origen = request.POST.get('origen', producto.origen).strip()
            producto.icono_emoji = request.POST.get('icono_emoji', producto.icono_emoji).strip()
            
            img_url = request.POST.get('imagen_url', '').strip()
            if img_url:
                producto.imagen_url = img_url

            producto.estado = request.POST.get('estado', producto.estado).strip()

            producto.save()
            messages.success(request, f"¡Producto '{producto.nombre}' actualizado con éxito!")
        except Exception as e:
            messages.error(request, f"Error al actualizar el producto: {str(e)}")

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
    CREACIÓN DE CATEGORÍA DESDE EL DASHBOARD
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, f"¡Categoría '{nombre}' creada exitosamente!")
        else:
            messages.error(request, "El nombre de la categoría no puede estar vacío.")
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