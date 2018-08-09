#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the required libraries.
import sys
import codecs
sys.stdout = codecs.getwriter("iso-8859-1")(sys.stdout, 'xmlcharrefreplace')

import os

from datetime import datetime, date, time
import re
import time
import random
from operator import itemgetter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

import ucsv as csv
import unicodedata

# Import BeautifulSoup library
from bs4 import SoupStrainer, BeautifulSoup

# Import the library needed to decode html characters.
import HTMLParser
hparser = HTMLParser.HTMLParser()

import urllib

import nltk, string
# nltk.download('punkt') # if necessary...
from sklearn.feature_extraction.text import TfidfVectorizer

# Import Website Scraping Library.
from WebsiteScapingLibrary import GETRequestFromWebsite, strip_tags, ifMoreThan10ErrorsDelay4Minutes, soupStructure
from WikipediaScrapingLibrary import GETRequestFromWikipedia


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


def click_and_wait(htmlObj):

    htmlObj.click()

    # Random float x, 1.0 <= x < 10.0
    # randomTimePeriod = random.uniform(1, 4)

    print "Wait time: " + str(1) + " seconds"

    time.sleep(1)


# Define the webbrowser as Phantomjs and pretend it as Google Chrome.
def defineBrowser():
    path_to_phantomjs = 'phantomjs'
    browser = webdriver.PhantomJS(service_args=['--load-images=no'])
    dcap = browser.desired_capabilities
    dcap["phantomjs.page.settings.userAgent"] = (
         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
         "(KHTML, like Gecko) Chrome/15.0.87")
    browser = webdriver.PhantomJS(executable_path = path_to_phantomjs, desired_capabilities = dcap, service_args=['--load-images=no'])
    # firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # firefox_profile.set_preference('permissions.default.image', 2)

    # browser = webdriver.Firefox(firefox_profile)

    return browser


RecommendationRepetition = {}
WikipagesStats = {}

with open('Main_Study_Comments.csv', 'rb') as fr:
    reader = csv.reader(fr)

    header = next(reader)
    for row in reader:
        row[34] = row[34].replace('http://', 'https://')
        row[34] = row[34].replace('https://en.wikipedia.org/?title=', 'https://en.wikipedia.org/wiki/')
        row[34] = row[34].replace('%28', '(')
        row[34] = row[34].replace('%29', ')')
        row[34] = row[34].replace('%27', "'")
        # row[34] = row[34].replace('%E2%80%93', "–")

        if row[34] in RecommendationRepetition:
            RecommendationRepetition[row[34]] += 1
        else:
            RecommendationRepetition[row[34]] = 1
            WikipagesStats[row[34]] = {}
            WikipagesStats[row[34]]["Stub"] = 0
            WikipagesStats[row[34]]["Start"] = 0
            WikipagesStats[row[34]]["C-Class"] = 0
            WikipagesStats[row[34]]["B-Class"] = 0
            WikipagesStats[row[34]]["GA-Class"] = 0
            WikipagesStats[row[34]]["FA-Class"] = 0

            WikipagesStats[row[34]]["Top-importance"] = 0
            WikipagesStats[row[34]]["High-importance"] = 0
            WikipagesStats[row[34]]["Mid-importancee"] = 0
            WikipagesStats[row[34]]["Low-importance"] = 0

            WikipagesStats[row[34]]["PageLength"] = row[38]
            WikipagesStats[row[34]]["Watchers"] = row[39]
            WikipagesStats[row[34]]["Redirects"] = row[42]
            WikipagesStats[row[34]]["TotalEdits"] = row[43]
            WikipagesStats[row[34]]["Views"] = row[46]

        if "Stub" in row[36]:
            WikipagesStats[row[34]]["Stub"] = 1
        elif "Start" in row[36]:
            WikipagesStats[row[34]]["Start"] = 1
        elif "C-Class" in row[36]:
            WikipagesStats[row[34]]["C-Class"] = 1
        elif "B-Class" in row[36]:
            WikipagesStats[row[34]]["B-Class"] = 1
        elif "GA-Class" in row[36]:
            WikipagesStats[row[34]]["GA-Class"] = 1
        elif "FA-Class" in row[36]:
            WikipagesStats[row[34]]["FA-Class"] = 1

        if "Top-importance" in row[37]:
            WikipagesStats[row[34]]["Top-importance"] = 1
        elif "High-importance" in row[37]:
            WikipagesStats[row[34]]["High-importance"] = 1
        elif "Mid-importancee" in row[37]:
            WikipagesStats[row[34]]["Mid-importancee"] = 1
        elif "Low-importance" in row[37]:
            WikipagesStats[row[34]]["Low-importance"] = 1

