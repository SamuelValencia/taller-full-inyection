# Analisis y cambios realizados

## Aplicaciones encontradas

- `authentication`, `usuarios`, `clientes`, `vehiculos`, `ordenes`, `cotizaciones`, `mantenimiento`, `alertas`, `dashboard`, `reportes`, `inventario`, `facturacion`.
- Se agrego `servicios` para el catalogo solicitado.

## Cambios principales

- Eliminado manejo activo de fotografias: campos `ImageField`, formularios `file`, vistas/URLs de evidencias, `MEDIA_URL` y `MEDIA_ROOT`.
- Eliminado `telefono_alternativo` de clientes.
- Vehiculos limitados a `AUTOMOVIL`, `SUV` y `CAMIONETA`.
- Ordenes conectadas a catalogo de servicios mediante `servicio_id`.
- Ordenes ahora usan `precio` manual para el servicio principal.
- El formulario de orden filtra vehiculos segun el cliente seleccionado.
- Agregado CRUD de servicios.
- Agregado soporte base para alertas por canal: interna, email, WhatsApp o ambos.
- Agregado comando `enviar_alertas`.
- Mejoras responsive con `.form-shell` y tablas protegidas con `table-responsive`.
- Corregido serializer de vehiculos: `kilometraje_actual`.

## Archivos afectados

- Settings/URLs: `fuel_injection/settings/base.py`, `fuel_injection/urls.py`.
- Clientes: modelos, formularios, templates y migracion.
- Vehiculos: modelos, formularios, templates, serializers y migracion.
- Ordenes: modelos, formularios, vistas, URLs, serializers, templates, admin y migracion.
- Servicios: nueva app completa.
- Alertas: modelos, admin, services, comando y migracion.
- Dashboard: indicadores ejecutivos y calculo de ingresos.
- Documentacion: `docs/INSTALL.md`, `docs/ANALISIS_CAMBIOS.md`, `sql/schema.sql`.

## Pendientes operativos

- Reinstalar Python localmente o recrear `venv`; el entorno copiado apunta a otro usuario.
- Ejecutar `python manage.py migrate` en una maquina con Python/Django disponibles.
- Configurar credenciales reales SMTP y WhatsApp antes de enviar mensajes reales.
