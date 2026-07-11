"""Mixins de acceso por rol para vistas de clase."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RolRequeridoMixin(LoginRequiredMixin):
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.roles_permitidos and request.user.rol_codigo not in self.roles_permitidos:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminRequeridoMixin(RolRequeridoMixin):
    roles_permitidos = ["ADMIN"]


class AdminRecepcionistaMixin(RolRequeridoMixin):
    roles_permitidos = ["ADMIN", "RECEPCIONISTA"]
