# INICIO CAMBIOS GUÍA 4: formularios seguros y campos con estilos Bootstrap.
from typing import ClassVar

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Categoria, Producto


class FormularioInicioSesion(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "current-password"}
        )


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = (
            "categoria",
            "nombre",
            "icono_emoji",
            "imagen_url",
            "origen",
            "unidad_medida",
            "brix_minimo",
            "stock_actual",
            "stock_minimo",
            "precio_venta_unitario",
            "estado",
        )
        labels: ClassVar[dict[str, str]] = {
            "categoria": "Categoría",
            "nombre": "Nombre del producto",
            "icono_emoji": "Icono",
            "imagen_url": "URL de imagen",
            "origen": "Origen y cosecha",
            "unidad_medida": "Unidad de medida",
            "brix_minimo": "Grados Brix mínimos",
            "stock_actual": "Stock actual",
            "stock_minimo": "Stock mínimo",
            "precio_venta_unitario": "Precio de venta unitario",
            "estado": "Estado",
        }
        error_messages: ClassVar[dict[str, str | dict[str, str]]] = {
            "categoria": {"required": "Selecciona una categoría."},
            "nombre": {
                "required": "El nombre del producto es obligatorio.",
                "max_length": "El nombre no puede superar los 100 caracteres.",
            },
            "imagen_url": {"invalid": "Ingresa una URL válida para la imagen."},
            "precio_venta_unitario": {
                "required": "El precio de venta es obligatorio.",
                "invalid": "Ingresa un precio válido.",
            },
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "icono_emoji": forms.TextInput(attrs={"class": "form-control"}),
            "imagen_url": forms.URLInput(attrs={"class": "form-control"}),
            "origen": forms.TextInput(attrs={"class": "form-control"}),
            "unidad_medida": forms.TextInput(attrs={"class": "form-control"}),
            "brix_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.01"}
            ),
            "stock_actual": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.001"}
            ),
            "stock_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.001"}
            ),
            "precio_venta_unitario": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "0.01"}
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre no puede estar vacío.")
        return nombre

    def clean_unidad_medida(self):
        unidad_medida = self.cleaned_data["unidad_medida"].strip()
        if not unidad_medida:
            raise forms.ValidationError("La unidad de medida no puede estar vacía.")
        return unidad_medida

    def clean_origen(self):
        origen = self.cleaned_data["origen"].strip()
        if not origen:
            raise forms.ValidationError("El origen no puede estar vacío.")
        return origen

    def clean_brix_minimo(self):
        brix_minimo = self.cleaned_data["brix_minimo"]
        if brix_minimo < 0:
            raise forms.ValidationError("Los grados Brix no pueden ser negativos.")
        return brix_minimo

    def clean_stock_actual(self):
        stock_actual = self.cleaned_data["stock_actual"]
        if stock_actual < 0:
            raise forms.ValidationError("El stock actual no puede ser negativo.")
        return stock_actual

    def clean_stock_minimo(self):
        stock_minimo = self.cleaned_data["stock_minimo"]
        if stock_minimo < 0:
            raise forms.ValidationError("El stock mínimo no puede ser negativo.")
        return stock_minimo

    def clean_precio_venta_unitario(self):
        precio = self.cleaned_data["precio_venta_unitario"]
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre", "descripcion")
        labels: ClassVar[dict[str, str]] = {
            "nombre": "Nombre de la categoría",
            "descripcion": "Descripción",
        }
        error_messages: ClassVar[dict[str, str | dict[str, str]]] = {
            "nombre": {
                "required": "El nombre de la categoría es obligatorio.",
                "max_length": "El nombre no puede superar los 60 caracteres.",
            },
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre no puede estar vacío.")
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if descripcion and not descripcion.strip():
            return ""
        return descripcion.strip() if descripcion else descripcion
# FIN CAMBIOS GUÍA 4
