from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from apps.decorators import admin_o_recepcionista_requerido, rol_autenticado_requerido
from .models import Alerta, ConfiguracionRecordatorio, RegistroMantenimiento, RecordatorioMantenimiento
from .services import procesar_recordatorio


# ──────────────────────────────────────────────────────────────
# Módulo principal: Recordatorios de mantenimiento para clientes
# ──────────────────────────────────────────────────────────────

@admin_o_recepcionista_requerido
def lista(request):
    """Vista principal: tabla de todos los recordatorios de mantenimiento."""
    from apps.clientes.models import Cliente
    from apps.vehiculos.models import Vehiculo

    # Filtros opcionales
    estado_filtro = request.GET.get("estado", "")
    cliente_q = request.GET.get("cliente", "")

    registros = RegistroMantenimiento.objects.filter(activo=True).select_related(
        "cliente", "vehiculo", "orden"
    ).prefetch_related("recordatorios").order_by("fecha_proximo_mantenimiento")

    if cliente_q:
        from django.db.models import Q
        registros = registros.filter(
            Q(cliente__nombres__icontains=cliente_q) |
            Q(cliente__apellidos__icontains=cliente_q) |
            Q(vehiculo__placa__icontains=cliente_q)
        )

    if estado_filtro == "proximos":
        hoy = timezone.localdate()
        registros = registros.filter(
            fecha_proximo_mantenimiento__gte=hoy,
            fecha_proximo_mantenimiento__lte=hoy + timedelta(days=10),
        )
    elif estado_filtro == "vencidos":
        hoy = timezone.localdate()
        registros = registros.filter(fecha_proximo_mantenimiento__lt=hoy)
    elif estado_filtro == "pendientes":
        # Tiene recordatorio pendiente de envío
        registros = registros.filter(recordatorios__estado="PENDIENTE")

    config = ConfiguracionRecordatorio.obtener()

    return render(request, "alertas/lista.html", {
        "registros": registros,
        "config": config,
        "estado_filtro": estado_filtro,
        "cliente_q": cliente_q,
        "hoy": timezone.localdate(),
    })


@admin_o_recepcionista_requerido
def crear_registro(request):
    """Crea manualmente un registro de mantenimiento para un vehículo."""
    from apps.vehiculos.models import Vehiculo
    from apps.clientes.models import Cliente

    if request.method == "POST":
        try:
            vehiculo_id = request.POST.get("vehiculo")
            vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
            tipo_intervalo = request.POST.get("tipo_intervalo", "DIAS")
            intervalo_dias = request.POST.get("intervalo_dias") or None
            intervalo_km = request.POST.get("intervalo_km") or None
            canal_envio = request.POST.get("canal_envio", "EMAIL")

            registro = RegistroMantenimiento(
                vehiculo=vehiculo,
                cliente=vehiculo.cliente,
                tipo_mantenimiento=request.POST.get("tipo_mantenimiento", "Mantenimiento preventivo"),
                descripcion_trabajos=request.POST.get("descripcion_trabajos", ""),
                fecha_mantenimiento=request.POST.get("fecha_mantenimiento"),
                kilometraje_mantenimiento=int(request.POST.get("kilometraje_mantenimiento", 0)),
                tipo_intervalo=tipo_intervalo,
                intervalo_dias=int(intervalo_dias) if intervalo_dias else None,
                intervalo_km=int(intervalo_km) if intervalo_km else None,
                canal_envio=canal_envio,
            )
            registro.calcular_proximo()
            registro.save()

            # Crear recordatorio pendiente automáticamente
            _crear_recordatorio_pendiente(registro)

            messages.success(request, "Registro de mantenimiento creado correctamente.")
            return redirect("alertas:lista")
        except Exception as e:
            messages.error(request, f"Error al crear el registro: {e}")

    vehiculos = Vehiculo.objects.filter(activo=True).select_related("cliente").order_by("placa")
    return render(request, "alertas/crear_registro.html", {
        "vehiculos": vehiculos,
        "hoy": timezone.localdate().isoformat(),
    })


