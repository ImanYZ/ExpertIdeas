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

# Import Website Scraping Library.
from WebsiteScapingLibrary import GETRequestFromWebsite, strip_tags, ifMoreThan10ErrorsDelay4Minutes, soupStructure


# Define a nunction to convert the obfuscated email address on ideas.repec.org to the structured format.
def liame2(arguments):

	# Define the return value as the first argument.
	address = arguments[0]

	iterator = range(1, len(arguments)).__iter__()

	# Iterate through arguments.
	for i in iterator:

		# If the current argument equals 'm7i7', replace it in address with @:
		if arguments[i] == 'm7i7':

			# Add an @ plus the next argument to address.
			address = arguments[i+1] + "@" + address

			# Increment the index of arguments.
			iterator.next()

		# Otherwise:
		else:

			# Add the next argument to address.
			address = arguments[i] + "." + address

	return address

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

# Define the webbrowser as Phantomjs and pretend it as Google Chrome.
browserEconpapers = defineBrowser()
browserIdeas = defineBrowser()

# Define a funtion which extracts the first keyword of a paper from http://econpapers.repec.org/.
def keywordExtractor(econpapersURL):

	browserEconpapers.get(econpapersURL)

	keywords = []

	try:

		iframe = browserEconpapers.find_element_by_id('absframe')
		browserEconpapers.switch_to_default_content()
		browserEconpapers.switch_to_frame(iframe)

		# Find the Main tag.
		mainTag = browserEconpapers.find_element_by_css_selector(".abstractframe")

		# abstractTag = ''

		# try:
		#     # Find the tag containging abstract text.
		#     abstractTag = mainTag.find_element_by_xpath("//*[contains(text(), 'Abstract:')]")
		#     abstractTag = abstractTag.find_element_by_xpath('..')

		#     # Find the first abstract text.
		#     abstract = abstractTag.text

		# except:
		#     print "There is no abstract available for this publication."
		
		#     abstract = ''

		# if abstract == '' or is_ascii(abstract):

		# Find the tag containging keyword text.
		keywordTag = mainTag.find_element_by_xpath("//*[contains(text(), 'Keywords:')]")

		keywordsTags = keywordTag.find_element_by_xpath('..').find_elements_by_tag_name('a')
		
		for keywordTag in keywordsTags:

			keyword = keywordTag.text

			if '&' in keyword:
				keyword = re.sub(r"([&]amp;)", " and ", keyword)

			if is_ascii(keyword) and not 'http' in keyword:
				print "Keyword from EconPapers: " + keyword

				keywords.append(keyword.lower())
			else:
				keyword = ''
				print "There are Non-English characters in the keyword on econpapers.repec.org."

	except:
		print "There is no keyword for this publication on econpapers.repec.org."
		keywords = []
	# # If there is any Non-English characters in the abstract:
	# else:
	#     keyword = ''
	#     print "There are Non-English characters in the Abstract."

	return keywords

def keywordAndSpecializationExtractor(ideasURL, econpapersURL):

	browserIdeas.get(ideasURL)

	keywords = []
	specializations = []

	try:
		relatedResearchDIV = browserIdeas.find_element_by_id('related-body')

		paperSpecs = relatedResearchDIV.find_elements_by_xpath("//*[contains(text(), 'been announced in the following')]/parent::*/following-sibling::ul/child::li")

		if len(paperSpecs) == 0:
			print "There is no category for this publication."
			return keywords, specializations

	except:
		print "There is no category for this publication."
		return keywords, specializations
	
	try:
		keywordsParent = relatedResearchDIV.find_element_by_xpath("//*[contains(text(), 'Keywords:')]")

		keywordsTags = keywordsParent.find_element_by_xpath('..').find_elements_by_tag_name('a')

		for keywordTag in keywordsTags:
			keyword = keywordTag.get_attribute("innerHTML")

			if '&' in keyword:
				keyword = re.sub(r"([&]amp;)", " and ", keyword)

			if is_ascii(keyword) and not 'http' in keyword:
				print "Keyword from EconPapers: " + keyword

				keywords.append(keyword.lower())
			else:
				print "There are Non-English characters in the keyword on econpapers.repec.org."

	except:
		print "There is no keyword for this publication on Ideas. I'm going to search Econpapers.repec.org"
		keywords = keywordExtractor(econpapersURL)
		if keywords == []:
			specializations = []
			return keywords, specializations
	
	for specTag in paperSpecs:

		paperCategories = re.search("[ ][(](.+)[)]", specTag.get_attribute("innerHTML"))

		if paperCategories != None:

			paperCategory = paperCategories.group(1)

			print "paperCategory: ", paperCategory

			if paperCategory != "All new papers":

				specializations.append(paperCategory)

	# # If there is any Non-English characters in the abstract:
	# else:
	#     keyword = ''
	#     print "There are Non-English characters in the Abstract."

	return keywords, specializations

