"""Pasa el articulo LNCS a la plantilla Word de IJCOPI.

Con dw_agua_icokg2026.tex (el camera-ready enviado a Springer) produce la version
base: el texto se conserva palabra por palabra y solo cambia lo que exige la
plantilla (citas y referencias en APA 7, numeracion explicita de secciones, tablas,
figura, ecuacion y listado con el formato de la plantilla, declaraciones finales).

Con dw_agua_ijcopi.tex (la version extendida) hace lo mismo y ademas resalta en
amarillo lo marcado como nuevo respecto al camera-ready: \\nuevo{...} dentro de un
parrafo y el entorno nuevobloque para secciones, parrafos, tablas o figuras
enteras. Las referencias nuevas llevan "!" al inicio en REFERENCIAS.

Uso: py -3 -I latex_a_ijcopi.py <tex> <plantilla.docx> <carpeta_imagenes> <salida.docx>
"""
import copy
import re
import sys
import unicodedata

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph
from lxml import etree

TEX, PLANTILLA, IMGS, SALIDA = sys.argv[1:5]

NBSP = "\u00a0"
NNBSP = "\u202f"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
avisos = []

# ---------------------------------------------------------------- citas APA 7
CITAS = {
    "abecker2014": (["Abecker", "Brauer", "Magoutas", "Mentzas", "Papageorgiou", "Quenzer"], "2014"),
    "berro2015": (["Berro", "Megdiche", "Teste"], "2015"),
    "carhomburg2022": (["Car", "Homburg"], "2022"),
    "hill2023": (["Hill", "Dunham", "Larsen", "Collins"], "2023"),
    "kimball": (["Kimball", "Ross"], "2013"),
    "purves2018": (["Purves", "Clough", "Jones", "Hall", "Murdock"], "2018"),
    "roussey2023": (["Roussey", "Guéret", "Laporte"], "2023"),
    "sacmex": (["SACMEX"], "2023"),
    "sandve2013": (["Sandve", "Nekrutenko", "Taylor", "Hovig"], "2013"),
    "soares2019": (["Soares", "Leite", "Teixeira", "Lopes", "Silva"], "2019"),
    "vassiliadis2009": (["Vassiliadis"], "2009"),
    "vetro2016": (["Vetrò", "Canova", "Torchiano", "Orozco Minotas", "Iemma", "Morando"], "2016"),
    "villa2026": (["Villa Vargas", "Hurtado Avilés", "Climent Hernández"], "2026"),
    "r2rml": (["World Wide Web Consortium"], "2012"),
    "datacube": (["World Wide Web Consortium"], "2014"),
    # Solo en la version extendida
    "velazquez2026icokg": (["Velázquez Arrieta", "Pulido Morales", "García López", "Hernández Martínez",
                            "Hurtado Avilés"], "in press"),
    "sacmex2026": (["SACMEX"], "2026"),
    "liu2008": (["Liu", "Ting", "Zhou"], "2008"),
    "breunig2000": (["Breunig", "Kriegel", "Ng", "Sander"], "2000"),
    "saito2015": (["Saito", "Rehmsmeier"], "2015"),
    "medina2022": (["Medina-Rivas", "Rodríguez-Tapia", "Morales-Novelo", "Revollo-Fernández"], "2022"),
    "medina2025": (["Medina-Rivas", "Morales-Novelo", "Rodríguez-Tapia", "Revollo-Fernández"], "2025"),
    "ramosbueno2021": (["Ramos-Bueno", "Perevochtchikova", "Chang"], "2021"),
    "ramosbueno2024": (["Ramos-Bueno", "Galeana-Pizaña", "Perevochtchikova"], "2024"),
    "lippolis2025": (["Lippolis", "Lodi", "Nuzzolese"], "2025"),
    "inegi2021": (["Instituto Nacional de Estadística y Geografía"], "2021"),
    "infocdmx2022": (["INFO CDMX"], "2022"),
    # Ampliacion a la zona metropolitana. Cada una alimenta una tabla: ver control_ingesta_fuentes.
    "conapo2025a": (["CONAPO"], "2025a"),
    "conapo2025b": (["CONAPO"], "2025b"),
    "inegicngmd": (["Instituto Nacional de Estadística y Geografía"], "n.d."),
    "shcp2026": (["SHCP"], "2026"),
    "conagua2026a": (["CONAGUA"], "2026a"),
    "conagua2026b": (["CONAGUA"], "2026b"),
    "conaguacalidad": (["CONAGUA"], "n.d."),
    "smn2026": (["SMN"], "2026"),
    "khorrami2023": (["Khorrami", "Shirzaei", "Ghobadi-Far", "Werth", "Carlson", "Zhai"], "2023"),
    "sacmexreportes": (["SACMEX"], "n.d."),
}

