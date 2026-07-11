from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from apps.mixins import AdminRequeridoMixin
from .models import Usuario
from .forms import UsuarioCrearForm, UsuarioEditarForm, PerfilForm


@login_required
def lista(request):
    if not request.user.es_admin and not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    usuarios = Usuario.objects.filter(activo=True).order_by("rol", "last_name")
    return render(request, "usuarios/lista.html", {"usuarios": usuarios})


@login_required
def crear(request):
    if not request.user.es_admin and not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    if request.method == "POST":
        form = UsuarioCrearForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("usuarios:lista")
        else:
            for field, errors in form.errors.items():
                label = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(request, f"{label}: {error}")
    else:
        form = UsuarioCrearForm()
    return render(request, "usuarios/form.html", {"form": form, "titulo": "Nuevo usuario"})


@login_required
def editar(request, pk):
    if not request.user.es_admin and not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado.")
            return redirect("usuarios:lista")
        else:
            for field, errors in form.errors.items():
                label = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(request, f"{label}: {error}")
    else:
        form = UsuarioEditarForm(instance=usuario)
    return render(request, "usuarios/form.html", {"form": form, "titulo": "Editar usuario", "usuario": usuario})


@login_required
def perfil(request):
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("usuarios:perfil")
    else:
        form = PerfilForm(instance=request.user)
    return render(request, "usuarios/perfil.html", {"form": form})
