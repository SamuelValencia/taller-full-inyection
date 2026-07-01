from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO

from apps.ordenes.models import OrdenTrabajo, DetalleOrdenTrabajo
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.mantenimiento.models import HistorialMantenimiento
from apps.inventario.models import Repuesto


def render_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return HttpResponse("Error generando PDF", status=500)


@login_required
def index(request):
    total_ordenes = OrdenTrabajo.objects.count()
    total_clientes = Cliente.objects.filter(activo=True).count()
    total_vehiculos = Vehiculo.objects.filter(activo=True).count()
    ordenes_por_estado = {
        "recibidas": OrdenTrabajo.objects.filter(estado="RECIBIDA").count(),
        "en_proceso": OrdenTrabajo.objects.filter(estado="EN_PROCESO").count(),
        "finalizadas": OrdenTrabajo.objects.filter(estado="FINALIZADA").count(),
        "entregadas": OrdenTrabajo.objects.filter(estado="ENTREGADA").count(),
    }
    return render(request, "reportes/index.html", {
        "total_ordenes": total_ordenes,
        "total_clientes": total_clientes,
        "total_vehiculos": total_vehiculos,
        "ordenes_por_estado": ordenes_por_estado,
    })


@login_required
def orden_pdf(request, pk):
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related("vehiculo", "cliente", "tecnico_asignado", "recepcionista"),
        pk=pk
    )
    detalles = orden.detalles.all()
    context = {
        "orden": orden,
        "detalles": detalles,
        "taller_nombre": settings.TALLER_NOMBRE,
        "taller_telefono": settings.TALLER_TELEFONO,
        "taller_direccion": settings.TALLER_DIRECCION,
    }
    return render_pdf("reportes/orden_pdf.html", context)


@login_required
def historial_vehiculo_pdf(request, pk):
    vehiculo = get_object_or_404(Vehiculo.objects.select_related("cliente"), pk=pk)
    historial = HistorialMantenimiento.objects.filter(vehiculo=vehiculo).order_by("-fecha_servicio")
    context = {
        "vehiculo": vehiculo,
        "historial": historial,
        "taller_nombre": settings.TALLER_NOMBRE,
        "taller_telefono": settings.TALLER_TELEFONO,
        "taller_direccion": settings.TALLER_DIRECCION,
    }
    return render_pdf("reportes/historial_pdf.html", context)


