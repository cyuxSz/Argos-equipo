"""Genera sketches para Arduino IDE 2.x a partir de firmware/src (que sigue siendo la fuente de verdad).

PlatformIO pasa NODO_ID y USAR_OLED con build_flags; Arduino IDE no tiene build_flags, asi que cada
sketch lleva un main.cpp con esos #define al principio y un .ino vacio (evita el preprocesado del .ino).
Uso (desde la raiz):
    python firmware/herramientas/exportar_arduino.py
Salida: firmware/arduino_ide/argos_<entorno>/  (se regenera; no editar ahi).
Las credenciales: copiar secrets.example.h a secrets.h DENTRO de cada sketch (no se versiona).
"""
import configparser
import re
import shutil
from pathlib import Path

FW = Path(__file__).resolve().parent.parent
DESTINO = FW / "arduino_ide"
CABECERAS = ("nodo_comun.h", "api_http.h", "alarma_dht.h", "vista_oled.h", "secrets.example.h")   # nunca el real


def entornos():
    """entorno -> (carpeta de src, #defines), leido de platformio.ini (build_src_filter y build_flags)."""
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(FW / "platformio.ini", encoding="utf-8")
    res = {}
    for sec in ini.sections():
        if sec.startswith("env:"):
            src = re.search(r"\+<(\w+)/>", ini[sec]["build_src_filter"])[1]
            defs = {k: v.replace('\\"', '"') for k, v in re.findall(r"-D\s*(\w+)=(\S+)", ini[sec].get("build_flags", ""))}
            res[sec[4:]] = (src, defs)
    return res


def main():
    for env, (src, defs) in entornos().items():
        sk = DESTINO / f"argos_{env}"
        if sk.exists():
            for f in sk.iterdir():           # conserva el secrets.h que haya puesto el usuario
                if f.name != "secrets.h":
                    f.unlink()
        sk.mkdir(parents=True, exist_ok=True)
        # El programa va DENTRO del .ino (es el archivo que se entrega: renombrarlo como
        # Arduino-EquipoX-Matricula.ino junto con la carpeta). Los .h son los "archivos necesarios".
        cab = "".join(f"#define {k} {v}\n" for k, v in defs.items())
        cuerpo = (FW / "src" / src / "main.cpp").read_text(encoding="utf-8")
        (sk / f"{sk.name}.ino").write_text(
            f"// Argos, nodo {env}. GENERADO por firmware/herramientas/exportar_arduino.py desde "
            f"firmware/src/{src}/main.cpp (editar alla y regenerar).\n"
            "// Placa: NodeMCU 1.0 (ESP-12E Module). Credenciales: copiar secrets.example.h a secrets.h en esta carpeta.\n"
            + cab + cuerpo, encoding="utf-8")
        for h in CABECERAS:
            shutil.copy2(FW / "include" / h, sk / h)
        print("ok", sk.relative_to(FW.parent))


if __name__ == "__main__":
    main()
