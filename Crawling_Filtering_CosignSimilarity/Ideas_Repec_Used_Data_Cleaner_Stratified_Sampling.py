import math
import random

import unicodedata
import ucsv as csv

firstNamesList = []
lastNamesList = []
emailsList = []
specializationsDict = {}

usedFirstNamesList = []
usedLastNamesList = []
usedEmailsList = []


mainDatasetNamesList = ['Ideas_Repec_Dataset_Pilot2_Standard', 'Ideas_Repec_Dataset_Standard', 'Ideas_Repec_Dataset1_Standard', 
    'Ideas_Repec_Dataset3_Standard', 'Ideas_Repec_Dataset4_Standard', 'Ideas_Repec_Dataset10_Standard']

usedDatasetNamesList = ['Ideas_Repec_Dataset_Pilot1_Used', 'Ideas_Repec_Dataset_Pilot2_Clean' ]

outputDatasetName = 'Ideas_Repec_Dataset_Pilot3_Clean'

for usedDatasetName in usedDatasetNamesList:
    with open(usedDatasetName + '.csv', 'rb') as frUsed:
        readerUsed = csv.reader(frUsed)

        headerUsed = next(readerUsed)
        for row in readerUsed:
            email = row[2]

            if not email in usedEmailsList:
                usedFirstNamesList.append(row[0])
                usedLastNamesList.append(row[1])
                usedEmailsList.append(email)
                print email, "entered."

with open(outputDatasetName + '.csv', 'wb') as fw:
    writer = csv.writer(fw)

    resultRow = ['firstName', 'lastName', 'email', 'specialization', 'EconPapers Profile', 'affiliation', 'location', 'timezone',
        'homepage', 'publication1', 'publicationYear1', 'citation1', 'firstKeyword1', 'publication2', 'publicationYear2', 'citation2',
        'firstKeyword2', 'publication3', 'publicationYear3', 'citation3', 'firstKeyword3', 'publication4', 'publicationYear4', 'citation4',
        'firstKeyword4', 'publication5', 'publicationYear5', 'citation5', 'firstKeyword5', 'publication6', 'publicationYear6', 'citation6',
        'firstKeyword6', 'publication7', 'publicationYear7', 'citation7', 'firstKeyword7']
    writer.writerow(resultRow)

    for mainDatasetName in mainDatasetNamesList:
        print mainDatasetName, "started."
        with open(mainDatasetName + '.csv', 'rb') as fr:
            reader = csv.reader(fr)

            header = next(reader)
            for row in reader:
                firstName = row[0]
                lastName = row[1]
                email = row[2]
                specialization = row[3]

                numberOfPubs = 0

                for i in range(8, len(row) - 3, 4):
                    if row[i] != "":
                        numberOfPubs += 1

                if (firstName != None and firstName != "" and lastName != None and lastName != "" and email != None and email != ""
                    and not email in usedEmailsList and specialization != "" and specialization.lower() != "german papers" and numberOfPubs >= 6):
                    foundIndex = -1

                    for index in range(len(firstNamesList)):
                        if firstNamesList[index] == firstName and lastNamesList[index] == lastName and emailsList[index] == email:
                            foundIndex = index
                            break

                    if foundIndex == -1:
                        if not specialization in specializationsDict:
                            firstNamesList.append(firstName)
                            lastNamesList.append(lastName)
                            emailsList.append(email)
                            specializationsDict[specialization] = [row]
                        else:
                            firstNamesList.append(firstName)
                            lastNamesList.append(lastName)
                            emailsList.append(email)
                            specializationsDict[specialization].append(row)

    for key, authorList in specializationsDict.iteritems():
        requiredNum = int(math.ceil(1.0 * len(authorList)))

        sampleIndices = random.sample(range(len(authorList)), requiredNum)

        for index in sampleIndices:
            writer.writerow(authorList[index])


