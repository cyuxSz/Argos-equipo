"""Exporta las 3 cajas y sus accesorios para el visor web (presentacion/), y los cortes por niveles.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/web.py
Salida:
  presentacion/modelos/<caja>_<grupo>.stl y acc_<pieza>.stl (coordenadas del nodo: y arriba, z al frente)
  presentacion/modelos.json   todos los STL en base64 (el artifact no sirve .stl)
  presentacion/nodos.json     medidas, grupos y niveles de corte por caja
  cad/renders/niveles_<caja>.png (cad/niveles.py)
"""
import base64
import json
from pathlib import Path

from build123d import Compound, export_stl

import escenas
import niveles
import nodos

RAIZ = Path(__file__).resolve().parent.parent
PRES = RAIZ / "presentacion"
DESTINO = PRES / "modelos"
VISIBLES = {"oled": "pantalla", "pir_domo": "domo"}
Z_TAPA = 26.0          # lo que empieza por encima de este z va montado en la tapa (se mueve con ella)


def grupo_de(nombre, solido):
    if nombre.endswith("_patas") or nombre == "cable_usb":
        return None
    if nombre in VISIBLES:
        return VISIBLES[nombre]
    if nombre.startswith("led_verde"):
        return "led_v"
    if nombre.startswith("led_rojo"):
        return "led_r"
    cat = niveles.categoria(nombre)
    return cat + ("_t" if solido.bounding_box().min.Z >= Z_TAPA else "")


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    for viejo in DESTINO.glob("*.stl"):
        viejo.unlink()
    info, paquete = {}, {}

    def guardar(nombre, partes):
        ruta = DESTINO / f"{nombre}.stl"
        export_stl(Compound(children=partes), str(ruta), tolerance=0.05, angular_tolerance=0.3)
        paquete[nombre] = base64.b64encode(ruta.read_bytes()).decode()

    for clave, fabrica in nodos.NODOS.items():
        n = fabrica()
        grupos = {"base": [n["piezas"]["base"]], "tapa": [n["piezas"]["tapa"]]}
        if "embolo_boton" in n["piezas"]:
            grupos["tapa"].append(n["piezas"]["embolo_boton"])
        for nombre, (s, _) in n["gemelo"].partes.items():
            g = grupo_de(nombre, s)
            if g:
                grupos.setdefault(g, []).append(s)
        for g, partes in grupos.items():
            guardar(f"{clave}_{g}", partes)
        bb = Compound(children=[n["piezas"]["base"], n["piezas"]["tapa"]]).bounding_box()
        info[clave] = {"grupos": list(grupos), "W": round(n["W"], 1), "H": round(n["H"], 1), "D": n["D"],
                       "con_orejas": [round(v, 1) for v in bb.size],
                       "centro": [round(bb.center().X, 2), round(bb.center().Y, 2), round(bb.center().Z, 2)],
                       "niveles": [{"clave": k, "nombre": nom, "z": z} for k, nom, z in niveles.NIVELES]}
        print(clave, "grupos:", ", ".join(f"{g}({len(p)})" for g, p in grupos.items()))
        print("   cortes:", niveles.dibujar(n).name)
    acc = escenas.accesorios()
    for k, s in acc.items():
        guardar(f"acc_{k}", [s])
    info["accesorios"] = {"piezas": list(acc)}
    (PRES / "nodos.json").write_text(json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")
    (PRES / "modelos.json").write_text(json.dumps(paquete), encoding="utf-8")
    print("modelos.json:", round((PRES / "modelos.json").stat().st_size / 1e6, 2), "MB,", len(paquete), "piezas")


if __name__ == "__main__":
    main()
