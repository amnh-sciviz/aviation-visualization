# -*- coding: utf-8 -*-

import argparse
import os
from PIL import Image, ImageColor, ImageDraw
from pprint import pprint
import sys
import time

from lib.collection_utils import *
from lib.image_utils import *
from lib.io_utils import *
from lib.math_utils import *
from lib.string_utils import *

# input
parser = argparse.ArgumentParser()
parser.add_argument('-airports', dest="AIRPORTS_FILE", default="data/airports.dat.csv", help="Input airports csv file")
parser.add_argument('-routes', dest="ROUTES_FILE", default="data/routes.dat.csv", help="Input routes csv file")
parser.add_argument('-width', dest="WIDTH", default=4320, type=int, help="Width of video")
parser.add_argument('-height', dest="HEIGHT", default=2160, type=int, help="Height of video")
parser.add_argument('-fps', dest="FRAMES_PER_SECOND", default=30, type=int, help="Frames per second of video")
parser.add_argument('-duration', dest="DURATION", default=20, type=float, help="Target duration in seconds")
parser.add_argument('-route_dur', dest="MAX_SECONDS_PER_ROUTE", default=8, type=float, help="Max duration of a route in seconds")
parser.add_argument('-route_dur_min', dest="MIN_SECONDS_PER_ROUTE", default=2, type=float, help="Min duration of a route in seconds")
parser.add_argument('-route_tail', dest="ROUTE_TAIL", default=0.5, type=float, help="How long the route tail should be as a percent of full route")
parser.add_argument('-count', dest="COUNT", default=10000, type=int, help="Number of routes to process")
parser.add_argument('-img', dest="MAP_IMAGE_FILE", default="img/map.png", help="Background map image file")
parser.add_argument('-color', dest="LINE_COLOR", default="#b31e1e", help="Color of line")
parser.add_argument('-line', dest="LINE_WIDTH", default=2, type=int, help="Width of line")
parser.add_argument('-res', dest="RESOLUTION", default=2, type=int, help="Multiply resolution by this much")
parser.add_argument('-frames', dest="OUTPUT_FRAMES", default="output/frames/", help="Output frames directory")
parser.add_argument('-out', dest="OUTPUT_VIDEO", default="output/aviation_visualization.mp4", help="Output video if applicable (must also include -map flag)")
parser.add_argument('-seed', dest="SEED", default=8, type=int, help="Seed for randomizing routes")
parser.add_argument('-debug', dest="DEBUG", action="store_true", help="Just output debug image?")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing frames?")
parser.add_argument('-map', dest="OUTPUT_WITH_MAP", action="store_true", help="Output video with map?")
a = parser.parse_args()

w = a.WIDTH * a.RESOLUTION
h = a.HEIGHT * a.RESOLUTION

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

def drawArc(fromX, fromY, toX, toY, im, progress):
    global a
    global w
    global h

    progressHead = min(progress * 2, 1.0)
    progressTail = norm(progress, (0.5, 1.0), limit=True)

    midX, midY = midpoint((fromX, fromY), (toX, toY))
    radiusA = distance(fromX, fromY, midX, midY)
    radiusB = radiusA / 2
    lineWidth = a.LINE_WIDTH * a.RESOLUTION
    padding = lineWidth * 2

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
    fromDegreesInt = fromDegrees
    toDegrees = 0
    toDegreesInt = toDegrees
    degreesDecimal = 0
    isReverseDirection = (fromX > toX)

    # if fromY > h * 0.5 and toY > h * 0.5:
    #     fromDegrees = 0
    #     toDegrees = 180
    #     isReverseDirection = (fromX < toX)

    if isReverseDirection:
        fromDegrees = lerp((toDegrees, fromDegrees), progressHead)
        fromDegreesInt = ceilInt(fromDegrees)

    else:
        toDegrees = lerp((fromDegrees, toDegrees), progressHead)
        toDegreesInt = floorInt(toDegrees)

    x0 = padding
    y0 = padding + (radiusA - radiusB)
    x1 = x0 + radiusA * 2
    y1 = y0 + radiusB * 2
    arcImW = arcImH = roundInt(radiusA * 2 + padding * 2)

    arcIm = Image.new(mode="RGBA", size=(arcImW, arcImH), color=(0,0,0,0))
    arcDraw = ImageDraw.Draw(arcIm)
    lineColor = list(ImageColor.getrgb(a.LINE_COLOR))

    totalDegrees = ceilInt(abs(toDegrees - fromDegrees))
    for i in range(totalDegrees):
        progressDegrees = 1.0 - i / 179
        toDegreesPartial = ceilInt(toDegrees) - i
        fromDegreesPartial = toDegreesPartial - 1
        if i == 0:
            toDegreesPartial = toDegrees

        if isReverseDirection:
            fromDegreesPartial = floorInt(fromDegrees) + i
            toDegreesPartial = fromDegreesPartial + 1
            if i == 0:
                fromDegreesPartial = fromDegrees

        alpha = roundInt(progressDegrees * (1.0 - progressTail) * 255)
        lineColorWithAlpha = tuple(lineColor + [alpha])

        arcDraw.arc([x0, y0, x1, y1], fromDegreesPartial, toDegreesPartial, lineColorWithAlpha, lineWidth)

    arcIm = arcIm.rotate(angle=-angleBetweenPoints)

    arcX = roundInt(midX - arcImW * 0.5)
    arcY = roundInt(midY - arcImH * 0.5)
    offsetX = 0
    offsetY = 0
    if arcX < 0:
        offsetX = -arcX
        arcX = 0
    if arcY < 0:
        offsetY = -arcY
        arcY = 0
    im.alpha_composite(arcIm, (arcX, arcY), (offsetX, offsetY))

