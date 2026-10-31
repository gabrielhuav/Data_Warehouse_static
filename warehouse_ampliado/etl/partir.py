#!/usr/bin/env python3
"""Divide un archivo verificado en partes dentro de snapshots/partes/ y las anota en fuentes.json.

    python etl/partir.py D15 --mb 20

Es para las fuentes que el origen rechaza a los scripts y que no conviene subir enteras. El
archivo original debe estar en datos_crudos/ y coincidir con el manifiesto. descargar.py
reconstruye el original a partir de las partes y vuelve a comprobar su MD5 y su SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import SNAPSHOTS, guardar_manifiesto, leer_manifiesto, verificar  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id")
    ap.add_argument("--mb", type=int, default=20)
    args = ap.parse_args()

    origen, f = verificar(args.id)
    dir_partes = SNAPSHOTS / "partes"
    dir_partes.mkdir(parents=True, exist_ok=True)
    for viejo in dir_partes.glob(f"{f['archivo']}.*"):
        viejo.unlink()

    partes = []
    with open(origen, "rb") as fh:
        for i, bloque in enumerate(iter(lambda: fh.read(args.mb * 1_000_000), b""), start=1):
            nombre = f"{f['archivo']}.{i:03d}"
            (dir_partes / nombre).write_bytes(bloque)
            partes.append({"archivo": f"partes/{nombre}", "bytes": len(bloque),
                           "sha256": hashlib.sha256(bloque).hexdigest()})
            print(f"{nombre}: {len(bloque):,} B")

    man = leer_manifiesto()
    next(x for x in man["fuentes"] if x["id"] == args.id)["partes"] = partes
    guardar_manifiesto(man)
    print(f"{args.id}: {len(partes)} partes anotadas en fuentes.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
