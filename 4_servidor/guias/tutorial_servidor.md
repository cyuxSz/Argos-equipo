# Tutorial: montar el servidor de Argos (Docker, MQTT, MySQL, n8n, API, Oracle)

Guía paso a paso para armar tú mismo todo el lado servidor. Cada lección dice qué es la pieza, te da el archivo con comentarios, cómo comprobar que funciona y cómo guardarla en git. **Está escrita sin haberla corrido**: el motor de Docker estaba apagado cuando se redactó, así que lo que dependa de la versión exacta de una herramienta está marcado con `[verificar]`. Si algo no sale como dice aquí, cámbialo tú y anótalo.

Conviene seguir el orden. Cada lección usa lo de la anterior.

## Antes de empezar

**Terminal.** Usa **Git Bash** (no PowerShell). Todos los comandos están escritos para Git Bash.

**Rutas.** Todo se hace desde la raíz del proyecto (`IncuMonitor/`) salvo que diga `cd servidor`.

**Fin de línea (LF, no CRLF).** Windows guarda los archivos con un salto de línea distinto al de Linux. Si un archivo de configuración o un `.sh` queda con CRLF, los programas dentro de los contenedores fallan con errores raros (`$'\r': command not found`, usuarios con un carácter invisible al final). Evítalo desde el inicio:

1. Crea `.vscode/settings.json` con:

```json
{
  "files.eol": "\n"
}
```

   Eso hace que los archivos **nuevos** se creen con LF. Si ya creaste uno, cambia el modo abajo a la derecha de VS Code (donde dice `CRLF`) a `LF` y guarda.

2. Crea `.gitattributes` en la raíz con:

```
*.sh   text eol=lf
*.conf text eol=lf
acl    text eol=lf
```

**Versiones fijadas** (verificadas en Docker Hub el 2-nov-2026; todas existen para amd64 y arm64, así que valen igual en tu laptop y en Oracle):

| Programa | Imagen |
|---|---|
| Mosquitto | `eclipse-mosquitto:2.0.22` |
| MySQL | `mysql:8.4` |
| n8n | `n8nio/n8n:2.45.7` (la etiqueta `stable` de hoy) |
| nginx | `nginx:1.30.6-alpine` |

Las versiones se fijan para que dentro de un mes `docker compose up` no baje otra distinta sin avisarte.

**Árbol final de archivos** (a donde llegamos):

```
IncuMonitor/
  .env                      (secretos, NO se sube a git)
  .env.example              (solo nombres, sí se sube)
  .gitattributes
  .vscode/settings.json
  servidor/
    docker-compose.yml
    crear_usuarios_mqtt.sh
    mosquitto/  mosquitto.conf, acl, passwd (generado, no se sube)
    mysql/      02_usuarios.sh
    nginx/      default.conf
    web/        index.html
    n8n/workflows/   (flujos exportados en la lección 5 a 7)
```

---

## Lección 1: Docker y tu primer broker MQTT

Ya la tienes (mensaje anterior de la conversación). Resumen de lo que debe quedar:

- Docker Desktop abierto y `docker version` mostrando Client y Server.
- `servidor/mosquitto/mosquitto.conf` con `listener 1883` y `allow_anonymous true` (**temporal**).
- `servidor/docker-compose.yml` con el servicio `mosquitto`.
- `docker compose up -d`, y mensajes que pasan de `mosquitto_pub` a `mosquitto_sub`.

Para guardarla:

```bash
git add servidor/ .gitattributes .vscode/settings.json
git commit -m "Servidor: compose con Mosquitto abierto para pruebas"
```

> No subas este commit a GitHub todavía: el broker está abierto. Se sube después de la lección 2.

---

## Lección 2: usuarios y permisos en Mosquitto (y los secretos)

**Objetivo.** Que cada nodo entre con su usuario y contraseña y **solo pueda publicar en sus propios topics**. Así el `pir` no puede hacerse pasar por el `dht`.

### 2.1 Los secretos van en `.env`

El archivo `.env` guarda las contraseñas. Git lo ignora (está en `.gitignore`), así que nunca se sube. `.env.example` solo lista los **nombres** y sí se sube.

1. Abre `.env.example` y agrega al final los nombres nuevos:

```
MQTT_PASSWORD_N8N=
MQTT_PASSWORD_DASHBOARD=
MYSQL_ROOT_PASSWORD=
MYSQL_PASSWORD_ESCRITURA=
MYSQL_PASSWORD_LECTURA=
N8N_ENCRYPTION_KEY=
API_KEY=
```

2. Copia el archivo para crear el verdadero:

```bash
cp .env.example .env
```

3. Abre `.env` y pon **a mano** solo estas dos (el simulador las necesita; si las dejas vacías intenta conectarse a un host llamado "" y falla):

```
MQTT_HOST=localhost
MQTT_PORT=1883
```

4. Las contraseñas no las inventes tú: genéralas al azar. Este comando imprime una contraseña aleatoria de 24 caracteres usando solo letras, números, `-` y `_` (esos caracteres no dan problemas en comandos ni en SQL):

```bash
python -c "import secrets; print(secrets.token_urlsafe(18))"
```

Córrelo una vez por cada variable vacía y pega el resultado después del `=` en `.env`. Son 12 en total: 5 nodos, `n8n`, `dashboard`, 3 de MySQL, la llave de cifrado de n8n y la `API_KEY`. `WIFI_SSID` y `WIFI_PASSWORD` los dejas vacíos por ahora.

> Respalda `.env` fuera del repo (por ejemplo en un gestor de contraseñas). Si lo pierdes tienes que regenerar todo, y sobre todo `N8N_ENCRYPTION_KEY`: sin esa llave, n8n no puede leer sus credenciales guardadas.

### 2.2 Archivo `servidor/mosquitto/mosquitto.conf` (reemplaza el de la lección 1)

```
# --- Puerto MQTT para los nodos ---
listener 1883
# Ahora SI se exige usuario y contrasena
allow_anonymous false
# Archivo con los usuarios (contrasenas guardadas como hash, no en texto)
password_file /mosquitto/config/passwd
# Archivo con quien puede leer/escribir en que topic
acl_file /mosquitto/config/acl

# --- Guarda los mensajes retenidos (el "estado" de cada nodo) en disco ---
persistence true
persistence_location /mosquitto/data/

# --- Puerto WebSocket, para el dashboard en el navegador (lo usara nginx) ---
listener 9001
protocol websockets
```

### 2.3 Archivo `servidor/mosquitto/acl`

Sin extensión. Una ACL (lista de control de acceso) es una lista de reglas "este usuario puede leer o escribir en estos topics".

```
# Cada usuario tiene su bloque. "topic read X" = puede suscribirse a X.
# "topic write X" = puede publicar en X.

user n8n
topic read invernadero/#
topic write invernadero/cmd/alarma
topic write invernadero/alertas

user dashboard
topic read invernadero/#

user dht
topic read invernadero/cmd/alarma
topic write invernadero/cmd/silenciar

# Los "pattern" valen para TODOS los usuarios. %u se sustituye por el nombre
# con el que se conecto: si entras como "pir", solo puedes escribir en
# invernadero/telemetria/pir, invernadero/evento/pir e invernadero/estado/pir.
pattern write invernadero/telemetria/%u
pattern write invernadero/evento/%u
pattern write invernadero/estado/%u
```

Sintaxis: una regla por línea, `#` empieza un comentario. `#` dentro de un topic es el comodín "todo lo que cuelga de aquí". Las líneas `topic` aplican al último `user` que las precede.

### 2.4 Script que crea las contraseñas: `servidor/crear_usuarios_mqtt.sh`

Mosquitto no guarda contraseñas en texto: las guarda hasheadas en el archivo `passwd`, que se crea con el programa `mosquitto_passwd`. Este script lo corre por ti para los 7 usuarios.

