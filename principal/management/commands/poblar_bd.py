import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from principal.models import Producto, Categoria, Proveedor


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

        # Resumen de registros cargados
        User = get_user_model()
        num_users = User.objects.count()
        num_prods = Producto.objects.count()
        num_cats = Categoria.objects.count()
        num_provs = Proveedor.objects.count()

        self.stdout.write(self.style.SUCCESS("\n======================================================="))
        self.stdout.write(self.style.SUCCESS("  BASE DE DATOS SINCRONIZADA CON EXITO"))
        self.stdout.write(self.style.SUCCESS("======================================================="))
        self.stdout.write(f"  - Usuarios y Roles: {num_users} cuentas listas (admin, guti, mario, etc.)")
        self.stdout.write(f"  - Categorias:       {num_cats} registradas")
        self.stdout.write(f"  - Productos:        {num_prods} en inventario")
        self.stdout.write(f"  - Proveedores:      {num_provs} activos")
        self.stdout.write(self.style.SUCCESS("=======================================================\n"))
