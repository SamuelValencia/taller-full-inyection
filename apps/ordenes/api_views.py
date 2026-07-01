from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OrdenTrabajo
from .serializers import OrdenTrabajoSerializer, OrdenTrabajoListSerializer


class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrdenTrabajoListSerializer
        return OrdenTrabajoSerializer
    
    def get_queryset(self):
        queryset = OrdenTrabajo.objects.select_related('cliente', 'vehiculo', 'servicio', 'tecnico_asignado')
        estado = self.request.query_params.get('estado', None)
        cliente_id = self.request.query_params.get('cliente', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset
