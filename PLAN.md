# Argos: auditoría y reparto en 5 frentes

9-nov-2026 (arranque: martes 10 de nov). Equipo G507 (TC1004B). Líder e integrador: Luis Mendoza, dueño del repositorio. Contexto del proyecto en `README.md`; pines en `1_electronica/README.md`; contrato MQTT en `3_firmware/README.md`.

## 1. Auditoría: dónde estamos

| Área | Hecho | Falta |
|---|---|---|
| Diseño electrónico | Circuitos de los 5 nodos, protoboard punto a punto con chequeo automático de redes, WireViz, KiCad con ERC, Fritzing, árbol de alimentación | **Nada armado ni medido con piezas reales.** Medir componentes, armar, probar continuidad y voltajes |
| Firmware | Los 6 entornos compilan (PlatformIO y Arduino IDE); reglas del buzzer con 21 pruebas en PC; envío por HTTP POST a la API en curso (sin commit) | **Ningún NodeMCU flasheado.** Faltan la prueba en hardware, el WiFi real del invernadero, la calibración y el horario del fotoperiodo |
| Carcasas 3D | 3 cajas + caja de potencia sin interferencias, imprimibles sin soportes, 3MF listos, piezas de prueba de ajuste | **Nada impreso.** Falta el peine de holguras, ajustar `medidas.json` con lo medido e imprimir en PETG |
| Cuarto e instalación | Medidas de los encargados, plano 2D, modelo 3D y largos de cable (`2_carcasas_3d/guias/plano_ubicacion.md`) | Medir alturas de planchas, puerta, minisplit y contactos; autorización de fijación |
| Servidor | Docker Compose con Mosquitto (usuarios + ACL), MySQL (esquema v2), API Node.js, nginx y página inicial (**casi todo sin commit**); simulador de los 5 nodos | Levantarlo en la laptop con Windows 11 de punta a punta con el simulador, flujos de alertas en n8n con horario 7–22 h, dashboard con 5 indicadores, Oracle Cloud solo si sobra tiempo |
| Entregables | Avances 1–2 (docx/pdf), Etapa 2 de BD, presupuesto, solicitud de compra | **ExpoIngenierías: video, reporte técnico, perfil y fotos (vencen 20 y 24 de nov)**; entregas del curso que sigan |
| Gestión | Este repositorio de lectura para el equipo | Repositorio principal en GitHub donde cada quien haga commits; `5_expo/preguntas_pendientes.md` sin enviar |

### Riesgos principales

1. **El hardware no ha llegado y no hay fecha (9-nov).** Todo lo que no depende de él avanza ya: firmware y servidor probados con el simulador, diseño 3D, plano, video y reporte. El armado se prepara (checklists, tablas de medición, guion de pruebas) para hacerse en uno o dos días cuando llegue.
2. **ExpoIngenierías pide demostrar el prototipo físico** "de manera robusta y consistente" en el video, que vence el **20 de nov**. Si el hardware no llega a tiempo, el video muestra el sistema completo con el simulador, los modelos 3D y las pruebas en PC, y se explica qué falta. Si llega cualquier NodeMCU del kit, se graba al menos un nodo real `[POR CONFIRMAR qué del kit ya tenemos]`.
3. **WiFi del invernadero desconocido.** Si es WPA2-Enterprise, el ESP8266 casi no conecta. Plan B: un router o hotspot propio para la demo.
4. **Una sola persona tiene los archivos.** Este repositorio de lectura reparte la información; el trabajo se integra en el repositorio principal.

### Medidas que faltan (se reparten en los frentes)

- **Componentes (calibrador):** NodeMCU (Amica o LoLin), OLED 2.42", DHT22, KY-012, GY-61, ADS1115, MC-38 y su distancia real de cierre, HC-SR501, botón, LED, LDR, MB-102 y protoboard de 400.
- **Cuarto (cinta y foto):** altura y espesor de cada plancha, ancho y giro de la puerta, posición del minisplit, contactos junto a la puerta, distancia de los anaqueles a la puerta.
- **Eléctricas:** consumo de cada caja (P-05), corriente real de las fuentes, breaker del circuito C7, watts reales de una luminaria.
- **Ambiente:** RSSI del WiFi en cada ubicación, lectura del DHT22 contra el termohigrómetro de referencia, lectura de la LDR con luz encendida y apagada.

