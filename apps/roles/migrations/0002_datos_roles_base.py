from django.db import migrations


MODULOS = [
    # (codigo, nombre, icono, url_name, orden)
    ("dashboard",     "Dashboard",           "fas fa-tachometer-alt",     "dashboard:index",        1),
    ("clientes",      "Clientes",            "fas fa-users",              "clientes:lista",         2),
    ("vehiculos",     "Vehiculos",           "fas fa-car",                "vehiculos:lista",        3),
    ("ordenes",       "Ordenes de Trabajo",  "fas fa-clipboard-list",     "ordenes:lista",          4),
    ("cotizaciones",  "Cotizaciones",        "fas fa-file-invoice-dollar","cotizaciones:lista",     5),
    ("servicios",     "Servicios",           "fas fa-screwdriver-wrench", "servicios:lista",        6),
    ("inventario",    "Inventario",          "fas fa-boxes",              "inventario:index",       7),
    ("mantenimiento", "Mantenimiento",       "fas fa-tools",              "mantenimiento:lista",    8),
    ("alertas",       "Alertas",             "fas fa-bell",               "alertas:lista",          9),
    ("reportes",      "Reportes",            "fas fa-chart-bar",          "reportes:index",        10),
    ("usuarios",      "Usuarios",            "fas fa-user-cog",           "usuarios:lista",        11),
    ("roles",         "Roles y Permisos",    "fas fa-shield-halved",      "roles:lista",           12),
]