```bash
#!/usr/bin/env bash
# Crea servidor/mosquitto/passwd con un usuario por nodo, mas n8n y dashboard.
# Las contrasenas salen de .env. Correr desde cualquier carpeta.

set -euo pipefail                 # se detiene ante cualquier error o variable vacia
cd "$(dirname "$0")/.."           # sube a la raiz del repo (donde esta .env)

# Carga .env como variables. tr -d '\r' quita los CR si el archivo quedo con CRLF.
set -a; source <(tr -d '\r' < .env); set +a

PASSWD=servidor/mosquitto/passwd
: > "$PASSWD"                     # vacia el archivo para crearlo desde cero

for u in dht luz pir puerta acel n8n dashboard; do
  var="MQTT_PASSWORD_${u^^}"      # ${u^^} = el nombre en MAYUSCULAS
  # MSYS_NO_PATHCONV=1: evita que Git Bash "traduzca" la ruta /mosquitto/... a una de Windows.
  # pwd -W da la ruta de Windows (C:/...), que Docker Desktop si entiende.
  MSYS_NO_PATHCONV=1 docker run --rm \
    -v "$(pwd -W)/servidor/mosquitto:/mosquitto/config" \
    eclipse-mosquitto:2.0.22 \
    mosquitto_passwd -b /mosquitto/config/passwd "$u" "${!var}"   # ${!var} = valor de la variable cuyo nombre esta en var
done
echo "usuarios creados en $PASSWD"
```

Cada vuelta del `for` arranca un contenedor desechable (`--rm` lo borra al terminar), le presta la carpeta `mosquitto/` y corre `mosquitto_passwd -b archivo usuario contraseña`.

### 2.5 Cambia el compose: `servidor/docker-compose.yml`

En el servicio `mosquitto` cambia el bloque `volumes` para prestar **toda la carpeta** (antes era solo el archivo `.conf`) y agrega un volumen con nombre para los datos:

```yaml
services:
  mosquitto:
    image: eclipse-mosquitto:2.0.22
    container_name: argos-mosquitto
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto:/mosquitto/config:ro      # conf, acl y passwd (solo lectura)
      - mosquitto_datos:/mosquitto/data       # mensajes retenidos; sobrevive a reinicios
    restart: unless-stopped

volumes:
  mosquitto_datos:                            # volumen con nombre: Docker lo administra
```

`volumes:` al final (sin sangría) **declara** los volúmenes con nombre; el `volumes:` de dentro del servicio los **usa**.

### 2.6 Agrega a `.gitignore` (raíz del repo)

```
servidor/mosquitto/passwd
```

El `passwd` tiene hashes de las contraseñas: no se sube.

### 2.7 Levantar y probar

```bash
bash servidor/crear_usuarios_mqtt.sh
cd servidor
docker compose up -d --force-recreate mosquitto
docker compose logs mosquitto
```

`--force-recreate` obliga a recrear el contenedor para que lea la configuración nueva. En los logs no debe haber `Error`. Una advertencia de "world readable permissions" es normal en 2.0.x.

Carga las variables de `.env` en tu terminal (hazlo en cada terminal nueva; vuelve a `cd ..` a la raíz primero):

```bash
cd ..
set -a; source <(tr -d '\r' < .env); set +a
```

**Pruebas** (necesitas dos terminales, A y B, cada una con las variables cargadas):

**A, escucha como n8n:**
```bash
docker exec argos-mosquitto mosquitto_sub -u n8n -P "$MQTT_PASSWORD_N8N" -t "invernadero/#" -v
```

**B, tres pruebas:**
```bash
# 1. Sin credenciales: debe decir "Connection Refused: not authorised"
docker exec argos-mosquitto mosquitto_pub -t invernadero/telemetria/dht -m prueba

# 2. El dht publica en lo suyo: debe LLEGAR a la terminal A
docker exec argos-mosquitto mosquitto_pub -u dht -P "$MQTT_PASSWORD_DHT" -t invernadero/telemetria/dht -m '{"lecturas":[]}'

# 3. El pir intenta hacerse pasar por el dht: NO debe llegar a la terminal A
docker exec argos-mosquitto mosquitto_pub -u pir -P "$MQTT_PASSWORD_PIR" -t invernadero/telemetria/dht -m intruso
```

En la prueba 3 `mosquitto_pub` **no marca error**: MQTT 3.1.1 descarta en silencio lo que no tiene permiso. La prueba válida es que la terminal A **no muestre** "intruso".

### Si falla

| Síntoma | Causa y arreglo |
|---|---|
| `Error: Unable to open pwfile` o `Permission denied` en los logs | El archivo `passwd` quedó con permisos que el usuario `mosquitto` del contenedor no puede leer. Prueba agregar al servicio `user: "0:0"` (corre como root) [verificar]; es un arreglo de laboratorio, no de producción. |
| La prueba 2 tampoco llega | Revisa que `acl` no tenga CRLF (modo LF en VS Code) y que el nombre del usuario en el `acl` sea idéntico al de `passwd`. |
| `Connection refused` en la prueba 1 | Es lo esperado. Si en cambio conecta, `allow_anonymous` sigue en `true`: no se recreó el contenedor. |
| `port is already allocated` | Otro programa usa el 1883. `netstat -ano \| findstr :1883` lo muestra. |

### Guardar y subir a GitHub

Ahora el broker ya no está abierto. Confirma que ningún secreto está versionado (el comando no debe imprimir nada):

```bash
git ls-files | grep -E "(^|/)\.env$|secrets\.h|passwd$"
```

```bash
git add .
git commit -m "Servidor: Mosquitto con usuarios por nodo y ACL; plantilla de secretos"
```

Para subirlo, crea en github.com un repositorio **privado y vacío** (sin README) y luego:

```bash
git remote add origin https://github.com/TU_USUARIO/NOMBRE_DEL_REPO.git
git push -u origin HEAD
```

La primera vez, una ventana del navegador te pide iniciar sesión. A partir de aquí, al terminar cada lección: `git add .`, `git commit -m "..."` y `git push`.

---

## Lección 3: MySQL con el esquema de Argos

**Objetivo.** Un MySQL con las 14 tablas de `docs/bd/esquema.sql` y dos usuarios con permisos distintos: uno que escribe (la ingesta) y uno que solo lee (la API). Principio de mínimo privilegio: si alguien rompe la API, no puede borrar datos.

**Importante.** `esquema.sql` **nunca se ha ejecutado** en un servidor. Si falla, el error te dice la línea; corrígelo ahí y avisa para ajustar el documento.

### 3.1 `servidor/mysql/02_usuarios.sh`

La imagen de MySQL ejecuta, **una sola vez** (cuando el volumen está vacío), todo lo que haya en `/docker-entrypoint-initdb.d/` en orden alfabético. Por eso los números: `01_esquema.sql` crea las tablas y `02_usuarios.sh` crea los usuarios.

```bash
#!/bin/bash
# Corre UNA vez, al crear la base por primera vez. Las variables vienen del compose.
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<EOSQL
CREATE USER 'argos_escritura'@'%' IDENTIFIED BY '${MYSQL_PASSWORD_ESCRITURA}';
GRANT SELECT, INSERT, UPDATE ON argos.* TO 'argos_escritura'@'%';

CREATE USER 'argos_lectura'@'%' IDENTIFIED BY '${MYSQL_PASSWORD_LECTURA}';
GRANT SELECT ON argos.Medicion   TO 'argos_lectura'@'%';
GRANT SELECT ON argos.Sensor     TO 'argos_lectura'@'%';
GRANT SELECT ON argos.Parametro  TO 'argos_lectura'@'%';
GRANT SELECT ON argos.Alerta     TO 'argos_lectura'@'%';
GRANT SELECT ON argos.EstadoNodo TO 'argos_lectura'@'%';
EOSQL
```

