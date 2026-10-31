# Solicitudes de más datos de consumo de agua

Hay dos vías y conviene usar ambas en paralelo:

1. **Correo al mantenedor del dataset** (`datosabiertos@cdmx.gob.mx`). Es la dirección que el portal muestra como "Email mantenedor", pero la atiende la Agencia Digital de Innovación Pública (ADIP), no el organismo de agua. No tiene plazo legal y en la práctica alimenta el plan anual de apertura de datos. Sirve para que publiquen más periodos, pero difícilmente antes del 9 de noviembre.
2. **Solicitud de acceso a la información** en la Plataforma Nacional de Transparencia, dirigida a la **Secretaría de Gestión Integral del Agua (SEGIAGUA, antes SACMEX)**. Es la única vía con plazo legal: 9 días hábiles, prorrogables una vez por 7 (art. 157 de la Ley de Transparencia de la CDMX vigente desde el 14 de julio de 2026). Si se presenta el lunes 19 de octubre, la respuesta vence el 30 de octubre, o entre el 10 y el 11 de noviembre si hay prórroga.

Antecedentes que conviene conocer:

- En 2025 alguien pidió el consumo 2021–2024 por alcaldía, colonia, uso y manzana (folio 090173525000627). SEGIAGUA solo entregó totales anuales por alcaldía y tipo de uso, y el órgano garante lo validó porque no hay obligación de "procesar" información (art. 164).
- Ramos-Bueno et al. (2021) sí obtuvieron consumo **por colonia** de 2008–2013 por esta vía (folio 0324000022614). El nivel de colonia es realista; el de manzana, poco probable.
- Los recursos de revisión están suspendidos mientras arranca el nuevo órgano garante, así que una mala respuesta no se puede impugnar a tiempo.

Por eso la solicitud de abajo: pide un año por folio (para que no parezca procesamiento), pide la base de datos tal como existe en formato abierto (art. 153), ofrece el nivel de colonia como alternativa, y pide que una eventual inexistencia la confirme el Comité de Transparencia (art. 162). También pide **el número de tomas por tipo de facturación**, que respondería directamente la pregunta que plantea el artículo: por qué el export abierto implica solo 47 l/hab/día. El volumen anualizado del export (unos 243 millones de m³) es cercano a los 255 millones que SACMEX informó como facturados en 2021 (resolución INFOCDMX/RR.IP.0679/2022). Por eso todo indica que el export está casi completo respecto a la facturación y que lo que falta son las tomas que no se facturan por volumen, como las de cuota fija en colonias con tandeo.

---

## 1. Correo a datosabiertos@cdmx.gob.mx

**Para:** datosabiertos@cdmx.gob.mx
**CC:** infoadip@cdmx.gob.mx
**Asunto:** Solicitud de publicación de periodos adicionales del conjunto "Consumo de agua" (SACMEX/SEGIAGUA)

