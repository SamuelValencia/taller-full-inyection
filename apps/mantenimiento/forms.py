from django import forms
from .models import TipoServicioMantenimiento, ProgramaMantenimiento, HistorialMantenimiento


class TipoServicioForm(forms.ModelForm):
    class Meta:
        model = TipoServicioMantenimiento
        fields = ["nombre", "descripcion", "intervalo_km_recomendado", "intervalo_dias_recomendado"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "intervalo_km_recomendado": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "intervalo_dias_recomendado": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


class ProgramaMantenimientoForm(forms.ModelForm):
    class Meta:
        model = ProgramaMantenimiento
        fields = ["vehiculo", "tipo_servicio", "ultimo_km", "ultima_fecha", "intervalo_km", "intervalo_dias", "observaciones"]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-select"}),
            "tipo_servicio": forms.Select(attrs={"class": "form-select"}),
            "ultimo_km": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ultima_fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "intervalo_km": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "intervalo_dias": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class HistorialMantenimientoForm(forms.ModelForm):
    class Meta:
        model = HistorialMantenimiento
        fields = ["vehiculo", "orden", "tipo_servicio", "descripcion", "km_al_servicio",
                  "proximo_km_sugerido", "proxima_fecha_sugerida", "costo", "fecha_servicio", "observaciones"]
        widgets = {
            "vehiculo": forms.Select(attrs={"class": "form-select"}),
            "orden": forms.Select(attrs={"class": "form-select"}),
            "tipo_servicio": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "km_al_servicio": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "proximo_km_sugerido": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "proxima_fecha_sugerida": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "costo": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "fecha_servicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