# Referencias APA 7 por clave. Se escriben en orden alfabetico y solo las que el .tex
# declara en thebibliography. *...* = cursiva; "!" al inicio = referencia nueva (amarillo).
REFERENCIAS = {
    # Solo en la version extendida. La de ICOKG: confirmar serie, volumen y paginas cuando
    # Springer publique las memorias.
    "velazquez2026icokg": (
        "!Velázquez Arrieta, E. U., Pulido Morales, O. F., García López, E., Hernández Martínez, C. A., & Hurtado "
        "Avilés, G. (in press). Territorial information retrieval from heterogeneous open data through the "
        "construction of a data warehouse for water management in Mexico City. In *Proceedings of the 5th "
        "International Conference on Ontologies and Knowledge Graphs (ICOKG 2026)*. Springer."
    ),
    "sacmex2026": (
        "!SACMEX. (2026, August 28). *Consumo de agua: Consumo Agua (1° Semestre 2019)* [Data set, CSV, with data "
        "dictionary and clarifying note]. Portal de Datos Abiertos de la Ciudad de México, Agencia Digital de "
        "Innovación Pública. Retrieved October 18, 2026, from https://datos.cdmx.gob.mx/dataset/consumo-agua"
    ),
    "liu2008": (
        "!Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. In *2008 Eighth IEEE International "
        "Conference on Data Mining* (pp. 413–422). IEEE. https://doi.org/10.1109/ICDM.2008.17"
    ),
    "breunig2000": (
        "!Breunig, M. M., Kriegel, H.-P., Ng, R. T., & Sander, J. (2000). LOF: Identifying density-based local "
        "outliers. In *Proceedings of the 2000 ACM SIGMOD International Conference on Management of Data* "
        "(pp. 93–104). ACM. https://doi.org/10.1145/342009.335388"
    ),
    "medina2022": (
        "!Medina-Rivas, C. M., Rodríguez-Tapia, L., Morales-Novelo, J. A., & Revollo-Fernández, D. A. (2022). "
        "Spatial inequality of domestic water consumption in Mexico city. *Water Resources and Economics, 40*, "
        "100210. https://doi.org/10.1016/j.wre.2022.100210"
    ),
    "medina2025": (
        "!Medina-Rivas, C. M., Morales-Novelo, J. A., Rodríguez-Tapia, L., & Revollo-Fernández, D. A. (2025). "
        "Mexico city's decline in per capita domestic water use: A comprehensive spatial-temporal study. *Urban "
        "Water Journal, 22*(1), 1–15. https://doi.org/10.1080/1573062X.2024.2423400"
    ),
    "ramosbueno2021": (
        "!Ramos-Bueno, A., Perevochtchikova, M., & Chang, H. (2021). Socio-spatial analysis of residential water "
        "demand in Mexico City. *Tecnología y Ciencias del Agua, 12*(2), 59–110. "
        "https://doi.org/10.24850/j-tyca-2021-02-02"
    ),
    "ramosbueno2024": (
        "!Ramos-Bueno, A., Galeana-Pizaña, J. M., & Perevochtchikova, M. (2024). Urban water consumption analysis "
        "through a spatial panel modeling approach: A case study of Mexico City, 2004–2022. *Water Supply, 24*(9), "
        "3179–3195. https://doi.org/10.2166/ws.2024.191"
    ),
    "inegi2021": (
        "!Instituto Nacional de Estadística y Geografía. (2021). *Censo de Población y Vivienda 2020: Principales "
        "resultados por localidad (ITER), Ciudad de México* [Data set, CSV]. INEGI. "
        "https://www.inegi.org.mx/programas/ccpv/2020/"
    ),
    "infocdmx2022": (
        "!INFO CDMX [Instituto de Transparencia, Acceso a la Información Pública, Protección de Datos Personales y "
        "Rendición de Cuentas de la Ciudad de México]. (2022). *Resolución del recurso de revisión "
        "INFOCDMX/RR.IP.0679/2022* (Sujeto obligado: Sistema de Aguas de la Ciudad de México). "
        "https://documentosobligaciones.infocdmx.org.mx/ST/LTAIPRC-2016-OT/Art133/Fr01/2022/T02-INFOCDMX.RR.IP.0679.2022.pdf"
    ),
    "lippolis2025": (
        "!Lippolis, A. S., Lodi, G., & Nuzzolese, A. G. (2025). The Water Health Open Knowledge Graph. *Scientific "
        "Data, 12*, 274. https://doi.org/10.1038/s41597-025-04537-4"
    ),
    "conapo2025a": (
        "!CONAPO [Consejo Nacional de Población]. (2025a). *Índices de marginación* [Data set]. datos.gob.mx. "
        "https://www.datos.gob.mx/dataset/d8f2a534-bcee-4114-853d-82982a81ce24"
    ),
    "conapo2025b": (
        "!CONAPO [Consejo Nacional de Población]. (2025b). *Las metrópolis de México, 2020* [Data set]. datos.gob.mx. "
        "https://www.datos.gob.mx/dataset/da65ccd9-888c-4ce8-b3b5-6bd867be344d"
    ),
    "inegicngmd": (
        "!Instituto Nacional de Estadística y Geografía. (n.d.). *Censo Nacional de Gobiernos Municipales y "
        "Demarcaciones Territoriales de la Ciudad de México, 2019 and 2021 editions* [Data set]. Retrieved October "
        "31, 2026, from https://www.inegi.org.mx/programas/cngmd/2021/"
    ),
    "shcp2026": (
        "!SHCP [Secretaría de Hacienda y Crédito Público]. (2026). *Derechos de agua municipal* [Data set]. "
        "datos.gob.mx. https://www.datos.gob.mx/dataset/derechos_agua_municipal"
    ),
    "conagua2026a": (
        "!CONAGUA [Comisión Nacional del Agua]. (2026a). *Aguas subterráneas* [Data set]. datos.gob.mx. "
        "https://www.datos.gob.mx/dataset/aguas_subterraneas"
    ),
    "conagua2026b": (
        "!CONAGUA [Comisión Nacional del Agua]. (2026b). *Sistema de Información Hidrológica: Series diarias de "
        "presas* [Data set, 15 CSV files]. Retrieved October 30, 2026, from "
        "https://sih.conagua.gob.mx/basedatos/Presas/VBRMX.csv"
    ),
    "conaguacalidad": (
        "!CONAGUA [Comisión Nacional del Agua]. (n.d.). *Indicadores de calidad del agua* [Data set]. Retrieved "
        "October 31, 2026, from https://www.gob.mx/conagua/es/articulos/indicadores-de-calidad-del-agua?idiom=es"
    ),
    "smn2026": (
        "!SMN [Servicio Meteorológico Nacional]. (2026). *Monitor de Sequía de México: Municipios* [Data set]. "
        "CONAGUA. https://smn.conagua.gob.mx/tools/RESOURCES/Monitor%20de%20Sequia%20en%20Mexico/MunicipiosSequia.xlsx"
    ),
    "khorrami2023": (
        "!Khorrami, M., Shirzaei, M., Ghobadi-Far, K., Werth, S., Carlson, G., & Zhai, G. (2023). Groundwater volume "
        "loss in Mexico City constrained by InSAR and GRACE observations and mechanical models. *Geophysical "
        "Research Letters, 50*(5), e2022GL101962. https://doi.org/10.1029/2022GL101962"
    ),
    "sacmexreportes": (
        "!SACMEX. (n.d.). *Reportes de agua* [Data set, CSV]. Portal de Datos Abiertos de la Ciudad de México. "
        "https://datos.cdmx.gob.mx/dataset/reportes-de-agua"
    ),
    "saito2015": (
        "!Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when "
        "evaluating binary classifiers on imbalanced datasets. *PLoS ONE, 10*(3), e0118432. "
        "https://doi.org/10.1371/journal.pone.0118432"
    ),
    "abecker2014": (
        'Abecker, A., Brauer, T., Magoutas, B., Mentzas, G., Papageorgiou, N., & Quenzer, M. (2014). A sensor and '
        'semantic data warehouse for integrated water resource management. In *EnviroInfo 2014*. BIS-Verlag.'
    ),
    "berro2015": (
        'Berro, A., Megdiche, I., & Teste, O. (2015). A content-driven ETL processes for open data. In N. Bassiliades'
        ' et al. (Eds.), *New trends in database and information systems II*. Springer. '
        'https://doi.org/10.1007/978-3-319-10518-5_3'
    ),
    "carhomburg2022": (
        'Car, N. J., & Homburg, T. (2022). GeoSPARQL 1.1: Motivations, details and applications of the decadal update'
        ' to the most important geospatial LOD standard. *ISPRS International Journal of Geo-Information, 11*(2), '
        '117. https://doi.org/10.3390/ijgi11020117'
    ),
    "hill2023": (
        'Hill, D., Dunham, C., Larsen, D. A., & Collins, M. (2023). Operationalizing an open-source dashboard for '
        'wastewater-based surveillance. *MethodsX, 11*, 102299. https://doi.org/10.1016/j.mex.2023.102299'
    ),
    "kimball": (
        'Kimball, R., & Ross, M. (2013). *The data warehouse toolkit: The definitive guide to dimensional modeling* '
        '(3rd ed.). Wiley.'
    ),
    "purves2018": (
        'Purves, R. S., Clough, P., Jones, C. B., Hall, M. H., & Murdock, V. (2018). Geographic information '
        'retrieval. *Foundations and Trends in Information Retrieval, 12*(2–3), 164–318. '
        'https://doi.org/10.1561/1500000034'
    ),
    "roussey2023": (
        'Roussey, C., Guéret, C., & Laporte, M.-A. (2023). Editorial: Knowledge graph technologies—The next frontier '
        'of the food, agriculture, and water domains. *Frontiers in Artificial Intelligence, 6*, 1319844. '
        'https://doi.org/10.3389/frai.2023.1319844'
    ),
    "sacmex": (
        'SACMEX. (2023, February 2). *Consumo de agua: Consumo Agua (1er Semestre 2019)* [Data set, CSV]. Portal de '
        'Datos Abiertos de la Ciudad de México, Agencia Digital de Innovación Pública. Retrieved May 2026, from '
        'https://datos.cdmx.gob.mx/dataset/consumo-agua'
    ),
    "sandve2013": (
        'Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for reproducible '
        'computational research. *PLoS Computational Biology, 9*(10), e1003285. '
        'https://doi.org/10.1371/journal.pcbi.1003285'
    ),
    "soares2019": (
        'Soares, J., Leite, P., Teixeira, P., Lopes, N., & Silva, J. P. (2019). Data warehouse for the monitoring and'
        ' analysis of water supply and consumption. In I. Ramos, R. Quaresma, P. Resende da Silva, & T. Oliveira '
        '(Eds.), *Information systems for Industry 4.0*. Springer. https://doi.org/10.1007/978-3-030-14850-8_1'
    ),
    "vassiliadis2009": (
        'Vassiliadis, P. (2009). A survey of extract–transform–load technology. *International Journal of Data '
        'Warehousing and Mining, 5*(3), 1–27. https://doi.org/10.4018/jdwm.2009070101'
    ),
    "vetro2016": (
        'Vetrò, A., Canova, L., Torchiano, M., Orozco Minotas, C., Iemma, R., & Morando, F. (2016). Open data quality'
        ' measurement framework. *Government Information Quarterly, 33*(2), 325–337. '
        'https://doi.org/10.1016/j.giq.2016.02.001'
    ),
    "villa2026": (
        'Villa Vargas, J. M., Hurtado Avilés, G., & Climent Hernández, J. A. (2026). Cuando México tiembla: La '
        'historia contada por los datos. *AZCATL Revista de Divulgación en Ciencias, Ingeniería e Innovación, 4*(6), '
        '28–33. https://doi.org/10.24275/AZC2026E1004'
    ),
    "r2rml": (
        'World Wide Web Consortium. (2012, September 27). *R2RML: RDB to RDF mapping language* [W3C Recommendation]. '
        'https://www.w3.org/TR/r2rml/'
    ),
    "datacube": (
        'World Wide Web Consortium. (2014, January 16). *The RDF Data Cube vocabulary* [W3C Recommendation]. '
        'https://www.w3.org/TR/vocab-data-cube/'
    ),
}


