"""Vista explosionada y escena en anaquel del nodo dht, y ensamble de los accesorios (renders y visor web).

Uso (desde la raiz):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/escenas.py

Escribe STEP en cad/exports/vista/ (girados: y del nodo -> z, como los demas de esa carpeta),
uno por grupo para poder colorearlos o mostrarlos por separado en el visor.
"""
from build123d import Compound, Cone, Pos, Rot, export_step

import nodos
from nodos import DIS, SALIDA, caja_c, cil, med

VISTA = SALIDA / "vista"
GRUPO_X = {"ldr": -55.0, "mc38": 45.0}   # posicion de cada grupo de accesorios en el visor

ELECTRONICA = ("protoboard", "nodemcu", "C1", "R1", "R3", "R4", "R5", "R6", "Q1", "dht22")
TAPA_DISP = ("oled", "oled_dupont", "led_verde", "led_verde_patas", "led_rojo", "led_rojo_patas",
             "boton", "boton_dupont", "buzzer", "buzzer_pcb", "buzzer_dupont")


def tornillo_m3x10(x, y, z_cabeza):
    """M3 x 10 cabeza plana avellanada a 90 grados; z_cabeza = cara de la cabeza."""
    return (Pos(x, y, z_cabeza - 1.7) * Cone(1.5, 3.0, 1.7, align=(nodos.C, nodos.C, nodos.MIN))
            + cil(x, y, z_cabeza - 10.0, 3.0, 8.3))


def guardar(nombre, partes):
    export_step(Rot(90, 0, 0) * Compound(children=list(partes)), str(VISTA / f"{nombre}.step"))


def explosionada(n):
    g = n["gemelo"].partes
    Db, D = n["Db"], n["D"]
    torretas = n["torretas"]
    z_ins = Db - DIS["torreta_tapa"]
    pasos = {"base": 0, "insertos": 25, "electronica": 45, "tapa_disp": 95, "tapa": 130, "embolo": 150,
             "tornillos": 180}
    guardar("explosionada_dht_base", [n["piezas"]["base"]])
    guardar("explosionada_dht_insertos",
            [Pos(0, 0, pasos["insertos"]) * cil(x, y, z_ins - 5.0, 4.6, 5.0) for x, y in torretas])
    guardar("explosionada_dht_electronica",
            [Pos(0, 0, pasos["electronica"]) * g[k][0] for k in g if k in ELECTRONICA or k.startswith("dupont_")])
    guardar("explosionada_dht_tapa_disp", [Pos(0, 0, pasos["tapa_disp"]) * g[k][0] for k in TAPA_DISP])
    guardar("explosionada_dht_tapa", [Pos(0, 0, pasos["tapa"]) * n["piezas"]["tapa"]])
    guardar("explosionada_dht_embolo", [Pos(0, 0, pasos["embolo"]) * n["piezas"]["embolo_boton"]])
    guardar("explosionada_dht_tornillos",
            [Pos(0, 0, pasos["tornillos"]) * tornillo_m3x10(x, y, D) for x, y in torretas])


def escena(n):
    """dht colgado de la pinza de anaquel en la repisa superior; frascos en la inferior."""
    H, paso = n["H"], n["paso_pernos"]
    e, t_an = 4.0, DIS["anaquel_espesor"] + 2 * DIS["holgura"]
    largo = paso + 22
    y_repisa_sup = largo / 2 - e                      # cara superior de la repisa (el gancho apoya ahi)
    dy_nodo = paso / 2 - (H + 10.0)                   # perno superior en el tope de su ranura
    nodo = [Pos(0, dy_nodo, e) * s for s in (n["piezas"]["base"], n["piezas"]["tapa"], n["piezas"]["embolo_boton"])]
    centro_nodo = dy_nodo + H / 2
    y_repisa_inf = centro_nodo - 55                   # frascos de ~110 mm centrados a la altura del nodo
    repisas = [caja_c(0, y_repisa_sup - t_an / 2 + 0.3, -320, 700, t_an - 0.6, 320),
               caja_c(0, y_repisa_inf - 9, -320, 700, 18, 320)]
    # las cajas de caja_c crecen en +z desde z0: repisas de z=-320 a 0 (frente en z = 0)
    poste = [caja_c(x, (y_repisa_inf - 200 + y_repisa_sup + 150) / 2, -330, 25, y_repisa_sup - y_repisa_inf + 350, 25)
             for x in (-350, 350)]
    lampara = [Pos(0, y_repisa_sup - t_an - 15, -150) * Rot(0, 90, 0) * nodos.Cylinder(12, 600)]
    frascos = []
    for i, x in enumerate((-230, -140, -50, 140, 230)):
        z = -70 - (i % 2) * 90
        frascos.append(Pos(x, y_repisa_inf, z) * Rot(-90, 0, 0) *
                       nodos.Cylinder(33, 95, align=(nodos.C, nodos.C, nodos.MIN)))
        frascos.append(Pos(x, y_repisa_inf + 95, z) * Rot(-90, 0, 0) *
                       nodos.Cylinder(35, 14, align=(nodos.C, nodos.C, nodos.MIN)))
    guardar("escena_dht_nodo", nodo)
    guardar("escena_dht_soporte", [n["montaje"]["soporte_anaquel"]])
    guardar("escena_dht_anaquel", repisas + poste)
    guardar("escena_dht_lampara", lampara)
    guardar("escena_dht_frascos", frascos)


def accesorios():
    """Ensambles de accesorios en coordenadas del visor (y arriba): LDR a la izquierda, MC-38 a la derecha."""
    acc = nodos.capuchon_ldr()["piezas"]
    T = nodos.sobre_horquilla(-20)              # mirando a +y, inclinado 20 grados hacia arriba
    gem = nodos.ldr_en_capuchon(largo_cable=25)
    piezas = {"ldr_capuchon": T * acc["capuchon_ldr"], "ldr_difusor": T * nodos.difusor_en_asiento(acc["difusor_ldr"]),
              "ldr_ldr": T * gem["ldr"], "ldr_cable": T * gem["cable"], "ldr_soporte": acc["soporte_ldr"]}
    # MC-38: porta-sensor y porta-iman encarados a 20 mm (cuerpo a cuerpo) y la calza de 2 mm bajo el sensor
    cs, ci = med("mc38", "cuerpo_sensor"), med("mc38", "cuerpo_iman") or med("mc38", "cuerpo_sensor")
    piso, gap = med("mc38", "porta")["piso"], 20.0
    e_calza = 2.0
    sep = cs[1] / 2 + gap + ci[1] / 2
    piezas.update({
        "mc38_calza": nodos.huella_mc38(cs, e_calza)[0],
        "mc38_porta_sensor": Pos(0, 0, e_calza) * nodos.porta_mc38(cs, "REED", cable=True),
        "mc38_cuerpo_sensor": Pos(0, 0, e_calza) * caja_c(0, 0, piso, *cs),
        "mc38_porta_iman": Pos(0, sep, 0) * Rot(0, 0, 180) * nodos.porta_mc38(ci, "IMAN", cable=False),
        "mc38_cuerpo_iman": Pos(0, sep, 0) * caja_c(0, 0, piso, *ci),
    })
    aY = Rot(-90, 0, 0)                          # z arriba -> y arriba
    return {k: Pos(GRUPO_X["ldr" if k.startswith("ldr") else "mc38"], 0, 0) * aY * s for k, s in piezas.items()}


if __name__ == "__main__":
    VISTA.mkdir(parents=True, exist_ok=True)
    dht = nodos.nodo_dht()
    explosionada(dht)
    escena(dht)
    print("ok")
