# -*- coding: utf-8 -*-

import argparse
import os
from PIL import Image, ImageDraw
from pprint import pprint
import sys
import time

from lib.collection_utils import *
from lib.image_utils import *
from lib.io_utils import *
from lib.math_utils import *

# input
parser = argparse.ArgumentParser()
parser.add_argument('-airports', dest="AIRPORTS_FILE", default="data/airports.dat.csv", help="Input airports csv file")
parser.add_argument('-routes', dest="ROUTES_FILE", default="data/routes.dat.csv", help="Input routes csv file")
parser.add_argument('-width', dest="WIDTH", default=4320, type=int, help="Width of video")
parser.add_argument('-height', dest="HEIGHT", default=2160, type=int, help="Height of video")
parser.add_argument('-fps', dest="FRAMES_PER_SECOND", default=30, type=int, help="Frames per second of video")
parser.add_argument('-img', dest="MAP_IMAGE_FILE", default="img/map.png", help="Background map image file")
parser.add_argument('-frames', dest="OUTPUT_FRAMES", default="output/frames/", help="Output frames directory")
parser.add_argument('-out', dest="OUTPUT_VIDEO", default="output/aviation_visualization.mp4", help="Output video if applicable (must also include -map flag)")
parser.add_argument('-debug', dest="DEBUG", action="store_true", help="Just output debug image?")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing frames?")
parser.add_argument('-map', dest="OUTPUT_WITH_MAP", action="store_true", help="Also output video with map?")
a = parser.parse_args()
# Parse arguments

_, airports = readCsv(a.AIRPORTS_FILE)
_, routes = readCsv(a.ROUTES_FILE)

rows = sorted(rows, key=lambda r: r['yearorig'])
(yearStart, yearEnd) = (rows[0]['yearorig'], rows[-1]['yearorig'])

pprint(f'Time range: {yearStart}, {yearEnd}')

if a.DEBUG:

    width = 1920
    height = width/2
    dotRadius = 6
    img = readImage("img/map.png")
    img = resizeImage(img, width, height, mode="warp")
    draw = ImageDraw.Draw(img)

    for row in rows:
        lat = row['Latitude']
        lng = row['Longitude']
        ny = norm(lat, (90, -90))
        nx = norm(lng, (-180, 180))
        y = ny * height
        x = nx * width
        x0 = x - dotRadius
        y0 = y - dotRadius
        x1 = x + dotRadius
        y1 = y + dotRadius
        draw.ellipse((x0, y0, x1, y1), fill=(255, 0, 0))

    img.save("tmp/debug.png")
    sys.exit()

template = readTextFile(a.TEMPLATE_FILE)

dataStr = '';
rowCount = len(rows)
for i, row in enumerate(rows):
    lat = row['Latitude']
    lng = row['Longitude']
    ny = norm(lat, (90, -90))
    nx = norm(lng, (-180, 180))

    year = row['yearorig']
    nt = norm(year, (yearStart, yearEnd+1))

    dataStr += f'{{x: {nx}, y: {ny}, t: {nt}}}'
    if i < rowCount-1:
        dataStr += ',';

scriptString = template.replace('{cityData}', dataStr)
writeTextFile(a.OUTPUT_FILE, scriptString)
