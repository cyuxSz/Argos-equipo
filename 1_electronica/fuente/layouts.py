"""Distribuciones en protoboard de 400 puntos por nodo (fuente de verdad del armado).

Orificios: 'a20' (fila, columna) o 'A_5V:3' (riel, junto a la columna 3).
Rieles: A_5V / A_GND junto a la fila a; J_3V3 / J_GND junto a la fila j.
Pines en CLAUDE.md §3. Todo lo fisico es nominal hasta verificarlo con las piezas reales.
"""
import re

# NodeMCU Amica, micro-USB hacia la columna 1 [POR CONFIRMAR con la serigrafia de la placa].
# Lado A0 (fila b) y lado D0-D8 (fila i), de la punta USB (col 1) a la antena (col 15).
NODEMCU_LADO_A = {1: "VIN", 2: "GND", 3: "RST", 4: "EN", 5: "3V3", 6: "GND", 7: "CLK", 8: "SD0",
                  9: "CMD", 10: "SD1", 11: "SD2", 12: "SD3", 13: "RSV", 14: "RSV", 15: "A0"}
NODEMCU_LADO_J = {1: "3V3", 2: "GND", 3: "TX", 4: "RX", 5: "D8", 6: "D7", 7: "D6", 8: "D5",
                  9: "GND", 10: "3V3", 11: "D4", 12: "D3", 13: "D2", 14: "D1", 15: "D0"}
# PCB de 49 mm: ~2 pasos sobresalen del lado USB y ~3.3 del lado antena (nominal).
# Las columnas 16-18 quedan bajo la antena: no usar filas b-i ahi.
# Los orificios libres a/j junto al NodeMCU solo reciben puentes de cable UTP: una carcasa Dupont
# (2.54 mm) choca con el borde de la PCB (26 mm nominal). Los Dupont van en columnas 19-30.
NODEMCU_CUERPO = {"columnas": (1, 18), "borde_usb": -1.0, "borde_antena": 18.3}

# ── rejilla de la protoboard (la usan protoboard.py, prompts.py y el gemelo de cad/nodos.py) ──
PASO = 2.54
# posicion transversal de filas y rieles, en pasos de 0.1"
FILA_X = {**{f: i for i, f in enumerate("abcde")}, **{f: 7 + i for i, f in enumerate("fghij")},
          "A_GND": -3.2, "A_5V": -2.2, "J_3V3": 13.2, "J_GND": 14.2}


def orificio(h):
    """'a20' -> ('a', 20); 'A_5V:3' -> ('A_5V', 3)."""
    if ":" in h:
        riel, col = h.split(":")
        return riel, int(col)
    return h[0], int(h[1:])


def mover(h, d):
    """Corre un orificio d columnas."""
    fila, col = orificio(h)
    return f"{fila}:{col + d}" if ":" in h else f"{fila}{col + d}"


def columnas(lay):
    return lay.get("columnas", 30)


def puntos(lay):
    return 400 if columnas(lay) == 30 else 830


def placas(lay):
    """NodeMCU de la distribucion: [{'nombre', 'col0'}]; por omision uno en la columna 1."""
    return lay.get("nodemcus", [{"nombre": "NodeMCU", "col0": 1}])


def P(de, a, color, nota, carril=None):
    d = {"de": de, "a": a, "color": color, "nota": nota}
    if carril is not None:
        d["carril"] = carril
    return d


def E(disp, pin, orificio, color, nota="", largo=None):
    d = {"disp": disp, "pin": pin, "orificio": orificio, "color": color, "nota": nota}
    if largo:
        d["largo"] = largo
    return d


def R(ref, valor, p1, p2, nota=""):
    return {"ref": ref, "tipo": "R", "valor": valor, "pines": {"1": p1, "2": p2}, "nota": nota}


ALIMENTACION = [
    P("a1", "A_5V:1", "rojo", "VIN (5 V del USB) → riel 5V"),
    P("a2", "A_GND:2", "negro", "GND → riel GND lado A"),
    P("j1", "J_3V3:1", "naranja", "3V3 → riel 3V3"),
    P("j2", "J_GND:2", "negro", "GND → riel GND lado J"),
]
C1 = {"ref": "C1", "tipo": "C", "valor": "220 µF / 16 V electrolítico",
      "pines": {"+": "A_5V:3", "-": "A_GND:3"},
      "nota": "**Polaridad:** pata larga (+) al riel 5V; franja (−) al riel GND"}
LEDS_COMP = [
    R("R5", "330 Ω", "g20", "d20", "Cruza el canal (filas g→d). LED verde"),
    R("R6", "330 Ω", "g22", "d22", "Cruza el canal (filas g→d). LED rojo"),
]
LEDS_PUENTES = [
    P("j6", "h20", "cafe", "D7 → columna 20 (LED verde), por fuera de la fila j", 11.40),
    P("j5", "h22", "morado", "D8 → columna 22 (LED rojo), por fuera de la fila j", 11.62),
]
LEDS_EXT = [
    E("LED_V", "A", "a20", "verde", "Ánodo (pata larga) del LED verde, en la tapa"),
    E("LED_V", "K", "A_GND:19", "negro", "Cátodo (pata corta, lado plano)"),
    E("LED_R", "A", "a22", "rojo", "Ánodo (pata larga) del LED rojo, en la tapa"),
    E("LED_R", "K", "A_GND:23", "negro", "Cátodo (pata corta, lado plano)"),
]
REDES_BASE = {
    "D7": {"NodeMCU.D7", "R5.1"},
    "LED_V": {"R5.2", "LED_V.A"},
    "D8": {"NodeMCU.D8", "R6.1"},
    "LED_R": {"R6.2", "LED_R.A"},
}

