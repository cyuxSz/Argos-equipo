"""Compila oled_host.c con las fuentes U8g2 del firmware y genera:
  docs/oled_estados.png            la pantalla en 7 estados, pixel por pixel (0.43 mm por punto)
  presentacion/glifos_oled.json    los glifos reales, para que la pagina dibuje igual que el hardware

Uso (desde la raiz; necesita gcc de WinLibs y haber compilado el firmware dht una vez, para que PlatformIO
descargue U8g2):
    uv run --no-project --python 3.12 --with pillow python firmware/herramientas/oled_host.py
"""
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
CLIB = Path(os.environ.get("U8G2_CLIB", Path.home() / ".platformio/ws/incumonitor/libdeps/dht/U8g2/src/clib"))
GCC = os.environ.get("GCC") or next(iter(glob.glob(str(
    Path.home() / "AppData/Local/Microsoft/WinGet/Packages/BrechtSanders.WinLibs*/mingw64/bin/gcc.exe"))), "gcc")
SALIDA = RAIZ / "firmware" / "herramientas" / "_build"
SALIDA.mkdir(exist_ok=True)
EXE = SALIDA / "oled_host.exe"

if not EXE.exists() or EXE.stat().st_mtime < (RAIZ / "firmware/include/vista_oled.h").stat().st_mtime:
    fuentes = [str(p) for p in CLIB.glob("*.c") if not p.name.startswith("mui")]
    cmd = [GCC, "-O1", "-w", f"-I{CLIB}", str(RAIZ / "firmware/herramientas/oled_host.c"), *fuentes, "-o", str(EXE)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])

listado = subprocess.run([str(EXE), "estados", str(SALIDA)], capture_output=True, text=True, check=True).stdout.strip().splitlines()
subprocess.run([str(EXE), "glifos", str(RAIZ / "presentacion" / "glifos_oled.json")], check=True)

ESC = 5
VERDE = (233, 246, 238)
celdas = []
for linea in listado:
    i, nombre = linea.split("|", 1)
    filas = (SALIDA / f"estado_{i}.txt").read_text().split()
    im = Image.new("RGB", (128 * ESC, 64 * ESC), (0, 0, 0))
    px = im.load()
    for y, fila in enumerate(filas):
        for x, c in enumerate(fila):
            if c == "1":
                for dy in range(ESC - 1):
                    for dx in range(ESC - 1):
                        px[x * ESC + dx, y * ESC + dy] = VERDE
    celdas.append((nombre, im))

fuente = ImageFont.load_default()
cols = 2
filas_n = (len(celdas) + cols - 1) // cols
M = 14
ancho, alto = 128 * ESC, 64 * ESC + 22
hoja = Image.new("RGB", (cols * (ancho + M) + M, filas_n * (alto + M) + M), (235, 238, 236))
d = ImageDraw.Draw(hoja)
for k, (nombre, im) in enumerate(celdas):
    x = M + (k % cols) * (ancho + M)
    y = M + (k // cols) * (alto + M)
    hoja.paste(im, (x, y))
    d.text((x, y + 64 * ESC + 5), nombre, fill=(30, 40, 35), font=fuente)
destino = RAIZ / "docs" / "oled_estados.png"
hoja.save(destino)
print("ok", destino)
