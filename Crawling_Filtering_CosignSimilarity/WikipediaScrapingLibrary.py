# -*- coding: utf-8 -*-

# Import Regular Expressions' libraries
import re
import csv
import datetime, time
import unicodedata

# Import BeautifulSoup library
from bs4 import SoupStrainer, BeautifulSoup

# Import Regular Expressions' libraries
from DatabaseLibraries import submitAndPrint

# Import Website Scraping Library.
from WebsiteScapingLibrary import scrapeWebsite, strip_tags, soupStructure

# Import requests library.
import requests

# Import urllib to manipulate URLs
import urlparse, urllib
from urllib import FancyURLopener
import urllib2

# Import urlparse libraries
from urlparse import urljoin

def num(stringObj):
    try:
        return int(stringObj)
    except ValueError:
        try:
            return float(stringObj)
        except ValueError:
            return int(stringObj.replace(',', ''))

# Check if the string is in ASCII or not.
def convert_unicode(s):
    if isinstance(s, unicode):
        return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
    else:
        return s

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
                response = requests.get("http://en.wikipedia.org/w/api.php?", params=req)
                print ("Response received from MediaWiki API.")

                # Change the response encoding to utf-8.
                # response.encoding = 'utf-8'

                # Convert to JSON.
                result = response.json()

                # If the response is received, stop sending requests.
                responseNotReceived = False

            # If an error raised, send the request again.
            except Exception as e:

                # Increment errorCount
                errorCount += 1

                # If errorCount is less than 10:
                if errorCount < 10:

                    continue

                # Otherwise:
                else:

                    # Asign [ ] to result['query']:
                    result = {'query':[ ]}

                    # Return an empthy list.
                    break

        # If there is an error in the response, raise the error.
        if 'error' in result:

            print "The Error Message from Wikipedia is:", result['error']
            time.sleep(10)
            # result = {'query':[ ]}

        else:
            # If there is a warning in the response, raise the warning.
            if 'warnings' in result: print(result['warnings'])

            # If there is a query tag in the response, return the content of the query tag and continue.
            if 'query' in result: yield result['query']

            # If there is no continue tag in the result, stop sending more requests.
            if 'continue' not in result:
                print "There is no more data to continue request it from Wikimedia."
                return

            # Append the continue parameters to the next request.
            lastContinue = result['continue']
            
            print "I am going to continue requesting the rest of the data from Wikimedia."

