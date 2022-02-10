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

# pprint(airports[0])
# pprint(routes[0])

for i, a in enumerate(airports):
    lat, lon = (a['Latitude'], a['Longitude'])
    nx, ny = (norm(lon, (-180, 180)), norm(lat, (90, -90)))
    x, y = (nx * a.WIDTH, ny * a.HEIGHT)

    airports[i]['x'] = x
    airports[i]['y'] = y


airportLookup = createLookup(airports, "Airport ID"")
