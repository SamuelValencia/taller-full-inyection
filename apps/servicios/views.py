from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.decorators import admin_o_recepcionista_requerido
from .forms import ServicioForm
from .models import Servicio, ServicioRepuesto


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


def repuestos_sugeridos_json(request, pk):
    """Devuelve los repuestos sugeridos de un servicio (para AJAX en orden de trabajo)."""
    servicio = get_object_or_404(Servicio, pk=pk, estado=True)
    sugeridos = (
        ServicioRepuesto.objects
        .filter(servicio=servicio)
        .select_related("repuesto", "repuesto__categoria")
    )
    data = []
    for sr in sugeridos:
        r = sr.repuesto
        data.append({
            "repuesto_id": r.id,
            "nombre": r.nombre,
            "codigo": r.codigo,
            "marca": r.marca or "",
            "categoria": r.categoria.nombre if r.categoria else "",
            "cantidad_sugerida": float(sr.cantidad_sugerida),
            "precio_unitario": float(r.precio_venta or 0),
            "stock_actual": float(r.stock_actual),
            "stock_bajo": r.stock_bajo,
            "opcional": sr.opcional,
            "nota": sr.nota,
        })
    return JsonResponse({"servicio": servicio.nombre, "repuestos": data})


@admin_o_recepcionista_requerido
def gestionar_repuestos(request, pk):
    """Gestiona el catálogo de repuestos sugeridos para un servicio."""
    from apps.inventario.models import Repuesto
    servicio = get_object_or_404(Servicio, pk=pk)
    sugeridos = servicio.repuestos_sugeridos.select_related("repuesto", "repuesto__categoria")

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "agregar":
            repuesto_id = request.POST.get("repuesto_id")
            cantidad = request.POST.get("cantidad_sugerida", "1")
            opcional = request.POST.get("opcional") == "on"
            nota = request.POST.get("nota", "").strip()
            repuesto = get_object_or_404(Repuesto, pk=repuesto_id)
            try:
                cantidad = float(cantidad)
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                messages.error(request, "Cantidad inválida.")
                return redirect("servicios:gestionar_repuestos", pk=pk)
            obj, created = ServicioRepuesto.objects.update_or_create(
                servicio=servicio, repuesto=repuesto,
                defaults={"cantidad_sugerida": cantidad, "opcional": opcional, "nota": nota},
            )
            msg = "agregado" if created else "actualizado"
            messages.success(request, f"Repuesto «{repuesto.nombre}» {msg}.")

        elif accion == "eliminar":
            sr_id = request.POST.get("sr_id")
            ServicioRepuesto.objects.filter(pk=sr_id, servicio=servicio).delete()
            messages.success(request, "Repuesto sugerido eliminado.")

        return redirect("servicios:gestionar_repuestos", pk=pk)

    repuestos_disponibles = Repuesto.objects.filter(activo=True).order_by("nombre")
    repuestos_ya_ids = set(sugeridos.values_list("repuesto_id", flat=True))
    return render(request, "servicios/repuestos_sugeridos.html", {
        "servicio": servicio,
        "sugeridos": sugeridos,
        "repuestos_disponibles": repuestos_disponibles,
        "repuestos_ya_ids": repuestos_ya_ids,
    })


@admin_o_recepcionista_requerido
def eliminar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == "POST":
        servicio.estado = False
        servicio.save(update_fields=["estado"])
        messages.success(request, "Servicio desactivado correctamente.")
        return redirect("servicios:lista")
    return render(request, "servicios/confirmar_eliminar.html", {"servicio": servicio})