def click_and_wait(htmlObj):

	htmlObj.click()

	# Random float x, 1.0 <= x < 10.0
	# randomTimePeriod = random.uniform(1, 4)

	print "Wait time: " + str(1) + " seconds"

	time.sleep(1)

# Define the webbrowser as Phantomjs and pretend it as Google Chrome.
browser = defineBrowser()

# Define a funtion which extracts the email address and homepage url of an author from his ideas.repec.org page.
def econPapersProfileExtractor(ideasURL, specialization):

	returnValue = []
	affiliationReturnValue = []

	# Retrieve the url html page content and convert it into BeautifulSoup structure.
	ideasSoup = soupStructure(ideasURL)

	# If the content of the page is returned in BeautifulSoup structure:
	while ideasSoup == '':
		ideasURL = raw_input()
		ideasSoup = soupStructure(ideasURL)

	# while True:
	# 	try:

	# Find the main DIV.
	obfuscateScriptMainDIV = ideasSoup.body.find('div', id="main")

	# If there is a main DIV:
	if obfuscateScriptMainDIV != None:

		# Find the FirstName tag.
		firstNameTag = ideasSoup.body.find(text=re.compile('.*First Name:.*'))
		
		if firstNameTag == None:

			firstName = ''

		else:
			# firstNameTag = strip_tags(firstNameTag)
			# # Find the first name.
			# firstName = firstNameTag[15:]
			firstNameTag = firstNameTag.parent.parent.findNext('td')
			# Find the first name.
			firstName = strip_tags(unicode(firstNameTag.renderContents(), 'utf8'))

		# Find the LastName tag.
		lastNameTag = ideasSoup.body.find(text=re.compile('.*Last Name:.*'))

		if lastNameTag == None:

			lastName = ''

		else:
			# lastNameTag = strip_tags(lastNameTag)
			# # Find the last name.
			# lastName = lastNameTag[14:]
			lastNameTag = lastNameTag.parent.parent.findNext('td')
			# Find the first name.
			lastName = strip_tags(unicode(lastNameTag.renderContents(), 'utf8'))

		locations = []

		# Find all the Location tags.
		locationTags = ideasSoup.body.findAll(text=re.compile('.*Location:.*'))

		for locationTag in locationTags:

			locationTag = strip_tags(locationTag)
			# Find the location.
			locations.append(locationTag[10:])

		affiliations = []

		# Find the Affiliation tag.
		affiliationTags = ideasSoup.body.find('div', id='affiliation-body').findAll('h4')

		for affiliationTag in affiliationTags:

			# Find the affiliation.
			affiliation = strip_tags(unicode(affiliationTag.renderContents(), 'utf8'))

			affiliations.append(affiliation)

		# Find the Homepage tag.
		homepageParentTag = ideasSoup.body.find(text=re.compile('.*Homepage:.*'))

		if homepageParentTag == None:
       
			homepage = ''

		else:
			# Find the homepage tag.
			homepageTag = homepageParentTag.parent.parent.findNext('td').findNext('a')

			if homepageParentTag == None:

				homepage = ''

			else:
				# Find the homdepage.
				homepage = homepageTag['href']

		browser.get(ideasURL)

		email = ''

		# Find the obfuscating email tag.
		emailTag = browser.find_element_by_xpath("//*[@id='details-body']/table/tbody/tr[7]/td[2]")

		# If there is an email tag inside obfuscateScriptMainDIV:
		# if emailTag != None and emailTag.text != '[This author has chosen not to make the email address public]':
		if emailTag != None and not ' ' in emailTag.text:

			# Add the found email address in an appropriate format to returnVariable.
			email = emailTag.text

			print email

		# # Find the obfuscating script.
		# obfuscateScriptTag = obfuscateScriptMainDIV.find('div', id='details-body').find('span', {'data-liame2'})

		# # If there is a script tag inside obfuscateScriptMainDIV:
		# if obfuscateScriptTag != None:

		#     # Find the content of the obfuscating script.
		#     obfuscateScriptContent = obfuscateScriptTag.renderContents()

		#     # Find both email parts from the content of the obfuscating script.
		#     emailParts = re.findall("'([^',]+)'", hparser.unescape(obfuscateScriptContent))

		#     # Add the found email address in an appropriate format to returnVariable.
		#     returnVariable['email'] = liame2(emailParts)

		# Define publication array.
		publicationArray = []
		specializations = []
		specializationRepetition = []

		# Find the list of publications.
		publicationsList = browser.find_element_by_id('works-group').find_elements_by_tag_name('li')

		# If there is any publication listed:
		if len(publicationsList) != 0:

			# For each publication:
			for publicationIndex in range(len(publicationsList)):

				# Extract the citation.
				citationText = convert_unicode(publicationsList[publicationIndex].text)

				# If there are multiple versions of the citation, only take the first one.
				citationTextFirst = re.split(r'\s*\n+\s*', citationText)

				# Extract Publication title.
				publicationTitleTag = publicationsList[publicationIndex].find_element_by_tag_name('a')
				publicationTitle = publicationTitleTag.text

				notUnicodeCharacter = True
				try:
					print 'publicationTitle: ' + publicationTitle
					print 'citationText: ' + citationTextFirst[0]

				except:
					print "Unicode character found."
					notUnicodeCharacter = False
						
				# Check it publicationTitle is in ASCII (all English characters) continue:
				if is_ascii(publicationTitle) and notUnicodeCharacter:

					# Identify if this citation has been shown up previously.
					isNotAnotherVersion = True

					# For all citations listed previously:
					for citationIndex in range(len(publicationArray)):

						# if citation has been shown up previously:
						if publicationTitle.lower() in publicationArray[citationIndex][2].lower():

							# Citation has been shown up previously.
							isNotAnotherVersion = False

							print citationText, "Is another version of", publicationArray[citationIndex][2]
							break

					paperYearGroup = re.search("^\D+[,][ ](\d+)[.]", citationTextFirst[0])

					if isNotAnotherVersion and paperYearGroup != None:

						paperYear = paperYearGroup.group(1)

						# Extract the first keyword of this paper from econpapers.
						# firstKeyword = keywordExtractor("http://econpapers.repec.org/scripts/search.pf?ft=" + urllib.quote_plus(publicationTitle.encode('utf-8')))
						keywords, paperspecList = keywordAndSpecializationExtractor(publicationTitleTag.get_attribute("href"), 'http://econpapers.repec.org/scripts/search.pf?ft=' + urllib.quote_plus(('"' + publicationTitle + '" ' + firstName + " " + lastName).encode('utf-8')))

						if keywords != None and keywords != [] and paperspecList != None and paperspecList != []:

							print "keywords: ", keywords

							# Append the results to the returning array.
							publicationArray.append([publicationTitle, paperYear, citationTextFirst[0], keywords, paperspecList])

							print "publicationArray: ", publicationArray

			publicationArray.sort(key=itemgetter(1), reverse=True)
			print "Sorted publicationArray: ", publicationArray

			specializationFound = False
			for publicationElement in publicationArray:
				paperspecList = publicationElement[4]
				if paperspecList != []:
					for paperSpec in paperspecList:
						if paperSpec in specializations:
							specializationRepetition[specializations.index(paperSpec)] += 1
							if specializationRepetition[specializations.index(paperSpec)] == 7:
								specializationFound = True
								break
						else:
							specializations.append(paperSpec)
							specializationRepetition.append(1)
				if specializationFound:
					break
			print "specializations: ", specializations
			print "specializationRepetition: ", specializationRepetition

			maxSpex = -1
			maxIndex = -1
			for specIndex in range(len(specializationRepetition)):
				if specializationRepetition[specIndex] > maxSpex:
					maxSpex = specializationRepetition[specIndex]
					maxIndex = specIndex
			print "Specialization before:", specialization
			specialization = ""
			print publicationArray
			pubIndex = 0
			if maxSpex != -1:
				specialization = specializations[maxIndex]
				while pubIndex < len(publicationArray):
					paperspecList = publicationArray[pubIndex][4]
					if not specialization in paperspecList:
						print publicationArray[pubIndex], "deleted!"
						del publicationArray[pubIndex]
					else:
						pubIndex += 1
			else:
				print "maxSpex:", maxSpex, "and len(publicationArray):", len(publicationArray)

			print "Specialization after: " + specialization
			print "publicationArray After:", publicationArray

			# with open('test_publicationArray', 'wb') as f:
			# 	f.write(str(publicationArray))
			# f.closed

			publicationsSorted = []

			for publication in publicationArray:
				keywords = publication[3]

				for keyword in keywords:
					keywordIndex = -1
					for publicationSortedIndex in range(len(publicationsSorted)):
						if publicationsSorted[publicationSortedIndex][0] == keyword:
							keywordIndex = publicationSortedIndex
							break
					if keywordIndex != -1:
						publicationsSorted[keywordIndex][1] += 1
						publicationsSorted[keywordIndex][2].append(publication)
					else:
						publicationsSorted.append([keyword, 1, [publication]])

			publicationsSorted.sort(key=itemgetter(1), reverse=True)

			publicationsPicked = []

			print "publicationsSorted:", publicationsSorted

			# with open('test_publicationsSorted', 'wb') as f:
			# 	f.write(str(publicationsSorted))
			# f.closed

			if len(locations) != 0:
				location = locations[0]
			else:
				location = ""
			
			if len(affiliations) != 0:
				affiliation = affiliations[0]
			else:
				affiliation = ""

			# Return the result array.
			returnValue = [firstName, lastName, email, specialization, ideasURL, affiliation, location, homepage]
			affiliationReturnValue = [firstName, lastName, email]

			for affiliationIndex in range(len(affiliations)):
				affiliationReturnValue.append(affiliations[affiliationIndex])
				if affiliationIndex < len(locations):
					location = locations[affiliationIndex]
				else:
					location = ""
				affiliationReturnValue.append(location)

			for publicationSorted in publicationsSorted:
				if len(publicationsPicked) < 7:
					publicationItemTitle = publicationSorted[2][0][0]

					publicationKeywordIndex = 0

					while publicationItemTitle in publicationsPicked and publicationKeywordIndex < len(publicationSorted[2]) - 1:

						publicationKeywordIndex += 1

						publicationItemTitle = publicationSorted[2][publicationKeywordIndex][0]

					if publicationItemTitle in publicationsPicked:
						continue
					else:
						publicationsPicked.append(publicationSorted[2][publicationKeywordIndex][0])

						returnValue.append(publicationSorted[2][publicationKeywordIndex][0])
						returnValue.append(publicationSorted[2][publicationKeywordIndex][1])
						returnValue.append(publicationSorted[2][publicationKeywordIndex][2])
						returnValue.append(publicationSorted[0])
				else:
					break
			
			print "returnValue:", returnValue
			print "affiliationReturnValue:", affiliationReturnValue

			# foundTheLastSubject = False
			# if firstName == endFirstname and lastName == endLastname:
			# 	foundTheLastSubject = True

			return returnValue, affiliationReturnValue

			# except:
			# 	ideasURL = raw_input()
			# 	ideasSoup = soupStructure(ideasURL)

