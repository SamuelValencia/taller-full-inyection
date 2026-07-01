from django import forms
from .models import Cotizacion


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ["vehiculo", "cliente", "descripcion", "fecha_validez", "descuento", "aplica_iva", "observaciones"]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-select"}),
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha_validez": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descuento": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "aplica_iva": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
