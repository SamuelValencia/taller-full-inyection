from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0002_remove_usuario_foto_perfil"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="rol",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Administrador"),
                    ("GERENTE", "Gerente"),
                    ("MECANICO", "Mecánico"),
                    ("RECEPCIONISTA", "Recepcionista"),
                ],
                default="RECEPCIONISTA",
                max_length=20,
                verbose_name="Rol",
            ),
        ),
    ]
