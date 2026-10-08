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
