"""Comprueba que todo lo que la version extendida agrega respecto a la base este en amarillo.

Toma de la v1 solo el texto SIN resaltar y lo compara palabra por palabra con la v0:
si el amarillo esta completo, ese texto es la v0 con supresiones y nada mas. Imprime
cada insercion o sustitucion sin resaltar, que es lo que habria que revisar; la
renumeracion automatica de tablas, figuras y secciones aparece ahi y es esperable.

Uso: py -3 -I verificar_amarillo.py <v0.docx> <v1.docx>
"""
import difflib
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")


def runs_de(doc):
    """Todos los w:r del cuerpo, en orden, incluidas tablas e hipervinculos."""
    return doc.element.body.iter(qn("w:r"))


def palabras(doc, solo_sin_resaltar):
    trozos = []
    for r in runs_de(doc):
        hl = r.find(qn("w:rPr") + "/" + qn("w:highlight")) is not None
        if solo_sin_resaltar and hl:
            trozos.append(" ")
            continue
        trozos.append("".join(t.text or "" for t in r.iter(qn("w:t"))))
        if r.find(qn("w:br")) is not None or r.find(qn("w:tab")) is not None:
            trozos.append(" ")
    texto = "".join(trozos)
    return re.findall(r"[\w.%-]+|[^\w\s]", texto)


v0 = palabras(Document(sys.argv[1]), False)
v1 = palabras(Document(sys.argv[2]), True)
print(f"v0: {len(v0)} palabras; v1 sin resaltar: {len(v1)} palabras")
sm = difflib.SequenceMatcher(a=v0, b=v1, autojunk=False)
sin_marcar = 0
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op in ("insert", "replace"):
        sin_marcar += j2 - j1
        print(f"[{op}] ...{' '.join(v0[max(0, i1 - 6):i1])}")
        print("   v0:", " ".join(v0[i1:i2])[:200])
        print("   v1:", " ".join(v1[j1:j2])[:200])
print(f"\npalabras agregadas sin amarillo: {sin_marcar}")
