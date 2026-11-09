"""Argos: caja de potencia del fotoperiodo (5-nov). Módulo de 4 relés + fusible + clemas; 127 V.

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/caja_potencia.py

Va fija al poste del anaquel junto a la estacion del anaquel (cinchos o M3 por las orejas laterales), a la
altura del contacto central (~150 cm). No lleva protoboard: la manda el nodo luz por un cable de 6 hilos.
Redes en hardware/breadboard/layouts.py (CAJA_POTENCIA); medidas nominales en cad/medidas.json
("caja_potencia"): MEDIR el modulo de reles, el cable de las extensiones y el portafusible antes de imprimir.

Marco local (igual que nodos.py): x = ancho, y = alto (arriba), z = profundidad (z = 0 espalda).
Zonas (de abajo hacia arriba): baja tension (tira de pines y salida del cable de senal por el piso) |
modulo de reles (clemas de los contactos hacia arriba) | 127 V (regleta de neutro/tierra, portafusible y las
4 entradas de cable por el techo: PARED, P2, P3, P4). Una costilla separa la zona de baja tension.
"""
import sys
from pathlib import Path

from build123d import Axis, Box, Compound, Plane, Pos, Rectangle, Rot, chamfer, extrude, fillet

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nodos  # noqa: E402
from nodos import DIS, Gemelo, caja, caja_c, cil, gota_x, med, texto  # noqa: E402

M = lambda k: med("caja_potencia", k)  # noqa: E731


def gota_y(xc, yc, zc, d, largo):
    """Agujero a lo largo de y (en el techo o el piso) con punta a 45 grados: sin soportes con la espalda en la cama."""
    return Pos(xc, yc, zc) * Rot(0, 0, 90) * Pos(-xc, -yc, -zc) * gota_x(xc, yc, zc, d, largo)


def ancla_cincho(xc, yc, ancho=16.0, alto=5.0):
    """Bloque en el piso con tunel a lo largo de x para un cincho que abraza el cable de encima (alivio de tension)."""
    b = caja_c(xc, yc, DIS["pared"], ancho, 5.0, alto)
    return b - caja_c(xc, yc, DIS["pared"] + 1.2, ancho + 1, 3.0, 2.0)


