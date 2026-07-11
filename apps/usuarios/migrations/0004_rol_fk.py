from django.db import migrations, models
import django.db.models.deletion


def migrar_rol_a_fk(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    Rol = apps.get_model("roles", "Rol")
    roles_map = {r.codigo: r for r in Rol.objects.all()}
    default_rol = roles_map.get("RECEPCIONISTA")
    for usuario in Usuario.objects.all():
        codigo = usuario.rol_legacy or "RECEPCIONISTA"
        usuario.rol = roles_map.get(codigo, default_rol)
        usuario.save(update_fields=["rol"])


def revertir_rol_a_fk(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    for usuario in Usuario.objects.select_related("rol").all():
        if usuario.rol:
            usuario.rol_legacy = usuario.rol.codigo
            usuario.save(update_fields=["rol_legacy"])


class Migration(migrations.Migration):

    dependencies = [
        ("roles", "0002_datos_roles_base"),
        ("usuarios", "0003_alter_usuario_rol"),
    ]

    operations = [
        # 1. Renombrar el CharField antiguo
        migrations.RenameField(model_name="usuario", old_name="rol", new_name="rol_legacy"),
        # 2. Añadir FK nullable
        migrations.AddField(
            model_name="usuario",
            name="rol",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="usuarios",
                to="roles.rol",
                verbose_name="Rol",
            ),
        ),
        # 3. Poblar FK desde el campo legacy
        migrations.RunPython(migrar_rol_a_fk, revertir_rol_a_fk),
        # 4. Hacer FK no-nullable
        migrations.AlterField(
            model_name="usuario",
            name="rol",
            field=models.ForeignKey(
                null=False, blank=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="usuarios",
                to="roles.rol",
                verbose_name="Rol",
            ),
        ),
        # 5. Eliminar campo legacy
        migrations.RemoveField(model_name="usuario", name="rol_legacy"),
    ]
