# ==============================================================================
# ENRUTADOR PRINCIPAL DEL PROYECTO (config/urls.py)
# Define el mapa de navegación y la correspondencia entre URLs y vistas de Django.
# ==============================================================================

from django.contrib import admin
from django.urls import path, include
from principal.views import (
    inicio,
    tienda_view,
    catalogo_frutas_view,
    dashboard_view,
    crear_producto_dashboard,
    editar_producto_dashboard,
    eliminar_producto_dashboard,
    crear_categoria_dashboard,
    eliminar_categoria_dashboard,
    logout_view,
    admin_preview,
    admin_productos_preview,
    admin_producto_list_preview
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. PANEL DE ADMINISTRACIÓN DE DJANGO (ORM & CRUD Nativo)
    # -------------------------------------------------------------------------
    # Acceso oficial para administradores del sistema (requiere superusuario)
    path('admin/', admin.site.urls),

    # Rutas auxiliares de previsualización para auditoría y capturas del informe técnico
    path('admin-preview/', admin_preview, name='admin_preview'),
    path('admin-preview/principal/', admin_productos_preview, name='admin_productos_preview'),
    path('admin-preview/principal/producto/', admin_producto_list_preview, name='admin_producto_list_preview'),

    # -------------------------------------------------------------------------
    # 2. VISTAS PÚBLICAS DE LA TIENDA WEB (FRONTEND CLIENTES)
    # -------------------------------------------------------------------------
    # Ruta raíz ('/') y alias ('/inicio/', '/tienda/'): Carga la tienda principal
    path('', inicio, name='index'),
    path('inicio/', inicio, name='inicio'),
    path('tienda/', inicio, name='tienda'),

    # Catálogo especializado de frutas con filtrado reactivo por categorías
    path('catalogo-frutas/', catalogo_frutas_view, name='catalogo_frutas'),
    path('catalogo/', catalogo_frutas_view, name='catalogo'),

    # -------------------------------------------------------------------------
    # 3. PANEL DE CONTROL INTERNO (DASHBOARD Y GESTIÓN TOTAL)
    # -------------------------------------------------------------------------
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/producto/crear/', crear_producto_dashboard, name='dashboard_crear_producto'),
    path('dashboard/producto/<int:id_producto>/editar/', editar_producto_dashboard, name='dashboard_editar_producto'),
    path('dashboard/producto/<int:id_producto>/eliminar/', eliminar_producto_dashboard, name='dashboard_eliminar_producto'),
    path('dashboard/categoria/crear/', crear_categoria_dashboard, name='dashboard_crear_categoria'),
    path('dashboard/categoria/<int:id_categoria>/eliminar/', eliminar_categoria_dashboard, name='dashboard_eliminar_categoria'),

    # -------------------------------------------------------------------------
    # 4. GESTIÓN DE SESIONES Y AUTENTICACIÓN
    # -------------------------------------------------------------------------
    # Soporta tanto /login/ como /accounts/login/
    path('login/', auth_views.LoginView.as_view(template_name='principal/login.html'), name='login_direct'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='principal/login.html'), name='login'),

    # Cierre de sesión seguro y redirección a la página principal
    path('logout/', logout_view, name='logout_direct'),
    path('accounts/logout/', logout_view, name='logout'),
]

