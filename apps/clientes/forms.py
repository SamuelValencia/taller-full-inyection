from django import forms
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["tipo_documento", "numero_documento", "nombres", "apellidos",
                  "telefono", "email", "direccion", "ciudad", "observaciones"]
        widgets = {
            "tipo_documento": forms.Select(attrs={"class": "form-select"}),
            "numero_documento": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "0912345678",
                "maxlength": "13"
            }),
            "nombres": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Nombres",
                "minlength": "2"
            }),
            "apellidos": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Apellidos",
                "minlength": "2"
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "0991234567",
                "maxlength": "10"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control", 
                "placeholder": "correo@ejemplo.com"
            }),
            "direccion": forms.Textarea(attrs={
                "class": "form-control", 
                "rows": 2,
                "minlength": "5"
            }),
            "ciudad": forms.TextInput(attrs={
                "class": "form-control",
                "minlength": "2"
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control", 
                "rows": 2
            }),
        }
        error_messages = {
            'numero_documento': {
                'unique': 'Ya existe un cliente con este numero de documento.',
                'required': 'El numero de documento es obligatorio.'
            },
            'telefono': {
                'required': 'El telefono es obligatorio.'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] += ' is-required'
            # Solo aplicar validacion de letras a campos de texto, no SELECT
            if field_name in ['nombres', 'apellidos']:
                field.validators.append(
                    RegexValidator(
                        regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                        message='Este campo solo debe contener letras y espacios.'
                    )
                )

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento', '').strip()
        tipo_documento = self.cleaned_data.get('tipo_documento', '')

        if not numero_documento:
            raise ValidationError('El número de documento es obligatorio.')

        if tipo_documento == 'PASAPORTE':
            # Pasaporte: letras y números, sin espacios
            import re
            if not re.match(r'^[a-zA-Z0-9]+$', numero_documento):
                raise ValidationError('El pasaporte solo debe contener letras y números, sin espacios.')
        else:
            # Cédula y RUC: solo dígitos
            if not numero_documento.isdigit():
                raise ValidationError('El número de documento solo debe contener dígitos.')
            if tipo_documento == 'CEDULA' and len(numero_documento) != 10:
                raise ValidationError('La cédula debe tener exactamente 10 dígitos.')
            if tipo_documento == 'RUC' and len(numero_documento) != 13:
                raise ValidationError('El RUC debe tener exactamente 13 dígitos.')

        return numero_documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and len(telefono) != 10:
            raise ValidationError('El telefono debe tener 10 digitos.')
        if telefono and not telefono.isdigit():
            raise ValidationError('El telefono solo debe contener digitos.')
        return telefono

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validator = EmailValidator()
            try:
                validator(email)
            except ValidationError:
                raise ValidationError('Ingrese un correo electronico valido.')
        return email

    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if nombres and len(nombres.strip()) < 2:
            raise ValidationError('Los nombres deben tener al menos 2 caracteres.')
        return nombres.strip() if nombres else nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if apellidos and len(apellidos.strip()) < 2:
            raise ValidationError('Los apellidos deben tener al menos 2 caracteres.')
        return apellidos.strip() if apellidos else apellidos
