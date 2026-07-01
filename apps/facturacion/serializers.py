from rest_framework import serializers
from .models import FacturaInterna


class FacturaInternaSerializer(serializers.ModelSerializer):
    orden_numero = serializers.CharField(source='orden.numero_orden', read_only=True)
    cliente_nombre = serializers.CharField(source='orden.cliente.nombre_completo', read_only=True)
    emitido_por_nombre = serializers.CharField(source='emitido_por.get_full_name', read_only=True)
    
    class Meta:
        model = FacturaInterna
        fields = [
            'id', 'numero_factura', 'orden', 'orden_numero', 'cliente_nombre',
            'estado', 'subtotal_mano_obra', 'subtotal_repuestos', 'subtotal',
            'iva', 'total', 'observaciones', 'fecha_emision', 'fecha_anulacion',
            'emitido_por', 'emitido_por_nombre'
        ]
        read_only_fields = ['id', 'numero_factura', 'fecha_emision', 'subtotal', 'iva', 'total']


class FacturaInternaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaInterna
        fields = ['id', 'numero_factura', 'orden', 'estado', 'total', 'fecha_emision']
