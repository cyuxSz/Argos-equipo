-- ScriptCreacionBaseDatos_iot_EquipoX.sql — Argos (G507 · TC1004B), Etapa 3.
-- Crea la base "argos" COMPLETA (tablas, llaves, restricciones, datos fijos) y le carga datos de prueba.
-- GENERADO por docs/bd/etapa3/generar_script.py a partir de docs/bd/esquema.sql y datos_prueba.sql.
-- Requiere MySQL 8.0 o mas nuevo. Correrlo entero (DBeaver: Alt+X / Workbench: rayo).
-- OJO: borra la base "argos" si ya existe, para poder correrlo varias veces.

DROP DATABASE IF EXISTS argos;

-- Argos: esquema MySQL 8 (InnoDB, UTC). Etapa 2 de software, version 2 (21-oct-2026).
-- Cambios contra la entrega: Caja (3 cajas, una fuente de 5 V cada una), LED rojo como actuador de cada
-- nodo, origen de la AccionControl, sensor_error en Evento y en Alerta. Ver docs/bd/etapa2_software_v2.md.
-- Sin probar en un servidor MySQL todavia.

SET time_zone = '+00:00';
CREATE DATABASE IF NOT EXISTS argos CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE argos;

CREATE TABLE Caja (
  id_caja        VARCHAR(10)  NOT NULL PRIMARY KEY,           -- dht, entrada, anaquel
  descripcion    VARCHAR(60)  NOT NULL,
  area           VARCHAR(40)  NOT NULL DEFAULT 'Cuarto de incubación',
  punto_montaje  VARCHAR(40)  NULL
) ENGINE = InnoDB;

CREATE TABLE Responsable (
  id_responsable INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(60)  NOT NULL UNIQUE
) ENGINE = InnoDB;

CREATE TABLE Nodo (
  id_nodo        VARCHAR(10)  NOT NULL PRIMARY KEY,           -- igual al topic MQTT
  id_caja        VARCHAR(10)  NOT NULL,
  descripcion    VARCHAR(60)  NOT NULL,
  id_responsable INT          NOT NULL,
  CONSTRAINT fk_nodo_caja FOREIGN KEY (id_caja) REFERENCES Caja (id_caja),
  CONSTRAINT fk_nodo_resp FOREIGN KEY (id_responsable) REFERENCES Responsable (id_responsable)
) ENGINE = InnoDB;

CREATE TABLE Sensor (
  id_sensor      INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_nodo        VARCHAR(10)  NOT NULL,
  modelo         VARCHAR(40)  NOT NULL,
  CONSTRAINT fk_sensor_nodo FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
) ENGINE = InnoDB;

CREATE TABLE Parametro (
  id_parametro   INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(30)  NOT NULL UNIQUE,
  unidad         VARCHAR(10)  NOT NULL
) ENGINE = InnoDB;

CREATE TABLE Medicion (
  id_medicion    BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_sensor      INT          NOT NULL,
  id_parametro   INT          NOT NULL,
  valor          DECIMAL(8,2) NOT NULL,
  fecha_hora     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_med_sensor FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  CONSTRAINT fk_med_param  FOREIGN KEY (id_parametro) REFERENCES Parametro (id_parametro),
  INDEX ix_med_param_fecha (id_parametro, fecha_hora)
) ENGINE = InnoDB;

CREATE TABLE Evento (
  id_evento        BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_sensor        INT          NOT NULL,
  tipo             ENUM('movimiento','golpe','puerta_abierta','puerta_cerrada','sensor_error') NOT NULL,
  magnitud         DECIMAL(8,2) NULL,
  fuera_de_horario BOOLEAN      NOT NULL DEFAULT FALSE,
  fecha_hora       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_evento_sensor FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  INDEX ix_evento_tipo_fecha (tipo, fecha_hora)
) ENGINE = InnoDB;

