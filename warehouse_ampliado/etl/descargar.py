#!/usr/bin/env python3
"""Baja las fuentes del manifiesto y las verifica contra bytes, MD5 y SHA-256.

    python etl/descargar.py                 baja lo que falte y verifica todo
    python etl/descargar.py --registrar     ademas escribe en fuentes.json las huellas
                                            que falten (la primera vez que se fija una version)
    python etl/descargar.py --solo A2 D5    limita a esos identificadores

Los archivos con snapshot=true viven en snapshots/ y no se vuelven a bajar salvo con
--actualizar-snapshots: su origen cambia, asi que la copia congelada es la version usada.
Los que tienen manual=true estan en hosts que responden 403 a scripts. Los que ademas traen
"partes" se reconstruyen desde snapshots/partes/; si no hay partes ni copia, hay que bajarlos
con un navegador desde la URL del manifiesto.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (  # noqa: E402
    FuenteInvalida, armar_partes, descargar, guardar_manifiesto, huellas, leer_manifiesto, ruta,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--actualizar-snapshots", action="store_true")
    ap.add_argument("--solo", nargs="*")
    args = ap.parse_args()

    man = leer_manifiesto()
    fallos = 0
    for f in man["fuentes"]:
        if args.solo and f["id"] not in args.solo:
            continue
        p = ruta(f)
        rehacer = args.actualizar_snapshots and f.get("snapshot")
        if f.get("partes") and not p.exists():
            print(f"[{f['id']}] uniendo {len(f['partes'])} partes de snapshots/partes/")
            try:
                armar_partes(f, p)
            except FuenteInvalida as e:
                print(f"[{f['id']}] FALLA {e}")
                fallos += 1
                continue
        if f.get("manual") and not p.exists():
            print(f"[{f['id']}] FALTA: el host rechaza scripts. Abre {f['url']} en un navegador y guardalo en {p}")
            fallos += 1
            continue
        if (not p.exists() or rehacer) and not f.get("manual"):
            print(f"[{f['id']}] bajando {f['url']}")
            try:
                descargar(f["url"], p)
            except RuntimeError as e:
                print(f"[{f['id']}] FALLA {e}")
                fallos += 1
                continue
        n, md5, sha = huellas(p)
        problemas = []
        for campo, real in (("bytes", n), ("md5_oficial", md5)):
            if f.get(campo) is not None and f[campo] != real:
                problemas.append(f"{campo} esperado {f[campo]}, calculado {real}")
        if not rehacer:
            for campo, real in (("md5", md5), ("sha256", sha)):
                if f.get(campo) is not None and f[campo] != real:
                    problemas.append(f"{campo} esperado {f[campo]}, calculado {real}")
        if problemas:
            print(f"[{f['id']}] NO COINCIDE: {'; '.join(problemas)}")
            fallos += 1
            continue
        if args.registrar:
            f.update(bytes=n, md5=md5, sha256=sha)
        print(f"[{f['id']}] ok {n:,} B md5 {md5} sha256 {sha[:16]}...")

    if args.registrar:
        guardar_manifiesto(man)
        print("manifiesto actualizado")
    print(f"fallos: {fallos}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
