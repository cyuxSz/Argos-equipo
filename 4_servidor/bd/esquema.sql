-- Argos: esquema MySQL 8 (InnoDB, UTC). Etapa 2 de software, version 2 (21-oct-2026).
-- Cambios contra la entrega: Caja (3 cajas, una fuente de 5 V cada una), LED rojo como actuador de cada
-- nodo, origen de la AccionControl, sensor_error en Evento y en Alerta. Ver docs/bd/etapa2_software_v2.md.
-- Probado el 6-nov-2026 en MySQL 8.4 (Docker): carga sin errores. Script de entrega: docs/bd/etapa3/.

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