CREATE TABLE Umbral (
  id_umbral      INT              NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_sensor      INT              NOT NULL,
  id_parametro   INT              NOT NULL,
  minimo         DECIMAL(8,2)     NOT NULL,
  maximo         DECIMAL(8,2)     NOT NULL,
  histeresis     DECIMAL(8,2)     NOT NULL DEFAULT 0,
  persistencia   TINYINT UNSIGNED NOT NULL DEFAULT 3,
  activa_buzzer  BOOLEAN          NOT NULL DEFAULT FALSE,
  CONSTRAINT fk_umbral_sensor FOREIGN KEY (id_sensor) REFERENCES Sensor (id_sensor),
  CONSTRAINT fk_umbral_param FOREIGN KEY (id_parametro) REFERENCES Parametro (id_parametro),
  CONSTRAINT uq_umbral_sensor_param UNIQUE (id_sensor, id_parametro),
  CONSTRAINT ck_umbral_rango CHECK (maximo > minimo)
) ENGINE = InnoDB;

CREATE TABLE Alerta (
  id_alerta      BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_nodo        VARCHAR(10)  NOT NULL,
  id_umbral      INT          NULL,
  tipo           VARCHAR(30)  NOT NULL,  -- temperatura, humedad, luz, golpe, puerta_abierta,
                                         -- movimiento_fuera_de_horario, nodo_sin_reporte, sensor_falla
  valor          DECIMAL(8,2) NULL,
  ts_inicio      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ts_fin         DATETIME     NULL,
  activa_clave   TINYINT      GENERATED ALWAYS AS (IF(ts_fin IS NULL, 1, NULL)) STORED,
  CONSTRAINT fk_alerta_nodo   FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo),
  CONSTRAINT fk_alerta_umbral FOREIGN KEY (id_umbral) REFERENCES Umbral (id_umbral),
  CONSTRAINT ck_alerta_fin    CHECK (ts_fin IS NULL OR ts_fin >= ts_inicio),
  CONSTRAINT uq_alerta_activa UNIQUE (id_nodo, tipo, activa_clave)   -- RN5: una activa por nodo y tipo
) ENGINE = InnoDB;

CREATE TABLE Notificacion (
  id_alerta      BIGINT       NOT NULL,
  canal          ENUM('whatsapp','telegram') NOT NULL,
  enviada        BOOLEAN      NOT NULL DEFAULT FALSE,
  ts_envio       DATETIME     NULL,
  PRIMARY KEY (id_alerta, canal),
  CONSTRAINT fk_notif_alerta FOREIGN KEY (id_alerta) REFERENCES Alerta (id_alerta)
) ENGINE = InnoDB;

CREATE TABLE Actuador (
  id_actuador    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_nodo        VARCHAR(10)  NOT NULL,
  tipo           ENUM('buzzer','led_rojo') NOT NULL,
  CONSTRAINT fk_act_nodo FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo),
  CONSTRAINT uq_act_nodo_tipo UNIQUE (id_nodo, tipo)
) ENGINE = InnoDB;

CREATE TABLE AccionControl (
  id_accion      BIGINT            NOT NULL AUTO_INCREMENT PRIMARY KEY,
  id_actuador    INT               NOT NULL,
  id_alerta      BIGINT            NULL,       -- solo si la ordeno una alerta (buzzer por cmd/alarma)
  origen         ENUM('alerta','local','manual') NOT NULL,
  comando        ENUM('on','off')  NOT NULL,
  duracion_s     SMALLINT UNSIGNED NULL,       -- encendidos de duracion fija (LED 5 s); NULL = hasta un off
  fecha_hora     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_acc_act    FOREIGN KEY (id_actuador) REFERENCES Actuador (id_actuador),
  CONSTRAINT fk_acc_alerta FOREIGN KEY (id_alerta) REFERENCES Alerta (id_alerta),
  CONSTRAINT ck_acc_origen CHECK ((origen = 'alerta') = (id_alerta IS NOT NULL))
) ENGINE = InnoDB;

CREATE TABLE EstadoNodo (
  id_nodo        VARCHAR(10)  NOT NULL PRIMARY KEY,
  estado         ENUM('online','offline') NOT NULL DEFAULT 'offline',
  ultimo_reporte DATETIME     NULL,
  reset_reason   VARCHAR(60)  NULL,
  uptime_s       INT UNSIGNED NULL,
  rssi           SMALLINT     NULL,
  CONSTRAINT fk_estado_nodo FOREIGN KEY (id_nodo) REFERENCES Nodo (id_nodo)
) ENGINE = InnoDB;

CREATE TABLE Configuracion (
  clave          VARCHAR(40)  NOT NULL PRIMARY KEY,
  valor          VARCHAR(60)  NOT NULL
) ENGINE = InnoDB;

