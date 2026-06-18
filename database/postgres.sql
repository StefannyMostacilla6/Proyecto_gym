CREATE TYPE estado_reserva AS ENUM ('confirmada', 'cancelada', 'lista_espera', 'completada');
CREATE TYPE dia_semana AS ENUM ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo');
CREATE TYPE rol_usuario AS ENUM ('admin', 'recepcionista', 'socio');
-- =====================================================
-- TABLA: miembros (socios del gimnasio)
-- =====================================================
CREATE TABLE miembros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT,
    fecha_nacimiento DATE,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(20) DEFAULT 'activo',
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP
);

-- =====================================================
-- TABLA: usuarios (sistema de autenticación)
-- =====================================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol rol_usuario NOT NULL DEFAULT 'socio',
    miembro_id INTEGER NULL,
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP,

    -- Constraint para la relación con miembros
    CONSTRAINT fk_usuarios_miembro
        FOREIGN KEY (miembro_id)
        REFERENCES miembros(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- =====================================================
-- TABLA: membresias (planes disponibles)
-- =====================================================
CREATE TABLE membresias (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    duracion_dias INTEGER NOT NULL,
    max_clases_semana INTEGER DEFAULT 3,
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP
);

-- =====================================================
-- TABLA: pagos (historial de pagos de miembros)
-- =====================================================
CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER NOT NULL,
    membresia_id INTEGER NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha_pago DATE DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE NOT NULL,
    metodo_pago VARCHAR(50) DEFAULT 'efectivo',
    comprobante VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'pagado',
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP,

    -- Constraints con ON DELETE CASCADE
    CONSTRAINT fk_pagos_miembro
        FOREIGN KEY (miembro_id)
        REFERENCES miembros(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_pagos_membresia
        FOREIGN KEY (membresia_id)
        REFERENCES membresias(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================
-- TABLA: entrenadores
-- =====================================================
CREATE TABLE entrenadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP
);

-- =====================================================
-- TABLA: clases (tipos de clase)
-- =====================================================
CREATE TABLE clases (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    cupo_maximo INTEGER NOT NULL DEFAULT 20,
    duracion_minutos INTEGER DEFAULT 60,
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP
);

-- =====================================================
-- TABLA: horarios (horarios de clases por entrenador)
-- =====================================================
CREATE TABLE horarios (
    id SERIAL PRIMARY KEY,
    clase_id INTEGER NOT NULL,
    entrenador_id INTEGER NOT NULL,
    dia_semana dia_semana NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    sala VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP,

    -- Constraints con ON DELETE CASCADE
    CONSTRAINT fk_horarios_clase
        FOREIGN KEY (clase_id)
        REFERENCES clases(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_horarios_entrenador
        FOREIGN KEY (entrenador_id)
        REFERENCES entrenadores(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT uq_horario_clase_dia_hora
        UNIQUE(clase_id, dia_semana, hora_inicio)
);

-- =====================================================
-- TABLA: reservas (reservas de miembros a clases)
-- =====================================================
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER NOT NULL,
    horario_id INTEGER NOT NULL,
    fecha_reserva DATE DEFAULT CURRENT_DATE,
    fecha_clase DATE NOT NULL,
    estado estado_reserva DEFAULT 'confirmada',
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP,

    -- Constraints con ON DELETE CASCADE
    CONSTRAINT fk_reservas_miembro
        FOREIGN KEY (miembro_id)
        REFERENCES miembros(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_reservas_horario
        FOREIGN KEY (horario_id)
        REFERENCES horarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- TABLA: asistencias (check-in a clases)
-- =====================================================
CREATE TABLE asistencias (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    fecha_checkin TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    creado_por VARCHAR(100) DEFAULT 'system',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_por VARCHAR(100),
    fecha_actualizacion TIMESTAMP,
    eliminado_por VARCHAR(100),
    fecha_eliminacion TIMESTAMP,

    -- Constraint con ON DELETE CASCADE
    CONSTRAINT fk_asistencias_reserva
        FOREIGN KEY (reserva_id)
        REFERENCES reservas(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- TABLA DE AUDITORÍA: registro de miembros eliminados
-- =====================================================
CREATE TABLE auditoria_miembros (
    id SERIAL PRIMARY KEY,
    miembro_id INTEGER NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    accion VARCHAR(20) NOT NULL,
    realizado_por VARCHAR(100) NOT NULL,
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_previos JSONB,
    ip_origen VARCHAR(45)
);


-- =====================================================
-- DATOS DE PRUEBA - SISTEMA GIMNASIO
-- =====================================================

-- -----------------------------------------------------
-- 1. MEMBRESIAS
-- -----------------------------------------------------
INSERT INTO membresias (tipo, descripcion, precio, duracion_dias, max_clases_semana, creado_por) VALUES
('Basica', 'Acceso a gimnasio y clases grupales basicas', 25000, 30, 3, 'system'),
('Premium', 'Acceso completo + clases especializadas + zona VIP', 45000, 30, 7, 'system'),
('VIP', 'Acceso ilimitado + entrenador personal + nutricion', 65000, 30, 10, 'system'),
('Semanal', 'Acceso por 7 dias', 8000, 7, 5, 'system'),
('Diario', 'Pase por 1 dia', 2000, 1, 2, 'system'),
('Estudiante', 'Plan especial para estudiantes', 15000, 30, 4, 'system'),
('Parejas', 'Plan para 2 personas', 40000, 30, 5, 'system'),
('Anual', 'Plan anual con descuento', 250000, 365, 7, 'system');

-- -----------------------------------------------------
-- 2. ENTRENADORES
-- -----------------------------------------------------
INSERT INTO entrenadores (nombre, apellido, especialidad, email, telefono, creado_por) VALUES
('Carlos', 'Gomez', 'Musculacion y Pesas', 'carlos.gomez@gym.com', '3001234567', 'system'),
('Maria', 'Rodriguez', 'Yoga y Pilates', 'maria.rodriguez@gym.com', '3002345678', 'system'),
('Juan', 'Perez', 'Cardio y Funcional', 'juan.perez@gym.com', '3003456789', 'system'),
('Ana', 'Martinez', 'CrossFit', 'ana.martinez@gym.com', '3004567890', 'system'),
('Luis', 'Sanchez', 'Boxeo y Artes Marciales', 'luis.sanchez@gym.com', '3005678901', 'system'),
('Laura', 'Torres', 'Zumba y Baile', 'laura.torres@gym.com', '3006789012', 'system'),
('Pedro', 'Ramirez', 'Entrenamiento Personal', 'pedro.ramirez@gym.com', '3007890123', 'system'),
('Sofia', 'Herrera', 'Nutricion y Wellness', 'sofia.herrera@gym.com', '3008901234', 'system');

-- -----------------------------------------------------
-- 3. CLASES
-- -----------------------------------------------------
INSERT INTO clases (nombre, descripcion, cupo_maximo, duracion_minutos, creado_por) VALUES
('Body Pump', 'Entrenamiento con pesas y barra', 20, 60, 'system'),
('Yoga', 'Clase de yoga para todos los niveles', 15, 90, 'system'),
('Cardio Extreme', 'Entrenamiento cardiovascular intenso', 25, 45, 'system'),
('CrossFit', 'Entrenamiento funcional de alta intensidad', 15, 60, 'system'),
('Zumba', 'Baile y ejercicio cardiovascular', 30, 60, 'system'),
('Boxeo', 'Entrenamiento de boxeo y defensa personal', 12, 60, 'system'),
('Pilates', 'Ejercicios de pilates para fortalecimiento', 12, 60, 'system'),
('Spinning', 'Ciclismo indoor', 20, 45, 'system'),
('Funcional', 'Entrenamiento con peso corporal', 20, 60, 'system'),
('Stretching', 'Estiramientos y flexibilidad', 15, 45, 'system'),
('Body Combat', 'Artes marciales y cardio', 20, 60, 'system'),
('Aquagym', 'Ejercicios en piscina', 15, 60, 'system');

-- -----------------------------------------------------
-- 4. HORARIOS
-- -----------------------------------------------------
INSERT INTO horarios (clase_id, entrenador_id, dia_semana, hora_inicio, hora_fin, sala, creado_por) VALUES
-- LUNES
(1, 1, 'Lunes', '08:00', '09:00', 'Sala A', 'system'),
(2, 2, 'Lunes', '09:30', '11:00', 'Sala B', 'system'),
(3, 3, 'Lunes', '11:30', '12:15', 'Sala C', 'system'),
(4, 4, 'Lunes', '14:00', '15:00', 'Sala D', 'system'),
(5, 6, 'Lunes', '16:00', '17:00', 'Sala E', 'system'),
(6, 5, 'Lunes', '18:00', '19:00', 'Sala D', 'system'),
-- MARTES
(7, 2, 'Martes', '08:00', '09:00', 'Sala B', 'system'),
(1, 1, 'Martes', '09:30', '10:30', 'Sala A', 'system'),
(8, 3, 'Martes', '11:00', '11:45', 'Sala C', 'system'),
(9, 4, 'Martes', '14:00', '15:00', 'Sala D', 'system'),
(10, 2, 'Martes', '16:00', '16:45', 'Sala B', 'system'),
(4, 4, 'Martes', '18:00', '19:00', 'Sala D', 'system'),
-- MIERCOLES
(2, 2, 'Miercoles', '08:00', '09:30', 'Sala B', 'system'),
(3, 3, 'Miercoles', '10:00', '10:45', 'Sala C', 'system'),
(5, 6, 'Miercoles', '11:30', '12:30', 'Sala E', 'system'),
(1, 1, 'Miercoles', '14:00', '15:00', 'Sala A', 'system'),
(6, 5, 'Miercoles', '16:00', '17:00', 'Sala D', 'system'),
(7, 2, 'Miercoles', '18:00', '19:00', 'Sala B', 'system'),
-- JUEVES
(9, 4, 'Jueves', '08:00', '09:00', 'Sala D', 'system'),
(1, 1, 'Jueves', '09:30', '10:30', 'Sala A', 'system'),
(8, 3, 'Jueves', '11:00', '11:45', 'Sala C', 'system'),
(10, 2, 'Jueves', '14:00', '14:45', 'Sala B', 'system'),
(4, 4, 'Jueves', '16:00', '17:00', 'Sala D', 'system'),
(5, 6, 'Jueves', '18:00', '19:00', 'Sala E', 'system'),
-- VIERNES
(3, 3, 'Viernes', '08:00', '08:45', 'Sala C', 'system'),
(2, 2, 'Viernes', '09:30', '11:00', 'Sala B', 'system'),
(6, 5, 'Viernes', '11:30', '12:30', 'Sala D', 'system'),
(1, 1, 'Viernes', '14:00', '15:00', 'Sala A', 'system'),
(11, 5, 'Viernes', '16:00', '17:00', 'Sala D', 'system'),
(12, 6, 'Viernes', '18:00', '19:00', 'Piscina', 'system'),
-- SABADO
(1, 1, 'Sabado', '09:00', '10:00', 'Sala A', 'system'),
(5, 6, 'Sabado', '10:30', '11:30', 'Sala E', 'system'),
(8, 3, 'Sabado', '12:00', '12:45', 'Sala C', 'system'),
(2, 2, 'Sabado', '16:00', '17:30', 'Sala B', 'system');

-- -----------------------------------------------------
-- 5. MIEMBROS
-- -----------------------------------------------------
INSERT INTO miembros (nombre, apellido, email, telefono, direccion, fecha_nacimiento, creado_por) VALUES
('Andres', 'Gonzalez', 'andres.gonzalez@email.com', '3101234567', 'Calle 123 #45-67', '1990-05-15', 'system'),
('Carolina', 'Lopez', 'carolina.lopez@email.com', '3102345678', 'Carrera 8 #20-30', '1988-09-22', 'system'),
('Miguel', 'Fernandez', 'miguel.fernandez@email.com', '3103456789', 'Avenida 45 #78-90', '1995-03-10', 'system'),
('Diana', 'Martinez', 'diana.martinez@email.com', '3104567890', 'Calle 67 #12-34', '1992-07-18', 'system'),
('Roberto', 'Garcia', 'roberto.garcia@email.com', '3105678901', 'Carrera 12 #45-67', '1985-11-30', 'system'),
('Paula', 'Rodriguez', 'paula.rodriguez@email.com', '3106789012', 'Avenida 23 #56-78', '1993-01-25', 'system'),
('Sergio', 'Perez', 'sergio.perez@email.com', '3107890123', 'Calle 90 #34-56', '1991-06-12', 'system'),
('Laura', 'Sanchez', 'laura.sanchez@email.com', '3108901234', 'Carrera 5 #67-89', '1987-04-05', 'system'),
('Jorge', 'Ramirez', 'jorge.ramirez@email.com', '3109012345', 'Avenida 34 #78-90', '1994-08-20', 'system'),
('Monica', 'Torres', 'monica.torres@email.com', '3100123456', 'Calle 56 #90-12', '1996-12-01', 'system'),
('Fernando', 'Diaz', 'fernando.diaz@email.com', '3101234560', 'Carrera 7 #34-56', '1989-02-14', 'system'),
('Valentina', 'Castro', 'valentina.castro@email.com', '3102345670', 'Avenida 67 #89-01', '1997-05-30', 'system'),
('Oscar', 'Mendoza', 'oscar.mendoza@email.com', '3103456780', 'Calle 89 #12-34', '1986-10-22', 'system'),
('Natalia', 'Rivas', 'natalia.rivas@email.com', '3104567890', 'Carrera 23 #45-67', '1998-07-15', 'system'),
('Ricardo', 'Salazar', 'ricardo.salazar@email.com', '3105678900', 'Avenida 78 #90-12', '1990-09-08', 'system');

-- -----------------------------------------------------
-- 6. USUARIOS (Contraseñas en texto plano: 123456)
-- -----------------------------------------------------
INSERT INTO usuarios (username, email, password_hash, rol, miembro_id, creado_por) VALUES
('admin', 'admin@gym.com', '123456', 'admin', NULL, 'system'),
('recepcion', 'recepcion@gym.com', '123456', 'recepcionista', NULL, 'system'),
('andres.g', 'andres.gonzalez@email.com', '123456', 'socio', 1, 'system'),
('carolina.l', 'carolina.lopez@email.com', '123456', 'socio', 2, 'system'),
('miguel.f', 'miguel.fernandez@email.com', '123456', 'socio', 3, 'system'),
('diana.m', 'diana.martinez@email.com', '123456', 'socio', 4, 'system'),
('roberto.g', 'roberto.garcia@email.com', '123456', 'socio', 5, 'system'),
('paula.r', 'paula.rodriguez@email.com', '123456', 'socio', 6, 'system'),
('sergio.p', 'sergio.perez@email.com', '123456', 'socio', 7, 'system'),
('laura.s', 'laura.sanchez@email.com', '123456', 'socio', 8, 'system'),
('jorge.r', 'jorge.ramirez@email.com', '123456', 'socio', 9, 'system'),
('monica.t', 'monica.torres@email.com', '123456', 'socio', 10, 'system');

-- -----------------------------------------------------
-- 7. PAGOS
-- -----------------------------------------------------
INSERT INTO pagos (miembro_id, membresia_id, monto, fecha_pago, fecha_vencimiento, metodo_pago, creado_por) VALUES
-- Pagos del mes actual
(1, 1, 25000, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE + INTERVAL '25 days', 'efectivo', 'system'),
(2, 2, 45000, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '20 days', 'tarjeta', 'system'),
(3, 3, 65000, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE + INTERVAL '15 days', 'nequi', 'system'),
(4, 1, 25000, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '27 days', 'efectivo', 'system'),
(5, 2, 45000, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE + INTERVAL '10 days', 'tarjeta', 'system'),
(6, 3, 65000, CURRENT_DATE - INTERVAL '25 days', CURRENT_DATE + INTERVAL '5 days', 'transferencia', 'system'),
(7, 4, 8000, CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '5 days', 'efectivo', 'system'),
(8, 5, 2000, CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '0 days', 'efectivo', 'system'),
(9, 1, 25000, CURRENT_DATE - INTERVAL '8 days', CURRENT_DATE + INTERVAL '22 days', 'tarjeta', 'system'),
(10, 2, 45000, CURRENT_DATE - INTERVAL '12 days', CURRENT_DATE + INTERVAL '18 days', 'nequi', 'system'),
-- Pagos anteriores
(1, 1, 25000, CURRENT_DATE - INTERVAL '35 days', CURRENT_DATE - INTERVAL '5 days', 'efectivo', 'system'),
(2, 2, 45000, CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '10 days', 'tarjeta', 'system'),
(3, 3, 65000, CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '15 days', 'nequi', 'system'),
(4, 1, 25000, CURRENT_DATE - INTERVAL '33 days', CURRENT_DATE - INTERVAL '3 days', 'efectivo', 'system'),
(5, 2, 45000, CURRENT_DATE - INTERVAL '50 days', CURRENT_DATE - INTERVAL '20 days', 'tarjeta', 'system');

-- -----------------------------------------------------
-- 8. RESERVAS
-- -----------------------------------------------------
INSERT INTO reservas (miembro_id, horario_id, fecha_reserva, fecha_clase, estado, creado_por) VALUES
-- Reservas confirmadas para hoy
(1, 1, CURRENT_DATE, CURRENT_DATE, 'confirmada', 'system'),
(2, 2, CURRENT_DATE, CURRENT_DATE, 'confirmada', 'system'),
(3, 3, CURRENT_DATE, CURRENT_DATE, 'confirmada', 'system'),
(4, 4, CURRENT_DATE, CURRENT_DATE, 'confirmada', 'system'),
(5, 5, CURRENT_DATE, CURRENT_DATE, 'confirmada', 'system'),
-- Reservas para manana
(6, 6, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'confirmada', 'system'),
(7, 7, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'confirmada', 'system'),
(8, 8, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'confirmada', 'system'),
(9, 9, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'confirmada', 'system'),
(10, 10, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'confirmada', 'system'),
-- Reservas para el fin de semana
(1, 11, CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 'confirmada', 'system'),
(2, 12, CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 'confirmada', 'system'),
(3, 13, CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', 'confirmada', 'system'),
-- Reservas canceladas
(4, 14, CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE - INTERVAL '1 day', 'cancelada', 'system'),
(5, 15, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE - INTERVAL '2 days', 'cancelada', 'system'),
-- Reservas en lista de espera
(6, 1, CURRENT_DATE, CURRENT_DATE, 'lista_espera', 'system'),
(7, 2, CURRENT_DATE, CURRENT_DATE, 'lista_espera', 'system');

-- -----------------------------------------------------
-- 9. ASISTENCIAS
-- -----------------------------------------------------
INSERT INTO asistencias (reserva_id, fecha_checkin, creado_por) VALUES
(1, CURRENT_DATE + INTERVAL '8 hours', 'system'),
(2, CURRENT_DATE + INTERVAL '9 hours 30 minutes', 'system'),
(3, CURRENT_DATE + INTERVAL '11 hours 30 minutes', 'system'),
(4, CURRENT_DATE + INTERVAL '14 hours', 'system'),
(5, CURRENT_DATE + INTERVAL '16 hours', 'system'),
(6, CURRENT_DATE + INTERVAL '8 hours' + INTERVAL '1 day', 'system'),
(7, CURRENT_DATE + INTERVAL '9 hours 30 minutes' + INTERVAL '1 day', 'system'),
(8, CURRENT_DATE + INTERVAL '11 hours' + INTERVAL '1 day', 'system'),
(9, CURRENT_DATE + INTERVAL '14 hours' + INTERVAL '1 day', 'system'),
(10, CURRENT_DATE + INTERVAL '16 hours' + INTERVAL '1 day', 'system');

-- -----------------------------------------------------
-- 10. AUDITORIA DE MIEMBROS
-- -----------------------------------------------------
INSERT INTO auditoria_miembros (miembro_id, nombre_completo, email, accion, realizado_por, datos_previos) VALUES
(1, 'Andres Gonzalez', 'andres.gonzalez@email.com', 'ACTUALIZACION', 'admin', '{"telefono": "3101234567", "direccion": "Calle 123 #45-67"}'::jsonb),
(2, 'Carolina Lopez', 'carolina.lopez@email.com', 'CAMBIO_PLAN', 'recepcion', '{"plan_anterior": "Basica", "plan_nuevo": "Premium"}'::jsonb),
(3, 'Miguel Fernandez', 'miguel.fernandez@email.com', 'CANCELACION_TARDIA', 'system', '{"reserva_id": 15, "motivo": "No asistio sin avisar"}'::jsonb);

-- =====================================================
-- RESUMEN DE DATOS INSERTADOS
-- =====================================================
-- membresias: 8 registros
-- entrenadores: 8 registros
-- clases: 12 registros
-- horarios: 34 registros
-- miembros: 15 registros
-- usuarios: 12 registros (contraseña: 123456)
-- pagos: 15 registros
-- reservas: 17 registros
-- asistencias: 10 registros
-- auditoria_miembros: 3 registros
-- =====================================================







-- =====================================================
-- EXTENSIÓN PARA CRYPT (si no existe)
-- =====================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================
-- PROCEDIMIENTO 1: Registrar nuevo miembro con usuario
-- =====================================================
CREATE OR REPLACE PROCEDURE registrar_miembro_completo(
    p_nombre VARCHAR,
    p_apellido VARCHAR,
    p_email VARCHAR,
    p_telefono VARCHAR,
    p_direccion TEXT,
    p_fecha_nacimiento DATE,
    p_username VARCHAR,
    p_password VARCHAR,
    p_membresia_id INTEGER,
    p_metodo_pago VARCHAR DEFAULT 'efectivo'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_miembro_id INTEGER;
    v_monto DECIMAL(10,2);
    v_duracion_dias INTEGER;
BEGIN
    -- Validaciones básicas
    IF p_email IS NULL OR p_email = '' THEN
        RAISE EXCEPTION 'El email es requerido';
    END IF;

    -- Insertar miembro
    INSERT INTO miembros (nombre, apellido, email, telefono, direccion, fecha_nacimiento, creado_por)
    VALUES (p_nombre, p_apellido, p_email, p_telefono, p_direccion, p_fecha_nacimiento, p_username)
    RETURNING id INTO v_miembro_id;

    -- Crear usuario
    INSERT INTO usuarios (username, email, password_hash, rol, miembro_id, creado_por)
    VALUES (p_username, p_email, crypt(p_password, gen_salt('bf')), 'socio', v_miembro_id, p_username);

    -- Obtener datos de la membresía
    SELECT precio, duracion_dias INTO v_monto, v_duracion_dias
    FROM membresias WHERE id = p_membresia_id;

    -- Registrar primer pago
    INSERT INTO pagos (miembro_id, membresia_id, monto, fecha_vencimiento, metodo_pago, creado_por)
    VALUES (
        v_miembro_id,
        p_membresia_id,
        v_monto,
        CURRENT_DATE + v_duracion_dias,
        p_metodo_pago,
        p_username
    );

    RAISE NOTICE 'Miembro registrado exitosamente con ID: %', v_miembro_id;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE EXCEPTION 'Error al registrar miembro: %', SQLERRM;
END;
$$;

-- =====================================================
-- PROCEDIMIENTO 2: Renovar membresía
-- =====================================================
CREATE OR REPLACE PROCEDURE renovar_membresia(
    p_miembro_id INTEGER,
    p_membresia_id INTEGER,
    p_metodo_pago VARCHAR DEFAULT 'efectivo',
    p_usuario VARCHAR DEFAULT 'system'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_monto DECIMAL(10,2);
    v_duracion_dias INTEGER;
    v_ultimo_vencimiento DATE;
BEGIN
    -- Obtener datos de la nueva membresía
    SELECT precio, duracion_dias INTO v_monto, v_duracion_dias
    FROM membresias WHERE id = p_membresia_id;

    -- Obtener último vencimiento
    SELECT fecha_vencimiento INTO v_ultimo_vencimiento
    FROM pagos
    WHERE miembro_id = p_miembro_id
    AND activo = TRUE
    ORDER BY fecha_vencimiento DESC
    LIMIT 1;

    -- Calcular nueva fecha de vencimiento
    IF v_ultimo_vencimiento IS NULL OR v_ultimo_vencimiento < CURRENT_DATE THEN
        v_ultimo_vencimiento := CURRENT_DATE;
    END IF;

    -- Registrar nuevo pago
    INSERT INTO pagos (
        miembro_id,
        membresia_id,
        monto,
        fecha_vencimiento,
        metodo_pago,
        creado_por
    ) VALUES (
        p_miembro_id,
        p_membresia_id,
        v_monto,
        v_ultimo_vencimiento + v_duracion_dias,
        p_metodo_pago,
        p_usuario
    );

    -- Actualizar estado del miembro
    UPDATE miembros
    SET estado = 'activo', actualizado_por = p_usuario
    WHERE id = p_miembro_id;

    RAISE NOTICE 'Membresía renovada exitosamente para el miembro %', p_miembro_id;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE EXCEPTION 'Error al renovar membresía: %', SQLERRM;
END;
$$;

-- =====================================================
-- PROCEDIMIENTO 3: Registrar asistencia masiva
-- =====================================================
CREATE OR REPLACE PROCEDURE registrar_asistencia(
    p_reserva_id INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    v_reserva RECORD;
BEGIN
    -- Verificar que la reserva existe y está confirmada
    SELECT * INTO v_reserva
    FROM reservas
    WHERE id = p_reserva_id
    AND estado = 'confirmada'
    AND activo = TRUE;

    IF v_reserva IS NULL THEN
        RAISE EXCEPTION 'Reserva no encontrada o no está confirmada';
    END IF;

    -- Verificar que no se haya registrado asistencia previamente
    IF EXISTS (
        SELECT 1 FROM asistencias
        WHERE reserva_id = p_reserva_id
        AND activo = TRUE
    ) THEN
        RAISE EXCEPTION 'Ya se registró asistencia para esta reserva';
    END IF;

    -- Registrar asistencia
    INSERT INTO asistencias (reserva_id, creado_por)
    VALUES (p_reserva_id, 'staff');

    RAISE NOTICE 'Asistencia registrada exitosamente';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE EXCEPTION 'Error al registrar asistencia: %', SQLERRM;
END;
$$;

-- =====================================================
-- PROCEDIMIENTO 4: Cancelar reserva con penalización
-- =====================================================
CREATE OR REPLACE PROCEDURE cancelar_reserva_con_penalizacion(
    p_reserva_id INTEGER,
    p_motivo VARCHAR DEFAULT 'Cancelación voluntaria',
    p_usuario VARCHAR DEFAULT 'system'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_reserva RECORD;
    v_dias_anticipacion INTEGER;
BEGIN
    -- Obtener datos de la reserva
    SELECT * INTO v_reserva
    FROM reservas
    WHERE id = p_reserva_id AND activo = TRUE;

    IF v_reserva IS NULL THEN
        RAISE EXCEPTION 'Reserva no encontrada';
    END IF;

    -- Calcular días de anticipación
    v_dias_anticipacion := v_reserva.fecha_clase - CURRENT_DATE;

    -- Verificar si se puede cancelar
    IF v_dias_anticipacion < 1 THEN
        RAISE EXCEPTION 'No se puede cancelar con menos de 24 horas de anticipación';
    END IF;

    -- Cancelar reserva
    UPDATE reservas SET
        estado = 'cancelada',
        actualizado_por = p_usuario,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = p_reserva_id;

    -- Si cancela con poca anticipación, registrar en auditoría
    IF v_dias_anticipacion <= 3 THEN
        INSERT INTO auditoria_miembros (
            miembro_id,
            nombre_completo,
            email,
            accion,
            realizado_por,
            datos_previos
        ) VALUES (
            v_reserva.miembro_id,
            (SELECT nombre || ' ' || apellido FROM miembros WHERE id = v_reserva.miembro_id),
            (SELECT email FROM miembros WHERE id = v_reserva.miembro_id),
            'CANCELACION_TARDIA',
            p_usuario,
            jsonb_build_object(
                'reserva_id', p_reserva_id,
                'motivo', p_motivo,
                'dias_anticipacion', v_dias_anticipacion
            )
        );
    END IF;

    RAISE NOTICE 'Reserva cancelada exitosamente';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE EXCEPTION 'Error al cancelar reserva: %', SQLERRM;
END;
$$;

-- =====================================================
-- PROCEDIMIENTO 5: Generar reporte de ingresos mensuales
-- =====================================================
CREATE OR REPLACE FUNCTION generar_reporte_mensual(
    p_anio INTEGER,
    p_mes INTEGER
)
RETURNS TABLE(
    metrica VARCHAR,
    valor VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_total_ingresos DECIMAL(10,2);
    v_total_transacciones INTEGER;
    v_miembros_activos INTEGER;
    v_membresia_popular VARCHAR;
    v_ticket_promedio DECIMAL(10,2);
BEGIN
    -- Total de ingresos
    SELECT COALESCE(SUM(monto), 0) INTO v_total_ingresos
    FROM pagos
    WHERE EXTRACT(YEAR FROM fecha_pago) = p_anio
    AND EXTRACT(MONTH FROM fecha_pago) = p_mes
    AND estado = 'pagado';

    -- Total de transacciones
    SELECT COUNT(*) INTO v_total_transacciones
    FROM pagos
    WHERE EXTRACT(YEAR FROM fecha_pago) = p_anio
    AND EXTRACT(MONTH FROM fecha_pago) = p_mes
    AND estado = 'pagado';

    -- Miembros activos (que pagaron en el mes)
    SELECT COUNT(DISTINCT miembro_id) INTO v_miembros_activos
    FROM pagos
    WHERE EXTRACT(YEAR FROM fecha_pago) = p_anio
    AND EXTRACT(MONTH FROM fecha_pago) = p_mes
    AND estado = 'pagado';

    -- Membresía más popular
    SELECT m.tipo INTO v_membresia_popular
    FROM pagos p
    INNER JOIN membresias m ON p.membresia_id = m.id
    WHERE EXTRACT(YEAR FROM p.fecha_pago) = p_anio
    AND EXTRACT(MONTH FROM p.fecha_pago) = p_mes
    GROUP BY m.tipo
    ORDER BY COUNT(*) DESC
    LIMIT 1;

    -- Ticket promedio
    v_ticket_promedio := ROUND(v_total_ingresos / NULLIF(v_total_transacciones, 0), 2);

    -- Retornar métricas
    RETURN QUERY VALUES
        ('Periodo', p_anio || '-' || LPAD(p_mes::TEXT, 2, '0')),
        ('Total Ingresos', '$' || v_total_ingresos::TEXT),
        ('Total Transacciones', v_total_transacciones::TEXT),
        ('Miembros Activos', v_miembros_activos::TEXT),
        ('Membresía Más Popular', COALESCE(v_membresia_popular, 'N/A')),
        ('Ticket Promedio', '$' || COALESCE(v_ticket_promedio::TEXT, '0'));
END;
$$;