from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from ..decorators import admin_o_recepcionista_requerido
from .models import Cotizacion, DetalleCotizacion
from .forms import CotizacionForm


@admin_o_recepcionista_requerido
def lista(request):
    estado_filtro = request.GET.get("estado", "")
    cotizaciones = Cotizacion.objects.select_related("cliente", "vehiculo").order_by("-fecha_creacion")
    if estado_filtro:
        cotizaciones = cotizaciones.filter(estado=estado_filtro)
    return render(request, "cotizaciones/lista.html", {
        "cotizaciones": cotizaciones,
        "estado_filtro": estado_filtro,
        "estados": Cotizacion.Estado.choices,
    })


@admin_o_recepcionista_requerido
def crear(request):
    if request.method == "POST":
        form = CotizacionForm(request.POST)
        if form.is_valid():
            try:
                cot = form.save(commit=False)
                cot.elaborado_por = request.user
                cot.save()
                messages.success(request, f"Cotización {cot.numero_cotizacion} creada.")
                return redirect("cotizaciones:detalle", pk=cot.pk)
            except Exception as e:
                messages.error(request, f"Error al crear la cotización: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CotizacionForm()
    return render(request, "cotizaciones/form.html", {"form": form, "titulo": "Nueva cotización"})


@admin_o_recepcionista_requerido
def editar(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if request.method == "POST":
        form = CotizacionForm(request.POST, instance=cot)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cotización actualizada.")
                return redirect("cotizaciones:detalle", pk=pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar la cotización: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CotizacionForm(instance=cot)
    return render(request, "cotizaciones/form.html", {"form": form, "titulo": "Editar cotización", "cotizacion": cot})


@admin_o_recepcionista_requerido
def detalle(request, pk):
    from apps.servicios.models import Servicio
    cot = get_object_or_404(Cotizacion.objects.select_related("cliente", "vehiculo", "elaborado_por"), pk=pk)
    detalles = cot.detalles.select_related("servicio").all()
    servicios_catalogo = Servicio.objects.filter(estado=True).order_by("categoria", "nombre")
    # IDs de servicios ya agregados (para validación de duplicados JS)
    servicios_agregados_ids = list(
        detalles.filter(tipo="SERVICIO", servicio__isnull=False).values_list("servicio_id", flat=True)
    )
    return render(request, "cotizaciones/detalle.html", {
        "cotizacion": cot,
        "detalles": detalles,
        "servicios_catalogo": servicios_catalogo,
        "servicios_agregados_ids": servicios_agregados_ids,
    })


@admin_o_recepcionista_requerido
def aprobar(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "aprobar":
            cot.estado = "APROBADA"
            cot.fecha_aprobacion = timezone.now()
            cot.save()
            messages.success(request, "Cotización aprobada.")
        elif accion == "rechazar":
            cot.estado = "RECHAZADA"
            cot.save()
            messages.warning(request, "Cotización rechazada.")
        elif accion == "borrador":
            cot.estado = "BORRADOR"
            cot.save()
            messages.info(request, "Cotización regresada a borrador.")
    return redirect("cotizaciones:detalle", pk=pk)


@admin_o_recepcionista_requerido
def agregar_servicio(request, pk):
    """Agrega un servicio del catálogo a la cotización."""
    from apps.servicios.models import Servicio
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado not in ("BORRADOR", "ENVIADA"):
        messages.error(request, "Solo se pueden agregar ítems a cotizaciones en borrador o enviada.")
        return redirect("cotizaciones:detalle", pk=pk)
    if request.method == "POST":
        servicio_id = request.POST.get("servicio")
        try:
            precio_unitario = Decimal(request.POST.get("precio_unitario", "0"))
            cantidad = int(request.POST.get("cantidad", "1"))
        except (ValueError, Exception):
            messages.error(request, "Precio o cantidad inválidos.")
            return redirect("cotizaciones:detalle", pk=pk)

        if not servicio_id:
            messages.error(request, "Debe seleccionar un servicio del catálogo.")
            return redirect("cotizaciones:detalle", pk=pk)
        servicio = get_object_or_404(Servicio, pk=servicio_id, estado=True)

        if cot.detalles.filter(servicio=servicio).exists():
            messages.error(request, f"El servicio «{servicio.nombre}» ya fue agregado a esta cotización.")
            return redirect("cotizaciones:detalle", pk=pk)
        if cantidad < 1:
            messages.error(request, "La cantidad debe ser un número entero positivo.")
            return redirect("cotizaciones:detalle", pk=pk)
        if precio_unitario < 0:
            messages.error(request, "El precio unitario no puede ser negativo.")
            return redirect("cotizaciones:detalle", pk=pk)

        DetalleCotizacion.objects.create(
            cotizacion=cot, tipo="SERVICIO",
            servicio=servicio, descripcion=servicio.nombre,
            cantidad=cantidad, precio_unitario=precio_unitario,
        )
        messages.success(request, f"Servicio «{servicio.nombre}» agregado.")
    return redirect("cotizaciones:detalle", pk=pk)


@admin_o_recepcionista_requerido
def agregar_repuesto(request, pk):
    """Agrega un repuesto/material con texto libre a la cotización."""
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado not in ("BORRADOR", "ENVIADA"):
        messages.error(request, "Solo se pueden agregar ítems a cotizaciones en borrador o enviada.")
        return redirect("cotizaciones:detalle", pk=pk)
    if request.method == "POST":
        descripcion = request.POST.get("descripcion", "").strip()
        try:
            precio_unitario = Decimal(request.POST.get("precio_unitario", "0"))
            cantidad = int(request.POST.get("cantidad", "1"))
        except (ValueError, Exception):
            messages.error(request, "Precio o cantidad inválidos.")
            return redirect("cotizaciones:detalle", pk=pk)

        if not descripcion:
            messages.error(request, "Ingrese la descripción del repuesto.")
            return redirect("cotizaciones:detalle", pk=pk)
        if cantidad < 1:
            messages.error(request, "La cantidad debe ser un número entero positivo.")
            return redirect("cotizaciones:detalle", pk=pk)
        if precio_unitario < 0:
            messages.error(request, "El precio unitario no puede ser negativo.")
            return redirect("cotizaciones:detalle", pk=pk)

        DetalleCotizacion.objects.create(
            cotizacion=cot, tipo="REPUESTO",
            descripcion=descripcion,
            cantidad=cantidad, precio_unitario=precio_unitario,
        )
        messages.success(request, f"Repuesto «{descripcion}» agregado.")
    return redirect("cotizaciones:detalle", pk=pk)


@admin_o_recepcionista_requerido
def eliminar_detalle(request, pk, det_pk):
    det = get_object_or_404(DetalleCotizacion, pk=det_pk, cotizacion__pk=pk)
    if request.method == "POST":
        det.delete()
        messages.success(request, "Ítem eliminado.")
    return redirect("cotizaciones:detalle", pk=pk)


@admin_o_recepcionista_requerido
def convertir_orden(request, pk):
    from apps.ordenes.models import OrdenTrabajo, DetalleOrdenTrabajo
    cot = get_object_or_404(Cotizacion, pk=pk, estado="APROBADA")
    if not cot.orden_generada:
        orden = OrdenTrabajo.objects.create(
            vehiculo=cot.vehiculo,
            cliente=cot.cliente,
            recepcionista=request.user,
            descripcion_problema=cot.descripcion or "Generada desde cotización aprobada",
            observaciones=cot.observaciones or "",
            descuento=cot.descuento,
        )
        for d in cot.detalles.select_related("servicio").all():
            DetalleOrdenTrabajo.objects.create(
                orden=orden, tipo=d.tipo,
                servicio=d.servicio,
                descripcion=d.descripcion,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
            )
        servicios = sum(det.subtotal for det in orden.detalles.filter(tipo="SERVICIO"))
        repuestos = sum(det.subtotal for det in orden.detalles.filter(tipo="REPUESTO"))
        orden.costo_mano_obra = servicios
        orden.costo_repuestos = repuestos
        orden.save(update_fields=["costo_mano_obra", "costo_repuestos"])
        cot.orden_generada = orden
        cot.save(update_fields=["orden_generada"])
        messages.success(request, f"Orden de Trabajo {orden.numero_orden} generada desde la cotización.")
        return redirect("ordenes:detalle", pk=orden.pk)
    messages.info(request, "Esta cotización ya tiene una Orden de Trabajo generada.")
    return redirect("cotizaciones:detalle", pk=pk)


@admin_o_recepcionista_requerido
def pdf(request, pk):
    from django.http import HttpResponse
    from django.template.loader import get_template
    from xhtml2pdf import pisa
    from django.conf import settings
    from io import BytesIO
    cot = get_object_or_404(Cotizacion.objects.select_related("cliente", "vehiculo", "elaborado_por"), pk=pk)
    detalles = cot.detalles.select_related("servicio").all()
    template = get_template("cotizaciones/cotizacion_pdf.html")
    html = template.render({
        "cotizacion": cot,
        "detalles": detalles,
        "taller_nombre": getattr(settings, "TALLER_NOMBRE", "Fuel Injection"),
        "taller_telefono": getattr(settings, "TALLER_TELEFONO", ""),
        "taller_direccion": getattr(settings, "TALLER_DIRECCION", ""),
    })
    result = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="proforma-{cot.numero_cotizacion}.pdf"'
    return response
