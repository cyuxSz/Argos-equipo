"""Modelo 3D del cuarto de incubacion con las cajas instaladas, plano 2D y tabla de cables.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib --with pyvista python cad/cuarto.py
Salida:
  cad/exports/cuarto/cuarto.step y cuarto.glb   (cuarto + cajas, mm, z arriba)
  cad/renders/cuarto_iso.png, cuarto_zoom_*.png  (render 3D)
  cad/renders/cuarto_plano.png / .svg            (planta y alzado de la pared del fondo con rutas de cable)
  cad/exports/cuarto/cables.json                 (largos calculados)

Ejes del cuarto: x = a lo largo de los anaqueles (0 = pared del fondo, con los contactos C7),
y = a lo ancho (0 = pared del anaquel A), z = altura desde el piso. Unidades: mm.
Medidas de los encargados (5-nov): anaquel 1840 x 483 x 1830, pasillo 1295, ~340 entre luminaria y plataforma,
contacto central a ~1500 de altura. Lo demas es SUPUESTO y esta en SUP (cambiar ahi y volver a correr).
"""
import json
import math
from pathlib import Path

from build123d import Align, Box, Color, Compound, Cylinder, Location, Plane, Pos, Rot, Vector, import_step, export_step

RAIZ = Path(__file__).resolve().parent
EXPORTS = RAIZ / "exports"
SALIDA = EXPORTS / "cuarto"
RENDERS = RAIZ / "renders"

# ---------------- medidas de los encargados ----------------
AN_L, AN_F, AN_H = 1840.0, 483.0, 1830.0      # anaquel: largo, fondo, alto
PASILLO = 1295.0
LUM_A_PLAT = 340.0                            # luminaria -> plataforma
Z_CONTACTO = 1500.0

# ---------------- supuestos [POR CONFIRMAR] ----------------
SUP = {
    "puerta_a_anaquel": 2500.0,      # punta de los anaqueles -> pared de la puerta (hay mesas, sillas y contactos)
    "contacto_puerta": (300.0, 300.0),   # en la pared de la puerta, del lado del anaquel B: (distancia al marco, altura)
    "puerta_ancho": 900.0, "puerta_alto": 2100.0,
    "puerta_bisagra": "y_min",       # la bisagra del lado del anaquel A; la chapa del lado de la estacion de entrada
    "techo": 2700.0,
    "minisplit": (800.0, 200.0, 300.0),          # ancho (y), fondo (x), alto (z)
    "minisplit_sobre_anaquel": 550.0,            # 400-700 mm por encima del anaquel (dato del usuario), pared del fondo
    "planchas_z": {1: 1800.0, 2: 1400.0, 3: 1000.0, 4: 600.0},   # cara superior de cada plancha (1 = arriba)
    "plancha_espesor": 30.0,
    "poste": 30.0,
    "lum_diam": 30.0, "lum_largo": 610.0,        # GLP24 = 24 in con 2 tubos (supuesto por el 24 del modelo)
    "lum_x": (AN_L * 0.25, AN_L * 0.75),         # 2 por plancha y anaquel = 12 (hoy 8-12, cambian)
}
DIAG = {"usb_holgura": 1.2}       # largo de cable = ruta x 1.2

Y_A = (0.0, AN_F)                               # anaquel A
Y_B = (AN_F + PASILLO, 2 * AN_F + PASILLO)      # anaquel B
ANCHO = Y_B[1]
X_FRENTE = AN_L + SUP["puerta_a_anaquel"]       # pared de la puerta
Y_PUERTA_C = (Y_A[1] + Y_B[0]) / 2              # puerta centrada en el pasillo
CONTACTO = Vector(0, Y_PUERTA_C, Z_CONTACTO)    # contacto central de la pared del fondo (a ~560-650 de cada anaquel)
CONTACTO_PUERTA = Vector(X_FRENTE, Y_PUERTA_C + SUP["puerta_ancho"] / 2 + SUP["contacto_puerta"][0],
                         SUP["contacto_puerta"][1])



def caja(x0, y0, z0, dx, dy, dz):
    return Pos(x0 + dx / 2, y0 + dy / 2, z0 + dz / 2) * Box(dx, dy, dz)


