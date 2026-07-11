from django import forms
from .models import Rol


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ["codigo", "nombre", "descripcion", "activo"]
        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control text-uppercase",
                "placeholder": "EJEMPLO: SUPERVISOR",
                "style": "font-family: monospace;",
            }),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo", "").upper().strip()
        qs = Rol.objects.filter(codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un rol con ese código.")
        return codigo
