"""
Formularios para el módulo de Inventario.
"""
from django import forms
from .models import CategoriaRepuesto, Repuesto


class CategoriaRepuestoForm(forms.ModelForm):
    class Meta:
        model = CategoriaRepuesto
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = [
            "codigo", "nombre", "descripcion", "categoria",
            "marca", "modelo", "stock_actual", "stock_minimo",
            "stock_maximo", "precio_compra", "precio_venta",
            "ubicacion", "activo"
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "marca": forms.TextInput(attrs={"class": "form-control"}),
            "modelo": forms.TextInput(attrs={"class": "form-control"}),
            "stock_actual": forms.NumberInput(attrs={"class": "form-control"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control"}),
            "stock_maximo": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_compra": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "precio_venta": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MovimientoInventarioForm(forms.Form):
    """Formulario para registrar movimientos manuales de inventario."""
    repuesto = forms.ModelChoiceField(
        queryset=Repuesto.objects.filter(activo=True),
        widget=forms.Select(attrs={"class": "form-select"})
    )
    tipo = forms.ChoiceField(
        choices=[("ENTRADA", "Entrada"), ("SALIDA", "Salida"), ("AJUSTE", "Ajuste")],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )
