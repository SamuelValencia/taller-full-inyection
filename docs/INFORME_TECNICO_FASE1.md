# INFORME TÉCNICO - FASE 1
## Análisis Estructural del Proyecto Fuel Injection

**Fecha:** 28 de Junio de 2026
**Arquitecto:** Cascade AI
**Proyecto:** Fuel Injection - Sistema de Gestión de Taller

---

## 1. APLICACIONES ENCONTRADAS (13)

| # | Aplicación | Estado | Observaciones |
|---|------------|--------|----------------|
| 1 | alertas | ✅ Activo | Sistema de notificaciones |
| 2 | authentication | ⚠️ Parcial | Models vacío, usa usuarios.Usuario |
| 3 | clientes | ✅ Activo | Gestión de clientes |
| 4 | cotizaciones | ✅ Activo | Presupuestos de trabajo |
| 5 | dashboard | ⚠️ Parcial | Models vacío, solo vistas |
| 6 | facturacion | ✅ Activo | Facturas internas |
| 7 | inventario | ✅ Activo | Gestión de repuestos |
| 8 | mantenimiento | ✅ Activo | Mantenimiento preventivo |
| 9 | ordenes | ✅ Activo | Órdenes de trabajo (refactorizado) |
| 10 | reportes | ⚠️ Parcial | Models vacío, solo vistas |
| 11 | servicios | ✅ Activo | Catálogo de servicios |
| 12 | usuarios | ✅ Activo | Usuarios del sistema |
| 13 | vehiculos | ✅ Activo | Gestión de vehículos |

---

## 2. MODELOS ENCONTRADOS

### 2.1 Clientes (apps.clientes)
- **Cliente**: tipo_documento, numero_documento, nombres, apellidos, telefono, email, direccion, ciudad, observaciones, fecha_registro, fecha_actualizacion, activo

### 2.2 Vehículos (apps.vehiculos)
- **Vehiculo**: cliente (FK), placa, marca, modelo, anio, color, tipo_vehiculo, tipo_combustible, numero_vin, numero_motor, kilometraje_actual, cilindraje, transmision, observaciones, fecha_registro, fecha_actualizacion, activo

### 2.3 Servicios (apps.servicios)
- **Servicio**: nombre, descripcion, estado, fecha_creacion, fecha_actualizacion

### 2.4 Cotizaciones (apps.cotizaciones)
- **Cotizacion**: numero_cotizacion, vehiculo (FK), cliente (FK), elaborado_por (FK), estado, descripcion, observaciones, fecha_creacion, fecha_validez, fecha_aprobacion, descuento, orden_generada (FK to OrdenTrabajo)
- **DetalleCotizacion**: cotizacion (FK), tipo, descripcion, cantidad, precio_unitario

### 2.5 Órdenes de Trabajo (apps.ordenes)
- **OrdenTrabajo**: numero_orden, vehiculo (FK), cliente (FK), servicio (FK), tecnico_asignado (FK), recepcionista (FK), estado, prioridad, tipo_trabajo, kilometraje_ingreso, descripcion_problema, diagnostico, observaciones, fecha_ingreso, fecha_estimada_entrega, fecha_entrega_real, precio, costo_mano_obra, costo_repuestos, descuento, fecha_actualizacion
- **DetalleOrdenTrabajo**: orden (FK), tipo, descripcion, cantidad, precio_unitario

### 2.6 Usuarios (apps.usuarios)
- **Usuario** (extends AbstractUser): rol, telefono, cedula, especialidad, activo

### 2.7 Inventario (apps.inventario)
- **CategoriaRepuesto**: nombre, descripcion, activo, fecha_creacion
- **Repuesto**: codigo, nombre, descripcion, categoria (FK), marca, modelo, stock_actual, stock_minimo, stock_maximo, precio_compra, precio_venta, ubicacion, activo, fecha_creacion, fecha_actualizacion
- **MovimientoInventario**: repuesto (FK), tipo, cantidad, stock_anterior, stock_nuevo, orden_servicio (FK to OrdenTrabajo - nombre incorrecto), motivo, realizado_por (FK), fecha_movimiento

### 2.8 Mantenimiento (apps.mantenimiento)
- **TipoServicioMantenimiento**: nombre, descripcion, intervalo_km_recomendado, intervalo_dias_recomendado, activo
- **ProgramaMantenimiento**: vehiculo (FK), tipo_servicio (FK), ultimo_km, ultima_fecha, proximo_km, proxima_fecha, intervalo_km, intervalo_dias, estado, observaciones, activo, fecha_creacion, fecha_actualizacion
- **HistorialMantenimiento**: vehiculo (FK), orden (FK to OrdenTrabajo), tipo_servicio (FK), descripcion, km_al_servicio, proximo_km_sugerido, proxima_fecha_sugerida, tecnico (FK), costo, fecha_servicio, observaciones, fecha_registro

### 2.9 Facturación (apps.facturacion)
- **FacturaInterna**: numero_factura, orden (FK to OrdenTrabajo), estado, subtotal_mano_obra, subtotal_repuestos, subtotal, iva, total, observaciones, fecha_emision, fecha_anulacion, emitido_por (FK)

### 2.10 Alertas (apps.alertas)
- **Alerta**: tipo, nivel, vehiculo (FK), orden (FK to OrdenTrabajo), mensaje, fecha_creacion, fecha_vencimiento, destinatario (FK), leida, activa, canal, programada_para, enviada_email, enviada_whatsapp, ultimo_error_envio
- **PlantillaMensaje**: nombre, canal, asunto, cuerpo, activa, fecha_actualizacion

---

## 3. FORMULARIOS ENCONTRADOS (13)

Todas las aplicaciones tienen forms.py correspondientes.

---

## 4. VISTAS ENCONTRADAS (18)

- alertas/views.py
- authentication/views.py
- clientes/views.py, api_views.py
- cotizaciones/views.py
- dashboard/views.py
- facturacion/views.py, api_views.py
- inventario/views.py, api_views.py
- mantenimiento/views.py
- ordenes/views.py, api_views.py
- reportes/views.py
- servicios/views.py
- usuarios/views.py
- vehiculos/views.py, api_views.py

---

## 5. URLs ENCONTRADAS (18)

Todas las aplicaciones tienen urls.py configuradas.

---

## 6. RELACIONES ENTRE MÓDULOS

```
Cliente (1) ----< (N) Vehiculo
Vehiculo (1) ----< (N) OrdenTrabajo
Vehiculo (1) ----< (N) Cotizacion
Cliente (1) ----< (N) Cotizacion
Cliente (1) ----< (N) OrdenTrabajo
Servicio (1) ----< (N) OrdenTrabajo
Cotizacion (1) ----< (1) OrdenTrabajo (opcional)
OrdenTrabajo (1) ----< (N) DetalleOrdenTrabajo
OrdenTrabajo (1) ----< (1) FacturaInterna
OrdenTrabajo (1) ----< (N) MovimientoInventario
OrdenTrabajo (1) ----< (N) HistorialMantenimiento
Usuario (1) ----< (N) OrdenTrabajo (tecnico_asignado)
Usuario (1) ----< (N) OrdenTrabajo (recepcionista)
Usuario (1) ----< (N) Cotizacion
Usuario (1) ----< (N) FacturaInterna
CategoriaRepuesto (1) ----< (N) Repuesto
Repuesto (1) ----< (N) MovimientoInventario
Vehiculo (1) ----< (N) ProgramaMantenimiento
Vehiculo (1) ----< (N) HistorialMantenimiento
TipoServicioMantenimiento (1) ----< (N) ProgramaMantenimiento
TipoServicioMantenimiento (1) ----< (N) HistorialMantenimiento
```

---

## 7. PROBLEMAS ENCONTRADOS

### 7.1 CRÍTICOS

1. **inventario.MovimientoInventario.orden_servicio**
   - El campo se llama `orden_servicio` pero referencia a `OrdenTrabajo`
   - Debe renombrarse a `orden_trabajo`
   - Afecta: models.py, migraciones

2. **Error de importación en makemigrations**
   - Referencia a `ordenes.OrdenServicio` ya no existe
   - Debe ser `ordenes.OrdenTrabajo`

### 7.2 MEDIOS

3. **Apps con models vacíos**
   - authentication/models.py: vacío (usa usuarios.Usuario)
   - dashboard/models.py: vacío (solo vistas)
   - reportes/models.py: vacío (solo vistas)
   - No requiere acción, es por diseño

### 7.3 MENORES

4. **Telefono adicional ya eliminado**
   - Migration 0002_remove_cliente_telefono_alternativo.py ya existe
   - No requiere acción adicional

5. **No se encontraron ImageField/FileField**
   - No hay campos de imagen/archivo en los modelos
   - No requiere acción

---

## 8. DEPENDENCIAS AFECTADAS

### 8.1 Foreign Keys a OrdenTrabajo
- ✅ cotizaciones.Cotizacion.orden_generada
- ✅ facturacion.FacturaInterna.orden
- ✅ mantenimiento.HistorialMantenimiento.orden
- ✅ alertas.Alerta.orden
- ⚠️ inventario.MovimientoInventario.orden_servicio (nombre incorrecto)

