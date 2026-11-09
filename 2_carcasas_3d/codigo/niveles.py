"""Cortes acotados por niveles de profundidad (de la espalda al frente) y un corte lateral, por caja.

Lo llama cad/web.py. Cada nivel es un plano paralelo al frente (z constante): se dibuja lo que corta de la base,
la tapa y el gemelo (protoboard, placas, modulos, cables), con cotas en mm.
Salida: cad/renders/niveles_<nodo>.png
"""
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from build123d import Compound, Plane  # noqa: E402

from vistas import cota  # noqa: E402

RENDERS = Path(__file__).resolve().parent / "renders"

# (clave, nombre, z en mm desde la espalda). Salen de las alturas del gemelo: protoboard 2-10.5,
# placas y componentes 10.5-24.5, modulos altos hasta 30.5, tapa 38-40.5.
NIVELES = [
    ("n1", "Piso: protoboard, guías y torretas", 6.0),
    ("n2", "Placas y componentes", 12.0),
    ("n3", "Conectores y módulos", 20.0),
    ("n4", "Bajo la tapa: módulos altos y costillas", 30.0),
    ("n5", "Frente de la tapa: ventanas y LED", 39.2),
]

CATEGORIAS = {   # categoria -> (color, etiqueta)
    "carcasa": ("#c9cec9", "Carcasa impresa (base y tapa)"),
    "protoboard": ("#f4efe2", "Protoboard"),
    "placa": ("#3b6ea5", "NodeMCU y entrada de 5 V"),
    "modulos": ("#3f8a5f", "Sensores, módulos y componentes"),
    "cables": ("#6b6b6b", "Conectores Dupont y cables"),
    "led": ("#d9902f", "LED"),
}


def categoria(nombre):
    if nombre == "protoboard" or nombre.endswith("_tira"):
        return "protoboard"
    if nombre.startswith("nodemcu") or nombre == "entrada_5v":
        return "placa"
    if "dupont" in nombre or nombre == "cable_usb":
        return "cables"
    if nombre.startswith("led_"):
        return "led"
    return "modulos"


def caras(shape, plano):
    try:
        sec = shape.intersect(plano)
    except Exception:
        return []
    return list(sec.faces()) if sec else []


def pintar(ax, cara, color, ejes, borde="#333333", lw=0.4):
    def pts(w, n):
        return [tuple(w @ (i / n)) for i in range(n + 1)]
    ext = pts(cara.outer_wire(), 160)
    ax.fill([p[ejes[0]] for p in ext], [p[ejes[1]] for p in ext], facecolor=color, edgecolor=borde, lw=lw)
    for w in cara.inner_wires():
        q = pts(w, 80)
        ax.fill([p[ejes[0]] for p in q], [p[ejes[1]] for p in q], facecolor="white", edgecolor=borde, lw=lw * 0.8)


def _seccion(ax, n, plano, ejes, rotulos=True):
    carcasa = Compound(children=[n["piezas"]["base"], n["piezas"]["tapa"]])
    for cara in caras(carcasa, plano):
        pintar(ax, cara, CATEGORIAS["carcasa"][0], ejes, borde="#666666")
    usados = set()
    for nom, (s, _) in n["gemelo"].partes.items():
        if nom.endswith("_patas") or nom == "cable_usb":
            continue
        cat = categoria(nom)
        cortes = caras(s, plano)
        for cara in cortes:
            pintar(ax, cara, CATEGORIAS[cat][0], ejes)
        if cortes:
            usados.add(cat)
            grande = cat in ("placa", "modulos") and s.bounding_box().size.X * s.bounding_box().size.Y > 150
            if rotulos and grande and nom != "cable_usb":
                c = s.bounding_box().center()
                xy = (c.X, c.Y) if ejes == (0, 1) else (c.Z, c.Y)
                ax.text(*xy, nom.replace("_", " "), fontsize=5.5, ha="center", va="center", color="white",
                        fontweight="bold")
    return usados


def dibujar(n):
    RENDERS.mkdir(exist_ok=True)
    nodo, W = n["nodo"], n["W"]
    bb = Compound(children=[n["piezas"]["base"], n["piezas"]["tapa"]]).bounding_box()
    ancho = W > n["H"]
    cols = 2 if ancho else 3
    filas = math.ceil((len(NIVELES) + 1) / cols)
    fig, ejes = plt.subplots(filas, cols, figsize=(14 if ancho else 13, 4.2 * filas if ancho else 7.2 * filas))
    ejes = list(ejes.flat)
    usados = set()
    for ax, (clave, nombre, z) in zip(ejes, NIVELES):
        usados |= _seccion(ax, n, Plane.XY.offset(z), (0, 1))
        ax.set_aspect("equal")
        ax.set_title(f"{clave.upper()} · z = {z:.1f} mm · {nombre}", fontsize=9)
        y0, y1 = bb.min.Y, bb.max.Y
        cota(ax, (bb.min.X, y0), (bb.max.X, y0), -9, f"{bb.size.X:.1f}")
        cota(ax, (bb.max.X, y0), (bb.max.X, y1), 9, f"{bb.size.Y:.1f}", vertical=True)
        ax.set_xlim(bb.min.X - 8, bb.max.X + 22)
        ax.set_ylim(y0 - 22, y1 + 6)
        ax.axis("off")
    # corte lateral por el centro de la primera placa, con los niveles marcados
    ax = ejes[len(NIVELES)]
    placas = [s for nom, (s, _) in n["gemelo"].partes.items() if nom.startswith("nodemcu")]
    x_lat = placas[0].bounding_box().center().X if placas else 0.0
    usados |= _seccion(ax, n, Plane.YZ.offset(x_lat), (2, 1), rotulos=False)
    for clave, _, z in NIVELES:
        ax.axvline(z, color="#b03030", lw=0.6, ls="--")
        ax.text(z, bb.max.Y + 3, clave.upper(), color="#b03030", fontsize=7, ha="center")
    cota(ax, (0, bb.min.Y), (n["D"], bb.min.Y), -9, f"{n['D']:.1f} prof.")
    ax.set_aspect("equal")
    ax.set_xlim(-6, n["D"] + 8)
    ax.set_ylim(bb.min.Y - 22, bb.max.Y + 10)
    ax.set_title(f"Corte lateral (x = {x_lat:.1f} mm): espalda a la izquierda, frente a la derecha", fontsize=9)
    ax.axis("off")
    for ax in ejes[len(NIVELES) + 1:]:
        ax.axis("off")
    fig.legend(handles=[Patch(facecolor=CATEGORIAS[c][0], edgecolor="#333", label=CATEGORIAS[c][1])
                        for c in CATEGORIAS if c in usados or c == "carcasa"],
               loc="lower center", ncol=3, fontsize=8, frameon=False)
    fig.suptitle(f"Caja {nodo}: cortes por niveles, vistos desde el frente (mm; medidas nominales)", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    destino = RENDERS / f"niveles_{nodo}.png"
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return destino
