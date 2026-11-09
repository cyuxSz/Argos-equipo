/**
 * Argos — API REST (Etapa 3).
 *
 * Los NodeMCU mandan sus datos por HTTP a esta API y la API es la UNICA que escribe en MySQL.
 * (MQTT con Mosquitto corre aparte para el tiempo real: estado/LWT, cmd/alarma y el dashboard en vivo.)
 *
 * Endpoints (todos piden la cabecera  X-API-Key: <clave>):
 *   POST /api/mediciones      lecturas de un sensor            -> tabla Medicion
 *   POST /api/eventos         evento de un sensor               -> tabla Evento
 *   POST /api/acciones        cambio de un actuador (LED/buzzer) -> tabla AccionControl
 *   POST /api/latido          el nodo sigue vivo                -> tabla EstadoNodo
 *   GET  /api/comandos/:nodo  instrucciones para el nodo (alarma del buzzer)
 *   GET  /api/estado          ultimo valor de cada sensor y estado de cada nodo
 *   GET  /api/mediciones      historial de un parametro (?nodo=&parametro=&desde=&hasta=&limite=)
 *   GET  /api/alertas         alertas activas o todas (?estado=activa|todas&limite=)
 *
 * Configuracion por variables de entorno: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, API_KEY, PUERTO.
 * Todas las fechas se guardan y se devuelven en UTC (ISO 8601 con "Z").
 */
const express = require("express");
const mysql = require("mysql2/promise");
const { crearMotor } = require("./alertas"); // reglas de alertas y aviso por MQTT (ver alertas.js)

// ─── Configuracion ──────────────────────────────────────────────────────────
const PUERTO = Number(process.env.PUERTO || 3000);
const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  console.error("Falta la variable API_KEY: la API no arranca sin clave.");
  process.exit(1);
}

// Pool de conexiones: reutiliza conexiones en vez de abrir una por peticion.
// timezone 'Z' = mysql2 interpreta y manda las fechas como UTC.
const pool = mysql.createPool({
  host: process.env.DB_HOST || "localhost",
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || "argos",
  timezone: "Z",
  connectionLimit: 10,
  decimalNumbers: true, // DECIMAL -> numero de JS (no texto)
});
// Cada conexion nueva trabaja en UTC, aunque el MySQL local tenga otra zona horaria.
pool.pool.on("connection", (c) => c.query("SET time_zone = '+00:00'"));

const motor = crearMotor(pool);
/** Corre una regla de alertas sin tumbar la peticion: el dato ya quedo guardado aunque la alerta falle. */
const conAlertas = (fn) => fn().catch((e) => console.error("error en alertas:", e.message));

// Rangos fisicamente posibles por parametro: lo que caiga fuera es un error de lectura y se rechaza.
const RANGOS = {
  temperatura: [-40, 80], // DHT22
  humedad: [0, 100],      // DHT22
  luz: [0, 1023],         // ADC del ESP8266 (A0)
};
const TIPOS_EVENTO = ["movimiento", "golpe", "puerta_abierta", "puerta_cerrada", "sensor_error"];

// ─── Utilidades ─────────────────────────────────────────────────────────────
/** Error con codigo HTTP: lo lanza la validacion y lo convierte en respuesta el manejador final. */
class ErrorHttp extends Error {
  constructor(codigo, mensaje) { super(mensaje); this.codigo = codigo; }
}
const esNumero = (v) => typeof v === "number" && Number.isFinite(v);

/** Busca el sensor del nodo; si el nodo no existe responde 400. */
async function sensorDe(conexion, nodo) {
  if (typeof nodo !== "string") throw new ErrorHttp(400, "falta 'nodo'");
  const [filas] = await conexion.query("SELECT id_sensor FROM Sensor WHERE id_nodo = ?", [nodo]);
  if (filas.length === 0) throw new ErrorHttp(400, `nodo desconocido: ${nodo}`);
  return filas[0].id_sensor;
}

/** Marca al nodo como vivo: cualquier POST suyo cuenta como reporte. */
function marcarVivo(conexion, nodo, extra = {}) {
  return conexion.query(
    `UPDATE EstadoNodo SET estado = 'online', ultimo_reporte = UTC_TIMESTAMP(),
       reset_reason = COALESCE(?, reset_reason), uptime_s = COALESCE(?, uptime_s), rssi = COALESCE(?, rssi)
     WHERE id_nodo = ?`,
    [extra.reset_reason ?? null, extra.uptime_s ?? null, extra.rssi ?? null, nodo]
  );
}

