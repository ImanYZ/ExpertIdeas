# Import the required libraries.
import sys
import os

from datetime import datetime, date, time
import re
import time
import random
import json

# Import requests library.
import requests

import ucsv as csv
import unicodedata

print "Enter the name of the recommendations Stats dataset csv file without any sufix:"
datatsetFileName = raw_input()

if datatsetFileName == "":
    datatsetFileName = 'Ideas_Repec_Dataset_Pilot3_Clean_Recommendations_Stats'

with open(datatsetFileName + '.csv', 'rb') as fr:
    reader = csv.reader(fr)

    with open('Ideas_Repec_Dataset_Pilot3_Clean_Recommendations_Quality_Stats.csv', 'wb') as fw:
        writer = csv.writer(fw)

        pubResultRow = ['ID', 'Title', 'Crawled Class', 'API Class', 'API Weighted Average Class', 'Importance', 
            'API FA Class Probability', 'API GA Class Probability', 'API B Class Probability', 'API C Class Probability', 
            'API Start Class Probability', 'API Stub Class Probability', 'Edit Protection Level', 'Length', '# Views 90 Days']
        writer.writerow(pubResultRow)

        counter = 0
        header = next(reader)
        for row in reader:
            counter += 1
            print(counter)
            newRow = []
            newRow.append(row[0])
            newRow.append(row[1])
            newRow.append(row[3])

            while True:
                try:
                    r = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&pageids=' + str(row[0]))
                    break
                except:
                    pass
            r = r.json()
            query = r['query']
            pages = query['pages']
            pageID = pages[str(row[0])]
            revisions = pageID['revisions']
            revisionID = revisions[0]['revid']
            while True:
                try:
                    r = requests.get('https://ores.wmflabs.org/scores/enwiki/wp10/' + str(revisionID))
                    break
                except:
                    pass
            r = r.json()
            qualityClass = r[str(revisionID)]['prediction']
            newRow.append(qualityClass)

            probabilitiesOfEachClass = r[str(revisionID)]['probability']
            FAClassProbability = probabilitiesOfEachClass['FA']
            GAClassProbability = probabilitiesOfEachClass['GA']
            BClassProbability = probabilitiesOfEachClass['B']
            CClassProbability = probabilitiesOfEachClass['C']
            StartClassProbability = probabilitiesOfEachClass['Start']
            StubClassProbability = probabilitiesOfEachClass['Stub']

            weightedAverage = (float(StubClassProbability) + 2 * float(StartClassProbability) + 3 * float(CClassProbability) +
                4 * float(BClassProbability) + 5 * float(GAClassProbability) + 6 * float(FAClassProbability)) / (
                float(StubClassProbability) + float(StartClassProbability) + float(CClassProbability) +
                float(BClassProbability) + float(GAClassProbability) + float(FAClassProbability))

            if weightedAverage > 5.5:
                weightedAverage = "FA"
            elif weightedAverage > 4.5:
                weightedAverage = "GA"
            elif weightedAverage > 3.5:
                weightedAverage = "B"
            elif weightedAverage > 2.5:
                weightedAverage = "C"
            elif weightedAverage > 1.5:
                weightedAverage = "Start"
            else:
                weightedAverage = "Stub"

            newRow.append(weightedAverage)

            newRow.append(row[4])

            newRow.append(FAClassProbability)
            newRow.append(GAClassProbability)
            newRow.append(BClassProbability)
            newRow.append(CClassProbability)
            newRow.append(StartClassProbability)
            newRow.append(StubClassProbability)

            newRow.append(row[2])
            newRow.append(row[5])
            newRow.append(row[14])

            writer.writerow(newRow)

with open('Ideas_Repec_Dataset_Pilot3_Clean_Recommendations_Quality_Stats.csv', 'rb') as fr:
    reader = csv.reader(fr)

    crawlingClass = {}
    apiClass = {}
    weightedAPIClass = {}
    diffNumAPICrawler = 0
    diffNumAPIWeighted = 0
    diffNumCrawlerWeighted = 0
    importance = {}
    counter = 0
    header = next(reader)
    for row in reader:
        counter += 1

        if row[2] in crawlingClass:
            crawlingClass[row[2]] += 1
        else:
            crawlingClass[row[2]] = 1

        if row[3] in apiClass:
            apiClass[row[3]] += 1
        else:
            apiClass[row[3]] = 1

        if row[4] in weightedAPIClass:
            weightedAPIClass[row[4]] += 1
        else:
            weightedAPIClass[row[4]] = 1

        if row[2] != row[3] and row[2] != "No-Class":
            diffNumAPICrawler += 1

        if row[3] != row[4]:
            diffNumAPIWeighted += 1

        if row[2] != row[4] and row[2] != "No-Class":
            diffNumCrawlerWeighted += 1

        if row[5] in importance:
            importance[row[5]] += 1
        else:
            importance[row[5]] = 1

print ("diffNumAPICrawler: " + str(diffNumAPICrawler))
print ("diffNumAPIWeighted: " + str(diffNumAPIWeighted))
print ("diffNumCrawlerWeighted: " + str(diffNumCrawlerWeighted))
print ("crawlingClass: " + str(crawlingClass))
print ("apiClass: " + str(apiClass))
print ("weightedAPIClass: " + str(weightedAPIClass))
print ("importance: " + str(importance))

