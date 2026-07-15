from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone

from ..decorators import admin_o_recepcionista_requerido, admin_o_mecanico_requerido, rol_autenticado_requerido
from .models import OrdenTrabajo, DetalleOrdenTrabajo
from .forms import OrdenTrabajoForm
from apps.vehiculos.models import Vehiculo
from apps.alertas.models import Alerta


@rol_autenticado_requerido
def lista(request):
    estado = request.GET.get("estado", "")
    q = request.GET.get("q", "")
    ordenes = OrdenTrabajo.objects.select_related("vehiculo", "cliente", "tecnico_asignado")
    if estado:
        ordenes = ordenes.filter(estado=estado)
    if q:
        ordenes = ordenes.filter(
            Q(numero_orden__icontains=q) | Q(vehiculo__placa__icontains=q) |
            Q(cliente__apellidos__icontains=q) | Q(cliente__nombres__icontains=q)
        )
    ordenes = ordenes.order_by("-fecha_ingreso")
    return render(request, "ordenes/lista.html", {
        "ordenes": ordenes, "estado": estado, "q": q,
        "estados": OrdenTrabajo.Estado.choices,
    })


@admin_o_recepcionista_requerido
def crear(request):
    user = request.user
    cotizacion_pk = request.GET.get("cotizacion")
    vehiculo_id = request.GET.get("vehiculo")
    initial = {}
    cotizacion = None

    # Enforcement del flujo: recepcionistas deben venir desde una cotización aprobada
    if user.rol_codigo == "RECEPCIONISTA" and not cotizacion_pk:
        from apps.cotizaciones.models import Cotizacion
        cotizaciones_aprobadas = Cotizacion.objects.filter(
            estado="APROBADA", orden_generada__isnull=True
        ).select_related("cliente", "vehiculo").order_by("-fecha_aprobacion")
        messages.info(request, "Seleccione una cotización aprobada para generar la Orden de Trabajo.")
        return render(request, "ordenes/seleccionar_cotizacion.html", {
            "cotizaciones": cotizaciones_aprobadas,
        })

    # Pre-cargar datos desde cotización aprobada
    if cotizacion_pk:
        from apps.cotizaciones.models import Cotizacion
        cotizacion = get_object_or_404(Cotizacion, pk=cotizacion_pk, estado="APROBADA")
        initial = {
            "cliente": cotizacion.cliente,
            "vehiculo": cotizacion.vehiculo,
            "kilometraje_ingreso": cotizacion.vehiculo.kilometraje_actual,
        }
    elif vehiculo_id:
        v = Vehiculo.objects.filter(pk=vehiculo_id).first()
        if v:
            initial = {"vehiculo": v, "cliente": v.cliente, "kilometraje_ingreso": v.kilometraje_actual}

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            try:
                orden = form.save(commit=False)
                orden.recepcionista = request.user
                orden.save()
                if orden.kilometraje_ingreso > orden.vehiculo.kilometraje_actual:
                    orden.vehiculo.kilometraje_actual = orden.kilometraje_ingreso
                    orden.vehiculo.save(update_fields=["kilometraje_actual"])
                # Copiar detalles desde cotización si viene de una
                if cotizacion_pk:
                    from apps.cotizaciones.models import Cotizacion
                    cot = Cotizacion.objects.filter(pk=cotizacion_pk, estado="APROBADA").first()
                    if cot and not cot.orden_generada:
                        for d in cot.detalles.select_related("servicio").all():
                            DetalleOrdenTrabajo.objects.create(
                                orden=orden, tipo=d.tipo,
                                servicio=d.servicio, descripcion=d.descripcion,
                                cantidad=d.cantidad, precio_unitario=d.precio_unitario,
                            )
                        servicios = sum(det.subtotal for det in orden.detalles.filter(tipo="SERVICIO"))
                        repuestos = sum(det.subtotal for det in orden.detalles.filter(tipo="REPUESTO"))
                        orden.costo_mano_obra = servicios
                        orden.costo_repuestos = repuestos
                        orden.descuento = cot.descuento
                        orden.save(update_fields=["costo_mano_obra", "costo_repuestos", "descuento"])
                        cot.orden_generada = orden
                        cot.save(update_fields=["orden_generada"])
                messages.success(request, f"Orden de Trabajo {orden.numero_orden} creada correctamente.")
                return redirect("ordenes:detalle", pk=orden.pk)
            except Exception as e:
                messages.error(request, f"Error al crear la orden: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = OrdenTrabajoForm(initial=initial)

    return render(request, "ordenes/form.html", {
        "form": form, "titulo": "Nueva Orden de Trabajo",
        "cotizacion": cotizacion,
    })


@admin_o_recepcionista_requerido
def editar(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            try:
                orden = form.save()
                if orden.estado == "ENTREGADA" and not orden.fecha_entrega_real:
                    orden.fecha_entrega_real = timezone.now()
                    orden.save(update_fields=["fecha_entrega_real"])
                messages.success(request, "Orden de Trabajo actualizada correctamente.")
                return redirect("ordenes:detalle", pk=pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar la orden: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "ordenes/form.html", {"form": form, "titulo": "Editar Orden de Trabajo", "orden": orden})


@rol_autenticado_requerido
def detalle(request, pk):
    from apps.servicios.models import Servicio
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related("vehiculo", "cliente", "tecnico_asignado", "recepcionista"),
        pk=pk,
    )
    detalles = orden.detalles.select_related("servicio").all()
    # Sanear costos almacenados por si están desactualizados (datos viejos)
    _recalcular_costos(orden)
    servicios_catalogo = Servicio.objects.filter(estado=True).order_by("categoria", "nombre")
    servicios_agregados_ids = list(
        detalles.filter(tipo="SERVICIO", servicio__isnull=False).values_list("servicio_id", flat=True)
    )
    return render(request, "ordenes/detalle.html", {
        "orden": orden,
        "detalles": detalles,
        "estados": OrdenTrabajo.Estado.choices,
        "servicios_catalogo": servicios_catalogo,
        "servicios_agregados_ids": servicios_agregados_ids,
    })


@admin_o_mecanico_requerido
def cambiar_estado(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        if nuevo_estado not in dict(OrdenTrabajo.Estado.choices):
            return redirect("ordenes:detalle", pk=pk)

        # Cuando se pasa a FINALIZADA, mostrar formulario de cierre
        if nuevo_estado == "FINALIZADA" and orden.estado != "FINALIZADA":
            return redirect("ordenes:formulario_finalizar", pk=pk)

        orden.estado = nuevo_estado
        if nuevo_estado == "ENTREGADA":
            orden.fecha_entrega_real = timezone.now()
            if orden.recepcionista:
                Alerta.objects.create(
                    tipo=Alerta.TipoAlerta.VEHICULO_LISTO,
                    nivel=Alerta.Nivel.INFO,
                    vehiculo=orden.vehiculo,
                    orden=orden,
                    mensaje=f"El vehiculo {orden.vehiculo.placa} ha sido entregado. Orden: {orden.numero_orden}",
                    destinatario=orden.recepcionista,
                )
        orden.save()
        messages.success(request, f"Estado actualizado a: {orden.get_estado_display()}")
    return redirect("ordenes:detalle", pk=pk)


@admin_o_mecanico_requerido
def formulario_finalizar(request, pk):
    """
    Formulario de cierre que se muestra antes de marcar una OT como FINALIZADA.
    Permite configurar el recordatorio de mantenimiento preventivo.
    """
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    if orden.estado == "FINALIZADA":
        messages.info(request, "Esta orden ya está finalizada.")
        return redirect("ordenes:detalle", pk=pk)

    if request.method == "POST":
        requiere = request.POST.get("requiere_recordatorio") == "on"
        orden.requiere_recordatorio = requiere

        if requiere:
            try:
                dias = int(request.POST.get("intervalo_dias_recordatorio") or 0)
                km = int(request.POST.get("intervalo_km_recordatorio") or 0)
            except ValueError:
                messages.error(request, "Los intervalos deben ser numeros enteros.")
                return render(request, "ordenes/formulario_finalizar.html", {"orden": orden})

            if not dias and not km:
                messages.error(request, "Debe indicar al menos un intervalo (dias o km) para el recordatorio.")
                return render(request, "ordenes/formulario_finalizar.html", {"orden": orden})

            orden.intervalo_dias_recordatorio = dias or None
            orden.intervalo_km_recordatorio = km or None
            orden.canal_recordatorio = request.POST.get("canal_recordatorio", "EMAIL")

        orden.estado = OrdenTrabajo.Estado.FINALIZADA
        orden.save()
        messages.success(
            request,
            f"Orden {orden.numero_orden} finalizada."
            + (" Se programó recordatorio de mantenimiento para el cliente." if requiere else "")
        )
        return redirect("ordenes:detalle", pk=pk)

    return render(request, "ordenes/formulario_finalizar.html", {"orden": orden})


@admin_o_mecanico_requerido
def agregar_servicio(request, pk):
    """Agrega un servicio del catálogo a la orden de trabajo."""
    from apps.servicios.models import Servicio
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        servicio_id = request.POST.get("servicio")
        try:
            precio_unitario = Decimal(request.POST.get("precio_unitario", "0"))
            cantidad = int(request.POST.get("cantidad", "1"))
        except (ValueError, Exception):
            messages.error(request, "Precio o cantidad inválidos.")
            return redirect("ordenes:detalle", pk=pk)

        if not servicio_id:
            messages.error(request, "Debe seleccionar un servicio del catálogo.")
            return redirect("ordenes:detalle", pk=pk)
        servicio = get_object_or_404(Servicio, pk=servicio_id, estado=True)

        if orden.detalles.filter(servicio=servicio).exists():
            messages.error(request, f"El servicio «{servicio.nombre}» ya fue agregado a esta orden.")
            return redirect("ordenes:detalle", pk=pk)
        if cantidad < 1:
            messages.error(request, "La cantidad debe ser un número entero positivo.")
            return redirect("ordenes:detalle", pk=pk)
        if precio_unitario < 0:
            messages.error(request, "El precio unitario no puede ser negativo.")
            return redirect("ordenes:detalle", pk=pk)

        DetalleOrdenTrabajo.objects.create(
            orden=orden, tipo="SERVICIO",
            servicio=servicio, descripcion=servicio.nombre,
            cantidad=cantidad, precio_unitario=precio_unitario,
        )
        _recalcular_costos(orden)
        messages.success(request, f"Servicio «{servicio.nombre}» agregado.")
    return redirect("ordenes:detalle", pk=pk)


@admin_o_mecanico_requerido
def agregar_repuesto(request, pk):
    """Agrega un repuesto/material con texto libre a la orden de trabajo."""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        descripcion = request.POST.get("descripcion", "").strip()
        try:
            precio_unitario = Decimal(request.POST.get("precio_unitario", "0"))
            cantidad = int(request.POST.get("cantidad", "1"))
        except (ValueError, Exception):
            messages.error(request, "Precio o cantidad inválidos.")
            return redirect("ordenes:detalle", pk=pk)

        if not descripcion:
            messages.error(request, "Ingrese la descripción del repuesto.")
            return redirect("ordenes:detalle", pk=pk)
        if cantidad < 1:
            messages.error(request, "La cantidad debe ser un número entero positivo.")
            return redirect("ordenes:detalle", pk=pk)
        if precio_unitario < 0:
            messages.error(request, "El precio unitario no puede ser negativo.")
            return redirect("ordenes:detalle", pk=pk)

        DetalleOrdenTrabajo.objects.create(
            orden=orden, tipo="REPUESTO",
            descripcion=descripcion,
            cantidad=cantidad, precio_unitario=precio_unitario,
        )
        _recalcular_costos(orden)
        messages.success(request, f"Repuesto «{descripcion}» agregado.")
    return redirect("ordenes:detalle", pk=pk)


@admin_o_mecanico_requerido
def agregar_repuestos_sugeridos(request, pk):
    """Recibe la selección del mecánico y agrega los repuestos sugeridos a la orden."""
    from apps.inventario.models import Repuesto, MovimientoInventario
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method != "POST":
        return redirect("ordenes:detalle", pk=pk)

    repuesto_ids = request.POST.getlist("repuesto_id")
    cantidades = request.POST.getlist("cantidad")
    precios = request.POST.getlist("precio_unitario")
    descripciones = request.POST.getlist("descripcion")

    agregados = 0
    for i, rid in enumerate(repuesto_ids):
        try:
            repuesto = Repuesto.objects.get(pk=rid, activo=True)
            cantidad = Decimal(cantidades[i]) if i < len(cantidades) else Decimal("1")
            precio = Decimal(precios[i]) if i < len(precios) else Decimal(str(repuesto.precio_venta or "0"))
            descripcion = descripciones[i] if i < len(descripciones) else repuesto.nombre
            if cantidad <= 0:
                continue
            det = DetalleOrdenTrabajo.objects.create(
                orden=orden, tipo="REPUESTO",
                repuesto_inventario=repuesto,
                descripcion=repuesto.nombre,
                cantidad=cantidad,
                precio_unitario=precio,
            )
            # Descontar del inventario
            stock_ant = repuesto.stock_actual
            repuesto.stock_actual = max(Decimal("0"), repuesto.stock_actual - cantidad)
            repuesto.save(update_fields=["stock_actual"])
            MovimientoInventario.objects.create(
                repuesto=repuesto,
                tipo=MovimientoInventario.TipoMovimiento.SALIDA,
                cantidad=cantidad,
                stock_anterior=stock_ant,
                stock_nuevo=repuesto.stock_actual,
                orden_trabajo=orden,
                motivo=f"Usado en OT {orden.numero_orden}",
                realizado_por=request.user,
            )
            agregados += 1
        except (Repuesto.DoesNotExist, Exception):
            continue

    _recalcular_costos(orden)
    if agregados:
        messages.success(request, f"{agregados} repuesto(s) agregado(s) a la orden.")
    else:
        messages.warning(request, "No se agregó ningún repuesto.")
    return redirect("ordenes:detalle", pk=pk)


@admin_o_recepcionista_requerido
def editar_detalle(request, pk, det_pk):
    """AJAX: edita cantidad y precio_unitario de un DetalleOrdenTrabajo y recalcula costos."""
    import json
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido."}, status=405)
    det = get_object_or_404(DetalleOrdenTrabajo, pk=det_pk, orden__pk=pk)
    try:
        data = json.loads(request.body)
        cantidad = Decimal(str(data["cantidad"]))
        precio = Decimal(str(data["precio_unitario"]))
        if cantidad <= 0 or precio < 0:
            raise ValueError
    except (KeyError, ValueError, Exception):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)
    det.cantidad = cantidad
    det.precio_unitario = precio
    det.save(update_fields=["cantidad", "precio_unitario"])
    _recalcular_costos(det.orden)
    return JsonResponse({"ok": True, "subtotal": float(det.subtotal)})


@admin_o_mecanico_requerido
def eliminar_detalle(request, pk, det_pk):
    det = get_object_or_404(DetalleOrdenTrabajo, pk=det_pk, orden__pk=pk)
    orden = det.orden
    if request.method == "POST":
        # Si vino del inventario, restaurar stock
        if det.repuesto_inventario_id:
            from apps.inventario.models import Repuesto, MovimientoInventario
            repuesto = det.repuesto_inventario
            stock_ant = repuesto.stock_actual
            repuesto.stock_actual += det.cantidad
            repuesto.save(update_fields=["stock_actual"])
            MovimientoInventario.objects.create(
                repuesto=repuesto,
                tipo=MovimientoInventario.TipoMovimiento.DEVOLUCION,
                cantidad=det.cantidad,
                stock_anterior=stock_ant,
                stock_nuevo=repuesto.stock_actual,
                orden_trabajo=orden,
                motivo=f"Eliminado de OT {orden.numero_orden}",
                realizado_por=request.user,
            )
        det.delete()
        _recalcular_costos(orden)
        messages.success(request, "Ítem eliminado.")
    return redirect("ordenes:detalle", pk=pk)


@admin_o_recepcionista_requerido
def eliminar(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        orden.estado = "CANCELADA"
        orden.save()
        messages.success(request, f"Orden {orden.numero_orden} cancelada.")
        return redirect("ordenes:lista")
    return render(request, "ordenes/confirmar_eliminar.html", {"orden": orden})


@admin_o_recepcionista_requerido
def vehiculos_por_cliente(request):
    cliente_id = request.GET.get("cliente")
    vehiculos = Vehiculo.objects.filter(cliente_id=cliente_id, activo=True).order_by("placa")
    data = [
        {"id": v.id, "text": f"{v.placa} - {v.descripcion_corta}", "kilometraje": v.kilometraje_actual}
        for v in vehiculos
    ]
    return JsonResponse({"results": data})


def _recalcular_costos(orden):
    """Recalcula y guarda costo_mano_obra y costo_repuestos en la orden."""
    detalles = orden.detalles.all()
    orden.costo_mano_obra = sum(d.subtotal for d in detalles if d.tipo == "SERVICIO")
    orden.costo_repuestos = sum(d.subtotal for d in detalles if d.tipo == "REPUESTO")
    orden.save(update_fields=["costo_mano_obra", "costo_repuestos"])
