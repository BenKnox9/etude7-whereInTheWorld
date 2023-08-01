import math
import sys
import pandas as pd
import geojson
import fileinput
import re

"""
Author: Ben Knox
Created: 18/05/2023
Description: This script performs data cleansing and validation on coordinate inputs and outputs all valid coordinates
in a geojson with POINT(Longitude, Latitude) and its label.
"""

finalResult = []
globLabel = ""
inputLine = ""

"""
dfToGeojson:
Method which takes in a dataframe, stores all points in the form POINT and stores the label with their corresponding point. 
The method will open the file jsonValues.geojson and write all points that it has collected to that file.

Params: df - a dataframe of Points and labels.
"""


def dfToGeojson(df):
    global finalResult
    features = []

    def insert_features(X): return features.append(
        geojson.Feature(geometry=geojson.Point((X["long"],
                                                X["lat"])),
                        properties=dict(label=X["label"])))
    df.apply(insert_features, axis=1)
    with open('jsonValues.geojson', 'w', encoding='utf8') as f:
        geojson.dump(geojson.FeatureCollection(features),
                     f, sort_keys=True, ensure_ascii=False)


"""
splitInput:
Method which takes in either user input or a file input, reads line by line and then calls most other methods in order validating and changing the
input string as it goes through. This is all encompassed in a try except so any time the line is unable to process invalid method is called.

Params: inputFile - a file with coordinates on each new line, alternatively if inputFile is set to "stdin" the method will take in user input.
"""


def splitInput(inputFile):
    global finalResult
    global globLabel
    global inputLine
    # for debugging
    # lineCount = 1

    if inputFile == "stdin":
        lines = sys.stdin
    else:
        lines = fileinput.input(inputFile)
    for line in lines:
        if not line.strip():
            continue
        # for debugging
        # print("line number: ", lineCount)
        # lineCount += 1

        inputLine = line.rstrip('\n')
        try:
            arr = hasLabel(line).split(",")

            result = []
            for sub in arr:
                if (sub[0] == " "):
                    sub = sub.replace(" ", "", 1)
                result.append(sub.replace("\n", ""))

            if len(result) == 1:
                result = addComma(result)

            result = swapSigns(result)
            result = removeNESW(result)
            result = isDD(result)
            if result == False or result == None:
                invalid()
                continue

        except:
            invalid()
            continue

        if float(result[0]) > 90 or float(result[0]) < -90 or float(result[1]) > 180 or float(result[1]) < -180:
            invalid()
            continue
        # for debugging
        # print(result)

        finalResult.append(toData(result))


"""
hasLabel:
Method which uses a regex to check for a label at the end of a coordinate. Where there is one it will trim the label off the input string
and save the label in the global variable 'globLabel'.

Params: inputString - the line read by the file reader.
Return: a string of coordinates without label.
"""


def hasLabel(inputString):
    global globLabel
    labelRgx = r"\s(?!(?:[nNsSeEwW])\b)[^\d]+\w+\b$"
    match = re.search(labelRgx, inputString)
    if match:
        # separating the label and the coordinate
        coordinates = re.sub(labelRgx, "", inputString).strip()
        coordinates = coordinates.rstrip(',')
        label = match.group().strip()
        globLabel = label
        return coordinates
    else:
        globLabel = ""
        return inputString


"""
addComma:
Method which is called if coordinates aren't separated by a comma. The method will then find and put the comma in the appropriate place between coordinates.
In the order of the method it will count how many times there is a cardinality and whether its at the start or not. Then uses a regex to insert a space before and after 
all cardinalities. The method will then split by the number of spaces.

Params: inputArr - Will be an array of length 1, just containing the input string.
Return: coordArr - the coordinates split by the comma added will give an array of length 2 which is returned.
"""


def addComma(inputArr):
    coordsString = inputArr[0]
    cardCount = 0
    letterCount = 0
    isStart = False

    # Counting the number of cardinal directions in the input
    a = ['N', 'E', 'S', 'W', 'n', 'e', 's', 'w']
    for c in coordsString:
        if c in a:
            cardCount += 1
            if letterCount == 0:
                isStart = True
        letterCount += 1

    # Adding spaces before and after all cardinal directions
    if not len(coordsString.split(" ")) == 2:
        pattern = r'(?<=[^\s])([NESWnesw])'
        coordsString = re.sub(pattern, r' \1', coordsString)
        pattern = r"([NEWSnews])(?!\s)"
        coordsString = re.sub(pattern, r"\1 ", coordsString)
        coordsString = coordsString.rstrip()

    if len(coordsString.split(" ")) == 2:
        coordArr = coordsString.split(" ")

    # counting the number of spaces and splitting by the middle space
    else:
        numSpaces = coordsString.count(" ")

        n = math.floor(numSpaces / 2)
        if numSpaces != 1:
            n += 1

        start = coordsString.find(" ")
        while start >= 0 and n > 1:
            start = coordsString.find(" ", start + 1)
            n -= 1

        newCoords = coordsString[:start] + "," + coordsString[start+1:]
        coordArr = newCoords.split(",")

    # If the split has split before the cardinality rather than after, transfer it back
    if coordArr[1][0] in a and cardCount == 1 and not isStart:
        coordArr[0] = coordArr[0] + coordArr[1][0]
        coordArr[1] = coordArr[1].replace(coordArr[1][0], "", 1)

    return coordArr


