from rest_framework import serializers
from .models import Repuesto, CategoriaRepuesto, MovimientoInventario


class CategoriaRepuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaRepuesto
        fields = ['id', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']


class RepuestoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    stock_bajo = serializers.BooleanField(read_only=True)
    valor_inventario = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    
    class Meta:
        model = Repuesto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'categoria', 'categoria_nombre',
            'marca', 'modelo', 'stock_actual', 'stock_minimo', 'stock_maximo',
            'precio_compra', 'precio_venta', 'ubicacion', 'activo', 'stock_bajo', 'valor_inventario'
        ]
        read_only_fields = ['id']


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    repuesto_codigo = serializers.CharField(source='repuesto.codigo', read_only=True)
    realizado_por_nombre = serializers.CharField(source='realizado_por.get_full_name', read_only=True)
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'repuesto', 'repuesto_codigo', 'tipo', 'cantidad',
            'stock_anterior', 'stock_nuevo', 'motivo', 'fecha_movimiento', 'realizado_por', 'realizado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_movimiento']
