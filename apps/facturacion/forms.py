"""
Formularios para el módulo de Facturación.
"""
from django import forms
from .models import FacturaInterna


class FacturaInternaForm(forms.ModelForm):
    class Meta:
        model = FacturaInterna
        fields = ["orden", "observaciones"]
        widgets = {
            "orden": forms.Select(attrs={"class": "form-select"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class AnularFacturaForm(forms.Form):
    motivo = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Motivo de anulación"
    )
