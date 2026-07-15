from django.db import migrations


CATEGORIAS = [
    ("FILTROS",    "Filtros de aire, aceite, combustible y habitáculo"),
    ("ACEITES",    "Aceites de motor, transmisión y frenos"),
    ("FRENOS",     "Pastillas, discos, tambores y cilindros de freno"),
    ("ENCENDIDO",  "Bujías, cables y bobinas de encendido"),
    ("SUSPENSION", "Amortiguadores, resortes y rótulas de suspensión"),
    ("CORREAS",    "Correas de distribución, alternador y accesorios"),
    ("ELECTRICO",  "Batería, alternador, arranque y fusibles"),
]

REPUESTOS = [
    # (codigo, nombre, categoria_slug, marca, stock_actual, stock_minimo, precio_compra, precio_venta)
    ("FLT-001", "Filtro de aceite universal",              "FILTROS",    "Mann",      20, 5,  "2.50",  "5.00"),
    ("FLT-002", "Filtro de aire rectangular",              "FILTROS",    "Bosch",     15, 4,  "4.00",  "8.00"),
    ("FLT-003", "Filtro de combustible gasolina",          "FILTROS",    "WIX",       12, 3,  "3.50",  "7.00"),
    ("FLT-004", "Filtro de habitaculo / polen",            "FILTROS",    "Corteco",   10, 3,  "3.00",  "6.50"),
    ("ACE-001", "Aceite 10W-40 semisintetico 1L",          "ACEITES",    "Castrol",   50, 10, "4.50",  "8.00"),
    ("ACE-002", "Aceite 5W-30 sintetico 1L",               "ACEITES",    "Mobil",     40, 8,  "6.00", "11.00"),
    ("ACE-003", "Aceite de transmision ATF 1L",            "ACEITES",    "Valvoline", 20, 5,  "5.00",  "9.50"),
    ("ACE-004", "Liquido de frenos DOT 4 500ml",           "ACEITES",    "ATE",       25, 5,  "3.00",  "6.00"),
    ("FRN-001", "Pastillas de freno delanteras (juego)",   "FRENOS",     "Brembo",    10, 3,  "12.00","22.00"),
    ("FRN-002", "Pastillas de freno traseras (juego)",     "FRENOS",     "Brembo",    10, 3,  "10.00","18.00"),
    ("FRN-003", "Disco de freno delantero",                "FRENOS",     "TRW",        8, 2,  "18.00","32.00"),
    ("FRN-004", "Disco de freno trasero",                  "FRENOS",     "TRW",        8, 2,  "16.00","28.00"),
    ("FRN-005", "Zapatas de freno traseras (juego)",       "FRENOS",     "Bosch",      6, 2,  "8.00", "15.00"),
    ("ENC-001", "Bujia estandar NGK BPR6ES",               "ENCENDIDO",  "NGK",       40, 8,  "1.50",  "3.50"),
    ("ENC-002", "Bujia iridium NGK ILFR6B",                "ENCENDIDO",  "NGK",       20, 4,  "6.00", "12.00"),
    ("ENC-003", "Cable de bujia (juego 4 cil.)",           "ENCENDIDO",  "Bosch",      8, 2,  "9.00", "18.00"),
    ("ENC-004", "Bobina de encendido individual",          "ENCENDIDO",  "Delphi",     6, 2, "22.00", "40.00"),
    ("SUS-001", "Amortiguador delantero Monroe",           "SUSPENSION", "Monroe",     6, 2, "30.00", "55.00"),
    ("SUS-002", "Amortiguador trasero Monroe",             "SUSPENSION", "Monroe",     6, 2, "25.00", "45.00"),
    ("SUS-003", "Rotula de suspension inferior",           "SUSPENSION", "Moog",       8, 2, "15.00", "28.00"),
    ("SUS-004", "Terminal de direccion (par)",             "SUSPENSION", "Moog",       8, 2, "12.00", "22.00"),
    ("SUS-005", "Bulon estabilizador (par)",               "SUSPENSION", "Moog",      10, 3,  "5.00", "10.00"),
    ("COR-001", "Correa de distribucion (kit)",            "CORREAS",    "Gates",      5, 2, "25.00", "45.00"),
    ("COR-002", "Correa de alternador",                    "CORREAS",    "Dayco",     10, 3,  "6.00", "12.00"),
    ("COR-003", "Correa de aire acondicionado",            "CORREAS",    "Dayco",      8, 2,  "5.00", "10.00"),
    ("COR-004", "Tensor de correa de distribucion",        "CORREAS",    "INA",        4, 1, "18.00", "32.00"),
    ("ELE-001", "Bateria 12V 60Ah",                        "ELECTRICO",  "Bosch",      5, 1, "65.00","110.00"),
    ("ELE-002", "Bateria 12V 45Ah",                        "ELECTRICO",  "Bosch",      5, 1, "50.00", "85.00"),
    ("ELE-003", "Relay de arranque 12V 30A",               "ELECTRICO",  "Hella",     15, 3,  "2.00",  "4.50"),
    ("ELE-004", "Fusible automotriz ATO 10A (pack 10)",    "ELECTRICO",  "LittleFuse",20, 5,  "1.00",  "2.50"),
]


def insertar_datos(apps, schema_editor):
    Categoria = apps.get_model("inventario", "CategoriaRepuesto")
    Repuesto  = apps.get_model("inventario", "Repuesto")

    cat_map = {}
    for slug, desc in CATEGORIAS:
        nombre = slug.capitalize().replace("_", " ")
        cat, _ = Categoria.objects.get_or_create(
            nombre=slug,
            defaults={"descripcion": desc, "activo": True},
        )
        cat_map[slug] = cat

    from decimal import Decimal
    for codigo, nombre, cat_slug, marca, stock, stock_min, pc, pv in REPUESTOS:
        if not Repuesto.objects.filter(codigo=codigo).exists():
            Repuesto.objects.create(
                codigo=codigo,
                nombre=nombre,
                categoria=cat_map[cat_slug],
                marca=marca,
                stock_actual=stock,
                stock_minimo=stock_min,
                stock_maximo=stock * 3,
                precio_compra=Decimal(pc),
                precio_venta=Decimal(pv),
                activo=True,
            )


def revertir(apps, schema_editor):
    Repuesto  = apps.get_model("inventario", "Repuesto")
    Categoria = apps.get_model("inventario", "CategoriaRepuesto")
    codigos = [r[0] for r in REPUESTOS]
    Repuesto.objects.filter(codigo__in=codigos).delete()
    slugs = [c[0] for c in CATEGORIAS]
    Categoria.objects.filter(nombre__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0003_movimientoinventario_orden_trabajo_and_more"),
    ]

    operations = [
        migrations.RunPython(insertar_datos, revertir),
    ]
