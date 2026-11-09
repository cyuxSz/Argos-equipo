"""Simulador de los 5 nodos: publica por MQTT exactamente lo que publicaria el firmware (contrato de CLAUDE.md §2).

Sirve para avanzar la Etapa 3 y 4 (n8n -> MySQL, alertas y los 5 indicadores del dashboard) sin hardware.
Cada nodo usa su usuario MQTT, client id "sim-<id>" (no choca con los nodos reales "nodo-<id>"), estado
retenido con LWT, latido cada 60 s y sus eventos. Los valores son inventados: NO usar como datos del cuarto.

Uso (desde la raiz; lee MQTT_HOST, MQTT_PORT y MQTT_PASSWORD_<NODO> de .env):
    uv run --no-project --python 3.12 --with paho-mqtt python simulador/simulador_nodos.py [--rapido] [--escenario X]
Escenarios: normal (por omision), calor (la temperatura sube hasta pasar 28 C), sin_red (el nodo luz se cae a
los 3 min), golpes (golpes y puerta abierta cada pocos minutos). --rapido divide los periodos entre 10.
Solo para el broker de pruebas (laptop): no apuntarlo al n8n productivo.
"""
import argparse
import json
import math
import os
import random
import threading
import time
from pathlib import Path

import paho.mqtt.client as mqtt

RAIZ = Path(__file__).resolve().parents[1]
NODOS = ("dht", "luz", "pir", "puerta", "acel")


def leer_env():
    env = {}
    ruta = RAIZ / ".env"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                env[k.strip()] = v.strip()
    return {**env, **{k: v for k, v in os.environ.items() if k.startswith(("MQTT_", "WIFI_"))}}


class Nodo:
    def __init__(self, nid, env, escala):
        self.id, self.escala, self.inicio = nid, escala, time.time()
        self.c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sim-{nid}")
        self.c.username_pw_set(nid, env.get(f"MQTT_PASSWORD_{nid.upper()}", ""))
        self.c.will_set(f"invernadero/estado/{nid}", json.dumps({"estado": "offline"}), qos=1, retain=True)
        self.c.on_connect = self.al_conectar
        self.c.on_message = self.al_recibir
        self.c.connect(env.get("MQTT_HOST", "localhost"), int(env.get("MQTT_PORT", 1883)), keepalive=45)
        self.c.loop_start()

    def al_conectar(self, c, _u, _f, rc, _p=None):
        if rc.is_failure:   # el broker rechazo usuario/contrasena: no seguir como si nada
            print(f"[{self.id}] el broker RECHAZO la conexion: {rc}")
            return
        estado = {"estado": "online", "reset_reason": "Power on", "uptime_s": int(time.time() - self.inicio),
                  "rssi": random.randint(-75, -55)}
        c.publish(f"invernadero/estado/{self.id}", json.dumps(estado), qos=1, retain=True)
        if self.id == "dht":
            c.subscribe("invernadero/cmd/alarma")
        print(f"[{self.id}] conectado (rc={rc})")

    def al_recibir(self, _c, _u, msg):
        print(f"[{self.id}] {msg.topic} = {msg.payload.decode()}  (el buzzer real sonaria si es 'on')")

    def lectura(self, *pares):
        cuerpo = {"lecturas": [{"parametro": p, "valor": round(v, 1), "unidad": u} for p, v, u in pares]}
        self.c.publish(f"invernadero/telemetria/{self.id}", json.dumps(cuerpo))

    def evento(self, tipo, magnitud=None):
        cuerpo = {"tipo": tipo} if magnitud is None else {"tipo": tipo, "magnitud": round(magnitud, 2)}
        self.c.publish(f"invernadero/evento/{self.id}", json.dumps(cuerpo))
        print(f"[{self.id}] evento {cuerpo}")

    def dormir(self, s):
        time.sleep(s / self.escala)


def correr(n, escenario):
    t0 = time.time()
    latido = 0.0
    puerta_abierta = False
    while True:
        minutos = (time.time() - t0) * n.escala / 60
        if n.id == "dht":
            sube = min(minutos * 0.5, 5.0) if escenario == "calor" else 0.0   # +0.5 C por minuto, tope +5
            t = 25 + 1.2 * math.sin(minutos / 30) + sube + random.gauss(0, 0.1)
            h = 50 + 5 * math.sin(minutos / 45) + random.gauss(0, 0.5)
            n.lectura(("temperatura", t, "C"), ("humedad", h, "%"))
            n.dormir(30)
            continue
        if n.id == "luz":
            if escenario == "sin_red" and minutos > 3:
                print("[luz] se desconecta sin avisar (debe disparar el LWT offline)")
                n.c.loop_stop()            # corte brusco, sin DISCONNECT: el broker publica el LWT al vencer
                if n.c.socket():           # el keep-alive (45 s x 1.5)
                    n.c.socket().close()
                return
            encendidas = (int(minutos) // 60) % 2 == 0    # alterna cada hora simulada
            n.lectura(("luz", (720 if encendidas else 90) + random.gauss(0, 15), "adc"))
            n.dormir(60)
            continue
        # pir, puerta y acel: latido cada 60 s y eventos al azar
        if time.time() - latido >= 60 / n.escala:
            latido = time.time()
            n.lectura(("latido", 1, ""))
        prob = 0.15 if escenario == "golpes" else 0.03
        if random.random() < prob:
            if n.id == "pir":
                n.evento("movimiento")
            elif n.id == "acel":
                n.evento("golpe", random.uniform(0.55, 2.0))
            elif n.id == "puerta":
                puerta_abierta = not puerta_abierta
                n.evento("puerta_abierta" if puerta_abierta else "puerta_cerrada")
        n.dormir(10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--escenario", choices=("normal", "calor", "sin_red", "golpes"), default="normal")
    args = ap.parse_args()
    env = leer_env()
    escala = 10.0 if args.rapido else 1.0
    nodos = [Nodo(nid, env, escala) for nid in NODOS]
    hilos = [threading.Thread(target=correr, args=(n, args.escenario), daemon=True) for n in nodos]
    for h in hilos:
        h.start()
    print(f"simulando {len(nodos)} nodos, escenario {args.escenario}; Ctrl+C para salir")
    try:
        while any(h.is_alive() for h in hilos):
            time.sleep(1)
    except KeyboardInterrupt:
        for n in nodos:   # salida ordenada: offline retenido, como el LWT
            n.c.publish(f"invernadero/estado/{n.id}", json.dumps({"estado": "offline"}), qos=1, retain=True)
            n.c.disconnect()


if __name__ == "__main__":
    main()
