"""
URL configuration for Inventario app.
"""
from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.index, name="index"),
    path("repuestos/", views.lista_repuestos, name="lista_repuestos"),
    path("repuestos/nuevo/", views.crear_repuesto, name="crear_repuesto"),
    path("repuestos/<int:pk>/editar/", views.editar_repuesto, name="editar_repuesto"),
    path("repuestos/<int:pk>/", views.detalle_repuesto, name="detalle_repuesto"),
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/nueva/", views.crear_categoria, name="crear_categoria"),
    path("categorias/<int:pk>/editar/", views.editar_categoria, name="editar_categoria"),
    path("movimiento/registrar/", views.registrar_movimiento, name="registrar_movimiento"),
]
