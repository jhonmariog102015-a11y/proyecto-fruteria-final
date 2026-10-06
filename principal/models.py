# ==============================================================================
# MODELO ENTIDAD-RELACIÓN DEL PROYECTO (principal/models.py)
# Define la estructura de base de datos relacional para "El Paso Frutería"
# Basado en la guía de diseño de datos SENA ADSO (Ficha 3321349).
# ==============================================================================

from django.db import models


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
    icono_emoji = models.CharField(max_length=10, default="🍎", verbose_name="Icono / Emoji")
    imagen_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL de Imagen")
    origen = models.CharField(max_length=150, default="🌱 Cosecha: Hace 1 día • Finca El Campo", verbose_name="Origen / Cosecha")
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
    precio_venta_unitario = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Precio de Venta Unitario"
    )
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="Disponible", verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "productos"

    # --------------------------------------------------------------------------
    # PROPIEDADES DE COMPATIBILIDAD (Dual API)
    # Permiten que las vistas de Guti que usaban '.precio' o '.stock' sigan
    # funcionando sin necesidad de modificar el esquema relacional G-03.
    # --------------------------------------------------------------------------
    @property
    def precio(self):
        """Retorna el precio unitario para compatibilidad con templates heredados"""
        return self.precio_venta_unitario

    @property
    def stock(self):
        """Retorna el stock entero para badges de cantidad en templates"""
        return int(self.stock_actual)

    def __str__(self):
        return f"{self.icono_emoji} {self.nombre} - ${self.precio_venta_unitario:,.0f} / {self.unidad_medida}"


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

