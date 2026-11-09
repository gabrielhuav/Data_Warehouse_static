#!/usr/bin/env python3
"""Comprueba que el mapa publicado es lo que devuelve la base de datos.

    python -I verificacion/verificar_mapa.py

Repite cada consulta de consultas/ y compara el resultado, byte por byte en forma canonica, con
ijcopi/datos/. Falla si una consulta cambio, si un archivo se edito a mano o si el almacen
ya no devuelve lo mismo. Escribe el resultado en evidencia_mapa.txt.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from comun import RAIZ, conectar  # noqa: E402
from exportar_mapa import SALIDA, canonico, consultas, correr, sha  # noqa: E402

EVIDENCIA = RAIZ / "verificacion" / "evidencia_mapa.txt"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    manifiesto = json.loads((SALIDA / "manifiesto.json").read_text(encoding="utf-8"))
    declaradas = {c["consulta"]: c for c in manifiesto["consultas"]}
    lineas = [f"Evidencia del mapa, generada {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC",
              f"Exportacion comprobada: {manifiesto['generado_en']}", ""]
    fallos = 0

    def decir(ok: bool, texto: str) -> None:
        nonlocal fallos
        fallos += 0 if ok else 1
        lineas.append(f"[{'OK ' if ok else 'MAL'}] {texto}")
        print(lineas[-1])

    conn = conectar()
    try:
        with conn.cursor() as cur:
            vistas = consultas()
            decir({q.name for q in vistas} == set(declaradas), f"{len(vistas)} consultas, las mismas del manifiesto")
            for q in vistas:
                d = declaradas.get(q.name)
                if d is None:
                    decir(False, f"{q.name}: no esta en el manifiesto")
                    continue
                columnas, filas = correr(cur, q)
                datos = canonico(columnas, filas)
                archivo = (SALIDA / d["datos"]).read_bytes()
                iguales = sha(datos) == d["sha256_datos"] == sha(archivo)
                mismo_sql = sha(q.read_bytes().replace(b"\r\n", b"\n")) == d["sha256_consulta"]
                decir(iguales and mismo_sql, f"{q.stem}: {len(filas):,} filas, sha256 {sha(datos)[:16]}")
    finally:
        conn.close()

    lineas += ["", f"verificaciones fallidas: {fallos}"]
    print(lineas[-1])
    EVIDENCIA.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
