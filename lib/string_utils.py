from datetime import datetime, timedelta
import re
import string
import urllib

from lib.math_utils import *

def containsWordBoundary(rawValue, word, caseSensitive=False):
    if not caseSensitive:
        rawValue = rawValue.lower()
        word = word.lower()

    if re.search(r"\b" + re.escape(word) + r"\b", rawValue):
      return True

    return False

def itemNotEmpty(row, key):
    return (key in row and len(str(row[key]).strip()) > 0)

def normalizeWhitespace(value):
    value = str(value)
    value = re.sub('\s', ' ', value)
    value = value.strip()
    return value

def parseList(value, delimeter):
    delimeter = delimeter.strip()
    if not isinstance(value, str) or delimeter not in value:
        return value
    arr = [v.strip().strip(delimeter).strip() for v in value.split(delimeter)]
    return arr

def padNum(number, total):
    padding = len(str(total))
    return str(number).zfill(padding)

def pluralizeString(value):
    value = str(value).strip()
    if len(value) < 1:
        return value

    lvalue = value.lower()
    if lvalue.endswith('s'):
        return value
    elif lvalue.endswith('y'):
        return value[:-1] + 'ies'
    else:
        return value + 's'

def stringContainsNumbers(string):
    return any(char.isdigit() for char in string)

def stringToYear(value, minYear=1000, maxYear=2050):
    matches = re.findall('\d{4}', str(value))
    year = None
    if matches:
        for match in matches:
            matchInt = int(match)
            if (minYear is None or matchInt >= minYear) and (maxYear is None or matchInt <= maxYear):
                year = matchInt
                break
    return year

def stripTags(text):
    text = str(text)
    text = re.sub('<[^<]+?>', '', text)
    return text

def urlEncodeString(value):
    return urllib.parse.quote_plus(value)
