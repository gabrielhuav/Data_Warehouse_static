"""Recalculate and draw the manuscript corpus diagram (SVG and 300 dpi PNG).

Run from any directory with Python and Pillow:
    python -I paper/ijcopi/generar_diagrama_corpus.py

Input paths are relative to this repository, never to another checkout. The two
retained CSVs are recounted; CRLF/LF differences are recorded and their canonical
LF SHA-256 hashes are checked without rewriting either file. Expanded warehouse
totals are summed from the SHA-256-verified SQL-count export, not from a new live
PostgreSQL query. No ETL, download, database or Git write is performed.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DPI = 300
WIDTH_CM, HEIGHT_CM = 16.5, 6.3
W, H = WIDTH_CM / 2.54 * 72, HEIGHT_CM / 2.54 * 72
SCALE = DPI / 72
MIN_FONT_PT = 8.0
RAW_INPUTS = {
    "sacmex": (
        "warehouse/data/consumo_agua_historico_2019.csv",
        "12aede58872a50856405ea24b6933e4b29b20d1de0e32d7463fabf855259b31d",
    ),
    "open_meteo": (
        "warehouse/data/open-meteo-19.44N99.11W2233m.csv",
        "3f7e6523150aae80e6fe88dfba3697b277dae72c255e4fcaeef17cc22a471933",
    ),
}
FAMILIES = ["INEGI", "CONAGUA / SMN", "CONAPO", "SACMEX / ADIP", "SHCP", "Academic"]
EXPECTED_FAMILY_COUNTS = [21, 25, 6, 2, 1, 7]
COLOUR = {
    "ink": "#172C38", "muted": "#435663", "line": "#667783",
    "teal": "#006E62", "teal_fill": "#EAF5F1", "teal_border": "#8DBAAF",
    "purple": "#673983", "purple_fill": "#F2EDF7", "purple_border": "#B29AC9",
    "neutral": "#F3F6F8", "neutral_border": "#A3B2BE", "white": "#FFFFFF",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def family(source_id: str) -> str:
    if source_id.startswith("B") or source_id.startswith(("D2", "D3")):
        return "INEGI"
    if source_id.startswith("A") or source_id == "D10":
        return "Academic"
    if source_id.startswith("C1"):
        return "SACMEX / ADIP"
    if source_id in {"D1a", "D1b", "D11", "D12", "D13", "D15"}:
        return "CONAPO"
    if source_id == "D4":
        return "SHCP"
    return "CONAGUA / SMN"


def check(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def calculate() -> dict:
    evidence = {"inputs": {}}
    csv_rows = {}
    for label, (relative, expected) in RAW_INPUTS.items():
        raw = (ROOT / relative).read_bytes()
        canonical = raw.replace(b"\r\n", b"\n")
        check(sha(canonical) == expected, f"Canonical LF SHA-256 mismatch: {relative}")
        evidence["inputs"][relative] = {
            "sha256_file_bytes": sha(raw), "sha256_canonical_lf": sha(canonical),
            "canonical_lf_sha256_verified": True,
        }
        csv_rows[label] = list(csv.DictReader(io.StringIO(raw.decode("utf-8"), newline="")))

    sources_path = "warehouse_ampliado/fuentes.json"
    sources = read_json(sources_path)["fuentes"]
    source_ids = {s["id"] for s in sources}
    check(len(source_ids) == len(sources), "Duplicate input source IDs")
    evidence["inputs"][sources_path] = {
        "sha256_canonical_lf": sha((ROOT / sources_path).read_bytes().replace(b"\r\n", b"\n")),
    }
    export_manifest = read_json("ijcopi/datos/manifiesto.json")
    exports = {}
    for name in ["01_fuentes_cargadas.json", "02_tablas_del_almacen.json"]:
        relative = "ijcopi/datos/" + name
        record = next(x for x in export_manifest["consultas"] if x["datos"] == name)
        raw = (ROOT / relative).read_bytes()
        check(sha(raw) == record["sha256_datos"], f"SQL-export SHA-256 mismatch: {relative}")
        evidence["inputs"][relative] = {"sha256_file_bytes": sha(raw), "export_sha256_verified": True}
        exports[name] = json.loads(raw)
    log_data = exports["01_fuentes_cargadas.json"]
    log = [dict(zip(log_data["columnas"], row)) for row in log_data["filas"]]
    check({r["id_fuente"] for r in log} == source_ids, "Source IDs disagree with the ingestion export")
    by_id = {s["id"]: s for s in sources}
    for row in log:
        check(row["sha256_inicio"] == by_id[row["id_fuente"]]["sha256"][:16],
              f"Source hash prefix mismatch for {row['id_fuente']}")
    groups = Counter(family(s["id"]) for s in sources)
    check([groups[f] for f in FAMILIES] == EXPECTED_FAMILY_COUNTS, "Source-family counts changed")
    check(sum(groups.values()) == len(sources) == 62, "Manifest input count changed")
    check(not any(s["sha256"] in {value[1] for value in RAW_INPUTS.values()} for s in sources),
          "A retained original CSV unexpectedly appears in the extension manifest")

    climate = csv_rows["open_meteo"]
    hours_by_day = Counter(row["time"][:10] for row in climate)
    check(set(hours_by_day.values()) == {24}, "An Open-Meteo day does not have 24 hourly rows")
    raw_billing = csv_rows["sacmex"]
    loaded_billing = [row for row in raw_billing
                      if all(row[key].strip() not in ("", "NA") for key in ["alcaldia", "colonia", "indice_des"])
                      and row["fecha_referencia"] in hours_by_day]
    original = {
        "retained_csv_files": len(RAW_INPUTS),
        "sacmex_source_rows": len(raw_billing), "sacmex_fact_rows": len(loaded_billing),
        "sacmex_excluded_rows": len(raw_billing) - len(loaded_billing),
        "open_meteo_hourly_rows": len(climate), "open_meteo_daily_rows": len(hours_by_day),
        "period_start": min(hours_by_day), "period_end": max(hours_by_day),
    }
    check([original[k] for k in ["sacmex_source_rows", "sacmex_fact_rows", "sacmex_excluded_rows",
                                 "open_meteo_hourly_rows", "open_meteo_daily_rows"]]
          == [71102, 70886, 216, 4344, 181], "Original CSV counts changed")
    tables = dict(exports["02_tablas_del_almacen.json"]["filas"])
    check(tables["fact_consumo_agua"] == len(loaded_billing), "Billing recount disagrees with SQL-count export")
    check(tables["fact_clima"] == len(hours_by_day), "Daily climate count disagrees with SQL-count export")
    check(len(tables) == 45 and sum(tables.values()) == 2794184, "Warehouse snapshot totals changed")
    check(tables["control_ingesta_fuentes"] == len(log) == 97, "Ingestion-control count changed")
    academic_parts = {
        "MexHiResClimDB": sorted(s["id"] for s in sources if s["id"].startswith("A1")),
        "InSAR": ["A2"], "Huerta-Vergara": ["A3"], "Hidro-MX": ["D10"],
    }
    evidence.update({
        "basis": "Fresh retained-CSV recount and arithmetic over verified frozen SQL exports; no fresh live-database count.",
        "export_generation_time": export_manifest["generado_en"],
        "original": original,
        "extension": {
            "manifest_input_files": len(sources),
            "original_csvs_in_manifest": 0,
            "families": [{"family": f, "input_files": groups[f],
                          "source_ids": sorted(s["id"] for s in sources if family(s["id"]) == f)} for f in FAMILIES],
            "academic_parts": academic_parts,
        },
        "integrated_warehouse": {"base_tables": len(tables), "physical_rows": sum(tables.values()),
                                 "included_ingestion_control_rows": tables["control_ingesta_fuentes"]},
        "scope": "The warehouse includes national/regional reference data at mixed periods and spatial grains. Physical rows are not independent observations. The 63-municipality analytical view does not delimit all warehouse contents.",
    })
    return evidence


def font_path(bold: bool = False) -> str:
    fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    candidates = [fonts / ("arialbd.ttf" if bold else "arial.ttf"),
                  Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    # Pillow also resolves bundled/system font names on platforms without Windows.
    fallback = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    ImageFont.truetype(fallback, 12)
    return fallback


class Drawing:
    """The SVG and PNG share this single physical-point layout."""

    def __init__(self):
        self.parts = []
        self.image = Image.new("RGB", (round(W * SCALE), round(H * SCALE)), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = {}
        self.font_regular, self.font_bold = font_path(), font_path(True)
        self.text_sizes = []

    def box(self, x, y, width, height, fill, border, radius=3, stroke=0.7):
        self.parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{width:.3f}" height="{height:.3f}" rx="{radius}" fill="{fill}" stroke="{border}" stroke-width="{stroke}"/>')
        self.draw.rounded_rectangle(tuple(round(v * SCALE) for v in (x, y, x + width, y + height)),
                                    radius=round(radius * SCALE), fill=fill, outline=border,
                                    width=max(1, round(stroke * SCALE)))

    def line(self, points, colour=None, width=1.1, arrow=False):
        colour = colour or COLOUR["line"]
        coordinates = " ".join(f"{x:.3f},{y:.3f}" for x, y in points)
        self.parts.append(f'<polyline points="{coordinates}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round"/>')
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=colour,
                       width=max(1, round(width * SCALE)), joint="curve")
        if arrow:
            (x0, y0), (x1, y1) = points[-2:]
            angle = math.atan2(y1 - y0, x1 - x0)
            size = 3.6
            triangle = [(x1, y1), (x1 - size * math.cos(angle) + size * .48 * math.sin(angle),
                                      y1 - size * math.sin(angle) - size * .48 * math.cos(angle)),
                        (x1 - size * math.cos(angle) - size * .48 * math.sin(angle),
                         y1 - size * math.sin(angle) + size * .48 * math.cos(angle))]
            self.parts.append('<polygon points="' + " ".join(f"{x:.3f},{y:.3f}" for x, y in triangle) + f'" fill="{colour}"/>')
            self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in triangle], fill=colour)

    def text(self, x, y, value, size=8.5, bold=False, colour=None, anchor="start", max_width=None):
        check(size >= MIN_FONT_PT, f"Text smaller than {MIN_FONT_PT} pt")
        colour = colour or COLOUR["ink"]
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(self.font_bold if bold else self.font_regular, math.ceil(size * SCALE))
        font = self.fonts[key]
        if max_width is not None:
            check(self.draw.textlength(value, font=font) <= max_width * SCALE,
                  f"Text exceeds its allocated width: {value}")
        self.text_sizes.append(size)
        self.parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{colour}">{escape(value)}</text>')
        self.draw.text((round(x * SCALE), round(y * SCALE)), value, font=font, fill=colour,
                       anchor={"start": "ls", "middle": "ms", "end": "rs"}[anchor])

    def save(self):
        svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_CM}cm" height="{HEIGHT_CM}cm" viewBox="0 0 {W:.6f} {H:.6f}" role="img" aria-labelledby="title desc">\n'
               '<title id="title">Original and extended input corpus of the integrated water data warehouse</title>\n'
               '<desc id="desc">The two original CSVs and the 62 additional manifest input files feed integration ETL, a shared warehouse, and the RDF graph, map and queries. Discarded billing rows branch away from the retained facts.</desc>\n'
               '<g font-family="Arial, DejaVu Sans, sans-serif">\n' + "\n".join(self.parts) + '\n</g>\n</svg>\n')
        (OUT / "figura_corpus_fuentes.svg").write_text(svg, encoding="utf-8", newline="\n")
        self.image.save(OUT / "figura_corpus_fuentes.png", dpi=(DPI, DPI), optimize=True)


def render(data: dict):
    f = lambda n: f"{n:,}"
    original = data["original"]
    groups = {x["family"]: x["input_files"] for x in data["extension"]["families"]}
    warehouse = data["integrated_warehouse"]
    d = Drawing()
    left_width, right_x = 194, 205
    d.box(.5, .5, left_width - 1, 111.5, COLOUR["teal_fill"], COLOUR["teal_border"], radius=4)
    d.box(right_x, .5, W - right_x - .5, 111.5, COLOUR["purple_fill"], COLOUR["purple_border"], radius=4)
    d.text(9, 13.5, "Original study", 10, True, COLOUR["teal"])
    d.text(9, 24.5, f'{original["retained_csv_files"]} retained CSV files', 8.5, colour=COLOUR["teal"])
    d.text(right_x + 9, 13.5, f'Extension: {data["extension"]["manifest_input_files"]} manifest input files', 10, True, COLOUR["purple"], max_width=W - right_x - 18)
    d.text(right_x + 9, 24.5, "Files/packages; the original two CSVs are excluded", 8, colour=COLOUR["purple"], max_width=W - right_x - 18)
    d.line([(8, 29), (left_width - 8, 29)], COLOUR["teal_border"], .6)
    d.line([(right_x + 8, 29), (W - 9, 29)], COLOUR["purple_border"], .6)

    d.text(9, 39, "SACMEX billing (Jan–Jun 2019)", 8.5, True, max_width=left_width - 18)
    for x, text in [(8, f'{f(original["sacmex_source_rows"])} raw rows'),
                    (106, f'{f(original["sacmex_fact_rows"])} fact rows')]:
        d.box(x, 44, 80, 17, COLOUR["white"], COLOUR["teal_border"], radius=2)
        d.text(x + 40, 55.5, text, 8.5, anchor="middle", max_width=75)
    d.line([(88, 52.5), (106, 52.5)], COLOUR["teal"], 1, arrow=True)
    d.line([(97, 52.5), (97, 66.5)], COLOUR["teal"], 1, arrow=True)
    d.text(97, 76.5, f'{f(original["sacmex_excluded_rows"])} excluded', 8, colour=COLOUR["muted"], anchor="middle")
    d.text(9, 88.5, "Open-Meteo weather (Jan–Jun 2019)", 8.5, True, max_width=left_width - 18)
    for x, text in [(8, f'{f(original["open_meteo_hourly_rows"])} hourly rows'),
                    (106, f'{f(original["open_meteo_daily_rows"])} daily rows')]:
        d.box(x, 93, 80, 16, COLOUR["white"], COLOUR["teal_border"], radius=2)
        d.text(x + 40, 104.5, text, 8.5, anchor="middle", max_width=75)
    d.line([(88, 101), (106, 101)], COLOUR["teal"], 1, arrow=True)

    row_labels = [("INEGI", "SACMEX / ADIP"), ("CONAGUA / SMN", "SHCP"), ("CONAPO", "Academic")]
    for row, labels in enumerate(row_labels):
        y = 40 + row * 22.5
        for col, label in enumerate(labels):
            x, width = (214, 114) if col == 0 else (337, W - 346)
            d.box(x, y, width, 18, COLOUR["white"], COLOUR["purple_border"], radius=2, stroke=.55)
            d.text(x + 6, y + 12.5, label, 8.5, max_width=width - 28)
            d.text(x + width - 6, y + 12.5, str(groups[label]), 9, True, COLOUR["purple"], anchor="end")

    # Retained and added inputs converge on the same integration process.
    d.line([(97, 112), (97, 119), (49, 119)], width=1.05)
    d.line([((right_x + W) / 2, 112), ((right_x + W) / 2, 119), (49, 119), (49, 124)], width=1.05, arrow=True)
    y, height = 124, 34
    d.box(.5, y, 97, height, COLOUR["neutral"], COLOUR["neutral_border"])
    d.text(49, y + 13, "Integration ETL", 9.5, True, anchor="middle")
    d.text(49, y + 25, "Clean · aggregate · link", 8, anchor="middle", max_width=90)
    d.line([(98, y + 17), (122, y + 17)], width=1.2, arrow=True)
    d.box(122, y, 206, height, COLOUR["neutral"], COLOUR["neutral_border"])
    d.text(225, y + 11, "Integrated warehouse", 9.5, True, anchor="middle")
    d.text(225, y + 22, f'{warehouse["base_tables"]} tables · {f(warehouse["physical_rows"])} rows', 9.5, True, anchor="middle")
    d.text(225, y + 31, f'including {warehouse["included_ingestion_control_rows"]} ingestion-control rows', 8, anchor="middle")
    d.line([(328, y + 17), (352, y + 17)], width=1.2, arrow=True)
    d.box(352, y, W - 352.5, height, COLOUR["neutral"], COLOUR["neutral_border"])
    d.text((352 + W) / 2, y + 13, "RDF graph", 9.5, True, anchor="middle")
    d.text((352 + W) / 2, y + 25, "Map + SQL/SPARQL", 8.5, anchor="middle", max_width=W - 360)

    d.text(0, 166, "National/regional reference data; mixed periods and grains. Rows are not independent observations.", 8, colour=COLOUR["muted"], max_width=W)
    stamp = datetime.strptime(data["export_generation_time"], "%Y-%m-%d %H:%M UTC").strftime("%d %b %Y")
    d.text(0, 176, f"Counts from the archived SQL export ({stamp}); input versions fixed by SHA-256.", 8, colour=COLOUR["muted"], max_width=W)
    d.save()
    return {"width_cm": WIDTH_CM, "height_cm": HEIGHT_CM, "png_dpi": DPI,
            "png_pixels": list(d.image.size), "minimum_font_pt": min(d.text_sizes),
            "font": "Arial" if Path(d.font_regular).name.lower() == "arial.ttf" else "DejaVu Sans"}


def main():
    data = calculate()
    data["figure"] = render(data)
    data["outputs"] = {name: {"sha256": sha((OUT / name).read_bytes())}
                       for name in ["figura_corpus_fuentes.svg", "figura_corpus_fuentes.png"]}
    (OUT / "evidencia_corpus_fuentes.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"original": data["original"], "extension_files": data["extension"]["manifest_input_files"],
                      "warehouse": data["integrated_warehouse"], "figure": data["figure"]}, indent=2))


if __name__ == "__main__":
    main()