ACCIONES = {
    "dashboard":     [("ver", "Ver dashboard"), ("ver_financiero", "Ver KPIs financieros")],
    "clientes":      [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar"), ("exportar", "Exportar Excel")],
    "vehiculos":     [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar")],
    "ordenes":       [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar/Cancelar"),
                      ("cambiar_estado", "Cambiar estado"), ("agregar_servicio", "Agregar servicio"),
                      ("agregar_repuesto", "Agregar repuesto"), ("imprimir_pdf", "Imprimir PDF")],
    "cotizaciones":  [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar"),
                      ("aprobar", "Aprobar"), ("generar_pdf", "Generar PDF"), ("convertir_orden", "Convertir a orden")],
    "servicios":     [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar"), ("configurar_repuestos", "Configurar repuestos sugeridos")],
    "inventario":    [("ver", "Ver"), ("crear", "Crear producto"), ("editar", "Editar producto"),
                      ("eliminar", "Eliminar producto"), ("ajustar_stock", "Ajustar stock")],
    "mantenimiento": [("ver", "Ver"), ("crear", "Crear programa"), ("editar", "Editar programa"),
                      ("eliminar", "Eliminar"), ("registrar_historial", "Registrar historial")],
    "alertas":       [("ver", "Ver"), ("crear", "Crear registro"), ("editar", "Editar"), ("eliminar", "Eliminar"), ("configurar", "Configurar"), ("enviar", "Reenviar recordatorio")],
    "reportes":      [("ver", "Ver reportes"), ("exportar_clientes", "Exportar clientes"),
                      ("exportar_vehiculos", "Exportar vehiculos"), ("exportar_ordenes", "Exportar ordenes"),
                      ("exportar_inventario", "Exportar inventario"), ("ver_productividad", "Ver productividad")],
    "usuarios":      [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar"), ("cambiar_password", "Restablecer contraseña")],
    "roles":         [("ver", "Ver"), ("crear", "Crear"), ("editar", "Editar"), ("eliminar", "Eliminar"), ("duplicar", "Duplicar")],
}

# Permisos por rol base
PERMISOS_ADMIN = None  # None = todos los permisos

PERMISOS_GERENTE = {
    "dashboard":     ["ver", "ver_financiero"],
    "clientes":      ["ver", "exportar"],
    "vehiculos":     ["ver"],
    "ordenes":       ["ver", "imprimir_pdf"],
    "cotizaciones":  ["ver", "aprobar", "generar_pdf"],
    "servicios":     ["ver"],
    "inventario":    ["ver"],
    "mantenimiento": ["ver"],
    "alertas":       ["ver"],
    "reportes":      ["ver", "exportar_clientes", "exportar_vehiculos", "exportar_ordenes", "exportar_inventario", "ver_productividad"],
    "usuarios":      [],
    "roles":         [],
}

PERMISOS_RECEPCIONISTA = {
    "dashboard":     ["ver"],
    "clientes":      ["ver", "crear", "editar"],
    "vehiculos":     ["ver", "crear", "editar"],
    "ordenes":       ["ver", "crear", "editar", "eliminar", "imprimir_pdf"],
    "cotizaciones":  ["ver", "crear", "editar", "aprobar", "generar_pdf", "convertir_orden"],
    "servicios":     ["ver"],
    "inventario":    ["ver"],
    "mantenimiento": ["ver", "crear", "editar"],
    "alertas":       ["ver", "crear", "enviar"],
    "reportes":      ["ver"],
    "usuarios":      [],
    "roles":         [],
}

PERMISOS_MECANICO = {
    "dashboard":     ["ver"],
    "clientes":      [],
    "vehiculos":     [],
    "ordenes":       ["ver", "cambiar_estado", "agregar_servicio", "agregar_repuesto"],
    "cotizaciones":  [],
    "servicios":     ["ver"],
    "inventario":    ["ver"],
    "mantenimiento": ["ver", "registrar_historial"],
    "alertas":       [],
    "reportes":      [],
    "usuarios":      [],
    "roles":         [],
}

ROLES_BASE = [
    ("ADMIN",         "Administrador",  "Acceso total al sistema.", True,  PERMISOS_ADMIN),
    ("GERENTE",       "Gerente",        "Vision gerencial: lectura total, exportaciones y aprobaciones.", True, PERMISOS_GERENTE),
    ("RECEPCIONISTA", "Recepcionista",  "Operacion de mostrador: clientes, vehiculos, ordenes y cotizaciones.", True, PERMISOS_RECEPCIONISTA),
    ("MECANICO",      "Mecanico",       "Ejecucion tecnica: ordenes asignadas y mantenimiento.", True, PERMISOS_MECANICO),
]


def crear_datos(apps, schema_editor):
    Modulo = apps.get_model("roles", "Modulo")
    Accion = apps.get_model("roles", "Accion")
    Rol = apps.get_model("roles", "Rol")

    # Crear módulos y sus acciones
    modulos = {}
    for codigo, nombre, icono, url_name, orden in MODULOS:
        m = Modulo.objects.create(
            codigo=codigo, nombre=nombre, icono=icono,
            url_name=url_name, orden=orden, activo=True
        )
        modulos[codigo] = m

    acciones = {}
    for mod_codigo, accs in ACCIONES.items():
        m = modulos[mod_codigo]
        acciones[mod_codigo] = {}
        for acc_codigo, acc_nombre in accs:
            a = Accion.objects.create(modulo=m, codigo=acc_codigo, nombre=acc_nombre)
            acciones[mod_codigo][acc_codigo] = a

    # Crear roles y asignar permisos
    for codigo, nombre, descripcion, es_sistema, permisos in ROLES_BASE:
        rol = Rol.objects.create(
            codigo=codigo, nombre=nombre,
            descripcion=descripcion, es_sistema=es_sistema, activo=True
        )
        if permisos is None:
            # Admin: todos los permisos
            for mod_accs in acciones.values():
                for accion in mod_accs.values():
                    rol.acciones.add(accion)
        else:
            for mod_codigo, acc_codigos in permisos.items():
                for acc_codigo in acc_codigos:
                    if acc_codigo in acciones.get(mod_codigo, {}):
                        rol.acciones.add(acciones[mod_codigo][acc_codigo])


def borrar_datos(apps, schema_editor):
    Modulo = apps.get_model("roles", "Modulo")
    Rol = apps.get_model("roles", "Rol")
    Rol.objects.all().delete()
    Modulo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("roles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_datos, borrar_datos),
    ]
