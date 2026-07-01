"""
Comando: python manage.py seed_data
Pobla la base de datos con datos de demostracion para la tesis.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = "Carga datos de demostracion para el sistema Taller Mecanico"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n[*] TALLER MECANICO - Cargando datos de demostracion...\n"))

        self._crear_usuarios()
        self._crear_clientes()
        self._crear_vehiculos()
        self._crear_servicios()
        self._crear_tipos_mantenimiento()
        self._crear_ordenes()
        self._crear_cotizaciones()
        self._crear_mantenimiento()
        self._crear_alertas()

        self.stdout.write(self.style.SUCCESS("\n[OK] Datos de demostracion cargados correctamente.\n"))
        self.stdout.write("   Ingresa en http://127.0.0.1:8000/auth/login/\n")
        self.stdout.write("   Usuario: admin  |  Contrasena: Admin1234!\n")

    # ------------------------------------------------------------------
    def _crear_usuarios(self):
        from apps.usuarios.models import Usuario
        usuarios = [
            dict(username="mecanico1", first_name="Carlos", last_name="Mendoza", rol="MECANICO",
                 email="carlos@tallermecanico.com", telefono="0991234001", especialidad="Motor y transmision"),
            dict(username="mecanico2", first_name="Luis", last_name="Paredes", rol="MECANICO",
                 email="luis@tallermecanico.com", telefono="0991234002", especialidad="Frenos y suspension"),
            dict(username="recep1", first_name="Maria", last_name="Guzman", rol="RECEPCIONISTA",
                 email="maria@tallermecanico.com", telefono="0991234003"),
            dict(username="recep2", first_name="Sofia", last_name="Torres", rol="RECEPCIONISTA",
                 email="sofia@tallermecanico.com", telefono="0991234004"),
        ]
        for u in usuarios:
            if not Usuario.objects.filter(username=u["username"]).exists():
                obj = Usuario.objects.create_user(password="Demo1234!", **u)
                self.stdout.write(f"   [+] Usuario creado: {u['username']}")
        # Asegurar superusuario admin
        if not Usuario.objects.filter(username="admin").exists():
            u = Usuario.objects.create_superuser(
                username="admin", email="admin@fuelinjection.com", password="Admin1234!",
                first_name="Administrador", last_name="Fuel Injection", rol="ADMIN"
            )
            self.stdout.write("   [+] Superusuario creado: admin")

    def _crear_servicios(self):
        from apps.servicios.models import Servicio
        servicios = [
            ("Cambio de aceite", "Cambio de aceite de motor y revision de niveles."),
            ("Cambio de filtros", "Cambio de filtro de aire, aceite o combustible segun necesidad."),
            ("Diagnostico electronico", "Escaneo OBD2 y diagnostico de codigos de falla."),
            ("Cambio de bateria", "Prueba, desmontaje e instalacion de bateria."),
            ("Cambio de frenos", "Revision y cambio de pastillas, zapatas o componentes de freno."),
            ("Balanceo", "Balanceo de ruedas para reducir vibraciones."),
            ("Alineacion", "Alineacion computarizada de direccion."),
            ("Limpieza de inyectores", "Limpieza preventiva o correctiva de inyectores."),
            ("Cambio de amortiguadores", "Cambio de amortiguadores delanteros o posteriores."),
            ("Revision de suspension", "Inspeccion de amortiguadores, terminales y bujes."),
            ("Cambio de bujias", "Cambio de bujias y revision de encendido."),
            ("Revision electrica", "Diagnostico de luces, alternador, arranque y cableado."),
            ("Mantenimiento preventivo", "Servicio preventivo programado por kilometraje o tiempo."),
            ("Mantenimiento correctivo", "Correccion de fallas mecanicas identificadas."),
            ("Revision de aire acondicionado", "Diagnostico de enfriamiento, fugas y carga de gas."),
            ("Cambio de correa de distribucion", "Cambio de correa, tensores y revision asociada."),
            ("Cambio de liquido de transmision", "Drenaje y reposicion de fluido de transmision."),
            ("Revision de motor", "Inspeccion de funcionamiento, fugas y rendimiento."),
            ("Cambio de refrigerante", "Cambio de refrigerante y purga del sistema."),
            ("Inspeccion precompra", "Revision general del vehiculo antes de compra."),
        ]
        for nombre, descripcion in servicios:
            Servicio.objects.get_or_create(nombre=nombre, defaults={"descripcion": descripcion, "estado": True})
        self.stdout.write(f"   [OK] {Servicio.objects.count()} servicios creados")

    def _crear_clientes(self):
        from apps.clientes.models import Cliente
        clientes_data = [
            ("0912345001", "Juan", "Perez Garcia", "0991100001", "juan.perez@gmail.com", "Cdla. Urdesa Central, Av. Las Monjas"),
            ("0912345002", "Ana", "Rodriguez Lopez", "0991100002", "ana.rodriguez@hotmail.com", "Av. de las Americas 234"),
            ("0912345003", "Roberto", "Sanchez Mora", "0991100003", "r.sanchez@empresa.com", "Urb. Alborada XII Etapa"),
            ("0912345004", "Carmen", "Flores Vega", "0991100004", "carmen.flores@gmail.com", "Miraflores, Calle 5ta"),
            ("0912345005", "Diego", "Herrera Castro", "0991100005", "d.herrera@outlook.com", "Los Ceibos, Mz. 8 V. 3"),
            ("0912345006", "Patricia", "Morales Rios", "0991100006", "p.morales@gmail.com", "Kennedy Norte, Av. San Jorge"),
            ("0912345007", "Fernando", "Cruz Espinoza", "0991100007", "fernando.cruz@mail.com", "Samborondon, Via a Daule"),
            ("0912345008", "Lucia", "Vargas Ponce", "0991100008", "lucia.vargas@gmail.com", "Cdla. Portete, Blk 7"),
            ("0912345009", "Marco", "Jimenez Loor", "0991100009", "marco.jimenez@empresa.ec", "Puerto Azul, Urb. 2"),
            ("0912345010", "Veronica", "Alvarado Suarez", "0991100010", "v.alvarado@gmail.com", "Guasmo Sur, Coop. 15 de Agosto"),
            ("0912345011", "Andres", "Munoz Delgado", "0991100011", "andres.munoz@mail.com", "Sauces 9, Av. Principal"),
            ("0912345012", "Isabella", "Ortiz Naranjo", "0991100012", "i.ortiz@outlook.com", "Av. Constitucion 890"),
            ("0912345013", "Ricardo", "Mendoza Vera", "0991100013", "r.mendoza@gmail.com", "Cdla. Kennedy Norte"),
            ("0912345014", "Gabriela", "Silva Castro", "0991100014", "g.silva@hotmail.com", "Urb. Los Olivos"),
            ("0912345015", "Eduardo", "Torres Mora", "0991100015", "e.torres@empresa.com", "Av. Principal 1234"),
        ]
        for doc, nom, ape, tel, email, dir_ in clientes_data:
            if not Cliente.objects.filter(numero_documento=doc).exists():
                Cliente.objects.create(
                    numero_documento=doc, nombres=nom, apellidos=ape,
                    telefono=tel, email=email, direccion=dir_, ciudad="Guayaquil"
                )
        self.stdout.write(f"   [OK] {Cliente.objects.count()} clientes creados")

    def _crear_vehiculos(self):
        from apps.vehiculos.models import Vehiculo
        from apps.clientes.models import Cliente
        clientes = list(Cliente.objects.all())
        vehiculos_data = [
            ("GUZ-1234", "Toyota", "Corolla", 2018, "Blanco", "AUTOMOVIL", "GASOLINA", 85000),
            ("GUZ-5678", "Chevrolet", "Aveo", 2016, "Rojo", "AUTOMOVIL", "GASOLINA", 120000),
            ("GUZ-9012", "Hyundai", "Tucson", 2020, "Gris", "SUV", "GASOLINA", 45000),
            ("GBA-3456", "Nissan", "Frontier", 2019, "Negro", "CAMIONETA", "DIESEL", 70000),
            ("GBA-7890", "Kia", "Sportage", 2021, "Azul", "SUV", "GASOLINA", 30000),
            ("GUZ-2345", "Mazda", "CX-5", 2017, "Plateado", "SUV", "GASOLINA", 95000),
            ("GUZ-6789", "Ford", "Ranger", 2020, "Blanco", "CAMIONETA", "DIESEL", 55000),
            ("GBA-0123", "Volkswagen", "Jetta", 2019, "Negro", "AUTOMOVIL", "GASOLINA", 60000),
            ("GUZ-4567", "Honda", "CR-V", 2022, "Blanco Perla", "SUV", "GASOLINA", 18000),
            ("GBA-8901", "Mitsubishi", "L200", 2018, "Gris", "CAMIONETA", "DIESEL", 88000),
            ("GUZ-1357", "Toyota", "Hilux", 2021, "Blanco", "CAMIONETA", "DIESEL", 40000),
            ("GUZ-2468", "Chevrolet", "D-MAX", 2017, "Negro", "CAMIONETA", "DIESEL", 110000),
            ("GBA-3579", "Suzuki", "Vitara", 2020, "Rojo", "SUV", "GASOLINA", 35000),
            ("GBA-4680", "Renault", "Duster", 2019, "Azul", "SUV", "GASOLINA", 65000),
            ("GUZ-5791", "Hyundai", "Santa Fe", 2016, "Gris Oscuro", "SUV", "GASOLINA", 130000),
        ]
        for i, (placa, marca, modelo, anio, color, tipo, comb, km) in enumerate(vehiculos_data):
            if not Vehiculo.objects.filter(placa=placa).exists():
                cliente = clientes[i % len(clientes)]
                Vehiculo.objects.create(
                    placa=placa, marca=marca, modelo=modelo, anio=anio, color=color,
                    tipo_vehiculo=tipo, tipo_combustible=comb, kilometraje_actual=km,
                    cliente=cliente
                )
        self.stdout.write(f"   [OK] {Vehiculo.objects.count()} vehiculos creados")

    def _crear_tipos_mantenimiento(self):
        from apps.mantenimiento.models import TipoServicioMantenimiento
        tipos = [
            ("Cambio de aceite y filtro", 5000, 90),
            ("Cambio de filtro de aire", 15000, 365),
            ("Cambio de filtro de combustible", 20000, 365),
            ("Revision de frenos", 20000, 180),
            ("Cambio de pastillas de freno", 30000, 0),
            ("Alineacion y balanceo", 10000, 180),
            ("Cambio de correa de distribucion", 60000, 0),
            ("Revision de bateria", 0, 180),
            ("Cambio de bujias", 30000, 365),
            ("Revision general (mantenimiento 30.000 km)", 30000, 365),
            ("Revision de sistema de enfriamiento", 20000, 365),
            ("Cambio de liquido de frenos", 40000, 730),
            ("Revision de suspension", 30000, 365),
            ("Cambio de correa de accesorios", 60000, 365),
            ("Revision de transmision", 60000, 365),
        ]
        for nombre, km, dias in tipos:
            TipoServicioMantenimiento.objects.get_or_create(
                nombre=nombre,
                defaults={"intervalo_km_recomendado": km, "intervalo_dias_recomendado": dias}
            )
        self.stdout.write(f"   [OK] {TipoServicioMantenimiento.objects.count()} tipos de mantenimiento creados")

    def _crear_ordenes(self):
        from apps.ordenes.models import OrdenTrabajo, DetalleOrdenTrabajo
        from apps.vehiculos.models import Vehiculo
        from apps.usuarios.models import Usuario
        from apps.servicios.models import Servicio

        if OrdenTrabajo.objects.count() >= 15:
            self.stdout.write("   [OK] Ordenes ya existentes, omitiendo...")
            return

        tecnicos = list(Usuario.objects.filter(rol="MECANICO"))
        recepcionistas = list(Usuario.objects.filter(rol="RECEPCIONISTA"))
        vehiculos = list(Vehiculo.objects.all())
        servicios = list(Servicio.objects.filter(estado=True))

        ordenes_data = [
            ("ENTREGADA", "MEDIA", "MECANICA_GENERAL", "Cambio de aceite y revision general", "Aceite desgastado, filtros en mal estado", Decimal("45.00"), Decimal("35.00"), -15),
            ("ENTREGADA", "ALTA", "MECANICA_GENERAL", "Falla en el sistema de frenos, ruido al frenar", "Pastillas de freno desgastadas al limite, disco rayado lado derecho", Decimal("80.00"), Decimal("120.00"), -10),
            ("FINALIZADA", "MEDIA", "MANTENIMIENTO_PREVENTIVO", "Alineacion y balanceo, vibracion al manejar", "Desbalance en rueda delantera derecha, eje levemente doblado", Decimal("35.00"), Decimal("0.00"), -7),
            ("EN_PROCESO", "URGENTE", "DIAGNOSTICO", "Motor no enciende, bateria descargada", "Bateria sulfatada, alternador con falla intermitente", Decimal("60.00"), Decimal("180.00"), -3),
            ("EN_PROCESO", "ALTA", "MECANICA_GENERAL", "Revision transmision, cambios duros", "Liquido de transmision contaminado, filtro obstruido", Decimal("70.00"), Decimal("45.00"), -2),
            ("RECIBIDA", "MEDIA", "DIAGNOSTICO", "Aire acondicionado no enfria correctamente", "Pendiente diagnostico del sistema de refrigeracion", Decimal("0.00"), Decimal("0.00"), -1),
            ("RECIBIDA", "BAJA", "MECANICA_GENERAL", "Revision de luces delanteras, faro quemado", "Pendiente inspeccion del cableado y reemplazo de bombillas", Decimal("0.00"), Decimal("0.00"), 0),
            ("EN_PROCESO", "ALTA", "MECANICA_GENERAL", "Chequeo motor, testigo de aceite encendido", "Fuga leve en empaque de valvulas, nivel bajo de aceite", Decimal("90.00"), Decimal("55.00"), -4),
            ("FINALIZADA", "MEDIA", "MANTENIMIENTO_PREVENTIVO", "Revision completa pre-venta del vehiculo", "Suspension delantera con holgura, amortiguadores al limite", Decimal("50.00"), Decimal("200.00"), -5),
            ("RECIBIDA", "MEDIA", "MANTENIMIENTO_PREVENTIVO", "Revision 30.000 km programada", "Mantenimiento preventivo completo programado", Decimal("0.00"), Decimal("0.00"), 0),
            ("ENTREGADA", "ALTA", "MECANICA_GENERAL", "Correa de distribucion, ruido en motor frio", "Correa de distribucion con desgaste, tensores flojos", Decimal("120.00"), Decimal("95.00"), -20),
            ("EN_PROCESO", "URGENTE", "DIAGNOSTICO", "Recalentamiento del motor, temperatura alta", "Termostato danado, radiador con fuga pequena", Decimal("85.00"), Decimal("140.00"), -1),
            ("COTIZADA", "MEDIA", "COLISION_ENDEREZADA", "Revision latoneria puerta delantera", "Golpe leve en puerta, requiere pintura", Decimal("0.00"), Decimal("0.00"), 0),
            ("APROBADA", "ALTA", "PINTURA", "Pintura completa capo y parachoques", "Rayaduras profundas, oxidacion en capo", Decimal("150.00"), Decimal("200.00"), -5),
            ("ESPERANDO_REPUESTOS", "URGENTE", "MECANICA_GENERAL", "Cambio kit de embrague", "Embrague patinando, requiere repuestos importados", Decimal("120.00"), Decimal("350.00"), -8),
        ]

        detalles_por_orden = [
            [("SERVICIO", "Cambio de aceite sintetico 5W30", 1, Decimal("25.00")), ("REPUESTO", "Filtro de aceite Toyota", 1, Decimal("15.00")), ("REPUESTO", "Aceite sintetico 5W30 (4 litros)", 4, Decimal("8.00"))],
            [("SERVICIO", "Cambio pastillas freno delantero", 1, Decimal("50.00")), ("REPUESTO", "Pastillas freno Brembo delantera", 1, Decimal("65.00")), ("SERVICIO", "Rectificacion disco derecho", 1, Decimal("30.00")), ("REPUESTO", "Kit reparacion frenos", 1, Decimal("55.00"))],
            [("SERVICIO", "Alineacion computarizada", 1, Decimal("20.00")), ("SERVICIO", "Balanceo 4 ruedas", 1, Decimal("15.00"))],
            [("SERVICIO", "Diagnostico electrico completo", 1, Decimal("40.00")), ("REPUESTO", "Bateria N70 12V 70Ah", 1, Decimal("150.00")), ("SERVICIO", "Revision y prueba alternador", 1, Decimal("20.00"))],
            [("SERVICIO", "Cambio liquido de transmision", 1, Decimal("45.00")), ("REPUESTO", "Liquido ATF Dexron VI (3 litros)", 3, Decimal("12.00")), ("REPUESTO", "Filtro transmision automatica", 1, Decimal("33.00"))],
            [], [],
            [("SERVICIO", "Diagnostico motor OBD2", 1, Decimal("30.00")), ("REPUESTO", "Empaque de valvulas motor", 1, Decimal("45.00")), ("SERVICIO", "Sellado fuga aceite motor", 1, Decimal("60.00"))],
            [("SERVICIO", "Inspeccion suspension completa", 1, Decimal("30.00")), ("REPUESTO", "Amortiguadores delanteros (par)", 1, Decimal("160.00")), ("REPUESTO", "Terminales direccion (par)", 1, Decimal("40.00"))],
            [],
            [("SERVICIO", "Cambio correa distribucion", 1, Decimal("80.00")), ("REPUESTO", "Kit distribucion completo", 1, Decimal("75.00")), ("SERVICIO", "Revision bomba de agua", 1, Decimal("20.00"))],
            [("SERVICIO", "Diagnostico sistema de enfriamiento", 1, Decimal("35.00")), ("REPUESTO", "Termostato original", 1, Decimal("45.00")), ("REPUESTO", "Kit reparacion radiador", 1, Decimal("60.00")), ("SERVICIO", "Cambio refrigerante completo", 1, Decimal("50.00"))],
            [("SERVICIO", "Revision latoneria puerta", 1, Decimal("40.00")), ("REPUESTO", "Material de pintura", 1, Decimal("80.00"))],
            [("SERVICIO", "Preparacion superficie", 1, Decimal("50.00")), ("REPUESTO", "Pintura original capo", 1, Decimal("120.00")), ("REPUESTO", "Pintura parachoques", 1, Decimal("80.00"))],
            [("SERVICIO", "Desmontaje transmision", 1, Decimal("60.00")), ("REPUESTO", "Kit embrague completo", 1, Decimal("280.00")), ("REPUESTO", "Rodamiento piloto", 1, Decimal("45.00")), ("SERVICIO", "Montaje y ajuste", 1, Decimal("60.00"))],
        ]

        hoy = date.today()
        for i, (estado, prioridad, tipo_trabajo, descripcion, diagnostico, costo_mo, costo_rep, dias_atras) in enumerate(ordenes_data):
            v = vehiculos[i % len(vehiculos)]
            fecha = timezone.now() - timedelta(days=abs(dias_atras))
            recep = recepcionistas[i % len(recepcionistas)] if recepcionistas else None
            tecnico = tecnicos[i % len(tecnicos)] if tecnicos else None

            orden = OrdenTrabajo.objects.create(
                vehiculo=v, cliente=v.cliente,
                servicio=servicios[i % len(servicios)] if servicios else None,
                tecnico_asignado=tecnico, recepcionista=recep,
                estado=estado, prioridad=prioridad, tipo_trabajo=tipo_trabajo,
                kilometraje_ingreso=v.kilometraje_actual - random.randint(0, 500),
                descripcion_problema=descripcion,
                diagnostico=diagnostico if diagnostico else "",
                fecha_estimada_entrega=hoy + timedelta(days=random.randint(1, 5)),
                precio=costo_mo,
                costo_mano_obra=costo_mo,
                costo_repuestos=costo_rep,
            )
            if estado == "ENTREGADA":
                orden.fecha_entrega_real = fecha + timedelta(days=random.randint(1, 3))
                orden.save(update_fields=["fecha_entrega_real"])

            for tipo, desc, cant, precio in (detalles_por_orden[i] if i < len(detalles_por_orden) else []):
                DetalleOrdenTrabajo.objects.create(orden=orden, tipo=tipo, descripcion=desc, cantidad=cant, precio_unitario=precio)

        self.stdout.write(f"   [OK] {OrdenTrabajo.objects.count()} ordenes de trabajo creadas")

    def _crear_cotizaciones(self):
        from apps.cotizaciones.models import Cotizacion, DetalleCotizacion
        from apps.vehiculos.models import Vehiculo
        from apps.usuarios.models import Usuario

        if Cotizacion.objects.count() >= 15:
            self.stdout.write("   [OK] Cotizaciones ya existentes, omitiendo...")
            return

        vehiculos = list(Vehiculo.objects.all())
        recep = Usuario.objects.filter(rol="RECEPCIONISTA").first()

        cotizaciones_data = [
            ("APROBADA", vehiculos[0], "Reparacion completa sistema de frenos y suspension delantera"),
            ("PENDIENTE", vehiculos[2], "Cambio de correa de distribucion, bomba de agua y revision general"),
            ("RECHAZADA", vehiculos[4], "Pintura y latoneria puerta trasera izquierda"),
            ("PENDIENTE", vehiculos[6], "Overhaul motor completo, revision de culata y pistones"),
            ("APROBADA", vehiculos[8], "Revision completa 60.000 km"),
            ("PENDIENTE", vehiculos[10], "Cambio kit de embrague y rodamiento piloto"),
            ("VENCIDA", vehiculos[12], "Pintura capo y parachoques"),
            ("PENDIENTE", vehiculos[1], "Cambio amortiguadores y terminales"),
            ("APROBADA", vehiculos[3], "Revision sistema de aire acondicionado"),
            ("PENDIENTE", vehiculos[5], "Cambio correa de accesorios y tensionadores"),
            ("RECHAZADA", vehiculos[7], "Overhaul transmision automatica"),
            ("PENDIENTE", vehiculos[9], "Revision general pre-compra"),
            ("APROBADA", vehiculos[11], "Cambio bateria y revision sistema electrico"),
            ("PENDIENTE", vehiculos[13], "Cambio liquido de frenos y purga"),
            ("VENCIDA", vehiculos[14], "Revision suspension y direccion"),
        ]

        detalles = [
            [("SERVICIO", "Mano de obra frenos completos", 1, Decimal("120.00")), ("REPUESTO", "Kit frenos completo 4 ruedas", 1, Decimal("280.00"))],
            [("SERVICIO", "Cambio correa distribucion", 1, Decimal("100.00")), ("REPUESTO", "Kit distribucion original", 1, Decimal("180.00")), ("REPUESTO", "Bomba de agua original", 1, Decimal("95.00"))],
            [("SERVICIO", "Pintura puerta + mano de obra", 1, Decimal("200.00")), ("REPUESTO", "Material pintura y latoneria", 1, Decimal("150.00"))],
            [("SERVICIO", "Overhaul motor completo", 1, Decimal("600.00")), ("REPUESTO", "Kit de pistones y aros", 1, Decimal("350.00")), ("REPUESTO", "Juego juntas motor", 1, Decimal("120.00"))],
            [("SERVICIO", "Revision 60.000 km completa", 1, Decimal("150.00")), ("REPUESTO", "Kit mantenimiento completo", 1, Decimal("200.00"))],
            [("SERVICIO", "Cambio kit embrague", 1, Decimal("80.00")), ("REPUESTO", "Kit embrague original", 1, Decimal("280.00")), ("REPUESTO", "Rodamiento piloto", 1, Decimal("45.00"))],
            [("SERVICIO", "Pintura capo y parachoques", 1, Decimal("180.00")), ("REPUESTO", "Material pintura premium", 1, Decimal("220.00"))],
            [("SERVICIO", "Cambio amortiguadores", 1, Decimal("100.00")), ("REPUESTO", "Amortiguadores (par)", 1, Decimal("180.00")), ("REPUESTO", "Terminales (par)", 1, Decimal("60.00"))],
            [("SERVICIO", "Revision aire acondicionado", 1, Decimal("60.00")), ("REPUESTO", "Gas refrigerante", 1, Decimal("80.00")), ("REPUESTO", "Kit reparacion", 1, Decimal("45.00"))],
            [("SERVICIO", "Cambio correa accesorios", 1, Decimal("50.00")), ("REPUESTO", "Correa accesorios", 1, Decimal("45.00")), ("REPUESTO", "Tensionadores (set)", 1, Decimal("85.00"))],
            [("SERVICIO", "Overhaul transmision", 1, Decimal("500.00")), ("REPUESTO", "Kit reparacion transmision", 1, Decimal("400.00"))],
            [("SERVICIO", "Inspeccion pre-compra", 1, Decimal("80.00")), ("REPUESTO", "Diagnostico computarizado", 1, Decimal("40.00"))],
            [("SERVICIO", "Cambio bateria", 1, Decimal("40.00")), ("REPUESTO", "Bateria premium", 1, Decimal("150.00"))],
            [("SERVICIO", "Cambio liquido frenos", 1, Decimal("45.00")), ("REPUESTO", "Liquido frenos DOT4", 1, Decimal("35.00"))],
            [("SERVICIO", "Revision suspension", 1, Decimal("70.00")), ("REPUESTO", "Kit revision direccion", 1, Decimal("120.00"))],
        ]

        for i, (estado, vehiculo, descripcion) in enumerate(cotizaciones_data):
            cot = Cotizacion.objects.create(
                vehiculo=vehiculo, cliente=vehiculo.cliente,
                elaborado_por=recep, estado=estado,
                descripcion=descripcion,
                fecha_validez=date.today() + timedelta(days=15),
            )
            if estado == "APROBADA":
                cot.fecha_aprobacion = timezone.now() - timedelta(days=2)
                cot.save(update_fields=["fecha_aprobacion"])
            for tipo, desc, cant, precio in detalles[i]:
                DetalleCotizacion.objects.create(cotizacion=cot, tipo=tipo, descripcion=desc, cantidad=cant, precio_unitario=precio)

        self.stdout.write(f"   [OK] {Cotizacion.objects.count()} cotizaciones creadas")

    def _crear_mantenimiento(self):
        from apps.mantenimiento.models import TipoServicioMantenimiento, ProgramaMantenimiento, HistorialMantenimiento
        from apps.vehiculos.models import Vehiculo
        from apps.usuarios.models import Usuario

        tipos = list(TipoServicioMantenimiento.objects.all())
        vehiculos = list(Vehiculo.objects.all())
        tecnico = Usuario.objects.filter(rol="MECANICO").first()

        if HistorialMantenimiento.objects.count() >= 15:
            self.stdout.write("   [OK] Historial ya existente, omitiendo...")
            return

        # Historial de mantenimiento
        historial_data = [
            (vehiculos[0], tipos[0], 80000, date.today() - timedelta(days=20), 85000, Decimal("45.00")),
            (vehiculos[1], tipos[0], 115000, date.today() - timedelta(days=45), 120000, Decimal("45.00")),
            (vehiculos[2], tipos[3], 40000, date.today() - timedelta(days=30), 60000, Decimal("80.00")),
            (vehiculos[0], tipos[1], 70000, date.today() - timedelta(days=90), 85000, Decimal("25.00")),
            (vehiculos[3], tipos[0], 65000, date.today() - timedelta(days=15), 70000, Decimal("50.00")),
            (vehiculos[4], tipos[8], 25000, date.today() - timedelta(days=60), 55000, Decimal("40.00")),
            (vehiculos[5], tipos[9], 90000, date.today() - timedelta(days=10), 120000, Decimal("180.00")),
            (vehiculos[6], tipos[0], 50000, date.today() - timedelta(days=25), 55000, Decimal("45.00")),
            (vehiculos[7], tipos[3], 55000, date.today() - timedelta(days=35), 60000, Decimal("80.00")),
            (vehiculos[8], tipos[0], 15000, date.today() - timedelta(days=5), 20000, Decimal("45.00")),
            (vehiculos[9], tipos[1], 45000, date.today() - timedelta(days=120), 60000, Decimal("25.00")),
            (vehiculos[10], tipos[8], 35000, date.today() - timedelta(days=45), 40000, Decimal("40.00")),
            (vehiculos[11], tipos[0], 100000, date.today() - timedelta(days=15), 105000, Decimal("50.00")),
            (vehiculos[12], tipos[10], 65000, date.today() - timedelta(days=30), 70000, Decimal("60.00")),
            (vehiculos[13], tipos[11], 35000, date.today() - timedelta(days=60), 40000, Decimal("45.00")),
        ]

        for v, tipo, km, fecha, prox_km, costo in historial_data:
            HistorialMantenimiento.objects.create(
                vehiculo=v, tipo_servicio=tipo,
                descripcion=f"{tipo.nombre} realizado segun mantenimiento programado",
                km_al_servicio=km, proximo_km_sugerido=prox_km,
                fecha_servicio=fecha, tecnico=tecnico, costo=costo
            )

        # Programas de mantenimiento
        programas_data = [
            (vehiculos[0], tipos[0], 80000, date.today() - timedelta(days=20), "AL_DIA"),
            (vehiculos[1], tipos[0], 115000, date.today() - timedelta(days=45), "PROXIMO"),
            (vehiculos[2], tipos[3], 40000, date.today() - timedelta(days=30), "AL_DIA"),
            (vehiculos[3], tipos[0], 65000, date.today() - timedelta(days=15), "AL_DIA"),
            (vehiculos[4], tipos[1], 20000, date.today() - timedelta(days=400), "VENCIDO"),
            (vehiculos[5], tipos[9], 90000, date.today() - timedelta(days=10), "AL_DIA"),
            (vehiculos[6], tipos[0], 50000, date.today() - timedelta(days=100), "VENCIDO"),
            (vehiculos[7], tipos[3], 55000, date.today() - timedelta(days=35), "AL_DIA"),
            (vehiculos[8], tipos[0], 15000, date.today() - timedelta(days=5), "AL_DIA"),
            (vehiculos[9], tipos[1], 45000, date.today() - timedelta(days=120), "VENCIDO"),
            (vehiculos[10], tipos[8], 35000, date.today() - timedelta(days=45), "AL_DIA"),
            (vehiculos[11], tipos[0], 100000, date.today() - timedelta(days=15), "PROXIMO"),
            (vehiculos[12], tipos[10], 65000, date.today() - timedelta(days=30), "AL_DIA"),
            (vehiculos[13], tipos[11], 35000, date.today() - timedelta(days=60), "PROXIMO"),
            (vehiculos[14], tipos[0], 125000, date.today() - timedelta(days=80), "VENCIDO"),
        ]

        for v, tipo, ultimo_km, ultima_fecha, estado in programas_data:
            intervalo_km = tipo.intervalo_km_recomendado or 5000
            ProgramaMantenimiento.objects.get_or_create(
                vehiculo=v, tipo_servicio=tipo,
                defaults={
                    "ultimo_km": ultimo_km,
                    "ultima_fecha": ultima_fecha,
                    "proximo_km": ultimo_km + intervalo_km,
                    "intervalo_km": intervalo_km,
                    "estado": estado,
                }
            )

        self.stdout.write(f"   [OK] {HistorialMantenimiento.objects.count()} registros de historial creados")
        self.stdout.write(f"   [OK] {ProgramaMantenimiento.objects.count()} programas de mantenimiento creados")

    def _crear_alertas(self):
        from apps.alertas.models import Alerta
        from apps.vehiculos.models import Vehiculo
        from apps.usuarios.models import Usuario
        from apps.ordenes.models import OrdenTrabajo

        if Alerta.objects.count() >= 15:
            self.stdout.write("   [OK] Alertas ya existentes, omitiendo...")
            return

        admin = Usuario.objects.filter(rol="ADMIN").first()
        recep = Usuario.objects.filter(rol="RECEPCIONISTA").first()
        tecnicos = list(Usuario.objects.filter(rol="MECANICO"))
        vehiculos = list(Vehiculo.objects.all())
        ordenes_pendientes = list(OrdenTrabajo.objects.filter(estado="RECIBIDA"))

        alertas_data = [
            (Alerta.TipoAlerta.MANTENIMIENTO_VENCIDO, Alerta.Nivel.DANGER, vehiculos[4],
             f"Mantenimiento VENCIDO: {vehiculos[4].placa} ({vehiculos[4].descripcion_corta}) — Cambio de filtro de aire supero el intervalo recomendado", admin),
            (Alerta.TipoAlerta.MANTENIMIENTO_VENCIDO, Alerta.Nivel.DANGER, vehiculos[6],
             f"Mantenimiento VENCIDO: {vehiculos[6].placa} ({vehiculos[6].descripcion_corta}) — Cambio de aceite no realizado en 100+ dias", recep),
            (Alerta.TipoAlerta.PROXIMO_MANTENIMIENTO, Alerta.Nivel.WARNING, vehiculos[1],
             f"Proximo mantenimiento: {vehiculos[1].placa} — Cambio de aceite en los proximos 500 km", recep),
            (Alerta.TipoAlerta.RETRASO, Alerta.Nivel.WARNING, vehiculos[3],
             f"Vehiculo {vehiculos[3].placa} lleva mas de 3 dias en taller sin actualizacion de estado", admin),
            (Alerta.TipoAlerta.ORDEN_PENDIENTE, Alerta.Nivel.INFO, vehiculos[5],
             f"Nueva orden pendiente de asignacion para {vehiculos[5].placa}", tecnicos[0] if tecnicos else admin),
            (Alerta.TipoAlerta.VEHICULO_LISTO, Alerta.Nivel.INFO, vehiculos[2],
             f"Vehiculo {vehiculos[2].placa} ({vehiculos[2].descripcion_corta}) esta LISTO para entrega", recep),
            (Alerta.TipoAlerta.PROXIMO_MANTENIMIENTO, Alerta.Nivel.WARNING, vehiculos[9],
             f"Proximo mantenimiento: {vehiculos[9].placa} — Cambio de filtro de aire proximos 1000 km", admin),
            (Alerta.TipoAlerta.MANTENIMIENTO_VENCIDO, Alerta.Nivel.DANGER, vehiculos[14],
             f"Mantenimiento VENCIDO: {vehiculos[14].placa} — Cambio de aceite vencido por 80 dias", recep),
            (Alerta.TipoAlerta.ORDEN_PENDIENTE, Alerta.Nivel.INFO, vehiculos[7],
             f"Orden pendiente para {vehiculos[7].placa} requiere asignacion de tecnico", tecnicos[1] if len(tecnicos) > 1 else admin),
            (Alerta.TipoAlerta.VEHICULO_LISTO, Alerta.Nivel.INFO, vehiculos[0],
             f"Vehiculo {vehiculos[0].placa} ({vehiculos[0].descripcion_corta}) esta LISTO para entrega", recep),
            (Alerta.TipoAlerta.PROXIMO_MANTENIMIENTO, Alerta.Nivel.WARNING, vehiculos[11],
             f"Proximo mantenimiento: {vehiculos[11].placa} — Cambio de aceite en proximos 500 km", admin),
            (Alerta.TipoAlerta.RETRASO, Alerta.Nivel.WARNING, vehiculos[10],
             f"Vehiculo {vehiculos[10].placa} lleva 5 dias en taller sin actualizacion", admin),
            (Alerta.TipoAlerta.ORDEN_PENDIENTE, Alerta.Nivel.INFO, vehiculos[12],
             f"Nueva orden recibida para {vehiculos[12].placa}", tecnicos[0] if tecnicos else admin),
            (Alerta.TipoAlerta.VEHICULO_LISTO, Alerta.Nivel.INFO, vehiculos[8],
             f"Vehiculo {vehiculos[8].placa} ({vehiculos[8].descripcion_corta}) esta LISTO para entrega", recep),
            (Alerta.TipoAlerta.PROXIMO_MANTENIMIENTO, Alerta.Nivel.WARNING, vehiculos[13],
             f"Proximo mantenimiento: {vehiculos[13].placa} — Cambio liquido frenos proximos 30 dias", admin),
        ]

        for tipo, nivel, vehiculo, mensaje, dest in alertas_data:
            Alerta.objects.create(
                tipo=tipo, nivel=nivel, vehiculo=vehiculo,
                mensaje=mensaje, destinatario=dest, activa=True,
            )

        self.stdout.write(f"   [OK] {Alerta.objects.count()} alertas creadas")
