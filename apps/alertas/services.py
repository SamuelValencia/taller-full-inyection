"""
Servicios de envío de recordatorios de mantenimiento a clientes.
Soporta: Email (Django SMTP) y WhatsApp (Twilio o Meta Cloud API).
"""
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import Alerta, RecordatorioMantenimiento


# ──────────────────────────────────────────────────────────────
# Helpers internos (compatibilidad con sistema de alertas antiguo)
# ──────────────────────────────────────────────────────────────

def enviar_alerta(alerta: Alerta) -> bool:
    errores = []
    if alerta.canal in ("EMAIL", "AMBOS"):
        try:
            email = getattr(alerta.destinatario, "email", "")
            if email:
                from django.core.mail import send_mail
                send_mail(
                    subject=f"Fuel Injection - {alerta.get_tipo_display()}",
                    message=alerta.mensaje,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[email],
                    fail_silently=False,
                )
                alerta.enviada_email = True
        except Exception as exc:
            errores.append(f"Email: {exc}")

    if alerta.canal in ("WHATSAPP", "AMBOS"):
        try:
            provider = getattr(settings, "WHATSAPP_PROVIDER", "")
            if provider:
                alerta.enviada_whatsapp = True
        except Exception as exc:
            errores.append(f"WhatsApp: {exc}")

    alerta.ultimo_error_envio = "\n".join(errores)
    alerta.save(update_fields=["enviada_email", "enviada_whatsapp", "ultimo_error_envio"])
    return not errores


def alertas_pendientes_envio():
    ahora = timezone.now()
    return Alerta.objects.filter(activa=True).exclude(canal="INTERNA").filter(
        programada_para__isnull=True
    ) | Alerta.objects.filter(activa=True).exclude(canal="INTERNA").filter(
        programada_para__lte=ahora
    )


# ──────────────────────────────────────────────────────────────
# Envío de recordatorios de mantenimiento a clientes
# ──────────────────────────────────────────────────────────────

def _contexto_recordatorio(recordatorio: RecordatorioMantenimiento) -> dict:
    """Construye el contexto para la plantilla del mensaje."""
    r = recordatorio.registro
    return {
        "nombre_cliente": r.cliente.nombre_completo,
        "marca": r.vehiculo.marca,
        "modelo": r.vehiculo.modelo,
        "placa": r.vehiculo.placa,
        "anio": r.vehiculo.anio,
        "tipo_mantenimiento": r.tipo_mantenimiento,
        "fecha_ultimo_mantenimiento": r.fecha_mantenimiento,
        "fecha_proximo_mantenimiento": r.fecha_proximo_mantenimiento,
        "kilometraje_proximo": r.kilometraje_proximo_mantenimiento,
        "dias_restantes": r.dias_para_proximo,
        "taller_nombre": getattr(settings, "TALLER_NOMBRE", "Fuel Injection"),
        "taller_telefono": getattr(settings, "TALLER_TELEFONO", ""),
        "taller_direccion": getattr(settings, "TALLER_DIRECCION", ""),
    }


def enviar_recordatorio_email(recordatorio: RecordatorioMantenimiento) -> tuple[bool, str]:
    """
    Envía el recordatorio por correo electrónico usando una plantilla HTML.
    Retorna (éxito: bool, mensaje_error: str).
    """
    cliente = recordatorio.registro.cliente
    email_destino = cliente.email
    if not email_destino:
        return False, f"El cliente {cliente.nombre_completo} no tiene correo registrado."

    try:
        contexto = _contexto_recordatorio(recordatorio)
        asunto = (
            f"Recordatorio de mantenimiento — {contexto['marca']} "
            f"{contexto['modelo']} ({contexto['placa']})"
        )
        html_content = render_to_string(
            "alertas/email/recordatorio_mantenimiento.html", contexto
        )
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=asunto,
            body=text_content,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@fuelinjection.com"),
            to=[email_destino],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def enviar_recordatorio_whatsapp(recordatorio: RecordatorioMantenimiento) -> tuple[bool, str]:
    """
    Envía el recordatorio por WhatsApp.
    Soporta Twilio WhatsApp y Meta Cloud API.
    Las credenciales se configuran en settings (ver .env).
    """
    cliente = recordatorio.registro.cliente
    telefono = cliente.telefono
    if not telefono:
        return False, f"El cliente {cliente.nombre_completo} no tiene teléfono registrado."

    # Normalizar número: debe empezar con código de país
    numero = telefono.strip().replace(" ", "").replace("-", "")
    if not numero.startswith("+"):
        # Ecuador: +593, quitar el 0 inicial si existe
        if numero.startswith("0"):
            numero = "+593" + numero[1:]
        else:
            numero = "+593" + numero

    provider = getattr(settings, "WHATSAPP_PROVIDER", "").upper()
    contexto = _contexto_recordatorio(recordatorio)
    mensaje = _texto_recordatorio_whatsapp(contexto)

    if provider == "TWILIO":
        return _enviar_twilio(numero, mensaje)
    elif provider == "META":
        return _enviar_meta(numero, mensaje)
    else:
        # Sin proveedor configurado: simular envío en modo desarrollo
        return False, (
            "WhatsApp no configurado. Configure WHATSAPP_PROVIDER=TWILIO o META "
            "y las credenciales correspondientes en el archivo .env"
        )


