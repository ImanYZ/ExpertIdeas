# Import the required libraries.
import sys
import os

from datetime import datetime, date, time
import re
import time
import random
from random import randint
import glob

import base64

import ucsv as csv
import unicodedata

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Define the log file:
try:
    log_file = open('log_file.txt', mode = 'w')
except:
    print ("Unable to open the log file.")

# Print out the error message to the both standard output and log_file.
def print_log(message):
    try:
        log_file.write(str(datetime.now()) + ': ' + message + '\n')
        print (str(datetime.now()) + ': ' + message)
    except:
        print ("Unable to write into the log file.")

# Expand definition of find_element_by_id to return False in case there is no element.
def exists_by_id(parentObj, idText, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        return parentObj.find_element_by_id(idText)
    except:
        print_log("Element by id = '" + idText + "' not found.")
        if ignoreNone:
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exists_by_id(parentObj, idText, ignoreNone, waitToFind, triesNum + 1)
            return None
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exists_by_id(parentObj, idText, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_element_by_name to return False in case there is no element.
def exists_by_name(parentObj, name, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        return parentObj.find_element_by_name(name)
    except:
        print_log("Element by name = '" + name + "' not found.")
        if (ignoreNone):
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exists_by_name(parentObj, name, ignoreNone, waitToFind, triesNum + 1)
            return None
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exists_by_name(parentObj, name, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_element_by_tag_name to return False in case there is no element.
def exists_by_tag_name(parentObj, tagName, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        return parentObj.find_element_by_tag_name(tagName)
    except:
        print_log("Element by tag name = '" + tagName + "' not found.")
        if (ignoreNone):
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exists_by_tag_name(parentObj, tagName, ignoreNone, waitToFind, triesNum + 1)
            return None
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exists_by_tag_name(parentObj, tagName, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_element_by_css_selector to return False in case there is no element.
def exists_by_css_selector(parentObj, css_selector, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        return parentObj.find_element_by_css_selector(css_selector)
    except:
        print_log("Element by CSS selector = '" + css_selector + "' not found.")
        if (ignoreNone):
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exists_by_css_selector(parentObj, css_selector, ignoreNone, waitToFind, triesNum + 1)
            return None
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exists_by_css_selector(parentObj, css_selector, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_element_by_xpath to return False in case there is no element.
def exists_by_xpath(parentObj, xpath, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        return parentObj.find_element_by_xpath(xpath)
    except:
        print_log("Element by xpath = '" + xpath + "' not found.")
        if (ignoreNone):
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exists_by_xpath(parentObj, xpath, ignoreNone, waitToFind, triesNum + 1)
            return None
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exists_by_xpath(parentObj, xpath, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_elements_by_tag_name to return False in case there is no element.
def exist_all_by_name(parentObj, name, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        elements = parentObj.find_elements_by_name(name)
        # If lisList is not found:
        if len(elements) == 0:
            print_log("Elements by name = '" + name + "' not found.")
            if (ignoreNone):
                if waitToFind and triesNum < 10:
                    time.sleep(1)
                    return exist_all_by_name(parentObj, name, ignoreNone, waitToFind, triesNum + 1)
                return None
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exist_all_by_name(parentObj, name, ignoreNone, waitToFind, triesNum + 1)
            sys.exit()
        return elements
    except:
        print_log("Element by name = '" + name + "' not found.")
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exist_all_by_name(parentObj, name, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_elements_by_tag_name to return False in case there is no element.
def exist_all_by_tag_name(parentObj, tagName, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        elements = parentObj.find_elements_by_tag_name(tagName)
        # If lisList is not found:
        if len(elements) == 0:
            print_log("Elements by tag name = '" + tagName + "' not found.")
            if (ignoreNone):
                if waitToFind and triesNum < 10:
                    time.sleep(1)
                    return exist_all_by_tag_name(parentObj, tagName, ignoreNone, waitToFind, triesNum + 1)
                return None
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exist_all_by_tag_name(parentObj, tagName, ignoreNone, waitToFind, triesNum + 1)
            sys.exit()
        return elements
    except:
        print_log("Element by tag name = '" + tagName + "' not found.")
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exist_all_by_tag_name(parentObj, tagName, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_elements_by_css_selector to return False in case there is no element.
def exist_all_by_css_selector(parentObj, css_selector, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        elements = parentObj.find_elements_by_css_selector(css_selector)
        # If lisList is not found:
        if len(elements) == 0:
            print_log("Elements by CSS selector = '" + css_selector + "' not found.")
            if (ignoreNone):
                if waitToFind and triesNum < 10:
                    time.sleep(1)
                    return exist_all_by_css_selector(parentObj, css_selector, ignoreNone, waitToFind, triesNum + 1)
                return None
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exist_all_by_css_selector(parentObj, css_selector, ignoreNone, waitToFind, triesNum + 1)
            sys.exit()
        return elements
    except:
        print_log("Element by CSS selector = '" + css_selector + "' not found.")
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exist_all_by_css_selector(parentObj, css_selector, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()

# Expand definition of find_elements_by_xpath to return False in case there is no element.
def exist_all_by_xpath(parentObj, xpath, ignoreNone = False, waitToFind = False, triesNum = 0):
    try:
        elements = parentObj.find_elements_by_xpath(xpath)
        # If lisList is not found:
        if len(elements) == 0:
            print_log("Elements by xpath = '" + xpath + "' not found.")
            if (ignoreNone):
                if waitToFind and triesNum < 10:
                    time.sleep(1)
                    return exist_all_by_xpath(parentObj, xpath, ignoreNone, waitToFind, triesNum + 1)
                return None
            if waitToFind and triesNum < 10:
                time.sleep(1)
                return exist_all_by_xpath(parentObj, xpath, ignoreNone, waitToFind, triesNum + 1)
            sys.exit()
        return elements
    except:
        print_log("Element by xpath = '" + xpath + "' not found.")
        if waitToFind and triesNum < 10:
            time.sleep(1)
            return exist_all_by_xpath(parentObj, xpath, ignoreNone, waitToFind, triesNum + 1)
        sys.exit()


# Find the element and extract its text.
def find_and_extract(parentObj, objName, xpath):
    # Find the element.
    ObjTag = exists_by_xpath(parentObj, xpath, True)

    # Find the text of the element.
    if ObjTag != None:
        objText = ObjTag.text
    else:
        objText = ""

    print_log(objName + ": " + objText)

    return objText

def find_by_ID_and_click(htmlObjID, browser):

    htmlObj = exists_by_id(browser, htmlObjID, ignoreNone = True, waitToFind = False)
    actionChains = ActionChains(browser)
    while not htmlObj.is_displayed():
        actionChains.send_keys(Keys.TAB).perform()
        htmlObj = exists_by_id(browser, htmlObjID, ignoreNone = True, waitToFind = False)

    click_and_wait(htmlObj, browser)

def hover_and_click(htmlObj, browser):

    actionChains = ActionChains(browser)
    actionChains.move_to_element(htmlObj).perform()

    browser.execute_script("arguments[0].setAttribute('style', 'visibility:visible;');", htmlObj)

    htmlObj.click()

    # bodyObj = exists_by_tag_name(browser, 'body', ignoreNone = False, waitToFind = True)
    # location = htmlObj.location

    # browser.execute_script("var e = new jQuery.Event('click'); e.pageX = " + str(location['x']) + "; e.pageY = " + str(location['y']) + "; $('body').trigger(e);")

    # actionChains.move_to_element_with_offset(bodyObj, location['x'], location['y'])
    # actionChains.click()
    # actionChains.perform()

# Click the element and wait for a random number between 1 and 10 seconds.
def click_and_wait(htmlObj, browser):

    hover_and_click(htmlObj, browser)

    # Random float x, 1.0 <= x < 10.0
    randomTimePeriod = random.uniform(1, 4)

    print_log("Wait time: " + str(randomTimePeriod) + " seconds")

    time.sleep(randomTimePeriod)

# Go back to the previous page and wait for a random number between 1 and 10 seconds.
def back_and_wait(browser):

    browser.back()

    # Random float x, 1.0 <= x < 10.0
    randomTimePeriod = random.uniform(1, 4)

    print_log("Wait time: " + str(randomTimePeriod) + " seconds")

    time.sleep(randomTimePeriod)

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


# Main program:


with open('Repec_Author_Rankings.csv', 'wb') as fw:
    writer = csv.writer(fw)

    pubResultRow = ['Ranking Class', 'Rank', 'Name', 'RePEc URL', 'Affiliation', 'Score']
    writer.writerow(pubResultRow)

    firefox_profile = webdriver.FirefoxProfile()
    browser = webdriver.Firefox(firefox_profile)

    # Retrieve the content of the start page.
    # browser.get('https://bftrain.miserver.it.umich.edu')
    browser.get('https://ideas.repec.org/top/top.person.all.html')
    browser.maximize_window()

    top5PercentTboday = exists_by_xpath(browser, '//*[@id="content-block"]/table/tbody', ignoreNone = False, waitToFind = True)
    top5PercentTrs = exist_all_by_tag_name(top5PercentTboday, 'tr', ignoreNone = False, waitToFind = True)

    for top5PercentTr in top5PercentTrs:
        pubResultRow = []

        pubResultRow.append("Top 5%")

        top5PercentTds = exist_all_by_tag_name(top5PercentTr, 'td', ignoreNone = False, waitToFind = True)

        pubResultRow.append(top5PercentTds[0].text)

        authorNameTag = exists_by_tag_name(top5PercentTds[1], 'a', ignoreNone = False, waitToFind = True)
        pubResultRow.append(authorNameTag.text)
        pubResultRow.append(authorNameTag.get_attribute("href"))

        authorAffiliationTag = exists_by_tag_name(top5PercentTds[1], 'p', ignoreNone = False, waitToFind = True)
        pubResultRow.append(authorAffiliationTag.text)

        pubResultRow.append(top5PercentTds[2].text)

        writer.writerow(pubResultRow)


    for index in range(10, 478):
        pubResultRow = []

        pubResultRow.append("Top 6%")

        authorNameTag = exists_by_xpath(browser, '//*[@id="content-block"]/a[' + str(index) + ']', ignoreNone = False, waitToFind = True)
        pubResultRow.append('')
        pubResultRow.append(authorNameTag.text)
        pubResultRow.append(authorNameTag.get_attribute("href"))
        pubResultRow.append('')
        pubResultRow.append('')

        writer.writerow(pubResultRow)

    for index in range(478, 947):
        pubResultRow = []

        pubResultRow.append("Top 7%")

        authorNameTag = exists_by_xpath(browser, '//*[@id="content-block"]/a[' + str(index) + ']', ignoreNone = False, waitToFind = True)
        pubResultRow.append('')
        pubResultRow.append(authorNameTag.text)
        pubResultRow.append(authorNameTag.get_attribute("href"))
        pubResultRow.append('')
        pubResultRow.append('')

        writer.writerow(pubResultRow)

    for index in range(947, 1416):
        pubResultRow = []

        pubResultRow.append("Top 8%")

        authorNameTag = exists_by_xpath(browser, '//*[@id="content-block"]/a[' + str(index) + ']', ignoreNone = False, waitToFind = True)
        pubResultRow.append('')
        pubResultRow.append(authorNameTag.text)
        pubResultRow.append(authorNameTag.get_attribute("href"))
        pubResultRow.append('')
        pubResultRow.append('')

        writer.writerow(pubResultRow)

    for index in range(1416, 1885):
        pubResultRow = []

        pubResultRow.append("Top 9%")

        authorNameTag = exists_by_xpath(browser, '//*[@id="content-block"]/a[' + str(index) + ']', ignoreNone = False, waitToFind = True)
        pubResultRow.append('')
        pubResultRow.append(authorNameTag.text)
        pubResultRow.append(authorNameTag.get_attribute("href"))
        pubResultRow.append('')
        pubResultRow.append('')

        writer.writerow(pubResultRow)

    for index in range(1885, 2353):
        pubResultRow = []

        pubResultRow.append("Top 10%")

        authorNameTag = exists_by_xpath(browser, '//*[@id="content-block"]/a[' + str(index) + ']', ignoreNone = False, waitToFind = True)
        pubResultRow.append('')
        pubResultRow.append(authorNameTag.text)
        pubResultRow.append(authorNameTag.get_attribute("href"))
        pubResultRow.append('')
        pubResultRow.append('')

        writer.writerow(pubResultRow)


browser.quit();