Sintaxis: `<<EOSQL ... EOSQL` es un *heredoc*: todo el texto entre las dos marcas se le entrega al comando `mysql` como si lo tecleara. Como `EOSQL` no lleva comillas, el shell sustituye `${MYSQL_PASSWORD_ESCRITURA}` por su valor antes de enviarlo. `'%'` significa "desde cualquier host" (dentro de la red de Docker eso es solo n8n).

### 3.2 Agrega el servicio `mysql` al compose

Dentro de `services:`, al mismo nivel que `mosquitto`:

```yaml
  mysql:
    image: mysql:8.4
    container_name: argos-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_PASSWORD_ESCRITURA: ${MYSQL_PASSWORD_ESCRITURA}
      MYSQL_PASSWORD_LECTURA: ${MYSQL_PASSWORD_LECTURA}
    # Opciones de MySQL: hora UTC, scheduler de eventos (la purga de 90 dias) y emojis/acentos
    command:
      - --default-time-zone=+00:00
      - --event-scheduler=ON
      - --character-set-server=utf8mb4
    ports:
      - "127.0.0.1:3306:3306"       # solo tu PC; 127.0.0.1 evita exponerlo a la red
    volumes:
      - mysql_datos:/var/lib/mysql
      - ../docs/bd/esquema.sql:/docker-entrypoint-initdb.d/01_esquema.sql:ro
      - ./mysql/02_usuarios.sh:/docker-entrypoint-initdb.d/02_usuarios.sh:ro
    healthcheck:                    # n8n esperara a que MySQL este listo
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -uroot -p$$MYSQL_ROOT_PASSWORD --silent"]
      interval: 10s
      timeout: 5s
      retries: 12
    restart: unless-stopped
```

Y al final, en el bloque `volumes:` de abajo, agrega `mysql_datos:`.

Detalles de sintaxis:
- `${NOMBRE}` lo sustituye **Compose** con lo que haya en `.env`. Por eso ahora el comando lleva `--env-file ../.env` (abajo).
- `$$` (doble) en el healthcheck evita que Compose sustituya esa variable y la deja para que la lea el contenedor.
- `../docs/bd/esquema.sql` es una ruta relativa al compose: sube a `IncuMonitor/` y baja a `docs/bd/`. Así hay **una sola** copia del esquema.

### 3.3 Atajo para no escribir `--env-file` siempre

Compose lee `.env` solo si está junto al `docker-compose.yml`. Como el tuyo está en la raíz, define este alias en cada terminal nueva (desde `servidor/`):

```bash
alias dc='docker compose --env-file ../.env'
```

A partir de aquí `dc up -d` equivale al comando largo.

### 3.4 Levantar y comprobar

```bash
cd servidor
dc up -d
dc ps
dc logs mysql
```

La primera vez tarda (descarga unos 800 MB y ejecuta el esquema). Espera a que `dc ps` muestre `healthy`. En los logs busca `ready for connections` y que no haya `ERROR`.

Comprueba tablas y datos fijos:

```bash
cd ..
set -a; source <(tr -d '\r' < .env); set +a
docker exec argos-mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" argos -e "SHOW TABLES; SELECT id_nodo, id_caja FROM Nodo; SELECT * FROM Umbral;"
```

Debes ver **14 tablas**, los 5 nodos con sus cajas y los 2 umbrales (temperatura 22 a 28 y humedad 40 a 60). Comprueba los permisos:

```bash
docker exec argos-mysql mysql -uargos_lectura -p"$MYSQL_PASSWORD_LECTURA" argos -e "SELECT COUNT(*) FROM Medicion; DELETE FROM Medicion;"
```

El `SELECT` funciona y el `DELETE` debe fallar con `command denied`.

### Si falla

| Síntoma | Arreglo |
|---|---|
| El contenedor reinicia y `dc logs mysql` muestra un error SQL | Es un problema de `esquema.sql`. Corrige el archivo, y como los scripts de init **solo corren con volumen vacío**, bórralo: `dc down -v` y `dc up -d`. **`-v` borra los datos**: úsalo solo en esta etapa. |
| `02_usuarios.sh`: `command not found` con `\r` | El archivo quedó con CRLF. Pásalo a LF y repite `dc down -v`. |
| `Access denied` con el usuario de lectura | Las variables no llegaron: ¿usaste `dc` o `docker compose` a secas? |
| Hay que cambiar una contraseña ya creada | Los scripts de init no se repiten. `ALTER USER 'argos_lectura'@'%' IDENTIFIED BY '...'` o borrar el volumen. |

```bash
git add . && git commit -m "Servidor: MySQL 8.4 con esquema y usuarios de lectura y escritura" && git push
```

---

## Lección 4: probar con el simulador (sin hardware)

El simulador publica por MQTT exactamente lo que publicarían los 5 NodeMCU, así que sirve para construir y probar todo lo demás antes de que lleguen las piezas.

### 4.1 Arregla un error del simulador

Hoy imprime "conectado" aunque el broker **rechace** las credenciales (hallazgo del 21-oct). Abre `simulador/simulador_nodos.py`, busca la función `al_conectar` y agrega las 3 primeras líneas del cuerpo:

```python
    def al_conectar(self, c, _u, _f, rc, _p=None):
        if rc.is_failure:                          # el broker dijo que no
            print(f"[{self.id}] el broker RECHAZO la conexion: {rc}")
            return
        estado = {...}   # el resto de la funcion queda igual
```

`rc` es el código de resultado; `rc.is_failure` es verdadero si la conexión falló. `return` sale antes de imprimir un falso "conectado".

### 4.2 Correrlo

Con el broker arriba (lección 2) y el `.env` lleno:

```bash
uv run --no-project --python 3.12 --with paho-mqtt python simulador/simulador_nodos.py --rapido
```

- `uv run --no-project ... --with paho-mqtt` ejecuta el script con la librería MQTT sin instalarla en tu sistema.
- `--rapido` divide los periodos entre 10 (el `dht` publica cada 3 s en vez de cada 30).

Debe imprimir `[dht] conectado (rc=Success)` para los 5 nodos. Mientras corre, en otra terminal (con las variables cargadas):

```bash
docker exec argos-mosquitto mosquitto_sub -u n8n -P "$MQTT_PASSWORD_N8N" -t "invernadero/#" -v
```

Verás telemetría del `dht`, latidos y eventos. Prueba que una contraseña mala se rechaza: cambia temporalmente una `MQTT_PASSWORD_PIR` y confirma el mensaje "RECHAZO". Ctrl+C para detenerlo; manda `offline` retenido para cada nodo.

Escenarios para después: `--escenario calor` (la temperatura sube hasta pasar 28 °C), `sin_red` (el nodo `luz` se cae a los 3 min), `golpes` (golpes y puertas abiertas seguido).

```bash
git add . && git commit -m "Simulador: avisa cuando el broker rechaza las credenciales" && git push
```

---

## Lección 5: n8n y el flujo de ingesta (MQTT → MySQL)

**Qué es n8n.** Una herramienta visual donde dibujas flujos: cajas ("nodos") conectadas con flechas. Cada caja hace algo (escuchar MQTT, ejecutar SQL, publicar). Aquí "nodo" de n8n no es lo mismo que "nodo" NodeMCU: para no confundirte, en este tutorial las cajas de n8n se llaman **pasos**.

### 5.1 Agregar n8n y nginx al compose

Dentro de `services:`:

```yaml
  n8n:
    image: n8nio/n8n:2.45.7
    container_name: argos-n8n
    depends_on:
      mysql:
        condition: service_healthy
      mosquitto:
        condition: service_started
    environment:
      N8N_ENCRYPTION_KEY: ${N8N_ENCRYPTION_KEY}   # cifra las credenciales guardadas
      GENERIC_TIMEZONE: America/Monterrey         # solo para los horarios de los cron; la BD sigue en UTC
      TZ: America/Monterrey
    ports:
      - "127.0.0.1:5678:5678"                     # el editor solo se abre desde tu PC
    volumes:
      - n8n_datos:/home/node/.n8n
    restart: unless-stopped

  nginx:
    image: nginx:1.30.6-alpine
    container_name: argos-nginx
    depends_on:
      - n8n
      - mosquitto
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - ./web:/usr/share/nginx/html:ro
    restart: unless-stopped
```

Y en `volumes:` del final agrega `n8n_datos:`.

Crea `servidor/web/index.html` (de momento un placeholder; el dashboard llega en la siguiente etapa):

```html
<!doctype html>
<html lang="es"><meta charset="utf-8"><title>Argos</title>
<h1>Argos funcionando</h1>
```

Crea `servidor/nginx/default.conf`:

```nginx
server {
  listen 80;
  server_name _;

  # Paginas estaticas (el dashboard)
  root /usr/share/nginx/html;
  index index.html;

  # /api/estado  ->  http://n8n:5678/webhook/api/estado
  # (nginx reemplaza el prefijo /api/ por /webhook/api/)
  location /api/ {
    proxy_pass http://n8n:5678/webhook/api/;
  }

  # WebSocket de MQTT para el dashboard
  location /mqtt {
    proxy_pass http://mosquitto:9001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

`n8n` y `mosquitto` son los nombres de los servicios del compose: dentro de la red de Docker se encuentran por nombre. Si el puerto 80 está ocupado en tu PC, cambia a `"8080:80"` y usa `localhost:8080`.

```bash
cd servidor && dc up -d && dc ps
```

### 5.2 Primer ingreso a n8n

1. Abre `http://localhost:5678`.
2. Crea la cuenta de dueño (correo y contraseña **tuyos**, solo para este n8n local).
3. Menú **Credentials** → **Create credential**. Crea dos (abre `.env` en VS Code para copiar los valores):

| Credencial | Campos |
|---|---|
| **MQTT** `mqtt-argos` | Protocol `mqtt`, Host `mosquitto`, Port `1883`, User `n8n`, Password = `MQTT_PASSWORD_N8N` |
| **MySQL** `mysql-escritura` | Host `mysql`, Port `3306`, Database `argos`, User `argos_escritura`, Password = `MYSQL_PASSWORD_ESCRITURA` |

El host es `mosquitto` y `mysql`, **no** `localhost`: n8n corre dentro de un contenedor y `localhost` sería él mismo. Cada credencial tiene botón para probar conexión: debe decir que sirve.

### 5.3 Dibujar el flujo `ingesta`

**Workflows → Create workflow**, nómbralo `ingesta`. Pasos, de izquierda a derecha:

**Paso 1: `MQTT Trigger`**
- Credential `mqtt-argos`. Topics: `invernadero/#`.
- Haz clic en **Listen for test event** y corre el simulador: el paso debe mostrar mensajes con `topic` y `message` (texto). [verificar los nombres de los campos]

**Paso 2: `Code` (renómbralo `Parsear`)**
- Language JavaScript, modo *Run Once for All Items*. Convierte cada mensaje en una o varias filas ya listas para la BD:

```javascript
// Entrada: { topic: "invernadero/telemetria/dht", message: "{...json...}" }
const salida = [];

for (const item of $input.all()) {
  const [, clase, nodo] = item.json.topic.split('/');   // ["invernadero", "telemetria", "dht"]

  let cuerpo;
  try { cuerpo = JSON.parse(item.json.message); }
  catch (e) { continue; }          // ignora lo que no sea JSON (por ejemplo cmd/alarma = "on")

  if (clase === 'telemetria') {
    for (const l of cuerpo.lecturas || []) {
      if (l.parametro === 'latido') {
        salida.push({ json: { tipo_msg: 'latido', nodo } });
      } else {
        salida.push({ json: { tipo_msg: 'medicion', nodo,
                              parametro: l.parametro, valor: l.valor } });
      }
    }
  } else if (clase === 'evento') {
    // Orden del LED rojo segun la regla del firmware: [comando, duracion en s]
    const led = { movimiento: ['on', 5], golpe: ['on', 5],
                  puerta_abierta: ['on', null], puerta_cerrada: ['off', null] }[cuerpo.tipo] || null;
    salida.push({ json: { tipo_msg: 'evento', nodo, evento: cuerpo.tipo,
                          magnitud: cuerpo.magnitud ?? null,
                          led_cmd: led ? led[0] : null, led_dur: led ? led[1] : null } });
  } else if (clase === 'estado') {
    salida.push({ json: { tipo_msg: 'estado', nodo, estado: cuerpo.estado,
                          reset_reason: cuerpo.reset_reason ?? null,
                          uptime_s: cuerpo.uptime_s ?? null, rssi: cuerpo.rssi ?? null } });
  } else if (clase === 'cmd' && nodo === 'silenciar') {
    salida.push({ json: { tipo_msg: 'silencio', minutos: cuerpo.minutos } });
  }
}
return salida;
```

Sintaxis rápida: `const` declara una variable; `for (const x of lista)` recorre una lista; `[, clase, nodo] = ...` descompone un arreglo ignorando el primer elemento; `??` usa el valor de la derecha si el de la izquierda es `null` o falta; `salida.push({ json: {...} })` agrega un resultado (n8n exige el envoltorio `json`). `try/catch` captura el error si el texto no es JSON válido.

**Paso 3: `Switch` (renómbralo `Reparto`)**
- Mode *Rules*. Cinco reglas sobre el valor `{{ $json.tipo_msg }}`, operador *is equal to*: `medicion`, `latido`, `evento`, `estado`, `silencio`. Cada regla crea una salida; conecta la salida de cada una a su paso de SQL.

**Pasos 4 a 9: `MySQL` (todos con credencial `mysql-escritura`, operación *Execute SQL*)**

En cada uno, el texto de la consulta lleva `?` donde va un valor, y los valores se dan en **Options → Query Parameters** con una expresión que devuelve una lista `[...]` en el **mismo orden** que los `?`. Así los valores nunca se pegan al texto de la consulta (evita inyección SQL). [verificar el nombre exacto de la opción en tu versión]

*4. `Guardar medición`* (salida `medicion`):
```sql
INSERT INTO Medicion (id_sensor, id_parametro, valor, fecha_hora)
SELECT s.id_sensor, p.id_parametro, ?, UTC_TIMESTAMP()
FROM Sensor s, Parametro p
WHERE s.id_nodo = ? AND p.nombre = ?;
```
Parámetros: `{{ [$json.valor, $json.nodo, $json.parametro] }}`

*5. `Guardar latido`* (salida `latido`):
```sql
UPDATE EstadoNodo SET estado = 'online', ultimo_reporte = UTC_TIMESTAMP() WHERE id_nodo = ?;
```
Parámetros: `{{ [$json.nodo] }}`

*6a. `Guardar evento`* (salida `evento`):
```sql
INSERT INTO Evento (id_sensor, tipo, magnitud, fecha_hora)
SELECT id_sensor, ?, ?, UTC_TIMESTAMP() FROM Sensor WHERE id_nodo = ?;
```
Parámetros: `{{ [$json.evento, $json.magnitud, $json.nodo] }}`

*6b. `Registrar LED`* (**también** conectado a la salida `evento`, en paralelo con el 6a; una salida puede alimentar varios pasos y cada uno recibe el mismo dato):
```sql
INSERT INTO AccionControl (id_actuador, origen, comando, duracion_s)
SELECT id_actuador, 'local', ?, ? FROM Actuador WHERE id_nodo = ? AND tipo = 'led_rojo' AND ? IS NOT NULL;
```
Parámetros: `{{ [$json.led_cmd, $json.led_dur, $json.nodo, $json.led_cmd] }}`. La última condición evita registrar eventos que no mueven el LED (como `sensor_error`).