def _texto_recordatorio_whatsapp(ctx: dict) -> str:
    """Texto plano para WhatsApp (sin HTML)."""
    fecha = ctx["fecha_proximo_mantenimiento"]
    dias = ctx["dias_restantes"]
    texto = (
        f"Hola {ctx['nombre_cliente']} 👋\n\n"
        f"Esperamos que se encuentre muy bien.\n\n"
        f"Le recordamos que el próximo mantenimiento de su vehículo "
        f"*{ctx['marca']} {ctx['modelo']}* con placa *{ctx['placa']}* "
        f"está programado para el día *{fecha.strftime('%d/%m/%Y')}*"
    )
    if dias is not None and dias >= 0:
        texto += f" (faltan {dias} días)"
    if ctx.get("kilometraje_proximo"):
        texto += f" o al llegar a *{ctx['kilometraje_proximo']:,} km*"
    texto += (
        f".\n\n"
        f"Le invitamos a contactarnos para agendar su cita con anticipación.\n\n"
        f"Será un gusto atenderlo nuevamente. 🔧\n\n"
        f"Atentamente,\n*{ctx['taller_nombre']}*"
    )
    if ctx.get("taller_telefono"):
        texto += f"\n📞 {ctx['taller_telefono']}"
    return texto


def _enviar_twilio(numero: str, mensaje: str) -> tuple[bool, str]:
    """Envío vía Twilio WhatsApp API."""
    try:
        from twilio.rest import Client
        account_sid = getattr(settings, "WHATSAPP_ACCOUNT_SID", "")
        auth_token = getattr(settings, "WHATSAPP_AUTH_TOKEN", "")
        from_number = getattr(settings, "WHATSAPP_FROM_NUMBER", "")

        if not all([account_sid, auth_token, from_number]):
            return False, "Credenciales de Twilio incompletas en .env"

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=mensaje,
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{numero}",
        )
        return True, ""
    except ImportError:
        return False, "Instalar twilio: pip install twilio"
    except Exception as exc:
        return False, str(exc)


def _enviar_meta(numero: str, mensaje: str) -> tuple[bool, str]:
    """Envío vía Meta Cloud API (WhatsApp Business)."""
    try:
        token = getattr(settings, "WHATSAPP_META_TOKEN", "")
        phone_id = getattr(settings, "WHATSAPP_META_PHONE_NUMBER_ID", "")

        if not all([token, phone_id]):
            return False, "Credenciales de Meta Cloud API incompletas en .env"

        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": numero.lstrip("+"),
            "type": "text",
            "text": {"body": mensaje},
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def procesar_recordatorio(recordatorio: RecordatorioMantenimiento) -> bool:
    """
    Envía un recordatorio por el canal configurado y actualiza su estado.
    Retorna True si al menos un canal tuvo éxito.
    """
    canal = recordatorio.canal
    errores = []
    exito_email = False
    exito_whatsapp = False

    if canal in ("EMAIL", "AMBOS"):
        ok, err = enviar_recordatorio_email(recordatorio)
        if ok:
            exito_email = True
            recordatorio.enviado_email = True
        else:
            errores.append(f"Email: {err}")

    if canal in ("WHATSAPP", "AMBOS"):
        ok, err = enviar_recordatorio_whatsapp(recordatorio)
        if ok:
            exito_whatsapp = True
            recordatorio.enviado_whatsapp = True
        else:
            errores.append(f"WhatsApp: {err}")

    exito_total = exito_email or exito_whatsapp
    recordatorio.estado = "ENVIADO" if exito_total else "ERROR"
    recordatorio.fecha_envio = timezone.now() if exito_total else None
    recordatorio.error_detalle = "\n".join(errores)
    recordatorio.save(update_fields=[
        "estado", "fecha_envio", "enviado_email", "enviado_whatsapp", "error_detalle"
    ])
    return exito_total