/** Envuelve un manejador async para que sus errores lleguen al manejador final (500/400). */
const ruta = (fn) => (req, res, next) => fn(req, res).catch(next);

// ─── App ────────────────────────────────────────────────────────────────────
const app = express();
app.use(express.json({ limit: "10kb" })); // los nodos mandan JSON chico

// Registro de cada peticion en consola (sirve para la demo y para depurar).
app.use((req, res, next) => {
  const t0 = Date.now();
  res.on("finish", () => console.log(`${new Date().toISOString()} ${req.method} ${req.originalUrl} -> ${res.statusCode} (${Date.now() - t0} ms)`));
  next();
});

// Sin clave o con clave equivocada: 401.
app.use("/api", (req, res, next) => {
  if (req.get("X-API-Key") !== API_KEY) return res.status(401).json({ error: "clave invalida" });
  next();
});

// ─── POST: lo que mandan los NodeMCU ────────────────────────────────────────

/**
 * POST /api/mediciones
 * Cuerpo: {"nodo":"dht","lecturas":[{"parametro":"temperatura","valor":25.4},{"parametro":"humedad","valor":51.2}]}
 * Guarda todas las lecturas juntas (transaccion): o entran todas o ninguna.
 * Respuesta 201: {"guardadas":2,"alarma":"off"}  -> el dht puede usar "alarma" como respaldo de MQTT.
 */
app.post("/api/mediciones", ruta(async (req, res) => {
  const { nodo, lecturas } = req.body ?? {};
  if (!Array.isArray(lecturas) || lecturas.length === 0 || lecturas.length > 10)
    throw new ErrorHttp(400, "'lecturas' debe ser una lista de 1 a 10 elementos");

  const conexion = await pool.getConnection();
  try {
    const idSensor = await sensorDe(conexion, nodo);
    // Validar TODO antes de escribir nada.
    const filas = [];
    for (const l of lecturas) {
      const rango = RANGOS[l?.parametro];
      if (!rango) throw new ErrorHttp(400, `parametro desconocido: ${l?.parametro}`);
      if (!esNumero(l.valor) || l.valor < rango[0] || l.valor > rango[1])
        throw new ErrorHttp(400, `valor fuera de rango para ${l.parametro}: ${l.valor}`);
      filas.push([l.parametro, l.valor]);
    }
    await conexion.beginTransaction();
    for (const [parametro, valor] of filas) {
      await conexion.query(
        `INSERT INTO Medicion (id_sensor, id_parametro, valor, fecha_hora)
         SELECT ?, id_parametro, ?, UTC_TIMESTAMP() FROM Parametro WHERE nombre = ?`,
        [idSensor, valor, parametro]
      );
    }
    await marcarVivo(conexion, nodo);
    await conexion.commit();
    await conAlertas(() => motor.lecturas(nodo, filas)); // puede abrir/cerrar alertas y avisar por MQTT
    res.status(201).json({ guardadas: filas.length, alarma: await alarmaDe(conexion, nodo) });
  } catch (e) {
    await conexion.rollback().catch(() => {});
    throw e;
  } finally {
    conexion.release();
  }
}));

/**
 * POST /api/eventos
 * Cuerpo: {"nodo":"acel","tipo":"golpe","magnitud":1.8}   (magnitud opcional)
 */
app.post("/api/eventos", ruta(async (req, res) => {
  const { nodo, tipo, magnitud = null } = req.body ?? {};
  if (!TIPOS_EVENTO.includes(tipo)) throw new ErrorHttp(400, `tipo de evento invalido: ${tipo}`);
  if (magnitud !== null && !esNumero(magnitud)) throw new ErrorHttp(400, "'magnitud' debe ser numero");

  const idSensor = await sensorDe(pool, nodo);
  const [r] = await pool.query(
    "INSERT INTO Evento (id_sensor, tipo, magnitud, fecha_hora) VALUES (?, ?, ?, UTC_TIMESTAMP())",
    [idSensor, tipo, magnitud]
  );
  await marcarVivo(pool, nodo);
  await conAlertas(() => motor.evento(nodo, tipo, magnitud));
  res.status(201).json({ id_evento: r.insertId });
}));