VERIF_DHT = """
Supuestos: USB entrega 5.0 V; el Amica pasa a VIN ≈ 4.7 V tras su diodo [medir]; GPIO del ESP8266 a 3.3 V,
corriente máx. recomendada ≈ 12 mA por pin.

| Punto | Cálculo | Resultado |
|---|---|---|
| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| Base de Q1 (D5, R3 = 1 kΩ) | (3.3 − 0.7) / 1 kΩ − 0.7 / 10 kΩ | ≈ 2.5 mA ✔ |
| Saturación de Q1 | I_C ≈ 30 mA; h_FE mín. 2N2222 ≈ 75 → I_B necesaria ≈ 0.4 mA | 2.5 mA da β forzada ≈ 12 → saturado ✔ (V_CE ≈ 0.1–0.3 V) |
| Buzzer | Entre VIN (≈ 4.7 V) y colector; KY-012 trabaja con 3.5–5.5 V | ✔ El GPIO nunca ve 5 V: solo maneja la base |
| R4 = 10 kΩ base–GND | Mantiene Q1 apagado mientras D5 flota en el arranque | ✔ Sin pitido al encender |
| DHT22 | Alimentado a 3V3 (rango 3.3–6 V); DATA con R1 = 10 kΩ a 3V3 | ✔ Señal de 3.3 V. Si el módulo ya trae pull-up, quedan ≈ 5 kΩ en paralelo: aceptable |
| D4 / GPIO2 en el arranque | Debe estar en alto: R1 (10 kΩ a 3V3) lo garantiza; el DHT22 en reposo deja la línea en alto | ✔ El LED azul de la placa parpadeará al leer el sensor (normal) |
| D8 / GPIO15 en el arranque | Debe estar en bajo: el NodeMCU trae pull-down en GPIO15; el LED con 330 Ω no lo sube | ✔ |
| OLED 2.42" SSD1309 | VCC a 3V3; sus pull-ups I²C (en el módulo) quedan a 3.3 V | ✔ Nunca alimentar la OLED a 5 V en este circuito (subiría SDA/SCL a 5 V) |
| Botón D6 | INPUT_PULLUP interno, botón a GND | ✔ Sin resistencia externa |
| Consumo 3V3 | ESP8266 pico ≈ 300–400 mA + OLED ≈ 20 mA + DHT22 ≈ 1.5 mA + LED ≈ 8 mA | ✔ Dentro del regulador del Amica (≈ 500–800 mA según modelo) |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V; amortigua picos del WiFi y del buzzer |
| Ninguna señal > 3.3 V en un GPIO | Sensores y OLED a 3V3; el único elemento a 5 V (buzzer) está del lado del colector | ✔ |

**Pendientes de verificar en físico:** pinout del 2N2222 (TO-92 suele ser E-B-C con la cara plana al
frente, pero hay variantes C-B-E); pinout del KY-012 (en muchos módulos "S" es el + del buzzer y el pin
central no se usa); orden de pines de la OLED (VCC-GND o GND-VCC según proveedor) y del módulo DHT22.
"""

DHT_BASE = dict(
    puentes=ALIMENTACION + LEDS_PUENTES + [
        P("j8", "h27", "blanco", "D5 → columna 27 (R3 hacia la base de Q1), por fuera de la fila j", 11.84),
        P("a26", "A_GND:26", "negro", "Emisor de Q1 → GND"),
        P("j7", "h21", "gris", "D6 → columna 21 (botón), por fuera de la fila j", 12.28),
    ],
    componentes=[C1] + LEDS_COMP + [
        R("R1", "10 kΩ", "j24", "J_3V3:24", "Pull-up de DATA. De pie (vertical) entre j24 y el riel 3V3"),
        R("R3", "1 kΩ", "g27", "d27", "Cruza el canal: de D5 a la base"),
        R("R4", "10 kΩ", "a27", "A_GND:27", "Base a GND. De pie entre a27 y el riel GND"),
        {"ref": "Q1", "tipo": "Q", "valor": "2N2222 (TO-92)", "pines": {"E": "b26", "B": "b27", "C": "b28"},
         "nota": "**Cara plana hacia la fila a; E-B-C de col. 26 a 28** [verificar pinout del lote]"},
    ],
    externos=LEDS_EXT + [
        E("Boton", "1", "j21", "gris", "Botón de silencio/pantalla (en la tapa)"),
        E("Boton", "2", "J_GND:7", "negro"),
        E("DHT22", "VCC", "J_3V3:25", "naranja", "Cámara inferior: cable más largo", "Dupont 20 cm"),
        E("DHT22", "DATA", "f24", "amarillo", "", "Dupont 20 cm"),
        E("DHT22", "GND", "J_GND:25", "negro", "", "Dupont 20 cm"),
        E("Buzzer", "+", "A_5V:30", "rojo", "KY-012: confirmar qué pin es + [POR CONFIRMAR]"),
        E("Buzzer", "-", "a28", "blanco", "Al colector de Q1 (conmutación del lado bajo)"),
    ],
)

