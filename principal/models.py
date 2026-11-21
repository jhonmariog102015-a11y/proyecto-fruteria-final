# ==============================================================================
# MODELO ENTIDAD-RELACIÓN DEL PROYECTO (principal/models.py)
# Define la estructura de base de datos relacional para "Al Paso Frutería"
# Basado en la guía de diseño de datos SENA ADSO (Ficha 3321349).
# ==============================================================================

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ==============================================================================
# 1. ENTIDAD CATEGORIA
# Clasificación de los productos (Frutas, Cítricos, Tropicales, Hortalizas, etc.)
# ==============================================================================
class Categoria(models.Model):
    """
    Representa las categorías taxonómicas del inventario.
    Permite agrupar productos para filtrado rápido y reportes comerciales.
    """
    id_categoria = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=60, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        db_table = "categorias"  # Mapeo directo a la tabla SQL

    def __str__(self):
        return self.nombre


# ==============================================================================
# 2. ENTIDAD PROVEEDOR
# Fincas aliadas y distribuidores mayoristas de la región de Boyacá y el país.
# ==============================================================================
class Proveedor(models.Model):
    """
    Registra los datos fiscales y de contacto de los productores del campo.
    Incluye trazabilidad de calidad mediante calificación en estrellas.
    """
    id_proveedor = models.BigAutoField(primary_key=True)
    razon_social = models.CharField(max_length=150, verbose_name="Razón Social")
    nit_rut = models.CharField(max_length=30, unique=True, verbose_name="NIT / RUT")
    contacto_nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre de Contacto")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Correo Electrónico")
    calificacion_estrellas = models.DecimalField(
        max_digits=2, decimal_places=1, default=5.0, verbose_name="Calificación (Estrellas)"
    )
    estado = models.CharField(max_length=20, default="Activo", verbose_name="Estado")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        db_table = "proveedores"

    def __str__(self):
        return f"{self.razon_social} ({self.nit_rut})"


