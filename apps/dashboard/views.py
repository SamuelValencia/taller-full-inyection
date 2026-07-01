from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, F, Sum
from datetime import timedelta

from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.ordenes.models import OrdenTrabajo
from apps.alertas.models import Alerta


@login_required
def index(request):
    hoy = timezone.now().date()
    hace_30 = hoy - timedelta(days=30)
    inicio_anio = hoy.replace(month=1, day=1)

    total_clientes = Cliente.objects.filter(activo=True).count()
    total_vehiculos = Vehiculo.objects.filter(activo=True).count()

    ordenes_pendientes = OrdenTrabajo.objects.filter(estado="RECIBIDA").count()
    ordenes_en_proceso = OrdenTrabajo.objects.filter(estado="EN_PROCESO").count()
    ordenes_finalizadas = OrdenTrabajo.objects.filter(estado="FINALIZADA").count()
    ordenes_entregadas = OrdenTrabajo.objects.filter(estado="ENTREGADA").count()

    ingresos_mes = OrdenTrabajo.objects.filter(fecha_ingreso__date__gte=hace_30).aggregate(
        total=Sum(F("precio") + F("costo_repuestos") - F("descuento"))
    )["total"] or 0
    ingresos_anio = OrdenTrabajo.objects.filter(fecha_ingreso__date__gte=inicio_anio).aggregate(
        total=Sum(F("precio") + F("costo_repuestos") - F("descuento"))
    )["total"] or 0

    servicios_top = (
        OrdenTrabajo.objects.filter(servicio__isnull=False)
        .values("servicio__nombre")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    ordenes_recientes = OrdenTrabajo.objects.select_related(
        "vehiculo", "cliente", "tecnico_asignado"
    ).order_by("-fecha_ingreso")[:8]

    alertas_urgentes = Alerta.objects.filter(
        activa=True, leida=False, nivel__in=["WARNING", "DANGER"]
    ).select_related("vehiculo")[:5]

    # Datos para grafica de ordenes por dia (ultimos 7 dias)
    labels_grafica = []
    datos_grafica = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        labels_grafica.append(dia.strftime("%d/%m"))
        datos_grafica.append(
            OrdenTrabajo.objects.filter(fecha_ingreso__date=dia).count()
        )

    # Distribucion de estados para grafica de dona
    estados_labels = ["Recibida", "En proceso", "Finalizada", "Entregada"]
    estados_datos = [ordenes_pendientes, ordenes_en_proceso, ordenes_finalizadas, ordenes_entregadas]

    context = {
        "total_clientes": total_clientes,
        "total_vehiculos": total_vehiculos,
        "ordenes_pendientes": ordenes_pendientes,
        "ordenes_en_proceso": ordenes_en_proceso,
        "ordenes_finalizadas": ordenes_finalizadas,
        "ordenes_entregadas": ordenes_entregadas,
        "ingresos_mes": ingresos_mes,
        "ingresos_anio": ingresos_anio,
        "servicios_top": servicios_top,
        "ordenes_recientes": ordenes_recientes,
        "alertas_urgentes": alertas_urgentes,
        "labels_grafica": labels_grafica,
        "datos_grafica": datos_grafica,
        "estados_labels": estados_labels,
        "estados_datos": estados_datos,
    }
    return render(request, "dashboard/index.html", context)
