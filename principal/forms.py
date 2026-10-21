# ==============================================================================
# FORMULARIOS ROBUSTOS DEL SISTEMA (principal/forms.py)
# Valida reglas de negocio, tipos de datos y persistencia con Django ModelForm.
# ==============================================================================

from decimal import Decimal
from typing import ClassVar
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Producto, Categoria, Proveedor


class FormularioInicioSesion(AuthenticationForm):
    """
    Formulario de autenticación con estilos y atributos Bootstrap para username y password.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "current-password"}
        )


class ProductoForm(forms.ModelForm):
    """
    Formulario para creación y edición de productos agrícolas.
    Aplica validaciones financieras de margen y coherencia de precios.
    """
    class Meta:
        model = Producto
        fields = [
            'categoria',
            'nombre',
            'costo_compra',
            'precio_venta_unitario',
            'en_oferta',
            'precio_oferta',
            'stock_actual',
            'stock_minimo',
            'unidad_medida',
            'brix_minimo',
            'origen',
            'icono_emoji',
            'imagen_url',
            'estado'
        ]
        labels: ClassVar[dict[str, str]] = {
            'categoria': 'Categoría',
            'nombre': 'Nombre del producto',
            'costo_compra': 'Costo de compra',
            'precio_venta_unitario': 'Precio de venta unitario',
            'en_oferta': '¿En oferta / promoción?',
            'precio_oferta': 'Precio de oferta',
            'stock_actual': 'Stock actual',
            'stock_minimo': 'Stock mínimo',
            'unidad_medida': 'Unidad de medida',
            'brix_minimo': 'Grados Brix mínimos',
            'origen': 'Origen y cosecha',
            'icono_emoji': 'Icono / Identificador',
            'imagen_url': 'URL de imagen',
            'estado': 'Estado',
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'costo_compra': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'precio_venta_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'en_oferta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'precio_oferta': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'brix_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'icono_emoji': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen_url': forms.URLInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

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
            if not data.get('imagen_url'):
                data['imagen_url'] = getattr(inst, 'imagen_url', '') or 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?q=80&w=600&auto=format&fit=crop'
            if not data.get('origen'):
                data['origen'] = getattr(inst, 'origen', '') or 'Cosecha: Hace 1 día • Finca El Campo'
            if 'icono_emoji' not in data:
                data['icono_emoji'] = getattr(inst, 'icono_emoji', '') or ''
            if not data.get('estado'):
                data['estado'] = getattr(inst, 'estado', '') or 'Disponible'
            if not data.get('unidad_medida'):
                data['unidad_medida'] = getattr(inst, 'unidad_medida', '') or 'kg'
            if 'costo_compra' not in data or data.get('costo_compra') in [None, '']:
                data['costo_compra'] = str(getattr(inst, 'costo_compra', '0.00') if getattr(inst, 'costo_compra', None) is not None else '0.00')
            if 'brix_minimo' not in data or data.get('brix_minimo') in [None, '']:
                data['brix_minimo'] = str(getattr(inst, 'brix_minimo', '0.00') if getattr(inst, 'brix_minimo', None) is not None else '0.00')
            if 'stock_minimo' not in data or data.get('stock_minimo') in [None, '']:
                data['stock_minimo'] = str(getattr(inst, 'stock_minimo', '0.000') if getattr(inst, 'stock_minimo', None) is not None else '0.000')

            if len(args) > 0:
                args[0] = data
                args = tuple(args)
            else:
                kwargs['data'] = data

        super().__init__(*args, **kwargs)
        for campo_opcional in ['costo_compra', 'brix_minimo', 'origen', 'icono_emoji', 'imagen_url', 'en_oferta', 'precio_oferta', 'stock_minimo', 'unidad_medida', 'estado']:
            if campo_opcional in self.fields:
                self.fields[campo_opcional].required = False

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre del producto no puede estar vacío.")
        return nombre

    def clean_unidad_medida(self):
        unidad_medida = self.cleaned_data.get('unidad_medida', '').strip()
        if not unidad_medida:
            return 'kg'
        return unidad_medida

    def clean_origen(self):
        origen = self.cleaned_data.get('origen', '').strip()
        if not origen:
            return 'Cosecha: Hace 1 día • Finca El Campo'
        return origen

    def clean_brix_minimo(self):
        brix = self.cleaned_data.get('brix_minimo')
        if brix is None:
            return Decimal('0.00')
        if brix < 0:
            raise forms.ValidationError("Los grados Brix no pueden ser negativos.")
        return brix

    def clean_stock_actual(self):
        stock = self.cleaned_data.get('stock_actual')
        if stock is not None and stock < 0:
            raise forms.ValidationError("El stock actual no puede ser negativo.")
        return stock

    def clean_stock_minimo(self):
        stock_min = self.cleaned_data.get('stock_minimo')
        if stock_min is None:
            return Decimal('0.000')
        if stock_min < 0:
            raise forms.ValidationError("El stock mínimo no puede ser negativo.")
        return stock_min

    def clean_costo_compra(self):
        costo = self.cleaned_data.get('costo_compra')
        if costo is None:
            return Decimal('0.00')
        if costo < 0:
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
        labels: ClassVar[dict[str, str]] = {
            'nombre': 'Nombre de la categoría',
            'descripcion': 'Descripción',
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre de la categoría es obligatorio.")
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and not descripcion.strip():
            return ""
        return descripcion.strip() if descripcion else descripcion


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
