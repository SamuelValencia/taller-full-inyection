from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from ..decorators import admin_o_recepcionista_requerido, admin_o_mecanico_requerido, rol_autenticado_requerido
from .models import TipoServicioMantenimiento, ProgramaMantenimiento, HistorialMantenimiento
from .forms import ProgramaMantenimientoForm, HistorialMantenimientoForm, TipoServicioForm


@rol_autenticado_requerido
def lista(request):
    programas = ProgramaMantenimiento.objects.filter(activo=True).select_related("vehiculo", "tipo_servicio").order_by("proxima_fecha", "proximo_km")
    return render(request, "mantenimiento/lista.html", {"programas": programas})


@admin_o_recepcionista_requerido
def crear_programa(request):
    if request.method == "POST":
        form = ProgramaMantenimientoForm(request.POST)
        if form.is_valid():
            try:
                p = form.save()
                p.actualizar_proximo()
                p.save()
                messages.success(request, "Programa de mantenimiento creado.")
                return redirect("mantenimiento:lista")
            except Exception as e:
                messages.error(request, f"Error al crear el programa: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProgramaMantenimientoForm()
    return render(request, "mantenimiento/form_programa.html", {"form": form, "titulo": "Nuevo programa de mantenimiento"})


@admin_o_recepcionista_requerido
def editar_programa(request, pk):
    programa = get_object_or_404(ProgramaMantenimiento, pk=pk)
    if request.method == "POST":
        form = ProgramaMantenimientoForm(request.POST, instance=programa)
        if form.is_valid():
            try:
                p = form.save()
                p.actualizar_proximo()
                p.save()
                messages.success(request, "Programa actualizado.")
                return redirect("mantenimiento:lista")
            except Exception as e:
                messages.error(request, f"Error al actualizar el programa: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProgramaMantenimientoForm(instance=programa)
    return render(request, "mantenimiento/form_programa.html", {"form": form, "titulo": "Editar programa", "programa": programa})


@admin_o_mecanico_requerido
def registrar_historial(request):
    if request.method == "POST":
        form = HistorialMantenimientoForm(request.POST)
        if form.is_valid():
            try:
                h = form.save(commit=False)
                h.tecnico = request.user
                h.save()
                # Actualizar programa
                prog = ProgramaMantenimiento.objects.filter(
                    vehiculo=h.vehiculo, tipo_servicio=h.tipo_servicio
                ).first()
                if prog:
                    prog.ultimo_km = h.km_al_servicio
                    prog.ultima_fecha = h.fecha_servicio
                    prog.actualizar_proximo()
                    prog.estado = "AL_DIA"
                    prog.save()
                # Actualizar km vehiculo
                if h.km_al_servicio > h.vehiculo.kilometraje_actual:
                    h.vehiculo.kilometraje_actual = h.km_al_servicio
                    h.vehiculo.save(update_fields=["kilometraje_actual"])
                messages.success(request, "Historial registrado correctamente.")
                return redirect("vehiculos:detalle", pk=h.vehiculo.pk)
            except Exception as e:
                messages.error(request, f"Error al registrar el historial: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = HistorialMantenimientoForm()
    return render(request, "mantenimiento/form_historial.html", {"form": form, "titulo": "Registrar mantenimiento"})


@admin_o_recepcionista_requerido
def tipos_servicio(request):
    tipos = TipoServicioMantenimiento.objects.filter(activo=True)
    return render(request, "mantenimiento/tipos.html", {"tipos": tipos})


@admin_o_recepcionista_requerido
def crear_tipo(request):
    if request.method == "POST":
        form = TipoServicioForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Tipo de servicio creado.")
                return redirect("mantenimiento:tipos")
            except Exception as e:
                messages.error(request, f"Error al crear el tipo: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TipoServicioForm()
    return render(request, "mantenimiento/form_tipo.html", {"form": form, "titulo": "Nuevo tipo de servicio"})
