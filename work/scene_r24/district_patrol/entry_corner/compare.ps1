param([Parameter(Mandatory)][string]$RunDirectory)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$baseline=Join-Path (Split-Path $RunDirectory) 'reviewed25/older_crossings'
$photos=@(
    @((Join-Path $PSScriptRoot 'player.png'),(Join-Path $RunDirectory 'older_crossings/turn_01_1.png')),
    @((Join-Path $baseline 'turn_02_2.png'),(Join-Path $RunDirectory 'older_crossings/turn_02_2.png'))
)
$captions=@('街口院坝 · 玩家原图','街口院坝 · 25b 同机位','中央梯坎 · 构建 25','中央梯坎 · 25b 同机位')
$canvas=[Drawing.Bitmap]::new(1600,970)
$graphics=[Drawing.Graphics]::FromImage($canvas)
$font=[Drawing.Font]::new('Microsoft YaHei',14)
try {
    $graphics.Clear([Drawing.Color]::FromArgb(35,36,34))
    $graphics.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    for($row=0;$row -lt 2;$row++){
        for($col=0;$col -lt 2;$col++){
            $picture=[Drawing.Image]::FromFile($photos[$row][$col])
            try {
                $x=$col*800
                $y=$row*485
                $graphics.DrawString($captions[$row*2+$col],$font,[Drawing.Brushes]::White,$x+12,$y+4)
                $graphics.DrawImage($picture,$x,$y+32,800,[int][Math]::Round(800*$picture.Height/$picture.Width))
            } finally { $picture.Dispose() }
        }
    }
    $canvas.Save((Join-Path $RunDirectory 'street_comparison.jpg'),[Drawing.Imaging.ImageFormat]::Jpeg)
} finally {
    $font.Dispose()
    $graphics.Dispose()
    $canvas.Dispose()
}
