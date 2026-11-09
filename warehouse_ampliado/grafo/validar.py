"""Invariantes RDF y de soporte poblacional; no necesita PostgreSQL ni morph-kgc."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import re

import rdflib
from rdflib.namespace import OWL, RDF, RDFS

AGUA = rdflib.Namespace("https://w3id.org/cdmx/agua/")
GEO = rdflib.Namespace("http://www.opengis.net/ont/geosparql#")


def comprobar(g: rdflib.Graph) -> list[tuple[bool, str]]:
    """Devuelve verificaciones sin modificar el grafo ni completar datos ausentes."""
    pruebas = []
    simetrica_rdf = rdflib.URIRef(str(RDF) + "SymmetricProperty")
    pruebas.append((not any(g.triples((None, RDF.type, simetrica_rdf))),
                    "sin rdf:SymmetricProperty: la clase estandar pertenece a OWL"))
    for pred, clase in ((AGUA.sharesBoundaryWith, AGUA.Municipality),
                        (GEO.sfTouches, AGUA.Neighbourhood),
                        (AGUA.touchesAcrossCityLimit, AGUA.Neighbourhood)):
        pares = set(g.subject_objects(pred))
        pruebas.append((all(s != o and (o, s) in pares for s, o in pares),
                        f"{pred.split('/')[-1]}: simetria sin autoenlaces"))
        pruebas.append((all((s, RDF.type, clase) in g and (o, RDF.type, clase) in g for s, o in pares),
                        f"{pred.split('/')[-1]}: extremos de la clase territorial correcta"))
        if pred != GEO.sfTouches:
            pruebas.append(((pred, RDF.type, OWL.SymmetricProperty) in g,
                            f"{pred.split('/')[-1]} declarado owl:SymmetricProperty"))
    cruces = set(g.subject_objects(AGUA.touchesAcrossCityLimit))
    pruebas.append((all((s, GEO.sfTouches, o) in g for s, o in cruces),
                    "touchesAcrossCityLimit conserva la relacion sfTouches"))
    pruebas.append(((AGUA.touchesAcrossCityLimit, RDFS.subPropertyOf, GEO.sfTouches) in g,
                    "touchesAcrossCityLimit es subpropiedad de sfTouches"))
    municipios = {s: set(g.objects(s, AGUA.inMunicipality)) for s in g.subjects(RDF.type, AGUA.Neighbourhood)}
    pruebas.append((all(len(ms) == 1 and all((m, RDF.type, AGUA.Municipality) in g for m in ms)
                        for ms in municipios.values()), "cada colonia pertenece a un municipio del grafo"))

    def estado(s):
        ms = municipios.get(s, set())
        return str(next(iter(ms))).rsplit('/', 1)[-1][:2] if len(ms) == 1 else None

    pruebas.append((all(estado(s) is not None and estado(o) is not None and
                        (estado(s) == '09') != (estado(o) == '09') for s, o in cruces),
                    "cada touchesAcrossCityLimit une CDMX con otro estado"))

    nulos = {"", "None", "none", "NULL", "null", "nan", "NaN", "#N/A", "N/A"}
    falsos = [(s, p, o) for s, p, o in g if
              (isinstance(o, rdflib.Literal) and str(o) in nulos) or
              (isinstance(o, rdflib.URIRef) and str(o).rsplit('/', 1)[-1] in nulos)]
    pruebas.append((not falsos, f"valores ausentes convertidos en literales o recursos: {len(falsos)}"))
    invalidos = [o for _, _, o in g if isinstance(o, rdflib.Literal) and
                 (getattr(o, "ill_typed", False) or
                  (o.datatype == rdflib.XSD.decimal and not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", str(o))))]
    pruebas.append((not invalidos, f"literales con forma lexica incompatible con su datatype: {len(invalidos)}"))

    colonias = set(g.subjects(RDF.type, AGUA.Neighbourhood))
    antiguas = (AGUA.billedLitresPerDay, AGUA.shortageReportsPerThousand, AGUA.leakReportsPerThousand)
    ambiguas = [s for s in colonias if any((s, p, None) in g for p in antiguas)]
    pruebas.append((not ambiguas, f"colonias con tasas sin distinguir soporte proxy: {len(ambiguas)}"))

    def numero(s, p):
        valores = list(g.objects(s, p))
        if not valores:
            return None
        if len(valores) != 1:
            raise ValueError("propiedad numerica repetida")
        n = Decimal(str(valores[0]))
        if not n.is_finite() or n < 0:
            raise ValueError("numero negativo o no finito")
        return n

    errores = []
    tasas = ((AGUA.proxyBilledLitresPerDay, AGUA.billedDomesticVolumeM3, Decimal(181), Decimal('.1')),
             (AGUA.proxyShortageReportsPerThousand, AGUA.shortageReportCount, Decimal(1), Decimal('.01')),
             (AGUA.proxyLeakReportsPerThousand, AGUA.leakReportCount, Decimal(1), Decimal('.01')))
    for s in colonias:
        try:
            total = numero(s, AGUA.matchedUtilityNeighbourhoods)
            con_pob = numero(s, AGUA.utilityNeighbourhoodsWithPopulation)
            con_dom = numero(s, AGUA.utilityNeighbourhoodsWithDomesticVolume)
            poblacion = numero(s, AGUA.ratePopulationProxy)
            if total is None:
                if any(numero(s, p) is not None for p in
                       (AGUA.utilityNeighbourhoodsWithPopulation, AGUA.utilityNeighbourhoodsWithDomesticVolume,
                        AGUA.ratePopulationProxy, *(p for tasa in tasas for p in tasa[:2]))):
                    raise ValueError("datos proxy sin unidades SACMEX enlazadas")
                continue
            if con_pob is None or con_dom is None or max(con_pob, con_dom) > total:
                raise ValueError("conteos de cobertura ausentes o incoherentes")
            for pred, numerador, dias, precision in tasas:
                tasa, n = numero(s, pred), numero(s, numerador)
                completo = total > 0 and con_pob == total and poblacion is not None and poblacion > 0
                if pred == AGUA.proxyBilledLitresPerDay:
                    completo = completo and con_dom == total
                esperado = (n * 1000 / (poblacion * dias)).quantize(precision, rounding=ROUND_HALF_UP) \
                    if completo and n is not None else None
                if tasa != esperado:
                    raise ValueError(f"{pred.split('/')[-1]} no coincide con su soporte y formula")
        except (ValueError, ArithmeticError) as exc:
            errores.append(f"{s}: {exc}")
    pruebas.append((not errores, f"colonias con denominador, cobertura o aritmetica proxy incoherentes: {len(errores)}"
                    + (f" ({errores[0]})" if errores else "")))
    return pruebas
