from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ordenes", "0002_initial"),
        ("servicios", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="EvidenciaOrden",
        ),
        migrations.AddField(
            model_name="ordenservicio",
            name="precio",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name="Precio del servicio ($)"),
        ),
        migrations.AddField(
            model_name="ordenservicio",
            name="servicio",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ordenes",
                to="servicios.servicio",
                verbose_name="Servicio",
            ),
        ),
    ]