def caja_potencia():
    p, hg, ch = DIS["pared"], DIS["holgura"], DIS["chaflan"]
    pcb_l, pcb_a, pcb_e = M("modulo_rele_pcb")
    ag_x, ag_y, ag_d = M("modulo_rele_agujeros")
    rele_h = M("modulo_rele_alto")
    born_f, born_h = M("modulo_rele_bornes")
    tira_f, tira_h = M("modulo_rele_tira")
    d_cab = M("cable_extension")
    fus_l, fus_d = M("portafusible_linea")
    reg_l, reg_f, reg_h = M("regleta_clemas")
    d_sen = M("cable_senal")

    # --- distribucion vertical (interior desde y = p) ---
    zona_bt, zona_hv = 18.0, 66.0
    Wi = pcb_l + 2 * 10.0
    W = Wi + 2 * p
    Hi = zona_bt + pcb_a + zona_hv
    H = Hi + 2 * p
    Db, t = 38.0, DIS["tapa"]
    D = Db + t
    y_pcb = p + zona_bt                       # borde inferior de la PCB (tira de pines)
    z_pcb = p + 6.0                           # alto de los postes
    y_reg = y_pcb + pcb_a + 14.0              # regleta: 14 mm para doblar los cables de las clemas
    y_fus = y_reg + reg_f + 6.0 + fus_d / 2   # eje del portafusible
    y_ancla = H - p - 7.5                     # anclas de los 4 cables de 127 V
    z_cab = p + 10.0                          # eje de los cables que entran por el techo
    x_cab = (-30.0, -10.0, 10.0, 30.0)        # PARED, P2, P3, P4
    rot_cab = ("PARED", "P2", "P3", "P4")

    # ═════ gemelo (bloques nominales) ═════
    g = Gemelo()
    yc_pcb = y_pcb + pcb_a / 2
    g.agregar("modulo_pcb", caja_c(0, yc_pcb, z_pcb, pcb_l, pcb_a, pcb_e), montado=True)
    z_s = z_pcb + pcb_e
    g.agregar("reles", caja_c(0, yc_pcb + 2.0, z_s, pcb_l - 6.0, 19.0, rele_h))
    g.agregar("bornes_contactos", caja_c(0, y_pcb + pcb_a - born_f / 2, z_s, pcb_l - 4.0, born_f, born_h), montado=True)
    g.agregar("tira_pines_dupont", caja_c(-pcb_l / 2 + 16.0, y_pcb + tira_f / 2, z_s, 26.0, tira_f, tira_h),
              montado=True)
    g.agregar("regleta_clemas", caja_c(0, y_reg + reg_f / 2, p, reg_l, reg_f, reg_h), montado=True)
    g.agregar("portafusible", Pos(0, y_fus, p + fus_d / 2) * Rot(0, 90, 0) * nodos.Cylinder(fus_d / 2, fus_l),
              montado=True)
    for x, nom in zip(x_cab, rot_cab):
        g.agregar(f"cable_{nom.lower()}", Pos(x, H - 6.0, z_cab) * Rot(90, 0, 0) * nodos.Cylinder(d_cab / 2, 12.0),
                  montado=True)
    g.agregar("cable_senal", Pos(-pcb_l / 2 + 16.0, 8.0, p + 12.0) * Rot(90, 0, 0) * nodos.Cylinder(d_sen / 2, 16.0),
              montado=True)

    # ═════ BASE ═════
    base = Box(W, H, Db, align=(nodos.C, nodos.MIN, nodos.MIN))
    base = chamfer(base.edges().filter_by(Axis.Z), ch)
    base = chamfer(base.edges().group_by(Axis.Z)[0], ch)
    base -= caja_c(0, H / 2, p, Wi, Hi, Db)

    # postes del modulo (M3 autorroscante en PETG: piloto de 2.8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * ag_x / 2, yc_pcb + sy * ag_y / 2
            base += cil(x, y, p, 6.0, z_pcb - p)
            base -= cil(x, y, p + 0.8, 2.8, z_pcb - p)

    # torretas de la tapa (M3 autorroscante, sin insertos)
    xt, mt = W / 2 - DIS["torreta_margen"], DIS["torreta_margen"]
    torretas = [(sx * xt, y) for sx in (-1, 1) for y in (mt, H - mt)]
    z_torre = Db - DIS["torreta_tapa"]
    for x, y in torretas:
        base += cil(x, y, p, DIS["torreta_d"], z_torre - p)
        base -= cil(x, y, z_torre - 10.0, 2.8, 10.01)

    # costilla de baja tension (con muesca para los Dupont de la tira de pines)
    lh = DIS["labio"][1]
    z_cost = Db - lh - 0.4
    base += caja(-Wi / 2, y_pcb - 1.6, p, Wi, 1.2, z_cost - p)
    base -= caja_c(-pcb_l / 2 + 16.0, y_pcb - 1.0, p + 9.0, 30.0, 2.0, z_cost)

    # 4 entradas de 127 V por el techo + anclas de cincho; salida del cable de senal por el piso
    for x in x_cab:
        base -= gota_y(x, H - p / 2, z_cab, d_cab + 0.6, p + 1)
        base += ancla_cincho(x, y_ancla)
    x_sen = -pcb_l / 2 + 16.0
    base -= gota_y(x_sen, p / 2, p + 12.0, d_sen + 1.4, p + 1)
    base += ancla_cincho(x_sen, p + 7.0, ancho=12.0)
    # regleta y portafusible: anclas de cincho a los lados
    for sx in (-1, 1):
        base += ancla_cincho(sx * (reg_l / 2 + 6.0), y_reg + reg_f / 2, ancho=8.0)
        base += ancla_cincho(sx * (fus_l / 2 + 6.0), y_fus, ancho=8.0)

    # ventilas pequenas (ranura de 1.6: no entra un dedo) a media altura de los reles
    r = DIS["ranura"]
    for y in (yc_pcb - 6, yc_pcb, yc_pcb + 6):
        for sx in (-1, 1):
            base -= caja_c(sx * (W / 2 - p / 2), y, 10, p + 1, r, Db - 18)

    # orejas laterales con ranura para M3 o cincho (al poste perforado del anaquel)
    ow, oh, oe = DIS["oreja"]
    for sx in (-1, 1):
        o = caja_c(sx * (W / 2 + oh / 2 - p), H / 2, 0, oh + p, ow + 10, oe)
        o = fillet(o.edges().filter_by(Axis.Z).group_by(Axis.X)[-1 if sx > 0 else 0], 4)
        base += o
        xr = sx * (W / 2 + oh / 2 - 1)
        base -= caja_c(xr, H / 2, -0.1, 3.4, 8.0, oe + 0.2)
        base -= cil(xr, H / 2 - 4, -0.1, 3.4, oe + 0.2)
        base -= cil(xr, H / 2 + 4, -0.1, 3.4, oe + 0.2)

    # ═════ TAPA ═════
    contorno = chamfer(Rectangle(W, H).vertices(), ch)
    tapa = Pos(0, H / 2, Db) * extrude(contorno, amount=t)
    tapa = chamfer(tapa.edges().group_by(Axis.Z)[-1], 1.2)
    lw = DIS["labio"][0]
    wi, hi = W - 2 * p - 2 * hg, H - 2 * p - 2 * hg
    labio = caja_c(0, H / 2, Db - lh, wi, hi, lh) - caja_c(0, H / 2, Db - lh - 0.1, wi - 2 * lw, hi - 2 * lw, lh + 0.2)
    for x, y in torretas:
        labio -= caja_c(x, y, Db - lh - 0.1, 12.0, 12.0, lh + 0.2)
    tapa += labio
    for x, y in torretas:
        tapa += cil(x, y, Db - DIS["torreta_tapa"], DIS["torreta_d"], DIS["torreta_tapa"])
        tapa -= cil(x, y, Db - DIS["torreta_tapa"] - 0.1, DIS["paso_m3"], DIS["torreta_tapa"] + t + 0.2)
        tapa -= cil(x, y, D - 1.6, 6.2, 1.7)                  # caja para la cabeza cilindrica M3
    frente = lambda x, y: Plane(origin=(x, y, D), z_dir=(0, 0, 1))  # noqa: E731
    hund = DIS["hundido"]
    try:
        tapa -= texto("127 V", 11.0, frente(0, H - 40.0), hund)
        tapa -= texto("LUZ · FOTOPERIODO", 4.5, frente(0, H - 54.0), hund)
        for x, nom in zip(x_cab, rot_cab):
            tapa -= texto(nom, 3.6, frente(x, H - 12.0), hund)
        tapa -= texto("SEÑAL 5 V", 3.6, frente(x_sen, 12.0), hund)
        tapa -= texto("Argos", 4.2, frente(18.0, 12.0), hund)
    except Exception as err:  # fuente no disponible
        print("aviso: texto omitido:", err)
    # raya bajo los rotulos de los cables: marca el lado de 127 V
    tapa -= caja_c(0, H - 20.0, D - hund, Wi - 10, 0.8, 1)

    return dict(nodo="potencia", H=H, W=W, D=D, Db=Db, gemelo=g, piezas={"base": base, "tapa": tapa}, montaje={},
                orientacion={"base": "espalda en la cama", "tapa": "frente en la cama"}, paso_pernos=0.0,
                notas={"zona_baja_tension": zona_bt, "zona_127v": zona_hv, "z_pcb": z_pcb}, torretas=torretas,
                y_pb_inf=y_pcb)


def main():
    n = caja_potencia()
    res = nodos.verificar(n)
    r = nodos.exportar(n, res)
    import vistas
    vistas.dibujar(n)
    malas = [h for h in res["holguras"] if not h["ok"]]
    print(f"potencia: envolvente {r['envolvente_mm']} mm; interferencias {len(res['interferencias'])}; "
          f"holguras < {DIS['holgura_min']} mm {len(malas)}; volumenes {res['volumenes']}")
    for i in res["interferencias"]:
        print("   interferencia", i)
    for h in malas:
        print("   holgura", h)
    sys.exit(1 if res["interferencias"] or malas else 0)


if __name__ == "__main__":
    main()
