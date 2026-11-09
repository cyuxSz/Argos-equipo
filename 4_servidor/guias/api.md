# Web API de consulta (n8n)

> **Reemplazado el 6-nov-2026:** la API ahora es Node.js (Express + mysql2) en `servidor/api/RestApi.js`, con los mismos GET de abajo más los POST de los nodos (Etapa 3). Este documento queda como antecedente del diseño de consultas.

21-oct-2026. **Diseño; no implementado ni probado.** Las consultas SQL no se han ejecutado en un servidor MySQL (ver `bd/esquema.sql`).

La Web API es obligatoria. Se implementa con **webhooks de n8n**: cada endpoint es un workflow corto `Webhook (GET)` → `MySQL` → `Respond to Webhook`. Es solo lectura: los nodos siguen publicando por MQTT y el contrato MQTT no cambia.

## Arquitectura

```
dashboard (navegador) ──GET /api/...──▶ nginx ──▶ n8n /webhook/api/... ──▶ MySQL (usuario solo lectura)
                      ◀──MQTT.js (tiempo real)── Mosquitto
```

- nginx reenvía `location /api/` a `n8n:5678/webhook/api/`. El dashboard usa el mismo origen (sin CORS) y el editor de n8n no queda expuesto.
- El tiempo real sigue por MQTT.js; la API sirve el estado inicial y el historial.
- n8n debe tener el workflow **activo** (la URL de producción es `/webhook/...`; `/webhook-test/...` solo funciona con el editor abierto).

## Autenticación

Credencial *Header Auth* en cada nodo Webhook: cabecera `X-API-Key` con la clave guardada en `.env` (`API_KEY`, no versionada; `.env.example` solo con el nombre). Sin cabecera o con clave errónea: **401**.

## Endpoints

Todas las fechas van en **UTC**, formato ISO 8601.

### `GET /api/estado`

Último valor por nodo y parámetro (últimas 24 h) y estado de cada nodo.

```json
{
  "nodos": [{"id_nodo": "dht", "estado": "online", "ultimo_reporte": "2026-10-21T18:02:11Z", "rssi": -62, "uptime_s": 5400}],
  "ultimos": [{"id_nodo": "dht", "parametro": "temperatura", "valor": 25.4, "unidad": "C", "fecha_hora": "2026-10-21T18:02:00Z"}]
}
```

### `GET /api/mediciones`

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `nodo` | sí | `dht`, `luz`, `pir`, `puerta`, `acel` |
| `parametro` | sí | `temperatura`, `humedad`, `luz`, … (nombre en `Parametro`) |
| `desde`, `hasta` | no | ISO 8601 UTC; por defecto, últimas 24 h |
| `limite` | no | Entero 1–1000; por defecto 500 |

Respuesta: `{"nodo": "dht", "parametro": "temperatura", "unidad": "C", "datos": [{"fecha_hora": "...", "valor": 25.4}]}`.

### `GET /api/alertas`

| Parámetro | Descripción |
|---|---|
| `estado` | `activa` (por defecto) o `todas` |
| `limite` | Entero 1–200; por defecto 50 |

Respuesta: lista de `{id_alerta, id_nodo, tipo, valor, ts_inicio, ts_fin}`; `ts_fin` es `null` mientras la alerta sigue activa.

## Errores

| Código | Cuándo |
|---|---|
| 400 | Falta `nodo` o `parametro`, valor fuera de lista, fecha inválida, `limite` fuera de rango |
| 401 | Falta la clave o es incorrecta |
| 500 | Falla de MySQL (mensaje genérico, sin detalle interno) |

## Consultas SQL (borrador)

Los valores del usuario van como **parámetros del nodo MySQL** (`?` + *Query Parameters*), nunca concatenados al texto de la consulta. Antes de consultar, un nodo `IF`/`Code` valida `nodo` y `parametro` contra lista y recorta `limite`.

```sql
-- /api/estado (ultimos)
SELECT id_nodo, nombre AS parametro, unidad, valor, fecha_hora FROM (
  SELECT s.id_nodo, p.nombre, p.unidad, m.valor, m.fecha_hora,
         ROW_NUMBER() OVER (PARTITION BY s.id_nodo, m.id_parametro ORDER BY m.fecha_hora DESC) AS rn
  FROM Medicion m
  JOIN Sensor s    ON s.id_sensor = m.id_sensor
  JOIN Parametro p ON p.id_parametro = m.id_parametro
  WHERE m.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 1 DAY
) t WHERE rn = 1;

-- /api/estado (nodos)
SELECT id_nodo, estado, ultimo_reporte, rssi, uptime_s FROM EstadoNodo;

-- /api/mediciones   (? = nodo, parametro, desde, hasta, limite)
SELECT m.fecha_hora, m.valor
FROM Medicion m
JOIN Sensor s    ON s.id_sensor = m.id_sensor
JOIN Parametro p ON p.id_parametro = m.id_parametro
WHERE s.id_nodo = ? AND p.nombre = ? AND m.fecha_hora BETWEEN ? AND ?
ORDER BY m.fecha_hora DESC LIMIT ?;

-- /api/alertas      (? = estado, limite)
SELECT id_alerta, id_nodo, tipo, valor, ts_inicio, ts_fin
FROM Alerta
WHERE (? = 'todas' OR ts_fin IS NULL)
ORDER BY ts_inicio DESC LIMIT ?;
```

## Seguridad y operación

- Usuario MySQL **de solo lectura** (`SELECT` sobre `Medicion`, `Sensor`, `Parametro`, `Alerta`, `EstadoNodo`) para estos workflows; distinto del usuario que escribe.
- No tocar el n8n productivo: se prueba en el compose local.
- Costo del paso extra: una consulta HTTP más (decenas de ms) y n8n como punto único de falla para consultas. No afecta la ingesta ni las alertas por MQTT.

## Pendiente

- `[POR CONFIRMAR]` si la rúbrica acepta webhooks de n8n como "Web API" (pregunta B1 en `preguntas.md`). Si exige una API propia, el siguiente paso es un servicio pequeño (p. ej. FastAPI) en el compose con los mismos endpoints.
- `[POR CONFIRMAR]` si piden documentación OpenAPI: se escribiría un `openapi.yaml` corto con estos tres endpoints.
- Falta construir los workflows, ubicar su JSON exportado en el repo, enlazar el dashboard y probar con `simulador/simulador_nodos.py`.