def drawFrame(frame, filename, routes, withMap):
    global a
    global w
    global h

    if not a.OVERWRITE and os.path.isfile(filename):
        return

    baseIm = None
    if not withMap:
        baseIm = Image.new(mode="RGBA", size=(w, h), color=(0,0,0,0))
    else:
        baseIm = Image.open(a.MAP_IMAGE_FILE)
        baseIm = baseIm.convert("RGBA")
        baseIm = baseIm.resize((w, h), resample=Image.LANCZOS)

    # for i, airport in enumerate(airports):
    #     draw.point([airport['x'], airport['y']], fill=a.LINE_COLOR)
    # baseIm.save("output/debug.png")
    # sys.exit()

    routeCount = len(routes)
    for i, route in enumerate(routes):
        if frame < route["frameStart"] or frame > route["frameEnd"]:
            continue

        progress = norm(frame, (route["frameStart"], route["frameEnd"]), limit=True)

        source = route["source"]
        dest = route["dest"]
        fromX, fromY, toX, toY = (source["x"], source["y"], dest["x"], dest["y"])

        deltaX = abs(fromX - toX)

        if deltaX <= w*0.5:
            drawArc(fromX, fromY, toX, toY, baseIm, progress)

        # distance is too far; go in the other direction (thus need to draw two arcs)
        else:
            fromX1, fromY1, toX1, toY1 = (fromX, fromY, toX-w, toY)
            fromX2, fromY2, toX2, toY2 = (fromX+w, fromY, toX, toY)

            if fromX > toX:
                fromX1, fromY1, toX1, toY1 = (fromX, fromY, toX+w, toY)
                fromX2, fromY2, toX2, toY2 = (fromX-w, fromY, toX, toY)

            drawArc(fromX1, fromY1, toX1, toY1, baseIm, progress)
            drawArc(fromX2, fromY2, toX2, toY2, baseIm, progress)

    if a.RESOLUTION > 1:
        baseIm = baseIm.resize((a.WIDTH, a.HEIGHT), resample=Image.LANCZOS)

    baseIm.save(filename)

def main(a):
    _, airports = readCsv(a.AIRPORTS_FILE)
    _, routes = readCsv(a.ROUTES_FILE)

    for i, airport in enumerate(airports):
        lat, lon = (airport['Latitude'], airport['Longitude'])
        nx, ny = (norm(lon, (-180, 180)), norm(lat, (90, -90)))
        x, y = (nx * w, ny * h)

        airports[i]['x'] = x
        airports[i]['y'] = y

    airportLookup = createLookup(airports, "Airport ID")

    # only take one direction of a route
    routeIds = []
    uniqueRoutes = []
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

        if source["x"] == dest["x"] and source["y"] == dest["y"]:
            print(f'Source and destination is the same for route {sourceId} to {destId}')
            continue

        route["source"] = source
        route["dest"] = dest

        id = tuple(sorted([sourceId, destId]))
        if id not in routeIds:
            routeIds.append(routeIds)
            uniqueRoutes.append(route)

    # randomize
    seed = a.SEED
    for i, route in enumerate(uniqueRoutes):
        uniqueRoutes[i]['random'] = randomInt(seed=seed)
        seed = uniqueRoutes[i]['random']
    uniqueRoutes = sorted(uniqueRoutes, key=lambda r: r['random'])

    print(f'{len(uniqueRoutes)} unique routes')
    routeCount = min(len(uniqueRoutes), a.COUNT)
    print(f'{routeCount} sliced routes')
    routes = uniqueRoutes[:routeCount]

    padSeconds = 2
    totalFrames = a.FRAMES_PER_SECOND * a.DURATION
    totalActiveFrames = totalFrames - a.FRAMES_PER_SECOND * padSeconds
    maxDistance = w * 0.5
    for i, route in enumerate(routes):
        n = i / (routeCount-1)
        routes[i]["frameStart"] = roundInt(n * (totalActiveFrames-1))
        routeDistance = distance(route["source"]["x"], route["source"]["y"], route["dest"]["x"], route["dest"]["y"])
        nMaxDistance = routeDistance / maxDistance
        routeDuration = max(nMaxDistance * a.MAX_SECONDS_PER_ROUTE, a.MIN_SECONDS_PER_ROUTE)
        routeDurationFrames = roundInt(routeDuration * a.FRAMES_PER_SECOND)
        routes[i]["frameEnd"] = routes[i]["frameStart"] + routeDurationFrames

    if a.OVERWRITE:
        removeDir(a.OUTPUT_FRAMES)
    makeDirectories([a.OUTPUT_FRAMES, a.OUTPUT_VIDEO])

    for i in range(totalFrames):
        filename = a.OUTPUT_FRAMES + "frame." + zeroPad(i, totalFrames) + ".png"
        drawFrame(i, filename, routes, withMap=a.OUTPUT_WITH_MAP)
        printProgress(i+1, totalFrames)

    if a.OUTPUT_WITH_MAP:
        compileFrames(a.OUTPUT_FRAMES + "frame.%s.png", a.FRAMES_PER_SECOND, a.OUTPUT_VIDEO, len(str(totalFrames)))

    # pprint(airports[0])
    # pprint(routes[0])

main(a)
