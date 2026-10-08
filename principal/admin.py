from django.contrib import admin
from .models import Categoria, Proveedor, Producto, Cliente


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id_proveedor', 'razon_social', 'nit_rut', 'contacto_nombre', 'telefono', 'calificacion_estrellas', 'estado')
    search_fields = ('razon_social', 'nit_rut', 'contacto_nombre')
    list_filter = ('estado',)


from django.utils.html import format_html


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id_producto',
        'icono_emoji',
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
            'fields': ('nombre', 'categoria', 'icono_emoji', 'imagen_url', 'origen', 'unidad_medida', 'brix_minimo')
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
