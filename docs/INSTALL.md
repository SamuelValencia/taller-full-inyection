# Guia de instalacion

1. Instalar Python 3.10+ y PostgreSQL 14+.
2. Crear el entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar variables:

```bash
copy .env.example .env
```

5. Crear base de datos PostgreSQL:

```sql
CREATE DATABASE fuel_injection;
```

6. Aplicar migraciones y datos iniciales:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

7. Procesar alertas programadas:

```bash
python manage.py enviar_alertas
```

Credenciales demo del seeder:

- Usuario: `admin`
- Contrasena: `Admin1234!`