*7. `Guardar estado`* (salida `estado`, incluye el LWT `offline`):
```sql
UPDATE EstadoNodo
SET estado = ?,
    ultimo_reporte = IF(? = 'online', UTC_TIMESTAMP(), ultimo_reporte),
    reset_reason = COALESCE(?, reset_reason),
    uptime_s = COALESCE(?, uptime_s),
    rssi = COALESCE(?, rssi)
WHERE id_nodo = ?;
```
Parámetros: `{{ [$json.estado, $json.estado, $json.reset_reason, $json.uptime_s, $json.rssi, $json.nodo] }}`. `COALESCE(a, b)` devuelve `a`, o `b` si `a` es nulo: un `offline` sin datos no borra lo que ya sabíamos.

*8. `Guardar silencio`* (salida `silencio`; el botón del `dht` publica `cmd/silenciar`):
```sql
INSERT INTO AccionControl (id_actuador, origen, comando, duracion_s)
SELECT id_actuador, 'manual', 'off', ? * 60 FROM Actuador WHERE id_nodo = 'dht' AND tipo = 'buzzer';
```
Parámetros: `{{ [$json.minutos] }}`

**Activar.** Arriba a la derecha, el interruptor **Active** (para que escuche siempre, no solo en pruebas). Guarda con Ctrl+S.

### 5.4 Probar

Con el simulador corriendo (`--rapido`):

```bash
docker exec argos-mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" argos -e "SELECT COUNT(*) AS mediciones FROM Medicion; SELECT * FROM EstadoNodo; SELECT * FROM Evento ORDER BY id_evento DESC LIMIT 5;"
```

`Medicion` debe crecer cada pocos segundos, los 5 nodos aparecer `online` y haber eventos. La pestaña **Executions** de n8n muestra cada ejecución y, si una falla, en qué paso y por qué.

### 5.5 Exportar el flujo para guardarlo en git

n8n guarda los flujos en su volumen, no en tus archivos. Para versionarlos:

```bash
mkdir -p servidor/n8n/workflows
docker exec argos-n8n n8n export:workflow --all --output=/tmp/workflows.json
docker cp argos-n8n:/tmp/workflows.json servidor/n8n/workflows/flujos.json
```

[verificar el comando de exportación en la versión 2.x; alternativa: menú ⋯ del flujo → *Download*]. El JSON referencia las credenciales por nombre, no incluye contraseñas. Para restaurar en otro n8n (por ejemplo Oracle): `docker cp` del archivo y `n8n import:workflow --input=...`.

```bash
git add . && git commit -m "Servidor: n8n y nginx; flujo de ingesta MQTT a MySQL" && git push
```

### Si falla

| Síntoma | Arreglo |
|---|---|
| `MQTT Trigger` no recibe nada | Credencial con host `localhost` en vez de `mosquitto`, o contraseña errónea (`dc logs mosquitto` muestra "not authorised"). |
| `Parsear` entrega 0 ítems | El paso anterior entrega campos con otros nombres: mira la pestaña *Output* del trigger y ajusta `item.json.topic` y `item.json.message`. |
| MySQL: `Unknown column` o `Incorrect datetime` | Revisa que la consulta use `UTC_TIMESTAMP()` y no fechas de JavaScript. |
| `Medicion` no crece pero no hay error | La consulta insertó 0 filas: el `nodo` o `parametro` no existe en `Sensor`/`Parametro`. Comprueba los datos fijos de la lección 3. |
| Un nodo (n8n) deja de ejecutar tras reiniciar | El flujo no está **Active**. |

---

## Lección 6: alertas (temperatura y humedad, buzzer y el resto)

### 6.1 Flujo `alertas_dht` (cada minuto)

Replica las reglas del firmware (`firmware/include/alarma_dht.h`): **persistencia de 3 lecturas** e **histéresis** de 0.5 °C y 2 % HR. El flujo no guarda estado propio: cada minuto mira la BD y decide.

- **Abre** una alerta si las últimas 3 lecturas están fuera de rango y no hay una abierta.
- **Cierra** la alerta si las últimas 3 están dentro del rango **recortado por la histéresis** (por ejemplo, entre 22.5 y 27.5 °C).

**Paso 1: `Schedule Trigger`**. Cada **1 minute**.

**Paso 2: `MySQL` `Leer estado`** (credencial `mysql-escritura`; en *Settings* activa **Always Output Data**):

```sql
SELECT t.parametro, u.id_umbral, u.minimo, u.maximo, u.histeresis,
       JSON_ARRAYAGG(t.valor) AS ultimos,
       MAX(CASE WHEN t.rn = 1 THEN t.valor END) AS ultimo,
       MAX(a.id_alerta) AS id_alerta_activa
FROM (
  SELECT m.id_sensor, m.id_parametro, p.nombre AS parametro, m.valor,
         ROW_NUMBER() OVER (PARTITION BY m.id_parametro
                            ORDER BY m.fecha_hora DESC, m.id_medicion DESC) AS rn
  FROM Medicion m
  JOIN Sensor s    ON s.id_sensor = m.id_sensor AND s.id_nodo = 'dht'
  JOIN Parametro p ON p.id_parametro = m.id_parametro
  WHERE p.nombre IN ('temperatura', 'humedad')
    AND m.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 10 MINUTE
) t
JOIN Umbral u ON u.id_sensor = t.id_sensor AND u.id_parametro = t.id_parametro
LEFT JOIN Alerta a ON a.id_nodo = 'dht' AND a.tipo = t.parametro AND a.ts_fin IS NULL
WHERE t.rn <= 3
GROUP BY t.parametro, u.id_umbral, u.minimo, u.maximo, u.histeresis;
```

Cómo leerla: la subconsulta `t` numera las lecturas de cada parámetro de la más nueva a la más vieja (`ROW_NUMBER`) y solo conserva las de los últimos 10 min; el `WHERE t.rn <= 3` se queda con 3; se une con los umbrales y con la alerta abierta, si existe. El resultado es una fila por parámetro.

**Paso 3: `Code` `Decidir`** (*Run Once for All Items*):

```javascript
const filas = $input.all().map(i => i.json);
const salida = [];
let sigueActiva = false, huboCierre = false;

for (const f of filas) {
  if (f.id_umbral === undefined) continue;         // "Always Output Data" puede dejar una fila vacia
  const v = (typeof f.ultimos === 'string' ? JSON.parse(f.ultimos) : f.ultimos).map(Number);
  const min = Number(f.minimo), max = Number(f.maximo), h = Number(f.histeresis);

  const fuera  = v.length >= 3 && v.every(x => x < min || x > max);
  const dentro = v.length >= 3 && v.every(x => x >= min + h && x <= max - h);
  const activa = !!f.id_alerta_activa;

  let accion = 'nada';
  if (!activa && fuera)       { accion = 'abrir';  sigueActiva = true; }
  else if (activa && dentro)  { accion = 'cerrar'; huboCierre = true; }
  else if (activa)            { sigueActiva = true; }

  salida.push({ json: { accion, parametro: f.parametro, id_umbral: f.id_umbral,
                        id_alerta: f.id_alerta_activa, valor: Number(f.ultimo),
                        nodo: 'dht', estado: accion === 'cerrar' ? 'cerrada' : 'abierta' } });
}

// Orden unica para el buzzer: "on" mientras quede alguna alerta, "off" cuando se cierre la ultima.
const mensaje = sigueActiva ? 'on' : (huboCierre ? 'off' : null);
salida.push({ json: { accion: 'buzzer', mensaje } });
return salida;
```

`array.every(f)` es verdadero si **todos** los elementos cumplen `f`. `x => x < min` es una función corta: "dado x, devuelve si x es menor que min".

