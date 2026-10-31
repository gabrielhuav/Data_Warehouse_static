"""Compara palabra por palabra el PDF LNCS (camera-ready) con el PDF exportado del Word IJCOPI.

Ignora lo que la conversion cambia a proposito: encabezados y pies de pagina, el bloque
de autores, el estilo de las citas y la lista de referencias. Todo lo demas deberia
coincidir; las diferencias que queden se imprimen con contexto.
"""
import collections
import difflib
import re
import sys

import pymupdf

LNCS, WORD = sys.argv[1:3]
sys.stdout.reconfigure(encoding="utf-8")


def texto(ruta, quitar):
    d = pymupdf.open(ruta)
    partes = []
    for p in d:
        t = p.get_text("text", flags=pymupdf.TEXT_DEHYPHENATE)
        for patron in quitar:
            t = re.sub(patron, " ", t, flags=re.M)
        partes.append(t)
    t = "\n".join(partes)
    t = t[t.index("Abstract."):]
    corte = [m.start() for m in re.finditer(r"^\s*References\s*$", t, flags=re.M)]
    return t[:corte[-1]] if corte else t


lncs = texto(LNCS, [
    r"^\s*A Data Warehouse for Water Management in Mexico City\s*\d*\s*$",
    r"^\s*\d+\s+E\. U\. Velázquez Arrieta et al\.\s*$",
    r"^\s*\d+\s*$",
    r"\[\d+(?:\s*,\s*\d+)*\]",
])
word = texto(WORD, [
    r"^.*International Journal of Combinatorial Optimization Problems and Informatics.*$",
    r"^.*Editorial Académica Dragón Azteca.*$",
    r"^\s*\d+\s*$",
    r"\((?:[^()]*?,\s*)?\d{4}(?:;[^()]*?\d{4})*\)",
    r"^\s*Article information\s*$", r"^\s*Received:\s*$", r"^\s*Accepted:\s*$",
])


def palabras(t):
    t = t.replace("­", "")
    return re.findall(r"[\w.%-]+|[^\w\s]", t)


# LaTeX parte palabras al final de linea; se unen si la palabra completa existe en el Word.
vocab = set(palabras(word))
lncs = re.sub(r"(\w+)-\s*\n\s*(\w+)",
              lambda m: m.group(1) + m.group(2) if m.group(1) + m.group(2) in vocab else m.group(1) + "-" + m.group(2),
              lncs)
a, b = palabras(lncs), palabras(word)
print("palabras LNCS:", len(a), "palabras Word:", len(b))
sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        continue
    ctx = " ".join(a[max(0, i1 - 6):i1])
    print(f"\n[{op}] ...{ctx}")
    print("   LNCS:", " ".join(a[i1:i2])[:400])
    print("   WORD:", " ".join(b[j1:j2])[:400])

# Palabras que aparecen distinto numero de veces (detecta texto perdido aunque cambie de lugar)
ca, cb = collections.Counter(w.lower() for w in a if w[0].isalnum()), collections.Counter(w.lower() for w in b if w[0].isalnum())
falta = {w: ca[w] - cb[w] for w in ca if ca[w] > cb[w]}
sobra = {w: cb[w] - ca[w] for w in cb if cb[w] > ca[w]}
print("\nen LNCS y no en Word:", dict(sorted(falta.items())))
print("en Word y no en LNCS:", dict(sorted(sobra.items())))
