from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Proveedor, Producto, Cliente, RegistroLogin, PerfilUsuario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id_proveedor', 'razon_social', 'nit_rut', 'contacto_nombre', 'telefono', 'calificacion_estrellas', 'estado')
    search_fields = ('razon_social', 'nit_rut', 'contacto_nombre')
    list_filter = ('estado',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id_producto',
        'nombre',
        'categoria',
        'costo_compra',
        'precio_venta_unitario',
        'en_oferta',
        'precio_oferta',
        'mostrar_margen',
        'stock_actual',
        'estado'
    )
    search_fields = ('nombre', 'categoria__nombre', 'origen')
    list_filter = ('categoria', 'en_oferta', 'estado', 'unidad_medida')
    list_editable = ('costo_compra', 'precio_venta_unitario', 'en_oferta', 'precio_oferta', 'stock_actual', 'estado')

    fieldsets = (
        ('Información General del Producto', {
            'fields': ('nombre', 'categoria', 'imagen_url', 'origen', 'unidad_medida', 'brix_minimo')
        }),
        ('Estructura de Precios, Costos y Ofertas (Margen de Ganancia)', {
            'fields': ('costo_compra', 'precio_venta_unitario', 'en_oferta', 'precio_oferta'),
            'description': 'Establezca el costo de compra al proveedor y el precio de venta para garantizar el margen de rentabilidad.'
        }),
        ('Inventario y Control de Existencias', {
            'fields': ('stock_actual', 'stock_minimo', 'estado')
        }),
    )

    @admin.display(description="Margen de Ganancia")
    def mostrar_margen(self, obj):
        """Muestra el margen en pesos y el porcentaje de rentabilidad con código de color"""
        margen = obj.margen_ganancia
        pct = obj.porcentaje_margen
        if margen > 0:
            color = "#1b5e20"  # Verde oscuro legible
            badge_bg = "#e8f5e9"
            signo = "+"
        elif margen == 0:
            color = "#616161"
            badge_bg = "#f5f5f5"
            signo = ""
        else:
            color = "#b71c1c"  # Rojo
            badge_bg = "#ffebee"
            signo = ""
        margen_str = f"{signo}${margen:,.0f}"
        pct_str = f"({pct:+.1f}%)"
        return format_html(
            '<span style="background:{}; padding: 3px 8px; border-radius: 4px; display: inline-block;">'
            '<strong style="color: {};">{}</strong> '
            '<small style="color: #333; font-weight:600;">{}</small>'
            '</span>',
            badge_bg, color, margen_str, pct_str
        )



@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'tipo_cliente', 'cupo_credito', 'puntos_fidelidad')
    list_filter = ('tipo_cliente',)


@admin.register(RegistroLogin)
class RegistroLoginAdmin(admin.ModelAdmin):
    list_display = ('fecha_creacion', 'identificador', 'rol', 'telefono', 'estado', 'ip_origen')
    list_filter = ('estado', 'rol', 'fecha_creacion')
    search_fields = ('identificador', 'telefono', 'ip_origen')
    readonly_fields = ('fecha_creacion', 'identificador', 'usuario', 'telefono', 'rol', 'estado', 'ip_origen')

    def has_add_permission(self, request):
        return False  # Los registros son automáticos, no se crean a mano


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'telefono', 'estado', 'fecha_creacion')
    list_filter = ('rol', 'estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'usuario__email', 'telefono')


# ==============================================================================
# INTEGRACIÓN DE PERFIL INSTITUCIONAL EN EL ADMINISTRADOR DE USUARIOS DE DJANGO
# NOTA PARA EL EQUIPO:
# Se integra PerfilUsuarioInline en UserAdmin para que los administradores puedan crear y asignar
# roles institucionales (Administrador, Cajero, Cliente) y teléfonos a cualquier usuario desde una sola pantalla.
# ==============================================================================
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class PerfilUsuarioInline(admin.StackedInline):
    """Permite ver y editar el rol y contacto directamente desde la ficha del usuario en admin."""
    model = PerfilUsuario
    can_delete = False
    verbose_name = 'Perfil Institucional'
    verbose_name_plural = 'Perfil Institucional y Rol'
    fk_name = 'usuario'


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Administrador extendido de usuarios que incluye perfil, roles (admin/cajero/cliente),
    estado de cuenta y filtros avanzados de auditoría.
    """
    inlines = (PerfilUsuarioInline,)
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_rol',
        'get_estado',
        'is_staff',
        'is_superuser'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'perfil__rol', 'perfil__estado')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__telefono')

    @admin.display(description="Rol Institucional")
    def get_rol(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil:
            return obj.perfil.get_rol_display()
        return "Sin perfil"

    @admin.display(description="Estado Cuenta")
    def get_estado(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil:
            return obj.perfil.get_estado_display()
        return "Activo"