# ==============================================================================
# 3. ENTIDAD PRODUCTO
# Catálogo de frutas y verduras comercializadas en tienda física y virtual.
# ==============================================================================
class Producto(models.Model):
    """
    Entidad nuclear del sistema de frutería.
    Almacena especificaciones técnicas del producto agrícola:
    - Grados Brix (°Brix): Indicador de dulzor natural y madurez.
    - Origen: Identificación de la finca y frescura de la cosecha.
    - Stocks: Control de existencias y alertas de reposición.
    """
    ESTADO_CHOICES = [
        ("Disponible", "Disponible"),
        ("Agotado", "Agotado"),
        ("En Maduracion", "En Maduración"),
    ]

    id_producto = models.BigAutoField(primary_key=True)

    # Clave Foránea: Relación Muchos a Uno (N:1) con Categoría
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos",
        verbose_name="Categoría"
    )

    nombre = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    icono_emoji = models.CharField(max_length=10, default="", blank=True, verbose_name="Icono / Identificador")
    imagen_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Imagen")
    origen = models.CharField(max_length=150, default="Cosecha: Hace 1 día • Finca El Campo", verbose_name="Origen / Cosecha")
    unidad_medida = models.CharField(max_length=20, default="kg", verbose_name="Unidad de Medida")

    # Parámetros Agroindustriales y de Calidad
    brix_minimo = models.DecimalField(
        max_digits=4, decimal_places=2, default=0.00, verbose_name="°Brix Mínimo (Dulzor)"
    )
    stock_actual = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.000, verbose_name="Stock Actual"
    )
    stock_minimo = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.000, verbose_name="Stock Mínimo"
    )
    # Estructura Financiera, Costos y Ofertas (Control de Margen de Ganancia)
    costo_compra = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, verbose_name="Costo de Compra"
    )
    precio_venta_unitario = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Precio de Venta Unitario"
    )
    en_oferta = models.BooleanField(
        default=False, verbose_name="¿En Oferta / Promoción?"
    )
    precio_oferta = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Precio de Oferta"
    )
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="Disponible", verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "productos"

    # --------------------------------------------------------------------------
    # PROPIEDADES FINANCIERAS Y DE COMPATIBILIDAD
    # Permiten calcular rentabilidad en tiempo real y mantener compatibilidad
    # con templates que usan .precio, .stock o necesitan ver promociones.
    # --------------------------------------------------------------------------
    @property
    def precio_efectivo(self):
        """Retorna el precio de oferta si está activo y es válido, o el precio regular"""
        if self.en_oferta and self.precio_oferta and self.precio_oferta > 0:
            return self.precio_oferta
        return self.precio_venta_unitario

    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia en pesos: (Precio Efectivo - Costo de Compra)"""
        precio_actual = self.precio_efectivo
        return precio_actual - self.costo_compra

    @property
    def porcentaje_margen(self):
        """Calcula el porcentaje de rentabilidad bruta sobre el costo de adquisición"""
        if self.costo_compra and self.costo_compra > 0:
            margen = self.margen_ganancia
            return round((margen / self.costo_compra) * 100, 1)
        return 0.0

    @property
    def porcentaje_descuento(self):
        """Calcula el porcentaje de descuento promocional si está en oferta"""
        if self.en_oferta and self.precio_oferta and self.precio_venta_unitario > 0:
            if self.precio_oferta < self.precio_venta_unitario:
                ahorro = self.precio_venta_unitario - self.precio_oferta
                return round((ahorro / self.precio_venta_unitario) * 100)
        return 0

    @property
    def precio(self):
        """Retorna el precio efectivo para compatibilidad con plantillas del frontend"""
        return self.precio_efectivo

    @property
    def stock(self):
        """Retorna el stock entero para badges de cantidad en templates"""
        return int(self.stock_actual)

    @property
    def imagen_resuelta(self):
        """
        Resuelve la ruta de imagen priorizando archivos locales en 'static/img/':
        - Si imagen_url coincide con fotos base descargadas en local, retorna la copia local
          para que siga funcionando aunque caiga Unsplash o internet externo.
        - Si el administrador configuró una URL externa personalizada, la conserva.
        - Si está vacía, asigna la imagen local de respaldo.
        """
        base_static = getattr(settings, "STATIC_URL", "/static/").rstrip("/")
        mapa_local = {
            "photo-1619566636858-adf3ef46400b": "img/categorias/citricos.jpg",
            "photo-1550258987-190a2d41a8ba": "img/categorias/tropicales.jpg",
            "photo-1586201375761-83865001e31c": "img/productos/frijol.jpg",
            "photo-1610832958506-aa56368176cf": "img/categorias/ver_todo.jpg",
            "photo-1488459716781-31db52582fe9": "img/secciones/finca_boyaca.jpg",
            "photo-1464965911861-746a04b4bca6": "img/productos/agraz.jpg",
            "photo-1498557850523-fd3d118b962e": "img/productos/arandano.jpg",
            "photo-1607623814075-e51df1bdc82f": "img/productos/mortadela.jpg",
            "photo-1611080626919-7cf5a9dbab5b": "img/productos/naranja.jpg",
            "photo-1590502593747-42a996133562": "img/productos/limon.jpg",
            "photo-1585059895524-72359e06133a": "img/productos/kiwi.jpg",
            "photo-1587049352846-4a222e784d38": "img/productos/sandia.jpg",
            "photo-1528825871115-3581a5387919": "img/productos/banano.jpg",
            "photo-1560806887-1e4cd0b6cbd6": "img/productos/manzana.jpg",
            "photo-1603833665858-e61d17a86224": "img/productos/platano.jpg",
            "photo-1618897996318-5a901fa6ca71": "img/productos/lulo.jpg",
            "photo-1595152772835-219674b2a8a6": "img/productos/durazno.jpg",
        }
        raw_url = (self.imagen_url or "").strip()
        if raw_url:
            for unsplash_id, rel_path in mapa_local.items():
                if unsplash_id in raw_url:
                    return f"{base_static}/{rel_path}"
            return raw_url
        return f"{base_static}/img/productos/default_fruta.jpg"

    def __str__(self):
        oferta_tag = f" [OFERTA: ${self.precio_oferta:,.0f}]" if self.en_oferta and self.precio_oferta else ""
        nombre_display = f"{self.icono_emoji} {self.nombre}".strip() if self.icono_emoji else self.nombre
        return f"{nombre_display} - Venta: ${self.precio_venta_unitario:,.0f}{oferta_tag} (Costo: ${self.costo_compra:,.0f})"


# ==============================================================================
# 4. ENTIDAD CLIENTE
# Gestión de compradores con diferenciación minorista / mayorista.
# ==============================================================================
class Cliente(models.Model):
    """
    Modela los perfiles de compradores de la frutería.
    Permite asignar cupos de crédito comercial y acumulación de puntos de fidelización.
    """
    TIPO_CHOICES = [
        ("DETAL", "Al Detal"),
        ("MAYORISTA", "Mayorista"),
    ]

    id_cliente = models.BigAutoField(primary_key=True)
    tipo_cliente = models.CharField(max_length=10, choices=TIPO_CHOICES, default="DETAL", verbose_name="Tipo de Cliente")
    cupo_credito = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Cupo de Crédito")
    puntos_fidelidad = models.IntegerField(default=0, verbose_name="Puntos de Fidelidad")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clientes"

    def __str__(self):
        return f"Cliente #{self.id_cliente} ({self.tipo_cliente})"


class RegistroLogin(models.Model):
    ESTADOS_LOGIN = [
        ('exitoso', 'Exitoso'),
        ('fallido', 'Credenciales Incorrectas'),
        ('inactivo', 'Usuario Inactivo / Pendiente'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='historial_logins')
    identificador = models.CharField(max_length=150, verbose_name="Usuario / Email ingresado")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    rol = models.CharField(max_length=30, blank=True, null=True, verbose_name="Rol en el sistema")
    estado = models.CharField(max_length=20, choices=ESTADOS_LOGIN, verbose_name="Estado del Acceso")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Acceso")
    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")

    class Meta:
        verbose_name = "Registro de Login"
        verbose_name_plural = "Registros de Login"
        ordering = ['-fecha_creacion']
        db_table = "registros_login"

    def __str__(self):
        return f"{self.identificador} - {self.get_estado_display()} ({self.fecha_creacion.strftime('%d/%m/%Y %H:%M')})"


class PerfilUsuario(models.Model):
    # NOTA TÉCNICA (INTEGRACIÓN EQUIPO):
    # Se integra el rol 'bodeguero' creado por Gutiérrez en conjunto con 'admin', 'cajero' y 'cliente'
    # para garantizar compatibilidad total con la administración, logística y catálogo de clientes.
    ROLES = [
        ('admin', 'Super Admin'),
        ('bodeguero', 'Bodeguero'),
        ('cajero', 'Cajero'),
        ('cliente', 'Cliente'),
    ]
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name="Usuario")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    rol = models.CharField(max_length=30, choices=ROLES, default='admin', verbose_name="Rol en el sistema")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo', verbose_name="Estado de la cuenta")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ['-fecha_creacion']
        db_table = "perfiles_usuario"

    @property
    def nombre_rol(self):
        """Retorna la etiqueta legible del rol (Super Admin, Bodeguero, Cajero, Cliente)"""
        if self.usuario.is_superuser or self.rol == 'admin':
            return 'Super Admin'
        elif self.rol == 'bodeguero':
            return 'Bodeguero'
        elif self.rol == 'cajero':
            return 'Cajero'
        elif self.rol == 'cliente':
            return 'Cliente'
        return self.get_rol_display()

    @property
    def rol_prioridad(self):
        """Jerarquía de ordenamiento requerida: 1. Super Admin, 2. Bodeguero, 3. Cajero"""
        if self.usuario.is_superuser or self.rol == 'admin':
            return 1
        elif self.rol == 'bodeguero':
            return 2
        elif self.rol == 'cajero':
            return 3
        return 4

    @property
    def es_admin(self):
        """Retorna True si el usuario tiene rol de Super Admin o rol 'admin'"""
        return self.usuario.is_superuser or self.rol == 'admin'

    def __str__(self):
        return f"{self.usuario.username} ({self.nombre_rol}) - {self.get_estado_display()}"


# ==============================================================================
# 5. ENTIDAD VENTA
# Gestión de transacciones comerciales y punto de venta
# ==============================================================================
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.IntegerField(null=True, blank=True, verbose_name="ID Cliente")
    id_usuario_cajero = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='id_usuario_cajero',
        related_name='ventas',
        verbose_name="Cajero / Vendedor"
    )
    origen_venta = models.CharField(max_length=40, default="Tienda Física", verbose_name="Origen de Venta")
    fecha_venta = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Subtotal")
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True, verbose_name="Descuento")
    total_neto = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total Neto")
    medio_pago = models.CharField(max_length=30, default="Efectivo", verbose_name="Medio de Pago")
    estado_venta = models.CharField(max_length=30, default="Completada", blank=True, null=True, verbose_name="Estado")

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        db_table = "ventas"
        ordering = ['-fecha_venta']

    @property
    def cliente(self):
        """Retorna la instancia de Cliente asociada a id_cliente si existe."""
        if not self.id_cliente:
            return None
        return Cliente.objects.filter(pk=self.id_cliente).first()

    def __str__(self):
        return f"Venta #{self.id_venta} - Total: ${self.total_neto}"


# ==============================================================================
# SEÑALES DE INTEGRIDAD Y AUDITORÍA AUTOMÁTICA
# NOTA PARA EL EQUIPO:
# Se implementan señales automáticas de Django para:
# 1. Garantizar que ningún usuario quede sin PerfilUsuario (post_save).
# 2. Poblar RegistroLogin automáticamente ante inicios de sesión exitosos o fallidos para auditoría.
# ==============================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed


@receiver(post_save, sender=User)
def garantizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Garantiza que todo usuario en el sistema disponga de un PerfilUsuario vinculado.
    Asigna rol 'admin' a superusuarios, 'cajero' a staff y 'cliente' a usuarios estándar.
    """
    if created:
        rol_default = 'admin' if instance.is_superuser else ('cajero' if instance.is_staff else 'cliente')
        PerfilUsuario.objects.get_or_create(
            usuario=instance,
            defaults={
                'rol': rol_default,
                'estado': 'activo',
            }
        )


@receiver(user_logged_in)
def registrar_acceso_exitoso(sender, request, user, **kwargs):
    """Registra automáticamente en RegistroLogin los accesos exitosos para auditoría."""
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1')) if request else '127.0.0.1'
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        perfil = getattr(user, 'perfil', None)
        RegistroLogin.objects.create(
            usuario=user,
            identificador=user.username,
            telefono=perfil.telefono if perfil else None,
            rol=perfil.rol if perfil else ('admin' if user.is_staff else 'cliente'),
            estado='exitoso',
            ip_origen=ip[:45] if ip else '127.0.0.1'
        )
    except Exception:
        pass


@receiver(user_login_failed)
def registrar_acceso_fallido(sender, credentials, request, **kwargs):
    """Registra automáticamente en RegistroLogin los intentos fallidos de autenticación."""
    try:
        identificador = credentials.get('username', 'desconocido') if credentials else 'desconocido'
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1')) if request else '127.0.0.1'
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        RegistroLogin.objects.create(
            usuario=None,
            identificador=identificador,
            estado='fallido',
            ip_origen=ip[:45] if ip else '127.0.0.1'
        )
    except Exception:
        pass
