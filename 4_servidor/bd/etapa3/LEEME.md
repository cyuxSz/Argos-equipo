# Etapa 3: base de datos, API REST e indicadores

Probado el 6-nov-2026 en un MySQL 8.4 limpio, configurado a propósito con una zona horaria distinta de UTC. El script corre sin errores y se puede volver a correr. Las 15 consultas dan resultados.

## Archivos

| Archivo | Para qué | Nombre de entrega |
|---|---|---|
| `ScriptCreacionBaseDatos_iot_EquipoX.sql` | Crea la base `argos` completa y carga los datos de prueba. Lo arma `generar_script.py`. | `ScriptCreacionBaseDatos_iot_Equipo#.sql` (el mismo para todo el equipo) |
| `indicadores_dht.sql` | José María García | `indicadores_iot_EquipoX-Matricula.sql` |
| `indicadores_luz.sql` | Arianna Téllez | ídem |
| `indicadores_pir.sql` | Luis Mendoza | ídem |
| `indicadores_puerta.sql` | Iván Acosta | ídem |
| `indicadores_acel.sql` | Mía Nieto | ídem |
| `../../../servidor/api/RestApi.js` + `alertas.js` + `package.json` | API REST (Node.js) | `RestApi-EquipoX-Matricula.js` + los demás archivos |
| `../../../firmware/arduino_ide/argos_<nodo>/` | Programa del NodeMCU (el `.ino` y sus `.h`) | `Arduino-EquipoX-Matricula.ino` + los `.h` |

Número de equipo y matrículas `[POR CONFIRMAR]`. Con el número: `python docs/bd/etapa3/generar_script.py 7` (por ejemplo) genera el script ya con su nombre.

Los datos de prueba son inventados (3 días que terminan en el momento en que corres el script). Cuando el circuito real mande datos, estos se agregan encima.

## Paso a paso (cada integrante, en su PC)

1. **Base de datos.** En DBeaver, conéctate a tu MySQL local, abre `ScriptCreacionBaseDatos_iot_EquipoX.sql` y ejecútalo como script con Alt+X.
   - Refresca la conexión. Debe aparecer `argos` con 14 tablas.
   - El diagrama de clases sale en la pestaña *ER Diagram* de la base. Captura la imagen y las tablas de tu sensor.
2. **Usuario para la API (recomendado).** En DBeaver, cambia `CLAVE` por una contraseña tuya y ejecuta:
   ```sql
   CREATE USER 'argos_api'@'localhost' IDENTIFIED BY 'CLAVE';
   GRANT SELECT, INSERT, UPDATE ON argos.* TO 'argos_api'@'localhost';
   ```
3. **API REST.** Necesitas Node.js 20 o más nuevo. En una terminal:
   ```bash
   cd servidor/api
   npm install
   ```
   Copia `config_local.example` como `config_local` y llena `DB_USER=argos_api`, `DB_PASSWORD` y una `API_KEY` que tú inventes. Deja `MQTT_URL` vacío si no tienes Mosquitto. Luego:
   ```bash
   npm run local
   ```
   Debe imprimir `API de Argos escuchando en el puerto 3000`.
4. **Probar la API sin el NodeMCU.** Cambia `TU_CLAVE` por tu `API_KEY`:
   ```bash
   curl -H "X-API-Key: TU_CLAVE" http://localhost:3000/api/estado
   ```
   ```bash
   curl -H "X-API-Key: TU_CLAVE" -H "Content-Type: application/json" -d "{\"nodo\":\"pir\",\"tipo\":\"movimiento\"}" http://localhost:3000/api/eventos
   ```
5. **NodeMCU.**
   - Abre `firmware/arduino_ide/argos_<tu_nodo>/` en Arduino IDE.
   - Copia `secrets.example.h` como `secrets.h` en esa carpeta y llena el WiFi. En `API_HOST` va la IP de tu PC (`ipconfig` → IPv4), en `API_PORT` va 3000 y en `API_KEY` la misma clave.
   - El firewall de Windows debe dejar entrar el puerto 3000.
   - Las versiones de las librerías están en `docs/arduino_ide.md`.
6. **Indicadores.** Abre tu `indicadores_<nodo>.sql` en DBeaver y ejecuta cada consulta. Captura el resultado para el PDF.

## Endpoints

| Método | Ruta | Qué hace | Tabla |
|---|---|---|---|
| POST | `/api/mediciones` | Guarda lecturas de un sensor | Medicion |
| POST | `/api/eventos` | Guarda un evento (movimiento, golpe, puerta…) | Evento |
| POST | `/api/acciones` | Guarda un cambio del LED rojo o del buzzer | AccionControl |
| POST | `/api/latido` | Marca al nodo como vivo | EstadoNodo |
| GET | `/api/comandos/:nodo` | Orden de alarma para el nodo (`on`/`off`) | Alerta |
| GET | `/api/estado` | Último valor de cada sensor y estado de los nodos | Medicion, EstadoNodo |
| GET | `/api/mediciones?nodo=&parametro=` | Historial de un parámetro | Medicion |
| GET | `/api/alertas?estado=activa\|todas` | Alertas | Alerta |

Todas las rutas piden la cabecera `X-API-Key`. Sin clave o con una clave equivocada responden 401. Con un dato inválido responden 400 (por ejemplo, humedad de 150 o un nodo que no existe). Si falla MySQL responden 500.

## Frecuencia de registro (para el video)

- `dht`: cada 30 s. Es un buen equilibrio entre detectar a tiempo (una alerta se abre en 90 s, con 3 lecturas) y no llenar la BD: son unas 5,800 filas al día. Las mediciones de más de 90 días se purgan solas.
- `luz`: toma una muestra cada 5 s y manda el promedio cada 60 s. La luz cambia poco, y el promedio filtra sombras momentáneas.
- `pir`, `puerta` y `acel`: solo cuando pasa algo (un evento). Además mandan un latido cada 60 s para que se sepa que siguen vivos.
- Actuadores: cada vez que el LED rojo se prende o se apaga, y cuando se silencia el buzzer con el botón. Las acciones del buzzer que ordena una alerta las registra el servidor.
