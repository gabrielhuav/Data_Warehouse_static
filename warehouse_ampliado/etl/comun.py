"""Utilidades del almacen ampliado: manifiesto, verificacion, conexion y carga masiva."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "fuentes.json"
SNAPSHOTS = RAIZ / "snapshots"
DATOS = Path(os.environ.get("DIR_DATOS_CRUDOS", RAIZ / "datos_crudos"))
DSN = os.environ.get("DW_DSN", "postgresql://postgres:postgres@localhost:5433/data_warehouse")
AGENTE = "Mozilla/5.0 (almacen de agua ESCOM-IPN; ETL reproducible)"

csv.field_size_limit(50_000_000)


def leer_manifiesto() -> dict:
    return json.loads(MANIFIESTO.read_text(encoding="utf-8"))


def guardar_manifiesto(man: dict) -> None:
    """Una fuente por linea, para que los cambios se lean bien en git."""
    lineas = [f'  "_nota": {json.dumps(man["_nota"], ensure_ascii=False)},', '  "fuentes": [']
    lineas += ["    " + json.dumps(f, ensure_ascii=False) + ("," if i < len(man["fuentes"]) - 1 else "")
               for i, f in enumerate(man["fuentes"])]
    MANIFIESTO.write_text("{\n" + "\n".join(lineas) + "\n  ]\n}\n", encoding="utf-8")


def fuentes() -> dict[str, dict]:
    return {f["id"]: f for f in leer_manifiesto()["fuentes"]}


def ruta(f: dict) -> Path:
    if f.get("snapshot"):
        return SNAPSHOTS / f["archivo"]
    return DATOS / f["id"] / f["archivo"]


def huellas(p: Path) -> tuple[int, str, str]:
    """(bytes, md5, sha256) del archivo, leyendolo por bloques."""
    md5, sha = hashlib.md5(), hashlib.sha256()
    n = 0
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            md5.update(b)
            sha.update(b)
            n += len(b)
    return n, md5.hexdigest(), sha.hexdigest()


class FuenteInvalida(RuntimeError):
    pass


def armar_partes(f: dict, destino: Path) -> None:
    """Une en destino las partes de snapshots/. Una parte alterada detiene la union."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    with open(parcial, "wb") as sal:
        for parte in f["partes"]:
            p = SNAPSHOTS / parte["archivo"]
            if not p.exists():
                raise FuenteInvalida(f"{f['id']}: falta {p}")
            datos = p.read_bytes()
            if hashlib.sha256(datos).hexdigest() != parte["sha256"]:
                raise FuenteInvalida(f"{f['id']}: {p.name} no coincide con el manifiesto")
            sal.write(datos)
    parcial.replace(destino)


def verificar(id_fuente: str, cache: dict | None = None) -> tuple[Path, dict]:
    """Devuelve (ruta, entrada) solo si el archivo coincide con el manifiesto."""
    cache = {} if cache is None else cache
    f = fuentes()[id_fuente]
    p = ruta(f)
    if not p.exists():
        raise FuenteInvalida(f"{id_fuente}: falta {p}. Corre etl/descargar.py")
    if id_fuente not in cache:
        cache[id_fuente] = huellas(p)
    n, md5, sha = cache[id_fuente]
    for campo, real in (("bytes", n), ("md5", md5), ("sha256", sha), ("md5_oficial", md5)):
        esperado = f.get(campo)
        if esperado is not None and esperado != real:
            raise FuenteInvalida(f"{id_fuente}: {campo} esperado {esperado}, calculado {real}")
    if not f.get("sha256"):
        raise FuenteInvalida(f"{id_fuente}: el manifiesto no tiene sha256. Corre etl/descargar.py --registrar")
    return p, f


