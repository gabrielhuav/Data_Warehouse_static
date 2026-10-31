param(
    [string]$Destino = (Join-Path $env:TEMP "zmvm"),
    [string]$Rama = "ijcopi-zmvm",
    [string]$Remoto = "https://github.com/gabrielhuav/Data_Warehouse_ZMVM.git"
)
# Prepara la copia publica de la version extendida, sin subir nada. Vive en un repositorio propio
# porque GitHub Pages solo publica main, que queda congelada para ICOKG. Lleva lo necesario para
# ver el mapa y reproducir el almacen; la memoria de trabajo y el manuscrito no se publican.
$ErrorActionPreference = "Stop"
$raiz = Split-Path $PSScriptRoot -Parent
$rutas = @(
    ".gitignore", "LICENSE", "index.html", "mapa.html", "grafo.html", "vecindad.html", "consumo.json",
    "alcaldias.geojson", "kg_demo.ttl", "mapping.r2rml.ttl", "schema.ttl", "evidencia_datacube.txt",
    "evidencia_grafo.txt", "evidencia_tabla9.txt", "assets", "ijcopi", "scripts", "evaluacion-ml",
    "warehouse", "warehouse_ampliado", "reports/Deep_Research_Ampliacion_DWH_IJCOPI.md"
)

if (-not (Test-Path (Join-Path $Destino ".git"))) { git clone -q $Remoto $Destino }
Get-ChildItem $Destino -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force

$tar = Join-Path $env:TEMP "zmvm_publicar.tar"
git -C $raiz -c core.autocrlf=false archive -o $tar $Rama -- @rutas
tar -xf $tar -C $Destino
Remove-Item $tar

Move-Item -Force (Join-Path $Destino "ijcopi\README_publico.md") (Join-Path $Destino "README.md")
Remove-Item (Join-Path $Destino "ijcopi\publicar.ps1")
Remove-Item (Join-Path $Destino "scripts\verificar_enlaces_springer.ps1")
# Sin esto, Jekyll procesaria los .md del repositorio y podria fallar la publicacion
New-Item -ItemType File (Join-Path $Destino ".nojekyll") | Out-Null

$n = (Get-ChildItem $Destino -Recurse -File -Force | Where-Object { $_.FullName -notmatch '\\\.git\\' } | Measure-Object Length -Sum)
"copia lista en {0}: {1} archivos, {2:N1} MB" -f $Destino, $n.Count, ($n.Sum / 1MB)
