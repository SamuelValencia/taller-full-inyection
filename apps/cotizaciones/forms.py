from django import forms
from .models import Cotizacion


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ["vehiculo", "cliente", "descripcion", "fecha_validez", "descuento", "observaciones"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select select2-enable", "data-placeholder": "Buscar cliente…"}),
            "vehiculo": forms.Select(attrs={"class": "form-select select2-enable", "data-placeholder": "Seleccione un vehículo…"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha_validez": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descuento": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