@admin_o_recepcionista_requerido
def detalle_registro(request, pk):
    """Detalle de un registro de mantenimiento con historial de recordatorios."""
    registro = get_object_or_404(
        RegistroMantenimiento.objects.select_related("cliente", "vehiculo", "orden"),
        pk=pk
    )
    recordatorios = registro.recordatorios.order_by("-fecha_creacion")
    return render(request, "alertas/detalle_registro.html", {
        "registro": registro,
        "recordatorios": recordatorios,
        "hoy": timezone.localdate(),
    })


@admin_o_recepcionista_requerido
def reenviar_recordatorio(request, pk):
    """Reenvía manualmente un recordatorio ya enviado o con error."""
    if request.method != "POST":
        return redirect("alertas:lista")

    registro = get_object_or_404(RegistroMantenimiento, pk=pk)
    canal = request.POST.get("canal", registro.canal_envio)

    config = ConfiguracionRecordatorio.obtener()
    hoy = timezone.localdate()

    # Calcular nueva fecha programada
    if registro.fecha_proximo_mantenimiento:
        fecha_programada = registro.fecha_proximo_mantenimiento - timedelta(days=config.dias_anticipacion)
    else:
        fecha_programada = hoy

    # Contar intentos anteriores
    intentos = registro.recordatorios.count()

    recordatorio = RecordatorioMantenimiento.objects.create(
        registro=registro,
        canal=canal,
        estado="PENDIENTE",
        fecha_programada=fecha_programada,
        intento_numero=intentos + 1,
    )

    exito = procesar_recordatorio(recordatorio)
    if exito:
        messages.success(request, "Recordatorio reenviado correctamente.")
    else:
        messages.error(
            request,
            f"Error al reenviar el recordatorio: {recordatorio.error_detalle}"
        )
    return redirect("alertas:detalle_registro", pk=pk)


@admin_o_recepcionista_requerido
def configuracion(request):
    """Vista de configuración del sistema de recordatorios."""
    config = ConfiguracionRecordatorio.obtener()
    if request.method == "POST":
        dias = request.POST.get("dias_anticipacion", 5)
        activo = request.POST.get("activo") == "on"
        config.dias_anticipacion = int(dias)
        config.activo = activo
        config.save()
        messages.success(request, "Configuración guardada correctamente.")
        return redirect("alertas:configuracion")
    return render(request, "alertas/configuracion.html", {"config": config})


# ──────────────────────────────────────────────────────────────
# Alertas internas (compatibilidad)
# ──────────────────────────────────────────────────────────────

@rol_autenticado_requerido
def marcar_leida(request, pk):
    alerta = get_object_or_404(Alerta, pk=pk, destinatario=request.user)
    alerta.leida = True
    alerta.save(update_fields=["leida"])
    return redirect("alertas:lista")


@rol_autenticado_requerido
def marcar_todas_leidas(request):
    if request.method == "POST":
        Alerta.objects.filter(destinatario=request.user, leida=False).update(leida=True)
        messages.success(request, "Todas las alertas marcadas como leídas.")
    return redirect("alertas:lista")


# ──────────────────────────────────────────────────────────────
# Helper interno
# ──────────────────────────────────────────────────────────────

def _crear_recordatorio_pendiente(registro: RegistroMantenimiento):
    """Crea un RecordatorioMantenimiento en estado PENDIENTE para un registro dado."""
    config = ConfiguracionRecordatorio.obtener()
    if registro.fecha_proximo_mantenimiento:
        fecha_programada = (
            registro.fecha_proximo_mantenimiento - timedelta(days=config.dias_anticipacion)
        )
    else:
        fecha_programada = timezone.localdate()

    RecordatorioMantenimiento.objects.create(
        registro=registro,
        canal=registro.canal_envio,
        estado="PENDIENTE",
        fecha_programada=fecha_programada,
        intento_numero=1,
    )