/**
 * POST /api/acciones   (evento de actuacion)
 * Cuerpo: {"nodo":"pir","actuador":"led_rojo","comando":"on","duracion_s":5,"origen":"local"}
 * origen: "local" (lo decidio el nodo) o "manual" (boton de silencio). Las de origen "alerta"
 * las registra el servidor, no el nodo.
 */
app.post("/api/acciones", ruta(async (req, res) => {
  const { nodo, actuador, comando, duracion_s = null, origen = "local" } = req.body ?? {};
  if (!["buzzer", "led_rojo"].includes(actuador)) throw new ErrorHttp(400, `actuador invalido: ${actuador}`);
  if (!["on", "off"].includes(comando)) throw new ErrorHttp(400, "'comando' debe ser on u off");
  if (!["local", "manual"].includes(origen)) throw new ErrorHttp(400, "'origen' debe ser local o manual");
  if (duracion_s !== null && !(Number.isInteger(duracion_s) && duracion_s > 0 && duracion_s <= 65535))
    throw new ErrorHttp(400, "'duracion_s' debe ser entero positivo");

  const [act] = await pool.query("SELECT id_actuador FROM Actuador WHERE id_nodo = ? AND tipo = ?", [nodo, actuador]);
  if (act.length === 0) throw new ErrorHttp(400, `el nodo ${nodo} no tiene ${actuador}`);
  const [r] = await pool.query(
    `INSERT INTO AccionControl (id_actuador, id_alerta, origen, comando, duracion_s, fecha_hora)
     VALUES (?, NULL, ?, ?, ?, UTC_TIMESTAMP())`,
    [act[0].id_actuador, origen, comando, duracion_s]
  );
  await marcarVivo(pool, nodo);
  res.status(201).json({ id_accion: r.insertId });
}));

/**
 * POST /api/latido
 * Cuerpo: {"nodo":"luz","uptime_s":3600,"rssi":-62,"reset_reason":"Power on"}  (los 3 ultimos opcionales)
 */
app.post("/api/latido", ruta(async (req, res) => {
  const { nodo, uptime_s = null, rssi = null, reset_reason = null } = req.body ?? {};
  await sensorDe(pool, nodo); // valida que el nodo exista
  if (uptime_s !== null && !(Number.isInteger(uptime_s) && uptime_s >= 0)) throw new ErrorHttp(400, "'uptime_s' invalido");
  if (rssi !== null && !(Number.isInteger(rssi) && rssi >= -120 && rssi <= 0)) throw new ErrorHttp(400, "'rssi' invalido");
  if (reset_reason !== null && (typeof reset_reason !== "string" || reset_reason.length > 60))
    throw new ErrorHttp(400, "'reset_reason' invalido");
  await marcarVivo(pool, nodo, { uptime_s, rssi, reset_reason });
  res.status(200).json({ ok: true });
}));

// ─── GET: instrucciones para el nodo ────────────────────────────────────────

/** "on" si el nodo tiene una alerta activa de temperatura o humedad (las unicas que suenan el buzzer). */
async function alarmaDe(conexion, nodo) {
  const [f] = await conexion.query(
    `SELECT 1 FROM Alerta a JOIN Umbral u ON u.id_umbral = a.id_umbral
     WHERE a.id_nodo = ? AND a.ts_fin IS NULL AND u.activa_buzzer LIMIT 1`,
    [nodo]
  );
  return f.length ? "on" : "off";
}

/**
 * GET /api/comandos/:nodo   ->  {"nodo":"dht","alarma":"on"}
 * Respaldo por HTTP del cmd/alarma de MQTT (por si el nodo no tiene MQTT en ese momento).
 */
app.get("/api/comandos/:nodo", ruta(async (req, res) => {
  await sensorDe(pool, req.params.nodo);
  res.json({ nodo: req.params.nodo, alarma: await alarmaDe(pool, req.params.nodo) });
}));

// ─── GET: consultas (dashboard e indicadores) ───────────────────────────────

