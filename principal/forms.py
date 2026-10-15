# ==============================================================================
# FORMULARIOS ROBUSTOS DEL SISTEMA (principal/forms.py)
# Valida reglas de negocio, tipos de datos y persistencia con Django ModelForm.
# ==============================================================================

from decimal import Decimal
from django import forms
from .models import Producto, Categoria, Proveedor


class ProductoForm(forms.ModelForm):
    """
    Formulario para creación y edición de productos agrícolas.
    Aplica validaciones financieras de margen y coherencia de precios.
    """
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'categoria',
            'costo_compra',
            'precio_venta_unitario',
            'en_oferta',
            'precio_oferta',
            'stock_actual',
            'stock_minimo',
            'unidad_medida',
            'origen',
            'icono_emoji',
            'imagen_url',
            'estado'
        ]

    def __init__(self, *args, **kwargs):
        # Normalizar ya sea que data venga como args[0] o kwargs['data']
        data = None
        if len(args) > 0 and args[0] is not None:
            data = args[0].copy()
            args = list(args)
        elif 'data' in kwargs and kwargs['data'] is not None:
            data = kwargs['data'].copy()

        inst = kwargs.get('instance')

        if data is not None:
            # Mapeo retrocompatible con templates y tests que envían categoria_id
            if 'categoria_id' in data and not data.get('categoria'):
                data['categoria'] = data.get('categoria_id')

            # Normalización de números con coma a punto
            for campo in ['costo_compra', 'precio_venta_unitario', 'precio_oferta', 'stock_actual', 'stock_minimo']:
                if campo in data and isinstance(data[campo], str):
                    val = data[campo].strip().replace(',', '.')
                    if campo == 'precio_oferta' and (val == '' or not data.get('en_oferta')):
                        data[campo] = None
                    else:
                        data[campo] = val

            # Respaldos predeterminados para asegurar consistencia
            if not data.get('imagen_url') and not getattr(inst, 'imagen_url', None):
                data['imagen_url'] = 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=600&auto=format&fit=crop'
            if not data.get('origen') and not getattr(inst, 'origen', None):
                data['origen'] = 'Cosecha: Hace 1 día • Finca El Campo'
            if 'icono_emoji' not in data and not getattr(inst, 'icono_emoji', None):
                data['icono_emoji'] = ''
            if not data.get('estado') and not getattr(inst, 'estado', None):
                data['estado'] = 'Disponible'
            if not data.get('unidad_medida') and not getattr(inst, 'unidad_medida', None):
                data['unidad_medida'] = 'kg'

            if len(args) > 0:
                args[0] = data
                args = tuple(args)
            else:
                kwargs['data'] = data

        super().__init__(*args, **kwargs)
        if 'origen' in self.fields:
            self.fields['origen'].required = False
        if 'icono_emoji' in self.fields:
            self.fields['icono_emoji'].required = False
        if 'imagen_url' in self.fields:
            self.fields['imagen_url'].required = False

    def clean_costo_compra(self):
        costo = self.cleaned_data.get('costo_compra')
        if costo is not None and costo < 0:
            raise forms.ValidationError("El costo de compra no puede ser negativo.")
        return costo

    def clean_precio_venta_unitario(self):
        precio = self.cleaned_data.get('precio_venta_unitario')
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio de venta debe ser mayor a cero.")
        return precio

    def clean(self):
        cleaned_data = super().clean()
        costo = cleaned_data.get('costo_compra')
        precio = cleaned_data.get('precio_venta_unitario')
        en_oferta = cleaned_data.get('en_oferta')
        precio_oferta = cleaned_data.get('precio_oferta')

        # Regla 1: El precio regular debe cubrir el costo para evitar pérdida comercial
        if costo and precio and costo >= precio:
            self.add_error('precio_venta_unitario', "El precio de venta debe ser superior al costo de compra.")

        # Regla 2: Coherencia en ofertas
        if en_oferta:
            if not precio_oferta or precio_oferta <= 0:
                self.add_error('precio_oferta', "Debe especificar un precio promocional válido si la oferta está activa.")
            elif precio and precio_oferta >= precio:
                self.add_error('precio_oferta', "El precio de oferta debe ser menor al precio de venta regular.")
            elif costo and precio_oferta < costo:
                self.add_error('precio_oferta', "El precio de oferta no puede ser inferior al costo de compra (margen negativo).")
        else:
            cleaned_data['precio_oferta'] = None

        return cleaned_data


class CategoriaForm(forms.ModelForm):
    """
    Formulario para la gestión de categorías del catálogo.
    """
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre de la categoría es obligatorio.")
        return nombre


class ProveedorForm(forms.ModelForm):
    """
    Formulario para el registro y actualización de productores agrícolas y proveedores aliados.
    """
    class Meta:
        model = Proveedor
        fields = [
            'razon_social',
            'nit_rut',
            'contacto_nombre',
            'telefono',
            'email',
            'calificacion_estrellas',
            'estado'
        ]

    def clean_razon_social(self):
        razon = self.cleaned_data.get('razon_social', '').strip()
        if not razon:
            raise forms.ValidationError("La razón social o nombre de la finca es obligatorio.")
        return razon

    def clean_nit_rut(self):
        nit = self.cleaned_data.get('nit_rut', '').strip()
        if not nit:
            raise forms.ValidationError("El NIT o RUT de identificación es obligatorio.")
        return nit

    def clean_calificacion_estrellas(self):
        calif = self.cleaned_data.get('calificacion_estrellas')
        if calif is not None:
            if calif < 1.0 or calif > 5.0:
                raise forms.ValidationError("La calificación debe estar entre 1.0 y 5.0 estrellas.")
        return calif