# Find the status of the Wikipedia article.
def classFinder(url, articleEncodedTitle, desiredCategory):

    qualityClass = "No-Class"
    importanceClass = "No-Class"
    desiredCategoryFound = False

    print ("Finding class for url: " + url)
    if "Category:" in url or "User:" in url or "Talk:" in url or "User_talk:" in url or "Book:" in url:
        return "No-Class", "No-Class", False

    # Find the talk pahe hyperlink.
    talkPageHyperlink = 'http://en.wikipedia.org/wiki/Talk:' + articleEncodedTitle

    # Convert the hyperlink to absolute if it is relative.
    # talkPageHyperlink = urljoin(url, talkPageHyperlink)

    # Retrieve url content, and convert it into the beautifulsoup structure.
    talkSoup = soupStructure(talkPageHyperlink)
    # talkSoup = scrapeWebsite(talkPageHyperlink, 'div', 'id', "catlinks", "b", "text", "Wikipedia does not have a")

    errorCounter = 0
    while (talkSoup == '' or (talkSoup.find('div', id="catlinks") == None and talkSoup.find('b', text="Wikipedia does not have a") == None)) and errorCounter <= 10:
            
            # print "talkPageHyperlink:", talkPageHyperlink, "is not found. Please enter a new one:"
            # talkPageHyperlink = raw_input()

            talkSoup = soupStructure(talkPageHyperlink)

            errorCounter += 1

    while True:
        try:
            r = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles=' + articleEncodedTitle)
            r = r.json()
            query = r['query']
            pages = query['pages']
            break
        except Exception, e:
            print ("\n\n\nI cannot retrieve the revision ID of this article! Error Message: " + str(e))
            time.sleep(1)
    try:
        revisions = pages.values()[0]['revisions']
        revisionID = revisions[0]['revid']
    except:
        return "No-Class", "No-Class", False
    qualityDict = None
    while True:
        try:
            r = requests.get('https://ores.wmflabs.org/scores/enwiki/wp10/' + str(revisionID))
            print("ores.wmflabs.org responded: " + str(r))
            r = r.json()
            qualityDict = r[str(revisionID)]
            innerIndex = 0
            while 'prediction' not in qualityDict and innerIndex < 4:
                qualityDict = qualityDict['score']
                innerIndex = innerIndex + 1
                print ("Found score in qualityDict for the " + str(innerIndex) + " time.")
            qualityClass = qualityDict['prediction']
            break
        except Exception, e:
            print ("\n\n\nI cannot retrieve the class of this article from the API! Error Message: " + str(e))
            time.sleep(1)

    probabilitiesOfEachClass = qualityDict['probability']
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

    if weightedAverage > 5:
        qualityClass = "FA-Class"
    elif weightedAverage > 4:
        qualityClass = "GA-Class"
    elif weightedAverage > 3:
        qualityClass = "B-Class"
    elif weightedAverage > 2:
        qualityClass = "C-Class"
    elif weightedAverage > 1:
        qualityClass = "Start-Class"
    else:
        qualityClass = "Stub-Class"

    print ("qualityClass: " + qualityClass)

    if talkSoup != '' and talkSoup.find('div', id="catlinks") != None and talkSoup.find('b', text="Wikipedia does not have a") == None:
        categoryDIVTag = talkSoup.find('div', id="catlinks")

        # # If the article is "FA-Class":
        # if categoryDIVTag.find(text=re.compile('.*FA-Class.*')) != None:
        #     qualityClass = "FA-Class"

        # # Otherwise if the article is "A-Class":
        # elif categoryDIVTag.find(text=re.compile('.* A-Class.*')) != None:
        #     qualityClass = "A-Class"

        # # Otherwise if the article is "GA-Class":
        # elif categoryDIVTag.find(text=re.compile('.*GA-Class.*')) != None:
        #     qualityClass = "GA-Class"

        # # Otherwise if the article is "B+ class":
        # elif categoryDIVTag.find(text=re.compile('.*B+ class.*')) != None:
        #     qualityClass = "B+ class"

        # # Otherwise if the article is "B-Class":
        # elif categoryDIVTag.find(text=re.compile('.*B-Class.*')) != None:
        #     qualityClass = "B-Class"

        # # Otherwise if the article is "C-Class":
        # elif categoryDIVTag.find(text=re.compile('.*C-Class.*')) != None:
        #     qualityClass = "C-Class"

        # # Otherwise if the article is "Stub-Class":
        # elif categoryDIVTag.find(text=re.compile('.*Stub-Class.*')) != None:
        #     qualityClass = "Stub-Class"

        # If the article is "Top-importance":
        if categoryDIVTag.find(text=re.compile('.*Top-importance.*')) != None:
            importanceClass = "Top-importance"

        # Otherwise if the article is "High-importance":
        elif categoryDIVTag.find(text=re.compile('.*High-importance.*')) != None:
            importanceClass = "High-importance"

        # Otherwise if the article is "Mid-importance":
        elif categoryDIVTag.find(text=re.compile('.*Mid-importance.*')) != None:
            importanceClass = "Mid-importancee"

        # Otherwise if the article is "Low-importance":
        elif categoryDIVTag.find(text=re.compile('.*Low-importance.*')) != None:
            importanceClass = "Low-importance"

        # Otherwise if the article is "NA-importance":
        elif categoryDIVTag.find(text=re.compile('.*NA-importance.*')) != None:
            importanceClass = "NA-importance"

        # Otherwise if the article is "Unknown-importance":
        elif categoryDIVTag.find(text=re.compile('.*Unknown-importance.*')) != None:
            importanceClass = "Unknown-importance"

        # Otherwise if the article is "Bottom-importance":
        elif categoryDIVTag.find(text=re.compile('.*Bottom-importance.*')) != None:
            importanceClass = "Bottom-importance"

        # If the article is included in the desired Category:
        if desiredCategory.lower() in categoryDIVTag.prettify().lower():
            desiredCategoryFound = True

    # Return the results.
    return qualityClass, importanceClass, desiredCategoryFound

