param([string]$Tex = "$PSScriptRoot\..\paper\dw_agua_icokg2026.tex")
# Comprueba que responden todos los enlaces del camera-ready enviado a Springer.
# Esos enlaces ya estan publicados: no pueden cambiar ni dejar de funcionar, asi
# que conviene correr esto antes de cada push.
$texto = (Get-Content $Tex -Encoding UTF8 | Where-Object { $_.TrimStart() -notmatch '^%' }) -join "`n"
$urls = [regex]::Matches($texto, '\\(?:url|href)\{([^}]+)\}') | ForEach-Object {
    $_.Groups[1].Value -replace '\\%', '%' -replace '\\_', '_' -replace '\\&', '&'
} | Where-Object { $_ -match '^https?://' } | Sort-Object -Unique
$fallos = 0
foreach ($u in $urls) {
    try {
        $r = Invoke-WebRequest $u -UseBasicParsing -MaximumRedirection 10 -TimeoutSec 30 -UserAgent "Mozilla/5.0"
        "{0} {1}" -f $r.StatusCode, $u
    } catch {
        $c = $_.Exception.Response.StatusCode.value__
        if ($u -match '^https://doi\.org/(.+)$' -and $c -in 403, 429) {
            # Algunas editoriales rechazan clientes automaticos; basta con que el DOI resuelva.
            $h = Invoke-RestMethod "https://doi.org/api/handles/$($Matches[1])" -TimeoutSec 30
            "{0} {1} (editorial bloquea scripts; DOI resuelve: {2})" -f $c, $u, ($h.responseCode -eq 1)
            if ($h.responseCode -ne 1) { $fallos++ }
        } else {
            "FALLA {0} {1}" -f $c, $u
            $fallos++
        }
    }
}
"enlaces: $($urls.Count), fallos: $fallos"
exit $fallos