> Estimado equipo de Datos Abiertos de la Ciudad de México:
>
> Reciban un cordial saludo. Somos un grupo de investigación de la Escuela Superior de Cómputo del Instituto Politécnico Nacional. Con base en el conjunto de datos "Consumo de agua" (https://datos.cdmx.gob.mx/dataset/consumo-agua), cuyo único recurso es "Consumo Agua (1° Semestre 2019)", construimos un almacén de datos y un grafo de conocimiento reproducibles. El trabajo fue aceptado en la conferencia ICOKG 2026 y ahora preparamos una versión extendida para la revista IJCOPI.
>
> Para continuar el análisis, les agradeceríamos mucho que valoraran publicar, con la misma estructura del recurso actual (nivel manzana, por bimestre, con alcaldía, colonia, tipo de uso, índice de desarrollo y coordenadas), los periodos disponibles posteriores al primer semestre de 2019 y, de ser posible, algunos anteriores.
>
> Les pedimos también considerar dos campos que harían los datos mucho más útiles:
>
> 1. el tipo de facturación de cada registro (consumo medido, consumo promedio o cuota fija), y
> 2. el número de tomas que representa cada registro.
>
> La nota aclaratoria del recurso explica que los valores combinan facturación por consumo medido y promedio. Al comparar el recurso con el Censo de Población y Vivienda 2020, encontramos que el consumo doméstico implícito es de unos 47 litros por habitante al día en promedio de la ciudad, con valores muy bajos en Milpa Alta, Tláhuac e Iztapalapa. Como el volumen anualizado del recurso es cercano al total facturado que se ha informado públicamente, creemos que la diferencia corresponde a tomas que no se facturan por volumen (por ejemplo, con cuota fija). Con esos dos campos, cualquier usuario podría interpretar correctamente qué representa el recurso.
>
> Con gusto compartimos el análisis y los programas con que lo hicimos, y citaremos el conjunto de datos y a la institución en todas las publicaciones que resulten.
>
> Quedamos atentos y agradecemos de antemano su atención.
>
> Atentamente,
>
> M. en C. Gabriel Hurtado Avilés
> Escuela Superior de Cómputo (ESCOM), Instituto Politécnico Nacional
> ghurtadoa@ipn.mx

*Opcional:* adjuntar un oficio con membrete de ESCOM; según la investigación, eso refuerza este tipo de peticiones.

---

## 2. Solicitud en la Plataforma Nacional de Transparencia

**Plataforma:** https://www.plataformadetransparencia.org.mx → Ciudad de México → **Secretaría de Gestión Integral del Agua**
**Modalidad de entrega:** electrónica a través de la PNT, en formato abierto (CSV o XLSX)

Conviene presentar **un folio por año** (2019, 2020, 2021, …). Texto para el folio de 2019; para los demás basta cambiar el año:

> Con fundamento en los artículos 14, 146 y 153 de la Ley de Transparencia para el Acceso y Socialización de la Información de la Ciudad de México, solicito, en formato abierto (CSV o XLSX) y sin datos personales, la base de datos de facturación de consumo de agua del ejercicio **2019** que ya se encuentre en los sistemas de la Secretaría, con la misma estructura del recurso "Consumo Agua (1° Semestre 2019)" publicado en https://datos.cdmx.gob.mx/dataset/consumo-agua: por bimestre y por manzana, con alcaldía, colonia, consumo total y promedio por tipo de uso (doméstico, no doméstico y mixto), índice de desarrollo y coordenadas, para los **seis bimestres de 2019**.
>
> Solicito además, para el mismo ejercicio y por colonia, el **número de tomas por tipo de facturación** (consumo medido, consumo promedio y cuota fija) y por tipo de uso.
>
> En caso de que la información no exista a nivel manzana, solicito la que exista a **nivel colonia** con las mismas variables. No pido que se elabore ningún documento nuevo, sino la extracción de la base de datos existente, que conforme al artículo 153 debe entregarse privilegiando formatos abiertos. Si se determinara la inexistencia de alguna parte de lo solicitado, pido que la confirme el Comité de Transparencia en términos del artículo 162.
>
> La información se usará con fines de investigación académica en el Instituto Politécnico Nacional, y los resultados citarán a la Secretaría como fuente.

**Folio adicional, agregado y con más probabilidad de respuesta.** Es el nivel de detalle que SEGIAGUA ya ha entregado antes:

> Con fundamento en los artículos 14, 146 y 153 de la Ley de Transparencia para el Acceso y Socialización de la Información de la Ciudad de México, solicito, en formato abierto, el volumen facturado de agua potable del ejercicio **2019** y el **número de tomas**, desglosados **por alcaldía, tipo de uso (doméstico, no doméstico y mixto) y tipo de facturación (consumo medido, consumo promedio y cuota fija)**, según se registre en el Sistema Comercial Centralizado. La información se usará con fines de investigación académica en el Instituto Politécnico Nacional.

**Antes de enviar:**

- Revisar en el buscador de solicitudes de la PNT las respuestas a los folios 090173525000627, 090173522000091 y 090173522001841. Si los anexos son públicos, ya traen totales por alcaldía y uso de 2021–2024, sin esperar nada.
- La dirección de correo `ut@sacmex.cdmx.gob.mx` aparece solo en un documento escaneado y no está confirmada. La vía segura es la PNT.