## 2. Calendario que manda

| Fecha | Qué |
|---|---|
| lun 9 nov | Aviso de preselección de ExpoIngenierías (revisar correo). Sin trabajo del equipo |
| **mar 10 nov** | **Arranque.** Cada quien lee `PLAN.md` y la carpeta de su frente e instala lo necesario |
| **jue 12 nov** | Servidor arriba en la laptop con Windows 11 (Docker Desktop) y el simulador conectado; lista de mejoras al diseño 3D propuesta |
| **vie 13 nov** | Servidor + simulador de punta a punta (dashboard con datos, una alerta en el celular); guion del video; mejoras de diseño decididas |
| **lun 16 nov** | Renders y capturas finales; borrador completo del reporte; checklists de armado y medición listos |
| **mar 17 nov** | Grabación del video (con hardware si ya llegó; si no, con simulador y CAD) |
| **jue 19 nov** | Video editado, reporte final en PDF, 3 imágenes + fondo del perfil. Meta: subir todo esa noche |
| Al llegar el hardware | 1–2 días: medir, armar, flashear y probar con el servidor ya listo; después imprimir con las medidas reales |
| **vie 20 nov, 23:59** | **Subir video MP4 (3–5 min), reporte PDF y perfil (3 imágenes + fondo + logo)** |
| **mar 24 nov** | **Fotos de cada integrante**; aviso de seleccionados y stand |
| mié 25 – lun 30 nov | Muestra virtual |
| mar 1 dic, 12–17 h | Expo presencial (Arena Borregos): demo en vivo en el stand |

## 3. Los 5 frentes

Cómo usar este repositorio: §4. Reparto acordado el 9-nov:

| Frente | Encargados |
|---|---|
| 1 · Electrónica, armado, mediciones y pruebas de banco | Iván, Arianna, Mía |
| 2 · Carcasas 3D: diseño, uniones, impresión e instalación | Mía, Arianna |
| 3 · Firmware y pruebas simuladas | Luis |
| 4 · Servidor, BD, API, alertas y dashboard | José María, Luis |
| 5 · ExpoIngenierías y entregables | Luis, Arianna, Mía, Iván, José María |

---

### Frente 1 · Electrónica, armado y pruebas de banco

*Encargados: Iván, Arianna y Mía.*

1. **Descripción.** Pasar el diseño a circuitos reales: armar las 3 cajas en protoboard siguiendo `1_electronica/fuente/layouts.py`, medir componentes y comprobar que todo enciende y lee bien antes de meterlo en las carcasas.
2. **Objetivo.** Mientras llega el hardware (sin fecha): dominar los circuitos y dejar listos los checklists de armado, la tabla de medición y el guion de pruebas para el **lunes 16 de nov**. Cuando llegue: en 1–2 días, las 3 cajas armadas en protoboard, con continuidad y voltajes verificados y cada sensor leyendo en el monitor serie.
3. **Requisitos a instalar.** Ninguno obligatorio para armar. Para consultar diagramas: un visor de PDF/PNG (están en `1_electronica/`). Opcional: KiCad 10 (esquemáticos), Fritzing (vista de protoboard). Herramientas: multímetro, calibrador, pinzas, cautín si hay que soldar headers.
4. **Puntos a investigar.**
   - Pinout del NodeMCU ESP8266 (D0–D8, A0, 3V3, VIN) y qué pines son de arranque (D3, D4, D8).
   - Niveles de 3.3 V vs 5 V; por qué el PIR y el buzzer van a VIN y los demás a 3V3.
   - Divisor de voltaje (LDR + 10 kΩ) y lectura del ADC del ESP8266 (el A0 del NodeMCU acepta 0–3.3 V gracias al divisor de la placa; 0–1023).
   - Transistor 2N2222 como interruptor de lado bajo (buzzer); resistencias de base y pull-down.
   - Pull-up interno (`INPUT_PULLUP`) para el reed y el botón; antirrebote.
   - Bus I²C (OLED y ADS1115, direcciones 0x3C / 0x48).
   - Cómo leer un esquemático y una tabla punto a punto; rieles partidos de la MB-102.
