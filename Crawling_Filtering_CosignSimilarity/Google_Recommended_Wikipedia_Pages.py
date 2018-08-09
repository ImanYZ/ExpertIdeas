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

# Import Website Scraping Library.
from WebsiteScapingLibrary import soupStructure


def num(stringObj):
    try:
        return int(stringObj)
    except ValueError:
        try:
            return float(stringObj)
        except ValueError:
            return int(stringObj.replace(',', ''))

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

# Extract search results from google.
def GoogleSearchAPIResults(searchTerm, numberOfPages):

    searchURL = "https://www.googleapis.com/customsearch/v1?key=EnterYourAPIKeyHere&q=" + searchTerm

    # Request a search query from Google and return the respone.
    try:
        response = requests.get(searchURL)
        response = response.text

        response = json.loads(response)
    except:
        print "An existing connection was forcibly closed by Google."
        response = {}

    while not 'items' in response:
        print "Search URL: " + searchURL
        print "Cannot find items in the search results. Please enter a new search URL:"
        searchURL = raw_input()
        searchURL = "https://www.googleapis.com/customsearch/v1?key=EnterYourAPIKeyHere&q=" + searchURL
        if searchURL == "1":
            return []
        try:
            response = requests.get(searchURL)
            response = response.text

            response = json.loads(response)
        except:
            print "That was a wrong URL."

    results = []

    for responseItem in response['items']:
        # Append the found data of the result to the array of results.
        results.append({'title':responseItem['title'], 'hyperlink':responseItem['link']})

    # return the results.
    return results

# Identify if the WIkipage is an appropriate one.
def IsWikipageAppropriate(title, hyperlink):

    if "Category:" in title or "User:" in title or "Talk:" in title or "User talk:" in title or "Book:" in title:
        return False, None

    wikipediaSoup = soupStructure(hyperlink)
    print "Wikipedia page Soup is Retrieved."

    trialNum = 0
    while wikipediaSoup == "" and trialNum < 10:
        trialNum += 1
        print "Wikipedia page:" + hyperlink + " Soup is not retreived. Please enter an appropriate URL:"
        # hyperlink = raw_input()
        # if hyperlink == "1":
        #     return False, None
        wikipediaSoup = soupStructure(hyperlink)

    if wikipediaSoup != "":
        pubResultRow = WikipediaPageStats (hyperlink, wikipediaSoup, title, 'list')

        trialNum = 0
        while pubResultRow == [] and trialNum < 10:
            trialNum += 1
            print "wikipageURL:", hyperlink, "is not found. Please enter a new one:"
            # hyperlink = raw_input()
            # if hyperlink == "1":
            #     return False, None
            wikipediaSoup = soupStructure(hyperlink)

            innerTrialNum = 0
            while wikipediaSoup == "" and innerTrialNum < 10:
                innerTrialNum += 1
                print "Wikipedia page:" + hyperlink + " Soup is not retreived. Please enter an appropriate URL:"
                # hyperlink = raw_input()
                # if hyperlink == "1":
                #     return False, None
                wikipediaSoup = soupStructure(hyperlink)

            pubResultRow = WikipediaPageStats (hyperlink, wikipediaSoup, title, 'list')

        if pubResultRow == []:
            return False, None
        print "Wikipedia page Stats:", pubResultRow

        # If the edit protection os the page is not None:
        if pubResultRow[2].lower() != "none":
            print "The Wikipedia page is edit protected. Do not recommend it."
            return False, None
        if pubResultRow[3].lower() == "stub-class":
            print "The Wikipedia page is a Stub. Do not recommend it."
            return False, None
        # if pubResultRow[3].lower() == "b-class":
        #   print "The Wikipedia page is a B-Class. Do not recommend it."
        #   return False, None
        # if pubResultRow[3].lower() == "b+ class":
        #   print "The Wikipedia page is a B+ class. Do not recommend it."
        #   return False, None
        # if pubResultRow[3].lower() == "ga-class":
        #   print "The Wikipedia page is a GA-Class. Do not recommend it."
        #   return False, None
        # if pubResultRow[3].lower() == "a-class":
        #   print "The Wikipedia page is a A-Class. Do not recommend it."
        #   return False, None
        # if pubResultRow[3].lower() == "fa-class":
        #   print "The Wikipedia page is a FA-Class. Do not recommend it."
        #   return False, None
        if num(pubResultRow[14]) < 1000:
            print "The Wikipedia page has been viewed less than 1000 times. Do not recommend it."
            return False, None

        print "The Wikipedia page is OK to recommend."
        return True, pubResultRow

