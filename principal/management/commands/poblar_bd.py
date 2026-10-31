import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from principal.models import Producto, Categoria, Proveedor, Venta


class Command(BaseCommand):
    help = "Sincroniza y puebla la base de datos local con los datos oficiales del equipo (Usuarios, Categorías, Productos y Proveedores)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--exportar',
            action='store_true',
            help='Exporta el estado actual de la base de datos a fixtures/datos_iniciales.json'
        )

    def handle(self, *args, **options):
        fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', 'datos_iniciales.json')

        if options.get('exportar'):
            self.stdout.write(self.style.NOTICE("Exportando datos actuales a fixtures/datos_iniciales.json..."))
            os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
            try:
                # Usar call_command con encoding seguro
                with open(fixture_path, 'w', encoding='utf-8') as f:
                    call_command(
                        'dumpdata',
                        'auth.User',
                        'principal',
                        natural_foreign=True,
                        natural_primary=True,
                        exclude=['contenttypes', 'auth.Permission'],
                        indent=2,
                        stdout=f
                    )
                self.stdout.write(self.style.SUCCESS(f"¡Exportación exitosa! Archivo guardado en: {fixture_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al exportar fixture: {e}"))
            return

        self.stdout.write(self.style.NOTICE("1. Verificando y aplicando migraciones pendientes..."))
        call_command('migrate', interactive=False)

        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f"No se encontró el archivo de datos: {fixture_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"2. Cargando datos desde {os.path.relpath(fixture_path)}..."))
        try:
            call_command('loaddata', fixture_path)
            self.stdout.write(self.style.SUCCESS("[OK] Datos cargados correctamente."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al cargar fixture: {e}"))
            return

        # 3. Inicializar ventas de demostración para el Dashboard si no existen
        if Venta.objects.count() == 0:
            self._crear_ventas_demostracion()

        # Resumen de registros cargados
        User = get_user_model()
        num_users = User.objects.count()
        num_prods = Producto.objects.count()
        num_cats = Categoria.objects.count()
        num_provs = Proveedor.objects.count()
        num_ventas = Venta.objects.count()

        self.stdout.write(self.style.SUCCESS("\n======================================================="))
        self.stdout.write(self.style.SUCCESS("  BASE DE DATOS SINCRONIZADA CON EXITO"))
        self.stdout.write(self.style.SUCCESS("======================================================="))
        self.stdout.write(f"  - Usuarios y Roles: {num_users} cuentas listas (admin, guti, mario, etc.)")
        self.stdout.write(f"  - Categorias:       {num_cats} registradas")
        self.stdout.write(f"  - Productos:        {num_prods} en inventario")
        self.stdout.write(f"  - Proveedores:      {num_provs} activos")
        self.stdout.write(f"  - Ventas:           {num_ventas} registradas (Hoy, Mes, Año y General)")
        self.stdout.write(self.style.SUCCESS("=======================================================\n"))

    def _crear_ventas_demostracion(self):
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        cajero_user = User.objects.filter(username__in=['cajero', 'empleado_caja', 'guti']).first() or admin_user
        guti_user = User.objects.filter(username='guti').first() or admin_user

        now = timezone.now()
        ventas_data = [
            # Hoy (Día actual)
            {'cajero': guti_user, 'origen': 'WhatsApp', 'medio': 'Transferencia', 'subtotal': Decimal('52000.00'), 'descuento': Decimal('4000.00'), 'total_neto': Decimal('48000.00'), 'estado': 'Completada', 'fecha': now - timedelta(hours=2, minutes=15)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('32500.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('32500.00'), 'estado': 'Completada', 'fecha': now - timedelta(hours=3, minutes=40)},
            {'cajero': admin_user, 'origen': 'WhatsApp', 'medio': 'Nequi', 'subtotal': Decimal('89000.00'), 'descuento': Decimal('5000.00'), 'total_neto': Decimal('84000.00'), 'estado': 'Completada', 'fecha': now - timedelta(hours=5, minutes=10)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Daviplata', 'subtotal': Decimal('21200.00'), 'descuento': Decimal('1200.00'), 'total_neto': Decimal('20000.00'), 'estado': 'Completada', 'fecha': now - timedelta(hours=6, minutes=30)},
            # Este Mes (días anteriores)
            {'cajero': guti_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('46000.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('46000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=2, hours=4)},
            {'cajero': admin_user, 'origen': 'WhatsApp', 'medio': 'Nequi', 'subtotal': Decimal('73500.00'), 'descuento': Decimal('3500.00'), 'total_neto': Decimal('70000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=4, hours=2)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Tarjeta', 'subtotal': Decimal('58000.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('58000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=7, hours=5)},
            {'cajero': guti_user, 'origen': 'WhatsApp', 'medio': 'Transferencia', 'subtotal': Decimal('92000.00'), 'descuento': Decimal('6000.00'), 'total_neto': Decimal('86000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=10, hours=3)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('38400.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('38400.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=14, hours=1)},
            {'cajero': admin_user, 'origen': 'Tienda Física', 'medio': 'Nequi', 'subtotal': Decimal('64500.00'), 'descuento': Decimal('4500.00'), 'total_neto': Decimal('60000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=18, hours=4)},
            {'cajero': guti_user, 'origen': 'WhatsApp', 'medio': 'Daviplata', 'subtotal': Decimal('51000.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('51000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=22, hours=6)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('41500.00'), 'descuento': Decimal('1500.00'), 'total_neto': Decimal('40000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=26, hours=3)},
            # Este Año (meses anteriores)
            {'cajero': admin_user, 'origen': 'WhatsApp', 'medio': 'Transferencia', 'subtotal': Decimal('125000.00'), 'descuento': Decimal('10000.00'), 'total_neto': Decimal('115000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=38, hours=2)},
            {'cajero': guti_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('67000.00'), 'descuento': Decimal('2000.00'), 'total_neto': Decimal('65000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=50, hours=5)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Tarjeta', 'subtotal': Decimal('84000.00'), 'descuento': Decimal('4000.00'), 'total_neto': Decimal('80000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=65, hours=4)},
            {'cajero': guti_user, 'origen': 'WhatsApp', 'medio': 'Nequi', 'subtotal': Decimal('98000.00'), 'descuento': Decimal('8000.00'), 'total_neto': Decimal('90000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=80, hours=1)},
            {'cajero': admin_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('53500.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('53500.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=95, hours=3)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Daviplata', 'subtotal': Decimal('76000.00'), 'descuento': Decimal('6000.00'), 'total_neto': Decimal('70000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=110, hours=2)},
            {'cajero': guti_user, 'origen': 'WhatsApp', 'medio': 'Transferencia', 'subtotal': Decimal('110000.00'), 'descuento': Decimal('5000.00'), 'total_neto': Decimal('105000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=130, hours=5)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('49000.00'), 'descuento': Decimal('0.00'), 'total_neto': Decimal('49000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=150, hours=4)},
            {'cajero': admin_user, 'origen': 'WhatsApp', 'medio': 'Nequi', 'subtotal': Decimal('82000.00'), 'descuento': Decimal('4000.00'), 'total_neto': Decimal('78000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=170, hours=3)},
            {'cajero': cajero_user, 'origen': 'Tienda Física', 'medio': 'Efectivo', 'subtotal': Decimal('61000.00'), 'descuento': Decimal('1000.00'), 'total_neto': Decimal('60000.00'), 'estado': 'Completada', 'fecha': now - timedelta(days=190, hours=6)},
        ]
        for vd in ventas_data:
            Venta.objects.create(
                id_usuario_cajero=vd['cajero'],
                origen_venta=vd['origen'],
                medio_pago=vd['medio'],
                subtotal=vd['subtotal'],
                descuento=vd['descuento'],
                total_neto=vd['total_neto'],
                estado_venta=vd['estado'],
                fecha_venta=vd['fecha'],
            )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Creadas {len(ventas_data)} ventas de demostración para el Dashboard."))