5. **Qué aporta.** Sin esto no hay prototipo físico: es lo que el jurado ve funcionar.
6. **Instrucciones y entregable.**
   - Medir con calibrador cada componente y anotar en `2_carcasas_3d/codigo/medidas.json` (valor, unidad, `medido`). Pasar los cambios al Frente 2.
   - Verificar con multímetro que el riel de 3V3 de cada MB-102 esté partido.
   - Armar cada caja con `1_electronica/protoboard/` y `1_electronica/guias/prompts_armado.md`; pruebas de continuidad y voltajes de `1_electronica/guias/guia_ensamble.md`.
   - Pruebas de componente: LDR con la lámpara (`1_electronica/guias/prueba_ldr.md`), distancia de cierre del MC-38, consumo por caja (P-05), sensibilidad y retardo del PIR.
   - **Entregable:** las 3 cajas armadas, una tabla de mediciones (`mediciones.md` (repo principal): componente, valor esperado, medido, ok) y fotos del armado para el Frente 5.

**Pines (resumen; fuente de verdad: `1_electronica/README.md`).**

| Nodo | Pines |
|---|---|
| Todos | D7 LED verde, D8 LED rojo (cada uno con 330 Ω a GND); C1 220 µF entre VIN y GND |
| `dht` | D4 DATA DHT22 (pull-up 10 kΩ); D1/D2 SCL/SDA de la OLED; D5 base del 2N2222 (buzzer); D6 botón a GND |
| `luz` | A0 divisor LDR + 10 kΩ |
| `pir` | D5 OUT del HC-SR501 (alimentado a VIN) |
| `puerta` | D5 reed a GND |
| `acel` | D1/D2 SCL/SDA del ADS1115 (0x48); GY-61 X/Y/Z a A0/A1/A2 del ADS1115 |

---

### Frente 2 · Carcasas 3D, uniones e instalación en el cuarto

*Encargadas: Mía y Arianna.*

1. **Descripción.** Revisar, afinar y mejorar el diseño de las carcasas (3 cajas, capuchón de la LDR, portas del MC-38, soportes): estética, uniones, facilidad de armado, ventilación, montaje. Se puede cambiar lo que haga falta. Después imprimirlas y planear la instalación en el cuarto con el plano de ubicación.
2. **Objetivo.** Para el **jueves 12 de nov**, una lista de mejoras al diseño y los bocetos de identidad propuestos; el **viernes 13**, decididos (incluye si se adopta la variante modular); para el **lunes 16 de nov**, aplicada, renders finales para el video y el reporte e impresas las piezas de prueba (peine de holguras). Las cajas finales se imprimen cuando el hardware llegue y se midan las piezas.
3. **Requisitos a instalar.** El laminador de la impresora (Creality Print, PrusaSlicer o Cura). Para ver modelos: el Visor 3D de Windows abre los `.3mf`, `.stl` y `.glb`. Para modificar el CAD: Python con `uv` y build123d (comando en `2_carcasas_3d/README.md`) o pedírselo al líder.
4. **Puntos a investigar.**
   - Tolerancias de impresión FDM (holgura de 0.3 mm), el peine de holguras y por qué se imprime primero.
   - Uniones: insertos térmicos M3 vs tuercas cautivas vs tornillo directo en plástico (piloto de 2.8 mm); orejas, tacos de pared y ranuras tipo bocallave.
   - Uniones a presión (clips): brazo en voladizo, relación largo/espesor, redondeo en la raíz, por qué el brazo se imprime acostado y cómo se afina el apriete con un cupón. Ejemplo ya modelado en `2_carcasas_3d/guias/carcasas_modulares.md`.
   - Sistemas modulares de montaje impresos (SnapBoards, CheeseBoard, openGrid): qué ideas sirven para quitar y poner la electrónica sin herramienta.
   - **Forma e identidad del producto:** buscar referencias de sensores y estaciones ambientales, siluetas distintas a la caja rectangular, patrones de ventilación, dos tonos, iconos y un rasgo que identifique a Argos (por ejemplo el ojo). Lista inicial de ideas en `2_carcasas_3d/guias/carcasas_modulares.md`.
   - Orientación de impresión sin soportes, puentes y voladizos; PETG vs PLA (temperatura, humedad, limpieza con alcohol).
   - Ventilación pasiva y por qué el DHT22 va en una cámara separada abajo.
   - Alivio de tensión de cables y paso del micro-USB/USB-C.
   - Fijación en anaqueles sin dañarlos (cinchos, pinza); qué autoricen los encargados.
5. **Qué aporta.** Convierte el prototipo de banco en algo instalable, limpio y presentable: pesa mucho en la impresión del jurado y en el uso real.
6. **Instrucciones y entregable.**
   - Revisar los modelos (visor web y renders) y proponer mejoras: forma y acabado, tamaño, ubicación de LED y pantalla, tipo de unión de la tapa, cómo se cuelga o se fija, acceso a cables. Las mejoras se aplican en el código build123d (`2_carcasas_3d/codigo/nodos.py`, medidas en `2_carcasas_3d/codigo/medidas.json`) o se piden a Luis con un boceto.
   - **Variante modular (10-nov):** revisar el modelo base con clips de protoboard, tapa a presión sin tornillos y grapa de la OLED (`2_carcasas_3d/guias/carcasas_modulares.md`, renders en `2_carcasas_3d/renders/modular/`). Decidir si se adopta en lugar de la tapa con tornillos y qué falta (retención del PIR, bandeja, montaje).
   - **Propuesta de identidad:** 2 o 3 bocetos a mano que combinen las ideas de forma (cápsula, frente inclinado, persianas del DHT22, aro de luz, ojo de Argos, patrón de ventilas, dos tonos). Elegir una con el equipo y aplicarla primero al `dht`.
   - Imprimir primero `2_carcasas_3d/imprimir/pruebas_ajuste/` (peine de holguras y piezas de ajuste) y el cupón de clips de `2_carcasas_3d/imprimir/pruebas_ajuste/`; registrar el resultado en `2_carcasas_3d/guias/pruebas_ajuste.md`.
   - Con las medidas del Frente 1, regenerar (Luis, en el repo principal) e imprimir las piezas de `2_carcasas_3d/imprimir/3mf/` según `2_carcasas_3d/guias/impresion_3d.md`.
   - Medir el cuarto (lista de §1) y actualizar `SUP` en `2_carcasas_3d/codigo/cuarto.py`; rehacer el plano.
   - **Entregable:** carcasas impresas y montadas, fotos y renders para el Frente 5, `2_carcasas_3d/guias/plano_ubicacion.md` con medidas reales y la lista de fijaciones usadas.

---

### Frente 3 · Firmware y pruebas simuladas

*Encargado: Luis.*

1. **Descripción.** Cargar y depurar el código de los 5 nodos; validar todo lo posible sin hardware (simulador y pruebas en PC) y después en las placas armadas.
2. **Objetivo.** Para el **viernes 13 de nov**, el simulador de los 5 nodos funcionando de punta a punta con el servidor (MQTT + HTTP), y el firmware compilando con la versión final. Cuando llegue el hardware: los 5 nodos reales publicando, con LED, buzzer y LWT comportándose como se diseñó.
3. **Requisitos a instalar.** Arduino IDE 2.x con el core ESP8266 3.1.2 y las librerías de `3_firmware/guias/arduino_ide.md`, **o** VS Code + PlatformIO. Driver USB del NodeMCU (CP2102 o CH340, según la placa). Python 3.12 (para el simulador y `prueba_alarma.py`). Un cliente MQTT para observar (MQTT Explorer).
4. **Puntos a investigar.**
   - Ciclo `setup()`/`loop()` sin bloqueos (`millis()` en vez de `delay()`).
   - WiFi en ESP8266: reconexión, RSSI, por qué no conviene WPA2-Enterprise.
   - MQTT: topics, QoS, mensajes retenidos, keep-alive y LWT; librería PubSubClient. JSON con ArduinoJson 6.
   - HTTP POST desde el ESP8266 a la API (cuándo MQTT y cuándo HTTP; decisión del 6-nov).
   - Persistencia e histéresis en alarmas (`3_firmware/firmware/include/alarma_dht.h`).
   - NTP y zona horaria (para el fotoperiodo futuro).
   - Cómo flashear y leer el monitor serie; `secrets.h` (nunca se sube a GitHub).
