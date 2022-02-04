# -*- coding: utf-8 -*-

import csv
import glob
import os
from pprint import pprint
import re
import shutil
import sys

from lib.collection_utils import *
from lib.math_utils import *
from lib.string_utils import *

def appendToFilename(fn, appendString):
    ext = getFileExt(fn)
    extLen = len(ext)
    return fn[:-extLen] + appendString + ext

def getBasename(fn):
    return os.path.splitext(os.path.basename(fn))[0]

def getFileExt(fn):
    basename = os.path.basename(fn)
    return "." + basename.split(".")[-1]

def makeDirectories(filenames):
    if not isinstance(filenames, list):
        filenames = [filenames]
    for filename in filenames:
        dirname = os.path.dirname(filename)
        if len(dirname) > 0 and not os.path.exists(dirname):
            os.makedirs(dirname)

def parseHeadings(arr, headings):
    newArr = []
    headingKeys = [key for key in headings]
    for i, item in enumerate(arr):
        newItem = {}
        for key in item:
            if key in headingKeys:
                newItem[headings[key]] = item[key]
        newArr.append(newItem)
    return newArr

def parseLists(arr, delimeter):
    for i, item in enumerate(arr):
        if isinstance(item, (list,)):
            for j, v in enumerate(item):
                arr[i][j] = parseList(v, delimeter)
        else:
            for key in item:
                arr[i][key] = parseList(item[key], delimeter)
    return arr

def readCsv(filename, headings=False, doParseNumbers=True, skipLines=0, encoding="utf-8-sig", readDict=True, verbose=True, doParseLists=False, listDelimeter=" | "):
    rows = []
    fieldnames = []
    if os.path.isfile(filename):
        lines = []
        with open(filename, 'r', encoding=encoding, errors="replace") as f:
            lines = list(f)
        if skipLines > 0:
            lines = lines[skipLines:]
        if readDict:
            reader = csv.DictReader(lines, skipinitialspace=True)
            fieldnames = list(reader.fieldnames)
        else:
            reader = csv.reader(lines, skipinitialspace=True)
        rows = list(reader)
        if headings:
            rows = parseHeadings(rows, headings)
        if doParseLists:
            rows = parseLists(rows, listDelimeter)
        if doParseNumbers:
            rows = parseNumbers(rows)
        if verbose:
            print("  Read %s rows from %s" % (len(rows), filename))
    return (fieldnames, rows)

def readTextFile(filename):
    contents = ""
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf8", errors="replace") as f:
            contents = f.read()
    return contents

def removeDir(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)

def removeFiles(listOrString):
    filenames = listOrString
    if not isinstance(listOrString, list) and "*" in listOrString:
        filenames = glob.glob(listOrString)
    elif not isinstance(listOrString, list):
        filenames = [listOrString]
    print("Removing %s files" % len(filenames))
    for fn in filenames:
        if os.path.isfile(fn):
            os.remove(fn)

def replaceFileExtension(fn, newExt):
    extLen = len(getFileExt(fn))
    i = len(fn) - extLen
    return fn[:i] + newExt

def writeTextFile(filename, text):
    with open(filename, "w", encoding="utf8", errors="replace") as f:
        f.write(text)