# Define a funtion which extracts list of authors from each category pages of ideas.repec.org.
def econPapersAuthorListExtractor(writer, writerAffiliations, specialization, ideasURL):

	# Retrieve the url html page content and convert it into BeautifulSoup structure.
	ideasSoup = soupStructure(ideasURL)

	# If the content of the page is returned in BeautifulSoup structure:
	while ideasSoup == '':
		ideasURL = raw_input()
		ideasSoup = soupStructure(ideasURL)

	# while True:
	# 	try:

	# # Set if startFirstname is observed.
	# startFirstnameObserved = False

	# # Set if startLastname is observed.
	# startLastnameObserved = False

	# Find the main tables list.
	tablesList = ideasSoup.body.findAll('table')

	for tableIndex in range(2, len(tablesList)):

		# Find the main table.
		mainTable = tablesList[tableIndex]

		# If there is a main table:
		if mainTable != None:

			# Find all a tags inside the main table.
			aTags = mainTable.findAll('a')

			for i in range(len(aTags)):

				# if aTags[i].find(text=re.compile(startFirstname)) != None:
				#     startFirstnameObserved = True

				#     if aTags[i].find(text=re.compile(startLastname)) != None:
				#         startLastnameObserved = True

				# If there is a question mark after the hyperlinked name, it means there is something wrong with it, so it's better to just ignore it.
				# if aTags[i].parent.find(text=re.compile('.*[?].*')) == None and startFirstnameObserved and startLastnameObserved:
				if aTags[i].parent.find(text=re.compile('.*[?].*')) == None:

					try:
						# Define an array as the return variable.
						returnVariable, affiliationReturnValue = econPapersProfileExtractor('https://ideas.repec.org' + aTags[i]['href'], specialization)

						writer.writerow(returnVariable)
						writerAffiliations.writerow(affiliationReturnValue)
						
						print str(returnVariable)
					except:
						pass
					# if foundTheLastSubject:
					# 	return foundTheLastSubject

		# 	break
		# except:
		# 	ideasURL = raw_input()
		# 	ideasSoup = soupStructure(ideasURL)
	return False

