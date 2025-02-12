from dokkanfunctions import *

from dokkanfunctions import *


stringToFind = 'Can be activated'

includeAsElementOf=True

CSVtoExclude = []

try:
    inttoFind = int(stringToFind)
except ValueError:
    inttoFind = None

try:
    floattoFind = float(stringToFind)
except ValueError:
    floattoFind = None

found=False
directory = "data/"
for filename in os.listdir(directory):
    if (filename.endswith(".csv") and filename not in CSVtoExclude):
        data = storedatabase(directory, filename)


        for row in data:
            for column in row:
                if(stringToFind!=None):
                    if (column==stringToFind or (includeAsElementOf and stringToFind in column)):
                        print(filename,data.index(row),row.index(column),data[0][row.index(column)])
                        found=True
                elif(inttoFind!=None or (includeAsElementOf and inttoFind in column)):
                    if column==inttoFind:
                        print(filename,data.index(row),row.index(column),data[0][row.index(column)])
                        found=True
                elif(floattoFind!=None or (includeAsElementOf and floattoFind in column)):
                    if column==floattoFind:
                        print(filename,data.index(row),row.index(column),data[0][row.index(column)])
                        found=True
    else:
        continue

if(found==False):
    print("Nothing found")