def nombre_parentetico(autores):
    if len(autores) == 1:
        return autores[0]
    if len(autores) == 2:
        return f"{autores[0]} & {autores[1]}"
    return f"{autores[0]} et al."


def reemplazar_citas(texto):
    """\\cite -> APA. Narrativa si el texto previo ya nombra al autor."""
    def sustituir(m):
        claves = [k.strip() for k in m.group(1).split(",")]
        for k in claves:
            if k not in CITAS:
                raise KeyError(f"cita sin datos APA: {k}")
        previo = texto[: m.start()].rstrip()
        if len(claves) == 1:
            autores, anio = CITAS[claves[0]]
            cola = previo[-45:]
            if previo.endswith(autores[-1]) or (previo.endswith("et al.") and autores[0] in cola):
                return f" ({anio})"
        partes = sorted((nombre_parentetico(CITAS[k][0]), CITAS[k][1]) for k in claves)
        return " (" + "; ".join(f"{n}, {a}" for n, a in partes) + ")"
    return re.sub(r"~?\\cite\{([^}]*)\}", sustituir, texto)


# ------------------------------------------------------------- lectura LaTeX
ACENTOS = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303"}


def acentos(s):
    s = re.sub(r"\\([`'^\"~])\{\\i\}", lambda m: "i" + ACENTOS[m.group(1)], s)
    s = re.sub(r"\\([`'^\"~])\\i\b", lambda m: "i" + ACENTOS[m.group(1)], s)
    s = re.sub(r"\\([`'^\"~])\{([A-Za-z])\}", lambda m: m.group(2) + ACENTOS[m.group(1)], s)
    s = re.sub(r"\\([`'^\"~])([A-Za-z])", lambda m: m.group(2) + ACENTOS[m.group(1)], s)
    return unicodedata.normalize("NFC", s)


def sin_comentarios(tex):
    lineas = []
    for linea in tex.splitlines():
        if linea.lstrip().startswith("%"):
            continue
        lineas.append(re.sub(r"(?<!\\)%.*$", "", linea))
    return "\n".join(lineas)


