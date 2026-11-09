"""Compara los pines del firmware con las redes de hardware/breadboard/layouts.py (no cambia ninguno).

Por cada entorno de firmware/platformio.ini lee las constantes PIN_* (respetando #if USAR_OLED) y el uso
de I2C (Wire.begin: D1/D2), y exige que coincidan con los pines del NodeMCU que aparecen en las redes de
su distribucion. Uso (desde la raiz):
    python hardware/chequeo_pines.py
Sale con codigo 1 si algo no coincide.
"""
import configparser
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "hardware" / "breadboard"))
import layouts  # noqa: E402

FW = RAIZ / "firmware"
ALIMENTACION = {"VIN", "3V3", "GND"}


def entornos():
    """entorno -> (carpeta de src, {define: valor}), leido de platformio.ini."""
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(FW / "platformio.ini", encoding="utf-8")
    res = {}
    for sec in ini.sections():
        if not sec.startswith("env:"):
            continue
        src = re.search(r"\+<(\w+)/>", ini[sec]["build_src_filter"])[1]
        defs = dict(re.findall(r"-D\s*(\w+)=(\S+)", ini[sec].get("build_flags", "")))
        res[sec[4:]] = (src, defs)
    return res


def pines_firmware(src, defs):
    """Pines usados por el firmware de un entorno, evaluando solo los #if de sus defines."""
    usados = set()
    for f in (FW / "src" / src / "main.cpp", FW / "include" / "nodo_comun.h"):
        texto = f.read_text(encoding="utf-8")
        if f.name == "nodo_comun.h" and '#include "nodo_comun.h"' not in (FW / "src" / src / "main.cpp").read_text(encoding="utf-8"):
            continue
        activo = [True]
        for linea in texto.splitlines():
            s = linea.strip()
            m = re.match(r"#if\s+(\w+)$", s)
            if m:
                activo.append(activo[-1] and defs.get(m[1], "0") not in ("0", ""))
                continue
            if s.startswith("#if"):
                activo.append(activo[-1])
            elif s.startswith("#else"):
                activo[-1] = not activo[-1] and activo[-2]
            elif s.startswith("#endif"):
                activo.pop()
            elif activo[-1]:
                usados |= set(re.findall(r"constexpr\s+uint8_t\s+PIN_\w+\s*=\s*(D\d|A0)\b", s))
                if re.search(r"\bWire\.begin\(\)", s):
                    usados |= {"D1", "D2"}   # ESP8266: SDA = D2, SCL = D1
    return usados


def pines_layout(nombre):
    lay = layouts.LAYOUTS[nombre]
    return {m.split(".", 1)[1] for red in lay["redes"].values() for m in red
            if m.startswith("NodeMCU.")} - ALIMENTACION


def main():
    falla = False
    for env, (src, defs) in entornos().items():
        lay = f"nodo_{env}"
        fw, hw = pines_firmware(src, defs), pines_layout(lay)
        ok = fw == hw
        falla |= not ok
        print(f"{env}: {'OK' if ok else 'NO COINCIDE'} {sorted(fw)}" +
              ("" if ok else f"\n   solo firmware: {sorted(fw - hw)}  solo {lay}: {sorted(hw - fw)}"))
    sys.exit(1 if falla else 0)


if __name__ == "__main__":
    main()
