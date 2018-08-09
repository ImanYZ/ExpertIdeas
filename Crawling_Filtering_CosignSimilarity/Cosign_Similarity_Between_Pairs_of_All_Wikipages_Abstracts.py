#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the required libraries.
import sys
import os

from datetime import datetime, date, time
import re
import time
import random
from operator import itemgetter
import requests
import csv

import unicodedata


import urllib

import nltk, string
# nltk.download('punkt') # if necessary...
from sklearn.feature_extraction.text import TfidfVectorizer



# Check if the string is in ASCII or not.
def is_ascii(s):
    ASCIICharNum = 0
    for c in s:
        if ord(c) < 191:
            ASCIICharNum += 1
    if len(s) != 0 and ASCIICharNum / len(s) >= 0.99:
        return True
    else:
        return False


# Check if the string is in ASCII or not.
def convert_unicode(s):
    if isinstance(s, unicode):
        return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
    else:
        return s


stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


# Send request to Wikipedia by the use of Wikipedia API , and return the response as a Dictionary.
def GETRequestFromWikipedia(request):
    # Add required parameters to the request.
    request['action'] = 'query'
    request['format'] = 'json'

    # Define a dictionary to add the continue parameters to the request.
    lastContinue = {'continue': ''}

    result = {}

    # While there is more pages of response, continue sending the request.
    while True:

        if not 'error' in result:
            # Clone original request
            req = request.copy()

            # Modify it with the values returned in the 'continue' section of the last result.
            req.update(lastContinue)

            # Define a flag showing if the response has not received yet.
            responseNotReceived = True

            # Number of times there is no appropriate response from Wikipedia.
            errorCount = 0

        # While the response has not reeived correctly, send the request again.
        while responseNotReceived:

            try:

                print ("http://en.wikipedia.org/w/api.php?" + str(req))

                # Call API
                response = requests.get("http://en.wikipedia.org/w/api.php?", params=req, timeout=70)

                # Change the response encoding to utf-8.
                # response.encoding = 'utf-8'

                # Convert to JSON.
                result = response.json()

                # If the response is received, stop sending requests.
                responseNotReceived = False

            # If an error raised, send the request again.
            except Exception as e:
                print (e)

                # Increment errorCount
                errorCount += 1

                # If errorCount is less than 10:
                if errorCount < 10:

                    continue

                # Otherwise:
                else:

                    # Asign [ ] to result['query']:
                    result = {'query': []}

                    # Return an empthy list.
                    break

        # If there is an error in the response, raise the error.
        if 'error' in result:

            print ("The Error Message from Wikipedia is:", result['error'])
            time.sleep(10)
        # result = {'query':[ ]}

        else:
            # If there is a warning in the response, raise the warning.
            if 'warnings' in result: print(result['warnings'])

            # If there is a query tag in the response, return the content of the query tag and continue.
            if 'query' in result: yield result['query']

            # If there is no continue tag in the result, stop sending more requests.
            if 'continue' not in result:
                print ("There is no more data to continue request it from Wikimedia.")
                yield result['query']
                return

            # Append the continue parameters to the next request.
            lastContinue = result['continue']

            print ("I am going to continue requesting the rest of the data from Wikimedia.")


with open('Main_Study_Comments_Abstracts_Authors_Rankings_OverallRatings.csv', 'r', encoding='ISO-8859-1') as fr:
    reader = csv.reader(fr)

    with open('Cosign_Similarity_Between_Pairs_of_All_Wikipages_Abstracts.csv', 'w', encoding='ISO-8859-1') as fw:
        writer = csv.writer(fw)

        pubResultRow = ["Publication", "Wikipage URL", "Cosine Similarity"]
        writer.writerow(pubResultRow)

        wikipages = {}
        publications = {}

        header = next(reader)
        for row in reader:
            # firstname = row[1]
            # lastname = row[2]
            publicationTitle = row[33]
            # publicationTitle = publicationTitle.replace(":", " ")
            WikipediaURL = row[34]
            # abstract = IdeasAbstractExtractor(urllib.quote_plus(('"' + publicationTitle + '" ' + firstname + " " +
            #                                                 lastname).encode('utf-8')))[10:]
            abstract = row[61]
            if publicationTitle not in publications or publications[publicationTitle] == "":
                publications[publicationTitle] = abstract
            urlTitle = WikipediaURL.replace("https://en.wikipedia.org/wiki/", "")
            urlTitle = urlTitle.replace("http://en.wikipedia.org/wiki/", "")
            urlTitle = urlTitle.replace("https://en.wikipedia.org/?title=", "")
            urlTitle = urlTitle.replace("_", " ")
            urlTitle = urlTitle.replace("%E2%80%93", u"–")
            if WikipediaURL in wikipages:
                pageData = wikipages[WikipediaURL]
            else:
                for result in GETRequestFromWikipedia( {'titles':urlTitle, 'prop':'revisions', 'rvprop':'content'} ):
                    pageData = list(result['pages'].values())[0]
                    wikipages[WikipediaURL] = pageData

        print ("\n\n\nI'm done with retrieving all the data. I'm going to calculate the cosign similarities. \n\n\n")
        for WikipediaURL, pageData in wikipages.items():
            for publicationTitle, abstract in publications.items():
                cosine_similarity = cosine_sim(abstract, str(pageData))
                print ("publication:", publicationTitle)
                print ("cosine_similarity:", str(cosine_similarity))

                writer.writerow([publicationTitle, WikipediaURL, cosine_similarity])