def leer_grupo(s, i):
    """s[i] debe ser '{' (se saltan espacios). Devuelve (contenido, indice tras '}')."""
    while s[i] in " \n":
        i += 1
    if s[i] != "{":
        raise ValueError("se esperaba '{': " + s[i:i + 60])
    prof = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("llave sin cerrar: " + s[i:i + 60])


tex = acentos(sin_comentarios(open(TEX, encoding="utf8").read()))

# Numeracion de \label en el orden en que LaTeX la asigna.
NUM = {}
cont = {"sec": 0, "sub": 0, "tab": 0, "fig": 0, "subfig": 0}
actual = None
for m in re.finditer(r"\\(section|subsection)(\*?)\{|\\begin\{(table|figure|subfigure)\}|\\end\{subfigure\}|\\label\{([^}]*)\}", tex):
    if m.group(1) == "section" and not m.group(2):
        cont["sec"] += 1
        cont["sub"] = 0
        actual = str(cont["sec"])
    elif m.group(1) == "subsection" and not m.group(2):
        cont["sub"] += 1
        actual = f"{cont['sec']}.{cont['sub']}"
    elif m.group(3) == "table":
        cont["tab"] += 1
        actual = str(cont["tab"])
    elif m.group(3) == "figure":
        cont["fig"] += 1
        cont["subfig"] = 0
        actual = str(cont["fig"])
    elif m.group(3) == "subfigure":
        cont["subfig"] += 1
        actual = f"{cont['fig']}{'abcdefg'[cont['subfig'] - 1]}"
    elif m.group(0).startswith("\\end{subfigure}"):
        actual = str(cont["fig"])
    elif m.group(4):
        NUM[m.group(4)] = actual
NUM["lst:sparql"] = "1"

# ------------------------------------------------------- texto en linea -> runs
FORMATO = {"textbf": {"b": True}, "emph": {"i": True}, "textit": {"i": True},
           "texttt": {"tt": True}, "textsc": {"sc": True}}
TAMANOS = {"scriptsize": 14, "footnotesize": 16, "small": 18}
SIMBOLOS = {"LaTeX": "LaTeX", "copyright": "©", "ldots": "…", "textasciitilde": "~"}
IGNORAR = {"noindent", "centering", "hfill", "par", "unskip"}
GRIEGO = {"mu": "μ", "sigma": "σ", "epsilon": "ε", "alpha": "α", "beta": "β", "lambda": "λ"}
OPERADORES = {"pm": "±", "times": "×"}


def matematicas(s, fmt):
    out = []
    s = s.strip()
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                nombre = m.group(1)
                i += m.end()
                if nombre in GRIEGO:
                    out.append(dict(fmt, text=GRIEGO[nombre], i=True))
                elif nombre in OPERADORES:
                    antes = " " if out else ""
                    despues = " " if i < len(s) else ""
                    out.append(dict(fmt, text=antes + OPERADORES[nombre] + despues))
                elif nombre in ("left", "right"):
                    pass
                else:
                    avisos.append("math:\\" + nombre)
                continue
            if s[i + 1] == ",":
                out.append(dict(fmt, text=NNBSP))
            i += 2
            continue
        if c in "_^":
            i += 1
            if s[i] == "{":
                arg, i = leer_grupo(s, i)
            else:
                arg, i = s[i], i + 1
            for r in matematicas(arg, fmt):
                r["sub" if c == "_" else "sup"] = True
                out.append(r)
            continue
        if c.isalpha():
            out.append(dict(fmt, text=c, i=True))
        elif c != " ":
            out.append(dict(fmt, text=c))
        i += 1
    return out


def en_linea(s, fmt=None):
    fmt = dict(fmt or {})
    out, buf = [], []

    def vaciar():
        if buf:
            out.append(dict(fmt, text="".join(buf)))
            buf.clear()

    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)\*?", s[i:])
            if m:
                nombre = m.group(1)
                j = i + m.end()
                if nombre in FORMATO:
                    arg, j = leer_grupo(s, j)
                    vaciar()
                    out += en_linea(arg, {**fmt, **FORMATO[nombre]})
                elif nombre == "nuevo":
                    arg, j = leer_grupo(s, j)
                    vaciar()
                    out += en_linea(arg, {**fmt, "hl": True})
                elif nombre in ("icokg", "mbox"):
                    arg, j = leer_grupo(s, j)
                    vaciar()
                    out += en_linea(arg, fmt)
                elif nombre == "url":
                    arg, j = leer_grupo(s, j)
                    vaciar()
                    url = re.sub(r"\\([%_#&])", r"\1", arg)
                    out.append(dict(fmt, text=url, link=url))
                elif nombre == "href":
                    url, j = leer_grupo(s, j)
                    txt, j = leer_grupo(s, j)
                    vaciar()
                    for r in en_linea(txt, fmt):
                        r["link"] = re.sub(r"\\([%_#&])", r"\1", url)
                        out.append(r)
                elif nombre == "footnote":
                    arg, j = leer_grupo(s, j)
                    vaciar()
                    out.append({"fn": en_linea(arg)})
                elif nombre == "ref":
                    arg, j = leer_grupo(s, j)
                    buf.append(NUM[arg])
                elif nombre in TAMANOS:
                    vaciar()
                    fmt["size"] = TAMANOS[nombre]
                    while j < n and s[j] == " ":
                        j += 1
                elif nombre in SIMBOLOS:
                    buf.append(SIMBOLOS[nombre])
                    if s.startswith("{}", j):
                        j += 2
                    else:
                        while j < n and s[j] == " ":
                            j += 1
                elif nombre in IGNORAR:
                    while j < n and s[j] == " ":
                        j += 1
                else:
                    avisos.append("\\" + nombre)
                i = j
                continue
            ch = s[i + 1]
            if ch == "\\":
                vaciar()
                out.append({"br": True})
                i += 2
                while i < n and s[i] == " ":
                    i += 1
                continue
            if ch == ",":
                buf.append(NNBSP)
            elif ch in "%_&#${}":
                buf.append(ch)
            elif ch == " ":
                buf.append(" ")
            else:
                avisos.append("\\" + ch)
            i += 2
            continue
        if c == "{":
            arg, j = leer_grupo(s, i)
            vaciar()
            out += en_linea(arg, fmt)
            i = j
            continue
        if c == "$":
            j = s.index("$", i + 1)
            vaciar()
            out += matematicas(s[i + 1:j], fmt)
            i = j + 1
            continue
        if c == "~":
            buf.append(NBSP)
        elif s.startswith("---", i):
            buf.append("—")
            i += 3
            continue
        elif s.startswith("--", i):
            buf.append("–")
            i += 2
            continue
        elif s.startswith("``", i):
            buf.append("“")
            i += 2
            continue
        elif s.startswith("''", i):
            buf.append("”")
            i += 2
            continue
        elif c == "`":
            buf.append("‘")
        elif c == "'":
            buf.append("’")
        elif c != "}":
            buf.append(c)
        i += 1
    vaciar()
    return fusionar(out)