def descargar(url: str, destino: Path, intentos: int = 4, timeout: int = 300) -> None:
    """Escribe en .part y renombra al terminar: una descarga cortada no pasa por completa."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    for i in range(1, intentos + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
            with urllib.request.urlopen(req, timeout=timeout) as r, open(parcial, "wb") as fh:
                for b in iter(lambda: r.read(1 << 20), b""):
                    fh.write(b)
            parcial.replace(destino)
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"  intento {i}/{intentos} fallido: {e}")
            time.sleep(5 * i)
    raise RuntimeError(f"No se pudo descargar {url}")


def conectar():
    import psycopg2

    return psycopg2.connect(DSN)


def normalizar(texto) -> str | None:
    """MAYUSCULAS, sin acentos ni signos y con un solo espacio."""
    if texto is None:
        return None
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    t = re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", t)).strip()
    return None if t in ("", "NA", "N A", "NAN", "NONE") else t


def copiar(cur, tabla: str, columnas: list[str], df) -> int:
    """COPY masivo de un DataFrame. NaN y None llegan como NULL."""
    buf = io.StringIO()
    df[columnas].to_csv(buf, index=False, header=False, na_rep="")
    buf.seek(0)
    cur.copy_expert(f"COPY {tabla} ({', '.join(columnas)}) FROM STDIN WITH (FORMAT csv, NULL '')", buf)
    return len(df)


def registrar(cur, id_fuente: str, tabla: str, filas: int, nota: str | None = None, cache: dict | None = None) -> None:
    """Escribe en control_ingesta_fuentes lo que realmente se cargo. No hay entradas a mano."""
    p, f = verificar(id_fuente, cache)
    n, md5, sha = (cache or {}).get(id_fuente) or huellas(p)
    cur.execute(
        """INSERT INTO control_ingesta_fuentes
           (id_fuente, nombre, publicador, archivo, url, doi, licencia, bytes, md5, sha256,
            md5_oficial_coincide, tabla_destino, filas, nota)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (id_fuente, f["nombre"], f.get("publicador"), f["archivo"], f["url"], f.get("doi"), f.get("licencia"),
         n, md5, sha, (f["md5_oficial"] == md5) if f.get("md5_oficial") else None, tabla, filas, nota))
    print(f"  {tabla:<34}{filas:>10,}  {id_fuente}{'  ' + nota if nota else ''}")


def asegurar_fechas(cur, fechas) -> dict:
    """Agrega a dim_tiempo las fechas que falten, con la misma regla de bimestre que
    warehouse/etl/2_dim.sql, y devuelve {fecha: id_tiempo}. Los id existentes no cambian."""
    import pandas as pd

    unicas = pd.to_datetime(pd.Series(list(set(fechas)))).dropna().dt.normalize().drop_duplicates().sort_values()
    buf = io.StringIO()
    pd.DataFrame({"f": unicas.dt.strftime("%Y-%m-%d")}).to_csv(buf, index=False, header=False)
    buf.seek(0)
    cur.execute("CREATE TEMP TABLE t_fechas (fecha DATE) ON COMMIT DROP")
    cur.copy_expert("COPY t_fechas FROM STDIN WITH (FORMAT csv)", buf)
    cur.execute("""INSERT INTO dim_tiempo (fecha, anio, mes, dia, bimestre)
                   SELECT fecha, EXTRACT(YEAR FROM fecha)::INT, EXTRACT(MONTH FROM fecha)::INT,
                          EXTRACT(DAY FROM fecha)::INT, (EXTRACT(MONTH FROM fecha)::INT + 1) / 2
                   FROM t_fechas ORDER BY fecha ON CONFLICT (fecha) DO NOTHING""")
    cur.execute("SELECT t.fecha, d.id_tiempo FROM t_fechas t JOIN dim_tiempo d USING (fecha)")
    mapa = {pd.Timestamp(f): i for f, i in cur.fetchall()}
    cur.execute("DROP TABLE t_fechas")
    return mapa


def abrir_csv_zip(z: zipfile.ZipFile, sufijo: str, **kw):
    """Lee a pandas, como texto, el CSV del ZIP con ese nombre exacto (o ese sufijo, si es unico)."""
    import pandas as pd

    objetivo = sufijo.lower()
    n = [x for x in z.namelist() if x.lower().rsplit("/", 1)[-1] == objetivo]
    if not n:
        n = [x for x in z.namelist() if x.lower().endswith(objetivo)]
    if len(n) != 1:
        raise FuenteInvalida(f"{sufijo}: {len(n)} coincidencias en {z.filename}")
    raw = z.read(n[0])
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=enc, keep_default_na=False, **kw)
        except UnicodeDecodeError:
            continue
    raise FuenteInvalida(f"{sufijo}: codificacion desconocida")


def num(s):
    """Texto a numero. Los codigos -1, -2 y -3 del CNGMD son 'no aplica', 'no disponible' y 'no sabe'."""
    import pandas as pd

    v = pd.to_numeric(s, errors="coerce")
    return v.where(v >= 0)
