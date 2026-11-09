"""Convierte los STEP orientados para imprimir (cad/exports/impresion/) a 3MF (cad/exports/3mf/).

El 3MF guarda la pieza en mm y sin ambiguedad de unidades; el slicer lo abre igual que el STL.
Uso (desde la raiz, despues de cad/nodos.py):
    uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" python cad/exportar_3mf.py
"""
from pathlib import Path

from build123d import Mesher, Unit, import_step

RAIZ = Path(__file__).resolve().parent / "exports"


def main():
    destino = RAIZ / "3mf"
    destino.mkdir(exist_ok=True)
    for step in sorted((RAIZ / "impresion").glob("*.step")):
        forma = import_step(str(step))
        salida = destino / f"{step.stem}.3mf"
        for lin, ang in ((0.02, 0.2), (0.05, 0.3), (0.1, 0.5)):   # si la malla fina sale invalida, se afloja
            try:
                m = Mesher(unit=Unit.MM)
                m.add_shape(forma, linear_deflection=lin, angular_deflection=ang)
                m.write(str(salida))
                print(f"{salida.name}: {len(forma.solids())} solido(s), {forma.volume / 1000:.2f} cm3, malla {lin} mm")
                break
            except RuntimeError as err:
                print(f"   {step.stem}: malla {lin} mm invalida ({err})")
        else:
            print(f"   {step.stem}: SIN 3MF (usar el STL)")


if __name__ == "__main__":
    main()
