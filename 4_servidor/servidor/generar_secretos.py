"""Crea el archivo de secretos de la raiz con contrasenas al azar. Tu lo corres; no imprime ningun valor.

Uso (desde la raiz del repo):  python servidor/generar_secretos.py
- Si el archivo no existe, lo crea a partir de la plantilla (.env.example).
- Si ya existe, solo llena las variables que estan vacias; nunca cambia las que ya tienen valor.
- WIFI_SSID y WIFI_PASSWORD se dejan vacios (los pones tu con los datos del invernadero).
"""
import secrets
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / ".env"
PLANTILLA = RAIZ / ".env.example"
FIJOS = {"MQTT_HOST": "localhost", "MQTT_PORT": "1883"}   # para probar en tu PC; en Oracle pones la IP
A_MANO = {"WIFI_SSID", "WIFI_PASSWORD"}


def variable(linea):
    """Nombre de la variable de una linea 'NOMBRE=valor', o None si es comentario o vacia."""
    if "=" in linea and not linea.lstrip().startswith("#"):
        return linea.split("=", 1)[0].strip()
    return None


base = DESTINO if DESTINO.exists() else PLANTILLA
lineas = base.read_text(encoding="utf-8").splitlines()
if base is DESTINO:   # agrega las variables nuevas de la plantilla que el archivo aun no tiene
    conocidas = {variable(l) for l in lineas}
    lineas += [l for l in PLANTILLA.read_text(encoding="utf-8").splitlines()
               if variable(l) and variable(l) not in conocidas]

llenadas = 0
salida = []
for linea in lineas:
    nombre = variable(linea)
    if nombre and not linea.split("=", 1)[1].strip() and nombre not in A_MANO:
        linea = f"{nombre}={FIJOS.get(nombre) or secrets.token_urlsafe(18)}"   # 24 caracteres: letras, numeros, - y _
        llenadas += 1
    salida.append(linea)

DESTINO.write_text("\n".join(salida) + "\n", encoding="utf-8", newline="\n")
print(f"listo: {llenadas} variables llenadas (no se muestran). Archivo: {DESTINO.name}")