REDES_DHT_COMUN = {
    **REDES_BASE,
    "5V": {"NodeMCU.VIN", "C1.+", "Buzzer.+"},
    "D5": {"NodeMCU.D5", "R3.1"},
    "BASE": {"R3.2", "R4.1", "Q1.B"},
    "COLECTOR": {"Q1.C", "Buzzer.-"},
    "D6": {"NodeMCU.D6", "Boton.1"},
}

LAYOUTS = {
    "nodo_dht": dict(
        titulo="dht (con OLED 2.42\")",
        intro="Variante adoptada: OLED SSD1309 2.42\" (versión I²C de 4 pines) en D1 (SCL) / D2 (SDA) y DATA del DHT22 en **D4 (GPIO2)**.",
        puentes=DHT_BASE["puentes"] + [
            P("j11", "h24", "amarillo", "D4 → columna 24 (DATA del DHT22), por fuera de la fila j", 12.06),
            P("j13", "h23", "verde", "D2/SDA → columna 23 (OLED), por fuera de la fila j", 12.50),
            P("j14", "h25", "azul", "D1/SCL → columna 25 (OLED), por fuera de la fila j", 12.72),
        ],
        componentes=DHT_BASE["componentes"],
        externos=DHT_BASE["externos"] + [
            E("OLED", "VCC", "J_3V3:12", "naranja", "Orden de pines según serigrafía [POR CONFIRMAR]"),
            E("OLED", "GND", "J_GND:12", "negro"),
            E("OLED", "SCL", "f25", "azul", "D1 llega por el puente j14 → h25"),
            E("OLED", "SDA", "f23", "verde", "D2 llega por el puente j13 → h23"),
        ],
        redes={
            **REDES_DHT_COMUN,
            "GND": {"NodeMCU.GND", "C1.-", "Q1.E", "R4.2", "LED_V.K", "LED_R.K", "Boton.2",
                    "OLED.GND", "DHT22.GND"},
            "3V3": {"NodeMCU.3V3", "R1.2", "OLED.VCC", "DHT22.VCC"},
            "SCL": {"NodeMCU.D1", "OLED.SCL"},
            "SDA": {"NodeMCU.D2", "OLED.SDA"},
            "DATA": {"NodeMCU.D4", "DHT22.DATA", "R1.1"},
        },
        verificacion=VERIF_DHT,
    ),
    "nodo_dht_sin_oled": dict(
        titulo="dht (sin OLED, respaldo)",
        intro="Respaldo si los encargados no autorizan la pantalla: DATA del DHT22 vuelve a **D2 (GPIO4)**, "
              "como en el diseño original. D1 y D4 quedan libres.",
        puentes=DHT_BASE["puentes"] + [P("j13", "h24", "amarillo", "D2 → columna 24 (DATA del DHT22), por fuera de la fila j", 12.06)],
        componentes=DHT_BASE["componentes"],
        externos=DHT_BASE["externos"],
        redes={
            **REDES_DHT_COMUN,
            "GND": {"NodeMCU.GND", "C1.-", "Q1.E", "R4.2", "LED_V.K", "LED_R.K", "Boton.2", "DHT22.GND"},
            "3V3": {"NodeMCU.3V3", "R1.2", "DHT22.VCC"},
            "DATA": {"NodeMCU.D2", "DHT22.DATA", "R1.1"},
        },
        verificacion=VERIF_DHT.replace("| D4 / GPIO2 en el arranque | Debe estar en alto: R1 (10 kΩ a 3V3) lo garantiza; el DHT22 en reposo deja la línea en alto | ✔ El LED azul de la placa parpadeará al leer el sensor (normal) |\n", "")
                                .replace("| OLED 2.42\" SSD1309 | VCC a 3V3; sus pull-ups I²C (en el módulo) quedan a 3.3 V | ✔ Nunca alimentar la OLED a 5 V en este circuito (subiría SDA/SCL a 5 V) |\n", ""),
    ),
}


# ═════════════════════════════════════════════════════════════════════════════
#  Nodos luz, pir, puerta y acel (Fase 5)
# ═════════════════════════════════════════════════════════════════════════════
def M(ref, valor, fila, col0, pines, nota=""):
    """Modulo con una tira de pines macho clavada en la protoboard (una columna por pin)."""
    return {"ref": ref, "tipo": "M", "valor": valor,
            "pines": {p: f"{fila}{col0 + i}" for i, p in enumerate(pines)}, "nota": nota}


