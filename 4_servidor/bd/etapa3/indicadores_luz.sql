-- indicadores_iot_EquipoX-Matricula.sql — nodo luz (LDR en A0, valor ADC 0-1023). Argos, Etapa 3.
-- Las fechas se guardan en UTC; para mostrarlas en hora de Monterrey se restan 6 h (UTC-6 todo el año).
-- "Lamparas encendidas" = lectura >= Configuracion.umbral_luz_adc (300 por ahora, se calibra en sitio).
USE argos;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 1. Nivel de luz promedio por hora del dia (perfil del fotoperiodo)
-- Utilidad: muestra a que hora se encienden y apagan las lamparas en la practica.
-- Usa: JOIN Medicion-Sensor, HOUR() en hora local, GROUP BY hora, AVG/MIN/MAX.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT HOUR(m.fecha_hora - INTERVAL 6 HOUR) AS hora_local,
       ROUND(AVG(m.valor))                  AS promedio_adc,
       MIN(m.valor)                         AS minimo_adc,
       MAX(m.valor)                         AS maximo_adc,
       COUNT(*)                             AS lecturas
FROM Medicion m
JOIN Sensor s ON s.id_sensor = m.id_sensor
WHERE s.id_nodo = 'luz'
GROUP BY hora_local
ORDER BY hora_local;

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 2. Horas de luz por dia (estimadas)
-- Utilidad: comprueba que cada dia los cultivos reciben las horas de luz del fotoperiodo.
-- Horas = (lecturas encendidas / lecturas del dia) x 24. El umbral sale de la tabla Configuracion.
-- Usa: subconsulta a Configuracion, SUM de condicion, GROUP BY dia.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT DATE(m.fecha_hora - INTERVAL 6 HOUR)                  AS dia_local,
       SUM(m.valor >= c.umbral)                              AS lecturas_encendidas,
       COUNT(*)                                              AS lecturas,
       ROUND(24 * SUM(m.valor >= c.umbral) / COUNT(*), 1)    AS horas_de_luz
FROM Medicion m
JOIN Sensor s ON s.id_sensor = m.id_sensor
CROSS JOIN (SELECT CAST(valor AS DECIMAL(8,2)) AS umbral FROM Configuracion WHERE clave = 'umbral_luz_adc') c
WHERE s.id_nodo = 'luz'
GROUP BY dia_local
ORDER BY dia_local;
-- Nota: el primer y el ultimo dia pueden salir incompletos (los datos no cubren las 24 h).

-- ─────────────────────────────────────────────────────────────────────────────
-- Indicador 3. Apagones en horario de luz (06:00-20:00 local) y cuanto duraron
-- Utilidad: detecta lamparas que se apagaron cuando debian estar encendidas (falla de luminaria,
-- temporizador o corte) usando el LED rojo del nodo, que se enciende con las lamparas apagadas.
-- Usa: AccionControl + Actuador, LEAD() para emparejar cada "on" con su "off", TIMESTAMPDIFF.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT inicio - INTERVAL 6 HOUR                 AS inicio_local,
       fin - INTERVAL 6 HOUR                    AS fin_local,
       TIMESTAMPDIFF(MINUTE, inicio, fin)       AS duracion_min
FROM (
  SELECT ac.comando, ac.fecha_hora AS inicio,
         LEAD(ac.fecha_hora) OVER (ORDER BY ac.fecha_hora) AS fin
  FROM AccionControl ac
  JOIN Actuador a ON a.id_actuador = ac.id_actuador
  WHERE a.id_nodo = 'luz' AND a.tipo = 'led_rojo'
) t
WHERE comando = 'on' AND HOUR(inicio - INTERVAL 6 HOUR) BETWEEN 6 AND 19
ORDER BY inicio;