-- RNF03: purga diaria de mediciones con mas de 90 dias (requiere event_scheduler = ON)
CREATE EVENT IF NOT EXISTS purga_mediciones
  ON SCHEDULE EVERY 1 DAY
  DO DELETE FROM Medicion WHERE fecha_hora < UTC_TIMESTAMP() - INTERVAL 90 DAY;

-- ── datos fijos del cuarto ─────────────────────────────────────────────────
INSERT INTO Caja VALUES
  ('dht',     'Nodo de temperatura y humedad (caja propia)', 'Cuarto de incubación', 'Anaquel, a la altura de los frascos'),
  ('entrada', 'Estación de entrada: pir + puerta',           'Cuarto de incubación', 'Pared junto a la puerta'),
  ('anaquel', 'Estación del anaquel: acel + luz',            'Cuarto de incubación', 'Anaquel');

INSERT INTO Responsable (nombre) VALUES
  ('José María García'), ('Arianna Téllez'), ('Luis Mendoza'), ('Iván Acosta'), ('Mía Nieto');

INSERT INTO Nodo (id_nodo, id_caja, descripcion, id_responsable) VALUES
  ('dht',    'dht',     'Temperatura y humedad',    (SELECT id_responsable FROM Responsable WHERE nombre = 'José María García')),
  ('luz',    'anaquel', 'Luz / fotoperiodo',        (SELECT id_responsable FROM Responsable WHERE nombre = 'Arianna Téllez')),
  ('pir',    'entrada', 'Movimiento / accesos',     (SELECT id_responsable FROM Responsable WHERE nombre = 'Luis Mendoza')),
  ('puerta', 'entrada', 'Puerta abierta o cerrada', (SELECT id_responsable FROM Responsable WHERE nombre = 'Iván Acosta')),
  ('acel',   'anaquel', 'Golpes / vibración',       (SELECT id_responsable FROM Responsable WHERE nombre = 'Mía Nieto'));

INSERT INTO Sensor (id_nodo, modelo) VALUES
  ('dht', 'DHT22'), ('luz', 'LDR (modelo POR CONFIRMAR)'), ('pir', 'HC-SR501'),
  ('puerta', 'Reed MC-38'), ('acel', 'GY-61 (ADXL335) + ADS1115');

INSERT INTO Parametro (nombre, unidad) VALUES ('temperatura', 'C'), ('humedad', '%'), ('luz', 'adc');

INSERT INTO Umbral (id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer) VALUES
  ((SELECT id_sensor FROM Sensor WHERE id_nodo = 'dht'), (SELECT id_parametro FROM Parametro WHERE nombre = 'temperatura'), 22, 28, 0.5, 3, TRUE),
  ((SELECT id_sensor FROM Sensor WHERE id_nodo = 'dht'), (SELECT id_parametro FROM Parametro WHERE nombre = 'humedad'),     40, 60, 2.0, 3, TRUE);

INSERT INTO Actuador (id_nodo, tipo) VALUES
  ('dht', 'buzzer'), ('dht', 'led_rojo'), ('luz', 'led_rojo'), ('pir', 'led_rojo'),
  ('puerta', 'led_rojo'), ('acel', 'led_rojo');

INSERT INTO EstadoNodo (id_nodo) VALUES ('dht'), ('luz'), ('pir'), ('puerta'), ('acel');

INSERT INTO Configuracion VALUES
  ('horario_lamparas', 'POR CONFIRMAR'),
  ('horario_acceso', 'POR CONFIRMAR'),
  ('umbral_golpe_g', '0.5'),               -- igual que el firmware; calibrar en sitio
  ('umbral_luz_adc', '300'),               -- igual que el firmware; calibrar con docs/prueba_ldr.md
  ('puerta_abierta_max_s', '120'),
  ('retencion_mediciones_dias', '90');

