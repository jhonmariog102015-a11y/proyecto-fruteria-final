# INICIO CAMBIOS GUÍA 4: pruebas de formularios, operaciones CRUD y seguridad.
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


class FormulariosCrudTests(TestCase):
    def test_categoria_rechaza_nombre_vacio(self):
        formulario = CategoriaForm({"nombre": "   ", "descripcion": ""})

        self.assertFalse(formulario.is_valid())
        self.assertIn("nombre", formulario.errors)

    def test_producto_rechaza_precio_negativo(self):
        categoria = Categoria.objects.create(nombre="Frutas")
        formulario = ProductoForm(
            {
                "categoria": categoria.pk,
                "nombre": "Manzana",
                "icono_emoji": "🍎",
                "imagen_url": "",
                "origen": "Finca local",
                "unidad_medida": "kg",
                "brix_minimo": "0",
                "stock_actual": "1",
                "stock_minimo": "0",
                "precio_venta_unitario": "-1",
                "estado": "Disponible",
            }
        )

        self.assertFalse(formulario.is_valid())
        self.assertIn("precio_venta_unitario", formulario.errors)


class CrudProductoFbvTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username="gestor", password="Clave-segura-123"
        )
        self.client.force_login(usuario)
        self.categoria = Categoria.objects.create(nombre="Frutas")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Manzana",
            precio_venta_unitario=Decimal("2500.00"),
        )

    def test_listado_y_edicion_producto(self):
        respuesta_lista = self.client.get(reverse("principal:producto_listar"))
        respuesta_edicion = self.client.get(
            reverse("principal:producto_editar", args=[self.producto.pk])
        )

        self.assertEqual(respuesta_lista.status_code, 200)
        self.assertContains(respuesta_lista, "Manzana")
        self.assertEqual(respuesta_edicion.status_code, 200)

    def test_creacion_producto(self):
        respuesta = self.client.post(
            reverse("principal:producto_crear"),
            {
                "categoria": self.categoria.pk,
                "nombre": "Pera",
                "icono_emoji": "🍐",
                "imagen_url": "",
                "origen": "Finca local",
                "unidad_medida": "kg",
                "brix_minimo": "0",
                "stock_actual": "1",
                "stock_minimo": "0",
                "precio_venta_unitario": "3000",
                "estado": "Disponible",
            },
        )

        self.assertRedirects(respuesta, reverse("principal:producto_listar"))
        self.assertTrue(Producto.objects.filter(nombre="Pera").exists())

    def test_actualizacion_producto(self):
        respuesta = self.client.post(
            reverse("principal:producto_editar", args=[self.producto.pk]),
            {
                "categoria": self.categoria.pk,
                "nombre": "Manzana roja",
                "icono_emoji": "🍎",
                "imagen_url": "",
                "origen": "Finca local",
                "unidad_medida": "kg",
                "brix_minimo": "0",
                "stock_actual": "1",
                "stock_minimo": "0",
                "precio_venta_unitario": "2500",
                "estado": "Disponible",
            },
        )

        self.assertRedirects(respuesta, reverse("principal:producto_listar"))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Manzana roja")

    def test_get_eliminar_solo_confirma_y_post_elimina(self):
        url = reverse("principal:producto_eliminar", args=[self.producto.pk])

        respuesta_get = self.client.get(url)
        self.assertEqual(respuesta_get.status_code, 200)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

        respuesta_post = self.client.post(url)
        self.assertRedirects(respuesta_post, reverse("principal:producto_listar"))
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())


class CrudCategoriaCbvTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username="gestor", password="Clave-segura-123"
        )
        self.client.force_login(usuario)
        self.categoria = Categoria.objects.create(nombre="Tropicales")

    def test_vista_lista_y_formulario_categoria(self):
        respuesta_lista = self.client.get(reverse("principal:categoria_listar"))
        respuesta_formulario = self.client.get(reverse("principal:categoria_crear"))

        self.assertEqual(respuesta_lista.status_code, 200)
        self.assertContains(respuesta_lista, "Tropicales")
        self.assertEqual(respuesta_formulario.status_code, 200)
        self.assertContains(respuesta_formulario, "Crear categoría")

    def test_creacion_y_actualizacion_categoria(self):
        respuesta_creacion = self.client.post(
            reverse("principal:categoria_crear"),
            {"nombre": "Cítricos", "descripcion": "Frutas cítricas"},
        )
        self.assertRedirects(
            respuesta_creacion, reverse("principal:categoria_listar")
        )
        categoria = Categoria.objects.get(nombre="Cítricos")

        respuesta_edicion = self.client.post(
            reverse("principal:categoria_editar", args=[categoria.pk]),
            {"nombre": "Cítricos frescos", "descripcion": "Selección cítrica"},
        )
        self.assertRedirects(respuesta_edicion, reverse("principal:categoria_listar"))
        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre, "Cítricos frescos")

    def test_eliminacion_categoria_requiere_post(self):
        url = reverse("principal:categoria_eliminar", args=[self.categoria.pk])

        respuesta_get = self.client.get(url)
        self.assertEqual(respuesta_get.status_code, 200)
        self.assertTrue(Categoria.objects.filter(pk=self.categoria.pk).exists())

        respuesta_post = self.client.post(url)
        self.assertRedirects(respuesta_post, reverse("principal:categoria_listar"))
        self.assertFalse(Categoria.objects.filter(pk=self.categoria.pk).exists())


class SeguridadCrudTests(TestCase):
    def test_listados_requieren_autenticacion(self):
        rutas = [
            reverse("principal:producto_listar"),
            reverse("principal:categoria_listar"),
        ]

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn("/accounts/login/", respuesta.url)

    def test_logout_no_acepta_get(self):
        respuesta = self.client.get(reverse("logout"))

        self.assertEqual(respuesta.status_code, 405)

    def test_logout_por_post_cierra_sesion(self):
        usuario = get_user_model().objects.create_user(
            username="salida", password="Clave-segura-123"
        )
        self.client.force_login(usuario)

        respuesta = self.client.post(reverse("logout"))

        self.assertRedirects(respuesta, reverse("index"))
        self.assertNotIn("_auth_user_id", self.client.session)
# FIN CAMBIOS GUÍA 4
