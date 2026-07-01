# -*- coding: utf-8 -*-
"""
Management command: crear_datos_prueba_alertas
Crea cliente, vehiculo, OT y registro de mantenimiento de prueba
con proximo mantenimiento en exactamente 5 dias.

Uso:
    python manage.py crear_datos_prueba_alertas
"""
import sys
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Crea datos de prueba para el modulo de alertas/recordatorios."

    def handle(self, *args, **options):
        # Forzar salida UTF-8 en Windows
        if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

        from apps.clientes.models import Cliente
        from apps.vehiculos.models import Vehiculo
        from apps.ordenes.models import OrdenTrabajo, DetalleOrdenTrabajo
        from apps.alertas.models import (
            RegistroMantenimiento, RecordatorioMantenimiento, ConfiguracionRecordatorio
        )
        from apps.usuarios.models import Usuario

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("  Fuel Injection - Datos de Prueba: Modulo Alertas")
        self.stdout.write("=" * 60 + "\n")

        # Configuracion
        config = ConfiguracionRecordatorio.obtener()
        self.stdout.write(f"  Configuracion: {config.dias_anticipacion} dias de anticipacion")

        # ── Cliente ────────────────────────────────────────────────
        cliente, creado = Cliente.objects.get_or_create(
            numero_documento="0988794071",
            defaults={
                "tipo_documento": "CEDULA",
                "nombres": "Dennys Samuel",
                "apellidos": "Valencia Mosquera",
                "telefono": "0988794071",
                "email": "SamuelValencia780@gmail.com",
                "direccion": "Av. de las Americas y Portete, Guayaquil",
                "ciudad": "Guayaquil",
                "observaciones": "Cliente de prueba - modulo alertas",
                "activo": True,
            }
        )
        tag = "CREADO" if creado else "YA EXISTIA"
        self.stdout.write(self.style.SUCCESS(
            f"  [OK] Cliente: {cliente.nombres} {cliente.apellidos} [{tag}]"
        ))

        # ── Vehiculo ───────────────────────────────────────────────
        vehiculo, creado = Vehiculo.objects.get_or_create(
            placa="ABC-1234",
            defaults={
                "cliente": cliente,
                "marca": "Chevrolet",
                "modelo": "Aveo Emotion",
                "anio": 2022,
                "color": "Blanco",
                "tipo_vehiculo": "AUTOMOVIL",
                "tipo_combustible": "GASOLINA",
                "numero_vin": "9BWZZZ377VT004251",
                "numero_motor": "F16D3-C123456",
                "kilometraje_actual": 45320,
                "cilindraje": "1.6",
                "transmision": "MANUAL",
                "observaciones": "Vehiculo de prueba",
                "activo": True,
            }
        )
        tag = "CREADO" if creado else "YA EXISTIA"
        self.stdout.write(self.style.SUCCESS(
            f"  [OK] Vehiculo: {vehiculo.placa} - {vehiculo.marca} {vehiculo.modelo} [{tag}]"
        ))

        # ── Orden de Trabajo ───────────────────────────────────────
        intervalo_dias = 90
        dias_atras = intervalo_dias - config.dias_anticipacion
        fecha_ingreso = timezone.now() - timedelta(days=dias_atras)

        recepcionista = Usuario.objects.filter(is_active=True).first()

        orden_existente = OrdenTrabajo.objects.filter(
            vehiculo=vehiculo,
            tipo_trabajo="MANTENIMIENTO_PREVENTIVO",
            estado="FINALIZADA",
        ).first()

        if not orden_existente:
            orden = OrdenTrabajo.objects.create(
                vehiculo=vehiculo,
                cliente=cliente,
                recepcionista=recepcionista,
                tipo_trabajo="MANTENIMIENTO_PREVENTIVO",
                estado="FINALIZADA",
                prioridad="MEDIA",
                kilometraje_ingreso=45320,
                descripcion_problema="Mantenimiento preventivo programado",
                diagnostico="Vehiculo en buen estado. Se realizan servicios preventivos.",
                observaciones="Datos de prueba generados automaticamente.",
                costo_mano_obra=80.00,
                costo_repuestos=95.00,
                descuento=0,
                fecha_estimada_entrega=fecha_ingreso.date(),
                fecha_entrega_real=fecha_ingreso,
            )
            OrdenTrabajo.objects.filter(pk=orden.pk).update(fecha_ingreso=fecha_ingreso)
            orden.refresh_from_db()

            servicios = [
                ("SERVICIO", "Cambio de aceite de motor 10W-40", 1, 25.00),
                ("SERVICIO", "Mano de obra - cambio filtros y limpieza", 1, 55.00),
                ("REPUESTO", "Filtro de aceite Bosch", 1, 15.00),
                ("REPUESTO", "Filtro de aire Mann", 1, 22.00),
                ("REPUESTO", "Aceite de motor 10W-40 (4 litros)", 4, 14.50),
                ("SERVICIO", "Limpieza y regulacion de frenos delanteros", 1, 35.00),
            ]
            for tipo, desc, cant, precio in servicios:
                DetalleOrdenTrabajo.objects.create(
                    orden=orden, tipo=tipo, descripcion=desc,
                    cantidad=cant, precio_unitario=precio,
                )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Orden de Trabajo: {orden.numero_orden} [CREADA]"))
        else:
            orden = orden_existente
            self.stdout.write(self.style.WARNING(f"  [--] Orden: {orden.numero_orden} [YA EXISTIA]"))

        # ── Registro de Mantenimiento ──────────────────────────────
        registro_existente = RegistroMantenimiento.objects.filter(
            vehiculo=vehiculo, activo=True
        ).first()

        fecha_mantenimiento = (timezone.now() - timedelta(days=dias_atras)).date()
        fecha_proximo = date.today() + timedelta(days=config.dias_anticipacion)

        if not registro_existente:
            descripcion = (
                "- Cambio de aceite de motor 10W-40 (4 litros)\n"
                "- Cambio de filtro de aceite Bosch\n"
                "- Cambio de filtro de aire Mann\n"
                "- Limpieza y regulacion de frenos delanteros"
            )
            registro = RegistroMantenimiento.objects.create(
                orden=orden,
                vehiculo=vehiculo,
                cliente=cliente,
                tipo_mantenimiento="Mantenimiento Preventivo",
                descripcion_trabajos=descripcion,
                fecha_mantenimiento=fecha_mantenimiento,
                kilometraje_mantenimiento=45320,
                tipo_intervalo="DIAS",
                intervalo_dias=intervalo_dias,
                fecha_proximo_mantenimiento=fecha_proximo,
                kilometraje_proximo_mantenimiento=50320,
                canal_envio="EMAIL",
                activo=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f"  [OK] Registro de mantenimiento creado | Proximo: {fecha_proximo} (en {config.dias_anticipacion} dias)"
            ))
        else:
            registro = registro_existente
            registro.fecha_proximo_mantenimiento = fecha_proximo
            registro.save(update_fields=["fecha_proximo_mantenimiento"])
            self.stdout.write(self.style.WARNING(
                f"  [--] Registro actualizado | Proximo: {fecha_proximo} (en {config.dias_anticipacion} dias)"
            ))

        # ── Recordatorio pendiente ─────────────────────────────────
        recordatorio_existente = RecordatorioMantenimiento.objects.filter(
            registro=registro, estado="PENDIENTE"
        ).first()

        if not recordatorio_existente:
            RecordatorioMantenimiento.objects.create(
                registro=registro,
                canal="EMAIL",
                estado="PENDIENTE",
                fecha_programada=date.today(),
                intento_numero=1,
            )
            self.stdout.write(self.style.SUCCESS("  [OK] Recordatorio pendiente creado"))
        else:
            self.stdout.write(self.style.WARNING("  [--] Ya existe un recordatorio pendiente"))

        # ── Resumen ───────────────────────────────────────────────
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("  DATOS DE PRUEBA CREADOS CORRECTAMENTE"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Cliente  : {cliente.nombres} {cliente.apellidos}")
        self.stdout.write(f"  Email    : {cliente.email}")
        self.stdout.write(f"  Telefono : {cliente.telefono}")
        self.stdout.write(f"  Vehiculo : {vehiculo.placa} - {vehiculo.marca} {vehiculo.modelo} {vehiculo.anio}")
        self.stdout.write(f"  OT       : {orden.numero_orden}")
        self.stdout.write(f"  Proximo  : {fecha_proximo} (en {config.dias_anticipacion} dias)")
        self.stdout.write("")
        self.stdout.write("  Para enviar el recordatorio ahora:")
        self.stdout.write("    python manage.py enviar_recordatorios")
        self.stdout.write("")
        self.stdout.write("  Para ver el modulo:")
        self.stdout.write("    http://127.0.0.1:8000/alertas/")
        self.stdout.write("")