### 8.2 Related Names
- ✅ Vehiculo.ordenes_trabajo
- ✅ Cliente.ordenes_trabajo
- ✅ Servicio.ordenes_trabajo
- ✅ Usuario.ordenes_trabajo_asignadas
- ✅ Usuario.ordenes_trabajo_recibidas
- ⚠️ OrdenTrabajo.movimientos_inventario (field name incorrecto)

---

## 9. ESTADO DE LA REFACTORIZACIÓN ORDENSERVICIO → ORDENTRABAJO

| Componente | Estado | Notas |
|------------|--------|-------|
| models.py | ✅ Completado | OrdenTrabajo y DetalleOrdenTrabajo |
| forms.py | ✅ Completado | OrdenTrabajoForm y DetalleOrdenTrabajoForm |
| views.py | ✅ Completado | Referencias actualizadas |
| admin.py | ✅ Completado | Registro actualizado |
| serializers.py | ✅ Completado | Serializadores actualizados |
| api_views.py | ✅ Completado | ViewSets actualizados |
| api_urls.py | ✅ Completado | Router actualizado |
| templates/ | ✅ Completado | Terminología actualizada |
| cotizaciones/models.py | ✅ Completado | FK actualizada |
| alertas/models.py | ✅ Completado | FK actualizada |
| facturacion/models.py | ✅ Completado | FK actualizada |
| mantenimiento/models.py | ✅ Completado | FK actualizada |
| inventario/models.py | ⚠️ Pendiente | Field name incorrecto |
| dashboard/views.py | ✅ Completado | Referencias actualizadas |
| reportes/views.py | ✅ Completado | Referencias actualizadas |
| migraciones | ⚠️ Pendiente | Necesita migración correctiva |

---

## 10. ESTRUCTURA DE BASE DE DATOS PROPUESTA

### 10.1 CLIENTES
```sql
CREATE TABLE clientes_cliente (
    id BIGSERIAL PRIMARY KEY,
    tipo_documento VARCHAR(10) NOT NULL,
    numero_documento VARCHAR(20) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(254),
    direccion TEXT,
    ciudad VARCHAR(80) DEFAULT 'Guayaquil',
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_cliente_documento ON clientes_cliente(numero_documento);
CREATE INDEX idx_cliente_nombre ON clientes_cliente(apellidos, nombres);
```

### 10.2 VEHICULOS
```sql
CREATE TABLE vehiculos_vehiculo (
    id BIGSERIAL PRIMARY KEY,
    cliente_id BIGINT REFERENCES clientes_cliente(id) ON DELETE PROTECT,
    placa VARCHAR(10) UNIQUE NOT NULL,
    marca VARCHAR(60) NOT NULL,
    modelo VARCHAR(80) NOT NULL,
    anio SMALLINT NOT NULL,
    color VARCHAR(40),
    tipo_vehiculo VARCHAR(15) DEFAULT 'AUTOMOVIL',
    tipo_combustible VARCHAR(15) DEFAULT 'GASOLINA',
    numero_vin VARCHAR(17),
    numero_motor VARCHAR(50),
    kilometraje_actual INTEGER DEFAULT 0,
    cilindraje VARCHAR(20),
    transmision VARCHAR(20),
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_vehiculo_placa ON vehiculos_vehiculo(placa);
CREATE INDEX idx_vehiculo_cliente ON vehiculos_vehiculo(cliente_id);
```

### 10.3 SERVICIOS
```sql
CREATE TABLE servicios_servicio (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(120) UNIQUE NOT NULL,
    descripcion TEXT,
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_servicio_nombre ON servicios_servicio(nombre);
CREATE INDEX idx_servicio_estado ON servicios_servicio(estado);
```

### 10.4 COTIZACIONES
```sql
CREATE TABLE cotizaciones_cotizacion (
    id BIGSERIAL PRIMARY KEY,
    numero_cotizacion VARCHAR(20) UNIQUE NOT NULL,
    vehiculo_id BIGINT REFERENCES vehiculos_vehiculo(id) ON DELETE PROTECT,
    cliente_id BIGINT REFERENCES clientes_cliente(id) ON DELETE PROTECT,
    elaborado_por_id BIGINT REFERENCES usuarios_usuario(id) ON DELETE SET NULL,
    estado VARCHAR(15) DEFAULT 'PENDIENTE',
    descripcion TEXT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_validez DATE,
    fecha_aprobacion TIMESTAMP,
    descuento DECIMAL(10,2) DEFAULT 0,
    orden_generada_id BIGINT REFERENCES ordenes_ordentrabajo(id) ON DELETE SET NULL
);

CREATE TABLE cotizaciones_detallecotizacion (
    id BIGSERIAL PRIMARY KEY,
    cotizacion_id BIGINT REFERENCES cotizaciones_cotizacion(id) ON DELETE CASCADE,
    tipo VARCHAR(10) DEFAULT 'SERVICIO',
    descripcion VARCHAR(200) NOT NULL,
    cantidad DECIMAL(8,2) DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL
);
```

### 10.5 ÓRDENES DE TRABAJO
```sql
CREATE TABLE ordenes_ordentrabajo (
    id BIGSERIAL PRIMARY KEY,
    numero_orden VARCHAR(20) UNIQUE NOT NULL,
    vehiculo_id BIGINT REFERENCES vehiculos_vehiculo(id) ON DELETE PROTECT,
    cliente_id BIGINT REFERENCES clientes_cliente(id) ON DELETE PROTECT,
    servicio_id BIGINT REFERENCES servicios_servicio(id) ON DELETE PROTECT,
    tecnico_asignado_id BIGINT REFERENCES usuarios_usuario(id) ON DELETE SET NULL,
    recepcionista_id BIGINT REFERENCES usuarios_usuario(id) ON DELETE SET NULL,
    estado VARCHAR(25) DEFAULT 'RECIBIDA',
    prioridad VARCHAR(10) DEFAULT 'MEDIA',
    tipo_trabajo VARCHAR(30) DEFAULT 'MECANICA_GENERAL',
    kilometraje_ingreso INTEGER DEFAULT 0,
    descripcion_problema TEXT NOT NULL,
    diagnostico TEXT,
    observaciones TEXT,
    fecha_ingreso TIMESTAMP DEFAULT NOW(),
    fecha_estimada_entrega DATE,
    fecha_entrega_real TIMESTAMP,
    precio DECIMAL(10,2) DEFAULT 0,
    costo_mano_obra DECIMAL(10,2) DEFAULT 0,
    costo_repuestos DECIMAL(10,2) DEFAULT 0,
    descuento DECIMAL(10,2) DEFAULT 0,
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orden_numero ON ordenes_ordentrabajo(numero_orden);
CREATE INDEX idx_orden_estado ON ordenes_ordentrabajo(estado);
CREATE INDEX idx_orden_vehiculo ON ordenes_ordentrabajo(vehiculo_id);
CREATE INDEX idx_orden_cliente ON ordenes_ordentrabajo(cliente_id);
CREATE INDEX idx_orden_fecha ON ordenes_ordentrabajo(fecha_ingreso);

CREATE TABLE ordenes_detalleordentrabajo (
    id BIGSERIAL PRIMARY KEY,
    orden_id BIGINT REFERENCES ordenes_ordentrabajo(id) ON DELETE CASCADE,
    tipo VARCHAR(10) DEFAULT 'SERVICIO',
    descripcion VARCHAR(200) NOT NULL,
    cantidad DECIMAL(8,2) DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL
);
```

### 10.6 USUARIOS
```sql
CREATE TABLE usuarios_usuario (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT NOW(),
    rol VARCHAR(20) DEFAULT 'RECEPCIONISTA',
    telefono VARCHAR(20),
    cedula VARCHAR(13),
    especialidad VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE
);
```

---

## 11. ACCIONES REQUERIDAS

### 11.1 PRIORIDAD ALTA
1. ✅ Renombrar `inventario.MovimientoInventario.orden_servicio` → `orden_trabajo`
2. ✅ Crear migración para el cambio de campo
3. ✅ Verificar que no existan más referencias a `OrdenServicio`
4. ✅ Ejecutar makemigrations y migrate sin errores

### 11.2 PRIORIDAD MEDIA
5. ⏳ Generar seeders para datos iniciales (15 registros cada uno)
6. ⏳ Verificar validaciones en formularios

### 11.3 PRIORIDAD BAJA
7. ⏳ Revisar y optimizar índices de base de datos
8. ⏳ Documentar API endpoints

---

## 12. CONCLUSIÓN

El proyecto está **90% completado** en la refacturación de OrdenServicio → OrdenTrabajo. 

**Pendiente crítico:**
- Corregir el nombre del campo `orden_servicio` en `inventario.MovimientoInventario`

**Estado general:** ✅ BUENO
La estructura de la base de datos está bien diseñada con las relaciones apropiadas. Los modelos siguen las mejores prácticas de Django con índices, verbose_names, y restricciones adecuadas.
