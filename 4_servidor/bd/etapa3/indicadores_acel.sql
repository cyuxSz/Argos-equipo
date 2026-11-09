-- indicadores_iot_EquipoX-Matricula.sql — nodo acel (GY-61 + ADS1115, golpes en el anaquel). Argos, Etapa 3.
-- Las fechas se guardan en UTC; para mostrarlas en hora de Monterrey se restan 6 h (UTC-6 todo el año).
-- magnitud = | |a| - 1 g |, en g. El firmware solo reporta golpes de mas de 0.5 g.
USE argos;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 1. Golpes por dia: cuantos, magnitud promedio y maxima
-- Utilidad: los golpes al anaquel pueden tirar o contaminar frascos; ver si van en aumento.
-- Usa: JOIN Evento-Sensor, filtro por tipo, GROUP BY dia, COUNT/AVG/MAX.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(e.fecha_hora - INTERVAL 6 HOUR) AS dia_local,
       COUNT(*)                             AS golpes,
       ROUND(AVG(e.magnitud), 2)            AS magnitud_promedio_g,
       MAX(e.magnitud)                      AS magnitud_maxima_g
FROM Evento e
JOIN Sensor s ON s.id_sensor = e.id_sensor
WHERE s.id_nodo = 'acel' AND e.tipo = 'golpe'
GROUP BY dia_local
ORDER BY dia_local;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 2. Golpes clasificados por intensidad
-- Utilidad: separa vibraciones leves de golpes que si pueden dañar los cultivos.
-- Usa: CASE para clasificar, GROUP BY, COUNT y porcentaje con funcion de ventana.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT CASE WHEN e.magnitud < 1 THEN '1. leve (< 1 g)'
            WHEN e.magnitud < 1.5 THEN '2. medio (1 - 1.5 g)'
            ELSE '3. fuerte (>= 1.5 g)' END              AS intensidad,
       COUNT(*)                                          AS golpes,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS porcentaje
FROM Evento e
JOIN Sensor s ON s.id_sensor = e.id_sensor
WHERE s.id_nodo = 'acel' AND e.tipo = 'golpe'
GROUP BY intensidad
ORDER BY intensidad;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 3. Golpes con y sin gente en el cuarto (cruce con el nodo pir)
-- Utilidad: un golpe con alguien presente es manipulacion; sin nadie puede ser una falla del anaquel,
-- del minisplit o un sismo, y hay que revisarlo.
-- Usa: relacion entre nodos: subconsulta EXISTS a los movimientos del pir en los 2 min anteriores.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT g.fecha_hora - INTERVAL 6 HOUR AS golpe_local,
       g.magnitud                     AS magnitud_g,
       IF(EXISTS (SELECT 1 FROM Evento m JOIN Sensor sp ON sp.id_sensor = m.id_sensor
                  WHERE sp.id_nodo = 'pir' AND m.tipo = 'movimiento'
                    AND m.fecha_hora BETWEEN g.fecha_hora - INTERVAL 2 MINUTE AND g.fecha_hora),
          'con gente', 'sin nadie')   AS presencia
FROM Evento g
JOIN Sensor s ON s.id_sensor = g.id_sensor
WHERE s.id_nodo = 'acel' AND g.tipo = 'golpe'
ORDER BY g.fecha_hora;
