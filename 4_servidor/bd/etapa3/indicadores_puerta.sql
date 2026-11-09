-- indicadores_iot_EquipoX-Matricula.sql — nodo puerta (reed MC-38). Argos, Etapa 3.
-- Las fechas se guardan en UTC; para mostrarlas en hora de Monterrey se restan 6 h (UTC-6 todo el año).
USE argos;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 1. Aperturas de la puerta por dia
-- Utilidad: cada apertura mete aire del pasillo y puede mover la temperatura y la humedad.
-- Usa: JOIN Evento-Sensor, filtro por tipo, GROUP BY dia, COUNT.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(e.fecha_hora - INTERVAL 6 HOUR) AS dia_local,
       COUNT(*)                             AS aperturas
FROM Evento e
JOIN Sensor s ON s.id_sensor = e.id_sensor
WHERE s.id_nodo = 'puerta' AND e.tipo = 'puerta_abierta'
GROUP BY dia_local
ORDER BY dia_local;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 2. Tiempo que queda abierta: promedio y maximo por dia
-- Utilidad: una puerta abierta mucho tiempo es la que mas afecta el ambiente del cuarto.
-- Usa: LEAD() para emparejar cada apertura con el siguiente cierre, TIMESTAMPDIFF, AVG/MAX.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(abre - INTERVAL 6 HOUR)                  AS dia_local,
       COUNT(*)                                      AS aperturas,
       ROUND(AVG(TIMESTAMPDIFF(SECOND, abre, cierra))) AS promedio_s,
       MAX(TIMESTAMPDIFF(SECOND, abre, cierra))      AS maximo_s
FROM (
  SELECT e.tipo, e.fecha_hora AS abre,
         LEAD(e.fecha_hora) OVER (ORDER BY e.fecha_hora, e.id_evento) AS cierra
  FROM Evento e
  JOIN Sensor s ON s.id_sensor = e.id_sensor
  WHERE s.id_nodo = 'puerta' AND e.tipo IN ('puerta_abierta', 'puerta_cerrada')
) t
WHERE tipo = 'puerta_abierta' AND cierra IS NOT NULL
GROUP BY dia_local
ORDER BY dia_local;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 3. Veces que la puerta se quedo abierta de mas (alertas) y cuanto tardaron en cerrarla
-- Utilidad: mide la disciplina de uso; el limite sale de Configuracion.puerta_abierta_max_s.
-- Usa: Alerta + Configuracion, TIMESTAMPDIFF, filtro por tipo.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT a.id_alerta,
       a.ts_inicio - INTERVAL 6 HOUR                           AS alerta_local,
       c.valor                                                 AS limite_s,
       a.valor                                                 AS segundos_abierta,
       TIMESTAMPDIFF(SECOND, a.ts_inicio, a.ts_fin)            AS segundos_despues_del_limite
FROM Alerta a
CROSS JOIN Configuracion c
WHERE a.id_nodo = 'puerta' AND a.tipo = 'puerta_abierta' AND c.clave = 'puerta_abierta_max_s'
ORDER BY a.ts_inicio;
