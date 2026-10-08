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
            'icono_emoji': '🍋',
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
            'icono_emoji': '🍊',
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

