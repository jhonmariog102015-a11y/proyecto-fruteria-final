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
        self.user = User.objects.create_user(username='admin_prov', password='password123')
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
        self.user = User.objects.create_user(username='admin_csv', password='password123')
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



