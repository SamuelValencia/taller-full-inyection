from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Servicio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, unique=True, verbose_name="Nombre")),
                ("descripcion", models.TextField(blank=True, verbose_name="Descripción")),
                ("estado", models.BooleanField(default=True, verbose_name="Activo")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True, verbose_name="Creado el")),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True, verbose_name="Actualizado el")),
            ],
            options={
                "verbose_name": "Servicio",
                "verbose_name_plural": "Servicios",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddIndex(
            model_name="servicio",
            index=models.Index(fields=["nombre"], name="servicios_s_nombre_b6403b_idx"),
        ),
        migrations.AddIndex(
            model_name="servicio",
            index=models.Index(fields=["estado"], name="servicios_s_estado_2d3c90_idx"),
        ),
    ]