viewedRecommendations = {}

print "Enter the name of the authors and publications dataset csv file without any sufix:"
datatsetFileName = raw_input()

if datatsetFileName == "":
    datatsetFileName = 'Ideas_Repec_Dataset_Pilot3_Clean'

with open(datatsetFileName + '.csv', 'rb') as fr:
    reader = csv.reader(fr)

    with open(datatsetFileName + '_Recommendations.csv', 'wb') as fw:
        writer = csv.writer(fw)

        pubResultRow = ['email', 'publication1', 'Wikipage1', 'WikipageURL1', 'publication2', 'Wikipage2', 'WikipageURL2', 'publication3', 'Wikipage3', 'WikipageURL3', 'publication4', 'Wikipage4', 'WikipageURL4', 'publication5', 'Wikipage5', 'WikipageURL5', 'publication6', 'Wikipage6', 'WikipageURL6', 'publication7', 'Wikipage7', 'WikipageURL7']
        writer.writerow(pubResultRow)

        with open(datatsetFileName + '_Recommendations_Stats.csv', 'wb') as fw:
            writer_Stats = csv.writer(fw)

            wikipageResultRow = ['ID', 'Title', 'Edit Protection Level', 'Class', 'Importance', 'Page Length', '# watchers', 'Time of Last Edit', '# redirects to this page', 'Page Creation Date', 'Total # edits', 'Total # distinct authors', 'Recent # edits (over the past month)', 'Recent # distinct authors', '# views (last 90 days)', 'Total # references', '# references published after 2010', '# External Hyperlinks']
            writer_Stats.writerow(wikipageResultRow)

            previousURLs = []

            header = next(reader)
            for row in reader:
                pubResultRow = []
                
                email = row[2]
                print email
                pubResultRow.append(email)

                for i in range(8, len(row) - 3, 4):
                    if row[i] != "":
                        publication = convert_unicode(row[i])
                        keyword = row[i + 3]
                        keyword = keyword.replace(" ", "+")
                        print "Paper:", publication
                        print "Keyword:", keyword
                        recommendations = []
                        publicationNotAppropriate = False
                        if keyword in viewedRecommendations:
                            recommendations = viewedRecommendations[keyword]
                        else:
                            while len(recommendations) == 0 and publicationNotAppropriate == False:
                                recommendations = GoogleSearchAPIResults("econ+" + keyword, 1)
                                print recommendations
                                if len(recommendations) == 0:
                                    print "The publication is not appropriate. I'm going to skip it."
                                    publicationNotAppropriate = True
                            viewedRecommendations[keyword] = recommendations

                        if not publicationNotAppropriate:
                            recommendationIndex = 0
                            recommendedTitle = recommendations[recommendationIndex]['title']
                            recommendedURL = recommendations[recommendationIndex]['hyperlink']

                            if not recommendedURL in previousURLs:

                                flag, wikipageResultRow = IsWikipageAppropriate(recommendedTitle, recommendedURL)
                                while flag == False and recommendationIndex < len(recommendations) - 1:
                                    print "The recommendation is not appropriate."
                                    recommendationIndex += 1
                                    recommendedTitle = recommendations[recommendationIndex]['title']
                                    recommendedURL = recommendations[recommendationIndex]['hyperlink']
                                    flag, wikipageResultRow = IsWikipageAppropriate(recommendedTitle, recommendedURL)

                                if flag:
                                    previousURLs.append(recommendedURL)
                                    writer_Stats.writerow(wikipageResultRow)
                                
                            pubResultRow.extend([publication, recommendedTitle, recommendedURL])
                writer.writerow(pubResultRow)