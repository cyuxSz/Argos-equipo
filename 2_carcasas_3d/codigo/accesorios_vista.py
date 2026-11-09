"""Cortes de los accesorios armados (capuchon LDR y portas MC-38) con sus sensores adentro, y la ruta del cable
hasta la estacion. Salida: cad/renders/accesorios_conexion.png

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/accesorios_vista.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from build123d import Plane  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import escenas  # noqa: E402
from niveles import caras, pintar  # noqa: E402

COLOR = {"ldr_capuchon": "#2a2d2b", "ldr_difusor": "#cfe0ee", "ldr_ldr": "#d4a017", "ldr_cable": "#8a3b2e",
         "ldr_soporte": "#6b706d", "mc38_calza": "#b9c2bb", "mc38_porta_sensor": "#c9cec9",
         "mc38_porta_iman": "#c9cec9", "mc38_cuerpo_sensor": "#f7f7f2", "mc38_cuerpo_iman": "#f7f7f2"}
NOTA = dict(fontsize=7.5, va="top", color="#333")


def corte(ax, piezas, prefijo, x):
    for k, s in piezas.items():
        if k.startswith(prefijo):
            for cara in caras(s, Plane.YZ.offset(x)):
                pintar(ax, cara, COLOR[k], (2, 1), borde="#222", lw=0.5)
    ax.set_aspect("equal")
    ax.axis("off")


def caja(ax, x, y, w, h, texto, color="#eef1ee"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02", fc=color, ec="#333", lw=0.8))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=7.5)


def ruta(ax, y, sensor, pieza, alivio_pieza, largo):
    """Esquema (sin escala) de la ruta del cable: sensor en su pieza -> fijaciones -> estacion -> protoboard."""
    caja(ax, 0.00, y, 0.17, 0.16, f"{sensor}\nen su {pieza}", "#f7f7f2")
    caja(ax, 0.72, y - 0.02, 0.27, 0.20, "Estación\n(caja impresa)", "#c9cec9")
    ax.plot([0.17, 0.72], [y + 0.08, y + 0.08], color="#8a3b2e", lw=2.2)
    for xc in (0.30, 0.42, 0.54):
        ax.plot([xc, xc], [y + 0.05, y + 0.11], color="#333", lw=1.2)
    ax.text(0.42, y + 0.15, f"cable de 2 hilos, {largo}\nfijo a la pared cada 20–30 cm (grapas o canaleta adhesiva)",
            ha="center", fontsize=7, color="#333")
    ax.text(0.17, y - 0.015, alivio_pieza, fontsize=6.8, va="top", color="#333")
    ax.text(0.72, y - 0.035, "entra por un agujero de Ø5.2 mm (abajo);\nadentro, un cincho en 2 ranuras evita\n"
            "que un tirón llegue a la protoboard;\nluego terminal Dupont macho en su orificio", fontsize=6.8, va="top",
            color="#333")


def main():
    p = escenas.accesorios()
    fig = plt.figure(figsize=(13, 9.6))
    g = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], width_ratios=[1, 1.25])
    a1, a2, a3 = fig.add_subplot(g[0, 0]), fig.add_subplot(g[0, 1]), fig.add_subplot(g[1, :])
    # --- capuchon LDR (grupo en x = -55) ---
    corte(a1, p, "ldr_", escenas.GRUPO_X["ldr"])
    a1.set_title("Capuchón de la LDR cortado por su eje", fontsize=10)
    a1.text(0.0, 0.99, "Luz de la lámpara: entra solo por la visera\ny la ventana de Ø4.5 mm, tras el difusor (azul)",
            transform=a1.transAxes, **NOTA)
    a1.text(0.0, 0.75, "LDR (amarillo) apoyada en un\nasiento cónico: no se mueve", transform=a1.transAxes, **NOTA)
    a1.text(0.0, 0.17, "Cable (rojo) con termocontraíble en las\nsoldaduras; un cincho por el túnel de\nla cola lo sujeta",
            transform=a1.transAxes, **NOTA)
    a1.text(0.74, 0.14, "Horquilla (gris): con\ntornillos o cinchos a\nla lámpara. El capuchón\n"
            "gira en un tornillo M3\n(fuera del corte)", transform=a1.transAxes, **NOTA)
    # --- portas MC-38 (grupo en x = +45); en esta vista el iman queda a la izquierda ---
    corte(a2, p, "mc38_", escenas.GRUPO_X["mc38"])
    a2.set_title("Guías del sensor de puerta (MC-38) cortadas por el centro", fontsize=10)
    a2.text(0.0, 0.99, "Hoja de la puerta: porta-imán.\nEl imán no lleva cable", transform=a2.transAxes, **NOTA)
    a2.text(0.58, 0.99, "Marco: porta-sensor sobre calza de 2 mm.\nEl reed (blanco) entra con clic bajo 4 topes",
            transform=a2.transAxes, **NOTA)
    a2.text(0.22, 0.12, "≈ 20 mm cuerpo a cuerpo con la puerta cerrada\n(distancia de cierre POR CONFIRMAR con el MC-38 real)",
            transform=a2.transAxes, **NOTA)
    # --- ruta del cable (esquema, sin escala) ---
    a3.set_xlim(-0.01, 1.0)
    a3.set_ylim(0, 1)
    a3.axis("off")
    a3.set_title("Cómo llega cada sensor a su estación (esquema sin escala)", fontsize=10)
    ruta(a3, 0.62, "LDR", "capuchón", "cincho en el túnel de la cola", "largo POR CONFIRMAR")
    ruta(a3, 0.12, "Reed MC-38", "guía del marco", "salida lateral de la guía\n(propuesta: agregar un anclaje para cincho)",
         "≈ 30 cm de fábrica; se empalma si falta")
    fig.suptitle("Sensores fuera de la caja: cómo quedan adentro de sus piezas y cómo se conectan (medidas nominales)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    destino = Path(__file__).resolve().parent / "renders" / "accesorios_conexion.png"
    fig.savefig(destino, dpi=160, bbox_inches="tight")
    print("ok", destino.name)


if __name__ == "__main__":
    main()
