from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alertas", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="alerta",
            name="canal",
            field=models.CharField(
                choices=[("INTERNA", "Interna"), ("EMAIL", "Correo electrónico"), ("WHATSAPP", "WhatsApp"), ("AMBOS", "Correo y WhatsApp")],
                default="INTERNA",
                max_length=10,
                verbose_name="Canal de envío",
            ),
        ),
        migrations.AddField(
            model_name="alerta",
            name="programada_para",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Programada para"),
        ),
        migrations.AddField(
            model_name="alerta",
            name="enviada_email",
            field=models.BooleanField(default=False, verbose_name="Enviada por correo"),
        ),
        migrations.AddField(
            model_name="alerta",
            name="enviada_whatsapp",
            field=models.BooleanField(default=False, verbose_name="Enviada por WhatsApp"),
        ),
        migrations.AddField(
            model_name="alerta",
            name="ultimo_error_envio",
            field=models.TextField(blank=True, verbose_name="Último error de envío"),
        ),
        migrations.CreateModel(
            name="PlantillaMensaje",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, unique=True, verbose_name="Nombre")),
                ("canal", models.CharField(choices=[("EMAIL", "Correo electrónico"), ("WHATSAPP", "WhatsApp")], max_length=10, verbose_name="Canal")),
                ("asunto", models.CharField(blank=True, max_length=180, verbose_name="Asunto")),
                ("cuerpo", models.TextField(verbose_name="Cuerpo")),
                ("activa", models.BooleanField(default=True, verbose_name="Activa")),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Plantilla de mensaje",
                "verbose_name_plural": "Plantillas de mensajes",
                "ordering": ["canal", "nombre"],
            },
        ),
        migrations.AddIndex(
            model_name="alerta",
            index=models.Index(fields=["canal", "programada_para"], name="alertas_ale_canal_44d1a1_idx"),
        ),
    ]