"""
swapSigns:
Method which will swap the coordinates around for example if the inputArr is ['40 E', '60 N'] it will need to be swapped to 
['60 N', '40 E']. this method will check if any of NnSs are in the second part of the coordinate and vice versa. If either of them are in the incorrect position 
both items in the array are swapped.

Params: inputArr - an array of length two containing both coordinates
Return: inputArr - the same array but coordinates will be swapped if need be
"""


def swapSigns(inputArr):
    lon = ["N", "S", "n", "s"]
    lat = ["E", "W", "e", "w"]
    dms = ["d", "m", "s"]
    seg1order = True
    seg2order = True
    dmsCount = 0

    # Check for East or West in the first segment
    currentString = inputArr[0]
    for i in lat:
        if i in currentString:
            seg1order = False

    # Check if string contains dms
    currentString = inputArr[1]
    for i in dms:
        if i in currentString:
            dmsCount += 1

    # Check for North and South in second segment but do not check for dms
    for i in lon:
        if i in currentString:
            if i == 's':
                if not dmsCount >= 2:
                    seg2order = False

    # flip order
    if seg1order == False or seg2order == False:
        return [inputArr[1], inputArr[0]]
    else:
        return inputArr


"""
removeNESW:
Method which removes the NESW. If the cardinal direction is W or S then a negative will be added to the front of the coordinate. This is performed with for loops,
they will iterate through each segment and replace the cardinal direction with either an empty string or an empty string with a minus at the beginning. It will also
get rid of unnecessary whitespace at the start of the string. This method also deals with the case that the coordinate is incorrect e.g. "41 N 89 S", The 'S' will not be replaced
so once it comes to calculation this will fail and this coordinate will fall into the except block in the splitInput method.

Param: inputArr - An array of length two containing the coordinate
Return: result - The same array but with cardinal directions removed
"""


def removeNESW(inputArr):
    north = ["N", "n"]
    south = ["S", "s"]
    east = ["E", "e"]
    west = ["W", "w"]

    seg1String = inputArr[0]
    seg2String = inputArr[1]
    result = []
    swapCount = 0

    # Replace N or n with ""
    for n in north:
        if n in seg1String:
            seg1String = seg1String.replace(n, "")
            swapCount += 1

    # Replace E or e with ""
    for e in east:
        if e in seg2String:
            seg2String = seg2String.replace(e, "")
            swapCount += 1

    # Replace W or w with a minus and ""
    for w in west:
        if w in seg2String:
            seg2String = "-" + seg2String.replace(w, "")
            swapCount += 1

    if swapCount < 2:
        # Replace S or s with a minus and ""
        for s in south:
            if s in seg1String:
                seg1String = "-" + seg1String.replace(s, "")
                swapCount += 1

    # Get rid of unnecessary whitespace
    if seg1String[0] == " " or (seg1String[0] == "-" and seg1String[1] == " "):
        seg1String = seg1String.replace(" ", "", 1)
    if seg2String[0] == " " or (seg2String[0] == "-" and seg2String[1] == " "):
        seg2String = seg2String.replace(" ", "", 1)

    result = [seg1String, seg2String]
    return result


"""
isDD:
Method which checks if the coordinate is in decimal degree form. If so the array is returned. If not the method will call the is DDM method. The method works by trying
to cast each segment to a float, which will work if it is in decimal degree form but otherwise wont.

Param: inputArr - Array of length 2 containing the coordinate.
Return: either the result or returns the value of the next method called, isDDM.

"""


def isDD(inputArr):
    try:
        for i in inputArr:
            float(i)
            s1 = inputArr[0]
            s1 = s1.strip()

            s2 = inputArr[1]
            s2 = s2.strip()

            result = [s1, s2]
            return result

    except ValueError:
        return isDDM(inputArr)


