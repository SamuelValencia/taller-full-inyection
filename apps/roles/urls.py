from django.urls import path
from . import views

app_name = "roles"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("crear/", views.crear, name="crear"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar, name="eliminar"),
    path("<int:pk>/duplicar/", views.duplicar, name="duplicar"),
    path("<int:pk>/toggle/", views.toggle_activo, name="toggle_activo"),
    path("<int:pk>/usuarios/", views.asignar_usuarios, name="asignar_usuarios"),
]
