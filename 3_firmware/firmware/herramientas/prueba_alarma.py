"""Compila y corre prueba_alarma.cpp (reglas del buzzer del dht) en la PC. Necesita g++ de WinLibs.
Uso (desde la raiz):
    python firmware/herramientas/prueba_alarma.py
"""
import glob
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
GPP = os.environ.get("GXX") or next(iter(glob.glob(str(
    Path.home() / "AppData/Local/Microsoft/WinGet/Packages/BrechtSanders.WinLibs*/mingw64/bin/g++.exe"))), "g++")
SALIDA = AQUI / "_build"
SALIDA.mkdir(exist_ok=True)
EXE = SALIDA / "prueba_alarma.exe"

r = subprocess.run([GPP, "-std=c++17", "-O1", "-Wall", str(AQUI / "prueba_alarma.cpp"), "-o", str(EXE)],
                   capture_output=True, text=True)
if r.returncode:
    sys.exit(r.stderr[-3000:])
sys.exit(subprocess.run([str(EXE)]).returncode)