-- Argos — DATOS DE PRUEBA para la Etapa 3 (se corren despues de docs/bd/esquema.sql).
-- Son INVENTADOS y coherentes entre si: 3 dias que terminan "ahora", para probar la API y los indicadores.
-- NO son mediciones del cuarto. Hora en UTC; Monterrey = UTC-6 todo el año (sin horario de verano).
--
-- Que contiene:
--   dht    T y HR cada 30 min; un episodio de calor (T > 28 C) y uno de humedad alta (HR > 60 %)
--   luz    lectura cada 10 min; lamparas encendidas 06:00-20:00 (local) y un apagon de 2 h el dia -2
--   pir    movimientos en horario de trabajo y dos fuera de horario
--   puerta aperturas cortas y largas (las de mas de 120 s generan alerta)
--   acel   golpes, dos de ellos con alguien en el cuarto (movimiento en el pir al mismo tiempo)
--   + las alertas, acciones de actuadores y el estado de los nodos que corresponden a esos datos
SET time_zone = '+00:00';
USE argos;

SET @ahora = UTC_TIMESTAMP() - INTERVAL SECOND(UTC_TIMESTAMP()) SECOND;   -- ahora, sin segundos
SET @base  = TIMESTAMP(DATE(@ahora - INTERVAL 6 HOUR)) + INTERVAL 6 HOUR;  -- hoy 00:00 de Monterrey, en UTC

-- ── dht: 144 lecturas (3 dias x 48) de temperatura y humedad ───────────────
-- Base: T = 25 +- 2.2 C y HR = 50 +- 8 % (dentro de rango). Lecturas 60-66: calor (+3.5 C);
-- lecturas 100-104: humedad alta (+10 %). Lectura i = hace (143 - i) * 30 min.
INSERT INTO Medicion (id_sensor, id_parametro, valor, fecha_hora)
WITH RECURSIVE t (i) AS (SELECT 0 UNION ALL SELECT i + 1 FROM t WHERE i < 143)
SELECT s.id_sensor, p.id_parametro,
       IF(p.nombre = 'temperatura',
          ROUND(25 + 2.2 * SIN(i * PI() / 24) + IF(i BETWEEN 60 AND 66, 3.5, 0), 1),
          ROUND(50 + 8 * COS(i * PI() / 24) + IF(i BETWEEN 100 AND 104, 10, 0), 1)),
       @ahora - INTERVAL (143 - i) * 30 MINUTE
FROM t
JOIN Sensor s ON s.id_nodo = 'dht'
JOIN Parametro p ON p.nombre IN ('temperatura', 'humedad');

-- ── luz: 432 lecturas (3 dias, cada 10 min), valor ADC 0-1023 ───────────────
-- Encendidas (06:00-20:00 local) ~ 700-760; apagadas ~ 60-90. Dia -2 de 12:00 a 14:00: apagon (~ 90).
INSERT INTO Medicion (id_sensor, id_parametro, valor, fecha_hora)
WITH RECURSIVE t (i) AS (SELECT 0 UNION ALL SELECT i + 1 FROM t WHERE i < 431),
     l AS (SELECT i, @ahora - INTERVAL (431 - i) * 10 MINUTE AS ts FROM t)
SELECT s.id_sensor, p.id_parametro,
       CASE
         WHEN l.ts >= @base - INTERVAL 2 DAY + INTERVAL 12 HOUR
          AND l.ts <  @base - INTERVAL 2 DAY + INTERVAL 14 HOUR THEN 90 + (l.i % 5)
         WHEN HOUR(l.ts - INTERVAL 6 HOUR) BETWEEN 6 AND 19 THEN 700 + (l.i * 7) % 60
         ELSE 60 + (l.i * 3) % 30
       END,
       l.ts
FROM l
JOIN Sensor s ON s.id_nodo = 'luz'
JOIN Parametro p ON p.nombre = 'luz';

-- ── eventos de pir, puerta y acel (dia = dias atras, minuto = minuto del dia local) ──
CREATE TABLE tmp_evento (nodo VARCHAR(10), tipo VARCHAR(20), magnitud DECIMAL(8,2), ts DATETIME);

-- pir: 6 movimientos por dia en horario (08:15 ... 16:45) + 07:20 del dia -2 y 22:10 del dia -1 (fuera de horario)
INSERT INTO tmp_evento
SELECT 'pir', 'movimiento', NULL, @base - INTERVAL d.d DAY + INTERVAL m.m MINUTE
FROM (SELECT 1 AS d UNION ALL SELECT 2 UNION ALL SELECT 3) d
JOIN (SELECT 495 AS m UNION ALL SELECT 580 UNION ALL SELECT 665 UNION ALL SELECT 810 UNION ALL SELECT 950 UNION ALL SELECT 1005) m;
INSERT INTO tmp_evento VALUES
  ('pir', 'movimiento', NULL, @base - INTERVAL 2 DAY + INTERVAL 440 MINUTE),
  ('pir', 'movimiento', NULL, @base - INTERVAL 1 DAY + INTERVAL 1330 MINUTE);

