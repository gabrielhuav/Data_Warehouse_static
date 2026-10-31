param([string]$Entrada, [string]$Salida)
# Abre el .docx en Word (solo lectura), lo exporta a PDF e imprime el numero de paginas.
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Entrada, $false, $true)
    $doc.Repaginate()
    "paginas: " + $doc.ComputeStatistics(2)
    "palabras: " + $doc.ComputeStatistics(0)
    $doc.ExportAsFixedFormat($Salida, 17)
    $doc.Close(0)
} finally {
    $word.Quit()
}
