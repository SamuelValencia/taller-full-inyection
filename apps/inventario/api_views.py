from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from .models import Repuesto, CategoriaRepuesto
from .serializers import RepuestoSerializer, CategoriaRepuestoSerializer


class CategoriaRepuestoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CategoriaRepuesto.objects.all()
    serializer_class = CategoriaRepuestoSerializer


class RepuestoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RepuestoSerializer
    
    def get_queryset(self):
        queryset = Repuesto.objects.select_related('categoria')
        categoria_id = self.request.query_params.get('categoria', None)
        stock_bajo = self.request.query_params.get('stock_bajo', None)
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if stock_bajo == 'true':
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
        return queryset
