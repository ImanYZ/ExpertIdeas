# Import Regular Expressions' libraries
import re
import unicodedata

# Import time libraries
import time

# Import BeautifulSoup library
from bs4 import SoupStrainer, BeautifulSoup

# Import the library needed to extract plain text from html.
from HTMLParser import HTMLParser

# Import requests library.
import requests

# Import urllib to manipulate URLs
import urllib
import urllib2

# Import UserAgent library to fake the user agent
from fake_useragent import UserAgent

# Import Tor Library.
from TorLibrary import randomUserAgentGenerator, userAgentGenerator, newIdentityGenerator


# Check if the string is in ASCII or not.
def convert_unicode(s):
    if isinstance(s, unicode):
        return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
    else:
        return s

# Define a function to request a search query from Google Scholar and return the respone:
def recieveResponseFromWebsite(oldUserAgent, domainName, subDomain, encoded_Url):
        
        # Creat an HTTP connection to the website.
        # conn = httplib.HTTPConnection(domainName)

        # Define a random user-agent.
        # user_agent = randomUserAgentGenerator(userAgentObj, oldUserAgent)

        user_agent = randomUserAgentGenerator(oldUserAgent)

        # Show the User Agent status.
        # print("Current User Agent:", user_agent)

        # Save current user agent in oldUserAgent.
        oldUserAgent = user_agent

        header = user_agent

        # Send a GET request to Google Scholar, searching for the encoded URL, and receive response from it.
        # conn.request("GET", subDomain + encoded_Url, headers = header)

        response = requests.get(domainName + subDomain + encoded_Url, headers = header, timeout=70)

        # Change the response encoding to utf-8.
        # response.encoding = 'utf-8'

        # Receive response from Google Scholar.
        # response = conn.getresponse()

        # Read the response, and convert it to BeautifulSoup format.
        # responseHTML = response.read()
        responseHTML = response.text

        # Return the responsze.
        return responseHTML

