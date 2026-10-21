# ==============================================================================
# ENRUTADOR PRINCIPAL DEL PROYECTO (config/urls.py)
# Define el mapa de navegación y la correspondencia entre URLs y vistas de Django.
# ==============================================================================

from django.contrib import admin
from django.urls import path, include
from principal.views import (
    inicio,
    catalogo_frutas_view,
    dashboard_view,
    crear_producto_dashboard,
    editar_producto_dashboard,
    eliminar_producto_dashboard,
    crear_categoria_dashboard,
    eliminar_categoria_dashboard,
    crear_usuario_dashboard,
    editar_usuario_dashboard,
    eliminar_usuario_dashboard,
    exportar_inventario_csv,
    crear_proveedor_dashboard,
    editar_proveedor_dashboard,
    eliminar_proveedor_dashboard,
    error_404_view,
    error_500_view,
    error_404_preview,
    error_500_preview,
    logout_view,
    admin_preview,
    admin_productos_preview,
    admin_producto_list_preview,
    registro_view
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. PANEL DE ADMINISTRACIÓN DE DJANGO (ORM & CRUD Nativo)
    # -------------------------------------------------------------------------
    path('admin/', admin.site.urls),

    # Rutas auxiliares de previsualización para auditoría y capturas del informe técnico
    path('admin-preview/', admin_preview, name='admin_preview'),
    path('admin-preview/principal/', admin_productos_preview, name='admin_productos_preview'),
    path('admin-preview/principal/producto/', admin_producto_list_preview, name='admin_producto_list_preview'),

    # -------------------------------------------------------------------------
    # 2. VISTAS PÚBLICAS DE LA TIENDA WEB (FRONTEND CLIENTES)
    # -------------------------------------------------------------------------
    path('', inicio, name='index'),
    path('inicio/', inicio, name='inicio'),
    path('tienda/', inicio, name='tienda'),

    # Catálogo especializado de frutas con filtrado reactivo por categorías
    path('catalogo-frutas/', catalogo_frutas_view, name='catalogo_frutas'),
    path('catalogo/', catalogo_frutas_view, name='catalogo'),

    # -------------------------------------------------------------------------
    # 3. PANEL DE CONTROL INTERNO (DASHBOARD, INVENTARIO Y PROVEEDORES)
    # -------------------------------------------------------------------------
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/producto/crear/', crear_producto_dashboard, name='dashboard_crear_producto'),
    path('dashboard/producto/<int:id_producto>/editar/', editar_producto_dashboard, name='dashboard_editar_producto'),
    path('dashboard/producto/<int:id_producto>/eliminar/', eliminar_producto_dashboard, name='dashboard_eliminar_producto'),
    path('dashboard/categoria/crear/', crear_categoria_dashboard, name='dashboard_crear_categoria'),
    path('dashboard/categoria/<int:id_categoria>/eliminar/', eliminar_categoria_dashboard, name='dashboard_eliminar_categoria'),
    # CRUD de Usuarios y Roles (FBV con get_object_or_404 y confirmación POST)
    path('dashboard/usuario/crear/', crear_usuario_dashboard, name='dashboard_crear_usuario'),
    path('dashboard/usuario/<int:user_id>/editar/', editar_usuario_dashboard, name='dashboard_editar_usuario'),
    path('dashboard/usuario/<int:user_id>/eliminar/', eliminar_usuario_dashboard, name='dashboard_eliminar_usuario'),
    
    # Exportación de inventario compatible con Excel
    path('dashboard/inventario/exportar-csv/', exportar_inventario_csv, name='dashboard_exportar_inventario_csv'),

    # Gestión de proveedores agrícolas
    path('dashboard/proveedor/crear/', crear_proveedor_dashboard, name='dashboard_crear_proveedor'),
    path('dashboard/proveedor/<int:id_proveedor>/editar/', editar_proveedor_dashboard, name='dashboard_editar_proveedor'),
    path('dashboard/proveedor/<int:id_proveedor>/eliminar/', eliminar_proveedor_dashboard, name='dashboard_eliminar_proveedor'),

    # -------------------------------------------------------------------------
    # 4. GESTIÓN DE SESIONES Y AUTENTICACIÓN
    # -------------------------------------------------------------------------
    path('login/', auth_views.LoginView.as_view(template_name='principal/login.html'), name='login_direct'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='principal/login.html'), name='login'),
    path('registro/', registro_view, name='registro'),

    path('logout/', logout_view, name='logout_direct'),
    path('accounts/logout/', logout_view, name='logout'),

    # -------------------------------------------------------------------------
    # 5. MÓDULO DE GESTIÓN CRUD GUÍA 4 (FBV Y CBV)
    # -------------------------------------------------------------------------
    path('gestion/', include('principal.urls')),

    # -------------------------------------------------------------------------
    # 6. RUTAS DE PREVISUALIZACIÓN DE ERRORES DE MARCA
    # -------------------------------------------------------------------------
    path('404/', error_404_preview, name='error_404_preview'),
    path('500/', error_500_preview, name='error_500_preview'),
]

# Manejadores globales de error HTTP para producción
handler404 = 'principal.views.error_404_view'
handler500 = 'principal.views.error_500_view'

