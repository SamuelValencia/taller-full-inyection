from django import template

register = template.Library()


@register.filter(name="puede")
def puede(user, permiso):
    """
    Uso: {% if request.user|puede:"modulo.accion" %}
    Retorna True si el usuario tiene el permiso indicado.
    """
    try:
        modulo_codigo, accion_codigo = permiso.split(".", 1)
    except ValueError:
        return False
    if not hasattr(user, "is_authenticated") or not user.is_authenticated:
        return False
    return user.tiene_permiso(modulo_codigo, accion_codigo)


@register.simple_tag(takes_context=True)
def tiene_permiso(context, modulo_codigo, accion_codigo):
    """
    Uso: {% tiene_permiso "modulo" "accion" as flag %}
    """
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return False
    return request.user.tiene_permiso(modulo_codigo, accion_codigo)