def anaquel(y0):
    s = SUP
    p = s["poste"]
    partes = [caja(x, y, 0, p, p, AN_H) for x in (0, AN_L - p) for y in (y0, y0 + AN_F - p)]
    partes += [caja(0, y0, z - s["plancha_espesor"], AN_L, AN_F, s["plancha_espesor"]) for z in s["planchas_z"].values()]
    return partes


def luminarias(y0):
    """Una luminaria por plancha util (2, 3, 4), colgada a 340 mm de la plataforma, centrada en el fondo."""
    s = SUP
    out = []
    for k in (2, 3, 4):
        z = s["planchas_z"][k] + LUM_A_PLAT
        for xc in s["lum_x"]:
            out.append(Pos(xc, y0 + AN_F / 2, z) * Rot(0, 90, 0) * Cylinder(s["lum_diam"] / 2, s["lum_largo"] / 2))
    return out


def frascos(y0):
    out = []
    for k in (2, 3, 4):
        z = SUP["planchas_z"][k]
        for i in range(10):
            x = 120 + i * 170
            for j, fy in enumerate((0.3, 0.7)):
                out.append(Pos(x + j * 60, y0 + AN_F * fy, z) * Cylinder(35, 110, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return out


def en_superficie(forma, origen, normal):
    """Coloca una caja en coordenadas del nodo (x ancho, y arriba, z hacia afuera, z = 0 espalda) sobre una
    superficie vertical con normal hacia afuera; origen = centro de la espalda de la caja en el cuarto."""
    n = Vector(*normal)
    xdir = Vector(0, 0, 1).cross(n)
    bb = forma.bounding_box()
    centrar = Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z)
    return Location(Plane(origin=Vector(*origen), x_dir=xdir, z_dir=n)) * (centrar * forma)


# ---------------- ubicacion de las cajas ----------------
# (archivo STEP, centro de la espalda, normal hacia afuera, texto)
Z_DHT = SUP["planchas_z"][3] + 100              # altura de los frascos de la plancha 3
CAJAS = {
    "dht": ("nodo_dht_ensamble.step", (AN_L / 2, Y_B[0], Z_DHT), (0, -1, 0),
            "Anaquel B, cara del pasillo, a media longitud, altura de frascos de la plancha 3"),
    "anaquel": ("nodo_anaquel_ensamble.step", (260, Y_A[1], SUP["planchas_z"][2] - 90), (0, 1, 0),
                "Anaquel A, bajo el borde de la plancha 2, cerca del fondo (acel fijo al anaquel; LDR a la luminaria de la plancha 3)"),
    "entrada": ("nodo_entrada_ensamble.step", (X_FRENTE, Y_PUERTA_C + SUP["puerta_ancho"] / 2 + 160, 1500), (-1, 0, 0),
                "Pared de la puerta, junto a la chapa; el PIR mira al cuarto y el MC-38 va al marco"),
    "potencia": ("nodo_potencia_ensamble.step", (560, Y_A[1], SUP["planchas_z"][2] - 110), (0, 1, 0),
                 "Opcional: junto a la estacion del anaquel"),
}

# puntos de llegada de cada cable
LDR = Vector(SUP["lum_x"][0] - SUP["lum_largo"] / 2 + 120, Y_A[1] - 60, SUP["planchas_z"][3] + LUM_A_PLAT - 25)
MC38_MARCO = Vector(X_FRENTE, Y_PUERTA_C + SUP["puerta_ancho"] / 2 + 20, 1500)
LUM_P = {k: (Vector(SUP["lum_x"][0], Y_A[1] / 2, SUP["planchas_z"][k] + LUM_A_PLAT),
             Vector(SUP["lum_x"][0], (Y_B[0] + Y_B[1]) / 2, SUP["planchas_z"][k] + LUM_A_PLAT)) for k in (2, 3, 4)}


def ruta(*pts):
    """Ruta ortogonal (por paredes y postes) entre puntos: suma de |dx| + |dy| + |dz| de cada tramo."""
    return sum(abs(b.X - a.X) + abs(b.Y - a.Y) + abs(b.Z - a.Z) for a, b in zip(pts, pts[1:]))


def cables():
    c = CAJAS
    dht = Vector(*c["dht"][1]); an = Vector(*c["anaquel"][1]); en = Vector(*c["entrada"][1]); po = Vector(*c["potencia"][1])
    esquina_b = Vector(0, Y_B[0], Z_CONTACTO)
    filas = [
        ("Fuente 5 V -> estacion del anaquel (USB-C)", ruta(CONTACTO, Vector(0, Y_A[1], Z_CONTACTO), an), "USB-C"),
        ("Fuente 5 V -> dht (micro-USB)", ruta(CONTACTO, esquina_b, Vector(dht.X, Y_B[0], Z_CONTACTO), dht), "micro-USB"),
        ("Fuente 5 V (contacto junto a la puerta) -> estacion de entrada (USB-C)",
         ruta(CONTACTO_PUERTA, Vector(X_FRENTE, en.Y, CONTACTO_PUERTA.Z), en), "USB-C"),
        ("LDR (capuchon) -> estacion del anaquel", ruta(an, Vector(an.X, an.Y, LDR.Z), LDR), "2 hilos"),
        ("MC-38 (marco) -> estacion de entrada", ruta(en, MC38_MARCO), "2 hilos"),
        ("Opcional: senal estacion -> caja de potencia", ruta(an, po), "6 hilos Dupont"),
        ("Opcional: PARED -> caja de potencia", ruta(CONTACTO, Vector(0, Y_A[1], Z_CONTACTO), po), "clavija 127 V"),
    ]
    for k in (2, 3, 4):
        a, b = LUM_P[k]
        filas.append((f"Opcional: P{k} -> luminarias plancha {k}, anaquel A", ruta(po, Vector(po.X, po.Y, a.Z), a), "extension 127 V"))
        filas.append((f"Opcional: P{k} -> luminarias plancha {k}, anaquel B (cruza por arriba)",
                      ruta(po, Vector(po.X, Y_A[1], AN_H + 50), Vector(po.X, Y_B[0], AN_H + 50), b), "extension 127 V"))
    return [{"cable": n, "ruta_cm": round(r / 10), "comprar_cm": round(r * DIAG["usb_holgura"] / 10), "tipo": t}
            for n, r, t in filas]


def escena():
    s = SUP
    grupos = {}
    grupos["piso"] = [caja(0, 0, -20, X_FRENTE, ANCHO, 20)]
    # paredes: fondo (x=0), lado A (y=0) y la de la puerta con su hueco (se dibujan transparentes)
    y1, y2 = Y_PUERTA_C - s["puerta_ancho"] / 2, Y_PUERTA_C + s["puerta_ancho"] / 2
    grupos["paredes"] = [caja(-60, 0, 0, 60, ANCHO, s["techo"]), caja(0, -60, 0, X_FRENTE, 60, s["techo"]),
                         caja(X_FRENTE, 0, 0, 60, y1, s["techo"]), caja(X_FRENTE, y2, 0, 60, ANCHO - y2, s["techo"]),
                         caja(X_FRENTE, y1, s["puerta_alto"], 60, y2 - y1, s["techo"] - s["puerta_alto"])]
    grupos["puerta"] = [caja(X_FRENTE + 10, y1, 0, 40, y2 - y1, s["puerta_alto"])]
    grupos["anaqueles"] = anaquel(Y_A[0]) + anaquel(Y_B[0])
    grupos["luminarias"] = luminarias(Y_A[0]) + luminarias(Y_B[0])
    grupos["frascos"] = frascos(Y_A[0]) + frascos(Y_B[0])
    mw, mf, mh = s["minisplit"]
    grupos["minisplit"] = [caja(0, Y_PUERTA_C - mw / 2, AN_H + s["minisplit_sobre_anaquel"], mf, mw, mh)]
    grupos["contactos"] = [caja(0, CONTACTO.Y + dy - 35, CONTACTO.Z - 60, 15, 70, 120) for dy in (-200, 0, 200)]
    grupos["contactos"].append(caja(X_FRENTE - 15, CONTACTO_PUERTA.Y - 35, CONTACTO_PUERTA.Z - 60, 15, 70, 120))
    for nombre, (archivo, origen, normal, _) in CAJAS.items():
        grupos[f"caja_{nombre}"] = [en_superficie(import_step(str(EXPORTS / archivo)), origen, normal)]
    grupos["ldr"] = [Pos(LDR) * Box(30, 30, 40)]
    grupos["mc38"] = [Pos(MC38_MARCO) * Box(30, 15, 60)]
    return grupos


COLORES = {"piso": "#d9d9d9", "paredes": "#f2efe9", "puerta": "#8a6d4b", "anaqueles": "#9aa3ab",
           "luminarias": "#ff6b6b", "frascos": "#bfe3c4", "minisplit": "#ffffff", "contactos": "#444444", 
           "caja_dht": "#1f77b4", "caja_anaquel": "#2ca02c", "caja_entrada": "#ff7f0e", "caja_potencia": "#9467bd",
           "ldr": "#2ca02c", "mc38": "#ff7f0e"}


def exportar(grupos):
    SALIDA.mkdir(parents=True, exist_ok=True)
    hijos = []
    for g, partes in grupos.items():
        comp = Compound(children=partes, label=g)
        comp.color = Color(COLORES[g])
        hijos.append(comp)
    todo = Compound(children=hijos, label="cuarto")
    export_step(todo, str(SALIDA / "cuarto.step"))
    try:
        from build123d import export_gltf
        export_gltf(todo, str(SALIDA / "cuarto.glb"), binary=True, linear_deflection=1.0, angular_deflection=0.5)
    except Exception as e:  # el GLB es extra
        print("GLB no exportado:", e)


def mallas(grupos):
    import numpy as np
    import pyvista as pv
    out = {}
    for g, partes in grupos.items():
        ms = []
        for p in partes:
            for sol in (p.solids() or [p]):
                v, t = sol.tessellate(2.0, 0.5)
                if not t:
                    continue
                pts = np.array([[q.X, q.Y, q.Z] for q in v])
                caras = np.hstack([[3, *tri] for tri in t])
                ms.append(pv.PolyData(pts, caras))
        out[g] = pv.merge(ms) if len(ms) > 1 else ms[0]
    return out


def render(grupos):
    import pyvista as pv
    RENDERS.mkdir(exist_ok=True)
    m = mallas(grupos)

    def toma(nombre, camara, ocultar=(), opac_paredes=0.12, tam=(1600, 1100)):
        pl = pv.Plotter(off_screen=True, window_size=tam)
        pl.set_background("white")
        for g, malla in m.items():
            if g in ocultar:
                continue
            op = opac_paredes if g == "paredes" else (0.5 if g == "frascos" else 1.0)
            pl.add_mesh(malla, color=COLORES[g], opacity=op, smooth_shading=False, show_edges=False)
        pl.camera_position = camara
        pl.enable_eye_dome_lighting() if False else None
        pl.screenshot(str(RENDERS / f"cuarto_{nombre}.png"))
        pl.close()

    c = Vector(X_FRENTE / 2, ANCHO / 2, 1200)
    toma("iso", [(X_FRENTE + 2200, -2600, 4600), (c.X, c.Y, c.Z), (0, 0, 1)])
    toma("desde_puerta", [(X_FRENTE - 300, Y_PUERTA_C + 200, 1700), (0, Y_PUERTA_C, 1100), (0, 0, 1)],
         ocultar=("paredes", "puerta"))
    for nombre in CAJAS:
        o = Vector(*CAJAS[nombre][1]); n = Vector(*CAJAS[nombre][2])
        ojo = o + n * 900 + Vector(250, 250, 250) - Vector(0, 0, 0)
        if nombre == "entrada":
            ojo = o + n * 1100 + Vector(0, -350, 250)
        toma(f"zoom_{nombre}", [(ojo.X, ojo.Y, ojo.Z), (o.X, o.Y, o.Z), (0, 0, 1)],
             ocultar=("paredes",) if nombre != "entrada" else (), opac_paredes=1.0, tam=(1100, 850))


def plano(filas):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Arc

    s = SUP
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(20, 8.5), gridspec_kw={"width_ratios": [1.7, 1]})
    # ---- planta (x hacia la derecha, y hacia arriba) ----
    ax.add_patch(Rectangle((0, 0), X_FRENTE, ANCHO, fill=False, lw=2))
    for y0, t in ((Y_A[0], "Anaquel A"), (Y_B[0], "Anaquel B")):
        ax.add_patch(Rectangle((0, y0), AN_L, AN_F, fc="#dfe3e6", ec="#555"))
        ax.text(AN_L / 2, y0 + AN_F / 2, f"{t}\n184 x 48.3 cm, 3 niveles utiles", ha="center", va="center", fontsize=9)
    y1, y2 = Y_PUERTA_C - s["puerta_ancho"] / 2, Y_PUERTA_C + s["puerta_ancho"] / 2
    ax.plot([X_FRENTE, X_FRENTE], [y1, y2], color="white", lw=4)
    ax.add_patch(Arc((X_FRENTE, y1), 2 * (y2 - y1), 2 * (y2 - y1), theta1=90, theta2=180, ls="--", color="#8a6d4b"))
    ax.plot([X_FRENTE, X_FRENTE - (y2 - y1)], [y1, y1], color="#8a6d4b", lw=2)
    ax.text(X_FRENTE + 40, Y_PUERTA_C, "Puerta\n[ancho y giro\nPOR CONFIRMAR]", fontsize=8, va="center")
    mw = s["minisplit"][0]
    ax.add_patch(Rectangle((0, Y_PUERTA_C - mw / 2), s["minisplit"][1], mw, fc="#ffffff", ec="#1f4e79", hatch="//"))
    ax.text(230, Y_PUERTA_C + mw / 2 - 40, f"Minisplit (arriba, ~{(AN_H + s['minisplit_sobre_anaquel']) / 10:.0f} cm)",
            fontsize=8, color="#1f4e79", va="top")
    ax.plot([0], [CONTACTO.Y], marker="s", color="k", ms=9)
    ax.plot([X_FRENTE], [CONTACTO_PUERTA.Y], marker="s", color="k", ms=9)
    ax.text(X_FRENTE + 40, CONTACTO_PUERTA.Y + 60, "Contacto\n(a 30 cm)\n[POR CONFIRMAR]", fontsize=8)
    ax.text((AN_L + X_FRENTE) / 2, ANCHO / 2 - 300, "Zona libre\n(mesas, sillas: las ubica el equipo)", ha="center",
            fontsize=8.5, color="#777")
    ax.text(-40, CONTACTO.Y, "Contactos C7\n(a 150 cm)", fontsize=8, ha="right", va="center")
    marcas = {"dht": "#1f77b4", "anaquel": "#2ca02c", "entrada": "#ff7f0e", "potencia": "#9467bd"}
    nombres = {"dht": "dht", "anaquel": "Estacion anaquel\n(acel + luz)", "entrada": "Estacion entrada\n(pir + puerta)",
               "potencia": "Caja potencia\n(opcional)"}
    texto_en = {"dht": (700, Y_B[0] - 250), "anaquel": (250, Y_A[1] + 330), "potencia": (800, Y_A[1] + 200),
                "entrada": (X_FRENTE - 650, Y_B[0] - 330)}
    for k, (_, o, n, _) in CAJAS.items():
        ax.plot(o[0], o[1], marker="o", ms=11, color=marcas[k], mec="k")
        ax.annotate(nombres[k], (o[0], o[1]), xytext=texto_en[k],
                    fontsize=8.5, color=marcas[k], arrowprops=dict(arrowstyle="-", color=marcas[k]))
    # rutas de cable (planta)
    an, dht, en = (Vector(*CAJAS[k][1]) for k in ("anaquel", "dht", "entrada"))
    rut = [([0, 0, an.X], [CONTACTO.Y, Y_A[1], Y_A[1]], "#2ca02c"),
           ([0, 0, dht.X], [CONTACTO.Y, Y_B[0], Y_B[0]], "#1f77b4"),
           ([X_FRENTE - 10, X_FRENTE - 10], [CONTACTO_PUERTA.Y, en.Y], "#ff7f0e")]
    for xs, ys, col in rut:
        ax.plot(xs, ys, color=col, lw=1.4, ls=":")
    # cotas
    def cota_h(x1, x2, y, txt):
        ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<->", color="#b03030", lw=0.8))
        ax.text((x1 + x2) / 2, y + 25, txt, ha="center", fontsize=8, color="#b03030")

    def cota_v(y1_, y2_, x, txt):
        ax.annotate("", (x, y1_), (x, y2_), arrowprops=dict(arrowstyle="<->", color="#b03030", lw=0.8))
        ax.text(x + 25, (y1_ + y2_) / 2, txt, rotation=90, va="center", fontsize=8, color="#b03030")
    cota_h(0, AN_L, -150, "184 cm")
    cota_h(AN_L, X_FRENTE, -150, f"~{s['puerta_a_anaquel'] / 10:.0f} cm [POR CONFIRMAR]")
    cota_v(Y_A[1], Y_B[0], AN_L + 120, "Pasillo 129.5 cm")
    cota_v(0, Y_A[1], -150, "48.3")
    cota_v(Y_B[0], Y_B[1], -150, "48.3")
    ax.set_xlim(-450, X_FRENTE + 450); ax.set_ylim(-420, ANCHO + 150)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Planta (vista desde arriba). Puntos = cajas; punteado = cable de 5 V", fontsize=11)

    # ---- alzado lateral del anaquel A (cara del pasillo) ----
    bx.add_patch(Rectangle((0, 0), AN_L, AN_H, fill=False, ec="#555"))
    for k, z in s["planchas_z"].items():
        bx.add_patch(Rectangle((0, z - s["plancha_espesor"]), AN_L, s["plancha_espesor"], fc="#9aa3ab"))
        bx.text(-40, z - 15, f"P{k}\n{z / 10:.0f} cm", ha="right", va="center", fontsize=8)
        if k > 1:
            for xc in s["lum_x"]:
                bx.plot([xc - s["lum_largo"] / 2, xc + s["lum_largo"] / 2], [z + LUM_A_PLAT] * 2, color="#ff6b6b", lw=3)
    bx.text(AN_L + 30, s["planchas_z"][2] + LUM_A_PLAT, "luminaria\n(34 cm sobre\nla plataforma)", fontsize=7.5,
            color="#c0392b", va="center")
    for k in ("anaquel", "potencia"):
        o = CAJAS[k][1]
        w, h = (202, 80) if k == "anaquel" else (125, 143)
        bx.add_patch(Rectangle((o[0] - w / 2, o[2] - h / 2), w, h, fc=marcas[k], ec="k"))
    bx.plot(LDR.X, LDR.Z, marker="v", ms=9, color="#2ca02c", mec="k")
    bx.text(LDR.X - 20, LDR.Z + 50, "LDR", fontsize=8, ha="right")
    bx.axhline(Z_CONTACTO, color="k", ls="--", lw=0.7)
    bx.text(AN_L - 20, Z_CONTACTO + 20, "altura de los contactos 150 cm", fontsize=7.5, ha="right")
    bx.set_xlim(-350, AN_L + 300); bx.set_ylim(-50, AN_H + 150)
    bx.set_aspect("equal"); bx.axis("off")
    bx.set_title("Anaquel A visto desde el pasillo: estacion del anaquel y caja de potencia", fontsize=11)
    fig.text(0.01, 0.01, "Supuestos [POR CONFIRMAR]: altura de las planchas, ancho y giro de la puerta, minisplit en la pared "
             "del fondo, anaqueles pegados a las paredes, distancia a la puerta y contacto junto a la puerta. Cambiar SUP en cad/cuarto.py y volver a correr.", fontsize=8)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(RENDERS / f"cuarto_plano.{ext}", dpi=170)
    plt.close(fig)


def main():
    filas = cables()
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "cables.json").write_text(json.dumps({"supuestos": SUP, "cajas": {k: v[3] for k, v in CAJAS.items()},
                                                     "cables": filas}, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in filas:
        print(f"{f['ruta_cm']:>5} cm  -> comprar {f['comprar_cm']:>4} cm  {f['tipo']:<16} {f['cable']}")
    plano(filas)
    grupos = escena()
    exportar(grupos)
    render(grupos)
    print("listo:", SALIDA, RENDERS)


if __name__ == "__main__":
    main()
