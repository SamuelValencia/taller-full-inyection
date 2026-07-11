from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from apps.decorators import admin_requerido
from apps.usuarios.models import Usuario
from .models import Rol, Modulo, Accion
from .forms import RolForm


@admin_requerido
def lista(request):
    roles = Rol.objects.prefetch_related("acciones", "usuarios").order_by("nombre")
    return render(request, "roles/lista.html", {"roles": roles})


@admin_requerido
def crear(request):
    modulos = Modulo.objects.prefetch_related("acciones").filter(activo=True)
    if request.method == "POST":
        form = RolForm(request.POST)
        if form.is_valid():
            rol = form.save()
            accion_ids = request.POST.getlist("acciones")
            rol.acciones.set(Accion.objects.filter(id__in=accion_ids))
            messages.success(request, f'Rol "{rol.nombre}" creado correctamente.')
            return redirect("roles:lista")
        for field, errors in form.errors.items():
            label = form.fields[field].label if field in form.fields else field
            for e in errors:
                messages.error(request, f"{label}: {e}")
    else:
        form = RolForm()
    return render(request, "roles/form.html", {
        "form": form, "modulos": modulos,
        "titulo": "Nuevo Rol", "acciones_seleccionadas": set(),
    })


@admin_requerido
def editar(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    modulos = Modulo.objects.prefetch_related("acciones").filter(activo=True)
    if request.method == "POST":
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            rol = form.save()
            accion_ids = request.POST.getlist("acciones")
            rol.acciones.set(Accion.objects.filter(id__in=accion_ids))
            messages.success(request, f'Rol "{rol.nombre}" actualizado.')
            return redirect("roles:lista")
        for field, errors in form.errors.items():
            label = form.fields[field].label if field in form.fields else field
            for e in errors:
                messages.error(request, f"{label}: {e}")
    else:
        form = RolForm(instance=rol)
    acciones_seleccionadas = set(rol.acciones.values_list("id", flat=True))
    return render(request, "roles/form.html", {
        "form": form, "modulos": modulos, "rol": rol,
        "titulo": f"Editar Rol: {rol.nombre}",
        "acciones_seleccionadas": acciones_seleccionadas,
    })


@admin_requerido
def eliminar(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method == "POST":
        if rol.es_sistema:
            messages.error(request, "Los roles de sistema no pueden eliminarse.")
            return redirect("roles:lista")
        if rol.usuarios.exists():
            messages.error(request, f'El rol "{rol.nombre}" tiene {rol.usuarios.count()} usuario(s) asignado(s). Reasígnalos antes de eliminar.')
            return redirect("roles:lista")
        nombre = rol.nombre
        rol.delete()
        messages.success(request, f'Rol "{nombre}" eliminado.')
        return redirect("roles:lista")
    return render(request, "roles/confirmar_eliminar.html", {"rol": rol})


@admin_requerido
def duplicar(request, pk):
    if request.method != "POST":
        return redirect("roles:lista")
    original = get_object_or_404(Rol, pk=pk)
    base_codigo = f"{original.codigo}_COPIA"
    codigo_final = base_codigo
    sufijo = 1
    while Rol.objects.filter(codigo=codigo_final).exists():
        codigo_final = f"{base_codigo}_{sufijo}"
        sufijo += 1
    nuevo = Rol.objects.create(
        codigo=codigo_final, nombre=f"{original.nombre} (Copia)",
        descripcion=original.descripcion, es_sistema=False, activo=True,
    )
    nuevo.acciones.set(original.acciones.all())
    messages.success(request, f'Rol duplicado como "{nuevo.nombre}". Puedes editarlo.')
    return redirect("roles:editar", pk=nuevo.pk)


@admin_requerido
def toggle_activo(request, pk):
    if request.method != "POST":
        return redirect("roles:lista")
    rol = get_object_or_404(Rol, pk=pk)
    if rol.es_sistema:
        messages.error(request, "Los roles de sistema no pueden desactivarse.")
    else:
        rol.activo = not rol.activo
        rol.save(update_fields=["activo"])
        estado = "activado" if rol.activo else "desactivado"
        messages.success(request, f'Rol "{rol.nombre}" {estado}.')
    return redirect("roles:lista")


@admin_requerido
def asignar_usuarios(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    todos_roles = Rol.objects.filter(activo=True).exclude(pk=pk)
    if request.method == "POST":
        usuario_ids = request.POST.getlist("usuario_ids")
        accion = request.POST.get("accion")
        if accion == "agregar":
            Usuario.objects.filter(pk__in=usuario_ids).update(rol=rol)
            messages.success(request, f"{len(usuario_ids)} usuario(s) asignado(s) al rol «{rol.nombre}».")
        elif accion == "mover":
            rol_destino_id = request.POST.get("rol_destino")
            if rol_destino_id:
                rol_destino = get_object_or_404(Rol, pk=rol_destino_id)
                Usuario.objects.filter(pk__in=usuario_ids, rol=rol).update(rol=rol_destino)
                messages.success(request, f"{len(usuario_ids)} usuario(s) movido(s) al rol «{rol_destino.nombre}».")
        return redirect("roles:asignar_usuarios", pk=pk)
    usuarios_con_rol = rol.usuarios.select_related("rol").order_by("last_name", "first_name")
    usuarios_disponibles = Usuario.objects.filter(activo=True).exclude(rol=rol).select_related("rol").order_by("last_name", "first_name")
    return render(request, "roles/asignar_usuarios.html", {
        "rol": rol,
        "usuarios_con_rol": usuarios_con_rol,
        "usuarios_disponibles": usuarios_disponibles,
        "todos_roles": todos_roles,
    })
