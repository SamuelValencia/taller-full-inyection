"""Context processor: inyecta contador de alertas no leídas en todos los templates."""
from apps.alertas.models import Alerta


def alertas_no_leidas(request):
    if request.user.is_authenticated:
        count = Alerta.objects.filter(
            activa=True,
            leida=False,
            destinatario=request.user,
        ).count()
        return {"alertas_no_leidas": count}
    return {"alertas_no_leidas": 0}