/** GET /api/estado -> {"nodos":[...], "ultimos":[...]} */
app.get("/api/estado", ruta(async (_req, res) => {
  const [nodos] = await pool.query("SELECT id_nodo, estado, ultimo_reporte, rssi, uptime_s FROM EstadoNodo ORDER BY id_nodo");
  const [ultimos] = await pool.query(`
    SELECT id_nodo, nombre AS parametro, unidad, valor, fecha_hora FROM (
      SELECT s.id_nodo, p.nombre, p.unidad, m.valor, m.fecha_hora,
             ROW_NUMBER() OVER (PARTITION BY s.id_nodo, m.id_parametro ORDER BY m.fecha_hora DESC) AS rn
      FROM Medicion m
      JOIN Sensor s    ON s.id_sensor = m.id_sensor
      JOIN Parametro p ON p.id_parametro = m.id_parametro
      WHERE m.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 1 DAY
    ) t WHERE rn = 1`);
  res.json({ nodos, ultimos });
}));

/** Convierte un texto ISO 8601 en Date; si viene vacio usa el valor por omision; si es invalido, 400. */
function fecha(texto, porOmision, nombre) {
  if (texto === undefined) return porOmision;
  const d = new Date(texto);
  if (Number.isNaN(d.getTime())) throw new ErrorHttp(400, `fecha invalida en '${nombre}'`);
  return d;
}
/** Entero dentro de [min, max]; si viene vacio usa el valor por omision; si no, 400. */
function entero(texto, porOmision, min, max, nombre) {
  if (texto === undefined) return porOmision;
  const n = Number(texto);
  if (!Number.isInteger(n) || n < min || n > max) throw new ErrorHttp(400, `'${nombre}' debe ser entero entre ${min} y ${max}`);
  return n;
}

/** GET /api/mediciones?nodo=dht&parametro=temperatura[&desde=&hasta=&limite=] */
app.get("/api/mediciones", ruta(async (req, res) => {
  const { nodo, parametro } = req.query;
  if (!parametro || !RANGOS[parametro]) throw new ErrorHttp(400, "falta 'parametro' o no existe");
  await sensorDe(pool, nodo);
  const hasta = fecha(req.query.hasta, new Date(), "hasta");
  const desde = fecha(req.query.desde, new Date(hasta.getTime() - 24 * 3600 * 1000), "desde");
  const limite = entero(req.query.limite, 500, 1, 1000, "limite");

  const [datos] = await pool.query(
    `SELECT m.fecha_hora, m.valor
     FROM Medicion m
     JOIN Sensor s    ON s.id_sensor = m.id_sensor
     JOIN Parametro p ON p.id_parametro = m.id_parametro
     WHERE s.id_nodo = ? AND p.nombre = ? AND m.fecha_hora BETWEEN ? AND ?
     ORDER BY m.fecha_hora DESC LIMIT ?`,
    [nodo, parametro, desde, hasta, limite]
  );
  const [[p]] = await pool.query("SELECT unidad FROM Parametro WHERE nombre = ?", [parametro]);
  res.json({ nodo, parametro, unidad: p?.unidad ?? null, datos });
}));

/** GET /api/alertas?estado=activa|todas&limite=50 */
app.get("/api/alertas", ruta(async (req, res) => {
  const estado = req.query.estado ?? "activa";
  if (!["activa", "todas"].includes(estado)) throw new ErrorHttp(400, "'estado' debe ser activa o todas");
  const limite = entero(req.query.limite, 50, 1, 200, "limite");
  const [alertas] = await pool.query(
    `SELECT id_alerta, id_nodo, tipo, valor, ts_inicio, ts_fin FROM Alerta
     WHERE (? = 'todas' OR ts_fin IS NULL) ORDER BY ts_inicio DESC LIMIT ?`,
    [estado, limite]
  );
  res.json({ alertas });
}));

// ─── Errores ────────────────────────────────────────────────────────────────
app.use("/api", (_req, res) => res.status(404).json({ error: "ruta no encontrada" }));

// Manejador final: 400 para JSON mal formado o validacion; 500 generico para lo demas (sin detalles internos).
app.use((err, _req, res, _next) => {
  if (err instanceof ErrorHttp) return res.status(err.codigo).json({ error: err.message });
  if (err.type === "entity.parse.failed") return res.status(400).json({ error: "JSON mal formado" });
  console.error("error interno:", err);
  res.status(500).json({ error: "error interno" });
});

app.listen(PUERTO, () => console.log(`API de Argos escuchando en el puerto ${PUERTO}`));
// El motor arranca aparte: si MySQL aun no responde, reintenta en 10 s (la API ya contesta mientras).
(function arrancarMotor() {
  motor.iniciar().catch((e) => { console.error("motor de alertas sin BD, reintento en 10 s:", e.message); setTimeout(arrancarMotor, 10000); });
})();