def fusionar(runs):
    out = []
    for r in runs:
        if out and "text" in r and "text" in out[-1]:
            a = {k: v for k, v in out[-1].items() if k != "text"}
            b = {k: v for k, v in r.items() if k != "text"}
            if a == b:
                out[-1]["text"] += r["text"]
                continue
        out.append(dict(r))
    return out


# True mientras se escribe el contenido de un entorno nuevobloque.
RESALTAR = [False]


def parrafo_latex(s):
    s = re.sub(r"\s+", " ", s).strip()
    return en_linea(reemplazar_citas(s), {"hl": True} if RESALTAR[0] else None)


def marcar(run):
    """Resalta un run que el conversor escribe por su cuenta (etiquetas, numeros)."""
    if RESALTAR[0]:
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return run


# --------------------------------------------------------- bloques del cuerpo
inicio = tex.index("\\begin{abstract}")
fin = tex.index("\\section*{Declaration on the Use of Generative AI}")
cuerpo = tex[inicio:fin]

bloques = []
TOKEN = re.compile(
    r"\\(section|subsection|subsubsection)(\*?)\{"
    r"|\\begin\{(table|figure|equation|lstlisting|itemize|abstract)\}"
    r"|\\keywords\{|\\maketitle|\\label\{[^}]*\}"
    r"|\\begin\{nuevobloque\}|\\end\{nuevobloque\}"
    r"|\\begin\{icokgblock\}|\\end\{icokgblock\}|\\begingroup|\\endgroup"
    r"|\\setlength\{[^}]*\}\{[^}]*\}")
pendiente = []
contador = {"sec": 0, "sub": 0}


def vaciar_texto():
    texto = "".join(pendiente)
    pendiente.clear()
    for trozo in re.split(r"\n\s*\n", texto):
        if trozo.strip():
            bloques.append(("p", trozo))


pos = 0
while True:
    m = TOKEN.search(cuerpo, pos)
    if not m:
        pendiente.append(cuerpo[pos:])
        vaciar_texto()
        break
    pendiente.append(cuerpo[pos:m.start()])
    pos = m.end()
    tok = m.group(0)
    if m.group(1):
        vaciar_texto()
        titulo, pos = leer_grupo(cuerpo, pos - 1)
        if m.group(1) == "section":
            contador["sec"] += 1
            contador["sub"] = 0
            bloques.append(("h1", f"{contador['sec']} ", titulo))
        elif m.group(1) == "subsection":
            contador["sub"] += 1
            bloques.append(("h2", f"{contador['sec']}.{contador['sub']} ", titulo))
        else:
            bloques.append(("runin", titulo))
    elif m.group(3):
        vaciar_texto()
        amb = m.group(3)
        cierre = cuerpo.index(f"\\end{{{amb}}}", pos)
        bloques.append((amb, cuerpo[pos:cierre]))
        pos = cierre + len(f"\\end{{{amb}}}")
    elif tok.startswith("\\keywords"):
        vaciar_texto()
        kw, pos = leer_grupo(cuerpo, pos - 1)
        bloques.append(("keywords", kw))
    elif tok in ("\\begin{nuevobloque}", "\\end{nuevobloque}"):
        vaciar_texto()
        bloques.append(("resaltar", tok.startswith("\\begin")))
    # el resto (maketitle, label, icokgblock, begingroup...) se descarta sin cortar parrafo

resumen = next(b[1] for b in bloques if b[0] == "abstract")
claves = next(b[1] for b in bloques if b[0] == "keywords")
bloques = [b for b in bloques if b[0] not in ("abstract", "keywords")]

# Declaraciones finales
cola = tex[fin:]
decl_ia = cola[cola.index("\\section*{Declaration on the Use of Generative AI}") + len("\\section*{Declaration on the Use of Generative AI}"):cola.index("\\end{icokgblock}")]
interes = cola[cola.index("\\section*{Disclosure of Interests}") + len("\\section*{Disclosure of Interests}"):cola.index("\\begingroup")]
claves_bib = re.findall(r"\\bibitem\{([^}]*)\}", cola)
citadas = {k.strip() for g in re.findall(r"\\cite\{([^}]*)\}", tex[:fin]) for k in g.split(",")}
assert set(claves_bib) <= set(CITAS) & set(REFERENCIAS), set(claves_bib) - (set(CITAS) & set(REFERENCIAS))
assert citadas == set(claves_bib), ("citada sin bibitem", citadas - set(claves_bib),
                                    "bibitem sin citar", set(claves_bib) - citadas)

# --------------------------------------------------------- escritura en Word
doc = Document(PLANTILLA)
body = doc.element.body
elems = list(body.iterchildren())
assert elems[0].xpath("string(.)").startswith("IJCOPI Manuscript Template"), "plantilla inesperada"
assert elems[6].tag == qn("w:tbl") and "Abstract." in elems[6].xpath("string(.)")
assert elems[-1].tag == qn("w:sectPr")
for e in elems[8:-1]:
    body.remove(e)

fn_id = [0]
partes_notas = [r.target_part for r in doc.part.rels.values() if r.reltype.endswith("/footnotes")]
parte_notas = partes_notas[0]
notas_xml = parse_xml(parte_notas.blob)


def formato_run(run, r):
    if r.get("b"):
        run.bold = True
    if r.get("i"):
        run.italic = True
    if r.get("tt"):
        run.font.name = "Courier New"
    if r.get("sc"):
        run.font.small_caps = True
    if r.get("sub"):
        run.font.subscript = True
    if r.get("sup"):
        run.font.superscript = True
    if r.get("size"):
        run.font.size = Pt(r["size"] / 2)
    if r.get("hl"):
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW


