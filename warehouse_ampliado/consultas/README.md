# Consultas al almacén

Cada archivo `.sql` es una consulta real al almacén de PostgreSQL. `etl/exportar_mapa.py` guarda su
resultado en `ijcopi/datos/` y el mapa dibuja ese resultado. No hay otra fuente de datos para el mapa.

| Archivo | Qué devuelve | Dónde se usa |
| --- | --- | --- |
| `01_fuentes_cargadas.sql` | Lo que entró al almacén, con el hash de cada archivo | Consultas |
| `02_tablas_del_almacen.sql` | Filas reales de cada tabla | Mapa y consultas |
| `03_municipios_zm.sql` | Los 63 municipios de la zona metropolitana | Mapa |
| `04_colonias_zm.sql` | Las 5,830 colonias de CONAPO, con lo de SACMEX donde existe | Mapa |
| `05_acuiferos_zm.sql` | Balance de 10 acuíferos y descenso del nivel | Mapa y artículo |
| `06_pozos_zm.sql` | Pozos con lectura en 2010 y en 2019 | Mapa |
| `07_presas.sql`, `08_presas_mensual.sql` | Las 15 presas y su volumen mensual | Mapa |
| `09_sequia_zm.sql` | Monitor de Sequía por municipio y fecha | Mapa |
| `10_calidad_zm.sql` | Sitios de calidad del agua | Mapa |
| `11_cruces_colonia.sql` | Cruces entre consumo, reportes y fugas | Artículo |
| `12_geometrias.sql` | Polígonos simplificados | Mapa |
| `13_sin_agua_zm.sql` | Acceso al agua entubada por entidad | Artículo |
| `14_vecinos_municipio.sql` | Municipios que comparten frontera, con su longitud | Consultas |
| `15_frontera_cdmx.sql` | Lo que cruza el límite de la CDMX | Artículo |

En `04_colonias_zm.sql`, `pob_total` es población del polígono CONAPO y `pob_sacmex` es la
población urbana asignada a las unidades SACMEX enlazadas. Las tasas son proxies sobre el segundo
soporte: no se reparten los registros según los límites del polígono. Se exponen volumen,
conteos y número de unidades con población/subtotal doméstico disponible; las tasas se omiten
si falta su denominador en alguna unidad. Disponer de subtotal por unidad no acredita cobertura
completa de cuentas o bimestres.

En `03_municipios_zm.sql` el volumen SACMEX de 2019 S1 se anualiza ×2 y divide entre 365 días
y población CONAPO de mitad de 2019. La Tabla 4 usa OCUPVIVPAR 2020 y 181 días; la capa de
colonias usa población urbana asignada y 181 días. Se mantienen esas bases explícitas, sin
interpretarlas como una sola tasa de consumo medido.

## Verlas en la base de datos

Desde la raíz del repositorio. Estos comandos funcionan igual en PowerShell y en Git Bash.

Arranca el almacén:

```bash
docker start data_warehouse_cdmx
```

Copia las consultas al contenedor:

```bash
docker cp warehouse_ampliado/consultas/. data_warehouse_cdmx:/consultas
```

Cuenta las filas de cada tabla:

```bash
docker exec data_warehouse_cdmx psql -U postgres -d data_warehouse -f /consultas/02_tablas_del_almacen.sql
```

Muestra los 63 municipios:

```bash
docker exec data_warehouse_cdmx psql -U postgres -d data_warehouse -f /consultas/03_municipios_zm.sql
```

Abre la consola de PostgreSQL. Dentro, `\dt` lista las tablas, `\dv` las vistas y `\q` sale:

```bash
docker exec -it data_warehouse_cdmx psql -U postgres -d data_warehouse
```

Para conectarte con pgAdmin o DBeaver: `localhost`, puerto `5433`, base `data_warehouse`, usuario y
contraseña `postgres`.

## Comprobar que el mapa es la base de datos

Repite las 15 consultas y compara cada resultado con lo publicado en `ijcopi/datos/`:

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/verificacion/verificar_mapa.py
```

Termina con `verificaciones fallidas: 0` y escribe
[`verificacion/evidencia_mapa.txt`](../verificacion/evidencia_mapa.txt). Al hacer clic en un
municipio, una colonia, un pozo o una presa, el mapa muestra además la consulta exacta de ese dato.

## Reflejar un cambio del almacén en el mapa

Si cambian los datos o una consulta, regenera lo publicado y vuelve a comprobarlo:

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/etl/exportar_mapa.py
```

El mapa no consulta PostgreSQL en vivo: es una página estática, así que lee lo último que se exportó.
