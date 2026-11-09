-- indicadores_iot_EquipoX-Matricula.sql — nodo pir (HC-SR501, movimiento en la entrada). Argos, Etapa 3.
-- Las fechas se guardan en UTC; para mostrarlas en hora de Monterrey se restan 6 h (UTC-6 todo el año).
-- Horario de acceso del cuarto: lunes a viernes 8:00-17:00.
USE argos;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 1. Movimientos por hora del dia
-- Utilidad: muestra en que horas hay mas actividad en el cuarto (y cuando conviene no entrar).
-- Usa: JOIN Evento-Sensor, filtro por tipo, HOUR() en hora local, GROUP BY, COUNT.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT HOUR(e.fecha_hora - INTERVAL 6 HOUR) AS hora_local,
       COUNT(*)                             AS movimientos
FROM Evento e
JOIN Sensor s ON s.id_sensor = e.id_sensor
WHERE s.id_nodo = 'pir' AND e.tipo = 'movimiento'
GROUP BY hora_local
ORDER BY hora_local;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 2. Movimientos por dia y cuantos fueron fuera del horario de acceso
-- Utilidad: control de accesos; un movimiento fuera de horario puede ser una entrada no autorizada.
-- Usa: WEEKDAY/HOUR en hora local, SUM de condicion, GROUP BY dia.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(e.fecha_hora - INTERVAL 6 HOUR)                               AS dia_local,
       DAYNAME(e.fecha_hora - INTERVAL 6 HOUR)                            AS dia_semana,
       COUNT(*)                                                           AS movimientos,
       SUM(WEEKDAY(e.fecha_hora - INTERVAL 6 HOUR) > 4
           OR HOUR(e.fecha_hora - INTERVAL 6 HOUR) NOT BETWEEN 8 AND 16)  AS fuera_de_horario
FROM Evento e
JOIN Sensor s ON s.id_sensor = e.id_sensor
WHERE s.id_nodo = 'pir' AND e.tipo = 'movimiento'
GROUP BY dia_local, dia_semana
ORDER BY dia_local;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 3. Primera y ultima deteccion de cada dia (ocupacion aproximada del cuarto)
-- Utilidad: estima a que hora llega y se va el personal, y cuanto tiempo hay gente cerca.
-- Usa: MIN/MAX por dia, TIMEDIFF.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(e.fecha_hora - INTERVAL 6 HOUR)          AS dia_local,
       TIME(MIN(e.fecha_hora) - INTERVAL 6 HOUR)     AS primera_deteccion,
       TIME(MAX(e.fecha_hora) - INTERVAL 6 HOUR)     AS ultima_deteccion,
       TIMEDIFF(MAX(e.fecha_hora), MIN(e.fecha_hora)) AS lapso_con_actividad
FROM Evento e
JOIN Sensor s ON s.id_sensor = e.id_sensor
WHERE s.id_nodo = 'pir' AND e.tipo = 'movimiento'
GROUP BY dia_local
ORDER BY dia_local;