VERIF_COMUN = """| LED verde (D7, 330 Ω) | (3.3 − 2.0…2.2 V) / 330 Ω | ≈ 3.3–3.9 mA ✔ (< 12 mA por GPIO) |
| LED rojo (D8, 330 Ω) | (3.3 − 1.8…2.0 V) / 330 Ω | ≈ 3.9–4.5 mA ✔ |
| D8 / GPIO15 en el arranque | Pull-down de la placa; el LED con 330 Ω no lo sube | ✔ |
| C1 | 220 µF / 16 V entre 5V y GND | ✔ 16 V > 5 V |
"""

REDES_COMUN = {**REDES_BASE, "5V": {"NodeMCU.VIN", "C1.+"}}

LAYOUTS["nodo_luz"] = dict(
    titulo="luz (fotorresistencia)",
    intro="Divisor: 3V3 → LDR → **A0** → R2 = 10 kΩ → GND. Más luz = más voltaje en A0.",
    puentes=ALIMENTACION + LEDS_PUENTES + [
        P("a15", "b25", "amarillo", "A0 → columna 25 (divisor), por fuera de la fila a", -0.7),
    ],
    componentes=[C1] + LEDS_COMP + [
        R("R2", "10 kΩ", "a25", "A_GND:25", "Del divisor a GND. De pie entre a25 y el riel GND. Valor final según "
          "docs/prueba_ldr.md (4.7–47 kΩ; no cambia pines)"),
    ],
    externos=LEDS_EXT + [
        E("LDR", "1", "c25", "amarillo", "LDR en su capuchón remoto (junto a la lámpara); cable de 2 hilos con "
          "terminal Dupont macho crimpado", "cable de la LDR"),
        E("LDR", "2", "J_3V3:25", "naranja", "Sin polaridad", "cable de la LDR"),
    ],
    redes={**REDES_COMUN,
           "A0": {"NodeMCU.A0", "R2.1", "LDR.1"},
           "3V3": {"NodeMCU.3V3", "LDR.2"},
           "GND": {"NodeMCU.GND", "C1.-", "R2.2", "LED_V.K", "LED_R.K"}},
    verificacion="""
| Punto | Cálculo | Resultado |
|---|---|---|
| A0 del NodeMCU | La placa trae un divisor 220 k / 100 k: acepta 0–3.3 V | ✔ El divisor LDR/10 k nunca supera 3.3 V |
| Corriente del divisor | 3.3 V / (R_LDR + 10 kΩ), con luz (R_LDR ≈ 1–5 kΩ) | ≈ 0.2–0.3 mA ✔ |
| Sensibilidad | R2 = 10 kΩ queda a la mitad del rango típico de una GL55xx con luz de interiores | R2 ≈ √(R_on × R_off) medidos en el capuchón (`docs/prueba_ldr.md`) [modelo de LDR POR CONFIRMAR] |
""" + VERIF_COMUN,
)

# Submódulo opcional (5-nov): misma distribucion que nodo_luz + entradas del módulo de 4 relés de la caja de
# potencia (docs/caja_potencia_luz.md). La version base de 3 cajas no lo lleva; solo se arma si da tiempo.
_LUZ = LAYOUTS["nodo_luz"]
LAYOUTS["nodo_luz_rele"] = dict(
    _LUZ,
    titulo="luz con relés (submódulo opcional del fotoperiodo)",
    intro=_LUZ["intro"] + " Submódulo opcional: **D1 / D2 / D5** mandan IN1 / IN2 / IN3 del módulo de 4 relés de "
          "la caja de potencia (activo en bajo: LOW = luz encendida). Un cable de 6 hilos sale de las columnas 27–30.",
    puentes=_LUZ["puentes"] + [
        P("j14", "h28", "azul", "D1 → columna 28 (IN1, plancha 2), por fuera de la fila j", 11.84),
        P("j13", "h29", "verde", "D2 → columna 29 (IN2, plancha 3), por fuera de la fila j", 12.06),
        P("j8", "h30", "blanco", "D5 → columna 30 (IN3, plancha 4), por fuera de la fila j", 12.28),
    ],
    externos=_LUZ["externos"] + [
        E("Rele", "IN1", "f28", "azul", "Módulo de 4 relés (caja de potencia): IN1 → plancha 2", "cable de señal"),
        E("Rele", "IN2", "f29", "verde", "IN2 → plancha 3", "cable de señal"),
        E("Rele", "IN3", "f30", "blanco", "IN3 → plancha 4 (IN4 queda libre)", "cable de señal"),
        E("Rele", "VCC", "J_3V3:27", "naranja", "VCC del lado de control (optoacopladores) a **3V3**: con 3.3 V "
          "en VCC, un GPIO en alto apaga bien el opto [verificar con el módulo, P-R1]", "cable de señal"),
        E("Rele", "GND", "J_GND:27", "negro", "", "cable de señal"),
        E("Rele", "JD-VCC", "A_5V:29", "rojo", "Bobinas a 5 V. **Quitar el puente JD-VCC–VCC del módulo**",
          "cable de señal"),
    ],
    redes={**_LUZ["redes"],
           "5V": {"NodeMCU.VIN", "C1.+", "Rele.JD-VCC"},
           "3V3": {"NodeMCU.3V3", "LDR.2", "Rele.VCC"},
           "GND": {"NodeMCU.GND", "C1.-", "R2.2", "LED_V.K", "LED_R.K", "Rele.GND"},
           "D1": {"NodeMCU.D1", "Rele.IN1"},
           "D2": {"NodeMCU.D2", "Rele.IN2"},
           "D5": {"NodeMCU.D5", "Rele.IN3"}},
    verificacion=_LUZ["verificacion"].replace(VERIF_COMUN, "") + """| Entradas IN1–IN3 (D1, D2, D5) | Opto del módulo entre VCC (3V3) e IN, con ≈ 1 kΩ: LOW → (3.3 − 1.2) / 1 kΩ | ≈ 2 mA por pin ✔ (< 12 mA). En alto (3.3 V = VCC) no circula corriente: relé apagado |
| Arranque | GPIO5, GPIO4 y GPIO14 no tienen función de arranque y quedan en alta impedancia: el opto no enciende | ✔ Relés apagados al arrancar o si el nodo se cuelga. El firmware escribe HIGH antes de `pinMode(OUTPUT)` |
| Bobinas (JD-VCC a 5 V) | 3 × ≈ 72 mA (SRD-05VDC, 0.36 W) [ficha del módulo POR CONFIRMAR] | ≈ 0.22 A del riel 5V ✔ (eliminador de 3 A) |
| Contactos | 10 A / 250 VAC por relé; carga por plancha ≤ 4 × 19 W ≈ 0.6 A a 127 V | ✔ Margen amplio. Fusible lento de 5 A en la caja de potencia |
| Nunca 5 V en un GPIO | IN1–IN3 solo ven el lado de 3V3 del opto; los 5 V quedan en el lado de las bobinas (JD-VCC) | ✔ Por eso se quita el puente JD-VCC |
""" + VERIF_COMUN,
)

