from django.urls import path
from . import views

app_name = "servicios"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.crear, name="crear"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar, name="eliminar"),
    path("<int:pk>/repuestos/", views.gestionar_repuestos, name="gestionar_repuestos"),
    path("<int:pk>/repuestos.json", views.repuestos_sugeridos_json, name="repuestos_sugeridos_json"),
    path("catalogo.json", views.catalogo_json, name="catalogo_json"),
]
