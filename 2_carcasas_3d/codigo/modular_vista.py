"""Variante modular de las cajas: chequeos extra y renders.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib --with pyvista python cad/modular_vista.py

Salida: cad/renders/modular/modular_*.png y un resumen en consola. Las piezas (STEP/STL) las escribe
`cad/nodos.py --modular` en cad/exports/modular/.
"""
import os
import sys
from pathlib import Path

os.environ["ARGOS_MODULAR"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

import nodos  # noqa: E402
from nodos import DIS  # noqa: E402

RENDERS = Path(__file__).resolve().parent / "renders" / "modular"
COL = dict(base="#e9ecef", tapa="#f8f9fa", proto="#fdfdf5", placa="#2b6cb0", comp="#718096", clip="#e8590c",
           oled="#1a202c", grapa="#e8590c", led_v="#2f9e44", led_r="#e03131")


def malla(s, tol=0.15):
    ms = []
    for sol in (s.solids() or [s]):
        v, t = sol.tessellate(tol, 0.3)
        if t:
            ms.append(pv.PolyData(np.array([[q.X, q.Y, q.Z] for q in v]), np.hstack([[3, *tri] for tri in t])))
    return pv.merge(ms) if len(ms) > 1 else ms[0]


def toma(nombre, partes, camara, tam=(1500, 1100), zoom=1.0, escala=None):
    pl = pv.Plotter(off_screen=True, window_size=tam)
    pl.set_background("white")
    for s, color, op in partes:
        pl.add_mesh(malla(s), color=color, opacity=op, smooth_shading=False, split_sharp_edges=True)
    pl.camera_position = camara
    pl.enable_parallel_projection()
    if escala:                       # acercamiento: se respeta el punto de mira y se fija la escala
        pl.camera.parallel_scale = escala
    else:
        pl.reset_camera()
        pl.camera.zoom(zoom)
    pl.enable_anti_aliasing("ssaa")
    RENDERS.mkdir(parents=True, exist_ok=True)
    pl.screenshot(str(RENDERS / f"modular_{nombre}.png"))
    pl.close()
    print("ok", f"modular_{nombre}.png")


def gemelo(n, nombres=None, excluir=()):
    g = n["gemelo"].partes
    return [g[k][0] for k in g if (nombres is None or k in nombres) and k not in excluir]


def chequeos(n):
    """Lo que nodos.verificar no cubre: la grapa de la OLED y el agarre real de clips y broches."""
    base, tapa, g = n["piezas"]["base"], n["piezas"]["tapa"], n["gemelo"].partes
    pb = g["protoboard"][0]
    print(f"[{n['nodo']}] base y tapa: {len(base.solids())} y {len(tapa.solids())} solido(s) (debe ser 1 y 1)")
    techo = pb.bounding_box().max.Z
    arriba = base & nodos.caja_c(0, 0, techo + 0.05, 400, 400, 3.0) & \
        nodos.Pos(0, 0, 0) * pb.moved(nodos.Pos(0, 0, 2.0))
    print(f"[{n['nodo']}] ganchos que pisan la protoboard: {len(arriba.solids())}, "
          f"de {DIS['clip']['gancho']} mm")
    if "grapa_oled" in n["montaje"]:
        gr = n["montaje"]["grapa_oled"]
        v_t = (gr & tapa).volume
        v_g = sum((gr & s).volume for s, _ in g.values())
        d_o = gr.distance_to(g["oled"][0])
        d_n = min(gr.distance_to(g[k][0]) for k in g if k not in ("oled", "oled_dupont"))
        print(f"[{n['nodo']}] grapa OLED: choque con tapa {v_t:.3f} mm3, con electronica {v_g:.3f} mm3; "
              f"a {d_o:.2f} mm de la OLED y a {d_n:.2f} mm de lo demas")


def main():
    dht = nodos.nodo_dht()
    chequeos(dht)
    W, H, D, Db = dht["W"], dht["H"], dht["D"], dht["Db"]
    base, tapa = dht["piezas"]["base"], dht["piezas"]["tapa"]
    c = (0, H / 2, D / 2)
    # 1. caja cerrada
    leds = [(s, COL["led_v"] if "verde" in k else COL["led_r"], 1.0) for k, (s, _) in dht["gemelo"].partes.items()
            if k in ("led_verde", "led_rojo")]
    toma("dht_cerrada", [(base, COL["base"], 1.0), (tapa, COL["tapa"], 1.0),
                         (dht["gemelo"].partes["oled"][0], COL["oled"], 1.0)] + leds,
         [(170, H / 2 - 150, 230), c, (0, 1, 0)], zoom=1.25)
    # 2. base abierta: protoboard sujeta por los clips
    electronica = gemelo(dht, excluir=("oled", "oled_dupont", "led_verde", "led_rojo", "led_verde_patas",
                                       "led_rojo_patas", "boton", "boton_dupont", "buzzer", "buzzer_pcb",
                                       "buzzer_dupont", "protoboard", "nodemcu", "cable_usb"))
    g = dht["gemelo"].partes
    toma("dht_base_clips", [(base, COL["base"], 1.0), (g["protoboard"][0], COL["proto"], 1.0),
                            (g["nodemcu"][0], COL["placa"], 1.0)] + [(s, COL["comp"], 1.0) for s in electronica],
         [(150, H / 2 - 120, 260), (0, H / 2 + 10, 10), (0, 1, 0)], zoom=1.25)
    # 3. acercamiento al clip derecho y a la lengua de la tapa
    yc = dht["y_pb_inf"] + 82.5 - 22
    toma("dht_detalle_clip", [(base, COL["base"], 1.0), (g["protoboard"][0], COL["proto"], 1.0)],
         [(-25, yc - 45, 85), (30, yc + 4, 8), (0, 0, 1)], escala=24)
    # 4. tapa por dentro con la OLED y su grapa
    gr = dht["montaje"]["grapa_oled"]
    toma("dht_tapa_grapa", [(tapa, COL["tapa"], 1.0), (g["oled"][0], COL["oled"], 1.0), (gr, COL["grapa"], 1.0)],
         [(120, H / 2 - 110, -170), (0, H / 2 + 10, Db), (0, 1, 0)], zoom=1.25)
    # 5. explosionada
    sep = 55.0
    mv = nodos.Pos(0, 0, sep)
    toma("dht_explosionada",
         [(base, COL["base"], 1.0), (mv * g["protoboard"][0], COL["proto"], 1.0), (mv * g["nodemcu"][0], COL["placa"], 1.0)]
         + [(mv * s, COL["comp"], 1.0) for s in electronica if s is not g["dht22"][0]]
         + [(nodos.Pos(0, 0, 2 * sep) * gr, COL["grapa"], 1.0), (nodos.Pos(0, 0, 2.3 * sep) * g["oled"][0], COL["oled"], 1.0),
            (nodos.Pos(0, 0, 3 * sep) * tapa, COL["tapa"], 1.0)],
         [(330, H / 2 - 260, 330), (0, H / 2, 100), (0, 0, 1)], zoom=1.15)
    # 6. estacion (entrada): cerrada y abierta
    for nombre in ("entrada", "anaquel"):
        e = nodos.NODOS[nombre]()
        chequeos(e)
        if nombre != "entrada":
            continue
        b, t, ge = e["piezas"]["base"], e["piezas"]["tapa"], e["gemelo"].partes
        ce = (e["W"] / 2, e["H"] / 2, 20)
        toma("entrada_cerrada", [(b, COL["base"], 1.0), (t, COL["tapa"], 1.0)]
             + [(s, "#f1f3f5", 1.0) for k, (s, _) in ge.items() if k == "pir_domo"]
             + [(s, COL["led_v"] if "verde" in k else COL["led_r"], 1.0) for k, (s, _) in ge.items()
                if k.startswith("led_") and "patas" not in k],
             [(e["W"] / 2 + 120, -190, 260), ce, (0, 1, 0)], zoom=1.2)
        toma("entrada_base_clips", [(b, COL["base"], 1.0), (ge["protoboard"][0], COL["proto"], 1.0)]
             + [(s, COL["placa"], 1.0) for k, (s, _) in ge.items() if k.startswith(("pir", "puerta")) and "pir_" not in k],
             [(e["W"] / 2 + 60, -150, 290), (e["W"] / 2, e["H"] / 2, 5), (0, 1, 0)], zoom=1.25)


if __name__ == "__main__":
    main()
