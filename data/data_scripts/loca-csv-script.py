import sys
import csv
from collections import OrderedDict

HEADER = ['LON', 'LAT', '(hist) 1976-2005', '(4.5) 2016-2045', '(4.5) 2036-2065', '(4.5) 2070-2099', '(8.5) 2016-2045', '(8.5) 2036-2065', '(8.5) 2070-2099', '(top) 2016-2045', '(top) 2036-2065', '(top) 2070-2099']

LON_I = 0
LAT_I = 1
HIST_I = 2
RCP85_2099_I = 8

FILENAME_TO_INDEX = { # getting data in one spot, trying to stay consistent
    "../raw_data/loca-precipitation-annual.csv": (0, 1), # tup[0] for historical, tup[1] for 8.5 2070-99
    "../raw_data/max-5-day-temp-annual.csv": (2, 3),
    "../raw_data/min-5-day-temp-annual.csv": (4, 5)
}

NEW_HEADER = [
    "LON",
    "LAT",
    "precip_historical",
    "precip_85_2099",
    "max_5_historical",
    "max_5_85_2099",
    "min_5_historical",
    "min_5_85_2099"
]

NULL_ROW = [-999.0, -999.0, -999.0, -999.0, -999.0, -999.0]

def getCoords(fileName):
    with open(fileName) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        numRowsRead = 0
        coords = set()
        for row in csvReader:
            if row != HEADER:
                numRowsRead+=1
                lon = float(row[0])
                lat = float(row[1])
                coords.add((lon, lat))
        return coords


def addData(fileName, newD):
    with open(fileName) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        for row in csvReader:
            if row != HEADER:
                coords = (float(row[LON_I]), float(row[LAT_I]))
                hist = float(row[HIST_I])
                rcp85 = float(row[RCP85_2099_I])
                if not coords in newD:
                    newD[coords] = [None]*(len(NEW_HEADER) - 2) # - lat, lon which are in key
                histI, rcp85I = FILENAME_TO_INDEX[fileName]
                newD[coords][histI] = hist
                newD[coords][rcp85I] = rcp85

        return coords

def printMinMaxRCP85(fileName):
    with open(fileName) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        maxRCP = 0
        maxR = []
        minRCP = int(sys.maxsize)
        minR = []
        for row in csvReader:
            if row != HEADER:
                rcp85 = float(row[RCP85_2099_I])
                if rcp85 != NULL_ROW[0]:
                    if rcp85 > maxRCP:
                        maxRCP = rcp85
                        maxR = row
                    if rcp85 < minRCP:
                        minRCP = rcp85
                        minR = row

        print("min: ", minR[1], ",", minR[0], ", ", minR[HIST_I], minR[RCP85_2099_I])
        print("max: ", maxR[1], ",", maxR[0], ", ", maxR[HIST_I], maxR[RCP85_2099_I])
        print(maxR)

def writeNewDictToCSV(dataD, header, fileName):
    with open(fileName, 'w') as csvfile:
        csvfile.write(header)
        csvfile.write("\n")
        cWriter = csv.writer(csvfile, delimiter=',')
        for k, v in dataD.items():
            row = [k[0], k[1]] + v
            cWriter.writerow(row)


def cleanAndConsolidate():
    newCSVDict = OrderedDict()
    addData("../raw_data/loca-precipitation-annual.csv", newCSVDict)
    addData("../raw_data/max-5-day-temp-annual.csv", newCSVDict)
    addData("../raw_data/min-5-day-temp-annual.csv", newCSVDict)
    print(len(newCSVDict))
    cleanCVSDict = OrderedDict()
    for k, v in newCSVDict.items():
        if v != NULL_ROW:
            cleanCVSDict[k] = v
    writeNewDictToCSV(cleanCVSDict, (',').join(NEW_HEADER), "clean_consolidated_loca.csv")

def printInterestingRows():
    # printMinMaxRCP85("../raw_data/loca-precipitation-annual.csv")
    # printMinMaxRCP85("../raw_data/loca-precipitation-annual.csv")
    printMinMaxRCP85("../raw_data/max-5-day-temp-annual.csv")

def main():
    # cleanAndConsolidate()
    printInterestingRows()

main()