LAYOUTS["nodo_pir"] = dict(
    titulo="pir (HC-SR501)",
    intro="HC-SR501 a 5 V (VIN); su salida OUT es de 3.3 V y entra directo a **D5**.",
    puentes=ALIMENTACION + LEDS_PUENTES + [
        P("j8", "h27", "blanco", "D5 → columna 27 (OUT del PIR), por fuera de la fila j", 11.84),
    ],
    componentes=[C1] + LEDS_COMP,
    externos=LEDS_EXT + [
        E("PIR", "VCC", "A_5V:28", "rojo", "HC-SR501 en la tapa; pinout VCC-OUT-GND [verificar serigrafía]"),
        E("PIR", "OUT", "f27", "blanco"),
        E("PIR", "GND", "A_GND:28", "negro"),
    ],
    redes={**REDES_COMUN,
           "5V": {"NodeMCU.VIN", "C1.+", "PIR.VCC"},
           "D5": {"NodeMCU.D5", "PIR.OUT"},
           "GND": {"NodeMCU.GND", "C1.-", "PIR.GND", "LED_V.K", "LED_R.K"}},
    verificacion="""
| Punto | Cálculo | Resultado |
|---|---|---|
| Alimentación del PIR | VIN ≈ 4.7 V; el HC-SR501 acepta 4.5–20 V | ✔ Justo arriba del mínimo: medir VIN con el nodo armado (P-02) |
| OUT → D5 | Salida de 3.3 V del regulador interno del módulo | ✔ Sin divisor. Medir que no pase de 3.3 V (P-02) |
| Consumo | HC-SR501 ≈ 65 µA en reposo | ✔ Despreciable |
""" + VERIF_COMUN,
)

LAYOUTS["nodo_puerta"] = dict(
    titulo="puerta (reed MC-38)",
    intro="Reed switch entre **D5** (INPUT_PULLUP) y GND: imán cerca = contacto cerrado = LOW = puerta cerrada.",
    puentes=ALIMENTACION + LEDS_PUENTES + [
        P("j8", "h27", "blanco", "D5 → columna 27 (reed), por fuera de la fila j", 11.84),
    ],
    componentes=[C1] + LEDS_COMP,
    externos=LEDS_EXT + [
        E("Reed", "1", "f27", "blanco", "Cable del MC-38 (≈ 30 cm) con terminal Dupont macho crimpado",
          "cable del MC-38"),
        E("Reed", "2", "J_GND:27", "negro", "Sin polaridad", "cable del MC-38"),
    ],
    redes={**REDES_COMUN,
           "D5": {"NodeMCU.D5", "Reed.1"},
           "GND": {"NodeMCU.GND", "C1.-", "Reed.2", "LED_V.K", "LED_R.K"}},
    verificacion="""
| Punto | Cálculo | Resultado |
|---|---|---|
| Pull-up interno de D5 | ≈ 30–100 kΩ a 3.3 V | ✔ Corriente con el reed cerrado ≈ 0.03–0.1 mA |
| Cable largo (≈ 30 cm) | Puede captar ruido | Antirrebote de 50 ms en firmware; si hay falsos cambios, agregar 10 kΩ externo de D5 a 3V3 |
""" + VERIF_COMUN,
)

