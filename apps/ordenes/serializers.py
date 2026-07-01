from rest_framework import serializers
from .models import OrdenTrabajo, DetalleOrdenTrabajo


class DetalleOrdenTrabajoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleOrdenTrabajo
        fields = ['id', 'tipo', 'descripcion', 'cantidad', 'precio_unitario']
        read_only_fields = ['id']


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    detalles = DetalleOrdenTrabajoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    
    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'numero_orden', 'cliente', 'cliente_nombre', 'vehiculo',
            'vehiculo_placa', 'servicio', 'servicio_nombre', 'precio',
            'tecnico_asignado', 'estado', 'prioridad', 'tipo_trabajo',
            'descripcion_problema', 'observaciones', 'costo_mano_obra', 'costo_repuestos',
            'descuento', 'fecha_ingreso', 'fecha_estimada_entrega',
            'fecha_entrega_real', 'detalles'
        ]
        read_only_fields = ['id', 'numero_orden', 'fecha_ingreso']


class OrdenTrabajoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenTrabajo
        fields = ['id', 'numero_orden', 'cliente', 'vehiculo', 'servicio', 'precio', 'estado', 'fecha_ingreso']
