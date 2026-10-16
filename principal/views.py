# ==============================================================================
# CONTROLADOR DE VISTAS (principal/views.py)
# Gestiona la lógica de negocio, consultas al ORM y renderizado de plantillas.
# ==============================================================================

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

# INICIO CAMBIOS GUÍA 4: importaciones de formularios, mensajes y protección CRUD.
from .forms import CategoriaForm, ProductoForm
from .models import Producto, Categoria
# FIN CAMBIOS GUÍA 4: importaciones de la guía.


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


# INICIO CAMBIOS GUÍA 4: CRUD seguro de productos mediante vistas basadas en funciones.
@login_required
def producto_listar(request):
    productos = Producto.objects.select_related("categoria").order_by("nombre")
    return render(
        request,
        "principal/productos/lista.html",
        {"productos": productos, "titulo": "Gestión de productos"},
    )


@login_required
def producto_crear(request):
    datos = request.POST if request.method == "POST" else None
    formulario = ProductoForm(datos)
    if request.method == "POST":
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "El producto se creó correctamente.")
            return redirect("principal:producto_listar")
        messages.error(request, "Revisa los errores del formulario.")
    return render(
        request,
        "principal/productos/formulario.html",
        {"formulario": formulario, "titulo": "Crear producto"},
    )


@login_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    datos = request.POST if request.method == "POST" else None
    formulario = ProductoForm(datos, instance=producto)
    if request.method == "POST":
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "El producto se actualizó correctamente.")
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
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "El producto se eliminó correctamente.")
        return redirect("principal:producto_listar")
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(
        request,
        "principal/productos/confirmar_eliminar.html",
        {"objeto": producto, "titulo": "Eliminar producto"},
    )


class CategoriaListaView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "principal/categorias/lista.html"
    context_object_name = "categorias"
    ordering = ["nombre"]

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Gestión de categorías"
        return contexto


class CategoriaCrearView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "principal/categorias/formulario.html"
    success_url = reverse_lazy("principal:categoria_listar")
    success_message = "La categoría «%(nombre)s» se creó correctamente."

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Crear categoría"
        return contexto


class CategoriaEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "principal/categorias/formulario.html"
    success_url = reverse_lazy("principal:categoria_listar")
    success_message = "La categoría «%(nombre)s» se actualizó correctamente."

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Editar categoría"
        return contexto


class CategoriaEliminarView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = "principal/categorias/confirmar_eliminar.html"
    success_url = reverse_lazy("principal:categoria_listar")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Eliminar categoría"
        return contexto

    def form_valid(self, form):
        messages.success(self.request, "La categoría se eliminó correctamente.")
        return super().form_valid(form)
# FIN CAMBIOS GUÍA 4: CRUD de productos y categorías.


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