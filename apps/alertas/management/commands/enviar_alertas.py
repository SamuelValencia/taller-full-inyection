from django.core.management.base import BaseCommand

from apps.alertas.services import alertas_pendientes_envio, enviar_alerta


class Command(BaseCommand):
    help = "Envia alertas programadas por correo o WhatsApp."

    def handle(self, *args, **options):
        enviadas = 0
        for alerta in alertas_pendientes_envio().distinct():
            if enviar_alerta(alerta):
                enviadas += 1
        self.stdout.write(self.style.SUCCESS(f"Alertas procesadas: {enviadas}"))
