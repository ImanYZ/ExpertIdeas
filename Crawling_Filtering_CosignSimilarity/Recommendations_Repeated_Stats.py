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

print "Enter the name of the recommendations dataset csv file without any sufix:"
datatsetFileName = raw_input()

if datatsetFileName == "":
    datatsetFileName = 'Ideas_Repec_Dataset_Pilot3_Clean_Recommendations'

with open(datatsetFileName + '.csv', 'rb') as fr:
    reader = csv.reader(fr)

    with open('Recommendations_Repeated_Recommendations_Stats.csv', 'wb') as fw:
        writer = csv.writer(fw)

        pubResultRow = ['Wikipage', 'WikipageURL', '# of Repetition']
        writer.writerow(pubResultRow)

        wikipages = {}

        header = next(reader)
        for row in reader:
            
            for index in range(3, 22, 3):
                if row[index] in wikipages:
                    wikipages[row[index]]['repetition'] += 1
                else:
                    wikipages[row[index]] = {}
                    wikipages[row[index]]['Wikipage'] = row[index - 1]
                    wikipages[row[index]]['repetition'] = 1

        for key, value in wikipages.iteritems():
            pubResultRow = [value['Wikipage'], key, value['repetition']]
            writer.writerow(pubResultRow)
