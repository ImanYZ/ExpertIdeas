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


# Define the webbrowser as Phantomjs and pretend it as Google Chrome.
browser = defineBrowser()

authorsRankings = []

for letterCounter in range(26):
    notRetrievedPage = True
    while notRetrievedPage:
        try:
            # logecSoup = soupStructure('http://logec.repec.org/RAS/')
            browser.get('http://logec.repec.org/RAS/')
            notRetrievedPage = False
        except:
            time.sleep(10)

    # alphabeticalListTag = logecSoup.body.find('html').find('body').find('table').find('tbody')
        # .find('tr').find_all('td')[1].find('div').find_all('p')[5]
    alphabeticalListTag = browser.find_element_by_xpath('/html/body/table/tbody/tr/td[2]/div/p[6]')
    # alphabeticalListATags = alphabeticalListTag.find_all('a')
    alphabeticalListATags = alphabeticalListTag.find_elements_by_tag_name('a')
    # soupStructure(alphabeticalListATags[letterCounter].get('href'))
    alphabeticalListATags[letterCounter].click()
    # tableBodyTag = (logecSoup.body.find('html').find('body').find('table').find('tbody')
        # .find('tr').find_all('td')[0].find('table').find('tbody'))
    tableBodyTag = browser.find_element_by_xpath('/html/body/table/tbody/tr/td[1]/table/tbody')
    # authorTRTags = tableBodyTag.find_all('tr')
    authorTRTags = tableBodyTag.find_elements_by_tag_name('tr')
    for authorTRTag in authorTRTags[2:]:
        # authorATag = authorTRTag.find('a')
        authorATag = authorTRTag.find_element_by_tag_name('a')
        # authorName = authorATag.renderContents()
        authorName = authorATag.text
        reCompiler = re.compile('([^,]+), ([^,]+)')
        authorNameCompiled = reCompiler.match(authorName)
        if authorNameCompiled is not None:
            authorLastName = authorNameCompiled.group(1)
            # authorLastName = strip_tags(unicode(authorLastName, 'utf8'))
            authorLastName = unicodedata.normalize('NFKD', authorLastName).encode("ascii","ignore")
            authorFirstName = authorNameCompiled.group(2)
            # authorFirstName = strip_tags(unicode(authorFirstName, 'utf8'))
            authorFirstName = unicodedata.normalize('NFKD', authorFirstName).encode("ascii","ignore")
            # authorLastTDTag = authorTRTag.find_all('td')[-1]
            authorLastTDTag = authorTRTag.find_elements_by_tag_name('td')[-2]
            # authorAbstractViews = authorLastTDTag.renderContents()
            authorAbstractViews = authorLastTDTag.text
            authorDict = {}
            authorDict['firstname'] = authorFirstName
            authorDict['lastname'] = authorLastName
            authorDict['abstractViews'] = authorAbstractViews
            print("\nauthorFirstName: " + authorFirstName)
            print("authorLastName: " + authorLastName)
            print("authorAbstractViews: " + authorAbstractViews)
            authorsRankings.append(authorDict)
    print("letterCounter: " + str(letterCounter))




with open('Main_Study_Comments_Abstracts.csv', 'rb') as fr:
    reader = csv.reader(fr)

    with open('Main_Study_Comments_Abstracts_Authors_Rankings.csv', 'wb') as fw:
        writer = csv.writer(fw)

        pubResultRow = ["Firstname", "Lastname", "Specialization", "Affiliation", "location", "Phase 1", "Phase 2", "Phase 3",
                        "High View", "Citation Benefit", "Private Comes First", "Acknowledgement", "Likely to Cite",
                        "May Include Reference", "Might Refer to", "Likely to Cite + Acknowledgement",
                        "May Include Reference + Acknowledgement", "Might Refer to + Acknowledgement", "Especially popular",
                        "Highly visible", "Highly popular", "Manual Recommendation", "Track changed", "Inappropriate Comment",
                        "Interested", "Withdrawal", "Email 1 Opened", "Email 2 Opened", "Email 3 Opened",
                        "Econ Wikiproject Clicked", "Email Communication", "User Agent",
                        "Publication", "Wikipage URL", "Edit Protection Level", "Quality Class", "Importance Class",
                        "Page Length", "Watchers", "Last Edit Time", "Creation Time", "Redirects", "Total Edits",
                        "Distinct Authors", "Last Month Total Edits", "# of Views over the past month",
                        "External Hyperlinks", "Rating", "# of Experts Referred to", "Submitted to the Talk page",
                        "Comment Length", "Link to the Post on the Talk page", "Clicked Article", "Clicked Post",
                        "Clicked Tutorial", "# of Comments", "Abstract", "Cosine Similarity", "Author Abstract Views"]
        writer.writerow(pubResultRow)

        header = next(reader)
        for row in reader:
            firstname = row[0]
            lastname = row[1]

            abstractViews = -1
            for authorRanking in authorsRankings:
                if (firstname in authorRanking['firstname'] and lastname in authorRanking['lastname']):
                    abstractViews = int(authorRanking['abstractViews'].replace(',', ''))
                    break

            rowAndRanking = row
            rowAndRanking.append(abstractViews)
            print("authorLastName: " + lastname)
            print("authorFirstName: " + firstname)
            print("authorAbstractViews: " + str(abstractViews))
            writer.writerow(rowAndRanking)