LAYOUTS["nodo_acel"] = dict(
    titulo="acel (GY-61 + ADS1115)",
    intro="ADS1115 y GY-61 **clavados en la protoboard** (tiras de pines, de pie) para que vibren con ella; "
          "una costilla de la tapa sujeta su borde superior. ADS1115 en I²C (D1 SCL, D2 SDA, 0x48 con ADDR a GND). "
          "GY-61 X/Y/Z → A0/A1/A2. Componentes del ADS1115 hacia la fila a y del GY-61 hacia la fila j. "
          "LED en las columnas 19 y 30.",
    puentes=ALIMENTACION + [
        P("j6", "h19", "cafe", "D7 → columna 19 (LED verde), por fuera de la fila j", 11.40),
        P("j5", "h30", "morado", "D8 → columna 30 (LED rojo), por fuera de la fila j", 11.62),
        P("j14", "h22", "azul", "D1/SCL → columna 22, por fuera de la fila j", 11.84),
        P("j13", "h23", "verde", "D2/SDA → columna 23, por fuera de la fila j", 12.06),
        P("f22", "e22", "azul", "SCL cruza el canal hacia el ADS1115"),
        P("f23", "e23", "verde", "SDA cruza el canal hacia el ADS1115"),
        P("e20", "f20", "naranja", "VDD del ADS1115 cruza el canal"),
        P("j20", "J_3V3:20", "naranja", "VDD del ADS1115 → riel 3V3"),
        P("a21", "A_GND:21", "negro", "GND del ADS1115 → riel GND"),
        P("a24", "A_GND:24", "negro", "ADDR → GND (dirección 0x48)"),
        P("j25", "J_3V3:25", "naranja", "VCC del GY-61 → riel 3V3"),
        P("j29", "J_GND:29", "negro", "GND del GY-61 → riel GND"),
        P("f26", "e26", "blanco", "X del GY-61 → A0 del ADS1115"),
        P("f27", "e27", "gris", "Y del GY-61 → A1 del ADS1115"),
        P("f28", "e28", "cafe", "Z del GY-61 → A2 del ADS1115"),
    ],
    componentes=[C1,
                 R("R5", "330 Ω", "g19", "d19", "Cruza el canal (filas g→d). LED verde"),
                 R("R6", "330 Ω", "g30", "d30", "Cruza el canal (filas g→d). LED rojo"),
                 dict(M("ADS1115", "ADS1115 (breakout 10 pines)", "c", 20,
                        ["VDD", "GND", "SCL", "SDA", "ADDR", "ALRT", "A0", "A1", "A2", "A3"],
                        "Tira de 10 pines en la fila c, columnas 20–29, componentes hacia la fila a "
                        "[orden de pines POR CONFIRMAR]"), lado=-1),
                 dict(M("GY61", "GY-61 (ADXL335)", "h", 25, ["VCC", "X", "Y", "Z", "GND"],
                        "Tira de 5 pines en la fila h, columnas 25–29, componentes hacia la fila j "
                        "[orden POR CONFIRMAR]"), lado=1)],
    externos=[
        E("LED_V", "A", "a19", "verde", "Ánodo del LED verde, en la tapa"),
        E("LED_V", "K", "A_GND:18", "negro", "Cátodo"),
        E("LED_R", "A", "a30", "rojo", "Ánodo del LED rojo, en la tapa"),
        E("LED_R", "K", "A_GND:30", "negro", "Cátodo"),
    ],
    redes={"5V": {"NodeMCU.VIN", "C1.+"},
           "D7": {"NodeMCU.D7", "R5.1"}, "LED_V": {"R5.2", "LED_V.A"},
           "D8": {"NodeMCU.D8", "R6.1"}, "LED_R": {"R6.2", "LED_R.A"},
           "3V3": {"NodeMCU.3V3", "ADS1115.VDD", "GY61.VCC"},
           "GND": {"NodeMCU.GND", "C1.-", "ADS1115.GND", "ADS1115.ADDR", "GY61.GND", "LED_V.K", "LED_R.K"},
           "SCL": {"NodeMCU.D1", "ADS1115.SCL"},
           "SDA": {"NodeMCU.D2", "ADS1115.SDA"},
           "X": {"GY61.X", "ADS1115.A0"}, "Y": {"GY61.Y", "ADS1115.A1"}, "Z": {"GY61.Z", "ADS1115.A2"}},
    verificacion="""
| Punto | Cálculo | Resultado |
|---|---|---|
| GY-61 a 3V3 | Salidas ratiométricas: 0 g ≈ 1.65 V, ≈ 0.33 V/g; rango ±3 g → 0.66–2.64 V | ✔ Nunca superan 3.3 V |
| ADS1115 a 3V3 | Entradas válidas de −0.3 a VDD + 0.3 V; ganancia ±4.096 V (GAIN_ONE) | ✔ Resolución 0.125 mV ≈ 0.4 mg |
| I²C | Pull-ups del breakout (≈ 10 kΩ) a 3V3 | ✔ Sin resistencias extra |
| Consumo | ADXL335 ≈ 0.35 mA + ADS1115 ≈ 0.2 mA | ✔ Despreciable |
| D1/D2 | GPIO5/GPIO4 sin función de arranque | ✔ |
""" + VERIF_COMUN,
)


