from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vehiculos", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vehiculo",
            name="foto",
        ),
        migrations.AlterField(
            model_name="vehiculo",
            name="tipo_vehiculo",
            field=models.CharField(
                choices=[
                    ("AUTOMOVIL", "Automóvil"),
                    ("CAMIONETA", "Camioneta"),
                    ("SUV", "SUV"),
                ],
                default="AUTOMOVIL",
                max_length=15,
                verbose_name="Tipo de vehículo",
            ),
        ),
    ]
