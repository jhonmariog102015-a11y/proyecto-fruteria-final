from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Proveedor, Producto, Cliente, RegistroLogin, PerfilUsuario, Venta


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


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id_venta',
        'id_usuario_cajero',
        'fecha_venta',
        'origen_venta',
        'medio_pago',
        'subtotal',
        'descuento',
        'total_neto',
        'estado_venta'
    )
    list_filter = ('estado_venta', 'medio_pago', 'origen_venta', 'fecha_venta')
    search_fields = ('id_venta', 'id_usuario_cajero__username', 'medio_pago')
    ordering = ('-fecha_venta',)


from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil del Usuario (Rol, Teléfono y Estado)'
    fk_name = 'usuario'
    extra = 0


# Re-registrar User para unificar el perfil sin duplicidad de tablas o columnas en el admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'mostrar_rol', 'mostrar_telefono', 'mostrar_estado', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'perfil__rol', 'perfil__estado')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__telefono')

    @admin.display(description="Rol en el Sistema", ordering="perfil__rol")
    def mostrar_rol(self, obj):
        if obj.is_superuser or (hasattr(obj, 'perfil') and obj.perfil.rol == 'admin'):
            return mark_safe('<span style="background:#fee2e2; color:#b91c1c; padding:3px 8px; border-radius:4px; font-weight:700;">Super Admin</span>')
        rol = getattr(obj.perfil, 'rol', None) if hasattr(obj, 'perfil') else None
        if rol == 'bodeguero':
            return mark_safe('<span style="background:#fef3c7; color:#b45309; padding:3px 8px; border-radius:4px; font-weight:700;">Bodeguero</span>')
        elif rol == 'cajero':
            return mark_safe('<span style="background:#d1fae5; color:#047857; padding:3px 8px; border-radius:4px; font-weight:700;">Cajero</span>')
        return mark_safe('<span style="color:#64748b;">—</span>')

    @admin.display(description="Teléfono")
    def mostrar_telefono(self, obj):
        return getattr(obj.perfil, 'telefono', '—') if hasattr(obj, 'perfil') else '—'

    @admin.display(description="Estado", ordering="perfil__estado")
    def mostrar_estado(self, obj):
        estado = getattr(obj.perfil, 'estado', 'activo') if hasattr(obj, 'perfil') else ('activo' if obj.is_active else 'inactivo')
        if estado == 'activo' and obj.is_active:
            return mark_safe('<span style="background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:4px; font-weight:600;">Activo</span>')
        return mark_safe('<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:4px; font-weight:600;">Inactivo</span>')


@admin.register(RegistroLogin)
class RegistroLoginAdmin(admin.ModelAdmin):
    list_display = ('fecha_creacion', 'identificador', 'rol', 'telefono', 'estado', 'ip_origen')
    list_filter = ('estado', 'rol', 'fecha_creacion')
    search_fields = ('identificador', 'telefono', 'ip_origen')
    readonly_fields = ('fecha_creacion', 'identificador', 'telefono', 'rol', 'estado', 'ip_origen')

    def has_add_permission(self, request):
        return False  # Los registros son automáticos, no se crean a mano


from django.utils.safestring import mark_safe


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mostrar_rol', 'telefono', 'mostrar_estado', 'fecha_creacion')
    list_filter = ('rol', 'estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'usuario__email', 'telefono')
    ordering = ('rol', 'usuario__username')

    @admin.display(description="Rol Asignado", ordering="rol")
    def mostrar_rol(self, obj):
        if obj.usuario.is_superuser or obj.rol == 'admin':
            return mark_safe('<span style="background:#fee2e2; color:#b91c1c; padding:3px 8px; border-radius:4px; font-weight:700;">Super Admin</span>')
        elif obj.rol == 'bodeguero':
            return mark_safe('<span style="background:#fef3c7; color:#b45309; padding:3px 8px; border-radius:4px; font-weight:700;">Bodeguero</span>')
        elif obj.rol == 'cajero':
            return mark_safe('<span style="background:#d1fae5; color:#047857; padding:3px 8px; border-radius:4px; font-weight:700;">Cajero</span>')
        return obj.get_rol_display()

    @admin.display(description="Estado", ordering="estado")
    def mostrar_estado(self, obj):
        if obj.estado == 'activo' and obj.usuario.is_active:
            return mark_safe('<span style="background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:4px; font-weight:600;">Activo</span>')
        return mark_safe('<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:4px; font-weight:600;">Inactivo</span>')


# ==============================================================================
# INTEGRACIÓN DE PERFIL INSTITUCIONAL EN EL ADMINISTRADOR DE USUARIOS DE DJANGO
# ==============================================================================
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil del Usuario (Rol, Teléfono y Estado)'
    fk_name = 'usuario'
    extra = 0


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'mostrar_rol', 'mostrar_telefono', 'mostrar_estado', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'perfil__rol', 'perfil__estado')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__telefono')

    @admin.display(description="Rol en el Sistema", ordering="perfil__rol")
    def mostrar_rol(self, obj):
        if obj.is_superuser or (hasattr(obj, 'perfil') and obj.perfil.rol == 'admin'):
            return mark_safe('<span style="background:#fee2e2; color:#b91c1c; padding:3px 8px; border-radius:4px; font-weight:700;">Super Admin</span>')
        rol = getattr(obj.perfil, 'rol', None) if hasattr(obj, 'perfil') else None
        if rol == 'bodeguero':
            return mark_safe('<span style="background:#fef3c7; color:#b45309; padding:3px 8px; border-radius:4px; font-weight:700;">Bodeguero</span>')
        elif rol == 'cajero':
            return mark_safe('<span style="background:#d1fae5; color:#047857; padding:3px 8px; border-radius:4px; font-weight:700;">Cajero</span>')
        return mark_safe('<span style="color:#64748b;">—</span>')

    @admin.display(description="Teléfono")
    def mostrar_telefono(self, obj):
        return getattr(obj.perfil, 'telefono', '—') if hasattr(obj, 'perfil') else '—'

    @admin.display(description="Estado", ordering="perfil__estado")
    def mostrar_estado(self, obj):
        estado = getattr(obj.perfil, 'estado', 'activo') if hasattr(obj, 'perfil') else ('activo' if obj.is_active else 'inactivo')
        if estado == 'activo' and obj.is_active:
            return mark_safe('<span style="background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:4px; font-weight:600;">Activo</span>')
        return mark_safe('<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:4px; font-weight:600;">Inactivo</span>')


# ==============================================================================
# RESTRICCIÓN DE SEGURIDAD: DJANGO ADMIN EXCLUSIVO PARA SUPERUSUARIOS
# Solo los usuarios con is_superuser=True y is_active=True pueden acceder a /admin/
# ==============================================================================
def superuser_only_has_permission(request):
    """Garantiza que el panel nativo de Django (/admin/) sea accesible únicamente para Super Admins."""
    return bool(request.user and request.user.is_active and request.user.is_superuser)

admin.site.has_permission = superuser_only_has_permission

