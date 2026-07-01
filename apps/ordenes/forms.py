from django import forms
from django.core.exceptions import ValidationError

from apps.vehiculos.models import Vehiculo
from .models import OrdenTrabajo


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = [
            "cliente", "vehiculo", "tecnico_asignado", "estado", "prioridad",
            "tipo_trabajo", "kilometraje_ingreso", "fecha_estimada_entrega",
            "descripcion_problema", "diagnostico", "autorizacion_cliente", "observaciones",
        ]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select", "id": "id_cliente"}),
            "vehiculo": forms.Select(attrs={"class": "form-select", "id": "id_vehiculo"}),
            "tecnico_asignado": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "prioridad": forms.Select(attrs={"class": "form-select"}),
            "tipo_trabajo": forms.Select(attrs={"class": "form-select"}),
            "kilometraje_ingreso": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "fecha_estimada_entrega": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descripcion_problema": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Síntomas reportados por el cliente..."}),
            "diagnostico": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Diagnóstico técnico..."}),
            "autorizacion_cliente": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "El cliente autoriza los trabajos indicados..."}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cliente_id = None
        if self.data.get("cliente"):
            cliente_id = self.data.get("cliente")
        elif self.instance and self.instance.pk:
            cliente_id = self.instance.cliente_id
        elif self.initial.get("cliente"):
            cliente = self.initial.get("cliente")
            cliente_id = getattr(cliente, "pk", cliente)

        if cliente_id:
            self.fields["vehiculo"].queryset = Vehiculo.objects.filter(cliente_id=cliente_id, activo=True)
        else:
            self.fields["vehiculo"].queryset = Vehiculo.objects.none()

        for field_name, field in self.fields.items():
            if field.required:
                css = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = css + " is-required"

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        vehiculo = cleaned_data.get("vehiculo")
        if cliente and vehiculo and vehiculo.cliente_id != cliente.id:
            self.add_error("vehiculo", "Seleccione un vehículo perteneciente al cliente indicado.")
        return cleaned_data

    def clean_kilometraje_ingreso(self):
        km = self.cleaned_data.get("kilometraje_ingreso")
        if km is not None and km < 0:
            raise ValidationError("El kilometraje no puede ser negativo.")
        return km

    def clean_fecha_estimada_entrega(self):
        fecha = self.cleaned_data.get("fecha_estimada_entrega")
        if fecha:
            from datetime import date
            if fecha < date.today():
                raise ValidationError("La fecha estimada de entrega no puede ser anterior a hoy.")
        return fecha
