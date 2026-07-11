from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.roles.models import Rol
from .models import Usuario


class UsuarioCrearForm(UserCreationForm):
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.filter(activo=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Rol",
    )

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "rol", "telefono", "cedula", "especialidad"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "cedula": forms.TextInput(attrs={"class": "form-control"}),
            "especialidad": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"


class UsuarioEditarForm(forms.ModelForm):
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.filter(activo=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Rol",
    )

    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "rol", "telefono", "cedula", "especialidad", "activo"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "cedula": forms.TextInput(attrs={"class": "form-control"}),
            "especialidad": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "telefono"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
        }