# Define a function which extracts statistics about a Wikipedia article and prints it out.
def WikipediaPageStats (articleHyperlink, articleSoup, articleTitle, desiredCategory):

    print "Wikipedia article title before correction:", convert_unicode(articleTitle)

    # Find the appropriate title of the Wikipedia page from articleTitle.
    appropriateArticleTitle = re.search("(.+) -", articleTitle)

    # IF appropriateArticleTitle is found:
    if appropriateArticleTitle != None:

        # Assign the value of appropriateArticleTitle to articleTitle.
        articleTitle = appropriateArticleTitle.group(1)

    print "Wikipedia article title after correction:", convert_unicode(articleTitle)

    # Find the encoded title of the article.
    articleEncodedTitles = re.findall("(?:wiki/([^?]+))|(?:title=([^&]+))", articleHyperlink)

    print "Wikipedia articles' Encoded Titles:", articleEncodedTitles

    # Find the encoded title of the article from the list of findings.
    if articleEncodedTitles[0][0] != '':

        articleEncodedTitle = articleEncodedTitles[0][0]

    elif articleEncodedTitles[0][1] != '':

        articleEncodedTitle = articleEncodedTitles[0][1]

    elif articleEncodedTitles[1][0] != '':

        articleEncodedTitle = articleEncodedTitles[1][0]

    elif articleEncodedTitles[1][1] != '':

        articleEncodedTitle = articleEncodedTitles[1][1]

    print "Encoded title of the article: " + articleEncodedTitle

    # If there is any %2F in the encoded title, convert it into /.
    # if '%E2%80%93' in articleEncodedTitle:
    #   strObjs = articleEncodedTitle.split('%E2%80%93')
    #   articleEncodedTitle = strObj[0]
    #   for index in range(len(strObjs)):
    #       articleEncodedTitle += u'–' + strObjs[index]
    # articleEncodedTitle = articleEncodedTitle.replace('%2F', '/')
    # articleEncodedTitle = articleEncodedTitle.replace('%3F', '?')
    # articleEncodedTitle = articleEncodedTitle.replace('%27', "&")
    # articleEncodedTitle = articleEncodedTitle.replace('%27', "'")
    # articleEncodedTitle = articleEncodedTitle.replace('%28', '(')
    # articleEncodedTitle = articleEncodedTitle.replace('%29', ')')
    articleEncodedTitle = articleEncodedTitle.replace('%E2%80%93', u'–')
    articleEncodedTitle = urllib.unquote(articleEncodedTitle)

    # Define a counter to count the number of continued parts of the response.
    responseCounter = 0

    # The number of external hyperlinks in this page.
    numberOfExternalLinks = 0

    # For each response to be continued:
    #for result in GETRequestFromWikipedia( {'titles':articleTitle, 'prop':'info|contributors|revisions', 'inprop':'protection|watchers', 'pclimit':'max', 'rvprop':'timestamp', 'rvlimit':'max'} ):
    for result in GETRequestFromWikipedia( {'titles':articleEncodedTitle, 'prop':'info|extlinks', 'inprop':'protection|watchers', 'ellimit':'max'} ):

        # If there is an appropriate result:
        # if result != [ ]:

            # Extract page data from the JSON response.
            pageData = result['pages'].values()[0]

            # Find the quality and importance classes of the Wikipedia page and if the page is included in the desired category.
            qualityClass, importanceClass, desiredCategoryFound = classFinder(articleHyperlink, articleEncodedTitle, desiredCategory)

            # If there is pageID which means this page actually exists on Wikipedia and the namespace is 0 which means that the page is the main article:
            if 'pageid' in pageData and pageData['ns'] == 0:
                # if 'pageid' in pageData and pageData['ns'] == 0 and desiredCategoryFound == True:

                # If this is the first part of the response:
                if responseCounter == 0:

                    # Extract page info data from the JSON response.
                    # pageInfoData = result['pages'].values()[0]

                    # Print out the page id.
                    print "\n\nID: " + str(pageData['pageid']), '\n'
                    
                    statsContext = {}
                    statsContext['pageid'] = pageData['pageid']
                    statsContext['title'] = articleTitle

                    # Initialize editProtectionLevel.
                    editProtectionLevel = 'None'

                    # OIterate on all types of protections:
                    for protection in pageData['protection']:

                        # It the edit protection found:
                        if protection['type'] == 'edit':

                            # If the edit protection level found, get out of the for loop.
                            editProtectionLevel = protection['level']
                            break

                    # Print out the edit protection level.
                    statsContext['editProtectionLevel'] = editProtectionLevel

                    # If the length of the article is less than 1500 characters, consider the page as a stub.
                    if num(pageData['length']) < 1500:
                        print "The length of the article is less than 1500 characters, consider the page as a stub. Do not recommend it."
                        qualityClass = "Stub-Class"

                    # Print out the quality class of the article.
                    statsContext['qualityClass'] = qualityClass

                    # Print out the Importance class of the article.
                    statsContext['importanceClass'] = importanceClass

                    # Print out the length of the article.
                    statsContext['length'] = pageData['length']

                    watchersNumber = '0'
                    # If watchers exists in the pageData dictionary:
                    if 'watchers' in pageData:
                        watchersNumber = str(pageData['watchers'])

                    # Print out the number of watchers.
                    statsContext['watchersNumber'] = watchersNumber

                    # Print out the timestamp showing whenever the page changes in a way requiring it to be re-rendered, invalidating caches. Aside from editing this includes permission changes, creation or deletion of linked pages, and alteration of contained templates.
                    statsContext['touched'] = pageData['touched']

                    # Retrieve content of the Information page in BeautifulSoup structure.
                    infoURL = "http://en.wikipedia.org/w/index.php?title=" + articleEncodedTitle + "&action=info"

                    # Find the soup structure if BeautifulSoup structure of the Wikipedia page is available, and there is number of watchers available in the soup structure of the Wikipedia page, which means that the Wikipedia page is in an appropriate format.
                    infoSoup = scrapeWebsite(infoURL, 'tr', 'id', "mw-pageinfo-watchers", "", "", "")

                    if infoSoup != False:

                        # Print out the number of redirects to this page.
                        redirectsStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-watchers").findNext('tr')
                        redirectsStatisticsNumber = '0'
                        if redirectsStatisticsTag:
                            redirectsStatisticsNumber = redirectsStatisticsTag.findAll('td')[1].renderContents()

                        statsContext['redirects'] = redirectsStatisticsNumber

                        # Print out the date of page creation.
                        firsttimeStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-firsttime")
                        firsttimeStatisticsNumber = '0'
                        if firsttimeStatisticsTag:
                            firsttimeStatisticsNumber = firsttimeStatisticsTag.findAll('td')[1].find('a').renderContents()

                        statsContext['creationDate'] = firsttimeStatisticsNumber

                        # Print out the total number of edits.
                        editsStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-edits")
                        editsStatisticsNumber = '0'
                        if editsStatisticsTag:
                            editsStatisticsNumber = editsStatisticsTag.findAll('td')[1].renderContents()

                        statsContext['editsNum'] = editsStatisticsNumber

                        # Print out the total number of distinct authors.
                        # authorsStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-authors")
                        # authorsStatisticsNumber = '0'
                        # if authorsStatisticsTag:
                        #     authorsStatisticsNumber = authorsStatisticsTag.findAll('td')[1].renderContents()

                        # statsContext['distinctAuthors'] = authorsStatisticsNumber

                        # Print out recent number of edits (within past 30 days).
                        recentEditsStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-recent-edits")
                        recentEditsStatisticsNumber = '0'
                        if recentEditsStatisticsTag:
                            recentEditsStatisticsNumber = recentEditsStatisticsTag.findAll('td')[1].renderContents()

                        statsContext['recentEdits'] = recentEditsStatisticsNumber

                        # Print out recent number of distinct authors.
                        recentAuthorsStatisticsTag = infoSoup.find('tr', id="mw-pageinfo-recent-authors")
                        recentAuthorsStatisticsNumber = '0'
                        if recentAuthorsStatisticsTag:
                            recentAuthorsStatisticsNumber = recentAuthorsStatisticsTag.findAll('td')[1].renderContents()

                        statsContext['recentDistinctAuthors'] = recentAuthorsStatisticsNumber

                    # Otherwise:
                    else:

                        statsContext['redirects'] = ''

                        # Print out the date of page creation.
                        statsContext['creationDate'] = ''

                        # Print out the total number of edits.
                        statsContext['editsNum'] = ''

                        # Print out the total number of distinct authors.
                        # statsContext['distinctAuthors'] = ''

                        # Print out recent number of edits (within past 30 days).
                        statsContext['recentEdits'] = ''

                        # Print out recent number of distinct authors.
                        statsContext['recentDistinctAuthors'] = ''

                    # # Retrieve content of the Revision history statistics page in BeautifulSoup structure.
                    # rhStatisticsURL = "http://tools.wmflabs.org/xtools/articleinfo/index.php?article=" + articleEncodedTitle + "&lang=en&wiki=wikipedia"

                    # # Find the soup structure if BeautifulSoup structure of the tools.wmflabs.org page is available, and there is generalstats container available in the soup structure of the tools.wmflabs.org page, which means that the tools.wmflabs.org page is in an appropriate format.
                    # rhStatisticsSoup = scrapeWebsite(rhStatisticsURL, 'div', 'id', "generalstats", "p", "class", "alert alert-danger xt-alert")
                    
                    # if rhStatisticsSoup != False and rhStatisticsSoup != "No Search Result":

                    #     # Find the container.
                    #     generalstatsContainer = rhStatisticsSoup.find('div', id="generalstats").find('tr').findAll('tr')

                    #     # Print out the number of minor edits.
                    #     submitAndPrint (statsFile, "Number of minor edits: ", re.search('(\d+) ', generalstatsContainer[6].findAll('td')[1].renderContents()).group(1))

                    #     # Print out the average time between edits.
                    #     submitAndPrint (statsFile, "Average time between edits: ", generalstatsContainer[10].findAll('td')[1].renderContents())

                    #     # Print out the average number of edits per month.
                    #     submitAndPrint (statsFile, "Average number of edits per month: ", generalstatsContainer[12].findAll('td')[1].renderContents())

                    #     # Print out the average number of edits per year.
                    #     submitAndPrint (statsFile, "Average number of edits per year: ", generalstatsContainer[13].findAll('td')[1].renderContents())

                    #     # Print out the number of edits in the last day.
                    #     submitAndPrint (statsFile, "Number of edits in the past 24 hours: ", generalstatsContainer[15].findAll('td')[1].renderContents())

                    #     # Print out the number of edits in the last week.
                    #     submitAndPrint (statsFile, "Number of edits in the past 7 days: ", generalstatsContainer[16].findAll('td')[1].renderContents())

                    #     # Print out the number of edits in the last month.
                    #     submitAndPrint (statsFile, "Number of edits in the past 30 days: ", generalstatsContainer[17].findAll('td')[1].renderContents())

                    #     # Print out the number of edits in the last year.
                    #     submitAndPrint (statsFile, "Number of edits in the past 365 days: ", generalstatsContainer[18].findAll('td')[1].renderContents())

                    #     # Print out the number of links to this page.
                    #     submitAndPrint (statsFile, "Number of links to this page: ", generalstatsContainer[27].findAll('td')[1].find('a').renderContents())

                    # # Otherwise:
                    # else:

                    #     # Print out the number of minor edits.
                    #     submitAndPrint (statsFile, "Number of minor edits: ", '')

                    #     # Print out the average time between edits.
                    #     submitAndPrint (statsFile, "Average time between edits: ", '')

                    #     # Print out the average number of edits per month.
                    #     submitAndPrint (statsFile, "Average number of edits per month: ", '')

                    #     # Print out the average number of edits per year.
                    #     submitAndPrint (statsFile, "Average number of edits per year: ", '')

                    #     # Print out the number of edits in the last day.
                    #     submitAndPrint (statsFile, "Number of edits in the the past 24 hours: ", '')

                    #     # Print out the number of edits in the last week.
                    #     submitAndPrint (statsFile, "Number of edits in the past 7 days: ", '')

                    #     # Print out the number of edits in the last month.
                    #     submitAndPrint (statsFile, "Number of edits in the past 30 days: ", '')

                    #     # Print out the number of edits in the last year.
                    #     submitAndPrint (statsFile, "Number of edits in the past 365 days: ", '')

                    #     # Print out the number of links to this page.
                    #     submitAndPrint (statsFile, "Number of links to this page: ", '')

                    # Find current date.
                    todayDate = (datetime.date.today()).strftime('%Y%m%d')

                    # Find date of a month ago.
                    pastMonthDate = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y%m%d')

                    # Retrieve content of the traffic statistics page in BeautifulSoup structure.
                    trafficStatisticsURL = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/" +
                                            "all-access/user/" + articleEncodedTitle.replace("/", "-") + "/daily/" +
                                            pastMonthDate + "/" + todayDate)

                    viewsErrorsNum = 0
                    while viewsErrorsNum < 10:
                        try:
                            print ("Requesting " + str(trafficStatisticsURL))
                        except:
                            print ("UnicodeEncodeError: 'ascii' codec can't encode character.")
                        try:
                            numberofViewsResponse = requests.get(trafficStatisticsURL)
                            numberofViewsResponse = numberofViewsResponse.json()
                            numberofViewsPerDays = numberofViewsResponse['items']
                            break
                        except:
                            print ("\n\n\nI cannot retrieve the number of views of this article!")
                            time.sleep(1)
                            viewsErrorsNum += 1

                    # Print out the number of views in the last month.
                    viewsNum = 0
                    if viewsErrorsNum < 10:
                        for numberofViewsPerDay in numberofViewsPerDays:
                            viewsNum += numberofViewsPerDay['views']

                    statsContext['viewsNum'] = viewsNum
                    print ("# of views in the last month: " + str(viewsNum))

                    if articleSoup != False:

                        # Retrieve the fully formatted reference tags.
                        referenceList = articleSoup.findAll('li', id=re.compile('cite_note.*'))

                        # Print out the total number of references.
                        statsContext['referencesNum'] = len(referenceList)

                        # If referenceList is None, return nothing.
                        # if referenceList != None:
                        #     referenceList = referenceList.findAll('li')
                        # else:
                        #     referenceList = [ ]

                        # Find the number of citation on the page after 1990, 1991, 1992, ... and 2014.
                        afterYear = 2010

                        # Number of references which have been published after afterYear.
                        referencesNumber = 0

                        # Among all th references, find the ones which have been published after afterYear.
                        for reference in referenceList:

                            # Find the year digits.
                            yearDigits = re.search('.*(\d\d\d\d).*', reference.renderContents())

                            # If year digits found, cvonvert yearDigits into a proper integer, and check if it is greater than afterYear
                            if yearDigits != None and int(yearDigits.group(1)) >= afterYear:

                                # Increment the number of references which have been published after afterYear.
                                referencesNumber += 1

                            # Print out the number of references which have been published after afterYear.
                        statsContext['referencesNumAfter2010'] = referencesNumber

                    # Otherwise:
                    else:
                        
                        statsContext['referencesNum'] = '0'

                        # Find the number of citation on the page after 1990, 1991, 1992, ... and 2014.
                        statsContext['referencesNumAfter2010'] = '0'

                    # Calculate the number of external hyperlinks in this page in the first part of the response.
                    if 'extlinks' in pageData:
                        numberOfExternalLinks = len(pageData['extlinks'])

                else:
                    # Calculate the number of external hyperlinks in this page in the first part of the response.
                    if 'extlinks' in pageData:
                        numberOfExternalLinks += len(pageData['extlinks'])

                # Increment responseCounter.
                responseCounter = 1
    
                # Print out the number of external hyperlinks in this page.
                print "# External Hyperlinks: " + str(numberOfExternalLinks), '\n'
                
                statsContext['externalLinks'] = numberOfExternalLinks

                # Return a signal indicating that the Wikipedia page data has been saved successfully.
                return statsContext

            # Otherwise:
            else:

                # Return a signal indicating that the Wikipedia page data has not been saved successfully.
                return []