# Exportacion Excel
@login_required
def exportar_clientes_excel(request):
    """Exportar lista de clientes a Excel."""
    clientes = Cliente.objects.filter(activo=True)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Clientes"
    
    # Encabezados
    headers = ["Documento", "Nombre", "Telefono", "Email", "Direccion", "Activo"]
    ws.append(headers)
    
    # Estilo para encabezados
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for cliente in clientes:
        ws.append([
            cliente.tipo_documento,
            cliente.nombre_completo,
            cliente.telefono or "",
            cliente.email or "",
            cliente.direccion or "",
            "Si" if cliente.activo else "No"
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="clientes.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_vehiculos_excel(request):
    """Exportar lista de vehiculos a Excel."""
    vehiculos = Vehiculo.objects.filter(activo=True).select_related("cliente")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Vehiculos"
    
    # Encabezados
    headers = ["Placa", "Marca", "Modelo", "Anio", "Color", "Cliente", "Activo"]
    ws.append(headers)
    
    # Estilo para encabezados
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for vehiculo in vehiculos:
        ws.append([
            vehiculo.placa,
            vehiculo.marca,
            vehiculo.modelo,
            vehiculo.anio,
            vehiculo.color,
            vehiculo.cliente.nombre_completo,
            "Si" if vehiculo.activo else "No"
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="vehiculos.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_ordenes_excel(request):
    """Exportar lista de ordenes a Excel."""
    ordenes = OrdenTrabajo.objects.select_related("cliente", "vehiculo", "tecnico_asignado")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Ordenes"
    
    # Encabezados
    headers = ["N Orden", "Cliente", "Vehiculo", "Estado", "Prioridad", "Tecnico", "Fecha Ingreso", "Total"]
    ws.append(headers)
    
    # Estilo para encabezados
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for orden in ordenes:
        ws.append([
            orden.numero_orden,
            orden.cliente.nombre_completo,
            orden.vehiculo.placa,
            orden.get_estado_display(),
            orden.get_prioridad_display(),
            orden.tecnico_asignado.get_full_name() if orden.tecnico_asignado else "",
            orden.fecha_ingreso.strftime("%d/%m/%Y %H:%M"),
            float(orden.costo_total)
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ordenes.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_inventario_excel(request):
    """Exportar inventario a Excel."""
    repuestos = Repuesto.objects.filter(activo=True)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    
    # Encabezados
    headers = ["Codigo", "Nombre", "Categoria", "Marca", "Stock Actual", "Stock Minimo", "Precio Compra", "Precio Venta", "Valor Inventario"]
    ws.append(headers)
    
    # Estilo para encabezados
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for repuesto in repuestos:
        ws.append([
            repuesto.codigo,
            repuesto.nombre,
            repuesto.categoria.nombre if repuesto.categoria else "",
            repuesto.marca or "",
            repuesto.stock_actual,
            repuesto.stock_minimo,
            float(repuesto.precio_compra),
            float(repuesto.precio_venta),
            float(repuesto.valor_inventario)
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    wb.save(response)
    return response


# Reportes Gerenciales
@login_required
def productividad_taller(request):
    """Reporte de productividad del taller."""
    from django.db.models import Count, Sum, Avg
    from django.db.models.functions import TruncDate
    from datetime import datetime, timedelta
    
    # Ultimos 30 dias
    fecha_inicio = datetime.now().date() - timedelta(days=30)
    
    # Ordenes completadas en el periodo
    ordenes_completadas = OrdenTrabajo.objects.filter(
        fecha_entrega_real__gte=fecha_inicio,
        estado__in=['FINALIZADA', 'ENTREGADA']
    )
    
    # Metricas
    total_ordenes = ordenes_completadas.count()
    total_ingresos = ordenes_completadas.aggregate(
        total=Sum('costo_total')
    )['total'] or 0
    
    promedio_por_orden = ordenes_completadas.aggregate(
        promedio=Avg('costo_total')
    )['promedio'] or 0
    
    # Ordenes por dia
    ordenes_por_dia = ordenes_completadas.annotate(
        fecha=TruncDate('fecha_entrega_real')
    ).values('fecha').annotate(
        count=Count('id')
    ).order_by('fecha')
    
    # Top 5 tecnicos por ordenes completadas
    from apps.usuarios.models import Usuario
    tecnicos = Usuario.objects.filter(
        rol=Usuario.Rol.MECANICO,
        ordenes_trabajo_asignadas__fecha_entrega_real__gte=fecha_inicio,
        ordenes_trabajo_asignadas__estado__in=['FINALIZADA', 'ENTREGADA']
    ).annotate(
        ordenes_completadas=Count('ordenes_trabajo_asignadas')
    ).order_by('-ordenes_completadas')[:5]
    
    context = {
        "fecha_inicio": fecha_inicio,
        "total_ordenes": total_ordenes,
        "total_ingresos": total_ingresos,
        "promedio_por_orden": promedio_por_orden,
        "ordenes_por_dia": ordenes_por_dia,
        "tecnicos": tecnicos,
    }
    return render(request, "reportes/productividad.html", context)


@login_required
def servicios_realizados(request):
    """Reporte de servicios realizados."""
    from django.db.models import Count, Sum
    
    # Servicios mas frecuentes
    servicios = DetalleOrdenTrabajo.objects.filter(
        tipo='SERVICIO'
    ).values('descripcion').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Repuestos mas utilizados
    repuestos = DetalleOrdenTrabajo.objects.filter(
        tipo='REPUESTO'
    ).values('descripcion').annotate(
        count=Count('id'),
        total_cantidad=Sum('cantidad')
    ).order_by('-count')[:20]
    
    context = {
        "servicios": servicios,
        "repuestos": repuestos,
    }
    return render(request, "reportes/servicios.html", context)


@login_required
def reporte_mantenimientos(request):
    """Reporte de mantenimientos preventivos."""
    from apps.mantenimiento.models import ProgramaMantenimiento, HistorialMantenimiento
    from django.db.models import Count
    
    # Mantenimientos vencidos
    vencidos = ProgramaMantenimiento.objects.filter(
        estado=ProgramaMantenimiento.EstadoPrograma.VENCIDO
    ).count()
    
    # Mantenimientos proximos
    proximos = ProgramaMantenimiento.objects.filter(
        estado=ProgramaMantenimiento.EstadoPrograma.PROXIMO
    ).count()
    
    # Mantenimientos al dia
    al_dia = ProgramaMantenimiento.objects.filter(
        estado=ProgramaMantenimiento.EstadoPrograma.AL_DIA
    ).count()
    
    # Tipos de mantenimiento mas comunes
    tipos_comunes = HistorialMantenimiento.objects.values(
        'tipo_servicio__nombre'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        "vencidos": vencidos,
        "proximos": proximos,
        "al_dia": al_dia,
        "tipos_comunes": tipos_comunes,
    }
    return render(request, "reportes/mantenimientos.html", context)
