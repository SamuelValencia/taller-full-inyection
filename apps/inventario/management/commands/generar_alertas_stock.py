"""
Comando de Django para generar alertas por stock bajo.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import F
from apps.inventario.models import Repuesto
from apps.alertas.models import Alerta

Usuario = get_user_model()


class Command(BaseCommand):
    help = "Genera alertas para repuestos con stock bajo"

    def handle(self, *args, **options):
        # Buscar repuestos con stock bajo
        repuestos_stock_bajo = Repuesto.objects.filter(
            activo=True,
            stock_actual__lte=F('stock_minimo')
        )
        
        # Obtener administradores para notificar
        admins = Usuario.objects.filter(rol__codigo="ADMIN", is_active=True)
        
        alertas_creadas = 0
        
        for repuesto in repuestos_stock_bajo:
            # Verificar si ya existe una alerta activa para este repuesto
            alerta_existente = Alerta.objects.filter(
                tipo=Alerta.TipoAlerta.MANTENIMIENTO_VENCIDO,
                nivel=Alerta.Nivel.DANGER,
                mensaje__icontains=repuesto.codigo,
                activa=True,
                leida=False
            ).exists()
            
            if not alerta_existente:
                # Crear alerta para cada administrador
                for admin in admins:
                    Alerta.objects.create(
                        tipo=Alerta.TipoAlerta.MANTENIMIENTO_VENCIDO,
                        nivel=Alerta.Nivel.DANGER,
                        mensaje=f"Stock bajo para repuesto {repuesto.codigo} - {repuesto.nombre}. Stock actual: {repuesto.stock_actual}, Mínimo: {repuesto.stock_minimo}",
                        destinatario=admin,
                        activa=True
                    )
                    alertas_creadas += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"Se crearon {alertas_creadas} alertas de stock bajo")
        )