def escribir(par, runs):
    for r in runs:
        if r.get("br"):
            par.add_run().add_break()
        elif "fn" in r:
            nota(par, r["fn"])
        elif r.get("link"):
            rid = par.part.relate_to(r["link"], RT.HYPERLINK, is_external=True)
            h = OxmlElement("w:hyperlink")
            h.set(qn("r:id"), rid)
            run = par.add_run(r["text"])
            formato_run(run, r)
            run.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
            run.font.underline = True
            par._p.append(h)
            h.append(run._r)
        else:
            formato_run(par.add_run(r["text"]), r)


def nota(par, runs):
    fn_id[0] += 1
    nid = str(fn_id[0])
    fn = parse_xml(
        f'<w:footnote xmlns:w="{W}" w:id="{nid}"><w:p><w:pPr><w:spacing w:after="0"/><w:jc w:val="both"/></w:pPr>'
        f'<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:footnoteRef/></w:r>'
        f'<w:r><w:t xml:space="preserve"> </w:t></w:r></w:p></w:footnote>')
    p = Paragraph(fn[0], par._parent)
    escribir(p, runs)
    for r in p.runs:
        r.font.size = Pt(9)
    notas_xml.append(fn)
    ref = par.add_run()
    ref.font.superscript = True
    ref._r.append(parse_xml(f'<w:footnoteReference xmlns:w="{W}" w:id="{nid}"/>'))


def parrafo(estilo=None, alinear=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph(style=estilo)
    if alinear is not None:
        p.alignment = alinear
    return p


def encabezado(nivel, numero, titulo):
    p = doc.add_paragraph(style=f"Heading {nivel}")
    run = p.add_run(numero + "".join(r.get("text", "") for r in en_linea(titulo)))
    run.font.name = "Times New Roman"
    if "\\nuevo" in titulo:
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    marcar(run)


def leyenda(etiqueta, runs, junto_a_siguiente):
    p = doc.add_paragraph(style="IJCOPI Caption")
    marcar(p.add_run(etiqueta))
    escribir(p, runs)
    p.paragraph_format.keep_with_next = junto_a_siguiente
    return p


def tabla_formato(tabla, anchos, bordes=True, cabecera=True):
    tbl = tabla._tbl
    tblPr = tbl.tblPr
    for hijo in list(tblPr):
        tblPr.remove(hijo)
    tblPr.append(parse_xml(f'<w:tblW xmlns:w="{W}" w:w="0" w:type="auto"/>'))
    tblPr.append(parse_xml(f'<w:jc xmlns:w="{W}" w:val="center"/>'))
    tblPr.append(parse_xml(f'<w:tblLayout xmlns:w="{W}" w:type="fixed"/>'))
    tblPr.append(parse_xml(f'<w:tblLook xmlns:w="{W}" w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" '
                           f'w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'))
    grid = tbl.tblGrid
    for k, g in enumerate(grid.findall(qn("w:gridCol"))):
        g.set(qn("w:w"), str(anchos[k]))
    for f, fila in enumerate(tabla.rows):
        trPr = fila._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:jc xmlns:w="{W}" w:val="center"/>'))
        trPr.append(parse_xml(f'<w:cantSplit xmlns:w="{W}"/>'))
        for c, celda in enumerate(fila.cells):
            borde = ('<w:{0} w:val="single" w:sz="6" w:space="0" w:color="CFCFCF"/>' if bordes
                     else '<w:{0} w:val="nil"/>')
            relleno = '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED"/>' if (bordes and cabecera and f == 0) else ""
            viejo = celda._tc.tcPr
            if viejo is not None:
                celda._tc.remove(viejo)
            celda._tc.insert(0, parse_xml(
                f'<w:tcPr xmlns:w="{W}"><w:tcW w:w="{anchos[c]}" w:type="dxa"/><w:tcBorders>'
                + "".join(borde.format(lado) for lado in ("top", "left", "bottom", "right"))
                + f'</w:tcBorders>{relleno}<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
                  f'<w:bottom w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tcMar></w:tcPr>'))
            for p in celda.paragraphs:
                p.paragraph_format.space_after = Pt(2)


ALINEA = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER, "r": WD_ALIGN_PARAGRAPH.RIGHT,
          "Y": WD_ALIGN_PARAGRAPH.LEFT, "X": WD_ALIGN_PARAGRAPH.LEFT}
# Anchos (dxa) por etiqueta de tabla; una tabla sin entrada reparte 9,000 dxa con la
# primera columna al doble que las demas.
ANCHOS_TABLA = {"tab:cleaning": [4800, 1400, 1600], "tab:volumen_datos": [3200, 1600],
                "tab:top5_alcaldias": [3200, 2400], "tab:eval_ml": [2400, 2100, 2100, 2100],
                "tab:api_perf": [4900, 1500, 1500, 1500],
                "tab:percapita": [2900, 1400, 1700, 1700, 1700], "tab:sens": [3000, 1300, 1700, 1300, 1300]}


def anchos(etiqueta, n):
    if etiqueta in ANCHOS_TABLA:
        return ANCHOS_TABLA[etiqueta]
    unidad = 9000 // (n + 1)
    return [2 * unidad] + [unidad] * (n - 1)


def bloque_tabla(contenido):
    titulo, _ = leer_grupo(contenido, contenido.index("\\caption{") + len("\\caption"))
    etiqueta = re.search(r"\\label\{([^}]*)\}", contenido).group(1)
    numero = NUM[etiqueta]
    m = re.search(r"\\begin\{(tabularx?)\}", contenido)
    amb = m.group(1)
    j = m.end()
    if amb == "tabularx":
        _, j = leer_grupo(contenido, j)
    espec, j = leer_grupo(contenido, j)
    cuerpo_t = contenido[j:contenido.index(f"\\end{{{amb}}}")]
    columnas = re.sub(r"@\{\}|\||p\{[^}]*\}", lambda x: "l" if x.group(0).startswith("p") else "", espec)
    filas = []
    for fila in re.split(r"\\\\", cuerpo_t):
        fila = re.sub(r"\\(hline|toprule|midrule|bottomrule)", "", fila).strip()
        if fila:
            filas.append([c.strip() for c in re.split(r"(?<!\\)&", fila)])
    assert all(len(f) == len(columnas) for f in filas), (numero, columnas, filas)
    leyenda(f"Table {numero}. ", parrafo_latex(titulo), True)
    tabla = doc.add_table(rows=len(filas), cols=len(columnas))
    tabla_formato(tabla, anchos(etiqueta, len(columnas)))
    for f, fila in enumerate(filas):
        for c, texto in enumerate(fila):
            p = tabla.cell(f, c).paragraphs[0]
            p.alignment = ALINEA[columnas[c]] if f > 0 else (WD_ALIGN_PARAGRAPH.LEFT if c == 0 else WD_ALIGN_PARAGRAPH.CENTER)
            escribir(p, parrafo_latex(texto))
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def recuadro(forma):
    """Una imagen no admite resaltado: una figura nueva se marca con un borde amarillo."""
    if RESALTAR[0]:
        forma._inline.graphic.graphicData.pic.spPr.append(parse_xml(
            f'<a:ln xmlns:a="{A}" w="38100"><a:solidFill><a:srgbClr val="FFFF00"/></a:solidFill></a:ln>'))


