param(
    [Parameter(Mandatory)][string]$Before,
    [Parameter(Mandatory)][string]$After,
    [Parameter(Mandatory)][string]$Output
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$sites = [ordered]@{ service_front='旧区 · 服务站'; west='向西出城'; east='向东出城'; north='向北出城'; south='向南出城'; oblique='总览'; plan='俯视' }
$width = 540
$height = 304
$rowHeight = 337
$canvas = [Drawing.Bitmap]::new($width * 2 + 12, 43 + $rowHeight * $sites.Count)
$graphics = [Drawing.Graphics]::FromImage($canvas)
$font = [Drawing.Font]::new('Microsoft YaHei',12)
try {
    $graphics.Clear([Drawing.Color]::FromArgb(30,35,37))
    $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.DrawString('原城区 · 200 × 200 米',$font,[Drawing.Brushes]::White,6,9)
    $graphics.DrawString('拓建试作 · 500 × 500 米',$font,[Drawing.Brushes]::White,$width+12,9)
    $row = 0
    foreach ($site in $sites.Keys) {
        $y = 43 + $row * $rowHeight
        $col = 0
        foreach ($folder in $Before,$After) {
            $img = [Drawing.Image]::FromFile((Join-Path $folder "$site.png"))
            try { $graphics.DrawImage($img,$col*($width+12),$y,$width,$height) } finally { $img.Dispose() }
            $col++
        }
        $graphics.DrawString($sites[$site],$font,[Drawing.Brushes]::White,6,$y+$height+3)
        $row++
    }
    $canvas.Save($Output,[Drawing.Imaging.ImageFormat]::Jpeg)
} finally {
    $font.Dispose()
    $graphics.Dispose()
    $canvas.Dispose()
}
