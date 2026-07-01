from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ["cliente", "placa", "marca", "modelo", "anio", "color", "tipo_vehiculo",
                  "tipo_combustible", "numero_vin", "numero_motor", "kilometraje_actual",
                  "cilindraje", "transmision", "observaciones"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "placa": forms.TextInput(attrs={"class": "form-control text-uppercase", "placeholder": "ABC-1234", "maxlength": 10}),
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": "Toyota", "minlength": 2}),
            "modelo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Corolla", "minlength": 2}),
            "anio": forms.NumberInput(attrs={"class": "form-control", "min": 1950, "max": 2030}),
            "color": forms.TextInput(attrs={"class": "form-control", "minlength": 2}),
            "tipo_vehiculo": forms.Select(attrs={"class": "form-select"}),
            "tipo_combustible": forms.Select(attrs={"class": "form-select"}),
            "numero_vin": forms.TextInput(attrs={"class": "form-control text-uppercase", "maxlength": 17}),
            "numero_motor": forms.TextInput(attrs={"class": "form-control"}),
            "kilometraje_actual": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "cilindraje": forms.TextInput(attrs={"class": "form-control", "placeholder": "1600cc"}),
            "transmision": forms.Select(attrs={"class": "form-select"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] += ' is-required'
            # Solo aplicar validacion de letras a campos de texto, no SELECT ni NUMBER
            if field_name in ['marca', 'modelo', 'color']:
                field.validators.append(
                    RegexValidator(
                        regex=r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-]+$',
                        message='Este campo solo debe contener letras, numeros y espacios.'
                    )
                )

    def clean_placa(self):
        placa = self.cleaned_data.get('placa')
        if placa:
            placa = placa.upper()
            if len(placa) < 6 or len(placa) > 10:
                raise ValidationError('La placa debe tener entre 6 y 10 caracteres.')
        return placa

    def clean_anio(self):
        anio = self.cleaned_data.get('anio')
        if anio:
            from datetime import date
            current_year = date.today().year
            if anio < 1950 or anio > current_year + 1:
                raise ValidationError(f'El ano debe estar entre 1950 y {current_year + 1}.')
        return anio

    def clean_kilometraje_actual(self):
        kilometraje = self.cleaned_data.get('kilometraje_actual')
        if kilometraje is not None and kilometraje < 0:
            raise ValidationError('El kilometraje no puede ser negativo.')
        return kilometraje

    def clean_numero_vin(self):
        vin = self.cleaned_data.get('numero_vin')
        if vin:
            if len(vin) != 17:
                raise ValidationError('El VIN debe tener 17 caracteres.')
            if not vin.isalnum():
                raise ValidationError('El VIN solo debe contener letras y numeros.')
        return vin.upper() if vin else vin
