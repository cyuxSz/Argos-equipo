#!/usr/bin/env bash
# Crea servidor/mosquitto/passwd con un usuario por nodo, mas n8n, dashboard y api.
# Las contrasenas salen del archivo de secretos de la raiz (o de otro que le pases como argumento).
# Uso:  bash servidor/crear_usuarios_mqtt.sh [archivo_de_secretos]

set -euo pipefail                      # se detiene ante cualquier error o variable vacia
cd "$(dirname "$0")/.."                # raiz del repo
SECRETOS="${1:-.env}"                  # sin argumento usa el archivo de secretos de la raiz

# Carga el archivo como variables. tr -d '\r' quita los CR si quedo con CRLF.
set -a; source <(tr -d '\r' < "$SECRETOS"); set +a

PASSWD=servidor/mosquitto/passwd
: > "$PASSWD"                          # vacia el archivo para crearlo desde cero
RUTA="$(pwd -W 2>/dev/null || pwd)"    # pwd -W: ruta de Windows (Git Bash); en Linux, pwd normal

for u in dht luz pir puerta acel n8n dashboard api; do
  var="MQTT_PASSWORD_${u^^}"           # ${u^^} = nombre en MAYUSCULAS
  # MSYS_NO_PATHCONV=1 evita que Git Bash "traduzca" /mosquitto/... a una ruta de Windows
  MSYS_NO_PATHCONV=1 docker run --rm \
    -v "$RUTA/servidor/mosquitto:/mosquitto/config" \
    eclipse-mosquitto:2.0.22 \
    mosquitto_passwd -b /mosquitto/config/passwd "$u" "${!var}"   # ${!var} = valor de la variable cuyo nombre esta en var
done
echo "usuarios creados en $PASSWD"
