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
parser.add_argument('-color', dest="LINE_COLOR", default="#ff2e2e", help="Color of line")
parser.add_argument('-line', dest="LINE_WIDTH", default=4, type=int, help="Width of line")
parser.add_argument('-frames', dest="OUTPUT_FRAMES", default="output/frames/", help="Output frames directory")
parser.add_argument('-out', dest="OUTPUT_VIDEO", default="output/aviation_visualization.mp4", help="Output video if applicable (must also include -map flag)")
parser.add_argument('-debug', dest="DEBUG", action="store_true", help="Just output debug image?")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing frames?")
parser.add_argument('-map', dest="OUTPUT_WITH_MAP", action="store_true", help="Also output video with map?")
a = parser.parse_args()
# Parse arguments

_, airports = readCsv(a.AIRPORTS_FILE)
_, routes = readCsv(a.ROUTES_FILE)

routes = routes[:1000]

# x0 = 0
# y0 = 10
# x1 = 1
# y1 = 0
# print(angleBetween(x0, y0, x1, y1))
# print(angleBetween(x1, y1, x0, y0))
# x0 = 0
# y0 = 0
# x1 = 1
# y1 = 10
# print(angleBetween(x0, y0, x1, y1))
# print(angleBetween(x1, y1, x0, y0))
# sys.exit()

# pprint(airports[0])
# pprint(routes[0])

for i, airport in enumerate(airports):
    lat, lon = (airport['Latitude'], airport['Longitude'])
    nx, ny = (norm(lon, (-180, 180)), norm(lat, (90, -90)))
    x, y = (nx * a.WIDTH, ny * a.HEIGHT)

    airports[i]['x'] = x
    airports[i]['y'] = y

airportLookup = createLookup(airports, "Airport ID")

w = a.WIDTH
h = a.HEIGHT
# baseIm = Image.new(mode="RGBA", size=(w, h), color=(0,0,0,0))
baseIm = Image.open(a.MAP_IMAGE_FILE)
baseIm = baseIm.convert("RGBA")
baseIm = baseIm.resize((w, h), resample=Image.LANCZOS)

# for i, airport in enumerate(airports):
#     draw.point([airport['x'], airport['y']], fill=a.LINE_COLOR)
# baseIm.save("output/debug.png")
# sys.exit()

routeCount = len(routes)
for i, route in enumerate(routes):
    sourceId = str(route["Source airport ID"])
    destId = str(route["Destination airport ID"])

    if sourceId not in airportLookup:
        print(f'Could not find {sourceId} in airports')
        continue

    if destId not in airportLookup:
        print(f'Could not find {sourceId} in airports')
        continue

    source = airportLookup[sourceId]
    dest = airportLookup[destId]

    fromX, fromY, toX, toY = (source["x"], source["y"], dest["x"], dest["y"])

    if fromY == toY and fromX == toX:
        print(f'Source and destination is the same for route {route["Source airport ID"]} to {route["Destination airport ID"]}')
        continue

    midX, midY = midpoint((fromX, fromY), (toX, toY))
    radiusA = distance(fromX, fromY, midX, midY)
    radiusB = radiusA / 2
    padding = a.LINE_WIDTH * 2

    angleBetweenPoints = 0
    if fromY == toY:
        angleBetweenPoints = 0
    elif fromX < toX:
        angleBetweenPoints = angleBetween(fromX, fromY, toX, toY)
    elif fromX > toX:
        angleBetweenPoints = angleBetween(toX, toY, fromX, fromY)
    elif fromX == toX:
        angleBetweenPoints = 90

    fromDegrees = -180
    toDegrees = 0

    x0 = padding
    y0 = padding + (radiusA - radiusB)
    x1 = x0 + radiusA * 2
    y1 = y0 + radiusB * 2
    arcImW = arcImH = roundInt(radiusA * 2 + padding * 2)
    arcIm = Image.new(mode="RGBA", size=(arcImW, arcImH), color=(0,0,0,0))
    arcDraw = ImageDraw.Draw(arcIm)
    arcDraw.arc([x0, y0, x1, y1], fromDegrees, toDegrees, a.LINE_COLOR, a.LINE_WIDTH)
    arcIm = arcIm.rotate(angle=-angleBetweenPoints)
    arcX = roundInt(midX - arcImW * 0.5)
    arcY = roundInt(midY - arcImH * 0.5)
    if arcX > 0 and arcY > 0:
        baseIm.alpha_composite(arcIm, (arcX, arcY))

    printProgress(i+1, routeCount)

baseIm.save("output/debug.png")
