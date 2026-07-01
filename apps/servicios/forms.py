from django import forms
from .models import Servicio


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["nombre", "categoria", "descripcion", "estado"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cambio de aceite"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
