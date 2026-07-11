"""
Vistas para el módulo de Inventario.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, F

from apps.decorators import admin_o_recepcionista_requerido, admin_o_mecanico_requerido, rol_autenticado_requerido
from .models import CategoriaRepuesto, Repuesto, MovimientoInventario
from .forms import CategoriaRepuestoForm, RepuestoForm, MovimientoInventarioForm


@rol_autenticado_requerido
def index(request):
    """Vista principal del inventario."""
    total_repuestos = Repuesto.objects.filter(activo=True).count()
    stock_bajo = Repuesto.objects.filter(activo=True).filter(stock_actual__lte=F('stock_minimo')).count()
    valor_inventario = Repuesto.objects.filter(activo=True).aggregate(
        total=Sum(F('stock_actual') * F('precio_compra'))
    )['total'] or 0

    categorias = CategoriaRepuesto.objects.filter(activo=True)

    context = {
        "total_repuestos": total_repuestos,
        "stock_bajo": stock_bajo,
        "valor_inventario": valor_inventario,
        "categorias": categorias,
    }
    return render(request, "inventario/index.html", context)


@rol_autenticado_requerido
def lista_repuestos(request):
    """Lista de repuestos con búsqueda y filtros."""
    query = request.GET.get("q", "")
    categoria_id = request.GET.get("categoria", "")

    repuestos = Repuesto.objects.filter(activo=True)

    if query:
        repuestos = repuestos.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query) |
            Q(marca__icontains=query) |
            Q(modelo__icontains=query)
        )

    if categoria_id:
        repuestos = repuestos.filter(categoria_id=categoria_id)

    categorias = CategoriaRepuesto.objects.filter(activo=True)

    context = {
        "repuestos": repuestos,
        "categorias": categorias,
        "query": query,
        "categoria_seleccionada": categoria_id,
    }
    return render(request, "inventario/lista_repuestos.html", context)


@admin_o_recepcionista_requerido
def crear_repuesto(request):
    """Crear nuevo repuesto."""
    if request.method == "POST":
        form = RepuestoForm(request.POST)
        if form.is_valid():
            repuesto = form.save()
            if repuesto.stock_actual > 0:
                MovimientoInventario.objects.create(
                    repuesto=repuesto,
                    tipo=MovimientoInventario.TipoMovimiento.ENTRADA,
                    cantidad=repuesto.stock_actual,
                    stock_anterior=0,
                    stock_nuevo=repuesto.stock_actual,
                    motivo="Stock inicial",
                    realizado_por=request.user
                )
            messages.success(request, "Repuesto creado exitosamente.")
            return redirect("inventario:lista_repuestos")
    else:
        form = RepuestoForm()

    context = {"form": form, "titulo": "Nuevo Repuesto"}
    return render(request, "inventario/form_repuesto.html", context)


@admin_o_recepcionista_requerido
def editar_repuesto(request, pk):
    """Editar repuesto existente."""
    repuesto = get_object_or_404(Repuesto, pk=pk)

    if request.method == "POST":
        form = RepuestoForm(request.POST, instance=repuesto)
        if form.is_valid():
            stock_anterior = repuesto.stock_actual
            form.save()
            stock_nuevo = form.instance.stock_actual
            if stock_nuevo != stock_anterior:
                MovimientoInventario.objects.create(
                    repuesto=repuesto,
                    tipo=MovimientoInventario.TipoMovimiento.AJUSTE,
                    cantidad=stock_nuevo - stock_anterior,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    motivo="Ajuste manual desde edición",
                    realizado_por=request.user
                )
            messages.success(request, "Repuesto actualizado exitosamente.")
            return redirect("inventario:lista_repuestos")
    else:
        form = RepuestoForm(instance=repuesto)

    context = {"form": form, "titulo": "Editar Repuesto", "repuesto": repuesto}
    return render(request, "inventario/form_repuesto.html", context)


@rol_autenticado_requerido
def detalle_repuesto(request, pk):
    """Ver detalles de un repuesto."""
    repuesto = get_object_or_404(Repuesto, pk=pk)
    movimientos = repuesto.movimientos.all()[:20]

    context = {
        "repuesto": repuesto,
        "movimientos": movimientos,
    }
    return render(request, "inventario/detalle_repuesto.html", context)


@admin_o_recepcionista_requerido
def lista_categorias(request):
    """Lista de categorías de repuestos."""
    categorias = CategoriaRepuesto.objects.all()
    context = {"categorias": categorias}
    return render(request, "inventario/lista_categorias.html", context)


@admin_o_recepcionista_requerido
def crear_categoria(request):
    """Crear nueva categoría."""
    if request.method == "POST":
        form = CategoriaRepuestoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada exitosamente.")
            return redirect("inventario:lista_categorias")
    else:
        form = CategoriaRepuestoForm()

    context = {"form": form, "titulo": "Nueva Categoría"}
    return render(request, "inventario/form_categoria.html", context)


@admin_o_recepcionista_requerido
def editar_categoria(request, pk):
    """Editar categoría existente."""
    categoria = get_object_or_404(CategoriaRepuesto, pk=pk)

    if request.method == "POST":
        form = CategoriaRepuestoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada exitosamente.")
            return redirect("inventario:lista_categorias")
    else:
        form = CategoriaRepuestoForm(instance=categoria)

    context = {"form": form, "titulo": "Editar Categoría", "categoria": categoria}
    return render(request, "inventario/form_categoria.html", context)


@admin_o_mecanico_requerido
def registrar_movimiento(request):
    """Registrar movimiento manual de inventario."""
    if request.method == "POST":
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            repuesto = form.cleaned_data["repuesto"]
            tipo = form.cleaned_data["tipo"]
            cantidad = form.cleaned_data["cantidad"]
            motivo = form.cleaned_data["motivo"]

            stock_anterior = repuesto.stock_actual

            if tipo == "SALIDA":
                if cantidad > stock_anterior:
                    messages.error(request, "No hay suficiente stock para esta salida.")
                    return redirect("inventario:lista_repuestos")
                cantidad = -cantidad

            stock_nuevo = stock_anterior + cantidad

            repuesto.stock_actual = stock_nuevo
            repuesto.save()

            MovimientoInventario.objects.create(
                repuesto=repuesto,
                tipo=tipo,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                motivo=motivo or "Movimiento manual",
                realizado_por=request.user
            )

            messages.success(request, "Movimiento registrado exitosamente.")
            return redirect("inventario:lista_repuestos")
    else:
        form = MovimientoInventarioForm()

    context = {"form": form, "titulo": "Registrar Movimiento"}
    return render(request, "inventario/form_movimiento.html", context)
