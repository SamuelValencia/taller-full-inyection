"""
Vistas para el módulo de Facturación.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from .models import FacturaInterna
from .forms import FacturaInternaForm, AnularFacturaForm


def render_pdf(template_path, context):
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return HttpResponse("Error generando PDF", status=500)


@login_required
def lista_facturas(request):
    """Lista de facturas internas."""
    facturas = FacturaInterna.objects.select_related("orden", "emitido_por").all()
    
    context = {"facturas": facturas}
    return render(request, "facturacion/lista.html", context)


@login_required
def crear_factura(request, orden_pk):
    """Crear factura desde una orden de trabajo."""
    from apps.ordenes.models import OrdenTrabajo

    orden = get_object_or_404(OrdenTrabajo, pk=orden_pk)
    
    # Verificar que no exista factura para esta orden
    if hasattr(orden, 'factura'):
        messages.warning(request, "Esta orden ya tiene una factura asociada.")
        return redirect("facturacion:detalle", orden.factura.pk)
    
    if request.method == "POST":
        form = FacturaInternaForm(request.POST)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.emitido_por = request.user
            factura.save()
            messages.success(request, "Factura creada exitosamente.")
            return redirect("facturacion:detalle", factura.pk)
    else:
        form = FacturaInternaForm(initial={"orden": orden})
    
    context = {"form": form, "titulo": "Nueva Factura", "orden": orden}
    return render(request, "facturacion/form.html", context)


@login_required
def detalle_factura(request, pk):
    """Ver detalles de una factura."""
    factura = get_object_or_404(
        FacturaInterna.objects.select_related("orden", "orden__cliente", "orden__vehiculo", "emitido_por"),
        pk=pk
    )
    
    context = {"factura": factura}
    return render(request, "facturacion/detalle.html", context)


@login_required
def factura_pdf(request, pk):
    """Generar PDF de la factura."""
    factura = get_object_or_404(
        FacturaInterna.objects.select_related("orden", "orden__cliente", "orden__vehiculo", "emitido_por"),
        pk=pk
    )
    
    detalles = factura.orden.detalles.all()
    
    context = {
        "factura": factura,
        "detalles": detalles,
        "taller_nombre": settings.TALLER_NOMBRE,
        "taller_telefono": settings.TALLER_TELEFONO,
        "taller_direccion": settings.TALLER_DIRECCION,
    }
    return render_pdf("facturacion/factura_pdf.html", context)


@login_required
def anular_factura(request, pk):
    """Anular una factura."""
    factura = get_object_or_404(FacturaInterna, pk=pk)
    
    if factura.estado == FacturaInterna.Estado.ANULADA:
        messages.warning(request, "Esta factura ya está anulada.")
        return redirect("facturacion:detalle", factura.pk)
    
    if request.method == "POST":
        form = AnularFacturaForm(request.POST)
        if form.is_valid():
            factura.anular(request.user)
            messages.success(request, "Factura anulada exitosamente.")
            return redirect("facturacion:detalle", factura.pk)
    else:
        form = AnularFacturaForm()
    
    context = {"form": form, "factura": factura}
    return render(request, "facturacion/anular.html", context)
