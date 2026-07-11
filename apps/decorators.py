"""
Decoradores para control de acceso por rol en vistas basadas en funciones.
"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps


def rol_requerido(*roles_permitidos):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados.
    
    Uso:
        @rol_requerido('ADMIN', 'RECEPCIONISTA')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            
            if not request.user.is_superuser and request.user.rol_codigo not in roles_permitidos:
                raise PermissionDenied(
                    "No tienes permisos para acceder a esta página. "
                    f"Roles requeridos: {', '.join(roles_permitidos)}"
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_requerido(view_func):
    """
    Decorador que requiere rol de administrador.
    """
    return rol_requerido('ADMIN')(view_func)


def admin_o_recepcionista_requerido(view_func):
    """
    Decorador que requiere rol de administrador, gerente o recepcionista.
    """
    return rol_requerido('ADMIN', 'GERENTE', 'RECEPCIONISTA')(view_func)


def admin_o_mecanico_requerido(view_func):
    """
    Decorador que requiere rol de administrador, gerente o mecánico.
    """
    return rol_requerido('ADMIN', 'GERENTE', 'MECANICO')(view_func)


def rol_autenticado_requerido(view_func):
    """
    Decorador que requiere cualquier rol autenticado (ADMIN, GERENTE, MECANICO, RECEPCIONISTA).
    """
    return rol_requerido('ADMIN', 'GERENTE', 'MECANICO', 'RECEPCIONISTA')(view_func)


def permiso_requerido(modulo_codigo, accion_codigo):
    """
    Decorador granular: verifica que el usuario tenga un permiso específico.

    Uso:
        @permiso_requerido('clientes', 'exportar')
        def exportar_clientes(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.tiene_permiso(modulo_codigo, accion_codigo):
                raise PermissionDenied(
                    f"No tienes permiso para realizar esta acción: {modulo_codigo}.{accion_codigo}"
                )
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
