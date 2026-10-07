from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from principal.models import Producto, Categoria


class Command(BaseCommand):
    help = "Puebla la base de datos con categorias, proveedores, productos iniciales y superusuario admin"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[INFO] Iniciando carga de datos iniciales para El Paso Fruteria..."))

        # 1. Cargar el fixture JSON con las 26 entidades
        try:
            call_command("loaddata", "productos_iniciales")
            total_prods = Producto.objects.count()
            total_cats = Categoria.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f"[OK] Datos cargados correctamente: {total_prods} productos y {total_cats} categorias.")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] Error al cargar productos_iniciales: {e}"))

        # 2. Crear superusuario admin si no existe
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@elpasofruteria.com", "admin123")
            self.stdout.write(self.style.SUCCESS("[OK] Superusuario creado: admin / admin123"))
        else:
            self.stdout.write(self.style.WARNING("[INFO] El usuario 'admin' ya existia en la base de datos."))

        self.stdout.write(self.style.SUCCESS("[LISTO] Base de datos lista. Ya puedes ver el carrusel, catalogo y panel."))