**Paso 4: `Switch`** sobre `{{ $json.accion }}` con tres reglas: `abrir`, `cerrar`, `buzzer` (lo demás se descarta).

**Rama `abrir`** (tres pasos en cadena, credencial `mysql-escritura`):

*`Abrir alerta`* (MySQL):
```sql
INSERT INTO Alerta (id_nodo, id_umbral, tipo, valor) VALUES ('dht', ?, ?, ?);
```
Parámetros: `{{ [$json.id_umbral, $json.parametro, $json.valor] }}`. La restricción `uq_alerta_activa` del esquema impide dos alertas abiertas del mismo tipo: si por error se intentara, MySQL rechaza la fila.

*`Registrar buzzer`* (MySQL):
```sql
INSERT INTO AccionControl (id_actuador, id_alerta, origen, comando)
SELECT ac.id_actuador, a.id_alerta, 'alerta', 'on'
FROM Actuador ac JOIN Alerta a ON a.id_nodo = 'dht' AND a.tipo = ? AND a.ts_fin IS NULL
WHERE ac.id_nodo = 'dht' AND ac.tipo = 'buzzer';
```
Parámetros: `{{ [$('Switch').item.json.parametro] }}`. [verificar: `$('Switch').item` recupera el dato del paso anterior aunque MySQL lo haya reemplazado; si falla, usa `$('Decidir').item.json.parametro`.]

*`Publicar alerta`* (paso **MQTT**, credencial `mqtt-argos`): Topic `invernadero/alertas`; apaga *Send Input Data*; Message:
```
{{ JSON.stringify({ id_nodo: 'dht', tipo: $('Switch').item.json.parametro, valor: $('Switch').item.json.valor, estado: 'abierta' }) }}
```
> `[POR CONFIRMAR]` el formato exacto del payload de `invernadero/alertas` (el contexto completo del proyecto lo define; este es un borrador razonable).

**Rama `cerrar`** (dos pasos MySQL):
```sql
UPDATE Alerta SET ts_fin = UTC_TIMESTAMP() WHERE id_alerta = ?;
```
Parámetros: `{{ [$json.id_alerta] }}`; y publica el mismo mensaje MQTT con `estado: 'cerrada'`.

**Rama `buzzer`**:
- Paso `IF`: condición `{{ $json.mensaje }}` *is not empty*.
- Verdadero → paso **MQTT**: Topic `invernadero/cmd/alarma`, *Send Input Data* apagado, Message `{{ $json.mensaje }}` (texto plano `on` u `off`, **no** JSON).

Esa rama corre cada minuto mientras haya alerta: es el "repetido cada 60 s" del contrato. El firmware da por vigente una orden `on` durante 150 s, así que si n8n se cae el buzzer deja de sonar solo (la alarma local sigue por su cuenta).

Activa el flujo y guarda.

### 6.2 Flujo `alertas_otros` (cada minuto)

Un `Schedule Trigger` (1 min) seguido de **seis pasos MySQL en cadena** (cada uno ignora lo que recibe). Los tres tipos de alerta:

**`nodo_sin_reporte`**: abre si un nodo con reporte previo lleva más de 150 s callado o publicó `offline`:
```sql
INSERT IGNORE INTO Alerta (id_nodo, tipo, valor)
SELECT id_nodo, 'nodo_sin_reporte', NULL FROM EstadoNodo
WHERE ultimo_reporte IS NOT NULL
  AND (estado = 'offline' OR ultimo_reporte < UTC_TIMESTAMP() - INTERVAL 150 SECOND);
```
Se cierra:
```sql
UPDATE Alerta a JOIN EstadoNodo e ON e.id_nodo = a.id_nodo
SET a.ts_fin = UTC_TIMESTAMP()
WHERE a.tipo = 'nodo_sin_reporte' AND a.ts_fin IS NULL
  AND e.estado = 'online' AND e.ultimo_reporte >= UTC_TIMESTAMP() - INTERVAL 150 SECOND;
```
`INSERT IGNORE` evita el error cuando la restricción de alerta única rechaza un duplicado. El `ultimo_reporte IS NOT NULL` evita alertar por nodos que aún no se han conectado jamás.

**`puerta_abierta`**: abre si el último evento de la puerta es una apertura de más de `puerta_abierta_max_s` segundos (tabla `Configuracion`, 120 por omisión):
```sql
INSERT IGNORE INTO Alerta (id_nodo, tipo, valor)
SELECT 'puerta', 'puerta_abierta', TIMESTAMPDIFF(SECOND, u.fecha_hora, UTC_TIMESTAMP())
FROM (
  SELECT ev.tipo, ev.fecha_hora
  FROM Evento ev JOIN Sensor s ON s.id_sensor = ev.id_sensor
  WHERE s.id_nodo = 'puerta' AND ev.tipo IN ('puerta_abierta', 'puerta_cerrada')
  ORDER BY ev.fecha_hora DESC, ev.id_evento DESC LIMIT 1
) u
WHERE u.tipo = 'puerta_abierta'
  AND TIMESTAMPDIFF(SECOND, u.fecha_hora, UTC_TIMESTAMP())
      > (SELECT CAST(valor AS UNSIGNED) FROM Configuracion WHERE clave = 'puerta_abierta_max_s');
```
Se cierra cuando el último evento es `puerta_cerrada`:
```sql
UPDATE Alerta SET ts_fin = UTC_TIMESTAMP()
WHERE id_nodo = 'puerta' AND tipo = 'puerta_abierta' AND ts_fin IS NULL
  AND (SELECT tipo FROM (
         SELECT ev.tipo FROM Evento ev JOIN Sensor s ON s.id_sensor = ev.id_sensor
         WHERE s.id_nodo = 'puerta' AND ev.tipo IN ('puerta_abierta', 'puerta_cerrada')
         ORDER BY ev.fecha_hora DESC, ev.id_evento DESC LIMIT 1) x) = 'puerta_cerrada';
```

**`golpe`**: abre si en el último minuto hubo un golpe mayor al umbral (`umbral_golpe_g`, 0.5 g); cierra tras 5 min sin golpes:
```sql
INSERT IGNORE INTO Alerta (id_nodo, tipo, valor)
SELECT 'acel', 'golpe', MAX(ev.magnitud)
FROM Evento ev JOIN Sensor s ON s.id_sensor = ev.id_sensor
WHERE s.id_nodo = 'acel' AND ev.tipo = 'golpe'
  AND ev.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 1 MINUTE
  AND ev.magnitud >= (SELECT CAST(valor AS DECIMAL(6,2)) FROM Configuracion WHERE clave = 'umbral_golpe_g')
HAVING COUNT(*) > 0;
```
```sql
UPDATE Alerta SET ts_fin = UTC_TIMESTAMP()
WHERE id_nodo = 'acel' AND tipo = 'golpe' AND ts_fin IS NULL
  AND ts_inicio < UTC_TIMESTAMP() - INTERVAL 5 MINUTE
  AND NOT EXISTS (SELECT 1 FROM Evento ev JOIN Sensor s ON s.id_sensor = ev.id_sensor
                  WHERE s.id_nodo = 'acel' AND ev.tipo = 'golpe'
                    AND ev.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 5 MINUTE);
```

**Desactivadas a propósito:** movimiento fuera de horario y luz contra fotoperiodo, porque sus horarios están `[POR CONFIRMAR]` en `Configuracion`. Cuando los encargados los den, se llenan y se agregan igual que estas. **Estas alertas no tocan el buzzer**: solo suena por temperatura y humedad.

### 6.3 Probar

```bash
uv run --no-project --python 3.12 --with paho-mqtt python simulador/simulador_nodos.py --rapido --escenario calor
```

Con `--rapido` la temperatura pasa de 28 °C en ~1 min. En 2 a 4 minutos:

