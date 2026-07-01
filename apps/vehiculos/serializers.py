from rest_framework import serializers
from .models import Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = [
            'id', 'placa', 'marca', 'modelo', 'anio', 'color',
            'tipo_vehiculo', 'kilometraje_actual', 'cliente', 'cliente_nombre', 'activo'
        ]
        read_only_fields = ['id']


class VehiculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'placa', 'marca', 'modelo', 'anio', 'tipo_vehiculo', 'kilometraje_actual', 'cliente']
