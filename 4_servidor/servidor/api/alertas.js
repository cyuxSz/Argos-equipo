/**
 * Argos — motor de alertas de la API.
 *
 * Decide cuando se abre y se cierra cada alerta, la guarda en MySQL y la anuncia por MQTT al instante.
 * Las reglas de temperatura y humedad son las MISMAS que las del firmware (firmware/include/alarma_dht.h):
 *   - se abre al juntar `persistencia` lecturas seguidas fuera de [minimo, maximo]   (3 x 30 s = 90 s)
 *   - se cierra al juntar `persistencia` lecturas seguidas dentro de [minimo + histeresis, maximo - histeresis]
 *   - en la zona de histeresis conserva su estado (no "parpadea")
 *   Los umbrales salen de la tabla Umbral (se recargan cada 15 s: si se editan en la BD, aplican solos).
 *
 * Otras alertas (no suenan el buzzer; solo temperatura y humedad lo hacen):
 *   - sensor_falla      llega un evento sensor_error; se cierra con la siguiente medicion valida del nodo
 *   - golpe             evento golpe con magnitud >= Configuracion.umbral_golpe_g (instantanea: abre y cierra)
 *   - puerta_abierta    la puerta lleva abierta mas de Configuracion.puerta_abierta_max_s; se cierra al cerrarla
 *   - nodo_sin_reporte  el nodo no ha mandado nada por HTTP en mas de SIN_REPORTE_S; se cierra al volver
 *
 * MQTT (si hay MQTT_URL):
 *   publica  invernadero/cmd/alarma  "on" al abrir una alerta con buzzer, repetido cada 60 s mientras siga
 *            activa (el dht da por buena la orden 150 s), y "off" al cerrarse la ultima
 *   publica  invernadero/alertas     {"evento":"abierta"|"cerrada","id_alerta","id_nodo","tipo","valor","ts"}
 *   escucha  invernadero/estado/+    online/offline (LWT) -> EstadoNodo.estado, para el dashboard
 * Sin MQTT_URL (p. ej. la Etapa 3 en tu PC) todo sigue funcionando: alertas en la BD y GET /api/comandos.
 */
const mqtt = require("mqtt");

const REVISION_MS = 15000;       // cada cuanto se revisan puerta, nodos caidos y umbrales
const REPETIR_ALARMA_MS = 60000; // contrato MQTT: cmd/alarma se repite cada 60 s
const SIN_REPORTE_S = 150;       // 2.5 latidos de 60 s sin saber del nodo = caido

