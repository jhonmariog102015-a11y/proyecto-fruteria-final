# ==============================================================================
# ENRUTADOR PRINCIPAL DEL PROYECTO (config/urls.py)
# Define el mapa de navegación y la correspondencia entre URLs y vistas de Django.
# ==============================================================================

from django.contrib import admin
# INICIO CAMBIOS GUÍA 4: autenticación POST y rutas del módulo CRUD.
from django.contrib.auth.views import LogoutView
from principal.forms import FormularioInicioSesion
from django.urls import include, path
# FIN CAMBIOS GUÍA 4: importaciones de autenticación y gestión.
from principal.views import (
    inicio,
    tienda_view,
    catalogo_frutas_view,
    dashboard_view,
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
    # Ruta raíz ('/') y alias ('/inicio/'): Carga la página de aterrizaje con carrusel
    path('', inicio, name='index'),
    path('inicio/', inicio, name='inicio'),

    # Tienda alternativa del proyecto formativo
    path('tienda/', tienda_view, name='tienda'),

    # Catálogo especializado de frutas con filtrado reactivo por categorías
    path('catalogo-frutas/', catalogo_frutas_view, name='catalogo_frutas'),

    # -------------------------------------------------------------------------
    # 3. PANEL DE CONTROL INTERNO (DASHBOARD)
    # -------------------------------------------------------------------------
    # Panel privado con métricas en tiempo real de inventario y usuarios
    path('dashboard/', dashboard_view, name='dashboard'),

    # -------------------------------------------------------------------------
    # 4. GESTIÓN DE SESIONES Y AUTENTICACIÓN
    # -------------------------------------------------------------------------
    # INICIO CAMBIOS GUÍA 4: login con formulario Bootstrap y logout seguro por POST.
    # Login oficial de Django usando la plantilla personalizada login.html
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='principal/login.html',
            authentication_form=FormularioInicioSesion,
        ),
        name='login',
    ),

    # Cierre de sesión seguro y redirección a la página principal
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('gestion/', include('principal.urls')),
    # FIN CAMBIOS GUÍA 4: rutas de autenticación y gestión.
]
