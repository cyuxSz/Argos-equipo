-- indicadores_iot_EquipoX-Matricula.sql — nodo dht (DHT22: temperatura y humedad). Argos, Etapa 3.
-- Las fechas se guardan en UTC; para mostrarlas en hora de Monterrey se restan 6 h (UTC-6 todo el año).
USE argos;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 1. Resumen diario de temperatura y humedad (promedio, minimo y maximo)
-- Utilidad: ver de un vistazo si el cuarto se mantuvo en 22-28 C y 40-60 % HR cada dia.
-- Usa: JOIN Medicion-Sensor-Parametro, GROUP BY dia y parametro, AVG/MIN/MAX.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(m.fecha_hora - INTERVAL 6 HOUR) AS dia_local,
       p.nombre                              AS parametro,
       p.unidad,
       ROUND(AVG(m.valor), 1)                AS promedio,
       MIN(m.valor)                          AS minimo,
       MAX(m.valor)                          AS maximo,
       COUNT(*)                              AS lecturas
FROM Medicion m
JOIN Sensor s    ON s.id_sensor = m.id_sensor
JOIN Parametro p ON p.id_parametro = m.id_parametro
WHERE s.id_nodo = 'dht'
GROUP BY dia_local, p.nombre, p.unidad
ORDER BY dia_local, parametro;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 2. Porcentaje de lecturas fuera de rango por dia
-- Utilidad: mide que tan seguido el ambiente sale del rango seguro de los cultivos in vitro.
-- El rango NO esta escrito aqui: sale de la tabla Umbral (si se cambia alla, el indicador lo sigue).
-- Usa: JOIN con Umbral, SUM de una condicion / COUNT, GROUP BY.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(m.fecha_hora - INTERVAL 6 HOUR)                                   AS dia_local,
       p.nombre                                                                AS parametro,
       CONCAT(u.minimo, ' - ', u.maximo, ' ', p.unidad)                        AS rango,
       SUM(m.valor < u.minimo OR m.valor > u.maximo)                           AS fuera_de_rango,
       COUNT(*)                                                                AS lecturas,
       ROUND(100 * SUM(m.valor < u.minimo OR m.valor > u.maximo) / COUNT(*), 1) AS porcentaje_fuera
FROM Medicion m
JOIN Sensor s    ON s.id_sensor = m.id_sensor
JOIN Parametro p ON p.id_parametro = m.id_parametro
JOIN Umbral u    ON u.id_sensor = m.id_sensor AND u.id_parametro = m.id_parametro
WHERE s.id_nodo = 'dht'
GROUP BY dia_local, p.nombre, u.minimo, u.maximo, p.unidad
ORDER BY dia_local, parametro;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 3. Alertas de temperatura y humedad: cuantas, cuanto duraron y como respondio el buzzer
-- Utilidad: evalua si las alertas se atienden rapido (duracion) y si alguien silencio el buzzer.
-- Usa: Alerta + AccionControl + Actuador (LEFT JOIN), TIMESTAMPDIFF, agregados por alerta.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT a.id_alerta,
       a.tipo,
       a.valor                                                   AS valor_al_abrir,
       a.ts_inicio - INTERVAL 6 HOUR                             AS inicio_local,
       COALESCE(TIMESTAMPDIFF(MINUTE, a.ts_inicio, a.ts_fin),
                CONCAT(TIMESTAMPDIFF(MINUTE, a.ts_inicio, UTC_TIMESTAMP()), ' (sigue activa)')) AS duracion_min,
       SUM(ac.origen = 'alerta' AND ac.comando = 'on')           AS buzzer_encendido,
       (SELECT COUNT(*) FROM AccionControl x
          JOIN Actuador b ON b.id_actuador = x.id_actuador AND b.id_nodo = 'dht' AND b.tipo = 'buzzer'
         WHERE x.origen = 'manual'
           AND x.fecha_hora BETWEEN a.ts_inicio AND COALESCE(a.ts_fin, UTC_TIMESTAMP())) AS silenciada_con_boton
FROM Alerta a
LEFT JOIN AccionControl ac ON ac.id_alerta = a.id_alerta
WHERE a.id_nodo = 'dht' AND a.tipo IN ('temperatura', 'humedad')
GROUP BY a.id_alerta, a.tipo, a.valor, a.ts_inicio, a.ts_fin
ORDER BY a.ts_inicio;