# ═════════════════════════════════════════════════════════════════════════════
#  Estaciones compartidas: 2 NodeMCU independientes en una MB-102 de 830 puntos
# ═════════════════════════════════════════════════════════════════════════════
# Cada nodo conserva su distribucion de 400 puntos: el de arriba usa las columnas 1-30 y el de abajo
# la misma distribucion corrida +33 columnas (34-63). Comparten 5V y GND; los rieles se tratan como
# partidos entre las columnas 31 y 32 (muchas MB-102 vienen asi) y se unen con puentes, EXCEPTO el de
# 3V3: cada NodeMCU tiene su propio regulador y sus salidas de 3V3 nunca deben unirse.
DESPLAZAMIENTO = 33
CORTE_RIELES = 32


def _renombrar(miembro, pref, placa):
    disp, pin = miembro.split(".", 1)
    return f"{placa}.{pin}" if disp == "NodeMCU" else f"{pref}_{disp}.{pin}"


def _nota(txt, d):
    """Corre tambien los orificios y columnas citados en las notas (a25 -> a58, "columna 27" -> "columna 60")."""
    if not d or not txt:
        return txt
    txt = re.sub(r"\b([a-j])(\d{1,2})\b", lambda m: f"{m[1]}{int(m[2]) + d}", txt)
    txt = re.sub(r"(columnas? |col\. )(\d+)(?:([–-])(\d+))?",
                 lambda m: f"{m[1]}{int(m[2]) + d}" + (f"{m[3]}{int(m[4]) + d}" if m[4] else ""), txt)
    return txt


def _parte(lay, pref, placa, d):
    puentes = [dict(p, de=mover(p["de"], d), a=mover(p["a"], d), nota=f"[{pref}] {_nota(p['nota'], d)}")
               for p in lay["puentes"]]
    comps = [dict(c, ref=f"{pref}_{c['ref']}", pines={k: mover(v, d) for k, v in c["pines"].items()},
                  nota=_nota(c.get("nota", ""), d))
             for c in lay["componentes"]]
    ext = [dict(e, disp=f"{pref}_{e['disp']}", orificio=mover(e["orificio"], d), nota=_nota(e.get("nota", ""), d))
           for e in lay["externos"]]
    redes = {f"{pref}_{k}": {_renombrar(m, pref, placa) for m in v} for k, v in lay["redes"].items()}
    return puentes, comps, ext, redes


def estacion(titulo, intro, nodo_a, nodo_b, verificacion):
    lay_a, lay_b = LAYOUTS[f"nodo_{nodo_a}"], LAYOUTS[f"nodo_{nodo_b}"]
    placa_a, placa_b = f"NodeMCU_{nodo_a}", f"NodeMCU_{nodo_b}"
    pa, ca, ea, ra = _parte(lay_a, nodo_a, placa_a, 0)
    pb, cb, eb, rb = _parte(lay_b, nodo_b, placa_b, DESPLAZAMIENTO)
    redes = {**ra, **rb}
    # 5V y GND son comunes a toda la estacion; 3V3 queda separado por placa
    cinco = set().union(ra.pop(f"{nodo_a}_5V"), rb.pop(f"{nodo_b}_5V")) | {"Entrada5V.+"}
    tierra = set().union(ra.pop(f"{nodo_a}_GND"), rb.pop(f"{nodo_b}_GND")) | {"Entrada5V.-"}
    redes = {**ra, **rb, "5V": cinco, "GND": tierra}
    puentes_rieles = [
        P("A_5V:31", "A_5V:33", "rojo", "Une el riel 5V partido (las dos mitades comparten la fuente)"),
        P("A_GND:31", "A_GND:33", "negro", "Une el riel GND superior partido"),
        P("J_GND:31", "J_GND:33", "negro", "Une el riel GND inferior partido. El riel 3V3 NO se une"),
    ]
    entrada = [
        E("Entrada5V", "+", "A_5V:32", "rojo", "Módulo de entrada USB-C a terminales (5 V de la fuente de la caja)",
          "cable corto"),
        E("Entrada5V", "-", "A_GND:32", "negro", "", "cable corto"),
    ]
    return dict(titulo=titulo, intro=intro, columnas=63, rieles_partidos=CORTE_RIELES,
                nodemcus=[{"nombre": placa_a, "col0": 1}, {"nombre": placa_b, "col0": 1 + DESPLAZAMIENTO}],
                puentes=pa + pb + puentes_rieles, componentes=ca + cb, externos=ea + eb + entrada,
                redes=redes, verificacion=verificacion)


