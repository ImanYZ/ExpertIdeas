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
browserEconpapers = defineBrowser()
browserIdeas = defineBrowser()


# Define a funtion which extracts the abstract of a paper from http://econpapers.repec.org/.
def abstractExtractor(query):

    notRetrievedPage = True
    while notRetrievedPage:
        try:
            browserEconpapers.get('http://econpapers.repec.org/scripts/search.pf?ft=' + query)
            notRetrievedPage = False
        except:
            time.sleep(10)

    try:

        iframe = browserEconpapers.find_element_by_id('absframe')
        browserEconpapers.switch_to_default_content()
        browserEconpapers.switch_to_frame(iframe)

        # Find the Main tag.
        mainTag = browserEconpapers.find_element_by_css_selector(".abstractframe")

        abstractTag = ''

        try:
            # Find the tag containging abstract text.
            abstractTag = mainTag.find_element_by_xpath("//*[contains(text(), 'Abstract:')]")
            abstractTag = abstractTag.find_element_by_xpath('..')

            # Find the first abstract text.
            abstract = abstractTag.text

        except:
            print "There is no abstract available for this publication."
            abstract = ''

    except:
        print "There is no abstract available for this publication."
        abstract = ''

    return abstract


def IdeasAbstractExtractor(query):

    notRetrievedPage = True
    while notRetrievedPage:
        try:
            browserIdeas.get('https://ideas.repec.org/cgi-bin/htsearch?cmd=Search%21&ul=&q=' + query)
            notRetrievedPage = False
        except:
            time.sleep(10)

    try:
        paperLinkTag = browserIdeas.find_element_by_xpath('//*[@id="content-block"]/dl[1]/dt/a')
        paperLinkTag.click()
        abstractTag = browserIdeas.find_element_by_xpath('//*[@id="abstract-body"]/p')
        return abstractTag.text + " " + abstractExtractor(query)

    except Exception, e:
        print "There is no keyword for this publication on Ideas. The error message is: " + str(e) + " I'm going to search Econpapers.repec.org"
        return abstractExtractor(query)


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


# Define the webbrowser as Phantomjs and pretend it as Google Chrome.
browser = defineBrowser()

with open('Main_Study_Comments.csv', 'rb') as fr:
    reader = csv.reader(fr)

    with open('Main_Study_Comments_Abstracts.csv', 'wb') as fw:
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
                        "Clicked Tutorial", "# of Comments", "Abstract", "Cosine Similarity"]
        writer.writerow(pubResultRow)

        header = next(reader)
        for row in reader:
            firstname = row[0]
            lastname = row[1]
            publicationTitle = row[32]
            publicationTitle = publicationTitle.replace(":", " ")
            WikipediaURL = row[33]
            abstract = IdeasAbstractExtractor(urllib.quote_plus(('"' + publicationTitle + '" ' + firstname + " " +
                                                            lastname).encode('utf-8')))[10:]
            urlTitle = WikipediaURL.replace("https://en.wikipedia.org/wiki/", "")
            urlTitle = urlTitle.replace("http://en.wikipedia.org/wiki/", "")
            urlTitle = urlTitle.replace("https://en.wikipedia.org/?title=", "")
            urlTitle = urlTitle.replace("_", " ")
            urlTitle = urlTitle.replace("%E2%80%93", u"–")
            for result in GETRequestFromWikipedia( {'titles':urlTitle, 'prop':'revisions', 'rvprop':'content', 'ellimit':'max'} ):

                pageData = result['pages'].values()[0]

            cosine_similarity = cosine_sim(abstract, str(pageData))
            print ("\n\n\n\n publication Query: " + 'http://econpapers.repec.org/scripts/search.pf?ft=' + urllib.quote_plus(('"' + publicationTitle + '" ' + firstname + " " + lastname).encode('utf-8')))
            print ("Wikipedia Parsed Title: " + urlTitle.encode('utf-8'))
            print ("cosine_similarity: " + str(cosine_similarity))

            rowAndAbstract = row
            rowAndAbstract.append(abstract)
            rowAndAbstract.append(cosine_similarity)
            writer.writerow(rowAndAbstract)