5. **Qué aporta.** Es el comportamiento del sistema: lecturas, avisos locales y la conexión con el servidor.
6. **Instrucciones y entregable.**
   - Sin hardware: correr `python 3_firmware/firmware/herramientas/prueba_alarma.py` y `3_firmware/simulador/simulador_nodos.py` contra el broker del Frente 4; compilar los 6 entornos.
   - Con hardware: crear `secrets.h` desde `secrets.example.h`, flashear un nodo a la vez y probar con el Frente 1.
   - Pruebas: reconexión al quitar el WiFi, LWT al desconectar, `cmd/alarma` on/off, botón de silencio 30 min, LED rojo de cada nodo, umbral de golpe del `acel`.
   - **Entregable:** firmware probado en las 5 placas, tabla de pruebas (`pruebas_firmware.md` (repo principal): prueba, resultado, evidencia) y capturas del monitor serie y MQTT Explorer para el video.

---

### Frente 4 · Servidor, base de datos, alertas y dashboard

*Encargados: José María y Luis.*

1. **Descripción.** La parte de software: Mosquitto, MySQL, API Node.js, n8n (alertas por WhatsApp/Telegram con horario) y el dashboard web con los indicadores.
2. **Objetivo.** Para el **viernes 13 de nov**, el sistema completo corriendo en la laptop con Windows 11 (Docker Desktop), recibiendo datos del simulador, con dashboard en vivo y al menos una alerta grave llegando al celular. Es lo que se puede demostrar aunque no llegue el hardware.
3. **Requisitos a instalar.** Docker Desktop, Git, Node.js 20+ (para la API fuera de Docker), un cliente MySQL (MySQL Workbench o DBeaver), MQTT Explorer, Postman o `curl`.
4. **Puntos a investigar.**
   - Docker Compose: servicios, volúmenes, redes y variables de entorno (`.env`, nunca en git).
   - Mosquitto: usuarios, ACL y LWT. MySQL: esquema v2 (`4_servidor/bd/esquema.sql`), UTC vs America/Monterrey.
   - API REST con Express: endpoints GET de consulta y POST de los nodos (`4_servidor/servidor/api/RestApi.js`).
   - n8n: disparadores MQTT/cron, nodos MySQL, CallMeBot y bot de Telegram; alertas "graves" de `README.md`, una por episodio, horario 7–22 h y resumen a las 7:00.
   - Dashboard con Chart.js y MQTT.js; los 5 indicadores propuestos en `5_expo/preguntas_pendientes.md` (B5).
   - Oracle Cloud Always Free (ARM64): opcional, después de la Expo; el servidor es la laptop con Windows 11.
5. **Qué aporta.** Convierte las lecturas en información útil para los encargados: historial, avisos al celular y tablero; también es el requisito de Web API del curso.
6. **Instrucciones y entregable.**
   - Seguir `4_servidor/guias/tutorial_servidor.md`; `docker compose up` en `4_servidor/servidor/`; crear usuarios MQTT con `crear_usuarios_mqtt.sh`.
   - Probar de punta a punta con el simulador antes de tener placas.
   - Flujos de n8n exportados en `servidor/n8n/*.json` (repo principal) (sin credenciales).
   - **Entregable:** servidor reproducible con `docker compose up`, dashboard con 5 indicadores, alerta probada (captura del WhatsApp/Telegram), y `pruebas_servidor.md` (repo principal).

---

### Frente 5 · ExpoIngenierías, entregables y coordinación

*Encargados: todo el equipo.*

