# SISTEMA WEB DE GESTIÓN — FUEL INJECTION
## Taller Mecánico · Guayaquil, Ecuador

> **Proyecto de tesis:** "Sistema Web de Gestión de Órdenes de Servicio y Control de Mantenimiento Preventivo con Alertas Inteligentes en el Taller Mecánico Fuel Injection, Guayaquil"

---

## REQUISITOS PREVIOS

Antes de empezar asegúrate de tener instalado en tu máquina:

| Requisito | Versión mínima | Cómo verificar |
|---|---|---|
| Python | 3.10+ | `python --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | cualquiera | `git --version` |

---

## PASOS PARA LEVANTAR EL PROYECTO

### 1. Clonar o copiar el proyecto

Si ya tienes la carpeta, entra en ella:

```bash
cd fuel-injection
```

---

### 2. Crear el entorno virtual de Python

```bash
# Windows (PowerShell o CMD)
python -m venv venv

# Linux / Mac
python3 -m venv venv
```

---

### 3. Activar el entorno virtual

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux / Mac
source venv/bin/activate
```

> Sabrás que está activo cuando el prompt muestre `(venv)` al inicio.

---

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará Django, PostgreSQL driver, Bootstrap, reportlab para PDFs, y todas las demás librerías del proyecto.

---

### 5. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus credenciales:

```bash
# Windows
copy .env.example .env

# Linux / Mac
cp .env.example .env
```

Abre el archivo `.env` con cualquier editor y actualiza estos campos obligatorios:

```ini
SECRET_KEY=pon-aqui-una-clave-secreta-larga-y-aleatoria

DB_NAME=fuel_injection          # nombre de la base de datos
DB_USER=postgres               # usuario de PostgreSQL
DB_PASSWORD=tu_password        # contraseña de PostgreSQL
DB_HOST=localhost
DB_PORT=5432                   # puerto de PostgreSQL (por defecto 5432)
```

> **Importante:** El archivo `.env` nunca debe subirse a Git. Ya está en `.gitignore`.

---

### 6. Crear la base de datos en PostgreSQL

Abre una terminal de PostgreSQL (`psql`) y ejecuta:

```sql
CREATE DATABASE fuel_injection;
```

O con pgAdmin: clic derecho en "Databases" → "Create" → escribe `fuel_injection`.

---

### 7. Aplicar las migraciones

```bash
python manage.py migrate
```

Esto crea todas las tablas del sistema en la base de datos automáticamente.

---

### 8. Crear el superusuario (Administrador)

```bash
python manage.py createsuperuser
```

Ingresa:
- **Username:** admin
- **Email:** dennys.valenciam@ug.edu.ec
- **Password:** Admin123

> **Credenciales por defecto del proyecto (primer inicio de sesión):**
>
> | Campo | Valor |
> |---|---|
> | Usuario | `admin` |
> | Contraseña | `Admin123` |
>
> Cambia la contraseña después del primer ingreso desde **Admin → Usuarios → admin → Cambiar contraseña**.

---

### 9. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Abre tu navegador en: **http://127.0.0.1:8000**

Panel de administración Django: **http://127.0.0.1:8000/admin**

---

## RESUMEN DE COMANDOS (desde cero)

```bash
# 1. Entrar a la carpeta del proyecto
cd fuel_injection

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate        # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar y editar variables de entorno
copy .env.example .env
# Editar .env con tus credenciales de PostgreSQL

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Ejecutar servidor
python manage.py runserver
```

---

## ESTRUCTURA DEL PROYECTO

```
fuel-injection/
├── manage.py                       ← Punto de entrada de comandos Django
├── requirements.txt                ← Dependencias Python
├── .env.example                    ← Plantilla de variables de entorno
├── .env                            ← Variables reales (NO subir a Git)
│
├── fuel_injection/                  ← Configuración principal
│   ├── urls.py                     ← URLs raíz
│   ├── wsgi.py / asgi.py
│   └── settings/
│       ├── base.py                 ← Configuración común
│       ├── development.py          ← Desarrollo (DEBUG=True)
│       └── production.py           ← Producción (HTTPS, seguridad)
│
├── apps/                           ← Módulos del sistema
│   ├── authentication/             ← Login, logout, recuperación
│   ├── usuarios/                   ← Gestión de usuarios y roles
│   ├── clientes/                   ← CRUD Clientes
│   ├── vehiculos/                  ← CRUD Vehículos
│   ├── ordenes/                    ← Órdenes de servicio
│   ├── cotizaciones/               ← Presupuestos
│   ├── mantenimiento/              ← Mantenimiento preventivo
│   ├── alertas/                    ← Alertas inteligentes
│   ├── dashboard/                  ← Panel de control
│   └── reportes/                   ← Generación de PDF y Excel
│
├── templates/                      ← HTML globales (base, navbar, sidebar)
├── static/                         ← CSS, JS, imágenes
└── media/                          ← Archivos subidos por usuarios
```

---

## MÓDULOS DEL SISTEMA

