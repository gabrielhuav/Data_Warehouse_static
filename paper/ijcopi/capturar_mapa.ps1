param(
    [string]$Base = "http://localhost:8765/ijcopi",
    [string]$Salida = $PSScriptRoot
)
# Captura las figuras del articulo desde el mapa real, con Edge sin ventana. Antes hay que
# servir la raiz del repositorio: py -3 -m http.server 8765
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
$perfil = Join-Path $env:TEMP "captura_mapa_edge"
$figuras = @{
    "figura_zm_volumen.png" = "mapa-zm.html?vista=figura&lang=en&ind=m_litros"
    "figura_zm_colonias.png" = "mapa-zm.html?vista=figura&lang=en&ind=c_sinagua&capas=acuiferos,pozos"
    "figura_zm_grafo.png" = "grafo-zm.html?vista=figura&lang=en&mun=09007"
}
foreach ($nombre in $figuras.Keys) {
    $destino = Join-Path $Salida $nombre
    if (Test-Path $destino) { Remove-Item $destino }
    $url = "$Base/$($figuras[$nombre])"
    Start-Process -Wait -NoNewWindow -FilePath $edge -ArgumentList @(
        "--headless=new", "--disable-gpu", "--hide-scrollbars", "--user-data-dir=$perfil",
        "--window-size=1000,760", "--force-device-scale-factor=1.6", "--virtual-time-budget=25000",
        "--screenshot=`"$destino`"", "`"$url`"")
    # Paleta de 256 colores: sin perder legibilidad, el .docx pesa una quinta parte
    py -3 -c "from PIL import Image; import sys; Image.open(sys.argv[1]).convert('RGB').quantize(256).save(sys.argv[1], optimize=True)" $destino
    "{0}: {1:N0} KB" -f $nombre, ((Get-Item $destino).Length / 1KB)
}
