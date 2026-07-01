from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from ..decorators import admin_o_recepcionista_requerido
from .models import Cliente
from .forms import ClienteForm


@admin_o_recepcionista_requerido
def lista(request):
    q = request.GET.get("q", "")
    clientes = Cliente.objects.filter(activo=True)
    if q:
        clientes = clientes.filter(
            Q(nombres__icontains=q) | Q(apellidos__icontains=q) |
            Q(numero_documento__icontains=q) | Q(telefono__icontains=q)
        )
    return render(request, "clientes/lista.html", {"clientes": clientes, "q": q})


@admin_o_recepcionista_requerido
def crear(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cliente registrado correctamente.")
                return redirect("clientes:lista")
            except Exception as e:
                messages.error(request, f"Error al registrar el cliente: {str(e)}")
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClienteForm()
    return render(request, "clientes/form.html", {"form": form, "titulo": "Nuevo cliente"})


@admin_o_recepcionista_requerido
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cliente actualizado correctamente.")
                return redirect("clientes:detalle", pk=pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar el cliente: {str(e)}")
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "clientes/form.html", {"form": form, "titulo": "Editar cliente", "cliente": cliente})


@admin_o_recepcionista_requerido
def detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    vehiculos = cliente.vehiculos.filter(activo=True).prefetch_related("ordenes_trabajo")
    ordenes = cliente.ordenes_trabajo.select_related("vehiculo", "tecnico_asignado").order_by("-fecha_ingreso")[:10]
    return render(request, "clientes/detalle.html", {"cliente": cliente, "vehiculos": vehiculos, "ordenes": ordenes})


@admin_o_recepcionista_requerido
def eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        cliente.activo = False
        cliente.save()
        messages.success(request, f"Cliente {cliente.nombre_completo} eliminado.")
        return redirect("clientes:lista")
    return render(request, "clientes/confirmar_eliminar.html", {"cliente": cliente})