# Define a funtion which extracts list of categories on ideas.repec.org.
def econPapersCategoriesExtractor(ideasURL, startSpecialization, endSpecialization):

	with open('Ideas_Repec_Dataset.csv', 'wb') as fw:
		writer = csv.writer(fw)

		with open('Ideas_Repec_Affiliations.csv', 'wb') as fwAffiliations:
			writerAffiliations = csv.writer(fwAffiliations)

			resultRow = ['firstName', 'lastName', 'email', 'specialization', 'EconPapers Profile', 'affiliation', 'location', 'homepage', 'publication1', 'publicationYear1', 'citation1', 'firstKeyword1', 'publication2', 'publicationYear2', 'citation2', 'firstKeyword2', 'publication3', 'publicationYear3', 'citation3', 'firstKeyword3', 'publication4', 'publicationYear4', 'citation4', 'firstKeyword4', 'publication5', 'publicationYear5', 'citation5', 'firstKeyword5', 'publication6', 'publicationYear6', 'citation6', 'firstKeyword6', 'publication7', 'publicationYear7', 'citation7', 'firstKeyword7']
			writer.writerow(resultRow)

			resultRowAffiliations = ['firstName', 'lastName', 'email', 'affiliation1', 'location1', 'affiliation2', 'location2', 'affiliation3', 'location3', 'affiliation4', 'location4', 'affiliation5', 'location5', 'affiliation6', 'location6', 'affiliation7', 'location7']
			writerAffiliations.writerow(resultRowAffiliations)

			ideasSoup = soupStructure(ideasURL)

			# If the content of the page is returned in BeautifulSoup structure:
			if ideasSoup != '':

				# Find the main list.
				mainList = ideasSoup.body.find(text=re.compile('.*Accounting & Auditing.*')).parent.parent

				# If there is a main list:
				if mainList != None:

					# Set if the startSpecialization is observed.
					startSpecializationObserved = False

					# Find all li tags inside the main list.
					liTags = mainList.findAll('li')

					for i in range(len(liTags)):

						# Find the hyperlink tag inside the list item.
						aTag = liTags[i].find('a')

						specialization = aTag.nextSibling[1:]

						print str(specialization)

						if specialization == startSpecialization:
							startSpecializationObserved = True

						if specialization != "All new papers" and  specialization != "German Papers" and startSpecializationObserved:

							econPapersAuthorListExtractor(writer, writerAffiliations, specialization, 'https://ideas.repec.org' + aTag['href'])

							# if foundTheLastSubject:
							# 	return
						if specialization == endSpecialization:
							return

# # Connect to Tor
# connectTor()

# Rum the main program.
econPapersCategoriesExtractor('https://ideas.repec.org/i/e.html', 'Resource Economics', 'Urban & Real Estate Economics')
