from decimal import Decimal
from django.test import TestCase
from principal.models import Categoria, Producto, PerfilUsuario, Venta
from django.contrib.auth import authenticate


class ProductoMargenOfertaTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Frutas Frescas",
            descripcion="Frutas de temporada"
        )
        self.producto_normal = Producto.objects.create(
            nombre="Manzana Roja",
            categoria=self.categoria,
            costo_compra=Decimal('2000.00'),
            precio_venta_unitario=Decimal('3500.00'),
            en_oferta=False,
            stock_actual=50
        )
        self.producto_oferta = Producto.objects.create(
            nombre="Naranja Valencia",
            categoria=self.categoria,
            costo_compra=Decimal('1000.00'),
            precio_venta_unitario=Decimal('2000.00'),
            en_oferta=True,
            precio_oferta=Decimal('1500.00'),
            stock_actual=80
        )

    def test_precio_efectivo_sin_oferta(self):
        self.assertEqual(self.producto_normal.precio_efectivo, Decimal('3500.00'))
        self.assertEqual(self.producto_normal.precio, Decimal('3500.00'))

    def test_precio_efectivo_con_oferta(self):
        self.assertEqual(self.producto_oferta.precio_efectivo, Decimal('1500.00'))
        self.assertEqual(self.producto_oferta.precio, Decimal('1500.00'))

    def test_margen_ganancia_sin_oferta(self):
        # 3500 - 2000 = 1500
        self.assertEqual(self.producto_normal.margen_ganancia, Decimal('1500.00'))
        # Rentabilidad sobre costo: (1500 / 2000) * 100 = 75.0%
        self.assertEqual(self.producto_normal.porcentaje_margen, Decimal('75.0'))

    def test_margen_ganancia_con_oferta(self):
        # Con oferta activa: 1500 - 1000 = 500
        self.assertEqual(self.producto_oferta.margen_ganancia, Decimal('500.00'))
        # Rentabilidad sobre costo: (500 / 1000) * 100 = 50.0%
        self.assertEqual(self.producto_oferta.porcentaje_margen, Decimal('50.0'))

    def test_porcentaje_descuento(self):
        # (2000 - 1500) / 2000 * 100 = 25%
        self.assertAlmostEqual(self.producto_oferta.porcentaje_descuento, 25.0, places=1)
        self.assertEqual(self.producto_normal.porcentaje_descuento, 0.0)


from django.contrib.auth import get_user_model
from django.urls import reverse

class DashboardCrudTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='admin_test', password='password123', is_staff=True)
        self.client.login(username='admin_test', password='password123')
        self.categoria = Categoria.objects.create(nombre="Cítricos", descripcion="Frutas ácidas")

    def test_dashboard_view_acceso(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catálogo e Inventario en Tiempo Real")

    def test_crear_producto_dashboard(self):
        response = self.client.post(reverse('dashboard_crear_producto'), {
            'nombre': 'Limón Tahití',
            'categoria_id': self.categoria.id_categoria,
            'costo_compra': '1200',
            'precio_venta_unitario': '2400',
            'en_oferta': 'on',
            'precio_oferta': '2000',
            'stock_actual': '45',
            'stock_minimo': '10',
            'unidad_medida': 'kg',
            'estado': 'Disponible',
            'icono_emoji': '',
        })
        self.assertRedirects(response, reverse('dashboard'))
        prod = Producto.objects.get(nombre='Limón Tahití')
        self.assertEqual(prod.costo_compra, Decimal('1200'))
        self.assertEqual(prod.precio_venta_unitario, Decimal('2400'))
        self.assertTrue(prod.en_oferta)
        self.assertEqual(prod.precio_oferta, Decimal('2000'))
        self.assertEqual(prod.margen_ganancia, Decimal('800'))  # 2000 - 1200

    def test_editar_producto_dashboard(self):
        prod = Producto.objects.create(
            nombre='Mandarina',
            categoria=self.categoria,
            costo_compra=Decimal('1500'),
            precio_venta_unitario=Decimal('2500'),
            stock_actual=30
        )
        response = self.client.post(reverse('dashboard_editar_producto', args=[prod.id_producto]), {
            'nombre': 'Mandarina Criolla',
            'categoria_id': self.categoria.id_categoria,
            'costo_compra': '1600',
            'precio_venta_unitario': '2800',
            'stock_actual': '50',
            'stock_minimo': '5',
            'unidad_medida': 'kg',
            'estado': 'Disponible',
            'icono_emoji': '',
        })
        self.assertRedirects(response, reverse('dashboard'))
        prod.refresh_from_db()
        self.assertEqual(prod.nombre, 'Mandarina Criolla')
        self.assertEqual(prod.costo_compra, Decimal('1600'))
        self.assertEqual(prod.precio_venta_unitario, Decimal('2800'))

    def test_eliminar_producto_dashboard(self):
        prod = Producto.objects.create(
            nombre='Toronja',
            categoria=self.categoria,
            costo_compra=Decimal('1000'),
            precio_venta_unitario=Decimal('2000'),
            stock_actual=20
        )
        response = self.client.post(reverse('dashboard_eliminar_producto', args=[prod.id_producto]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Producto.objects.filter(id_producto=prod.id_producto).exists())

    def test_crear_categoria_dashboard(self):
        response = self.client.post(reverse('dashboard_crear_categoria'), {
            'nombre': 'Tubérculos',
            'descripcion': 'Papas y yucas'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Categoria.objects.filter(nombre='Tubérculos').exists())


from principal.models import Proveedor
from principal.forms import ProveedorForm


class ProveedorFormTestCase(TestCase):
    def test_proveedor_form_valido(self):
        data = {
            'razon_social': 'Finca Villa Diana',
            'nit_rut': '900456789-1',
            'contacto_nombre': 'Carlos Mendoza',
            'telefono': '3124567890',
            'email': 'carlos@villadiana.co',
            'calificacion_estrellas': '4.8',
            'estado': 'Activo'
        }
        form = ProveedorForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_proveedor_form_requiere_razon_y_nit(self):
        form = ProveedorForm(data={'calificacion_estrellas': '5.0'})
        self.assertFalse(form.is_valid())
        self.assertIn('razon_social', form.errors)
        self.assertIn('nit_rut', form.errors)

    def test_proveedor_form_calificacion_invalida(self):
        data = {
            'razon_social': 'Finca La Esperanza',
            'nit_rut': '900111222-3',
            'calificacion_estrellas': '6.5',
            'estado': 'Activo'
        }
        form = ProveedorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('calificacion_estrellas', form.errors)


class ProveedorDashboardCrudTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='admin_prov', password='password123', is_staff=True)
        self.client.login(username='admin_prov', password='password123')

    def test_crear_proveedor_dashboard(self):
        response = self.client.post(reverse('dashboard_crear_proveedor'), {
            'razon_social': 'Finca Santa Inés',
            'nit_rut': '800555444-2',
            'contacto_nombre': 'Mariana Gómez',
            'telefono': '3157894561',
            'email': 'santaines@frutales.co',
            'calificacion_estrellas': '4.9',
            'estado': 'Activo'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Proveedor.objects.filter(nit_rut='800555444-2').exists())
        prov = Proveedor.objects.get(nit_rut='800555444-2')
        self.assertEqual(prov.razon_social, 'Finca Santa Inés')

    def test_editar_proveedor_dashboard(self):
        prov = Proveedor.objects.create(
            razon_social='Finca El Paraíso',
            nit_rut='900333222-1',
            telefono='3101112233',
            calificacion_estrellas=Decimal('4.5'),
            estado='Activo'
        )
        response = self.client.post(reverse('dashboard_editar_proveedor', args=[prov.id_proveedor]), {
            'razon_social': 'Finca El Paraíso Orgánico',
            'nit_rut': '900333222-1',
            'contacto_nombre': 'Pedro Vargas',
            'telefono': '3109998877',
            'email': 'pedro@elparaiso.co',
            'calificacion_estrellas': '5.0',
            'estado': 'Activo'
        })
        self.assertRedirects(response, reverse('dashboard'))
        prov.refresh_from_db()
        self.assertEqual(prov.razon_social, 'Finca El Paraíso Orgánico')
        self.assertEqual(prov.calificacion_estrellas, Decimal('5.0'))
        self.assertEqual(prov.telefono, '3109998877')

    def test_eliminar_proveedor_dashboard(self):
        prov = Proveedor.objects.create(
            razon_social='Distribuidora Andina',
            nit_rut='900777888-9',
            calificacion_estrellas=Decimal('3.8'),
            estado='Inactivo'
        )
        response = self.client.post(reverse('dashboard_eliminar_proveedor', args=[prov.id_proveedor]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Proveedor.objects.filter(id_proveedor=prov.id_proveedor).exists())


class ExportarInventarioCsvTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='admin_csv', password='password123', is_staff=True)
        self.client.login(username='admin_csv', password='password123')
        self.cat = Categoria.objects.create(nombre="Frutas Exóticas")
        self.prod = Producto.objects.create(
            nombre="Maracuyá Amarillo",
            categoria=self.cat,
            costo_compra=Decimal('2500.00'),
            precio_venta_unitario=Decimal('4500.00'),
            en_oferta=True,
            precio_oferta=Decimal('4000.00'),
            stock_actual=60,
            stock_minimo=15,
            unidad_medida='kg',
            estado='Disponible',
            origen='Boyacá'
        )

    def test_exportar_inventario_csv_respuesta(self):
        response = self.client.get(reverse('dashboard_exportar_inventario_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('charset=utf-8-sig', response['Content-Type'])
        self.assertIn('inventario_el_paso_', response['Content-Disposition'])

        content = response.content.decode('utf-8-sig')
        self.assertIn('ID Producto;Nombre del Producto;Categoría;', content)
        self.assertIn('Maracuyá Amarillo', content)
        self.assertIn('Boyacá', content)


class ErrorPagesViewsTestCase(TestCase):
    def test_error_404_preview(self):
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Error 404', status_code=404)
        self.assertContains(response, 'Esta fruta se cayó del canasto', status_code=404)

    def test_error_500_preview(self):
        response = self.client.get('/500/')
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, 'Error 500', status_code=500)
        self.assertContains(response, 'Interrupción en la cosecha', status_code=500)


class RegistroViewTestCase(TestCase):
    def test_registro_view_get(self):
        response = self.client.get('/registro/')
        self.assertEqual(response.status_code, 200)

    def test_registro_view_post_exitoso(self):
        response = self.client.post('/registro/', {
            'username': 'nuevo_cliente',
            'email': 'nuevo@example.com',
            'telefono': '3109998877',
            'password': 'PasswordSeguro123!',
            'confirm_password': 'PasswordSeguro123!',
            'terms': 'on'
        })
        self.assertRedirects(response, reverse('index'))
        User = get_user_model()
        self.assertTrue(User.objects.filter(username='nuevo_cliente').exists())
        nuevo = User.objects.get(username='nuevo_cliente')
        self.assertTrue(hasattr(nuevo, 'perfil'))
        self.assertEqual(nuevo.perfil.rol, 'cliente')
        self.assertFalse(nuevo.is_staff)
        self.assertFalse(nuevo.is_superuser)

    def test_registro_view_previene_escalamiento_privilegios(self):
        # Un atacante intenta forzar rol admin por POST
        response = self.client.post('/registro/', {
            'username': 'hacker_user',
            'email': 'hacker@example.com',
            'telefono': '3000000000',
            'rol': 'admin',
            'password': 'PasswordSeguro123!',
            'confirm_password': 'PasswordSeguro123!',
            'terms': 'on'
        })
        self.assertRedirects(response, reverse('index'))
        User = get_user_model()
        user = User.objects.get(username='hacker_user')
        # Debe ser forzado a cliente normal sin permisos de staff ni superuser
        self.assertEqual(user.perfil.rol, 'cliente')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registro_view_post_password_mismatch(self):
        response = self.client.post('/registro/', {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password': 'PasswordSeguro123!',
            'confirm_password': 'DifferentPassword123!',
            'terms': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las contraseñas ingresadas no coinciden')
        # Verifica persistencia del dato
        self.assertContains(response, 'value="mismatch_user"')

    def test_registro_view_post_terminos_obligatorios(self):
        response = self.client.post('/registro/', {
            'username': 'noterms_user',
            'email': 'noterms@example.com',
            'password': 'PasswordSeguro123!',
            'confirm_password': 'PasswordSeguro123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Debes aceptar los términos de servicio')

    def test_registro_view_post_email_invalido(self):
        response = self.client.post('/registro/', {
            'username': 'bademail_user',
            'email': 'correo_no_valido',
            'password': 'PasswordSeguro123!',
            'confirm_password': 'PasswordSeguro123!',
            'terms': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'formato válido')

    def test_creacion_usuario_crea_perfil_automaticamente(self):
        User = get_user_model()
        u = User.objects.create_user(username='auto_perfil_user', email='auto@fruteria.com', password='Password123!')
        self.assertTrue(hasattr(u, 'perfil'))
        self.assertEqual(u.perfil.rol, 'cliente')
        self.assertEqual(u.perfil.estado, 'activo')

    def test_autenticacion_por_email_y_username(self):
        User = get_user_model()
        User.objects.create_user(username='test_auth_user', email='test_auth@fruteria.com', password='PasswordSeguro123!')
        
        # Probar autenticación por nombre de usuario
        auth_by_user = authenticate(username='test_auth_user', password='PasswordSeguro123!')
        self.assertIsNotNone(auth_by_user)
        self.assertEqual(auth_by_user.username, 'test_auth_user')

        # Probar autenticación por correo electrónico
        auth_by_email = authenticate(username='test_auth@fruteria.com', password='PasswordSeguro123!')
        self.assertIsNotNone(auth_by_email)
        self.assertEqual(auth_by_email.username, 'test_auth_user')


# ==============================================================================
# PRUEBAS GUIA 4: FORMULARIOS, OPERACIONES CRUD Y SEGURIDAD (JUAN CARLOS)
# ==============================================================================

from .forms import CategoriaForm, ProductoForm


class FormulariosCrudTests(TestCase):
    def test_categoria_rechaza_nombre_vacio(self):
        formulario = CategoriaForm(data={"nombre": "   ", "descripcion": ""})
        self.assertFalse(formulario.is_valid())
        self.assertIn("nombre", formulario.errors)

    def test_producto_rechaza_precio_negativo(self):
        categoria = Categoria.objects.create(nombre="Frutas")
        formulario = ProductoForm(
            data={
                "categoria": categoria.pk,
                "nombre": "Manzana",
                "icono_emoji": "",
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
            username="gestor", password="Clave-segura-123", is_staff=True
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
                "icono_emoji": "",
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
                "icono_emoji": "",
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
            username="gestor_cat", password="Clave-segura-123", is_staff=True
        )
        self.client.force_login(usuario)
        self.categoria = Categoria.objects.create(nombre="Tropicales")

    def test_vista_lista_y_formulario_categoria(self):
        respuesta_lista = self.client.get(reverse("principal:categoria_listar"))
        respuesta_formulario = self.client.get(reverse("principal:categoria_crear"))

        self.assertEqual(respuesta_lista.status_code, 200)
        self.assertContains(respuesta_lista, "Tropicales")
        self.assertEqual(respuesta_formulario.status_code, 200)
        self.assertContains(respuesta_formulario, "Crear categoria")

    def test_creacion_y_actualizacion_categoria(self):
        respuesta_creacion = self.client.post(
            reverse("principal:categoria_crear"),
            {"nombre": "Citricos", "descripcion": "Frutas citricas"},
        )
        self.assertRedirects(
            respuesta_creacion, reverse("principal:categoria_listar")
        )
        categoria = Categoria.objects.get(nombre="Citricos")

        respuesta_edicion = self.client.post(
            reverse("principal:categoria_editar", args=[categoria.pk]),
            {"nombre": "Citricos frescos", "descripcion": "Seleccion citrica"},
        )
        self.assertRedirects(respuesta_edicion, reverse("principal:categoria_listar"))
        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre, "Citricos frescos")

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

    def test_cliente_publico_bloqueado_en_dashboard_y_crud(self):
        cliente = get_user_model().objects.create_user(
            username="comprador_publico", password="Clave-segura-123", is_staff=False
        )
        self.client.force_login(cliente)
        for ruta in [reverse("dashboard"), reverse("principal:producto_listar"), reverse("lista_ventas")]:
            res = self.client.get(ruta)
            self.assertRedirects(res, reverse("index"))


class UsuariosRolesDashboardTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        # 1. Super Admin
        self.superadmin = User.objects.create_superuser(username='super_boss', password='password123', email='super@fruteria.com')
        # 2. Bodeguero
        self.bodeguero = User.objects.create_user(username='carlos_bodega', password='password123', email='bodega@fruteria.com', is_staff=True)
        PerfilUsuario.objects.update_or_create(usuario=self.bodeguero, defaults={'rol': 'bodeguero', 'estado': 'activo', 'telefono': '3111111111'})
        # 3. Cajero
        self.cajero = User.objects.create_user(username='ana_caja', password='password123', email='caja@fruteria.com', is_staff=True)
        PerfilUsuario.objects.update_or_create(usuario=self.cajero, defaults={'rol': 'cajero', 'estado': 'activo', 'telefono': '3222222222'})
        # 4. Usuario Inactivo (no debe aparecer en activos)
        self.inactivo = User.objects.create_user(username='inactivo_user', password='password123', email='inactivo@fruteria.com', is_active=False)
        PerfilUsuario.objects.update_or_create(usuario=self.inactivo, defaults={'rol': 'cajero', 'estado': 'inactivo'})

        self.client.login(username='super_boss', password='password123')

    def test_dashboard_muestra_registros_activos_ordenados_por_roles(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Verificar contexto de roles y registros activos
        perfiles = list(response.context['perfiles_usuarios'])
        # Debe haber exactamente 3 perfiles activos (super_boss, carlos_bodega, ana_caja)
        self.assertEqual(len(perfiles), 3)

        # Jerarquia estricta requerida: 1. Super Admin, 2. Bodeguero, 3. Cajero
        self.assertEqual(perfiles[0].usuario.username, 'super_boss')
        self.assertTrue(perfiles[0].usuario.is_superuser or perfiles[0].rol == 'admin')

        self.assertEqual(perfiles[1].usuario.username, 'carlos_bodega')
        self.assertEqual(perfiles[1].rol, 'bodeguero')

        self.assertEqual(perfiles[2].usuario.username, 'ana_caja')
        self.assertEqual(perfiles[2].rol, 'cajero')

        # Verificar metricas
        self.assertEqual(response.context['total_activos'], 3)
        self.assertEqual(response.context['total_superadmins'], 1)
        self.assertEqual(response.context['total_bodegueros'], 1)
        self.assertEqual(response.context['total_cajeros'], 1)

        # Verificar que el usuario inactivo NO aparece
        nombres = [p.usuario.username for p in perfiles]
        self.assertNotIn('inactivo_user', nombres)

    def test_crear_usuario_dashboard_exitoso(self):
        User = get_user_model()
        response = self.client.post(reverse('dashboard_crear_usuario'), {
            'username': 'pedro_bodeguero',
            'first_name': 'Pedro',
            'last_name': 'Ramirez',
            'email': 'pedro@fruteria.com',
            'telefono': '3009998877',
            'rol': 'bodeguero',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertRedirects(response, '/dashboard/#usuarios')
        user = User.objects.get(username='pedro_bodeguero')
        self.assertEqual(user.first_name, 'Pedro')
        self.assertEqual(user.email, 'pedro@fruteria.com')
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.perfil.rol, 'bodeguero')
        self.assertEqual(user.perfil.telefono, '3009998877')
        self.assertEqual(user.perfil.estado, 'activo')

    def test_crear_usuario_dashboard_validaciones_duplicado_y_contrasena(self):
        User = get_user_model()
        # Contrasenas no coinciden
        response = self.client.post(reverse('dashboard_crear_usuario'), {
            'username': 'nuevo_user',
            'email': 'nuevo@fruteria.com',
            'rol': 'cajero',
            'password': 'pass1',
            'confirm_password': 'pass2',
        })
        self.assertFalse(User.objects.filter(username='nuevo_user').exists())

        # Username duplicado
        response = self.client.post(reverse('dashboard_crear_usuario'), {
            'username': 'ana_caja',
            'email': 'diferente@fruteria.com',
            'rol': 'cajero',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(User.objects.filter(username='ana_caja').count(), 1)

    def test_editar_usuario_dashboard_exitoso(self):
        response = self.client.post(reverse('dashboard_editar_usuario', args=[self.cajero.pk]), {
            'username': 'ana_cajera_senior',
            'first_name': 'Ana',
            'last_name': 'Lopez',
            'email': 'ana_senior@fruteria.com',
            'telefono': '3555555555',
            'rol': 'cajero',
            'estado': 'activo',
            'nueva_password': '',
        })
        self.assertRedirects(response, '/dashboard/#usuarios')
        self.cajero.refresh_from_db()
        self.assertEqual(self.cajero.username, 'ana_cajera_senior')
        self.assertEqual(self.cajero.email, 'ana_senior@fruteria.com')
        self.assertEqual(self.cajero.first_name, 'Ana')
        self.assertEqual(self.cajero.perfil.telefono, '3555555555')

    def test_editar_usuario_dashboard_seguridad_cuenta_propia(self):
        # Intentar desactivarse a si mismo
        response = self.client.post(reverse('dashboard_editar_usuario', args=[self.superadmin.pk]), {
            'username': 'super_boss',
            'email': 'super@fruteria.com',
            'rol': 'admin',
            'estado': 'inactivo',
        })
        self.superadmin.refresh_from_db()
        self.assertTrue(self.superadmin.is_active)
        self.assertEqual(self.superadmin.perfil.estado, 'activo')

    def test_eliminar_usuario_dashboard_exitoso_post(self):
        User = get_user_model()
        cajero_id = self.cajero.pk
        response = self.client.post(reverse('dashboard_eliminar_usuario', args=[cajero_id]))
        self.assertRedirects(response, '/dashboard/#usuarios')
        self.assertFalse(User.objects.filter(pk=cajero_id).exists())

    def test_eliminar_usuario_dashboard_previene_auto_eliminacion(self):
        User = get_user_model()
        super_id = self.superadmin.pk
        response = self.client.post(reverse('dashboard_eliminar_usuario', args=[super_id]))
        self.assertRedirects(response, '/dashboard/#usuarios')
        self.assertTrue(User.objects.filter(pk=super_id).exists())

    def test_no_administrador_no_puede_crear_usuario(self):
        User = get_user_model()
        # Iniciar sesion como Cajero (no administrador)
        self.client.login(username='ana_caja', password='password123')
        response = self.client.post(reverse('dashboard_crear_usuario'), {
            'username': 'intento_cajero',
            'email': 'hacker@fruteria.com',
            'rol': 'admin',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertRedirects(response, '/dashboard/#usuarios')
        self.assertFalse(User.objects.filter(username='intento_cajero').exists())

    def test_no_administrador_no_puede_editar_usuario(self):
        # Iniciar sesion como Bodeguero (no administrador)
        self.client.login(username='carlos_bodega', password='password123')
        response = self.client.post(reverse('dashboard_editar_usuario', args=[self.cajero.pk]), {
            'username': 'ana_modificada_ilegal',
            'email': 'ilegal@fruteria.com',
            'rol': 'admin',
            'estado': 'activo',
        })
        self.assertRedirects(response, '/dashboard/#usuarios')
        self.cajero.refresh_from_db()
        self.assertEqual(self.cajero.username, 'ana_caja')
        self.assertNotEqual(self.cajero.username, 'ana_modificada_ilegal')

    def test_no_administrador_no_puede_eliminar_usuario(self):
        User = get_user_model()
        # Iniciar sesion como Cajero (no administrador)
        self.client.login(username='ana_caja', password='password123')
        response = self.client.post(reverse('dashboard_eliminar_usuario', args=[self.bodeguero.pk]))
        self.assertRedirects(response, '/dashboard/#usuarios')
        self.assertTrue(User.objects.filter(pk=self.bodeguero.pk).exists())

    def test_no_administrador_ve_interfaz_solo_lectura(self):
        self.client.login(username='ana_caja', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['es_admin'])
        self.assertContains(response, 'Modo de solo lectura')
        self.assertContains(response, 'Solo Administrador')
        self.assertNotContains(response, 'onclick="abrirModalNuevoUsuario()"')

    def test_boton_iniciar_sesion_visible_para_anonimos(self):
        """Verifica que el boton Iniciar Sesion sea visible y destacado para usuarios anonimos."""
        self.client.logout()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-nav-login')
        self.assertContains(response, 'Iniciar Sesión')
        self.assertNotContains(response, 'btn-nav-admin')

    def test_boton_panel_admin_visible_para_autenticados(self):
        """Verifica que para usuarios autenticados se muestre el boton directo Panel Admin."""
        self.client.login(username='super_boss', password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'btn-nav-admin')
        self.assertContains(response, 'Panel Admin')
        self.assertNotContains(response, 'btn-nav-login')

    def test_django_admin_solo_accesible_para_superadmin(self):
        """Verifica que /admin/ rechace staff no-superadmin y permita acceso a superadmin."""
        # 1. Staff normal sin superusuario
        self.client.login(username='carlos_bodega', password='password123')
        # Asegurar is_staff=True pero is_superuser=False
        self.bodeguero.is_staff = True
        self.bodeguero.is_superuser = False
        self.bodeguero.save()
        res_staff = self.client.get('/admin/')
        # Debe redirigir al login del admin porque no tiene permiso
        self.assertEqual(res_staff.status_code, 302)

        # 2. Superusuario
        self.client.login(username='super_boss', password='password123')
        res_super = self.client.get('/admin/')
        self.assertEqual(res_super.status_code, 200)

    def test_dashboard_oculta_django_admin_para_no_superadmin(self):
        """Verifica que el dashboard oculte enlaces a Django Admin si el usuario no es superadmin."""
        self.client.login(username='ana_caja', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Django Admin ↗')
        self.assertNotContains(response, 'href="/admin/principal/producto/"')
        self.assertNotContains(response, 'href="/admin/principal/proveedor/"')


class VentasTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='cajero_test',
            email='cajero@fruteria.com',
            password='password123',
            is_staff=True
        )
        self.venta = Venta.objects.create(
            id_usuario_cajero=self.user,
            origen_venta='Tienda Física',
            subtotal=Decimal('15000.00'),
            descuento=Decimal('1000.00'),
            total_neto=Decimal('14000.00'),
            medio_pago='Efectivo',
            estado_venta='Completada'
        )

    def test_modelo_venta_str(self):
        self.assertIn(str(self.venta.id_venta), str(self.venta))
        self.assertIn('14000.00', str(self.venta))

    def test_lista_ventas_requiere_login(self):
        response = self.client.get(reverse('lista_ventas'))
        self.assertEqual(response.status_code, 302)

    def test_lista_ventas_autenticado(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.get(reverse('lista_ventas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestión de Ventas')
        self.assertContains(response, '14000')

    def test_crear_venta_post(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.post(reverse('crear_venta'), {
            'origen_venta': 'Domicilio / WhatsApp',
            'subtotal': '25000',
            'descuento': '2000',
            'total_neto': '23000',
            'medio_pago': 'Nequi',
            'estado_venta': 'Completada'
        })
        self.assertRedirects(response, reverse('lista_ventas'))
        self.assertTrue(Venta.objects.filter(medio_pago='Nequi', total_neto=Decimal('23000.00')).exists())

    def test_editar_venta_post(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.post(reverse('editar_venta', args=[self.venta.pk]), {
            'origen_venta': 'Tienda Física',
            'subtotal': '15000',
            'descuento': '3000',
            'total_neto': '12000',
            'medio_pago': 'Daviplata',
            'estado_venta': 'Completada'
        })
        self.assertRedirects(response, reverse('lista_ventas'))
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.medio_pago, 'Daviplata')
        self.assertEqual(self.venta.total_neto, Decimal('12000.00'))

    def test_eliminar_venta_post(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.post(reverse('eliminar_venta', args=[self.venta.pk]))
        self.assertRedirects(response, reverse('lista_ventas'))
        self.assertFalse(Venta.objects.filter(pk=self.venta.pk).exists())

    def test_dashboard_muestra_ventas(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestión de Ventas')
        self.assertContains(response, 'seccion-ventas')
        self.assertContains(response, 'modalNuevaVenta')
        self.assertContains(response, 'modalEditarVenta')
        self.assertContains(response, 'modalEliminarVenta')
        self.assertContains(response, 'abrirModalNuevaVenta')

    def test_crear_venta_dashboard(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.post(reverse('dashboard_crear_venta'), {
            'origen_venta': 'Tienda Virtual',
            'subtotal': '35000',
            'descuento': '5000',
            'total_neto': '30000',
            'medio_pago': 'Transferencia Bancaria',
            'estado_venta': 'Completada'
        })
        self.assertRedirects(response, '/dashboard/#ventas')
        self.assertTrue(Venta.objects.filter(origen_venta='Tienda Virtual', total_neto=Decimal('30000.00')).exists())

    def test_editar_venta_dashboard(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.post(reverse('dashboard_editar_venta', args=[self.venta.pk]), {
            'origen_venta': 'Venta Mayorista',
            'subtotal': '50000',
            'descuento': '10000',
            'total_neto': '40000',
            'medio_pago': 'Nequi',
            'estado_venta': 'Completada'
        })
        self.assertRedirects(response, '/dashboard/#ventas')
        self.venta.refresh_from_db()
        self.assertEqual(self.venta.origen_venta, 'Venta Mayorista')
        self.assertEqual(self.venta.total_neto, Decimal('40000.00'))

    def test_eliminar_venta_dashboard(self):
        self.client.login(username='cajero_test', password='password123')
        response = self.client.post(reverse('dashboard_eliminar_venta', args=[self.venta.pk]))
        self.assertRedirects(response, '/dashboard/#ventas')
        self.assertFalse(Venta.objects.filter(pk=self.venta.pk).exists())








