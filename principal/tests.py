from decimal import Decimal
from django.test import TestCase
from principal.models import Categoria, Producto


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
        self.user = User.objects.create_user(username='admin_test', password='password123')
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


from principal.models import PerfilUsuario

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

        # Jerarquía estricta requerida: 1. Super Admin, 2. Bodeguero, 3. Cajero
        self.assertEqual(perfiles[0].usuario.username, 'super_boss')
        self.assertTrue(perfiles[0].usuario.is_superuser or perfiles[0].rol == 'admin')

        self.assertEqual(perfiles[1].usuario.username, 'carlos_bodega')
        self.assertEqual(perfiles[1].rol, 'bodeguero')

        self.assertEqual(perfiles[2].usuario.username, 'ana_caja')
        self.assertEqual(perfiles[2].rol, 'cajero')

        # Verificar métricas
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
            'last_name': 'Ramírez',
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
        # Contraseñas no coinciden
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
            'last_name': 'López',
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
        # Intentar desactivarse a sí mismo
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
        # Iniciar sesión como Cajero (no administrador)
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
        # Iniciar sesión como Bodeguero (no administrador)
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
        # Iniciar sesión como Cajero (no administrador)
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



