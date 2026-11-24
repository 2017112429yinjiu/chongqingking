param([string]$Path,[string]$Result)
Add-Type -AssemblyName System.Drawing
$files=@(Get-ChildItem -LiteralPath $Path -Filter '*.png' | Sort-Object Name)
$canvas=New-Object Drawing.Bitmap (1040,([int][Math]::Ceiling($files.Count/3)*218))
$gfx=[Drawing.Graphics]::FromImage($canvas)
$gfx.Clear([Drawing.Color]::FromArgb(38,38,38))
$font=New-Object Drawing.Font('Arial',10)
for($i=0;$i -lt $files.Count;$i++){
 $img=[Drawing.Image]::FromFile($files[$i].FullName)
 $x=($i%3)*346
 $y=[int][math]::Floor($i/3)*218
 $gfx.DrawImage($img,$x,$y,344,194)
 $gfx.DrawString($files[$i].BaseName,$font,[Drawing.Brushes]::White,$x,$y+194)
 $img.Dispose()
}
$canvas.Save($Result,[Drawing.Imaging.ImageFormat]::Jpeg)
$font.Dispose()
$gfx.Dispose()
$canvas.Dispose()
