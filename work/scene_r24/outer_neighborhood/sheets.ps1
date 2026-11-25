param([string]$Final='r6_views',[switch]$Frames,[switch]$Architecture)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$root=Join-Path $PSScriptRoot evidence
function Sheet($target,$rows){
    $w=480
    $h=281
    if($Architecture){$w=600;$h=338}
    $canvas=[Drawing.Bitmap]::new($w*3,($h+38)*2)
    $g=[Drawing.Graphics]::FromImage($canvas)
    $font=[Drawing.Font]::new('Microsoft YaHei',12)
    try {
        $g.Clear([Drawing.Color]::FromArgb(31,37,36))
        $g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        for($i=0;$i -lt 6;$i++){
            $x=($i%3)*$w
            $y=[Math]::Floor($i/3)*($h+38)
            $entry=$rows[$i]
            $im=[Drawing.Image]::FromFile((Join-Path $root ($entry[0]+'.png')))
            try {$g.DrawImage($im,$x,$y,$w,$h)}finally{$im.Dispose()}
            $g.DrawString($entry[1],$font,[Drawing.Brushes]::White,$x+8,$y+$h+5)
        }
        $canvas.Save((Join-Path $root $target),[Drawing.Imaging.ImageFormat]::Jpeg)
    }finally{$font.Dispose();$g.Dispose();$canvas.Dispose()}
}
if($Architecture){
    Sheet 'architecture_before_after.jpg' @(
        ,@('frame_finish_views/market_street','上版 · 照相巷市场')
        ,@('architecture_reference/home_05_facade','上版 · 5 号住宅临街面')
        ,@('architecture_reference/market_bed','上版 · 院坝二楼 201')
        ,@('street_thresholds/market_street','本版 · 柱间菜档和挑棚')
        ,@('landing_views/home_05_facade','本版 · 首层窗洞和挑出的晒台')
        ,@('landing_views/market_bed','本版 · 墙裙、磨石地砖与家具落地')
    )
    Sheet 'old_and_outer.jpg' @(
        ,@('landing_views/old_service','老区 · 临街门面')
        ,@('landing_views/old_overhang','老区 · 坡道旁的出挑空间')
        ,@('../../../project/chongqing_godot_v05/verification_r24/district_patrol/final25b/bridge/02_pickup_202','老区 · 202 取餐点（25b 历史画面）')
        ,@('landing_views/market_facade','新区 · 照相巷市场')
        ,@('landing_views/home_05_facade','新区 · 5 号住宅的晒台与窗洞')
        ,@('landing_views/market_bed','新区 · 201 住宅')
    )
    return
}
if($Frames){
    Sheet 'inside_before_after.jpg' @(
        ,@('r6_views/market_hall','原版 · 照相巷市场穿堂')
        ,@('r6_views/ordinary_04','原版 · 4 号住宅洗衣间')
        ,@('r6_views/market_bed','原版 · 院坝二楼 201')
        ,@('frame_finish_views/market_hall','现版 · 柱网之间的菜档和通道')
        ,@('frame_finish_views/ordinary_04','现版 · 洗衣间柱脚和工作台')
        ,@('frame_finish_views/market_bed','现版 · 木搁栅、床架和窗帘')
    )
    return
}
Sheet 'street_iterations.jpg' @(
    ,@('baseline_views/repair_street','上版 · 修理铺被旧远景楼遮挡')
    ,@('round1_views/repair_hall','第一轮 · 旧立面穿进新屋')
    ,@('round2_views/repair_hall','第二轮 · 撤掉穿墙的旧楼和窗组')
    ,@('round3_views/market_yard','第三轮 · 后门接到院坝和外梯')
    ,@('round4_views/market_yard','第四轮 · 瓦檐、窗洞与生活陈设')
    ,@("$Final/market_counter",'现版 · 菜市入口的柜台与过道')
)
Sheet 'market_to_home.jpg' @(
    ,@("$Final/market_street",'街面 · 从台阶进照相巷市场')
    ,@("$Final/market_counter",'店内 · 街坊柜台')
    ,@("$Final/market_yard",'后院 · 转进共用外梯')
    ,@("$Final/market_gallery",'楼上 · 沿有盖外廊到住户门前')
    ,@("$Final/market_bed",'住户 · 进门看床、铺盖和木柜')
    ,@("$Final/ordinary_03",'另一处住宅 · 穿堂旁的住家')
)