-- puerta: (minuto de apertura, segundos abierta): 08:10 40 s, 12:00 5 min, 16:50 15 min cada dia + 10:00 25 min el dia -2
CREATE TABLE tmp_apertura (ts_abre DATETIME, dur_s INT);
INSERT INTO tmp_apertura
SELECT @base - INTERVAL d.d DAY + INTERVAL a.m MINUTE, a.s
FROM (SELECT 1 AS d UNION ALL SELECT 2 UNION ALL SELECT 3) d
JOIN (SELECT 490 AS m, 40 AS s UNION ALL SELECT 720, 300 UNION ALL SELECT 1010, 900) a;
INSERT INTO tmp_apertura VALUES (@base - INTERVAL 2 DAY + INTERVAL 600 MINUTE, 1500);
INSERT INTO tmp_evento SELECT 'puerta', 'puerta_abierta', NULL, ts_abre FROM tmp_apertura;
INSERT INTO tmp_evento SELECT 'puerta', 'puerta_cerrada', NULL, ts_abre + INTERVAL dur_s SECOND FROM tmp_apertura;

-- acel: golpes en g (el firmware solo manda los que pasan de 0.5 g)
INSERT INTO tmp_evento VALUES
  ('acel', 'golpe', 1.20, @base - INTERVAL 1 DAY + INTERVAL 581 MINUTE),   -- 1 min despues de un movimiento
  ('acel', 'golpe', 0.70, @base - INTERVAL 2 DAY + INTERVAL 811 MINUTE),   -- 1 min despues de un movimiento
  ('acel', 'golpe', 0.80, @base - INTERVAL 3 DAY + INTERVAL 200 MINUTE),   -- 03:20, cuarto vacio
  ('acel', 'golpe', 0.60, @base - INTERVAL 1 DAY + INTERVAL 1100 MINUTE),
  ('acel', 'golpe', 1.90, @base - INTERVAL 2 DAY + INTERVAL 1100 MINUTE);

INSERT INTO Evento (id_sensor, tipo, magnitud, fuera_de_horario, fecha_hora)
SELECT s.id_sensor, e.tipo, e.magnitud,
       e.tipo = 'movimiento' AND (WEEKDAY(e.ts - INTERVAL 6 HOUR) > 4 OR HOUR(e.ts - INTERVAL 6 HOUR) NOT BETWEEN 8 AND 16),
       e.ts
FROM tmp_evento e JOIN Sensor s ON s.id_nodo = e.nodo
ORDER BY e.ts;

-- ── alertas que corresponden a esos datos ───────────────────────────────────
-- T: se abre en la 3.a lectura fuera de rango (i = 62) y se cierra 3 lecturas despues de volver (i = 69)
INSERT INTO Alerta (id_nodo, id_umbral, tipo, valor, ts_inicio, ts_fin)
SELECT 'dht', u.id_umbral, 'temperatura', ROUND(25 + 2.2 * SIN(62 * PI() / 24) + 3.5, 1),
       @ahora - INTERVAL (143 - 62) * 30 MINUTE, @ahora - INTERVAL (143 - 69) * 30 MINUTE
FROM Umbral u JOIN Parametro p ON p.id_parametro = u.id_parametro WHERE p.nombre = 'temperatura';
-- HR: igual con las lecturas 102 (abre) y 107 (cierra)
INSERT INTO Alerta (id_nodo, id_umbral, tipo, valor, ts_inicio, ts_fin)
SELECT 'dht', u.id_umbral, 'humedad', ROUND(50 + 8 * COS(102 * PI() / 24) + 10, 1),
       @ahora - INTERVAL (143 - 102) * 30 MINUTE, @ahora - INTERVAL (143 - 107) * 30 MINUTE