```bash
docker exec argos-mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" argos -e "SELECT * FROM Alerta; SELECT * FROM AccionControl ORDER BY id_accion DESC LIMIT 5;"
```

- Debe haber una alerta `temperatura` con `ts_fin` en `NULL` (abierta) y la acción `on` del buzzer con `origen = alerta`.
- La terminal con `mosquitto_sub -t "invernadero/cmd/alarma"` debe mostrar `on` **repetido cada minuto**.
- Detén el simulador, espera 10 min sin datos y arráncalo en `normal`: tres lecturas dentro del rango recortado cierran la alerta y llega `off`.
- `--escenario sin_red`: tras ~3 min el LWT pone a `luz` en `offline` y aparece `nodo_sin_reporte`.
- `--escenario golpes`: aparecen alertas de `golpe` y `puerta_abierta`.

Exporta los flujos otra vez (5.5) y:

```bash
git add . && git commit -m "Servidor: flujos de alertas de temperatura, humedad, puerta, golpe y nodo sin reporte" && git push
```

---

## Lección 7: la Web API (webhooks de n8n)

Sigue `docs/api.md`. Cada endpoint es un flujo de tres pasos: `Webhook` → `MySQL` (solo lectura) → `Respond to Webhook`.

### 7.1 Credenciales nuevas en n8n

| Credencial | Campos |
|---|---|
| **MySQL** `mysql-lectura` | Igual que la de escritura pero User `argos_lectura`, Password = `MYSQL_PASSWORD_LECTURA` |
| **Header Auth** `api-key` | Name `X-API-Key`, Value = `API_KEY` de `.env` |

### 7.2 `GET /api/estado`

1. **`Webhook`**: HTTP Method `GET`, Path `api/estado`, Authentication `Header Auth` con `api-key`, Respond `Using 'Respond to Webhook' Node`.
2. **`MySQL`** `Nodos` (credencial `mysql-lectura`, *Always Output Data*):
```sql
SELECT id_nodo, estado, ultimo_reporte, rssi, uptime_s FROM EstadoNodo;
```
3. **`MySQL`** `Ultimos`, *Settings → Execute Once* (para que corra una sola vez, no una por cada fila de `Nodos`):
```sql
SELECT id_nodo, nombre AS parametro, unidad, valor, fecha_hora FROM (
  SELECT s.id_nodo, p.nombre, p.unidad, m.valor, m.fecha_hora,
         ROW_NUMBER() OVER (PARTITION BY s.id_nodo, m.id_parametro ORDER BY m.fecha_hora DESC) AS rn
  FROM Medicion m
  JOIN Sensor s    ON s.id_sensor = m.id_sensor
  JOIN Parametro p ON p.id_parametro = m.id_parametro
  WHERE m.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 1 DAY
) t WHERE rn = 1;
```
4. **`Code`** `Armar respuesta`:
```javascript
return [{ json: {
  nodos:   $('Nodos').all().map(i => i.json),
  ultimos: $('Ultimos').all().map(i => i.json),
} }];
```
5. **`Respond to Webhook`**: *Respond With* `First Incoming Item`.

### 7.3 `GET /api/alertas`

`Webhook` (path `api/alertas`, misma autenticación) → **`Code`** `Validar`:
```javascript
const q = $json.query || {};
const estado = q.estado === 'todas' ? 'todas' : 'activa';
let limite = parseInt(q.limite ?? '50', 10);
if (Number.isNaN(limite)) return [{ json: { error: 'limite invalido', codigo: 400 } }];
limite = Math.min(Math.max(limite, 1), 200);
return [{ json: { estado, limite } }];
```
→ **`IF`** `{{ $json.error }}` *is empty* → verdadero: **`MySQL`**
```sql
SELECT id_alerta, id_nodo, tipo, valor, ts_inicio, ts_fin
FROM Alerta
WHERE (? = 'todas' OR ts_fin IS NULL)
ORDER BY ts_inicio DESC LIMIT ?;
```
Parámetros `{{ [$json.estado, $json.limite] }}` → `Code` que agrupa (`return [{ json: { alertas: $input.all().map(i => i.json) } }]`) → `Respond to Webhook` (200). La rama falso del `IF` va a otro `Respond to Webhook` con *Response Code* `400` y cuerpo `{{ { error: $json.error } }}`.

> `LIMIT ?` con un parámetro puede dar error en algunas versiones del conector [verificar]. Si pasa, cambia ese `?` por `{{ $json.limite }}` directo en el texto: es seguro **solo porque `Validar` ya lo convirtió en un entero entre 1 y 200**.

### 7.4 `GET /api/mediciones`

`Webhook` (path `api/mediciones`) → **`Code`** `Validar`:
```javascript
const q = $json.query || {};
const NODOS = ['dht', 'luz', 'pir', 'puerta', 'acel'];
const PARAMS = ['temperatura', 'humedad', 'luz'];
if (!NODOS.includes(q.nodo) || !PARAMS.includes(q.parametro))
  return [{ json: { error: 'nodo o parametro invalido', codigo: 400 } }];

const aSql = (d) => d.toISOString().slice(0, 19).replace('T', ' ');   // 2026-10-21 18:02:00
const hasta = q.hasta ? new Date(q.hasta) : new Date();
const desde = q.desde ? new Date(q.desde) : new Date(hasta.getTime() - 24 * 3600 * 1000);
if (isNaN(desde) || isNaN(hasta)) return [{ json: { error: 'fecha invalida', codigo: 400 } }];

let limite = parseInt(q.limite ?? '500', 10);
if (Number.isNaN(limite)) return [{ json: { error: 'limite invalido', codigo: 400 } }];
limite = Math.min(Math.max(limite, 1), 1000);

return [{ json: { nodo: q.nodo, parametro: q.parametro, desde: aSql(desde), hasta: aSql(hasta), limite } }];
```
(Se convierte la fecha ISO con `Z` a `AAAA-MM-DD HH:MM:SS`, porque MySQL no entiende la `T` ni la `Z`.) → `IF` → **`MySQL`**:
```sql
SELECT m.fecha_hora, m.valor
FROM Medicion m
JOIN Sensor s    ON s.id_sensor = m.id_sensor
JOIN Parametro p ON p.id_parametro = m.id_parametro
WHERE s.id_nodo = ? AND p.nombre = ? AND m.fecha_hora BETWEEN ? AND ?
ORDER BY m.fecha_hora DESC LIMIT ?;
```
Parámetros `{{ [$json.nodo, $json.parametro, $json.desde, $json.hasta, $json.limite] }}` → agrupar y responder igual.

### 7.5 Activar y probar con `curl`

Activa los tres flujos (los webhooks de producción solo responden si el flujo está **Active**). Las pruebas pasan por nginx (puerto 80), como lo hará el dashboard:

```bash
curl -s -H "X-API-Key: $API_KEY" "http://localhost/api/estado"
curl -s -H "X-API-Key: $API_KEY" "http://localhost/api/alertas?estado=todas"
curl -s -H "X-API-Key: $API_KEY" "http://localhost/api/mediciones?nodo=dht&parametro=temperatura&limite=5"
curl -i "http://localhost/api/estado"                                         # sin clave
curl -i -H "X-API-Key: x" "http://localhost/api/estado"                       # clave mala
curl -i -H "X-API-Key: $API_KEY" "http://localhost/api/mediciones?nodo=zzz&parametro=luz"   # 400
```

> `docs/api.md` promete **401** sin clave o con clave errónea. n8n suele responder **401 sin cabecera y 403 con clave errónea** [verificar]. Si es así, ajusta la tabla de errores de `docs/api.md` a lo que de verdad responde.

Exporta los flujos y:

```bash
git add . && git commit -m "Servidor: Web API de consulta (estado, mediciones, alertas) con webhooks de n8n" && git push
```

---

## Lección 8: desplegar en Oracle Cloud (Always Free)

