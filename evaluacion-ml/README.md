# Evaluaciones reproducibles

Los CSV de sensibilidad conservan la clave histórica `PR-AUC`. Su contenido es
**average precision (AP)** de `sklearn.metrics.average_precision_score`: suma de la
precisión ponderada por los incrementos de recall, sin interpolación. No es la
integración trapezoidal de una curva precisión–recall. Las cifras históricas y las
claves de los CSV se mantienen; la salida pareada identifica la medida como AP.

## Comparación por semilla

Desde la raíz del repositorio:

```powershell
python evaluacion-ml/comparacion_pareada.py --csv evaluacion-ml/sensibilidad_anomalias.csv
python -m unittest discover -s evaluacion-ml -p test_comparacion_pareada.py
```

La comparación requiere Python 3.10 o posterior y pandas (incluido en
`requirements.txt`). Su salida identifica las versiones utilizadas. La prueba
exacta usa enteros de Python; no depende de SciPy ni de su selección automática de
método. La evidencia incluida se recalculó con Python 3.10.11 y pandas 2.3.3.

Cada par es la diferencia IF menos A_g de una misma semilla y configuración.
Se redondea a 12 decimales con redondeo decimal al par antes de identificar ceros y
empates. Los ceros se omiten de los rangos (convención Wilcox); los empates de
magnitud reciben su rango promedio. Una programación dinámica cuenta exactamente
las `2^n` asignaciones de signos de los pares no nulos, incluidas las magnitudes
empatadas. El valor p bilateral incluye ambos extremos y el estadístico observado;
si todos los pares son cero, p=1. Se imprimen el numerador y denominador exactos.
El nulo condicional supone signos intercambiables de las diferencias; las semillas
son réplicas sintéticas y no sustituyen la validación con etiquetas de campo. La
implementación admite hasta 200 pares no nulos (el experimento usa 20).

El archivo de requisitos también incluye RDFLib, necesario para leer las
identidades de `kg_demo.ttl` al repetir la simulación, y Matplotlib para la figura.
La evidencia pareada se recalcula desde los CSV ya almacenados, sin repetir el
entrenamiento. El SHA-256 de la entrada identifica sus bytes concretos, incluido
el formato de fin de línea; los repositorios pueden conservar finales distintos.

`GRID` contiene 12 entradas y 10 configuraciones paramétricas distintas: la
configuración publicada aparece en cada uno de los tres factores. La salida
pareada verifica que coincidan todos los campos por semilla de esas tres entradas
y omite únicamente esas copias. Si difieren, falla; otras configuraciones se
conservan aunque sus resultados coincidan.

## Grano del índice fiscal

```powershell
python evaluacion-ml/indice_fiscal_grano.py --csv warehouse/data/consumo_agua_historico_2019.csv
```

Este script usa solo la biblioteca estándar y escribe JSON a stdout; no modifica
el CSV. Incluye SHA-256 de la entrada y recuentos válidos por campo. Excluye los
registros sin alcaldía o colonia (`NA` o vacíos) y conserva los valores numéricos
faltantes como NULL: no los sustituye por cero. Cuenta los pares
`(alcaldia, colonia)` que contienen varios `indice_des` y calcula medias por
registro fuente, sin ponderación, para `consumo_total` y `consumo_prom`.

`consumo_prom` ya es un promedio reportado por la fuente. El CSV no aporta los
conteos necesarios para reconstruir su ponderación por cuentas; el promedio de
ese campo entre registros no se interpreta como promedio por residente, cuenta o
colonia. Las categorías del índice fiscal tampoco son grupos excluyentes de
colonias. La evidencia reproducible es `evidencia_indice_fiscal_grano.json`.
