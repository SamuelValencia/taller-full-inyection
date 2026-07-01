CREATE TABLE servicios_servicio (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL DEFAULT '',
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX servicios_s_nombre_b6403b_idx ON servicios_servicio (nombre);
CREATE INDEX servicios_s_estado_2d3c90_idx ON servicios_servicio (estado);

ALTER TABLE clientes_cliente DROP COLUMN IF EXISTS telefono_alternativo;
ALTER TABLE vehiculos_vehiculo DROP COLUMN IF EXISTS foto;

ALTER TABLE ordenes_ordenservicio
    ADD COLUMN IF NOT EXISTS servicio_id BIGINT NULL REFERENCES servicios_servicio(id) DEFERRABLE INITIALLY DEFERRED,
    ADD COLUMN IF NOT EXISTS precio NUMERIC(10, 2) NOT NULL DEFAULT 0;

DROP TABLE IF EXISTS ordenes_evidenciaorden CASCADE;

CREATE INDEX IF NOT EXISTS ordenes_ordenservicio_servicio_id_idx ON ordenes_ordenservicio (servicio_id);