El mismo compose corre en la nube. Así el sistema sigue funcionando aunque tu laptop esté apagada.

### 8.1 Crear la máquina virtual (en la consola de Oracle; tú, a mano)

1. **Compute → Instances → Create instance.**
2. **Image:** Canonical Ubuntu 24.04 (aarch64). **Shape:** `VM.Standard.A1.Flex` (Ampere ARM; el nivel gratis permite hasta 4 OCPU y 24 GB en total). Para Argos alcanza con **2 OCPU y 12 GB**. Si dice *Out of capacity*, prueba otro dominio de disponibilidad o reintenta más tarde: es común.
3. **Networking:** deja la red virtual (VCN) por defecto con IP pública.
4. **Add SSH keys → Generate a key pair** y **descarga la llave privada** (`.key`). Guárdala fuera del repo, por ejemplo en `C:\Users\luedm\.ssh\oracle_argos.key`. Quien tenga ese archivo entra a tu servidor.
5. Anota la **IP pública**.

### 8.2 Abrir puertos en Oracle (dos lugares, ambos necesarios)

**a) En la consola:** VCN → Security Lists → la lista por defecto → **Add Ingress Rules** (Source CIDR `0.0.0.0/0`, TCP) para los puertos **80** (dashboard y API) y **1883** (MQTT). El 22 (SSH) ya está. **No abras 3306 ni 5678.**

> El 1883 sin cifrar manda las contraseñas en claro por internet. Es un riesgo aceptado hasta agregar TLS (8883) al final, según la decisión del proyecto. Mientras tanto, cuando sepas la IP pública del invernadero, cambia el origen de la regla de `0.0.0.0/0` a esa IP.

**b) Dentro de la VM** (las imágenes de Ubuntu de Oracle traen un firewall extra):

```bash
ssh -i ~/.ssh/oracle_argos.key ubuntu@IP_PUBLICA
```

(Si Git Bash se queja de permisos de la llave: `chmod 600 ~/.ssh/oracle_argos.key`.) Ya dentro:

```bash
sudo iptables -L INPUT --line-numbers      # busca la linea de REJECT; anota su numero
sudo iptables -I INPUT 5 -p tcp --dport 80   -m state --state NEW -j ACCEPT
sudo iptables -I INPUT 5 -p tcp --dport 1883 -m state --state NEW -j ACCEPT
sudo apt-get update && sudo apt-get install -y iptables-persistent   # contesta Yes
sudo netfilter-persistent save
```

Cambia el `5` por un número **menor** al de la línea `REJECT` (las reglas se evalúan en orden, y las nuevas deben quedar antes del rechazo).

### 8.3 Instalar Docker en la VM

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
exit
```

Vuelve a entrar por SSH (para que se aplique el grupo) y comprueba `docker version` y `docker compose version`.

### 8.4 Copiar el proyecto

Desde tu PC, en la raíz del repo (el compose usa `../docs/bd/esquema.sql`, así que se conserva la misma estructura de carpetas):

```bash
ssh -i ~/.ssh/oracle_argos.key ubuntu@IP_PUBLICA "mkdir -p ~/argos/docs"
scp -i ~/.ssh/oracle_argos.key -r servidor ubuntu@IP_PUBLICA:~/argos/
scp -i ~/.ssh/oracle_argos.key -r docs/bd ubuntu@IP_PUBLICA:~/argos/docs/
scp -i ~/.ssh/oracle_argos.key .env ubuntu@IP_PUBLICA:~/argos/.env
```

Para producción conviene **otro `.env` con contraseñas nuevas** (no reutilices las de tu laptop). Genera las 12 con el mismo comando de la lección 2, y **vuelve a crear `passwd`** en el servidor:

```bash
ssh -i ~/.ssh/oracle_argos.key ubuntu@IP_PUBLICA
cd ~/argos
bash servidor/crear_usuarios_mqtt.sh
```

> En ese script `pwd -W` solo existe en Git Bash. En Linux cambia `$(pwd -W)` por `$(pwd)` y quita `MSYS_NO_PATHCONV=1`. Edita la copia del servidor, no la de tu repo.

### 8.5 Levantar

```bash
cd ~/argos/servidor
docker compose --env-file ../.env up -d
docker compose ps
```

Todas las imágenes tienen versión ARM, así que no hay que cambiar nada.

### 8.6 Entrar al editor de n8n

El editor está limitado a `127.0.0.1` a propósito. Se abre con un **túnel SSH** desde tu PC:

```bash
ssh -i ~/.ssh/oracle_argos.key -L 5678:localhost:5678 ubuntu@IP_PUBLICA
```

Con esa terminal abierta, entra a `http://localhost:5678` en tu navegador: ahí ves el n8n de Oracle. Crea la cuenta de dueño, las 4 credenciales (en el servidor los hosts también son `mosquitto` y `mysql`) e importa los flujos:

```bash
# En tu PC:
scp -i ~/.ssh/oracle_argos.key servidor/n8n/workflows/flujos.json ubuntu@IP_PUBLICA:~/flujos.json
# En el servidor:
docker cp ~/flujos.json argos-n8n:/tmp/flujos.json
docker exec argos-n8n n8n import:workflow --input=/tmp/flujos.json
```

[verificar el comando de importación en n8n 2.x]. Después reasigna las credenciales en cada paso si n8n lo pide y **activa** los flujos.

### 8.7 Probar desde fuera

Desde tu PC (no desde la VM), con el simulador apuntando a la nube: en `.env` de tu PC pon `MQTT_HOST=IP_PUBLICA` y las contraseñas **del servidor**:

```bash
uv run --no-project --python 3.12 --with paho-mqtt python simulador/simulador_nodos.py --rapido --escenario calor
curl -s -H "X-API-Key: LA_API_KEY_DEL_SERVIDOR" "http://IP_PUBLICA/api/alertas"
```

Si el simulador conecta, el puerto 1883 está bien abierto en los **dos** firewalls. Si no, revisa la 8.2.

### 8.8 Respaldo diario de la base

```bash
crontab -e
```

y agrega (una sola línea; reemplaza `ROOTPASS` por la contraseña, o mejor lee de `.env` con un script):

```
0 3 * * * docker exec argos-mysql mysqldump -uroot -pROOTPASS argos | gzip > ~/respaldo_argos_$(date +\%F).sql.gz
```

Corre a las 3:00 (hora de la VM, UTC). `\%` es necesario dentro de cron. Descarga un respaldo de vez en cuando con `scp` y verifica que se pueda leer.

### Lo que queda para más adelante

- **TLS en MQTT (8883)** y HTTPS en nginx, con un dominio gratuito y Let's Encrypt. Es el último paso, según las decisiones del proyecto.
- **Dashboard** (Chart.js + MQTT.js), **avisos por WhatsApp (CallMeBot) y Telegram**. La siguiente tanda. El dashboard en el navegador necesitará la `API_KEY` y un usuario MQTT de solo lectura, que quedan visibles en el código de la página: trátalos como claves "públicas de solo lectura" y no reutilices ninguna contraseña importante.
- **Preguntas abiertas** que afectan esto: WiFi del invernadero (¿deja salir el puerto 1883?, `docs/preguntas.md` C3) y la rúbrica de "Web API" con webhooks (B1).
- **Plan B si el WiFi del invernadero bloquea el 1883:** broker Mosquitto en una laptop dentro del cuarto con puente (*bridge*) hacia Oracle.

---

## Resumen de comandos del día a día

```bash
cd servidor
alias dc='docker compose --env-file ../.env'
dc up -d                  # levanta todo
dc ps                     # estado
dc logs -f n8n            # ver lo que hace n8n (Ctrl+C para salir)
dc restart mosquitto      # reinicia uno
dc down                   # apaga y borra contenedores (los datos se conservan)
dc down -v                # CUIDADO: tambien BORRA los datos (volumenes)
```