FROM Umbral u JOIN Parametro p ON p.id_parametro = u.id_parametro WHERE p.nombre = 'humedad';
-- Puerta abierta mas de 120 s (Configuracion.puerta_abierta_max_s): de los 120 s hasta que se cierra
INSERT INTO Alerta (id_nodo, tipo, valor, ts_inicio, ts_fin)
SELECT 'puerta', 'puerta_abierta', dur_s, ts_abre + INTERVAL 120 SECOND, ts_abre + INTERVAL dur_s SECOND
FROM tmp_apertura WHERE dur_s > 120;
-- Golpes de 0.5 g o mas: alerta instantanea (abre y cierra en el mismo segundo)
INSERT INTO Alerta (id_nodo, tipo, valor, ts_inicio, ts_fin)
SELECT 'acel', 'golpe', magnitud, ts, ts FROM tmp_evento WHERE tipo = 'golpe' AND magnitud >= 0.5;

-- ── acciones de los actuadores ──────────────────────────────────────────────
-- Buzzer del dht ordenado por las alertas de T y HR (origen = alerta)
INSERT INTO AccionControl (id_actuador, id_alerta, origen, comando, fecha_hora)
SELECT ac.id_actuador, a.id_alerta, 'alerta', c.comando, IF(c.comando = 'on', a.ts_inicio, a.ts_fin)
FROM Alerta a
JOIN Actuador ac ON ac.id_nodo = 'dht' AND ac.tipo = 'buzzer'
JOIN (SELECT 'on' AS comando UNION ALL SELECT 'off') c
WHERE a.tipo IN ('temperatura', 'humedad');
-- Silencio manual (boton) 10 min despues de que empezo el calor: 30 min
INSERT INTO AccionControl (id_actuador, origen, comando, duracion_s, fecha_hora)
SELECT ac.id_actuador, 'manual', 'off', 1800, a.ts_inicio + INTERVAL 10 MINUTE
FROM Alerta a JOIN Actuador ac ON ac.id_nodo = 'dht' AND ac.tipo = 'buzzer' WHERE a.tipo = 'temperatura';

-- LED rojo (origen = local): lo que hace el firmware de cada nodo
CREATE TABLE tmp_led (nodo VARCHAR(10), comando VARCHAR(3), ts DATETIME);
INSERT INTO tmp_led                                   -- dht: fijo mientras dura su alerta de T o HR
SELECT 'dht', 'on', ts_inicio FROM Alerta WHERE tipo IN ('temperatura', 'humedad')
UNION ALL SELECT 'dht', 'off', ts_fin FROM Alerta WHERE tipo IN ('temperatura', 'humedad');
INSERT INTO tmp_led                                   -- pir y acel: 5 s despues de cada deteccion
SELECT nodo, 'on', ts FROM tmp_evento WHERE tipo IN ('movimiento', 'golpe')
UNION ALL SELECT nodo, 'off', ts + INTERVAL 5 SECOND FROM tmp_evento WHERE tipo IN ('movimiento', 'golpe');
INSERT INTO tmp_led                                   -- puerta: mientras esta abierta
SELECT 'puerta', IF(tipo = 'puerta_abierta', 'on', 'off'), ts FROM tmp_evento WHERE nodo = 'puerta';
INSERT INTO tmp_led VALUES                            -- luz: lamparas apagadas en horario (apagon del dia -2)
  ('luz', 'on',  @base - INTERVAL 2 DAY + INTERVAL 12 HOUR),
  ('luz', 'off', @base - INTERVAL 2 DAY + INTERVAL 14 HOUR);
INSERT INTO AccionControl (id_actuador, origen, comando, fecha_hora)
SELECT ac.id_actuador, 'local', l.comando, l.ts
FROM tmp_led l JOIN Actuador ac ON ac.id_nodo = l.nodo AND ac.tipo = 'led_rojo'
ORDER BY l.ts;

-- ── estado de los nodos ─────────────────────────────────────────────────────
UPDATE EstadoNodo SET estado = 'online', ultimo_reporte = @ahora, reset_reason = 'Power on',
       uptime_s = 3 * 86400, rssi = CASE id_nodo WHEN 'dht' THEN -58 WHEN 'luz' THEN -66
                                                 WHEN 'pir' THEN -61 WHEN 'puerta' THEN -63 ELSE -70 END;

DROP TABLE tmp_evento, tmp_apertura, tmp_led;