1. **Descripción.** Todo lo que se entrega y se presenta: ExpoIngenierías (video, reporte, perfil, fotos, stand), entregas del curso, comunicación con encargados y profesores, y el repositorio en GitHub.
2. **Objetivo.** Subir video, reporte y perfil antes del **viernes 20 de nov, 23:59** (meta: el jueves 19 en la noche), y las fotos antes del **martes 24 de nov**, cumpliendo los anexos 4–6 de la convocatoria.
3. **Requisitos a instalar.** Editor de video (CapCut, Clipchamp o DaVinci Resolve), Canva o PowerPoint, Word, un convertidor a GIF (para la imagen 1 del perfil), Git + GitHub Desktop.
4. **Puntos a investigar.**
   - Convocatoria 28ª edición: categoría **Desarrollo de prototipo físico** (confirmar con la que se registró `[POR CONFIRMAR]`) y sus criterios: qué se desarrolló, creatividad, funcionamiento robusto, técnicas de ingeniería, impacto.
   - Atributos opcionales: Impacto Social (ODS 2 hambre cero / 9 industria / 12 producción responsable; vinculación con el invernadero) y Emprendimiento.
   - Estructura del reporte técnico (Anexo 5) y formato APA 7.
5. **Qué aporta.** Es lo que evalúan el profesor y el jurado; también deja el proyecto documentado para los encargados.
6. **Instrucciones y entregable.**
   - **Video (Anexo 4):** MP4, **3 a 5 min**, nombre de archivo ≤ 30 caracteres, voz explicando (no generado todo con IA), con imágenes de pruebas. Debe incluir: equipo, tutor(es), modelo educativo y materia; problema; solución; por qué es innovador; alcance; técnicas (diagramas); resultados; impacto; descripción del prototipo; demostración robusta sobre fondo blanco.
   - **Reporte (Anexo 5):** PDF, nombre ≤ 30 caracteres. Puede ser el reporte del curso. Secciones: resumen, introducción, contexto, delimitación, problema, justificación, marco teórico, objetivos, hipótesis, metodología, técnicas y herramientas, infraestructura, recursos, resultados, conclusiones, bibliografía, anexos.
   - **Perfil (Anexo 6):** 3 imágenes del proyecto (la 1 de preferencia GIF), una imagen de fondo y logo opcional. **Ninguna foto de integrantes ahí** (descalifica). Fotos de los integrantes van aparte, antes del 24 de nov.
   - **Stand (1 dic):** demo en vivo que no dependa del WiFi del lugar: laptop con el servidor + router propio + las 3 cajas + algo para provocar alertas (secadora o hielo para el DHT22, imán para el MC-38).
   - Enviar `5_expo/preguntas_pendientes.md` a encargados y profesores.
   - **Entregable:** video, reporte y perfil subidos (captura de la confirmación), guion del video en `5_expo/guion.md`, checklist de la convocatoria marcada.

---

### Submódulo opcional · Control de luces (fotoperiodo)

Solo si la versión base funciona antes del 20 de nov; si no, va como "trabajo a futuro" en el reporte y en el video. Lo comparten el Frente 1 (caja de potencia de 127 V, solo con revisión del Ing. Puga; `1_electronica/guias/caja_potencia_luz.md`) y el Frente 3 (horario por plancha con NTP). Falta definir si cada relé controla "la plancha N de los dos anaqueles" (extensiones de 4–5 m) o "de un solo anaquel".

## 4. Cómo usar este repositorio

- Es **de lectura**: aquí está todo lo necesario para entender y preparar cada frente. No hace falta saber git: se puede navegar en GitHub o bajar el ZIP (botón *Code → Download ZIP*).
- Cada carpeta `1_` a `5_` es un frente y tiene un `README.md` que dice por dónde empezar.
- Lo que cada frente produzca (mediciones, fotos, cambios de diseño, capturas, guion) se manda a Luis o se sube después al **repositorio principal del proyecto**, donde cada quien hará sus commits.
- Los documentos copiados de `guias/` mencionan rutas del repositorio principal (por ejemplo `2_carcasas_3d/codigo/nodos.py` o `docs/...`). La tabla de equivalencias está en el `README.md` de la raíz.
- No hay claves en este repositorio: las plantillas `*.example` solo traen los nombres de las variables.