# Receive Wikipedia pages recommendations file and generate Wikipedia pages' stats file.
def WikipediaStatsGenerator(recommendationsFile):

    previousURLs = []

    with open(recommendationsFile + '.csv', 'rb') as fr:
        reader = csv.reader(fr)

        with open(recommendationsFile + '_Stats.csv', 'wb') as fw:
            writer = csv.writer(fw)

            pubResultRow = ['ID', 'Title', 'Edit Protection Level', 'Class', 'Importance', 'Page Length', '# watchers', 'Time of Last Edit', '# redirects to this page', 'Page Creation Date', 'Total # edits', 'Recent # edits (within past 30 days)', 'Recent # distinct authors', '# views (last 90 days)', 'Total # references', '# references published after 2010', '# External Hyperlinks']
            writer.writerow(pubResultRow)

            header = next(reader)
            for row in reader:
                for i in range(2, len(row) - 1, 3):
                    if row[i] != ""  and row[i+1] != "":
                        wikipageTitle = convert_unicode(row[i])
                        print "Wikipage Title:", wikipageTitle
                        wikipageURL = row[i+1]
                        print "Wikipage URL:", wikipageURL
                        wikipediaSoup = soupStructure(wikipageURL)
                        print "Soup is Retrieved."

                        if wikipediaSoup != "" and not wikipageURL in previousURLs:
                            pubResultRow = WikipediaPageStats (wikipageURL, wikipediaSoup, wikipageTitle, 'Econ')

                            trialNum = 0
                            while pubResultRow == [] and trialNum < 10:
                                trialNum += 1
                                # print "wikipageURL:", wikipageURL, "is not found. Please enter a new one:"
                                # wikipageURL = raw_input()
                                pubResultRow = WikipediaPageStats (wikipageURL, wikipediaSoup, wikipageTitle, 'Econ')

                            print pubResultRow
                            writer.writerow(pubResultRow)
                            previousURLs.append(wikipageURL)

