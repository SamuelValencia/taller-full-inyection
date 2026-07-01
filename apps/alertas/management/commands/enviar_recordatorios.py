"""
Management command: enviar_recordatorios
Revisa diariamente los registros de mantenimiento próximos y envía
recordatorios automáticos a los clientes.

Uso:
    python manage.py enviar_recordatorios
    python manage.py enviar_recordatorios --forzar
    python manage.py enviar_recordatorios --dias 7
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.alertas.models import ConfiguracionRecordatorio, RegistroMantenimiento, RecordatorioMantenimiento
from apps.alertas.services import procesar_recordatorio


class Command(BaseCommand):
    help = "Revisa mantenimientos próximos y envía recordatorios automáticos a los clientes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias",
            type=int,
            default=None,
            help="Sobreescribir días de anticipación (usa el valor de ConfiguracionRecordatorio si no se especifica).",
        )
        parser.add_argument(
            "--forzar",
            action="store_true",
            default=False,
            help="Forzar el envío aunque ya se haya enviado un recordatorio previamente.",
        )
        parser.add_argument(
            "--simular",
            action="store_true",
            default=False,
            help="Simula el proceso sin enviar mensajes reales.",
        )

    def handle(self, *args, **options):
        config = ConfiguracionRecordatorio.obtener()

        if not config.activo and not options["forzar"]:
            self.stdout.write(self.style.WARNING(
                "Sistema de recordatorios DESACTIVADO. Use --forzar para ejecutar de todas formas."
            ))
            return

        dias_anticipacion = options["dias"] or config.dias_anticipacion
        hoy = timezone.localdate()
        fecha_limite = hoy + timedelta(days=dias_anticipacion)

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Fuel Injection — Envío de Recordatorios de Mantenimiento")
        self.stdout.write(f"  Fecha: {hoy} | Anticipación: {dias_anticipacion} días")
        self.stdout.write(f"  Buscando mantenimientos entre {hoy} y {fecha_limite}")
        if options["simular"]:
            self.stdout.write(self.style.WARNING("  MODO SIMULACIÓN — No se enviarán mensajes reales"))
        self.stdout.write(f"{'='*60}\n")

        # Buscar registros con próximo mantenimiento en el rango
        registros = RegistroMantenimiento.objects.filter(
            activo=True,
            fecha_proximo_mantenimiento__gte=hoy,
            fecha_proximo_mantenimiento__lte=fecha_limite,
        ).select_related("cliente", "vehiculo")

        if not registros.exists():
            self.stdout.write(self.style.SUCCESS(
                f"  Sin mantenimientos próximos en los próximos {dias_anticipacion} días."
            ))
            return

        total = registros.count()
        enviados = 0
        errores = 0
        omitidos = 0

        for registro in registros:
            cliente = registro.cliente
            vehiculo = registro.vehiculo
            dias_restantes = registro.dias_para_proximo

            self.stdout.write(
                f"  → {cliente.nombre_completo} | {vehiculo.placa} — "
                f"{vehiculo.marca} {vehiculo.modelo} | "
                f"Próximo: {registro.fecha_proximo_mantenimiento} ({dias_restantes} días)"
            )

            # Verificar si ya existe un recordatorio enviado recientemente (hoy)
            if not options["forzar"]:
                ya_enviado_hoy = registro.recordatorios.filter(
                    estado="ENVIADO",
                    fecha_envio__date=hoy,
                ).exists()
                if ya_enviado_hoy:
                    self.stdout.write(self.style.WARNING("    ⏭ Ya se envió un recordatorio hoy. Use --forzar para reenviar."))
                    omitidos += 1
                    continue

            if options["simular"]:
                self.stdout.write(self.style.SUCCESS(f"    ✓ [SIMULACIÓN] Se enviaría por {registro.canal_envio}"))
                enviados += 1
                continue

            # Crear y enviar el recordatorio
            recordatorio = RecordatorioMantenimiento.objects.create(
                registro=registro,
                canal=registro.canal_envio,
                estado="PENDIENTE",
                fecha_programada=hoy,
                intento_numero=registro.recordatorios.count() + 1,
            )

            exito = procesar_recordatorio(recordatorio)

            if exito:
                self.stdout.write(self.style.SUCCESS(
                    f"    ✓ Recordatorio enviado por {registro.canal_envio}"
                ))
                enviados += 1
            else:
                self.stdout.write(self.style.ERROR(
                    f"    ✗ Error: {recordatorio.error_detalle[:100]}"
                ))
                errores += 1

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(
            f"  Resumen: {total} registros | {enviados} enviados | {errores} errores | {omitidos} omitidos"
        ))
        self.stdout.write(f"{'='*60}\n")