with open('UniqueRecommendations_Features.csv', 'wb') as fw:
    writer = csv.writer(fw)

    row = ["URL", "Stub", "Start", "C-Class", "B-Class", "GA-Class", "FA-Class",
           "Top-importance", "High-importance", "Mid-importance", "Low-importance",
           "Page Length", "Watchers", "Redirects", "Total Edits", "Views"]
    writer.writerow(row)

    for url, articleFeatures in WikipagesStats.iteritems():
        row = [url]
        row.append(articleFeatures["Stub"])
        row.append(articleFeatures["Start"])
        row.append(articleFeatures["C-Class"])
        row.append(articleFeatures["B-Class"])
        row.append(articleFeatures["GA-Class"])
        row.append(articleFeatures["FA-Class"])
        row.append(articleFeatures["Top-importance"])
        row.append(articleFeatures["High-importance"])
        row.append(articleFeatures["Mid-importancee"])
        row.append(articleFeatures["Low-importance"])
        row.append(articleFeatures["PageLength"])
        row.append(articleFeatures["Watchers"])
        row.append(articleFeatures["Redirects"])
        row.append(articleFeatures["TotalEdits"])
        row.append(articleFeatures["Views"])

        writer.writerow(row)


names = []
rankings = []

with open('Repec_Author_Rankings.csv', 'rb') as fr:
    reader = csv.reader(fr)

    header = next(reader)
    for row in reader:
        names.append(strip_tags(unicode(row[2].encode('ascii', 'ignore'), 'utf8')))
        rankings.append(row[1])