function crearMotor(pool) {
  const vigilancias = new Map(); // "dht/temperatura" -> {fuera, dentro, alarma}
  let umbrales = new Map();      // "dht/temperatura" -> fila de Umbral (+ id_nodo, parametro)
  let config = {};               // tabla Configuracion como objeto
  let cliente = null;            // cliente MQTT (null si no hay MQTT_URL)
  let ultimaRepeticion = 0;

  // ─── utilidades ───────────────────────────────────────────────────────────
  const log = (...a) => console.log(new Date().toISOString(), "[alertas]", ...a);

  function publicar(topic, mensaje) {
    if (cliente?.connected) cliente.publish(topic, mensaje, { qos: 0, retain: false });
  }

  async function cargarReglas() {
    const [u] = await pool.query(
      `SELECT u.id_umbral, u.minimo, u.maximo, u.histeresis, u.persistencia, u.activa_buzzer,
              s.id_nodo, p.nombre AS parametro
       FROM Umbral u JOIN Sensor s ON s.id_sensor = u.id_sensor JOIN Parametro p ON p.id_parametro = u.id_parametro`
    );
    umbrales = new Map(u.map((r) => [`${r.id_nodo}/${r.parametro}`, r]));
    const [c] = await pool.query("SELECT clave, valor FROM Configuracion");
    config = Object.fromEntries(c.map((r) => [r.clave, r.valor]));
  }

  /** Registra el encendido/apagado del buzzer ordenado por una alerta (AccionControl, origen = alerta). */
  function accionBuzzer(nodo, comando, idAlerta) {
    return pool.query(
      `INSERT INTO AccionControl (id_actuador, id_alerta, origen, comando, fecha_hora)
       SELECT id_actuador, ?, 'alerta', ?, UTC_TIMESTAMP() FROM Actuador WHERE id_nodo = ? AND tipo = 'buzzer'`,
      [idAlerta, comando, nodo]
    );
  }

  async function hayBuzzerActivo() {
    const [f] = await pool.query(
      `SELECT 1 FROM Alerta a JOIN Umbral u ON u.id_umbral = a.id_umbral
       WHERE a.ts_fin IS NULL AND u.activa_buzzer LIMIT 1`
    );
    return f.length > 0;
  }

  // ─── abrir / cerrar ───────────────────────────────────────────────────────
  /** Abre una alerta. Si ya hay una activa del mismo nodo y tipo, no hace nada (una por episodio). */
  async function abrir(nodo, tipo, valor, umbral = null, instantanea = false) {
    let id;
    try {
      const [r] = await pool.query(
        `INSERT INTO Alerta (id_nodo, id_umbral, tipo, valor, ts_inicio, ts_fin)
         VALUES (?, ?, ?, ?, UTC_TIMESTAMP(), ${instantanea ? "UTC_TIMESTAMP()" : "NULL"})`,
        [nodo, umbral?.id_umbral ?? null, tipo, valor]
      );
      id = r.insertId;
    } catch (e) {
      if (e.code === "ER_DUP_ENTRY") return; // ya estaba activa
      throw e;
    }
    log(`ABIERTA #${id} ${nodo}/${tipo} valor=${valor}`);
    if (umbral?.activa_buzzer) {
      await accionBuzzer(nodo, "on", id);
      publicar("invernadero/cmd/alarma", "on");
      ultimaRepeticion = Date.now();
    }
    publicar("invernadero/alertas", JSON.stringify({
      evento: "abierta", id_alerta: id, id_nodo: nodo, tipo, valor, ts: new Date().toISOString(),
    }));
    if (instantanea) publicar("invernadero/alertas", JSON.stringify({
      evento: "cerrada", id_alerta: id, id_nodo: nodo, tipo, valor, ts: new Date().toISOString(),
    }));
  }

  /** Cierra la alerta activa de ese nodo y tipo (si la hay). */
  async function cerrar(nodo, tipo, valor = null) {
    const [f] = await pool.query(
      `SELECT a.id_alerta, u.activa_buzzer FROM Alerta a LEFT JOIN Umbral u ON u.id_umbral = a.id_umbral
       WHERE a.id_nodo = ? AND a.tipo = ? AND a.ts_fin IS NULL`,
      [nodo, tipo]
    );
    if (f.length === 0) return;
    const { id_alerta: id, activa_buzzer } = f[0];
    await pool.query("UPDATE Alerta SET ts_fin = UTC_TIMESTAMP() WHERE id_alerta = ?", [id]);
    log(`CERRADA #${id} ${nodo}/${tipo} valor=${valor}`);
    if (activa_buzzer) {
      await accionBuzzer(nodo, "off", id);
      if (!(await hayBuzzerActivo())) publicar("invernadero/cmd/alarma", "off");
    }
    publicar("invernadero/alertas", JSON.stringify({
      evento: "cerrada", id_alerta: id, id_nodo: nodo, tipo, valor, ts: new Date().toISOString(),
    }));
  }

  // ─── reglas ───────────────────────────────────────────────────────────────
  /** Persistencia + histeresis, igual que Vigilancia::evaluar del firmware. Devuelve "abrir", "cerrar" o null. */
  function evaluar(clave, u, v) {
    const s = vigilancias.get(clave) ?? { fuera: 0, dentro: 0, alarma: false };
    vigilancias.set(clave, s);
    const n = u.persistencia;
    if (v < u.minimo || v > u.maximo) {
      s.dentro = 0;
      s.fuera = Math.min(s.fuera + 1, n);
      if (s.fuera >= n && !s.alarma) { s.alarma = true; return "abrir"; }
    } else if (v >= u.minimo + u.histeresis && v <= u.maximo - u.histeresis) {
      s.fuera = 0;
      s.dentro = Math.min(s.dentro + 1, n);
      if (s.dentro >= n && s.alarma) { s.alarma = false; return "cerrar"; }
    } else {
      s.fuera = s.dentro = 0; // zona de histeresis
    }
    return null;
  }

  /** Lo llama POST /api/mediciones despues de guardar. lecturas = [[parametro, valor], ...] */
  async function lecturas(nodo, filas) {
    await cerrar(nodo, "sensor_falla"); // una medicion valida = el sensor volvio
    for (const [parametro, valor] of filas) {
      const clave = `${nodo}/${parametro}`;
      const u = umbrales.get(clave);
      if (!u) continue; // parametro sin umbral (p. ej. luz hasta confirmar el fotoperiodo)
      const accion = evaluar(clave, u, valor);
      if (accion === "abrir") await abrir(nodo, parametro, valor, u);
      if (accion === "cerrar") await cerrar(nodo, parametro, valor);
    }
  }

  /** Lo llama POST /api/eventos despues de guardar. */
  async function evento(nodo, tipo, magnitud) {
    if (tipo === "sensor_error") await abrir(nodo, "sensor_falla", null);
    if (tipo === "golpe") {
      const minimo = Number(config.umbral_golpe_g);
      if (magnitud === null || !Number.isFinite(minimo) || magnitud >= minimo) await abrir(nodo, "golpe", magnitud, null, true);
    }
    if (tipo === "puerta_cerrada") await cerrar(nodo, "puerta_abierta");
  }

  /** Revision periodica: umbrales, nodos sin reporte, puerta abierta de mas y repeticion de cmd/alarma. */
  async function revisar() {
    await cargarReglas();

    const [nodos] = await pool.query(
      `SELECT id_nodo, TIMESTAMPDIFF(SECOND, ultimo_reporte, UTC_TIMESTAMP()) AS hace_s
       FROM EstadoNodo WHERE ultimo_reporte IS NOT NULL`
    );
    for (const { id_nodo, hace_s } of nodos) {
      if (hace_s > SIN_REPORTE_S) await abrir(id_nodo, "nodo_sin_reporte", hace_s);
      else await cerrar(id_nodo, "nodo_sin_reporte");
    }

    const maxPuerta = Number(config.puerta_abierta_max_s);
    if (Number.isFinite(maxPuerta)) {
      const [[ultimo]] = await pool.query(
        `SELECT e.tipo, TIMESTAMPDIFF(SECOND, e.fecha_hora, UTC_TIMESTAMP()) AS hace_s
         FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor
         WHERE s.id_nodo = 'puerta' AND e.tipo IN ('puerta_abierta', 'puerta_cerrada')
         ORDER BY e.fecha_hora DESC, e.id_evento DESC LIMIT 1`
      );
      if (ultimo?.tipo === "puerta_abierta" && ultimo.hace_s > maxPuerta) await abrir("puerta", "puerta_abierta", ultimo.hace_s);
    }

    if (Date.now() - ultimaRepeticion >= REPETIR_ALARMA_MS && (await hayBuzzerActivo())) {
      publicar("invernadero/cmd/alarma", "on");
      ultimaRepeticion = Date.now();
    }
  }

  // ─── MQTT ─────────────────────────────────────────────────────────────────
  function conectarMqtt() {
    const url = process.env.MQTT_URL;
    if (!url) { log("sin MQTT_URL: las alertas solo quedan en la BD"); return; }
    cliente = mqtt.connect(url, {
      username: process.env.MQTT_USER,
      password: process.env.MQTT_PASSWORD,
      clientId: "argos-api",
      keepalive: 45,
      reconnectPeriod: 5000, // si se cae Mosquitto, reintenta cada 5 s sin tumbar la API
    });
    cliente.on("connect", () => { log("conectada a MQTT"); cliente.subscribe("invernadero/estado/+"); });
    cliente.on("error", (e) => log("MQTT:", e.message));
    cliente.on("message", (topic, cuerpo) => {
      const nodo = topic.split("/")[2];
      let estado;
      try { estado = JSON.parse(cuerpo.toString()).estado; } catch { return; }
      if (estado !== "online" && estado !== "offline") return;
      pool.query("UPDATE EstadoNodo SET estado = ? WHERE id_nodo = ?", [estado, nodo])
        .catch((e) => log("no se pudo guardar el estado:", e.message));
    });
  }

  // ─── arranque ─────────────────────────────────────────────────────────────
  async function iniciar() {
    await cargarReglas();
    // Si la API se reinicia con alertas de T/HR abiertas, retoma su estado para poder cerrarlas bien.
    const [activas] = await pool.query("SELECT id_nodo, tipo FROM Alerta WHERE ts_fin IS NULL AND id_umbral IS NOT NULL");
    for (const a of activas) {
      const u = umbrales.get(`${a.id_nodo}/${a.tipo}`);
      if (u) vigilancias.set(`${a.id_nodo}/${a.tipo}`, { fuera: u.persistencia, dentro: 0, alarma: true });
    }
    conectarMqtt();
    setInterval(() => revisar().catch((e) => log("error en la revision:", e.message)), REVISION_MS);
    log(`motor listo: ${umbrales.size} umbrales, ${activas.length} alertas retomadas`);
  }

  return { iniciar, lecturas, evento };
}

module.exports = { crearMotor };