VERIF_ESTACION = """
| Punto | Cálculo | Resultado |
|---|---|---|
| Alimentación compartida | Una fuente de 5 V ≥ 2 A (una por caja) entra por el módulo USB-C al riel 5V; cada NodeMCU recibe 5 V por su pin VIN | ✔ Consumo de la estación ≈ 0.1–0.2 A promedio, picos de WiFi ≈ 0.6 A |
| VIN directo | Alimentar por VIN salta el diodo del USB de la placa: los módulos de 5 V reciben ≈ 5.0 V en lugar de ≈ 4.7 V | ✔ Mejor margen para el HC-SR501 (mínimo 4.5 V) |
| 3V3 separado | Cada NodeMCU tiene su propio regulador; unir sus salidas los pondría a pelear | ✔ El riel 3V3 queda partido entre las columnas 31 y 32. **Verificar con el multímetro; si la protoboard trae el riel continuo, cortarlo** |
| Flasheo | Conectar la PC al micro-USB de una placa con la estación energizada es seguro: el diodo de la placa evita el retorno hacia la PC | ✔ La placa de arriba tiene su USB hacia el techo de la caja |
"""

LAYOUTS["estacion_entrada"] = estacion(
    "Estación de entrada (pir + puerta)",
    "Dos nodos independientes en una MB-102 de 830 puntos: **pir** en las columnas 1–30 y **puerta** en las "
    "34–63. Comparten la fuente (módulo USB-C) y la GND; cada placa conserva su propio 3V3.",
    "pir", "puerta", VERIF_ESTACION + VERIF_COMUN)

LAYOUTS["estacion_anaquel"] = estacion(
    "Estación del anaquel (acel + luz)",
    "Dos nodos independientes en una MB-102 de 830 puntos: **acel** en las columnas 1–30 y **luz** en las "
    "34–63. La fotorresistencia sale por un cable hasta su capuchón impreso junto a la lámpara.",
    "acel", "luz", VERIF_ESTACION + VERIF_COMUN)

LAYOUTS["estacion_anaquel_rele"] = estacion(
    "Estación del anaquel con relés (submódulo opcional)",
    "Igual que la estación del anaquel, pero el nodo luz usa la variante **luz_rele**: D1/D2/D5 salen por un cable "
    "de 6 hilos a la caja de potencia del fotoperiodo (docs/caja_potencia_luz.md).",
    "acel", "luz_rele", VERIF_ESTACION + VERIF_COMUN)


# ═════════════════════════════════════════════════════════════════════════════
#  Registro de cajas y variantes (lo leen cad/nodos.py, prompts.py, generar_wireviz.py y web.py)
# ═════════════════════════════════════════════════════════════════════════════
# Tres cajas, una fuente de 5 V por caja; cada nodo conserva su NodeMCU y su integrante.
CAJAS = {
    "dht": {"layout": "nodo_dht", "nodos": ("dht",)},
    "entrada": {"layout": "estacion_entrada", "nodos": ("pir", "puerta")},
    "anaquel": {"layout": "estacion_anaquel", "nodos": ("acel", "luz")},
}
# Caja de potencia del fotoperiodo (5-nov, SUBMÓDULO OPCIONAL: fuera de las 3 cajas base): no lleva protoboard ni
# NodeMCU. La manda el nodo luz_rele por el cable de señal (ver nodo_luz_rele); aquí solo va el lado de 127 V. La leen hardware/kicad/generar_kicad.py y cad/caja_potencia.py.
# Material comprado aparte: módulo de 4 relés de 5 V con opto y puente JD-VCC; 3 extensiones de 3 m y 3 contactos
# (calibre 16) que se cortan; portafusible en línea 5x20 con fusible lento de 5 A; clemas. Presupuesto aparte (≤ $500).
CAJA_POTENCIA = dict(
    titulo="Caja de potencia · fotoperiodo (127 V)",
    planchas={"CH1": 2, "CH2": 3, "CH3": 4},   # relé -> plancha que enciende (1 = arriba, sin uso)
    redes={
        "L_PARED": {"Clavija.L", "F1.1"},
        "L_FUS": {"F1.2", "K1.COM1", "K1.COM2", "K1.COM3"},
        "L_P2": {"K1.NO1", "Salida_P2.L"},
        "L_P3": {"K1.NO2", "Salida_P3.L"},
        "L_P4": {"K1.NO3", "Salida_P4.L"},
        "N": {"Clavija.N", "Salida_P2.N", "Salida_P3.N", "Salida_P4.N"},
        "PE": {"Clavija.PE", "Salida_P2.PE", "Salida_P3.PE", "Salida_P4.PE"},
    },
    notas=[
        "Solo se interrumpe la fase (L), siempre después del fusible; neutro y tierra pasan directos por clemas.",
        "Contacto NO (normalmente abierto): sin señal o sin 5 V, la luz queda apagada.",
        "Probar primero sin enchufar (continuidad con multímetro); a 127 V solo con la revisión del Ing. Puga.",
    ],
)

# Distribuciones que no son caja propia: respaldo sin OLED y nodos sueltos para probar cada integrante
# por separado (Etapa 2). Las estaciones se arman a partir de los sueltos.
VARIANTES = ("nodo_dht_sin_oled", "nodo_luz", "nodo_pir", "nodo_puerta", "nodo_acel",
             "nodo_luz_rele", "estacion_anaquel_rele")   # las 2 ultimas: submodulo opcional de luz
assert set(LAYOUTS) == {c["layout"] for c in CAJAS.values()} | set(VARIANTES), "LAYOUTS y registro no coinciden"
