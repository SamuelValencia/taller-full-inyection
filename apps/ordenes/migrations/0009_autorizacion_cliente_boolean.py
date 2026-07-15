from django.db import migrations, models


def texto_a_boolean(apps, schema_editor):
    OrdenTrabajo = apps.get_model("ordenes", "OrdenTrabajo")
    for o in OrdenTrabajo.objects.all():
        # Si el campo viejo tenía texto, se considera que hubo autorización
        o.autorizacion_cliente_bool = bool(o.autorizacion_cliente_texto and o.autorizacion_cliente_texto.strip())
        o.save(update_fields=["autorizacion_cliente_bool"])


def revertir(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("ordenes", "0008_recordatorio_campos_ot"),
    ]

    operations = [
        # 1. Renombrar el campo viejo (texto)
        migrations.RenameField(
            model_name="ordentrabajo",
            old_name="autorizacion_cliente",
            new_name="autorizacion_cliente_texto",
        ),
        # 2. Agregar el nuevo campo booleano
        migrations.AddField(
            model_name="ordentrabajo",
            name="autorizacion_cliente_bool",
            field=models.BooleanField(default=False, verbose_name="Cliente autorizo los trabajos"),
        ),
        # 3. Migrar datos existentes
        migrations.RunPython(texto_a_boolean, revertir),
        # 4. Eliminar el campo texto
        migrations.RemoveField(
            model_name="ordentrabajo",
            name="autorizacion_cliente_texto",
        ),
        # 5. Renombrar el booleano al nombre definitivo
        migrations.RenameField(
            model_name="ordentrabajo",
            old_name="autorizacion_cliente_bool",
            new_name="autorizacion_cliente",
        ),
    ]
