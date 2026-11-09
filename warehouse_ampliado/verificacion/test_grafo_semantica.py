"""Regresiones del soporte proxy, ausencias y semantica OWL del grafo.

    python -m unittest discover -s warehouse_ampliado/verificacion -p test_grafo_semantica.py
"""
from pathlib import Path
import sys
import unittest

import rdflib
from rdflib.namespace import OWL, RDF

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "grafo"))
from validar import AGUA, GEO, comprobar  # noqa: E402
from materializar import huella  # noqa: E402


class SemanticaGrafo(unittest.TestCase):
    def setUp(self):
        self.g = rdflib.Graph().parse(Path(__file__).resolve().parents[1] / "grafo" / "esquema_zm.ttl")
        self.c = AGUA["coloniaConapo/090010001"]
        self.g.add((self.c, RDF.type, AGUA.Neighbourhood))
        self.g.add((self.c, AGUA.inMunicipality, AGUA["municipio/09001"]))
        self.g.add((AGUA["municipio/09001"], RDF.type, AGUA.Municipality))

    def poner(self, predicado, valor):
        self.g.set((self.c, predicado, rdflib.Literal(valor)))

    def fallos(self):
        return [texto for valido, texto in comprobar(self.g) if not valido]

    def proxy_completo(self):
        # La poblacion oficial (10) difiere de la proxy (2000): nunca es el divisor de estas tasas.
        for p, v in ((AGUA.population, 10), (AGUA.ratePopulationProxy, 2000),
                     (AGUA.matchedUtilityNeighbourhoods, 1), (AGUA.utilityNeighbourhoodsWithPopulation, 1),
                     (AGUA.utilityNeighbourhoodsWithDomesticVolume, 1), (AGUA.billedDomesticVolumeM3, 362),
                     (AGUA.shortageReportCount, 100), (AGUA.leakReportCount, 20),
                     (AGUA.proxyBilledLitresPerDay, 1), (AGUA.proxyShortageReportsPerThousand, 50),
                     (AGUA.proxyLeakReportsPerThousand, 10)):
            self.poner(p, v)

    def test_colonia_sin_enlace_no_inventa_datos(self):
        self.assertEqual(self.fallos(), [])

    def test_proxy_coherente_con_su_denominador(self):
        self.proxy_completo()
        self.assertEqual(self.fallos(), [])

    def test_tasa_con_poblacion_conapo_se_rechaza(self):
        self.proxy_completo()
        self.poner(AGUA.proxyLeakReportsPerThousand, 2000)
        self.assertTrue(any("aritmetica" in f for f in self.fallos()))

    def test_soporte_poblacional_incompleto_omite_tasas(self):
        self.proxy_completo()
        self.poner(AGUA.matchedUtilityNeighbourhoods, 2)
        self.poner(AGUA.utilityNeighbourhoodsWithDomesticVolume, 2)
        for p in (AGUA.proxyBilledLitresPerDay, AGUA.proxyShortageReportsPerThousand, AGUA.proxyLeakReportsPerThousand):
            self.g.remove((self.c, p, None))
        self.assertEqual(self.fallos(), [])
        self.poner(AGUA.proxyLeakReportsPerThousand, 0)
        self.assertTrue(self.fallos())  # La ausencia tampoco se transforma en cero.

    def test_subtotal_domestico_ausente_no_suprime_reportes_validos(self):
        self.proxy_completo()
        self.poner(AGUA.utilityNeighbourhoodsWithDomesticVolume, 0)
        self.g.remove((self.c, AGUA.billedDomesticVolumeM3, None))
        self.g.remove((self.c, AGUA.proxyBilledLitresPerDay, None))
        self.assertEqual(self.fallos(), [])

    def test_none_no_es_literal_ni_recurso(self):
        self.g.add((self.c, AGUA.inMunicipality, AGUA["municipio/None"]))
        self.poner(AGUA.ratePopulationProxy, "None")
        self.assertTrue(any("ausentes" in f for f in self.fallos()))

    def test_clase_simetrica_pertenece_a_owl(self):
        self.g.remove((AGUA.sharesBoundaryWith, RDF.type, OWL.SymmetricProperty))
        self.g.add((AGUA.sharesBoundaryWith, RDF.type, rdflib.URIRef(str(RDF) + "SymmetricProperty")))
        self.assertTrue(any("rdf:SymmetricProperty" in f for f in self.fallos()))

    def test_cruce_necesita_colindancia_base_y_dos_direcciones(self):
        otra = AGUA["coloniaConapo/150010001"]
        self.g.add((otra, RDF.type, AGUA.Neighbourhood))
        self.g.add((otra, AGUA.inMunicipality, AGUA["municipio/15001"]))
        self.g.add((AGUA["municipio/15001"], RDF.type, AGUA.Municipality))
        self.g.add((self.c, AGUA.touchesAcrossCityLimit, otra))
        self.assertTrue(any("simetria" in f for f in self.fallos()))
        self.assertTrue(any("conserva" in f for f in self.fallos()))
        self.g.add((otra, AGUA.touchesAcrossCityLimit, self.c))
        self.g.add((self.c, GEO.sfTouches, otra))
        self.g.add((otra, GEO.sfTouches, self.c))
        self.assertEqual(self.fallos(), [])

    def test_huella_estable_tras_serializar_decimal_sql_cero(self):
        for numero in ("0", "0.00", "362.5000", "1000", "-0"):
            with self.subTest(numero=numero):
                g = rdflib.Graph()
                g.add((self.c, AGUA.billedDomesticVolumeM3,
                       rdflib.Literal(numero, datatype=rdflib.XSD.decimal, normalize=False)))
                publicado = rdflib.Graph().parse(data=g.serialize(format="turtle"), format="turtle")
                self.assertEqual(huella(g), huella(publicado))
        otro = rdflib.Graph()
        otro.add((self.c, AGUA.billedDomesticVolumeM3, rdflib.Literal("1", datatype=rdflib.XSD.decimal)))
        self.assertNotEqual(huella(g), huella(otro))

    def test_decimal_con_exponente_no_es_lexico_xsd_decimal(self):
        self.g.add((self.c, AGUA.billedDomesticVolumeM3,
                    rdflib.Literal("1E+3", datatype=rdflib.XSD.decimal, normalize=False)))
        self.assertTrue(any("forma lexica" in f for f in self.fallos()))


if __name__ == "__main__":
    unittest.main()
