from django.db import migrations, models

MARCAS_MAP = {
    "chevrolet": "CHEVROLET", "toyota": "TOYOTA", "hyundai": "HYUNDAI",
    "kia": "KIA", "suzuki": "SUZUKI", "mazda": "MAZDA", "nissan": "NISSAN",
    "ford": "FORD", "volkswagen": "VOLKSWAGEN", "honda": "HONDA",
    "mitsubishi": "MITSUBISHI", "renault": "RENAULT", "jeep": "JEEP",
    "dodge": "DODGE", "ram": "RAM", "great wall": "GREAT_WALL",
    "chery": "CHERY", "byd": "BYD", "jac": "JAC", "dfsk": "DFSK",
    "dongfeng": "DFSK", "hino": "HINO", "fuso": "FUSO", "isuzu": "ISUZU",
    "mercedes": "MERCEDES", "mercedes-benz": "MERCEDES", "bmw": "BMW",
    "audi": "AUDI", "subaru": "SUBARU", "land rover": "LAND_ROVER",
    "peugeot": "PEUGEOT", "citroen": "CITROEN", "citroën": "CITROEN",
    "volvo": "VOLVO",
}


def normalizar_marcas(apps, schema_editor):
    Vehiculo = apps.get_model("vehiculos", "Vehiculo")
    for v in Vehiculo.objects.all():
        clave = v.marca.lower().strip()
        v.marca = MARCAS_MAP.get(clave, "OTRA")
        v.save(update_fields=["marca"])


def revertir_marcas(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("vehiculos", "0002_remove_vehiculo_foto_restringir_tipos"),
    ]

    operations = [
        migrations.RunPython(normalizar_marcas, revertir_marcas),
        migrations.AlterField(
            model_name="vehiculo",
            name="marca",
            field=models.CharField(
                max_length=60,
                verbose_name="Marca",
                choices=[
                    ("CHEVROLET", "Chevrolet"), ("TOYOTA", "Toyota"),
                    ("HYUNDAI", "Hyundai"), ("KIA", "Kia"), ("SUZUKI", "Suzuki"),
                    ("MAZDA", "Mazda"), ("NISSAN", "Nissan"), ("FORD", "Ford"),
                    ("VOLKSWAGEN", "Volkswagen"), ("HONDA", "Honda"),
                    ("MITSUBISHI", "Mitsubishi"), ("RENAULT", "Renault"),
                    ("JEEP", "Jeep"), ("DODGE", "Dodge"), ("RAM", "RAM"),
                    ("GREAT_WALL", "Great Wall"), ("CHERY", "Chery"),
                    ("BYD", "BYD"), ("JAC", "JAC"), ("DFSK", "DFSK / Dongfeng"),
                    ("HINO", "Hino"), ("FUSO", "Fuso"), ("ISUZU", "Isuzu"),
                    ("MERCEDES", "Mercedes-Benz"), ("BMW", "BMW"), ("AUDI", "Audi"),
                    ("SUBARU", "Subaru"), ("LAND_ROVER", "Land Rover"),
                    ("PEUGEOT", "Peugeot"), ("CITROEN", "Citroën"),
                    ("VOLVO", "Volvo"), ("OTRA", "Otra"),
                ],
            ),
        ),
    ]
