"""
Signal: cuando una OrdenTrabajo de tipo MANTENIMIENTO_PREVENTIVO
pasa a estado FINALIZADA, crea automáticamente un RegistroMantenimiento.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="ordenes.OrdenTrabajo")
def crear_registro_mantenimiento(sender, instance, created, **kwargs):
    """
    Auto-genera RegistroMantenimiento al finalizar un mantenimiento preventivo.
    Solo actúa si:
    - La OT es de tipo MANTENIMIENTO_PREVENTIVO
    - El estado es FINALIZADA
    - No existe ya un RegistroMantenimiento para esta OT
    """
    if instance.estado != "FINALIZADA":
        return
    if instance.tipo_trabajo != "MANTENIMIENTO_PREVENTIVO":
        return

    # Importar aquí para evitar circular imports
    from apps.alertas.models import RegistroMantenimiento, ConfiguracionRecordatorio
    from apps.alertas.views import _crear_recordatorio_pendiente

    # No duplicar
    if hasattr(instance, "registro_mantenimiento"):
        return

    # Obtener descripción de los trabajos desde los detalles
    detalles = instance.detalles.all()
    descripcion = "\n".join(
        f"- {d.descripcion} (x{d.cantidad:.0f})" for d in detalles
    ) if detalles.exists() else instance.descripcion_problema

    # Intervalo por defecto: 90 días (3 meses)
    intervalo_dias = 90

    registro = RegistroMantenimiento(
        orden=instance,
        vehiculo=instance.vehiculo,
        cliente=instance.cliente,
        tipo_mantenimiento=instance.get_tipo_trabajo_display(),
        descripcion_trabajos=descripcion,
        fecha_mantenimiento=instance.fecha_ingreso.date() if instance.fecha_ingreso else None,
        kilometraje_mantenimiento=instance.kilometraje_ingreso or 0,
        tipo_intervalo="DIAS",
        intervalo_dias=intervalo_dias,
        canal_envio="EMAIL",
    )
    registro.calcular_proximo()
    registro.save()

    # Generar recordatorio pendiente
    _crear_recordatorio_pendiente(registro)
