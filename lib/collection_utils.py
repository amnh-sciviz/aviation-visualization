
import collections
import itertools
from operator import itemgetter
from pprint import pprint
import random
import sys

from lib.math_utils import *

def addIndices(arr, keyName="index", startIndex=0):
    for i, item in enumerate(arr):
        arr[i][keyName] = startIndex + i
    return arr

def addValueToStringOrList(strOrArr, value):
    if value == "":
        return strOrArr
    values = value
    if not isinstance(value, list):
        values = [str(value).strip()]
    if not isinstance(strOrArr, list):
        strOrArr = str(strOrArr).strip()
        if strOrArr == "":
            strOrArr = []
        else:
            strOrArr = [strOrArr]
    strOrArr = [str(v).strip() for v in strOrArr]
    for value in values:
        if value not in strOrArr:
            strOrArr.append(value)
    return strOrArr

def createLookup(arr, key):
    return dict([(str(item[key]), item) for item in arr])

def findByValue(arr, key, value):
    found = None
    for item in arr:
        if key in item and item[key] == value:
            found = item
            break
    return found

def flattenList(arr):
    return [item for sublist in arr for item in sublist]

def getCounts(arr, key=False, presence=False):
    values = arr[:]
    if key is not False:
        values = []
        for item in arr:
            value = ""
            if key in item:
                value = item[key]
            if isinstance(value, list) and not presence:
                values += value
            else:
                values.append(value)
        values = [str(v).strip() for v in values]
    if presence:
        values = ["no" if len(v) < 1 else "yes" for v in values]
    counter = collections.Counter(values)
    return counter.most_common()

def groupList(arr, groupBy, sort=False, desc=True):
    groups = []
    arr = sorted(arr, key=itemgetter(groupBy))
    for key, items in itertools.groupby(arr, key=itemgetter(groupBy)):
        group = {}
        litems = list(items)
        count = len(litems)
        group[groupBy] = key
        group["items"] = litems
        group["count"] = count
        groups.append(group)
    if sort:
        reversed = desc
        groups = sorted(groups, key=lambda k: k["count"], reverse=reversed)
    return groups

def prependAll(arr, prepends):
    if isinstance(prepends, tuple):
        prepends = [prepends]

    for i, item in enumerate(arr):
        for p in prepends:
            newKey = None
            if len(p) == 3:
                key, value, newKey = p
            else:
                key, value = p
                newKey = key
            arr[i][newKey] = value + item[key]

    return arr

def removeValueFromStringOrList(strOrArr, value):
    if value == "":
        return strOrArr
    values = value
    if not isinstance(value, list):
        values = [str(value).strip()]
    if not isinstance(strOrArr, list):
        strOrArr = str(strOrArr).strip()
        if strOrArr == "":
            strOrArr = []
        else:
            strOrArr = [strOrArr]
    strOrArr = [str(v).strip() for v in strOrArr]
    strOrArr = [v for v in strOrArr if v not in values]
    if len(strOrArr) < 1:
        strOrArr = ""
    return strOrArr

def unique(arr):
    return list(set(arr))
