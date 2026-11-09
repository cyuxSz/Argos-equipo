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