# Define a function to request a search query from the website Scholar and return the respone in BeautifulSoup structure:
def GETRequestFromWebsite(domainName, subDomain, searchTerm, errorCounter, requestCount):
        
        # Define a User Agent object.
        # userAgentObj = UserAgent()

        # Define a random user-agent, and save it in oldUserAgent.
        # oldUserAgent = userAgentGenerator(userAgentObj)

        oldUserAgent = userAgentGenerator()

        # Connect to Tor
        # connectTor()

        # Pick a new IP address. (If we initialize the requestCount to -1, there is no need of this command.)
        # newIdentityGenerator()

        # Flag to indicate inapproperiate response.
        notRespondedCorrectlyYet = True

        while notRespondedCorrectlyYet:

            # requestCount = requestCount + 1

            # # if we have not changed our IP address in the last 10 requests:
            # if requestCount % 10 == 0:

            #         # Pick a new IP address.
            #         newIdentityGenerator()

            # If the search term is unicode, encript it to string.
            if isinstance(searchTerm, unicode):

                searchTerm = searchTerm.encode('utf-8')

            # Encode the URL into an acceptable URL format.
            encoded_Url = urllib.quote_plus(searchTerm)

            # Try if the website does not return a strange error.
            try:

                print "Sending request to: " + domainName + subDomain + encoded_Url

                # Request a search query from the website Scholar and return the respone in BeautifulSoup format
                # responseHTML = recieveResponseFromWebsite(userAgentObj, oldUserAgent, domainName, subDomain, encoded_Url)

                responseHTML = recieveResponseFromWebsite(oldUserAgent, domainName, subDomain, encoded_Url)

            except:
                # If the website did not respond correctly, log the error, pick a new identity and continue to the next round of the loop.

                # Increment the number of error messages.
                errorCounter = errorCounter + 1

                # If there are less than 10 errors:
                if errorCounter < 10:

                    # Display the logMessage
                    print "\n\nThe website did not return an appropriate response.\n\n"

                    # Pick a new IP address.
                    newIdentityGenerator()

                    # Continue to the loop and search this query again.
                    continue

                # Otherwise:
                else:

                    print "I tried for 10 times, but I am not able to retrieve the content of the page:", domainName + subDomain + encoded_Url

                    return ''

            try:

                # Convert the html response into BeautifulSoup structure.
                soup = BeautifulSoup(responseHTML, 'html5lib')

            except Exception:

                soup = ''

                print "There is a problem with conversion to BeautifulSoup structure."

            # Convert the response to the BeautifulSoup format and return the result.
            return (responseHTML, soup, errorCounter)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        uniFed = self.fed
        if type(uniFed) == type("string"):
            uniFed = uniFed.decode('utf-8')
        return u' '.join(uniFed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# If there are more than 10 errors, delay for 4 minutes.
def ifMoreThan10ErrorsDelay4Minutes(errorCounter):

    newIdentityGenerator()

    if errorCounter % 10 == 0:

        print "\n\n\nI encountered more than 10 errors. So I am going to wait for 4 minutes.\n\n\n"

        # Delays for 240 seconds = 4 minutes.
        for minuteCounter in range(4 * errorCounter / 10):
            
            print str(4 * errorCounter / 10 - minuteCounter), "minutes left."

            time.sleep(60)

# Define a function which finds the domain name part of the url:
def domainNameFinder(url):

    # Find the domain name part of the url.
    return re.search('(?:https?:\/\/)?(?:www.)?([a-zA-Z0-9]+[.][a-zA-Z0-9]+)(?:\/|$|#|[:])', url).group(1)

# Define a function which recieves a Wikipedia Category page url, and returns the soup structure of that category page.
def soupStructure(url):

    # Number of times the website was not responsive.
    errorCounter = 0

    # While the response has not received correctly, send the request again.
    while True:

        try:

            # Increment errorNumber.
            errorCounter += 1
        
            print "Sending request to:" , convert_unicode(url)

            # Define a User Agent object.
            # userAgentObj = UserAgent()

            # Define a random user-agent, and save it as user_agent.
            # user_agent = userAgentGenerator(userAgentObj)

            user_agent = userAgentGenerator()

            header = user_agent

            # Retrive file from the url.
            # html = urllib2.urlopen(url).read()
            response = requests.get(url, headers = header, verify=False)
            html = response.text

            # Change the response encoding to latin-1.
            # html.encoding = 'latin-1'

            # Convert the html file into the BeautifulSoup structure.
            soup = BeautifulSoup(html, 'html5lib')

            # If there is no problem with the BeautifulSoup structure:
            if soup.title != None or soup.find('div') != None or soup.find('p') != None:

                # Return the soup structure.
                return soup

            # If there are less than 13 errors:
            if errorCounter < 13:

                continue

            # Otherwise:
            else:

                print "\n\n\nI am not able to retrieve the soup of the webpage:", url, "\n\nsoup.title:", str(soup.title), "\n\nsoup.find('div'):", str(soup.find('div')), "\n\nsoup.find('p'):", soup.find('p'), "\n\nPlease enter a new url:"

                url = raw_input()

                if url == "1":
                    return ''
        # If an error raised, send the request again.
        except Exception as e:

            # If there are less than 13 errors:
            if errorCounter < 13:

                continue

            # Otherwise:
            else:

                print "\n\n\nI am not able to retrieve the content of the webpage:", url, "The error message is:", str(e), "\n\nPlease enter a new url:"

                url = raw_input()

                if url == "-1":
                    return ''

# Define a function to extract the BeautifulSoup structure and check if the response soup is in a good shape:
def ifAppropriateSoup(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue):

    # Retrieve the BeautifulSoup structure of the webpage.
    soup = soupStructure(url)

    # Define the condition as soup is not available, or criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format.
    noAppropriateResponse = False

    # If there is no soup structure:
    if soup == '':

        print "Inappropriate Response. There is no soup."

        noAppropriateResponse = True

    # Otherwise, if there is no body tag:ifAppropriateSoup
    elif soup == None:

        print "Inappropriate Response. There is no soup."

        soup = False

    # Otherwise, if errorAttribute equals '':
    elif errorAttribute == '' and errorTag != "" and soup.find(errorTag) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'id', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'id' and errorTag != "" and soup.find(errorTag, id=errorValue) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'class', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'class' and errorTag != "" and soup.find(errorTag, class_=errorValue) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'idre', and errorTag having errorValue within the critical attribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'idre' and errorTag != "" and soup.find(errorTag, id=re.compile(errorValue)) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'classre', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'classre' and errorTag != "" and soup.find(errorTag, class_=re.compile(errorValue)) != None:

        soup = False

    # Otherwise, if errorAttribute equals 'text', and errorTag having errorValue within the errorAttribute is found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif errorAttribute == 'text' and errorTag != "" and soup.find(errorTag, text=re.compile(errorValue)) != None:

        soup = False

    # Otherwise, if criticalAttribute equals '':
    elif criticalAttribute == '' and soup.find(criticalTag) == None:

        print "Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag + "''):" + str(soup.find(criticalTag))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'id', and criticalTag having criticalValue within the criticalAttribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'id' and soup.find(criticalTag, id=criticalValue) == None:

        print "Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag + "', id='" + criticalValue + "'):" + str(soup.find(criticalTag, id=criticalValue))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'class', and criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'class' and soup.find(criticalTag, class_=criticalValue) == None:

        print "Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag + "', class_='" + criticalValue + "'):" + str(soup.find(criticalTag, class_=criticalValue))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'idre', and criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'idre' and soup.find(criticalTag, id=re.compile(criticalValue)) == None:

        print "Inappropriate Response. criticalAttribute:" + criticalAttribute + " Soup.find('" + criticalTag + "', id=" + "re.compile('" + criticalValue + "')):" +str(soup.find(criticalTag, id=re.compile(criticalValue)))

        noAppropriateResponse = True

    # Otherwise, if criticalAttribute equals 'classre', and criticalTag having critical value within the critical attribute is not found in the soup structure of the webpage, which means that the webpage is not in the appropriate format:
    elif criticalAttribute == 'classre' and soup.find(criticalTag, class_=re.compile(criticalValue)) == None:

        print "Inappropriate Response."
        noAppropriateResponse = True

    return noAppropriateResponse, soup

# Define a function to try a fair number of times to extract the soupStructure of the website.
def scrapeWebsite(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue):

    # Number of times the website has not responded an appropriate soup structure.
    errorCounter = 0

    # Define a function to extract the BeautifulSoup structure and check if the response soup is in a good shape:
    noAppropriateResponse, soup = ifAppropriateSoup(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue)

    # While noAppropriateResponse equals True:
    while noAppropriateResponse == True:

        # Pick a new IP address.
        # newIdentityGenerator()

        # Increment the number of times the website has not responded an appropriate soup structure.
        errorCounter += 1

        # If there are less than 10 errors:
        if errorCounter % 10 != 0:

            # Define a function to extract the BeautifulSoup structure and check if the response soup is in a good shape:
            noAppropriateResponse, soup = ifAppropriateSoup(url, criticalTag, criticalAttribute, criticalValue, errorTag, errorAttribute, errorValue)

            continue

        # Otherwise:
        else:

            return False

    return soup
