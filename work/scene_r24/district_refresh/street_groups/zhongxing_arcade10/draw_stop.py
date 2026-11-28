"""Draw the arcade stop's own printed artwork, without using street-view pixels."""
import argparse
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFont


def lettering(draw, typeface, xy, text, size, ink, anchor='lt'):
    font = ImageFont.truetype(str(typeface), size, index=2)
    draw.text(xy, text, font=font, anchor=anchor, fill=ink)


def station_plate(output, font):
    image = Image.new('RGB', (640, 192), '#64847a')
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((7, 7, 632, 183), radius=22, fill='#d6ded0', outline='#466860', width=6)
    draw.rounded_rectangle((21, 20, 617, 171), radius=15, outline='#96a795', width=3)
    lettering(draw, font, (319, 89), '中兴路站', 111, '#15574a', 'mm')
    for x in (35, 604):
        draw.ellipse((x-4, 90, x+4, 98), fill='#566c64')
    image.save(output/'arcade10-stop-name.png')


def passenger_panel(output, font):
    image = Image.new('RGB', (704, 432), '#163e3c')
    draw = ImageDraw.Draw(image)
    draw.rectangle((13, 13, 690, 418), fill='#e0e4cc', outline='#94a482', width=4)
    draw.rectangle((17, 17, 687, 82), fill='#2b695a')
    lettering(draw, font, (40, 34), '中兴路站', 33, '#f0f0d8')
    lettering(draw, font, (251, 40), '候车提示', 24, '#e6e6c9')
    draw.rectangle((34, 104, 414, 391), fill='#c6d1b8')
    for number, title in enumerate(('有序排队', '先下后上', '留出通道'), 1):
        y = 119+(number-1)*92
        draw.rectangle((55, y, 106, y+48), fill='#5c7960')
        lettering(draw, font, (80, y+23), str(number), 28, '#eef0d9', 'mm')
        lettering(draw, font, (126, y+2), title, 24, '#2b5248')
        draw.rectangle((126, y+44, 345, y+49), fill='#a4b398')
    draw.rectangle((440, 103, 667, 390), fill='#a6bdb1')
    draw.rounded_rectangle((491, 156, 618, 276), radius=24, fill='#315c51')
    draw.rectangle((508, 179, 600, 219), fill='#d6ddc9')
    draw.line((554, 179, 554, 219), fill='#315c51', width=5)
    for x in (518, 591):
        draw.ellipse((x-7, 233, x+7, 247), fill='#e3dbad')
        draw.rounded_rectangle((x-10, 265, x+10, 289), radius=6, fill='#315c51')
    lettering(draw, font, (556, 329), '文明候车', 27, '#315c51', 'mm')
    image.save(output/'arcade10-stop-passengers.png')


def public_poster(output, font):
    image = Image.new('RGB', (896, 448), '#567676')
    draw = ImageDraw.Draw(image)
    draw.rectangle((12, 12, 883, 435), outline='#acb8a4', width=4)
    draw.rectangle((700, 13, 883, 435), fill='#9b5140')
    for y in (75, 152, 229, 306):
        draw.line((738, y, 844, y), width=2, fill='#bc7660')
    for y, char in zip((35, 120, 205, 290), '文明候车'):
        lettering(draw, font, (790, y), char, 59, '#eadabf', 'mt')
    rng = Random(1010)
    for band, colors in enumerate(('#64827d', '#46656b', '#304f57')):
        y = 219+55*band
        hills = [(22+x*34, y-rng.randrange(5, 60)) for x in range(20)]
        draw.polygon([(22, 415), *hills, (688, y+10), (688, 415)], fill=colors)
    draw.ellipse((564, 84, 630, 150), fill='#b6af88')
    draw.line([(32, 372), (190, 348), (369, 379), (672, 336)], fill='#9cab9e', width=4)
    draw.line([(32, 380), (190, 356), (369, 387), (672, 344)], fill='#73948e', width=2)
    lettering(draw, font, (40, 48), '有序排队  留出通道', 45, '#e5e9d5')
    lettering(draw, font, (46, 116), '乘车礼让', 28, '#d3ddc9')
    image.save(output/'arcade10-stop-poster.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--font', type=Path, default=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'))
    args = parser.parse_args()
    station_plate(args.output, args.font)
    passenger_panel(args.output, args.font)
    public_poster(args.output, args.font)


if __name__ == '__main__':
    main()