# Define a function to convert a Unicode URL to ASCII (UTF-8 percent-escaped).
def fixurl(url):
    # turn string into unicode
    if not isinstance(url,unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass,at,hostport = parsed.netloc.rpartition('@')
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'),'')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'),'=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))

    # put it back together
    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))

def findWikiprojectNumOfViews(WikiprojectEncodedTitle="WikiProject_Economics"):

    with open(WikiprojectEncodedTitle + '_Pages_Views.csv', 'wb') as fw:
        writer = csv.writer(fw)

        pubResultRow = ['WikiprojectTitle', 'Page Id', 'Page Title', '# views (last 90 days)']
        writer.writerow(pubResultRow)

        # Define the parameters to be retrieved from alahele.ischool.uw.edu:8997 for Wikiproject pages.
        pagesReqParameteres = { 'project':WikiprojectEncodedTitle }

        # Define the URL to be retrieved from alahele.ischool.uw.edu:8997 for Wikiproject pages.
        pagesReqURL = "https://alahele.ischool.uw.edu:8997/api/getProjectPages?" + urllib.urlencode(pagesReqParameteres)

        print pagesReqURL

        # Define a flag to show if there is any problem with the API response.
        responseNotRetrieved = True

        # Define the response object.
        pagesResponse = {}

        # Define the list of pages in this WikiProject.
        pageDataList = {}

        TotalPagesViews = 0
        TotalPagesNum = 0

        errorNumber = 0

        while responseNotRetrieved and errorNumber <= 10:
            try:
                # Retrieve list of the Wikiproject pages through the API.
                pagesResponseJSON = requests.get(pagesReqURL, verify=False, timeout=1000)

                # Convert the response to JSON.
                pagesResponse = pagesResponseJSON.json()

                # Retrieve the errorstatus attribute of the response.
                errorstatusAttribute = pagesResponse['errorstatus']

                # If errorstatus shows that the data is retrieved properly:
                if errorstatusAttribute == 'success':
                    responseNotRetrieved = False

            except Exception, e:

                errorNumber += 1

                print "An exception occurred: " + str(e)

                # Sleep for 4 seconds to be able to retrieve the page content appropriately.
                time.sleep(4)
        if errorNumber >= 10:
            print "I am not able to request this page from Alahele server."
            raw_input()

        # If there is any page under the scope of this project:
        if len(pagesResponse['result'].keys()) != 0:

            # Retrieve the result list of pages from the response.
            pageDataList = pagesResponse['result'][WikiprojectEncodedTitle]

            # For all the pages in the result list:
            for pageData in pageDataList:

                pageEncodedTitle = pageData['tp_title']

                # Find the page encoded URL.
                pageEncodedTitle = fixurl(pageEncodedTitle)

                if "WikiProject_" in pageEncodedTitle:
                    pageEncodedTitle = "Wikipedia:" + pageEncodedTitle

                print "Page Title:", pageEncodedTitle

                pageID = pageData['pp_id']

                print "Page ID:", pageID

                # Retrieve content of the traffic statistics page in BeautifulSoup structure.
                trafficStatisticsURL = "http://stats.grok.se/en/latest90/" + pageEncodedTitle

                # Find the soup structure if BeautifulSoup structure of the stats.grok.se page is available, and there is a p tag available in the soup structure of the stats.grok.se page, which means that the stats.grok.se page is in an appropriate format.
                trafficStatisticsSoup = scrapeWebsite(trafficStatisticsURL, 'p', '', '', "", "", "")
                
                if trafficStatisticsSoup != False:

                    # Retrieve the p tag including the number of views and the traffic ranking.
                    trafficPTag = strip_tags(trafficStatisticsSoup.find('p').renderContents().decode('utf-8'))

                # Print out the number of views in the last 90 days.
                viewsOverPastNinetyDays = re.search('.*has been viewed (\d*).*', trafficPTag).group(1)

                print "# Views:", viewsOverPastNinetyDays

                # Write the Wikiproject info in the corresponding CSV file as a row.
                writer.writerow([WikiprojectEncodedTitle.encode('utf-8'), pageID, pageEncodedTitle.encode('utf-8'), viewsOverPastNinetyDays])

                TotalPagesViews = num(viewsOverPastNinetyDays)
                TotalPagesNum += 1

        print "Average # Views over the past 90 days:", (TotalPagesViews / TotalPagesNum)