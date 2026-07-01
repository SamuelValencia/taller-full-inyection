from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_documento', 'numero_documento', 'nombre_completo',
            'telefono', 'email', 'direccion', 'activo'
        ]
        read_only_fields = ['id']


class ClienteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre_completo', 'telefono', 'email', 'activo']
