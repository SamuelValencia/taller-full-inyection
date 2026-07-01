from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import FacturaInterna
from .serializers import FacturaInternaSerializer, FacturaInternaListSerializer


class FacturaInternaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacturaInternaListSerializer
        return FacturaInternaSerializer
    
    def get_queryset(self):
        queryset = FacturaInterna.objects.select_related('orden', 'emitido_por')
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