| Módulo | URL | Descripción |
|---|---|---|
| Dashboard | `/` | Panel principal con estadísticas y gráficos |
| Autenticación | `/auth/` | Login, logout, recuperar contraseña |
| Clientes | `/clientes/` | Registrar, editar, buscar, historial |
| Vehículos | `/vehiculos/` | Placa, marca, modelo, km, historial |
| Órdenes de servicio | `/ordenes/` | Crear, seguir, gestionar estados |
| Cotizaciones | `/cotizaciones/` | Presupuestos con aprobación del cliente |
| Mantenimiento | `/mantenimiento/` | Programación por km y por tiempo |
| Alertas | `/alertas/` | Notificaciones automáticas inteligentes |
| Reportes | `/reportes/` | PDF y Excel de órdenes e historial |
| Admin Django | `/admin/` | Panel de administración interno |
| API REST | `/api/v1/` | Endpoints JSON para integraciones |

---

## ROLES Y PERMISOS

| Rol | Accesos |
|---|---|
| **Administrador** | Acceso total: usuarios, reportes, configuración |
| **Mecánico** | Ver y gestionar sus órdenes asignadas, historial |
| **Recepcionista** | Clientes, vehículos, órdenes, cotizaciones |

---

## BASE DE DATOS

### Tablas principales

| Tabla | Descripción |
|---|---|
| `usuarios_usuario` | Usuarios con rol (Admin/Mecánico/Recepcionista) |
| `clientes_cliente` | Propietarios de vehículos |
| `vehiculos_vehiculo` | Vehículos registrados |
| `ordenes_ordenservicio` | Órdenes de servicio con estados y costos |
| `ordenes_detalleorden` | Ítems de trabajo / repuestos por orden |
| `ordenes_evidenciaorden` | Fotografías adjuntas a la orden |
| `cotizaciones_cotizacion` | Presupuestos previos a la orden |
| `mantenimiento_tiposervicioMantenimiento` | Catálogo de servicios preventivos |
| `mantenimiento_programamantenimiento` | Programación por km y fecha por vehículo |
| `mantenimiento_historialmantenimiento` | Registro histórico de cada servicio |
| `alertas_alerta` | Alertas automáticas del sistema |

---

## TECNOLOGÍAS UTILIZADAS

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + Django 4.2 |
| API REST | Django REST Framework 3.15 |
| Base de datos | PostgreSQL 14+ |
| Frontend | HTML5 + CSS3 + Bootstrap 5 + JavaScript |
| Formularios | django-crispy-forms + crispy-bootstrap5 |
| PDF | xhtml2pdf + reportlab |
| Excel | openpyxl |
| Variables de entorno | python-decouple |
| Imágenes | Pillow |

---

## DATOS DE DEMOSTRACIÓN (Seeder)

Para cargar datos de prueba y ver el sistema funcionando de inmediato, ejecuta:

```bash
python manage.py seed_data
```

Esto crea automáticamente:

| Datos | Cantidad |
|---|---|
| Usuarios (mecánicos + recepcionistas) | 4 |
| Clientes con datos reales de Guayaquil | 12 |
| Vehículos (Toyota, Chevrolet, Hyundai, Ford, etc.) | 15 |
| Tipos de mantenimiento (aceite, frenos, correa, etc.) | 10 |
| Órdenes de servicio (todos los estados) | 12 |
| Cotizaciones (aprobadas, pendientes, rechazadas) | 4 |
| Historial de mantenimiento | 7 |
| Programas de mantenimiento preventivo | 7 |
| Alertas inteligentes (urgentes, warnings, info) | 6 |

> El comando es **idempotente**: si ya existen datos, no duplica registros.

### Usuarios creados por el seeder

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Admin1234!` | Administrador |
| `mecanico1` | `Demo1234!` | Mecánico |
| `mecanico2` | `Demo1234!` | Mecánico |
| `recep1` | `Demo1234!` | Recepcionista |
| `recep2` | `Demo1234!` | Recepcionista |

---

## COMANDOS ÚTILES

```bash
# Ver migraciones pendientes
python manage.py showmigrations

# Generar nuevas migraciones tras cambiar modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Cargar datos de demostración
python manage.py seed_data

# Abrir shell interactivo de Django
python manage.py shell

# Colectar archivos estáticos (para producción)
python manage.py collectstatic

# Cambiar contraseña de un usuario
python manage.py changepassword admin
```

---

## SOLUCIÓN DE PROBLEMAS COMUNES

### Error: `ModuleNotFoundError: No module named 'decouple'`
El entorno virtual no está activado. Ejecuta:
```bash
venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate     # Linux/Mac
```

### Error: `django.db.utils.OperationalError: could not connect to server`
- Verifica que PostgreSQL esté corriendo
- Revisa `DB_HOST`, `DB_PORT`, `DB_USER` y `DB_PASSWORD` en `.env`

### Error: `relation "usuarios_usuario" does not exist`
Las migraciones no se aplicaron. Ejecuta `python manage.py migrate`

### Error al activar en PowerShell: `cannot be loaded because running scripts is disabled`
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

*Proyecto desarrollado para tesis — Mecánica Automotriz Fuel Inyection Electronic , Guayaquil, Ecuador*


venv\Scripts\Activate.ps1
python manage.py runserver#   t a l l e r - f u l l - i n y e c t i o n  
 