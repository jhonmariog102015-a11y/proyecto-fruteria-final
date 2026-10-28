# ==============================================================================
# ENRUTADOR PRINCIPAL DEL PROYECTO (config/urls.py)
# Define el mapa de navegación y la correspondencia entre URLs y vistas de Django.
# ==============================================================================
# NOTA TÉCNICA PARA EL EQUIPO (GAES):
# 1. Se eliminaron las rutas temporales sin uso ('/admin-preview/...') y se
#    unificaron las vistas de error 404 y 500 ('error_404_view', 'error_500_view').
# 2. Se integró 'CustomLoginView' para redirigir inteligentemente según el rol
#    del usuario (personal operativo -> '/dashboard/', cliente -> '/').
# 3. Se agregaron las rutas para conectar el carrito de WhatsApp con Ventas
#    ('/api/pedido-whatsapp/'), exportar ventas a CSV y generar recibos imprimibles.
# ==============================================================================

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
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
    exportar_ventas_csv,
    recibo_venta_view,
    registrar_pedido_whatsapp,
    CustomLoginView,
    crear_proveedor_dashboard,
    editar_proveedor_dashboard,
    eliminar_proveedor_dashboard,
    error_404_view,
    error_500_view,
    logout_view,
    registro_view,
    lista_ventas,
    crear_venta,
    editar_venta,
    eliminar_venta,
    crear_venta_dashboard,
    editar_venta_dashboard,
    eliminar_venta_dashboard,
)

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. PANEL DE ADMINISTRACIÓN DE DJANGO (ORM & CRUD Nativo)
    # -------------------------------------------------------------------------
    path('admin/', admin.site.urls),

    # -------------------------------------------------------------------------
    # 2. VISTAS PÚBLICAS DE LA TIENDA WEB (FRONTEND CLIENTES)
    # -------------------------------------------------------------------------
    path('', inicio, name='index'),
    path('inicio/', inicio, name='inicio'),
    path('tienda/', inicio, name='tienda'),

    # Catálogo especializado de frutas con filtrado reactivo por categorías
    path('catalogo-frutas/', catalogo_frutas_view, name='catalogo_frutas'),
    path('catalogo/', catalogo_frutas_view, name='catalogo'),

    # Endpoint API para registrar pedidos enviados desde el carrito de WhatsApp
    path('api/pedido-whatsapp/', registrar_pedido_whatsapp, name='api_pedido_whatsapp'),

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
    # Exportaciones compatibles con Excel (Inventario y Ventas)
    path('dashboard/inventario/exportar-csv/', exportar_inventario_csv, name='dashboard_exportar_inventario_csv'),
    path('dashboard/ventas/exportar-csv/', exportar_ventas_csv, name='dashboard_exportar_ventas_csv'),

    # Gestión de proveedores agrícolas
    path('dashboard/proveedor/crear/', crear_proveedor_dashboard, name='dashboard_crear_proveedor'),
    path('dashboard/proveedor/<int:id_proveedor>/editar/', editar_proveedor_dashboard, name='dashboard_editar_proveedor'),
    path('dashboard/proveedor/<int:id_proveedor>/eliminar/', eliminar_proveedor_dashboard, name='dashboard_eliminar_proveedor'),

    # Gestión de ventas directas desde modal en Dashboard y comprobante imprimible
    path('dashboard/venta/crear/', crear_venta_dashboard, name='dashboard_crear_venta'),
    path('dashboard/venta/<int:id_venta>/editar/', editar_venta_dashboard, name='dashboard_editar_venta'),
    path('dashboard/venta/<int:id_venta>/eliminar/', eliminar_venta_dashboard, name='dashboard_eliminar_venta'),
    path('dashboard/venta/<int:id_venta>/recibo/', recibo_venta_view, name='dashboard_recibo_venta'),

    # -------------------------------------------------------------------------
    # 4. GESTIÓN DE SESIONES Y AUTENTICACIÓN (Con redirección inteligente por rol)
    # -------------------------------------------------------------------------
    path('login/', CustomLoginView.as_view(), name='login_direct'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('registro/', registro_view, name='registro'),

    path('logout/', logout_view, name='logout_direct'),
    path('accounts/logout/', logout_view, name='logout'),

    # -------------------------------------------------------------------------
    # 5. RECUPERACIÓN DE CONTRASEÑA POR CORREO ELECTRÓNICO (SMTP)
    # -------------------------------------------------------------------------
    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='principal/password_reset_form.html',
             email_template_name='principal/password_reset_email.txt',
             html_email_template_name='principal/password_reset_email.html',
             subject_template_name='principal/password_reset_subject.txt'
         ),
         name='password_reset'),

    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='principal/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='principal/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='principal/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # -------------------------------------------------------------------------
    # 6. MÓDULO DE GESTIÓN CRUD GUÍA 4 (FBV Y CBV)
    # -------------------------------------------------------------------------
    path('gestion/', include('principal.urls')),

    # -------------------------------------------------------------------------
    # 7. RUTAS DE PREVISUALIZACIÓN DE ERRORES DE MARCA
    # -------------------------------------------------------------------------
    path('404/', error_404_view, name='error_404_preview'),
    path('500/', error_500_view, name='error_500_preview'),
    # Rutas del módulo de ventas por funciones
    path('dashboard/ventas/', lista_ventas, name='lista_ventas'),
    path('dashboard/ventas/nueva/', crear_venta, name='crear_venta'),
    path('dashboard/ventas/editar/<int:pk>/', editar_venta, name='editar_venta'),
    path('dashboard/ventas/eliminar/<int:pk>/', eliminar_venta, name='eliminar_venta'),
]

# Manejadores globales de error HTTP para producción
handler404 = 'principal.views.error_404_view'
handler500 = 'principal.views.error_500_view'
