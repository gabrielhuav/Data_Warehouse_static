#!/usr/bin/env python3
"""Exporta al mapa estatico lo que devuelven las consultas de consultas/.

    python -I etl/exportar_mapa.py

Cada archivo .sql produce ijcopi/datos/<nombre>.json con sus filas tal cual. No hay otra entrada:
ni archivos de las fuentes ni valores escritos aqui. manifiesto.json guarda el hash de cada consulta
y de su resultado, y verificacion/verificar_mapa.py lo comprueba contra la base de datos.
"""
from __future__ import annotations

import datetime as dt
import decimal
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import RAIZ, conectar  # noqa: E402

CONSULTAS = RAIZ / "consultas"
SALIDA = RAIZ.parent / "ijcopi" / "datos"


def plano(v):
    if isinstance(v, decimal.Decimal):
        return int(v) if v == v.to_integral_value() and abs(v) < 2 ** 53 else float(v)
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()
    return v


def correr(cur, sql_path: Path) -> tuple[list[str], list[list]]:
    cur.execute(sql_path.read_text(encoding="utf-8"))
    return [c.name for c in cur.description], [[plano(v) for v in fila] for fila in cur.fetchall()]


def canonico(columnas: list[str], filas: list[list]) -> bytes:
    return json.dumps({"columnas": columnas, "filas": filas}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def consultas() -> list[Path]:
    return sorted(CONSULTAS.glob("*.sql"))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    SALIDA.mkdir(parents=True, exist_ok=True)
    conn = conectar()
    resumen = []
    try:
        with conn.cursor() as cur:
            for q in consultas():
                columnas, filas = correr(cur, q)
                datos = canonico(columnas, filas)
                (SALIDA / f"{q.stem}.json").write_bytes(datos)
                resumen.append({"consulta": q.name, "datos": f"{q.stem}.json", "filas": len(filas), "columnas": columnas,
                                "sha256_consulta": sha(q.read_bytes().replace(b"\r\n", b"\n")), "sha256_datos": sha(datos)})
                print(f"{q.stem:<28}{len(filas):>8,} filas  {len(datos) / 1024:>8,.0f} KB")
    finally:
        conn.close()
    manifiesto = {"generado_en": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "consultas": resumen}
    (SALIDA / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
