"""Arma el script unico de la Etapa 3: esquema (docs/bd/esquema.sql) + datos de prueba (datos_prueba.sql).

Uso (desde la raiz):  python docs/bd/etapa3/generar_script.py [numero_de_equipo]
Salida: docs/bd/etapa3/ScriptCreacionBaseDatos_iot_Equipo<N>.sql  (sin numero: EquipoX)
El esquema sigue siendo la unica fuente: si cambia, se vuelve a correr este script.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
equipo = sys.argv[1] if len(sys.argv) > 1 else "X"
salida = AQUI / f"ScriptCreacionBaseDatos_iot_Equipo{equipo}.sql"

esquema = (AQUI.parent / "esquema.sql").read_text(encoding="utf-8")
datos = (AQUI / "datos_prueba.sql").read_text(encoding="utf-8")

encabezado = f"""-- ScriptCreacionBaseDatos_iot_Equipo{equipo}.sql — Argos (G507 · TC1004B), Etapa 3.
-- Crea la base "argos" COMPLETA (tablas, llaves, restricciones, datos fijos) y le carga datos de prueba.
-- GENERADO por docs/bd/etapa3/generar_script.py a partir de docs/bd/esquema.sql y datos_prueba.sql.
-- Requiere MySQL 8.0 o mas nuevo. Correrlo entero (DBeaver: Alt+X / Workbench: rayo).
-- OJO: borra la base "argos" si ya existe, para poder correrlo varias veces.

DROP DATABASE IF EXISTS argos;

"""
salida.write_text(encabezado + esquema.rstrip() + "\n\n" + datos, encoding="utf-8", newline="\n")
print("listo:", salida.relative_to(AQUI.parents[2]))