def bloque_figura(contenido):
    subfiguras = re.findall(r"\\begin\{subfigure\}.*?\\end\{subfigure\}", contenido, flags=re.S)
    if not subfiguras:
        archivo = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", contenido).group(1)
        titulo, _ = leer_grupo(contenido, contenido.index("\\caption{") + len("\\caption"))
        numero = NUM[re.findall(r"\\label\{([^}]*)\}", contenido)[-1]]
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        recuadro(p.add_run().add_picture(f"{IMGS}/{archivo}", width=Cm(16.5)))
        leyenda(f"Fig. {numero}. ", parrafo_latex(titulo), False)
        return
    resto = contenido[contenido.rindex("\\end{subfigure}"):]
    titulo, _ = leer_grupo(resto, resto.index("\\caption{") + len("\\caption"))
    numero = NUM[re.findall(r"\\label\{([^}]*)\}", resto)[-1]]
    tabla = doc.add_table(rows=2, cols=len(subfiguras))
    tabla_formato(tabla, [4986] * len(subfiguras), bordes=False)
    for k, sub in enumerate(subfiguras):
        archivo = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", sub).group(1)
        sub_titulo, _ = leer_grupo(sub, sub.index("\\caption{") + len("\\caption"))
        p = tabla.cell(0, k).paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        recuadro(p.add_run().add_picture(f"{IMGS}/{archivo}", width=Cm(8.4)))
        q = tabla.cell(1, k).paragraphs[0]
        q.style = doc.styles["IJCOPI Caption"]
        q.paragraph_format.space_before = Pt(0)
        q.paragraph_format.keep_with_next = True
        marcar(q.add_run(f"({'abcdefg'[k]}) "))
        escribir(q, parrafo_latex(sub_titulo))
    leyenda(f"Fig. {numero}. ", parrafo_latex(titulo), False)


def bloque_ecuacion(contenido):
    plano = re.sub(r"\s+", "", contenido)
    assert plano == r"A_g=\left|\frac{x_g-\mu}{\sigma+\epsilon}\right|,", plano
    tabla = doc.add_table(rows=1, cols=2)
    tabla_formato(tabla, [6804, 1134], bordes=False)
    p = tabla.cell(0, 0).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def r(t):
        return f'<m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>{t}</m:t></m:r>'

    def sub(base, indice):
        return f"<m:sSub><m:e>{r(base)}</m:e><m:sub>{r(indice)}</m:sub></m:sSub>"
    omml = (f'<m:oMath xmlns:m="{M}" xmlns:w="{W}">{sub("A", "g")}{r("=")}'
            f'<m:d><m:dPr><m:begChr m:val="|"/><m:endChr m:val="|"/></m:dPr><m:e><m:f>'
            f'<m:num>{sub("x", "g")}{r("−")}{r("μ")}</m:num><m:den>{r("σ")}{r("+")}{r("ε")}</m:den>'
            f'</m:f></m:e></m:d>{r(",")}</m:oMath>')
    p._p.append(parse_xml(omml))
    q = tabla.cell(0, 1).paragraphs[0]
    q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    q.add_run("(1)")


def bloque_listado(contenido):
    assert contenido.startswith("[")
    prof, j = 0, 0
    for j, c in enumerate(contenido):
        prof += c == "{"
        prof -= c == "}"
        if c == "]" and prof == 0:
            break
    opciones, codigo = contenido[1:j], contenido[j + 1:]
    titulo, _ = leer_grupo(opciones, opciones.index("caption=") + len("caption="))
    leyenda("Listing 1. ", parrafo_latex(titulo), True)
    lineas = codigo.strip("\n").split("\n")
    for k, linea in enumerate(lineas):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.space_after = Pt(0) if k < len(lineas) - 1 else Pt(8)
        pf.keep_with_next = k < len(lineas) - 1
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(
            f'<w:pBdr xmlns:w="{W}">' + "".join(
                f'<w:{lado} w:val="single" w:sz="4" w:space="3" w:color="808080"/>'
                for lado in ("top", "left", "bottom", "right")) + "</w:pBdr>"))
        run = marcar(p.add_run(linea if linea else " "))
        run.font.name = "Courier New"
        run.font.size = Pt(8)


def bloque_lista(contenido):
    for item in [x for x in re.split(r"\\item", contenido) if x.strip()]:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Pt(255 / 20)
        pf.first_line_indent = Pt(-142 / 20)
        pf.space_after = Pt(2)
        marcar(p.add_run("• "))
        escribir(p, parrafo_latex(item))


# ---- portada
titulo_art = re.search(r"\\title\{(.*?)\}\n", tex).group(1)
autores = [
    "Eduardo Uriel Velázquez Arrieta", "Omar Fernando Pulido Morales", "Emilio García López",
    "Clara Aide Hernández Martínez", "Gabriel Hurtado Avilés",
]
for a in autores:
    assert a in tex, a

p_titulo = Paragraph(elems[0], doc._body)
for r in list(p_titulo.runs):
    r._r.getparent().remove(r._r)
escribir(p_titulo, en_linea(titulo_art))

p_autores = Paragraph(elems[1], doc._body)
for r in list(p_autores.runs):
    r._r.getparent().remove(r._r)
tabs = p_autores._p.pPr.find(qn("w:tabs"))
p_autores._p.pPr.remove(tabs)
p_autores.alignment = WD_ALIGN_PARAGRAPH.CENTER
for k, a in enumerate(autores):
    if k:
        p_autores.add_run(", " if k < len(autores) - 1 else " and ")
    p_autores.add_run(a)
    p_autores.add_run("1").font.superscript = True

p_afil = Paragraph(elems[2], doc._body)
p_afil.runs[1].text = " Escuela Superior de Cómputo (ESCOM), Instituto Politécnico Nacional, Mexico City, Mexico"

