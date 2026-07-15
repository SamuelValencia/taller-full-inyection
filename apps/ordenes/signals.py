"""
Signal: cuando una OrdenTrabajo pasa a FINALIZADA:
  1. Crea automaticamente un HistorialMantenimiento en el vehiculo (siempre).
  2. Si requiere_recordatorio=True, crea un RegistroMantenimiento y su
     RecordatorioMantenimiento pendiente (sistema de avisos al cliente).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="ordenes.OrdenTrabajo")
def al_finalizar_orden(sender, instance, created, **kwargs):
    if instance.estado != "FINALIZADA":
        return

    _crear_historial_vehiculo(instance)

    if instance.requiere_recordatorio:
        _crear_registro_recordatorio(instance)


# ──────────────────────────────────────────────────────────────────────────────

def _crear_historial_vehiculo(orden):
    """
    Crea un HistorialMantenimiento para el vehiculo asociado a la orden.
    Evita duplicados comprobando si ya existe un registro para esta OT.
    """
    from apps.mantenimiento.models import HistorialMantenimiento
    from django.utils import timezone

    if HistorialMantenimiento.objects.filter(orden=orden).exists():
        return

    detalles = orden.detalles.all()
    if detalles.exists():
        descripcion = "\n".join(
            f"- {d.descripcion} (x{d.cantidad:.0f})" for d in detalles
        )
    else:
        descripcion = orden.descripcion_problema

    fecha_servicio = (
        orden.fecha_entrega_real.date()
        if orden.fecha_entrega_real
        else timezone.localdate()
    )

    HistorialMantenimiento.objects.create(
        vehiculo=orden.vehiculo,
        orden=orden,
        descripcion=descripcion,
        km_al_servicio=orden.kilometraje_ingreso or 0,
        tecnico=orden.tecnico_asignado,
        costo=orden.costo_total,
        fecha_servicio=fecha_servicio,
        observaciones=orden.observaciones,
    )


def _crear_registro_recordatorio(orden):
    """
    Crea un RegistroMantenimiento usando los intervalos configurados en la OT.
    Evita duplicados si ya existe un registro para esta OT.
    """
    from apps.alertas.models import RegistroMantenimiento
    from apps.alertas.views import _crear_recordatorio_pendiente
    from django.utils import timezone

    if RegistroMantenimiento.objects.filter(orden=orden).exists():
        return

    detalles = orden.detalles.all()
    descripcion = (
        "\n".join(f"- {d.descripcion} (x{d.cantidad:.0f})" for d in detalles)
        if detalles.exists()
        else orden.descripcion_problema
    )

    fecha_mant = (
        orden.fecha_entrega_real.date()
        if orden.fecha_entrega_real
        else timezone.localdate()
    )

    tiene_dias = bool(orden.intervalo_dias_recordatorio)
    tiene_km = bool(orden.intervalo_km_recordatorio)
    if tiene_dias and tiene_km:
        tipo_intervalo = "AMBOS"
    elif tiene_km:
        tipo_intervalo = "KM"
    else:
        tipo_intervalo = "DIAS"

    registro = RegistroMantenimiento(
        orden=orden,
        vehiculo=orden.vehiculo,
        cliente=orden.cliente,
        tipo_mantenimiento=orden.get_tipo_trabajo_display(),
        descripcion_trabajos=descripcion,
        fecha_mantenimiento=fecha_mant,
        kilometraje_mantenimiento=orden.kilometraje_ingreso or 0,
        tipo_intervalo=tipo_intervalo,
        intervalo_dias=orden.intervalo_dias_recordatorio or None,
        intervalo_km=orden.intervalo_km_recordatorio or None,
        canal_envio=orden.canal_recordatorio,
    )
    registro.calcular_proximo()
    registro.save()

    _crear_recordatorio_pendiente(registro)
