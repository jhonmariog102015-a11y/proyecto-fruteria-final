# ==============================================================================
# ENRUTADOR DE GESTIÓN CRUD (principal/urls.py)
# Módulo de gestión de productos y categorías (FBV y CBV - Guía de Aprendizaje 4)
# ==============================================================================

from django.urls import path
from . import views

app_name = "principal"

urlpatterns = [
    path("productos/", views.producto_listar, name="producto_listar"),
    path("productos/crear/", views.producto_crear, name="producto_crear"),
    path("productos/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path(
        "productos/<int:pk>/eliminar/",
        views.producto_eliminar,
        name="producto_eliminar",
    ),
    path("categorias/", views.CategoriaListaView.as_view(), name="categoria_listar"),
    path(
        "categorias/crear/",
        views.CategoriaCrearView.as_view(),
        name="categoria_crear",
    ),
    path(
        "categorias/<int:pk>/editar/",
        views.CategoriaEditarView.as_view(),
        name="categoria_editar",
    ),
    path(
        "categorias/<int:pk>/eliminar/",
        views.CategoriaEliminarView.as_view(),
        name="categoria_eliminar",
    ),
]