p_correos = Paragraph(elems[3], doc._body)
for r in list(p_correos.runs):
    r._r.getparent().remove(r._r)
lineas_correo = [
    "{evelazqueza1900, opulidom2000, egarcial2001, chernandezm1903}@alumno.ipn.mx",
    "ghurtadoa@ipn.mx",
    "velazquez.arrieta.uriel@gmail.com, pulido.morales.omar@gmail.com",
    "egarlo@hotmail.com, claraahm11@gmail.com, gabrielhuav@gmail.com",
]
for k, linea in enumerate(lineas_correo):
    if k:
        p_correos.add_run().add_break()
    p_correos.add_run(linea)

p_corr = Paragraph(elems[4], doc._body)
assert p_corr.runs[-1].text == "Corresponding author:"
p_corr.runs[-1].text = "Corresponding author: gabrielhuav@gmail.com"

celdas = elems[6].findall(f".//{{{W}}}tc")
p_res = Paragraph(celdas[0].find(qn("w:p")), doc._body)
for r in list(p_res.runs):
    r._r.getparent().remove(r._r)
p_res.add_run("Abstract. ").bold = True
escribir(p_res, parrafo_latex(resumen))
# Las palabras clave van en su propio parrafo: tras un salto de linea manual, Word
# estira la ultima linea del resumen justificado.
p_kw = Paragraph(OxmlElement("w:p"), p_res._parent)
p_kw._p.append(copy.deepcopy(p_res._p.pPr))
p_res._p.addnext(p_kw._p)
p_kw.add_run("Keywords: ").bold = True
escribir(p_kw, parrafo_latex(claves))

p_info = Paragraph(celdas[1].find(qn("w:p")), doc._body)
for r in list(p_info.runs):
    r._r.getparent().remove(r._r)
p_info.add_run("Article information")
p_info.add_run().add_break()
p_info.add_run("Received:")
p_info.add_run().add_break()
p_info.add_run("Accepted:")

# ---- cuerpo
prefijo_runin = None
for b in bloques:
    tipo = b[0]
    if tipo == "h1":
        encabezado(1, b[1], b[2])
    elif tipo == "h2":
        encabezado(2, b[1], b[2])
    elif tipo == "runin":
        prefijo_runin = b[1]
    elif tipo == "p":
        p = parrafo()
        if prefijo_runin:
            p.add_run(prefijo_runin + " ").bold = True
            prefijo_runin = None
        escribir(p, parrafo_latex(b[1]))
        # Un parrafo que presenta lo siguiente (ecuacion, lista) no se separa de ello.
        p.paragraph_format.keep_with_next = p.text.rstrip().endswith(":")
    elif tipo == "table":
        bloque_tabla(b[1])
    elif tipo == "figure":
        bloque_figura(b[1])
    elif tipo == "equation":
        bloque_ecuacion(b[1])
    elif tipo == "lstlisting":
        bloque_listado(b[1])
    elif tipo == "itemize":
        bloque_lista(b[1])
    elif tipo == "resaltar":
        RESALTAR[0] = b[1]
    else:
        raise ValueError(tipo)
assert not RESALTAR[0], "nuevobloque sin cerrar"

# ---- referencias
p = doc.add_paragraph(style="Heading 1")
p.add_run("References").font.name = "Times New Roman"
for ref in sorted((REFERENCIAS[k] for k in claves_bib), key=lambda t: unicodedata.normalize("NFD", t.lstrip("!")).lower()):
    nueva = ref.startswith("!")
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(1)
    pf.first_line_indent = Cm(-1)
    pf.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for k, trozo in enumerate(ref.lstrip("!").split("*")):
        for pieza in re.split(r"(https?://\S+)", trozo):
            if not pieza:
                continue
            if pieza.startswith("http"):
                escribir(p, [{"text": pieza, "link": pieza, "hl": nueva}])
            else:
                run = p.add_run(pieza)
                run.italic = k % 2 == 1
                if nueva:
                    run.font.highlight_color = WD_COLOR_INDEX.YELLOW

# ---- declaraciones finales, con el estilo del bloque de cierre de la plantilla
doc.add_paragraph()


def declaracion(etiqueta, runs):
    # La plantilla escribe su bloque de cierre en Times New Roman 10 pt, justificado,
    # sobre estilos heredados de MDPI; Normal da ese mismo resultado sin arrastrar Palatino.
    p = parrafo()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(etiqueta + " ").bold = True
    escribir(p, runs)


URL_RELEASE = "https://github.com/gabrielhuav/Data_Warehouse_static/releases/tag/v1.5-icokg2026"
assert URL_RELEASE in tex
# Enlaces nuevos de la version extendida. La rama solo existe en GitHub despues del push.
URL_RAMA = "https://github.com/gabrielhuav/Data_Warehouse_static/tree/ijcopi-zmvm"
declaracion("Data Availability Statement:", [
    {"text": "The source files, the warehouse, the R2RML mapping, the scripts and the static demonstration are "
             "distributed in the archived release "},
    {"text": URL_RELEASE, "link": URL_RELEASE}, {"text": "."},
    {"text": " The extended warehouse, its verified manifest of sources, the SQL queries and the metropolitan map "
             "are in the branch ", "hl": True},
    {"text": URL_RAMA, "link": URL_RAMA, "hl": True}, {"text": ".", "hl": True}])
declaracion("Declaration on the Use of Generative AI:", parrafo_latex(decl_ia))
declaracion("Conflicts of Interest:", parrafo_latex(interes))

# ---- notas al pie, encabezado y metadatos
parte_notas._blob = etree.tostring(notas_xml, xml_declaration=True, encoding="UTF-8", standalone=True)
encab = doc.sections[0].header
for p in encab.paragraphs:
    for r in p.runs:
        if "Author et al." in r.text:
            r.text = r.text.replace("Author et al.", "Velázquez Arrieta et al.")
doc.core_properties.title = "".join(r.get("text", "") for r in en_linea(titulo_art))
doc.core_properties.author = ""
doc.core_properties.last_modified_by = ""
doc.core_properties.comments = ""
doc.save(SALIDA)

print("bloques:", {t: sum(1 for b in bloques if b[0] == t) for t in sorted({b[0] for b in bloques})})
print("etiquetas:", NUM)
print("notas al pie:", fn_id[0])
print("avisos:", sorted(set(avisos)) or "ninguno")