"""
isDDM:
Method which checks if the coordinate is in degrees and decimal minutes form. This method works by stripping everything which isn't a number a decimal or a minus. 
Then it will try to cast both portions of each segment to a float. If this works the calculation is made, if not the isDMS method is called.

Param: inputArr - Array of length 2 containing the coordinate.
Return: either the result or returns the value of the next method called, isDMS.

"""


def isDDM(inputArr):
    try:
        latNeg = False
        lonNeg = False

        # Get rid of uncecessary characters
        s1 = inputArr[0]
        s1 = re.sub(r'[^0-9.-]', ' ', s1)
        s1 = s1.strip()
        s1Arr = s1.split(" ", 1)

        s2 = inputArr[1]
        s2 = re.sub(r'[^0-9.-]', ' ', s2)
        s2 = s2.strip()
        s2Arr = s2.split(" ", 1)

        # Perform calculations to change from ddm to dd

        # check if value is negative
        if float(s1Arr[0]) < 0:
            latNeg = True
        if float(s2Arr[0]) < 0:
            lonNeg = True

        if len(s1Arr) == 2 and len(s2Arr) == 2:
            s1dd = abs(float(s1Arr[0])) + (float(s1Arr[1])/60)
            s2dd = abs(float(s2Arr[0])) + (float(s2Arr[1])/60)

            # If the value was negative, make result negative
            if latNeg:
                s1dd = -s1dd

            if lonNeg:
                s2dd = -s2dd

            result = [str(s1dd), str(s2dd)]
            return result
    except ValueError:
        return isDMS(inputArr)


"""
isDMS:
Method which checks if the coordinate is in degrees minutes seconds form. This method will operate similarly to is DDM, stripping all non numbers decimal points and minus signs. 
It will also get rid of all whitespace which is bigger than one space. Then a similar method is used where if the cast to float works for each portion then the calculation is made.
Otherwise the False is returned and once back at the splitInput method the invalid method will be called on this coordinate.

Param: inputArr - Array of length 2 containing the coordinate.
Return: either the result or returns false.
"""


def isDMS(inputArr):
    try:
        latNeg = False
        lonNeg = False
        # Get rid of uncecessary characters
        s1 = inputArr[0]
        s1 = re.sub(r'[^0-9.-]', ' ', s1)
        s1 = s1.strip()
        s1 = re.sub('\s+', ' ', s1)

        s2 = inputArr[1]
        s2 = re.sub(r'[^0-9.-]', ' ', s2)
        s2 = s2.strip()
        s2 = re.sub('\s+', ' ', s2)

        # Perform calculations to change from dms to dd
        if len(s1.split(" ")) == 3 and len(s2.split(" ")) == 3:
            s1Arr = s1.split(" ")
            s2Arr = s2.split(" ")

            # check if value is negative
            if float(s1Arr[0]) < 0:
                latNeg = True
            if float(s2Arr[0]) < 0:
                lonNeg = True

            s1dd = abs(float(s1Arr[0])) + (float(s1Arr[1])/60) + \
                (float(s1Arr[2])/3600)
            s2dd = abs(float(s2Arr[0])) + (float(s2Arr[1])/60) + \
                (float(s2Arr[2])/3600)

            # If the value was negative then make result negative
            if latNeg:
                s1dd *= -1

            if lonNeg:
                s2dd *= -1

            result = [str(s1dd), str(s2dd)]
            return result
    except ValueError:
        return False


""" 
invalid:
Method which is called when an input is deemed invalid, will then print the offending line.
"""


def invalid():
    global inputLine
    print("Unable to process: ", inputLine)
    return


"""
toData:
Method which puts all coordinate results and their labels into a nested array. This nested array will be used in the dfToGeojson method and the finalArr will be its input. 

Param: inputArr - Array of length 2 containing the coordinates.
Return: finalArr - the final array containing all coordinates.
"""


def toData(inputArr):
    global globLabel
    label = globLabel.replace("\n", "")
    finalArr = []
    lat = float(inputArr[0])
    lon = float(inputArr[1])

    finalArr.append(lat)
    finalArr.append(lon)
    finalArr.append(label)
    return finalArr


"""
createFile:
Method which calls all relevant methods and converts the finalArr, nested array, into a dataframe for the use of the dfToGeojson method.

Param: inputFile - the file of coordinates that need validating
"""


def createFile(inputFile):
    splitInput(inputFile)

    col = ['lat', 'long', 'label']

    df = pd.DataFrame(finalResult, columns=col)
    dfToGeojson(df)


createFile("testcases.txt")
"""
To check coordinates without mapping them createFile can be called. To check coordinate results print statements in splitInput have been commented
out using the '#'

# if you want user input, enter "stdin" as the param for the createFile method
# to end the stdin on mac, press control + D
# on windows press control + z and then enter
"""