with open('Main_Study_Comments_Abstracts_Authors_Rankings_1.csv', 'rb') as fr:
    reader = csv.reader(fr)

    with open('Main_Study_Comments.csv', 'rb') as frMain:
        readerMain = csv.reader(frMain)

        with open('Main_Study_Comments_Abstracts_Authors_Rankings.csv', 'wb') as fw:
            writer = csv.writer(fw)

            header = next(readerMain)
            newHeader = header
            newHeader.append("Recommendation Repetition")
            newHeader.append("Abstract")
            newHeader.append("Cosine Similarity")
            newHeader.append("Author Abstract Views")
            newHeader.append("From US")
            newHeader.append("From English Language Country")
            newHeader.append("Top 10%")
            writer.writerow(newHeader)

            oldFirstname = ""
            oldLastname = ""
            participantRow = []
            commentedRecommendations = []

            for rowMain in readerMain:
                firstnameMain = rowMain[1]
                lastnameMain = rowMain[2]
                location = rowMain[5]
                US = 0
                English = 0
                if "USA" in location or "United States" in location:
                    US = 1
                if ("USA" in location or "United States" in location or "Australia" in location or "New Zealand" in location or
                    "United Kingdom" in location or "UK" in location or "Antigua and Barbuda" in location or
                    "Bahamas" in location or "Barbados" in location or "Belize" in location or "Botswana" in location or
                    "Cameroon" in location or "Canada" in location or "Cook Islands" in location or "Dominica" in location or
                    "Micronesia" in location or "Fiji" in location or "Gambia" in location or "Ghana" in location or
                    "Grenada" in location or "Guyana" in location or "India" in location or "Ireland" in location or
                    "Jamaica" in location or "Kenya" in location or "Lesotho" in location or "Liberia" in location or
                    "Malawi" in location or "Malta" in location or "Marshall Islands" in location or "Namibia" in location or
                    "Nauru" in location or "Nigeria" in location or "Niue" in location or "Pakistan" in location or
                    "Papua New Guinea" in location or "Philippines" in location or "Rwanda" in location or
                    "Saint Kitts and Nevis" in location or "Saint Lucia" in location or "Samoa" in location or
                    "Seychelles" in location or "Sierra Leone" in location or "Singapore" in location or
                    "Solomon Islands" in location or "South Africa" in location or "South Sudan" in location or
                    "Sudan" in location or "Swaziland" in location or "Tanzania" in location or "Tonga" in location or
                    "Tuvalu" in location or "Uganda" in location or "Vanuatu" in location or "Zambia" in location or
                    "Zimbabwe" in location or "Bangladesh" in location or "Brunei" in location or "Eritrea" in location or
                    "Ethiopia" in location or "Israel" in location or "Malaysia" in location or "Sri Lanka" in location or
                    "Akrotiri and Dhekelia" in location or "American Samoa" in location or "Anguilla" in location or
                    "Bermuda" in location or "British Virgin Islands" in location or "Cayman Islands" in location or
                    "Falkland Islands" in location or "Gibraltar" in location or "Guam" in location or
                    "Hong Kong" in location or "Isle of Man" in location or "Jersey" in location or
                    "Norfolk Island" in location or "Northern Mariana Islands" in location or "Pitcairn Islands" in location or
                    "Puerto Rico" in location or "Sint Maarten" in location or "Turks and Caicos Islands" in location or
                    "British Indian Ocean Territory" in location or "Guernsey" in location or "Montserrat" in location or
                    "Saint Helena, Ascension and Tristan da Cunha" in location or "Christmas Island" in location or
                    "Cocos (Keeling) Islands" in location or "Tokelau" in location):
                        English = 1

                # if firstnameMain != oldFirstname or lastnameMain != oldLastname:
                #     nonCommentedRecommendations = []
                #     for rowAndRanking in participantRow:
                #         if rowAndRanking[53] != 0:
                #             writer.writerow(rowAndRanking)
                #         elif (not rowAndRanking[34] in commentedRecommendations and
                #               not rowAndRanking[34] in nonCommentedRecommendations):
                #             nonCommentedRecommendations.append(rowAndRanking[34])
                #             writer.writerow(rowAndRanking)

                #     oldFirstname = firstnameMain
                #     oldLastname = lastnameMain
                #     participantRow = []
                #     commentedRecommendations = []

                for row in reader:
                    firstname = row[0]
                    lastname = row[1]

                    abstractViews = 0
                    if (firstname == firstnameMain and lastname == lastnameMain):
                        abstract = row[-3]
                        cosineSimilarity = row[-2]
                        abstractViews = row[-1]
                        break

                topten = 0
                for nameCounter, name in enumerate(names):
                    if firstnameMain in name and lastnameMain in name:
                        topten = 1

                rowMain[34] = rowMain[34].replace('http://', 'https://')
                rowMain[34] = rowMain[34].replace('https://en.wikipedia.org/?title=', 'https://en.wikipedia.org/wiki/')
                rowMain[34] = rowMain[34].replace('%28', '(')
                rowMain[34] = rowMain[34].replace('%29', ')')
                rowMain[34] = rowMain[34].replace('%27', "'")
                # rowMain[34] = rowMain[34].replace('%E2%80%93', "–")

                rowAndRanking = rowMain
                print("Recommendation: " + rowMain[34])
                print("authorLastName: " + lastname)
                print("authorFirstName: " + firstname)
                print("authorAbstractViews: " + str(abstractViews))
                print("topten: " + str(topten))
                if rowMain[34] in RecommendationRepetition:
                    rowAndRanking.append(RecommendationRepetition[rowMain[34]])
                    print("Recommendation Repetition: " + str(RecommendationRepetition[rowMain[34]]))
                else:
                    rowAndRanking.append(1)
                    raw_input()
                rowAndRanking.append(abstract)
                rowAndRanking.append(cosineSimilarity)
                rowAndRanking.append(abstractViews)
                rowAndRanking.append(US)
                rowAndRanking.append(English)
                rowAndRanking.append(topten)

                writer.writerow(rowAndRanking)

            #     participantRow.append(rowAndRanking)

            #     if rowAndRanking[53] != 0:
            #         commentedRecommendations.append(rowAndRanking[34])

            # nonCommentedRecommendations = []
            # for rowAndRanking in participantRow:
            #     if rowAndRanking[53] != 0:
            #         writer.writerow(rowAndRanking)
            #     elif (not rowAndRanking[34] in commentedRecommendations and
            #           not rowAndRanking[34] in nonCommentedRecommendations):
            #         nonCommentedRecommendations.append(rowAndRanking[34])
            #         writer.writerow(rowAndRanking)
