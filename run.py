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
baseIm = baseIm.resize((w, h), resample=Image.LANCZOS)
draw = ImageDraw.Draw(baseIm)
defaultArcHeight = h / 12

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

    fromDegrees = 0
    toDegrees = 0
    x0 = y0 = x1 = y1 = 0

    if fromY == toY:
        if fromX == toX:
            print(f'Source and destination is the same for route {route["Source airport ID"]} to {route["Destination airport ID"]}')
            continue

        if fromX < toX:
            fromDegrees = -180
        else:
            toDegrees = -180

        x0 = min(fromX, toX)
        x1 = max(fromX, toX)
        y0 = fromY - defaultArcHeight
        y1 = fromY + defaultArcHeight

    elif fromX == toX:
        if fromY < toY:
            fromDegrees = -90
            toDegrees = 90
        else:
            fromDegrees = 90
            toDegrees = -90

        y0 = min(fromY, toY)
        y1 = max(fromY, toY)
        x0 = fromX - defaultArcHeight
        x1 = fromX + defaultArcHeight

    elif fromY < toY:
        y0 = fromY
        y1 = toY + (toY-fromY)

        if fromX < toX:
            fromDegrees = -90
            x0 = fromX - (toX - fromX)
            x1 = toX
        else:
            fromDegrees = -90
            toDegrees = -180
            x0 = fromX
            x1 = toX + (fromX - toX)

    else:
        y0 = toY
        y1 = fromY + (fromY-toY)

        if fromX < toX:
            fromDegrees = -180
            toDegrees = -90
            x0 = fromX
            x1 = toX + (toX - fromX)

        else:
            toDegrees = -90
            x0 = toX - (fromX - toX)
            x1 = fromX


    draw.arc([x0, y0, x1, y1], fromDegrees, toDegrees, a.LINE_COLOR, a.LINE_WIDTH)

    printProgress(i+1, routeCount)

baseIm.save("output/debug.png")
