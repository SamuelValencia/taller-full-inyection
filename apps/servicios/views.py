from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.decorators import admin_o_recepcionista_requerido
from .forms import ServicioForm
from .models import Servicio


@admin_o_recepcionista_requerido
def lista(request):
    q = request.GET.get("q", "")
    servicios = Servicio.objects.all()
    if q:
        servicios = servicios.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    return render(request, "servicios/lista.html", {"servicios": servicios, "q": q})


@admin_o_recepcionista_requerido
def crear(request):
    if request.method == "POST":
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio creado correctamente.")
            return redirect("servicios:lista")
    else:
        form = ServicioForm()
    return render(request, "servicios/form.html", {"form": form, "titulo": "Nuevo servicio"})


@admin_o_recepcionista_requerido
def editar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == "POST":
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado correctamente.")
            return redirect("servicios:lista")
    else:
        form = ServicioForm(instance=servicio)
    return render(request, "servicios/form.html", {"form": form, "titulo": "Editar servicio", "servicio": servicio})


def catalogo_json(request):
    """Devuelve los servicios activos agrupados por categoría para el modal de selección."""
    q = request.GET.get("q", "")
    categoria = request.GET.get("categoria", "")
    servicios = Servicio.objects.filter(estado=True)
    if q:
        servicios = servicios.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if categoria:
        servicios = servicios.filter(categoria=categoria)
    data = [
        {
            "id": s.id,
            "nombre": s.nombre,
            "categoria": s.get_categoria_display(),
            "categoria_key": s.categoria,
            "descripcion": s.descripcion,
        }
        for s in servicios.order_by("categoria", "nombre")
    ]
    categorias = [{"key": k, "label": v} for k, v in Servicio.Categoria.choices]
    return JsonResponse({"servicios": data, "categorias": categorias})


@admin_o_recepcionista_requerido
def eliminar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == "POST":
        servicio.estado = False
        servicio.save(update_fields=["estado"])
        messages.success(request, "Servicio desactivado correctamente.")
        return redirect("servicios:lista")
    return render(request, "servicios/confirmar_eliminar.html", {"servicio": servicio})
