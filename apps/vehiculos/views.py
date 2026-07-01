from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from ..decorators import admin_o_recepcionista_requerido
from .models import Vehiculo
from .forms import VehiculoForm
from apps.clientes.models import Cliente


@admin_o_recepcionista_requerido
def lista(request):
    q = request.GET.get("q", "")
    vehiculos = Vehiculo.objects.filter(activo=True).select_related("cliente")
    if q:
        vehiculos = vehiculos.filter(
            Q(placa__icontains=q) | Q(marca__icontains=q) | Q(modelo__icontains=q) |
            Q(cliente__apellidos__icontains=q) | Q(numero_vin__icontains=q)
        )
    return render(request, "vehiculos/lista.html", {"vehiculos": vehiculos, "q": q})


@admin_o_recepcionista_requerido
def crear(request):
    cliente_id = request.GET.get("cliente")
    initial = {}
    if cliente_id:
        initial["cliente"] = cliente_id
    if request.method == "POST":
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                vehiculo = form.save()
                messages.success(request, f"Vehículo {vehiculo.placa} registrado correctamente.")
                return redirect("vehiculos:detalle", pk=vehiculo.pk)
            except Exception as e:
                messages.error(request, f"Error al registrar el vehículo: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = VehiculoForm(initial=initial)
    return render(request, "vehiculos/form.html", {"form": form, "titulo": "Registrar vehículo"})


@admin_o_recepcionista_requerido
def editar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        form = VehiculoForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Vehículo actualizado correctamente.")
                return redirect("vehiculos:detalle", pk=pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar el vehículo: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, "vehiculos/form.html", {"form": form, "titulo": "Editar vehículo", "vehiculo": vehiculo})


@admin_o_recepcionista_requerido
def detalle(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    ordenes = vehiculo.ordenes_trabajo.select_related("tecnico_asignado").order_by("-fecha_ingreso")[:10]
    historial = vehiculo.historial_mantenimiento.select_related("tipo_servicio", "tecnico").order_by("-fecha_servicio")[:10]
    programas = vehiculo.programas_mantenimiento.filter(activo=True).select_related("tipo_servicio")
    return render(request, "vehiculos/detalle.html", {
        "vehiculo": vehiculo, "ordenes": ordenes, "historial": historial, "programas": programas
    })


@admin_o_recepcionista_requerido
def eliminar(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == "POST":
        vehiculo.activo = False
        vehiculo.save()
        messages.success(request, f"Vehículo {vehiculo.placa} eliminado.")
        return redirect("vehiculos:lista")
    return render(request, "vehiculos/confirmar_eliminar.html", {"vehiculo": vehiculo})
