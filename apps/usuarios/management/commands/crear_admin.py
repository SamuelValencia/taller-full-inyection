from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea o actualiza el superusuario administrador"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="admin@fuelinjection.com")
        parser.add_argument("--password", required=True)
        parser.add_argument("--nombre", default="Administrador")
        parser.add_argument("--apellido", default="Sistema")

    def handle(self, *args, **options):
        username = options["username"]
        user, created = Usuario.objects.get_or_create(username=username)
        user.email = options["email"]
        user.first_name = options["nombre"]
        user.last_name = options["apellido"]
        from apps.roles.models import Rol
        user.rol = Rol.objects.get(codigo="ADMIN")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.activo = True
        user.set_password(options["password"])
        user.save()
        accion = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' {accion} correctamente."))
