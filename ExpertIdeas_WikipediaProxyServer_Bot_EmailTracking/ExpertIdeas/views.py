# -*- coding: utf-8 -*-

# Python first
# Djnago second
# My apps
# Local directory

import sys
import os

import datetime
from datetime import timedelta
import time
import json
import unicodedata
import random
import re

from operator import itemgetter

# Import requests library.
import requests
import urllib
from bs4 import BeautifulSoup
import codecs
import ucsv as csv
from urlparse import urljoin
import iso8601

from pytz import timezone as timezoneClass

from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, render_to_response, RequestContext, HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from django.contrib.sessions.backends.db import SessionStore

from .models import Wikipage
from .models import Expert
from .models import Publication
from .models import Expertwikipub
from .models import Expertwikipubreferee
from .models import Expertkeywords
from .models import SimilarExpert
from .models import StudyStatistic
from .models import Publicationkeyword
from .models import Locationtimezone

from .forms import ExpertForm

from ExpertIdeasBot import postCommentstoTalkpages

# from .forms import WikiPageForm


def num(stringObj):
    try:
        return int(stringObj)
    except ValueError:
        try:
            return float(stringObj)
        except ValueError:
            return int(stringObj.replace(',', ''))


def get_ip(request):
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        ip = ""
    return ip


def findCoordinatesZone(location, lat, lng, timeZoneStr):
    if lat is None or lng is None:
        randNum = random.uniform(1, 10)
        time.sleep(randNum)

        try:
            place, (lat, lng) = settings.GEOCODEROBJ.geocode(location)
        except Exception, e:
            raise Exception('Error is: ' + str(e) + " location: " + str(location))

    if timeZoneStr == "" or timeZoneStr is None:
        try:
            timeZoneStr = settings.TZWHEREOBJ.tzNameAt(lat, lng)
        except Exception, e:
            raise Exception('Error is: ' + str(e) + " timeZoneStr: " + str(timeZoneStr))

        if timeZoneStr is None or timeZoneStr == "None":
            timeZoneStr = ""

    return lat, lng, timeZoneStr


def findTimeZoneObj(location):
    timeZoneObj = None
    timeZoneStr = ""
    lat = None
    lng = None
    if location != "":
        locationtimezones = Locationtimezone.objects.filter(location=location)
        if len(locationtimezones) != 0:
            timeZoneStr = locationtimezones[0].timezone
            lat = locationtimezones[0].latitude
            lng = locationtimezones[0].longitude

            lat, lng, timeZoneStr = findCoordinatesZone(location, lat, lng, timeZoneStr)

            if (timeZoneStr != locationtimezones[0].timezone or lat != locationtimezones[0].latitude or
                    lng != locationtimezones[0].longitude):
                locationtimezones[0].timezone = timeZoneStr
                locationtimezones[0].latitude = lat
                locationtimezones[0].longitude = lng
                locationtimezones[0].save()

        else:
            lat, lng, timeZoneStr = findCoordinatesZone(location, lat, lng, timeZoneStr)

            locationtimezone = Locationtimezone(location=location, timezone=timeZoneStr, latitude=lat,
                                                longitude=lng)
            locationtimezone.save()

        if timeZoneStr != "":
            timeZoneObj = timezoneClass(timeZoneStr)
    return lat, lng, timeZoneObj


def findCurrentTime(location):
    now_time = ""

    lat, lng, timeZoneObj = findTimeZoneObj(location)
    if timeZoneObj is not None:
        timeComplete = datetime.datetime.now(timeZoneObj)
        now_time = str(timeComplete.hour) + ":" + str(timeComplete.minute)

    return now_time


def findLocalTime(location, timeObj):
    timeComplete = ""

    lat, lng, timeZoneObj = findTimeZoneObj(location)
    if timeZoneObj is not None:
        timeComplete = timeObj.astimezone(timeZoneObj)

    return timeComplete


def emaillist(request):

    # if request.user.is_authenticated():
    #     # Do something for logged-in users.
    # else:
    #     # Do something for anonymous users.   # form = WikiPageForm(request.POST or None)

    fromAuthor = 1
    toAuthor = 10000

    pageType = ''
    if request.method == 'GET':
        if 'key' in request.GET and request.GET['key'] != '':
            session_key = request.GET['key']

            if session_key != "":
                s = SessionStore(session_key=session_key)
                s['progressPercent'] == 0.0
                s.save()

        if 'pageType' in request.GET and request.GET['pageType'] != '':
            pageType = request.GET['pageType']
        else:
            pageType = 'Phase_1_EmailList'

        if 'version' in request.GET and request.GET['version'] != '':
            version = num(request.GET['version'])
        else:
            version = 0

        if 'FromNumber' in request.GET and request.GET['FromNumber'] != '':
            fromAuthor = num(request.GET['FromNumber'])
            if fromAuthor <= 0:
                fromAuthor = 1
        if 'ToNumber' in request.GET and request.GET['ToNumber'] != '':
            toAuthor = num(request.GET['ToNumber'])
            if toAuthor < fromAuthor:
                toAuthor = fromAuthor

        if (pageType == 'Phase_1_EmailList' or pageType == 'Phase_1_Waiting' or
                pageType == 'Phase_1_Not_Interested' or pageType == 'Phase_1_Interested'):
            studyPhase = "Phase1"

        elif (pageType == 'Phase_2_EmailList' or pageType == 'Phase_2_Waiting' or
                pageType == 'Phase_2_Not_Interested' or pageType == 'Phase_2_ApprovalPending' or
                pageType == 'Phase_2_Approved'):
            studyPhase = "Phase2"

        elif (pageType == 'Phase_3_EmailList' or pageType == 'Phase_3_Waiting' or pageType == 'Phase_3_Interested'):
            studyPhase = "Phase3"

    expertCounter = 1

    papersExpertsWikiPages = []

    allExperts = Expert.objects.all()

    expertNum = 0.00

    for expert in allExperts:
        expertNum += 1.00

        if expertCounter >= fromAuthor and expertCounter <= toAuthor:
            expertwikipages = expert.expertwikipub_set.all()
            expertPk = expert.pk
            firstname = expert.firstname
            expertName = expert.name
            expertTitle = expert.title
            phase1 = expert.phase1
            phase2 = expert.phase2
            phase3 = expert.phase3
            interested = expert.returned
            inSpecialtyArea = expert.inspecialtyarea
            indiscipline = expert.indiscipline
            citedpublication = expert.citedpublication
            highviewspast90days = expert.highviewspast90days
            email = expert.email
            location = expert.location
            school = expert.school
            citations = expert.citations
            expertDomain = expert.domain
            expertSpecialization = expert.specialization

            returned = expert.returned
            withdrawal = expert.withdrawal
            email1_opened = expert.email1_opened
            email2_opened = expert.email2_opened
            email3_opened = expert.email3_opened
            emailSent = expert.emailSent
            emailCount = expert.emailCount
            emailCommunication = expert.emailCommunication
            article_clicked = expert.article_clicked
            talkpage_clicked = expert.talkpage_clicked
            post_clicked = expert.post_clicked
            tutorial_clicked = expert.tutorial_clicked

            study_version = expert.study_version
            private_first = expert.private_first
            relevance_factor = expert.relevance_factor
            likely_to_cite = expert.likely_to_cite
            may_include_reference = expert.may_include_reference
            might_refer_to = expert.might_refer_to
            relevant_to_research = expert.relevant_to_research
            within_area = expert.within_area
            on_expertise_topic = expert.on_expertise_topic
            especially_popular = expert.especially_popular
            highly_visible = expert.highly_visible
            highly_popular = expert.highly_popular

            updated = expert.updated

            commentedOrRated = False

            emailSentToExpert = False

            if (email is not None and email != '' and expertSpecialization is not None and expertSpecialization != "" and
                    study_version == version and not indiscipline):

                for expertwikipage in expertwikipages:
                    if ((expertwikipage.rating is not None and expertwikipage.rating != "") or
                            (expertwikipage.comment != '' and expertwikipage.comment is not None)):
                        commentedOrRated = True

                # In case we wanted to include experts with no specialization:
                if expertSpecialization is None or expertSpecialization == "":
                    subject = expertDomain + " Articles in Wikipedia"
                else:
                    subject = expertSpecialization + " Articles in Wikipedia"

                if (pageType == 'Phase_1_EmailList' or pageType == 'Phase_1_Waiting' or
                    pageType == 'Phase_1_Not_Interested' or pageType == 'Phase_1_Interested'):
                    if (((phase1 == True and pageType == 'Phase_1_EmailList' and interested == False) and withdrawal == False and emailCount < 5 and ( emailCount == 0 or expert.emailSent + timedelta(weeks=2) <= timezone.now() ))
                        or ((phase1 == True and pageType == 'Phase_1_Waiting' and interested == False) and commentedOrRated == False and withdrawal == False and (emailCount < 5 and ( emailCount != 0 and expert.emailSent + timedelta(weeks=2) > timezone.now() )))
                        or (phase1 == True and pageType == 'Phase_1_Not_Interested' and interested == False and commentedOrRated == False and withdrawal == True)
                        or (phase1 == True and pageType == 'Phase_1_Interested' and interested == True and withdrawal == False)):

                        if pageType == 'Phase_1_EmailList':
                            now_time = findCurrentTime(location)
                        else:
                            now_time = ""

                        papersExpertsWikiPages.append({
                            'expertId': expertPk,
                            'expertNumber': expertCounter,
                            'firstname': smart_unicode(firstname),
                            'expertName': smart_unicode(expertName),
                            'inSpecialtyArea': inSpecialtyArea,
                            'highviewspast90days': highviewspast90days,
                            'citedpublication': citedpublication,
                            'relevance_factor': relevance_factor,
                            'likely_to_cite': likely_to_cite,
                            'may_include_reference': may_include_reference,
                            'might_refer_to': might_refer_to,
                            'relevant_to_research': relevant_to_research,
                            'within_area': within_area,
                            'on_expertise_topic': on_expertise_topic,
                            'private_first': private_first,
                            'especially_popular': especially_popular,
                            'highly_visible': highly_visible,
                            'highly_popular': highly_popular,
                            'email': email,
                            'location':location,
                            'school':school,
                            'now_time':now_time,
                            'expertTitle': expertTitle,
                            'subject': subject,
                            'emailSent': emailSent,
                            'emailCount': emailCount,
                            'email1_opened': email1_opened,
                            'updated': updated,
                            'citations': citations,
                            'domain': expertDomain,
                            'specialization': expertSpecialization,
                            'emailCommunication': emailCommunication,
                            'withdrawal': withdrawal,
                            'returned': returned, })
                        # expertCounter = expertCounter + 1
                        emailSentToExpert = True
                elif (pageType == 'Phase_2_EmailList' or pageType == 'Phase_2_Waiting'
                    or pageType == 'Phase_2_Not_Interested' or pageType == 'Phase_2_ApprovalPending'
                    or pageType == 'Phase_2_Approved'):
                    if (((phase2 == True and pageType == 'Phase_2_EmailList') and commentedOrRated == False and withdrawal == False and emailCount < 5 and ( emailCount == 0 or expert.emailSent + timedelta(weeks=2) <= timezone.now() ))
                        or ((phase2 == True and pageType == 'Phase_2_Waiting') and commentedOrRated == False and withdrawal == False and ( emailCount != 0 and expert.emailSent + timedelta(weeks=2) > timezone.now() ))
                        or ((phase2 == True and pageType == 'Phase_2_Not_Interested') and commentedOrRated == False and withdrawal == True)
                        or (phase2 == True and pageType == 'Phase_2_ApprovalPending' and commentedOrRated == True and withdrawal == False)
                        or (phase2 == True and pageType == 'Phase_2_Approved' and commentedOrRated == True and withdrawal == False)):

                        if pageType == 'Phase_2_EmailList' or pageType == 'Phase_2_ApprovalPending':
                            now_time = findCurrentTime(location)
                        else:
                            now_time = ""

                        expertwikipubArray = []

                        for expertwikipage in expertwikipages:
                            comment = expertwikipage.comment
                            if ((pageType != 'Phase_2_ApprovalPending' and pageType != 'Phase_2_Approved')
                                or (pageType == 'Phase_2_ApprovalPending' and expertwikipage.submittedtotalkpage == False and comment is not None and comment != '')
                                or (pageType == 'Phase_2_Approved' and (expertwikipage.submittedtotalkpage == True or comment is None or comment == ''))):
                                
                                expertwikipubrefereesNum = len(expertwikipage.expertwikipubreferee_set.all())

                                expertwikipagePk = expertwikipage.pk
                                last_name_ocurances = expertwikipage.last_name_ocurances
                                link_clicked = expertwikipage.link_clicked
                                rating = expertwikipage.rating
                                approvedbywikipedians = expertwikipage.approvedbywikipedians
                                rejectedbywikipedians = expertwikipage.rejectedbywikipedians
                                publication = expertwikipage.publication
                                wikipage = expertwikipage.wikipage

                                publicationTitle = publication.title
                                publicationCitations = publication.citations
                                publicationUrl = publication.url

                                wikipageTitle = wikipage.title
                                wikipageUrl = wikipage.url
                                wikipageEdit_protection_level = wikipage.edit_protection_level
                                wikipagepage_length = wikipage.page_length
                                wikipageWatchers = wikipage.watchers
                                wikipageLinks_to_this_page = wikipage.links_to_this_page
                                wikipageViews_last_90_days = wikipage.views_last_90_days

                                expertwikipubArray.append({
                                    'expertwikipagePk': expertwikipagePk,
                                    'last_name_ocurances': last_name_ocurances,
                                    'link_clicked': link_clicked,
                                    'rating': rating,
                                    'comment': smart_unicode(comment),
                                    'expertwikipubrefereesNum': expertwikipubrefereesNum,
                                    'approvedbywikipedians': approvedbywikipedians,
                                    'rejectedbywikipedians': rejectedbywikipedians,
                                    'publicationTitle': smart_unicode(publicationTitle),
                                    'publicationCitations': publicationCitations,
                                    'publicationUrl': publicationUrl,
                                    'wikipageTitle': smart_unicode(wikipageTitle),
                                    'wikipageUrl': wikipageUrl,
                                    'wikipageEdit_protection_level': wikipageEdit_protection_level,
                                    'wikipageViews_last_90_days': wikipageViews_last_90_days, })

                        if len(expertwikipubArray) > 0:
                            papersExpertsWikiPages.append({
                                'expertId': expertPk,
                                'expertNumber': expertCounter,
                                'firstname': smart_unicode(firstname),
                                'expertName': smart_unicode(expertName),
                                'inSpecialtyArea': inSpecialtyArea,
                                'highviewspast90days': highviewspast90days,
                                'citedpublication': citedpublication,
                                'relevance_factor': relevance_factor,
                                'likely_to_cite': likely_to_cite,
                                'may_include_reference': may_include_reference,
                                'might_refer_to': might_refer_to,
                                'relevant_to_research': relevant_to_research,
                                'within_area': within_area,
                                'on_expertise_topic': on_expertise_topic,
                                'private_first': private_first,
                                'especially_popular': especially_popular,
                                'highly_visible': highly_visible,
                                'highly_popular': highly_popular,
                                'email': email,
                                'location': location,
                                'school': school,
                                'now_time': now_time,
                                'expertTitle': expertTitle,
                                'subject': subject,
                                'emailSent': emailSent,
                                'emailCount': emailCount,
                                'email2_opened': email2_opened,
                                'updated': updated,
                                'citations': citations,
                                'domain': expertDomain,
                                'specialization': expertSpecialization,
                                'withdrawal': withdrawal,
                                'returned': returned,
                                'emailCommunication': emailCommunication,
                                'expertwikipubArray': expertwikipubArray, })

                            # expertCounter = expertCounter + 1
                            emailSentToExpert = True
                elif (pageType == 'Phase_3_EmailList' or pageType == 'Phase_3_Waiting' or pageType == 'Phase_3_Interested'):
                    if (((phase3 == True and pageType == 'Phase_3_EmailList') and article_clicked == False and talkpage_clicked == False and post_clicked == False and tutorial_clicked == False  and withdrawal == False and email3_opened == False and emailCount < 1 and ( emailCount == 0 or expert.emailSent + timedelta(weeks=2) <= timezone.now() ))
                        or ((phase3 == True and pageType == 'Phase_3_Waiting') and article_clicked == False and talkpage_clicked == False and post_clicked == False and tutorial_clicked == False and withdrawal == False and (email3_opened == True or ( emailCount != 0 and expert.emailSent + timedelta(weeks=2) > timezone.now() )))
                        or (phase3 == True and pageType == 'Phase_3_Interested' and (article_clicked == True or talkpage_clicked == True or post_clicked == True or tutorial_clicked == True) and withdrawal == False)):

                        if pageType == 'Phase_3_EmailList':
                            now_time = findCurrentTime(location)
                        else:
                            now_time = ""

                        expertwikipubArray = []

                        for expertwikipage in expertwikipages:
                            if expertwikipage.submittedtotalkpage == True:

                                expertwikipubrefereesNum = len(expertwikipage.expertwikipubreferee_set.all())

                                comment = expertwikipage.comment
                                expertwikipagePk = expertwikipage.pk
                                last_name_ocurances = expertwikipage.last_name_ocurances
                                link_clicked = expertwikipage.link_clicked
                                rating = expertwikipage.rating
                                approvedbywikipedians = expertwikipage.approvedbywikipedians
                                rejectedbywikipedians = expertwikipage.rejectedbywikipedians
                                publication = expertwikipage.publication
                                wikipage = expertwikipage.wikipage

                                publicationTitle = publication.title
                                publicationCitations = publication.citations
                                publicationUrl = publication.url

                                wikipageTitle = wikipage.title
                                wikipageUrl = wikipage.url
                                wikipageEdit_protection_level = wikipage.edit_protection_level
                                wikipagepage_length = wikipage.page_length
                                wikipageWatchers = wikipage.watchers
                                wikipageLinks_to_this_page = wikipage.links_to_this_page
                                wikipageViews_last_90_days = wikipage.views_last_90_days

                                talkPageHyperlink, postHyperlink = findArticleTalkPageAndPost(expertName, wikipageTitle, wikipageUrl)

                                expertwikipubArray.append({
                                    'expertwikipagePk': expertwikipagePk,
                                    'last_name_ocurances': last_name_ocurances,
                                    'link_clicked': link_clicked,
                                    'rating': rating,
                                    'comment': smart_unicode(comment),
                                    'expertwikipubrefereesNum': expertwikipubrefereesNum,
                                    'approvedbywikipedians': approvedbywikipedians,
                                    'rejectedbywikipedians': rejectedbywikipedians,
                                    'publicationTitle': smart_unicode(publicationTitle),
                                    'publicationCitations': publicationCitations,
                                    'publicationUrl': publicationUrl,
                                    'wikipageTitle': smart_unicode(wikipageTitle),
                                    'wikipageUrl': wikipageUrl,
                                    'wikipageEdit_protection_level': wikipageEdit_protection_level,
                                    'talkPageHyperlink': talkPageHyperlink,
                                    'postHyperlink': postHyperlink,
                                    'wikipageEdit_protection_level': wikipageEdit_protection_level,
                                    'wikipageViews_last_90_days': wikipageViews_last_90_days, })

                        if len(expertwikipubArray) > 0:
                            papersExpertsWikiPages.append({
                                'expertId': expertPk,
                                'expertNumber': expertCounter,
                                'firstname': smart_unicode(firstname),
                                'expertName': smart_unicode(expertName),
                                'inSpecialtyArea': inSpecialtyArea,
                                'highviewspast90days': highviewspast90days,
                                'citedpublication': citedpublication,
                                'relevance_factor': relevance_factor,
                                'likely_to_cite': likely_to_cite,
                                'may_include_reference': may_include_reference,
                                'might_refer_to': might_refer_to,
                                'relevant_to_research': relevant_to_research,
                                'within_area': within_area,
                                'on_expertise_topic': on_expertise_topic,
                                'private_first': private_first,
                                'especially_popular': especially_popular,
                                'highly_visible': highly_visible,
                                'highly_popular': highly_popular,
                                'email': email,
                                'location':location,
                                'school':school,
                                'now_time':now_time,
                                'expertTitle': expertTitle,
                                'subject': subject,
                                'emailSent': emailSent,
                                'emailCount': emailCount,
                                'email2_opened': email2_opened,
                                'email3_opened': email2_opened,
                                'updated': updated,
                                'citations': citations,
                                'domain': expertDomain,
                                'specialization': expertSpecialization,
                                'withdrawal': withdrawal,
                                'returned': returned,
                                'emailCommunication': emailCommunication,
                                'article_clicked': article_clicked,
                                'talkpage_clicked': talkpage_clicked,
                                'post_clicked': post_clicked,
                                'tutorial_clicked': tutorial_clicked,
                                'expertwikipubArray': expertwikipubArray, })
                            # expertCounter = expertCounter + 1
                            emailSentToExpert = True

        elif expertCounter > toAuthor:
            expertCounter = toAuthor + 1
            break
        if expertCounter < fromAuthor or emailSentToExpert == True:
            expertCounter = expertCounter + 1

        if 'key' in request.GET and request.GET['key'] != '':
            s['progressPercent'] = str(expertNum / float(len(allExperts)))
            s.save()

    expertCounter = expertCounter - 1
    if expertCounter < fromAuthor:
        fromAuthor = 0
        toAuthor = 0
    elif expertCounter >= fromAuthor and expertCounter < toAuthor:
        toAuthor = expertCounter
    # form = ExpertForm(request.POST or None)
    # if form.is_valid():
    #   new_expert = form.save(commit=False)
    #   email = form.cleaned_data['email']
    #   name = form.cleaned_data['name']
    #   new_expert, created = Expert.objects.get_or_create(email=email, name=name)

    papersExpertsWikiPages = sorted(papersExpertsWikiPages, key=itemgetter('location'))
    papersExpertsWikiPages = sorted(papersExpertsWikiPages, key=itemgetter('now_time'))

    return render_to_response("Email_List.html",
        # {"form": form, "papersExpertsWikiPages": papersExpertsWikiPages, },
        {'studyPhase': studyPhase, 'version': version, 'pageType': pageType, "papersExpertsWikiPages": papersExpertsWikiPages, "fromAuthor": fromAuthor, "toAuthor": toAuthor, },
        context_instance=RequestContext(request))

def dateTimeStats(expert, location):
    latitude, longitude, timeZoneObj = findTimeZoneObj(location)

    emailSentH = -1
    email1SentH = -1
    email2SentH = -1
    email3SentH = -1
    email1OpenedTimeH = -1
    email2OpenedTimeH = -1
    email3OpenedTimeH = -1
    commentTimeH = -1

    emailSentW = -1
    email1SentW = -1
    email2SentW = -1
    email3SentW = -1
    email1OpenedTimeW = -1
    email2OpenedTimeW = -1
    email3OpenedTimeW = -1
    commentTimeW = -1

    emailSentYear = -1
    email1SentYear = -1
    email2SentYear = -1
    email3SentYear = -1
    email1OpenedYear = -1
    email2OpenedYear = -1
    email3OpenedYear = -1
    commentYear = -1

    emailSentMonth = -1
    email1SentMonth = -1
    email2SentMonth = -1
    email3SentMonth = -1
    email1OpenedMonth = -1
    email2OpenedMonth = -1
    email3OpenedMonth = -1
    commentMonth = -1

    emailSentDay = -1
    email1SentDay = -1
    email2SentDay = -1
    email3SentDay = -1
    email1OpenedDay = -1
    email2OpenedDay = -1
    email3OpenedDay = -1
    commentDay = -1

    if expert.emailSent is not None and expert.emailSent != expert.timestamp:
        emailSentTime = findLocalTime(location, expert.emailSent)
        if emailSentTime != "":
            emailSentH = emailSentTime.hour
            emailSentW = emailSentTime.weekday()
            emailSentYear = emailSentTime.year
            emailSentMonth = emailSentTime.month
            emailSentDay = emailSentTime.day
    if expert.email1Sent is not None and expert.email1Sent != expert.timestamp:
        email1SentTime = findLocalTime(location, expert.email1Sent)
        if email1SentTime != "":
            email1SentH = email1SentTime.hour
            email1SentW = email1SentTime.weekday()
            email1SentYear = email1SentTime.year
            email1SentMonth = email1SentTime.month
            email1SentDay = email1SentTime.day
    if expert.email2Sent is not None and expert.email2Sent != expert.timestamp:
        email2SentTime = findLocalTime(location, expert.email2Sent)
        if email2SentTime != "":
            email2SentH = email2SentTime.hour
            email2SentW = email2SentTime.weekday()
            email2SentYear = email2SentTime.year
            email2SentMonth = email2SentTime.month
            email2SentDay = email2SentTime.day
    if expert.email3Sent is not None and expert.email3Sent != expert.timestamp:
        email3SentTime = findLocalTime(location, expert.email3Sent)
        if email3SentTime != "":
            email3SentH = email3SentTime.hour
            email3SentW = email3SentTime.weekday()
            email3SentYear = email3SentTime.year
            email3SentMonth = email3SentTime.month
            email3SentDay = email3SentTime.day
    if expert.email1OpenedTime is not None and expert.email1OpenedTime != expert.timestamp:
        email1OpenedTime = findLocalTime(location, expert.email1OpenedTime)
        if email1OpenedTime != "":
            email1OpenedTimeH = email1OpenedTime.hour
            email1OpenedTimeW = email1OpenedTime.weekday()
            email1OpenedTimeYear = email1OpenedTime.year
            email1OpenedTimeMonth = email1OpenedTime.month
            email1OpenedTimeDay = email1OpenedTime.day
    if expert.email2OpenedTime is not None and expert.email2OpenedTime != expert.timestamp:
        email2OpenedTime = findLocalTime(location, expert.email2OpenedTime)
        if email2OpenedTime != "":
            email2OpenedTimeH = email2OpenedTime.hour
            email2OpenedTimeW = email2OpenedTime.weekday()
            email2OpenedTimeYear = email2OpenedTime.year
            email2OpenedTimeMonth = email2OpenedTime.month
            email2OpenedTimeDay = email2OpenedTime.day
    if expert.email3OpenedTime is not None and expert.email3OpenedTime != expert.timestamp:
        email3OpenedTime = findLocalTime(location, expert.email3OpenedTime)
        if email3OpenedTime != "":
            email3OpenedTimeH = email3OpenedTime.hour
            email3OpenedTimeW = email3OpenedTime.weekday()
            email3OpenedTimeYear = email3OpenedTime.year
            email3OpenedTimeMonth = email3OpenedTime.month
            email3OpenedTimeDay = email3OpenedTime.day
    if expert.commentTime is not None and expert.commentTime != expert.timestamp:
        commentTime = findLocalTime(location, expert.commentTime)
        if commentTime != "":
            commentTimeH = commentTime.hour
            commentTimeW = commentTime.weekday()
            commentTimeYear = commentTime.year
            commentTimeMonth = commentTime.month
            commentTimeDay = commentTime.day

    if expert.phase1 == True and expert.phase2 == False and expert.phase3 == False:
        if email1SentH == -1 and emailSentH != -1:
            email1SentH = emailSentH
        if email1SentW == -1 and emailSentW != -1:
            email1SentW = emailSentW
        if email1SentYear == -1 and emailSentYear != -1:
            email1SentYear = emailSentYear
        if email1SentMonth == -1 and emailSentMonth != -1:
            email1SentMonth = emailSentMonth
        if email1SentDay == -1 and emailSentDay != -1:
            email1SentDay = emailSentDay
    elif expert.phase1 == True and expert.phase2 == True and expert.phase3 == False:
        if email2SentH == -1 and emailSentH != -1:
            email2SentH = emailSentH
        if email2SentW == -1 and emailSentW != -1:
            email2SentW = emailSentW
        if email2SentYear == -1 and emailSentYear != -1:
            email2SentYear = emailSentYear
        if email2SentMonth == -1 and emailSentMonth != -1:
            email2SentMonth = emailSentMonth
        if email2SentDay == -1 and emailSentDay != -1:
            email2SentDay = emailSentDay
    elif expert.phase1 == True and expert.phase2 == True and expert.phase3 == True:
        if email3SentH == -1 and emailSentH != -1:
            email3SentH = emailSentH
        if email3SentW == -1 and emailSentW != -1:
            email3SentW = emailSentW
        if email3SentYear == -1 and emailSentYear != -1:
            email3SentYear = emailSentYear
        if email3SentMonth == -1 and emailSentMonth != -1:
            email3SentMonth = emailSentMonth
        if email3SentDay == -1 and emailSentDay != -1:
            email3SentDay = emailSentDay

    return (latitude, longitude, timeZoneObj, emailSentH, email1SentH, email2SentH,
        email3SentH, email1OpenedTimeH, email2OpenedTimeH, email3OpenedTimeH, commentTimeH, emailSentW, email1SentW,
        email2SentW, email3SentW, email1OpenedTimeW, email2OpenedTimeW, email3OpenedTimeW, commentTimeW,
        emailSentYear, email1SentYear, email2SentYear, email3SentYear, email1OpenedYear, email2OpenedYear,
        email3OpenedYear, commentYear, emailSentMonth, email1SentMonth, email2SentMonth, email3SentMonth,
        email1OpenedMonth, email2OpenedMonth, email3OpenedMonth, commentMonth, emailSentDay, email1SentDay,
        email2SentDay, email3SentDay, email1OpenedDay, email2OpenedDay, email3OpenedDay, commentDay)

def progressPage(request):

    if request.method == 'GET':
        if 'key' in request.GET:
            session_key = request.GET['key']

            s = None;
            if session_key == "":
                s = SessionStore()
                s['progressPercent'] = 0.0
                s.save()
            else:
                s = SessionStore(session_key=session_key)
                # If progress is complete, restart it.
                if s['progressPercent'] == 1:
                    s['progressPercent'] = 0.0
                    s.save()

            return HttpResponse(json.dumps({'progressPercent':s['progressPercent'], 'key':s.session_key, }), content_type="application/json")

def results(request):

    pageType = ''
    if request.method == 'GET':
        if 'version' in request.GET and request.GET['version'] != '' and 'key' in request.GET and request.GET['key'] != '':
            version = num(request.GET['version'])
            session_key = request.GET['key']

            totalEmail1Sent = 0
            totalEmail1Opened = 0
            totalPositiveResponses = 0
            totalNegative1Responses = 0
            totalEmail2Sent = 0
            totalEmail2Opened = 0
            totalLinksClickedNum = 0
            totalNegative2Responses = 0
            totalCommentsNum = 0
            totalRatingsNum = 0
            totalRefereesNum = 0
            totalEmailCommunicationNum = 0
            totalEmail3Opened = 0
            totalArticle_clicked = 0
            totalTalkpage_clicked = 0
            totalPost_clicked = 0
            totalTutorial_clicked = 0

            # phase (0, 1, 2), public (0 = No, 1 = Yes), private (0 = No, 1 = Yes),
            #   relevance (0 = No, 1 = relevant_to_research, 2 = within_area, 3 = on_expertise_topic), 4 = total),
            #   citation (0 = No, 1 = likely_to_cite, 2 = may_include_reference, 3 = might_refer_to, 4 = total)
            #    <- [{ sent (number), positive (response number),
            #   negative (response number), opened (emails number), comment (number), ranking (number),
            #   referal (number), emailCommunication (number), article_clicked (number),
            #   talkpage_clicked (number), post_clicked (number), tutorial_clicked (number) }]
            resultNumbers = []
            for phase in range(3):
                resultNumbers.append([])
                for public in range(2):
                    resultNumbers[phase].append([])
                    for private in range(2):
                        resultNumbers[phase][public].append([])
                        for relevance in range(5):
                            resultNumbers[phase][public][private].append([])
                            for citation in range(5):
                                resultNumbers[phase][public][private][relevance].append({'sent':0, 'positive':0,
                                    'negative':0, 'opened':0, 'linksClicked':0, 'comment':0, 'rating':0, 'referal':0,
                                    'emailCommunication':0, 'article_clicked':0, 'talkpage_clicked':0, 'post_clicked':0,
                                    'tutorial_clicked':0})
            
            # hour(24 hours), phase (0, 1, 2), public (0 = No, 1 = Yes), private (0 = No, 1 = Yes),
            #   relevance (0 = No, 1 = total), citation (0 = No, 1 = total)
            #    <- [{ sent (number), positive (response number),
            #   negative (response number), opened (emails number), comment (number), ranking (number),
            #   referal (number), emailCommunication (number), article_clicked (number),
            #   talkpage_clicked (number), post_clicked (number), tutorial_clicked (number) }]
            resultHoursNumbers = []
            for hour in range(24):
                resultHoursNumbers.append([])
                for phase in range(3):
                    resultHoursNumbers[hour].append([])
                    for public in range(2):
                        resultHoursNumbers[hour][phase].append([])
                        for private in range(2):
                            resultHoursNumbers[hour][phase][public].append([])
                            for relevance in range(5):
                                resultHoursNumbers[hour][phase][public][private].append([])
                                for citation in range(5):
                                    resultHoursNumbers[hour][phase][public][private][relevance].append({'sent':0, 'positive':0, 'negative':0, 'opened':0,
                                        'linksClicked':0, 'comment':0, 'rating':0, 'referal':0, 'emailCommunication':0,
                                        'article_clicked':0, 'talkpage_clicked':0, 'post_clicked':0, 'tutorial_clicked':0})

            # weekday(24 hours), phase (0, 1, 2), public (0 = No, 1 = Yes), private (0 = No, 1 = Yes),
            #   relevance (0 = No, 1 = total), citation (0 = No, 1 = total)
            #    <- [{ sent (number), positive (response number),
            #   negative (response number), opened (emails number), comment (number), ranking (number),
            #   referal (number), emailCommunication (number), article_clicked (number),
            #   talkpage_clicked (number), post_clicked (number), tutorial_clicked (number) }]
            resultWeekdaysNumbers = []
            for hour in range(7):
                resultWeekdaysNumbers.append([])
                for phase in range(3):
                    resultWeekdaysNumbers[hour].append([])
                    for public in range(2):
                        resultWeekdaysNumbers[hour][phase].append([])
                        for private in range(2):
                            resultWeekdaysNumbers[hour][phase][public].append([])
                            for relevance in range(5):
                                resultWeekdaysNumbers[hour][phase][public][private].append([])
                                for citation in range(5):
                                    resultWeekdaysNumbers[hour][phase][public][private][relevance].append({'sent':0, 'positive':0, 'negative':0, 'opened':0,
                                        'linksClicked':0, 'comment':0, 'rating':0, 'referal':0, 'emailCommunication':0,
                                        'article_clicked':0, 'talkpage_clicked':0, 'post_clicked':0, 'tutorial_clicked':0})

            # [{ phase (0, 1, 2), public (0 = No, 1 = Yes), private (0 = No, 1 = Yes),
            #   relevance (0 = No, 1 = relevant_to_research, 2 = within_area, 3 = on_expertise_topic),
            #   citation (0 = No, 1 = likely_to_cite, 2 = may_include_reference, 3 = might_refer_to), sent (number), positive (response number),
            #   negative (response number), opened (emails number), comment (number), ranking (number),
            #   referal (number), emailCommunication (number), article_clicked (number),
            #   talkpage_clicked (number), post_clicked (number), tutorial_clicked (number), latitude (number), longitude (number) }]
            mapElements = []

            if session_key != "":
                s = SessionStore(session_key=session_key)
                s['progressPercent'] == 0.0
                s.save()

            allExperts = Expert.objects.all()

            expertNum = 0.00

            for expert in allExperts:
                expertNum += 1.00

                expertwikipages = expert.expertwikipub_set.all()
                expertPk = expert.pk
                email = expert.email
                firstName = expert.firstname
                lastName = expert.name
                study_version = expert.study_version
                phase1 = expert.phase1
                phase2 = expert.phase2
                phase3 = expert.phase3
                inSpecialtyArea = expert.inspecialtyarea
                indiscipline = expert.indiscipline
                expertDomain = expert.domain
                expertSpecialization = expert.specialization
                
                highviewspast90days = expert.highviewspast90days
                citedpublication = expert.citedpublication
                relevance_factor = expert.relevance_factor
                likely_to_cite = expert.likely_to_cite
                may_include_reference = expert.may_include_reference
                might_refer_to = expert.might_refer_to
                relevant_to_research = expert.relevant_to_research
                within_area = expert.within_area
                on_expertise_topic = expert.on_expertise_topic
                especially_popular = expert.especially_popular
                highly_visible = expert.highly_visible
                highly_popular = expert.highly_popular
                private_first = expert.private_first
                
                emailCount = expert.emailCount
                email1Count = expert.email1Count
                email2Count = expert.email2Count
                email3Count = expert.email3Count

                interested = expert.returned
                withdrawal = expert.withdrawal
                email1_opened = int(expert.email1_opened)
                email2_opened = int(expert.email2_opened)
                user_agent = expert.user_agent
                email1Sent = expert.email1Sent
                email1OpenedTime = expert.email1OpenedTime
                email2OpenedTime = expert.email2OpenedTime
                emailCommunication = int(expert.emailCommunication)
                email3_opened = int(expert.email3_opened)
                article_clicked = int(expert.article_clicked)
                talkpage_clicked = int(expert.talkpage_clicked)
                post_clicked = int(expert.post_clicked)
                tutorial_clicked = int(expert.tutorial_clicked)
                econ_wikiproject_clicked = int(expert.econ_wikiproject_clicked)
                updated = expert.updated

                location = expert.location

                (latitude, longitude, timeZoneObj, emailSentH, email1SentH, email2SentH,
                    email3SentH, email1OpenedTimeH, email2OpenedTimeH, email3OpenedTimeH, commentTimeH, emailSentW, email1SentW,
                    email2SentW, email3SentW, email1OpenedTimeW, email2OpenedTimeW, email3OpenedTimeW, commentTimeW,
                    emailSentYear, email1SentYear, email2SentYear, email3SentYear, email1OpenedYear, email2OpenedYear,
                    email3OpenedYear, commentYear, emailSentMonth, email1SentMonth, email2SentMonth, email3SentMonth,
                    email1OpenedMonth, email2OpenedMonth, email3OpenedMonth, commentMonth, emailSentDay, email1SentDay,
                    email2SentDay, email3SentDay, email1OpenedDay, email2OpenedDay, email3OpenedDay,
                    commentDay) = dateTimeStats(expert, location)

                recommendationsNum = len(expertwikipages)
                linksClickedNum = 0
                commentsNum = 0
                ratingsNum = 0
                refereesNum = 0
                for expertWikipage in expertwikipages:
                    linksClickedNum += expertWikipage.link_clicked
                    if expertWikipage.comment is not None and expertWikipage.comment != "":
                        commentsNum += 1
                    if expertWikipage.rating is not None and expertWikipage.rating != 0 and expertWikipage.rating != "":
                        ratingsNum += 1
                    expertwikipubreferees = expertWikipage.expertwikipubreferee_set.all()
                    refereesNum += len(expertwikipubreferees)

                if (email is not None and email != '' and expertSpecialization is not None and expertSpecialization != ""
                    and indiscipline == False and version == study_version):
                    public = 0
                    private = 0
                    relevance = 0
                    citation = 0
                    email1Sent = 0
                    email2Sent = 0
                    email3Sent = 0
                    positive = 0
                    negative1 = 0
                    negative2 = 0
                    if highviewspast90days == True:
                        public = 1
                    if citedpublication == True:
                        private = 1
                        if relevance_factor == True:
                            if relevant_to_research == True:
                                relevance = 1
                            elif within_area == True:
                                relevance = 2
                            elif on_expertise_topic == True:
                                relevance = 3
                        else:
                            if likely_to_cite == True:
                                citation = 1
                            elif may_include_reference == True:
                                citation = 2
                            elif might_refer_to == True:
                                citation = 3
                    if emailCount > 0:
                        email1Sent = 1
                    if email1_opened == 1:
                        email1Sent = 1
                    if interested == True:
                        email1Sent = 1
                        positive = 1
                    if email2_opened == 1:
                        email1Sent = 1
                        email2Sent = 1
                        positive = 1
                    if email3_opened == 1:
                        email1Sent = 1
                        email2Sent = 1
                        email3Sent = 1
                        positive = 1
                        comment = 1
                    if phase2 == True:
                        email1Sent = 1
                        positive = 1
                        if emailCount > 0:
                            email2Sent = 1
                        if withdrawal == True:
                            negative2 = 1
                    else:
                        if withdrawal == True:
                            email1Sent = 1
                            negative1 = 1
                    if phase3 == True:
                        email1Sent = 1
                        email2Sent = 1
                        positive = 1
                        if emailCount > 0:
                            email3Sent = 1

                    resultNumbers[0][public][private][relevance][citation]['sent'] += email1Sent
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':email1Sent,
                            'opened':0, 'positive':0, 'negative':0,
                            'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                        if email1SentH != -1:
                            resultHoursNumbers[email1SentH][0][public][private][0][0]['sent'] += email1Sent
                        if email1SentW != -1:
                            resultWeekdaysNumbers[email1SentW][0][public][private][0][0]['sent'] += email1Sent

                    resultNumbers[0][public][private][relevance][citation]['opened'] += email1_opened
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                            'opened':email1_opened, 'positive':0, 'negative':0,
                            'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                        if email1OpenedTimeH != -1:
                            resultHoursNumbers[email1OpenedTimeH][0][public][private][0][0]['opened'] += email1_opened
                        if email1OpenedTimeW != -1:
                            resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][0][0]['opened'] += email1_opened

                    resultNumbers[0][public][private][relevance][citation]['positive'] += positive
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                            'opened':0, 'positive':positive, 'negative':0,
                            'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                        if email1OpenedTimeH != -1:
                            resultHoursNumbers[email1OpenedTimeH][0][public][private][0][0]['positive'] += positive
                        if email1OpenedTimeW != -1:
                            resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][0][0]['positive'] += positive

                    resultNumbers[0][public][private][relevance][citation]['negative'] += negative1
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                            'opened':0, 'positive':0, 'negative':negative1,
                            'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                        if email1OpenedTimeH != -1:
                            resultHoursNumbers[email1OpenedTimeH][0][public][private][0][0]['negative'] += negative1
                        if email1OpenedTimeW != -1:
                            resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][0][0]['negative'] += negative1

                    resultNumbers[0][public][private][relevance][citation]['emailCommunication'] += emailCommunication
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                            'opened':0, 'positive':0, 'negative':0,
                            'emailCommunication':emailCommunication, 'firstName':firstName, 'lastName':lastName})

                    if relevance != 0 or citation != 0:
                        resultNumbers[0][public][private][0][0]['sent'] += email1Sent
                        resultNumbers[0][public][private][0][0]['opened'] += email1_opened
                        resultNumbers[0][public][private][0][0]['positive'] += positive
                        resultNumbers[0][public][private][0][0]['negative'] += negative1
                        resultNumbers[0][public][private][0][0]['emailCommunication'] += emailCommunication

                        if relevance != 0 and citation == 0:
                            resultNumbers[0][public][private][4][0]['sent'] += email1Sent
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':email1Sent,
                                'opened':0, 'positive':0, 'negative':0,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1SentH != -1:
                                resultHoursNumbers[email1SentH][0][public][private][1][0]['sent'] += email1Sent
                            if email1SentW != -1:
                                resultWeekdaysNumbers[email1SentW][0][public][private][1][0]['sent'] += email1Sent

                            resultNumbers[0][public][private][4][0]['opened'] += email1_opened
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':email1_opened, 'positive':0, 'negative':0,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1OpenedTimeH != -1:
                                resultHoursNumbers[email1OpenedTimeH][0][public][private][1][0]['opened'] += email1_opened
                            if email1OpenedTimeW != -1:
                                resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][1][0]['opened'] += email1_opened

                            resultNumbers[0][public][private][4][0]['positive'] += positive
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'positive':positive, 'negative':0,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1OpenedTimeH != -1:
                                resultHoursNumbers[email1OpenedTimeH][0][public][private][1][0]['positive'] += positive
                            if email1OpenedTimeW != -1:
                                resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][1][0]['positive'] += positive

                            resultNumbers[0][public][private][4][0]['negative'] += negative1
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'positive':0, 'negative':negative1,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1OpenedTimeH != -1:
                                resultHoursNumbers[email1OpenedTimeH][0][public][private][1][0]['negative'] += negative1
                            if email1OpenedTimeW != -1:
                                resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][1][0]['negative'] += negative1

                            resultNumbers[0][public][private][4][0]['emailCommunication'] += emailCommunication
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'positive':0, 'negative':0,
                                'emailCommunication':emailCommunication, 'firstName':firstName, 'lastName':lastName})

                        elif relevance == 0 and citation != 0:
                            resultNumbers[0][public][private][0][4]['sent'] += email1Sent
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':email1Sent,
                                'opened':0, 'positive':0, 'negative':0,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1SentH != -1:
                                resultHoursNumbers[email1SentH][0][public][private][0][1]['sent'] += email1Sent
                            if email1SentW != -1:
                                resultWeekdaysNumbers[email1SentW][0][public][private][0][1]['sent'] += email1Sent

                            resultNumbers[0][public][private][0][4]['opened'] += email1_opened
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':email1_opened, 'positive':0, 'negative':0,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1OpenedTimeH != -1:
                                resultHoursNumbers[email1OpenedTimeH][0][public][private][0][1]['opened'] += email1_opened
                            if email1OpenedTimeW != -1:
                                resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][0][1]['opened'] += email1_opened

                            resultNumbers[0][public][private][0][4]['positive'] += positive
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'positive':positive, 'negative':0,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1OpenedTimeH != -1:
                                resultHoursNumbers[email1OpenedTimeH][0][public][private][0][1]['positive'] += positive
                            if email1OpenedTimeW != -1:
                                resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][0][1]['positive'] += positive

                            resultNumbers[0][public][private][0][4]['negative'] += negative1
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'positive':0, 'negative':negative1,
                                'emailCommunication':0, 'firstName':firstName, 'lastName':lastName})

                            if email1OpenedTimeH != -1:
                                resultHoursNumbers[email1OpenedTimeH][0][public][private][0][1]['negative'] += negative1
                            if email1OpenedTimeW != -1:
                                resultWeekdaysNumbers[email1OpenedTimeW][0][public][private][0][1]['negative'] += negative1

                            resultNumbers[0][public][private][0][4]['emailCommunication'] += emailCommunication
                            mapElements.append({'phase':0, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'positive':0, 'negative':0,
                                'emailCommunication':emailCommunication, 'firstName':firstName, 'lastName':lastName})

                    totalEmailCommunicationNum += emailCommunication
                    totalEmail1Sent += email1Sent
                    totalEmail1Opened += email1_opened
                    totalPositiveResponses += positive
                    totalNegative1Responses += negative1

                    resultNumbers[1][public][private][relevance][citation]['sent'] += email2Sent
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':email2Sent,
                            'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                            'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                        if email2SentH != -1:
                            resultHoursNumbers[email2SentH][1][public][private][0][0]['sent'] += email2Sent
                        if email2SentW != -1:
                            resultWeekdaysNumbers[email2SentW][1][public][private][0][0]['sent'] += email2Sent

                    resultNumbers[1][public][private][relevance][citation]['opened'] += email2_opened
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                            'opened':email2_opened, 'negative':0, 'linksClicked':0, 'comment':0,
                            'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                        if email2OpenedTimeH != -1:
                            resultHoursNumbers[email2OpenedTimeH][1][public][private][0][0]['opened'] += email2_opened
                        if email2OpenedTimeW != -1:
                            resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][0]['opened'] += email2_opened

                    resultNumbers[1][public][private][relevance][citation]['negative'] += negative2
                    if relevance == 0 and citation == 0:
                        mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                            'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                            'opened':0, 'negative':negative2, 'linksClicked':0, 'comment':0,
                            'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                        if email2OpenedTimeH != -1:
                            resultHoursNumbers[email2OpenedTimeH][1][public][private][0][0]['negative'] += negative2
                        if email2OpenedTimeW != -1:
                            resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][0]['negative'] += negative2

                    if relevance != 0 or citation != 0:
                        resultNumbers[1][public][private][0][0]['sent'] += email2Sent
                        resultNumbers[1][public][private][0][0]['opened'] += email2_opened
                        resultNumbers[1][public][private][0][0]['negative'] += negative2

                        if relevance != 0 and citation == 0:
                            resultNumbers[1][public][private][4][0]['sent'] += email2Sent
                            mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':email2Sent,
                                'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                            if email2SentH != -1:
                                resultHoursNumbers[email2SentH][1][public][private][1][0]['sent'] += email2Sent
                            if email2SentW != -1:
                                resultWeekdaysNumbers[email2SentW][1][public][private][1][0]['sent'] += email2Sent

                            resultNumbers[1][public][private][4][0]['opened'] += email2_opened
                            mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':email2_opened, 'negative':0, 'linksClicked':0, 'comment':0,
                                'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                            if email2OpenedTimeH != -1:
                                resultHoursNumbers[email2OpenedTimeH][1][public][private][1][0]['opened'] += email2_opened
                            if email2OpenedTimeW != -1:
                                resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][1][0]['opened'] += email2_opened

                            resultNumbers[1][public][private][4][0]['negative'] += negative2
                            mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'negative':negative2, 'linksClicked':0, 'comment':0,
                                'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                            if email2OpenedTimeH != -1:
                                resultHoursNumbers[email2OpenedTimeH][1][public][private][1][0]['negative'] += negative2
                            if email2OpenedTimeW != -1:
                                resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][1][0]['negative'] += negative2

                        elif relevance == 0 and citation != 0:
                            resultNumbers[1][public][private][0][4]['sent'] += email2Sent
                            mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':email2Sent,
                                'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                            if email2SentH != -1:
                                resultHoursNumbers[email2SentH][1][public][private][0][1]['sent'] += email2Sent
                            if email2SentW != -1:
                                resultWeekdaysNumbers[email2SentW][1][public][private][0][1]['sent'] += email2Sent

                            resultNumbers[1][public][private][0][4]['opened'] += email2_opened
                            mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':email2_opened, 'negative':0, 'linksClicked':0, 'comment':0,
                                'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                            if email2OpenedTimeH != -1:
                                resultHoursNumbers[email2OpenedTimeH][1][public][private][0][1]['opened'] += email2_opened
                            if email2OpenedTimeW != -1:
                                resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][1]['opened'] += email2_opened

                            resultNumbers[1][public][private][0][4]['negative'] += negative2
                            mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                'opened':0, 'negative':negative2, 'linksClicked':0, 'comment':0,
                                'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                            if email2OpenedTimeH != -1:
                                resultHoursNumbers[email2OpenedTimeH][1][public][private][0][1]['negative'] += negative2
                            if email2OpenedTimeW != -1:
                                resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][1]['negative'] += negative2

                    totalEmail2Sent += email2Sent
                    totalEmail2Opened += email2_opened
                    totalNegative2Responses += negative2

                    if phase2 == 1:
                        if linksClickedNum != 0:
                            totalLinksClickedNum += 1
                            resultNumbers[1][public][private][relevance][citation]['linksClicked'] += 1
                            if relevance != 0 or citation != 0:
                                resultNumbers[1][public][private][0][0]['linksClicked'] += 1
                                if relevance != 0 and citation == 0:
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                        'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':1, 'comment':0,
                                        'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                    resultNumbers[1][public][private][4][0]['linksClicked'] += 1
                                    if email2OpenedTimeH != -1:
                                        resultHoursNumbers[email2OpenedTimeH][1][public][private][1][0]['linksClicked'] += 1
                                    if email2OpenedTimeW != -1:
                                        resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][1][0]['linksClicked'] += 1

                                elif relevance == 0 and citation != 0:
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                        'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':1, 'comment':0,
                                        'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                    resultNumbers[1][public][private][0][4]['linksClicked'] += 1
                                    if email2OpenedTimeH != -1:
                                        resultHoursNumbers[email2OpenedTimeH][1][public][private][0][1]['linksClicked'] += 1
                                    if email2OpenedTimeW != -1:
                                        resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][1]['linksClicked'] += 1
                            else:
                                mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                    'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                    'opened':0, 'negative':0, 'linksClicked':1, 'comment':0,
                                    'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                if email2OpenedTimeH != -1:
                                    resultHoursNumbers[email2OpenedTimeH][1][public][private][0][0]['linksClicked'] += 1
                                if email2OpenedTimeW != -1:
                                    resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][0]['linksClicked'] += 1

                        if commentsNum != 0:
                            totalCommentsNum += 1
                            resultNumbers[1][public][private][relevance][citation]['comment'] += 1
                            if relevance != 0 or citation != 0:
                                resultNumbers[1][public][private][0][0]['comment'] += 1
                                if relevance != 0 and citation == 0:
                                    resultNumbers[1][public][private][4][0]['comment'] += 1
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                        'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':0, 'comment':1,
                                        'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                    if commentTimeH != -1:
                                        resultHoursNumbers[commentTimeH][1][public][private][1][0]['comment'] += 1
                                    if commentTimeW != -1:
                                        resultWeekdaysNumbers[commentTimeW][1][public][private][1][0]['comment'] += 1

                                elif relevance == 0 and citation != 0:
                                    resultNumbers[1][public][private][0][4]['comment'] += 1
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                        'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':0, 'comment':1,
                                        'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                    if commentTimeH != -1:
                                        resultHoursNumbers[commentTimeH][1][public][private][0][1]['comment'] += 1
                                    if commentTimeW != -1:
                                        resultWeekdaysNumbers[commentTimeW][1][public][private][0][1]['comment'] += 1
                            else:
                                mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                    'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                    'opened':0, 'negative':0, 'linksClicked':0, 'comment':1,
                                    'rating':0, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                if commentTimeH != -1:
                                    resultHoursNumbers[commentTimeH][1][public][private][0][0]['comment'] += 1
                                if commentTimeW != -1:
                                    resultWeekdaysNumbers[commentTimeW][1][public][private][0][0]['comment'] += 1

                        if ratingsNum != 0:
                            totalRatingsNum += 1
                            resultNumbers[1][public][private][relevance][citation]['rating'] += 1
                            if relevance != 0 or citation != 0:
                                resultNumbers[1][public][private][0][0]['rating'] += 1
                                if relevance != 0 and citation == 0:
                                    resultNumbers[1][public][private][4][0]['rating'] += 1
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                        'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                        'rating':1, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                    if email2OpenedTimeH != -1:
                                        resultHoursNumbers[email2OpenedTimeH][1][public][private][1][0]['rating'] += 1
                                    if email2OpenedTimeW != -1:
                                        resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][1][0]['rating'] += 1

                                elif relevance == 0 and citation != 0:
                                    resultNumbers[1][public][private][0][4]['rating'] += 1
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                        'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                        'rating':1, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                    if email2OpenedTimeH != -1:
                                        resultHoursNumbers[email2OpenedTimeH][1][public][private][0][1]['rating'] += 1
                                    if email2OpenedTimeW != -1:
                                        resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][1]['rating'] += 1
                            else:
                                mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                    'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                    'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                    'rating':1, 'referal':0, 'firstName':firstName, 'lastName':lastName})

                                if email2OpenedTimeH != -1:
                                    resultHoursNumbers[email2OpenedTimeH][1][public][private][0][0]['rating'] += 1
                                if email2OpenedTimeW != -1:
                                    resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][0]['rating'] += 1

                        if refereesNum != 0:
                            totalRefereesNum += 1
                            resultNumbers[1][public][private][relevance][citation]['referal'] += 1
                            if relevance != 0 or citation != 0:
                                resultNumbers[1][public][private][0][0]['referal'] += 1
                                if relevance != 0 and citation == 0:
                                    resultNumbers[1][public][private][4][0]['referal'] += 1
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':1,
                                        'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                        'rating':0, 'referal':1, 'firstName':firstName, 'lastName':lastName})

                                    if email2OpenedTimeH != -1:
                                        resultHoursNumbers[email2OpenedTimeH][1][public][private][1][0]['referal'] += 1
                                    if email2OpenedTimeW != -1:
                                        resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][1][0]['referal'] += 1

                                elif relevance == 0 and citation != 0:
                                    resultNumbers[1][public][private][0][4]['referal'] += 1
                                    mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                        'citation':1, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                        'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                        'rating':0, 'referal':1, 'firstName':firstName, 'lastName':lastName})

                                    if email2OpenedTimeH != -1:
                                        resultHoursNumbers[email2OpenedTimeH][1][public][private][0][1]['referal'] += 1
                                    if email2OpenedTimeW != -1:
                                        resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][1]['referal'] += 1
                            else:
                                mapElements.append({'phase':1, 'public':public, 'private':private, 'relevance':0,
                                    'citation':0, 'latitude':latitude, 'longitude':longitude, 'sent':0,
                                    'opened':0, 'negative':0, 'linksClicked':0, 'comment':0,
                                    'rating':0, 'referal':1, 'firstName':firstName, 'lastName':lastName})

                                if email2OpenedTimeH != -1:
                                    resultHoursNumbers[email2OpenedTimeH][1][public][private][0][0]['referal'] += 1
                                if email2OpenedTimeW != -1:
                                    resultWeekdaysNumbers[email2OpenedTimeW][1][public][private][0][0]['referal'] += 1

                    if phase3 == 1:
                        resultNumbers[2][public][private][relevance][citation]['opened'] += email3_opened
                        totalEmail3Opened += email3_opened
                        resultNumbers[2][public][private][relevance][citation]['article_clicked'] += article_clicked
                        totalArticle_clicked += article_clicked
                        resultNumbers[2][public][private][relevance][citation]['talkpage_clicked'] += talkpage_clicked
                        totalTalkpage_clicked += talkpage_clicked
                        resultNumbers[2][public][private][relevance][citation]['post_clicked'] += post_clicked
                        totalPost_clicked += post_clicked
                        resultNumbers[2][public][private][relevance][citation]['tutorial_clicked'] += tutorial_clicked
                        totalTutorial_clicked += tutorial_clicked
                        if relevance != 0 or citation != 0:
                            resultNumbers[2][public][private][0][0]['opened'] += email3_opened
                            resultNumbers[2][public][private][0][0]['article_clicked'] += article_clicked
                            resultNumbers[2][public][private][0][0]['talkpage_clicked'] += talkpage_clicked
                            resultNumbers[2][public][private][0][0]['post_clicked'] += post_clicked
                            resultNumbers[2][public][private][0][0]['tutorial_clicked'] += tutorial_clicked
                            if relevance != 0 and citation == 0:
                                resultNumbers[2][public][private][4][0]['opened'] += email3_opened
                                resultNumbers[2][public][private][4][0]['article_clicked'] += article_clicked
                                resultNumbers[2][public][private][4][0]['talkpage_clicked'] += talkpage_clicked
                                resultNumbers[2][public][private][4][0]['post_clicked'] += post_clicked
                                resultNumbers[2][public][private][4][0]['tutorial_clicked'] += tutorial_clicked
                            elif relevance == 0 and citation != 0:
                                resultNumbers[2][public][private][0][4]['opened'] += email3_opened
                                resultNumbers[2][public][private][0][4]['article_clicked'] += article_clicked
                                resultNumbers[2][public][private][0][4]['talkpage_clicked'] += talkpage_clicked
                                resultNumbers[2][public][private][0][4]['post_clicked'] += post_clicked
                                resultNumbers[2][public][private][0][4]['tutorial_clicked'] += tutorial_clicked

                if session_key != "":
                    s['progressPercent'] = str(expertNum / float(len(allExperts)))
                    s.save()
                
            totalEmail1Opened = str(totalEmail1Opened) + " (" + str(totalEmail1Opened * 100 / totalEmail1Sent) + "%)"
            totalNegative1Responses = str(totalNegative1Responses) + " (" + str(totalNegative1Responses * 100 / totalEmail1Sent) + "%)"
            totalEmail2Sent = str(totalEmail2Sent) + " (" + str(totalEmail2Sent * 100 / totalPositiveResponses) + "%)"
            totalEmail2Opened = str(totalEmail2Opened) + " (" + str(totalEmail2Opened * 100 / totalPositiveResponses) + "%)"
            totalLinksClickedNum = str(totalLinksClickedNum) + " (" + str(totalLinksClickedNum * 100 / totalPositiveResponses) + "%)"
            totalNegative2Responses = str(totalNegative2Responses) + " (" + str(totalNegative2Responses * 100 / totalPositiveResponses) + "%)"
            totalRatingsNum = str(totalRatingsNum) + " (" + str(totalRatingsNum * 100 / totalPositiveResponses) + "%)"
            totalRefereesNum = str(totalRefereesNum) + " (" + str(totalRefereesNum * 100 / totalPositiveResponses) + "%)"
            totalEmailCommunicationNum = str(totalEmailCommunicationNum) + " (" + str(totalEmailCommunicationNum * 100 / totalEmail1Sent) + "%)"
            totalEmail3Opened = str(totalEmail3Opened) + " (" + str(totalEmail3Opened * 100 / totalCommentsNum) + "%)"
            totalArticle_clicked = str(totalArticle_clicked) + " (" + str(totalArticle_clicked * 100 / totalCommentsNum) + "%)"
            totalTalkpage_clicked = str(totalTalkpage_clicked) + " (" + str(totalTalkpage_clicked * 100 / totalCommentsNum) + "%)"
            totalPost_clicked = str(totalPost_clicked) + " (" + str(totalPost_clicked * 100 / totalCommentsNum) + "%)"
            totalTutorial_clicked = str(totalTutorial_clicked) + " (" + str(totalTutorial_clicked * 100 / totalCommentsNum) + "%)"
            totalCommentsNum = str(totalCommentsNum) + " (" + str(totalCommentsNum * 100 / totalPositiveResponses) + "%)"
            totalPositiveResponses = str(totalPositiveResponses) + " (" + str(totalPositiveResponses * 100 / totalEmail1Sent) + "%)"
            totalEmail1Sent = str(totalEmail1Sent)

            # for public in range(2):
            #     for private in range(2):
            #         for relevance in range(5):
            #             for citation in range(5):
            #                 if resultNumbers[0][public][private][relevance][citation]['sent'] == 0:
            #                     resultNumbers[0][public][private][relevance][citation]['opened'] = (str(resultNumbers[0][public][private][relevance][citation]['opened']) + " (0%)")
            #                     resultNumbers[0][public][private][relevance][citation]['negative'] = (str(resultNumbers[0][public][private][relevance][citation]['negative']) + " (0%)")
            #                 else:
            #                     resultNumbers[0][public][private][relevance][citation]['opened'] = (str(resultNumbers[0][public][private][relevance][citation]['opened']) +
            #                         " (" + str(resultNumbers[0][public][private][relevance][citation]['opened'] * 100 / resultNumbers[0][public][private][relevance][citation]['sent']) + "%)")
            #                     resultNumbers[0][public][private][relevance][citation]['negative'] = (str(resultNumbers[0][public][private][relevance][citation]['negative']) +
            #                         " (" + str(resultNumbers[0][public][private][relevance][citation]['negative'] * 100 / resultNumbers[0][public][private][relevance][citation]['sent']) + "%)")
            #                 if resultNumbers[0][public][private][relevance][citation]['positive'] == 0:
            #                     resultNumbers[1][public][private][relevance][citation]['sent'] = (str(resultNumbers[1][public][private][relevance][citation]['sent']) + " (0%)")
            #                     resultNumbers[1][public][private][relevance][citation]['opened'] = (str(resultNumbers[1][public][private][relevance][citation]['opened']) + " (0%)")
            #                     resultNumbers[1][public][private][relevance][citation]['linksClicked'] = (str(resultNumbers[1][public][private][relevance][citation]['linksClicked']) + " (0%)")
            #                     resultNumbers[1][public][private][relevance][citation]['negative'] = (str(resultNumbers[1][public][private][relevance][citation]['negative']) + " (0%)")
            #                     resultNumbers[1][public][private][relevance][citation]['rating'] = (str(resultNumbers[1][public][private][relevance][citation]['rating']) + " (0%)")
            #                 else:
            #                     resultNumbers[1][public][private][relevance][citation]['sent'] = (str(resultNumbers[1][public][private][relevance][citation]['sent']) +
            #                         " (" + str(resultNumbers[1][public][private][relevance][citation]['sent'] * 100 / resultNumbers[0][public][private][relevance][citation]['positive']) + "%)")
            #                     resultNumbers[1][public][private][relevance][citation]['opened'] = (str(resultNumbers[1][public][private][relevance][citation]['opened']) +
            #                         " (" + str(resultNumbers[1][public][private][relevance][citation]['opened'] * 100 / resultNumbers[0][public][private][relevance][citation]['positive']) + "%)")
            #                     resultNumbers[1][public][private][relevance][citation]['linksClicked'] = (str(resultNumbers[1][public][private][relevance][citation]['linksClicked']) +
            #                         " (" + str(resultNumbers[1][public][private][relevance][citation]['linksClicked'] * 100 / resultNumbers[0][public][private][relevance][citation]['positive']) + "%)")
            #                     resultNumbers[1][public][private][relevance][citation]['negative'] = (str(resultNumbers[1][public][private][relevance][citation]['negative']) +
            #                         " (" + str(resultNumbers[1][public][private][relevance][citation]['negative'] * 100 / resultNumbers[0][public][private][relevance][citation]['positive']) + "%)")
            #                     resultNumbers[1][public][private][relevance][citation]['rating'] = (str(resultNumbers[1][public][private][relevance][citation]['rating']) +
            #                         " (" + str(resultNumbers[1][public][private][relevance][citation]['rating'] * 100 / resultNumbers[0][public][private][relevance][citation]['positive']) + "%)")
            #                 if resultNumbers[1][public][private][relevance][citation]['comment'] == 0:
            #                     resultNumbers[2][public][private][relevance][citation]['opened'] = (str(resultNumbers[2][public][private][relevance][citation]['opened']) + " (0%)")
            #                     resultNumbers[2][public][private][relevance][citation]['article_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['article_clicked']) + " (0%)")
            #                     resultNumbers[2][public][private][relevance][citation]['talkpage_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['talkpage_clicked']) + " (0%)")
            #                     resultNumbers[2][public][private][relevance][citation]['post_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['post_clicked']) + " (0%)")
            #                     resultNumbers[2][public][private][relevance][citation]['tutorial_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['tutorial_clicked']) + " (0%)")
            #                 else:
            #                     resultNumbers[2][public][private][relevance][citation]['opened'] = (str(resultNumbers[2][public][private][relevance][citation]['opened']) +
            #                         " (" + str(resultNumbers[2][public][private][relevance][citation]['opened'] * 100 / resultNumbers[1][public][private][relevance][citation]['comment']) + "%)")
            #                     resultNumbers[2][public][private][relevance][citation]['article_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['article_clicked']) +
            #                         " (" + str(resultNumbers[2][public][private][relevance][citation]['article_clicked'] * 100 / resultNumbers[1][public][private][relevance][citation]['comment']) + "%)")
            #                     resultNumbers[2][public][private][relevance][citation]['talkpage_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['talkpage_clicked']) +
            #                         " (" + str(resultNumbers[2][public][private][relevance][citation]['talkpage_clicked'] * 100 / resultNumbers[1][public][private][relevance][citation]['comment']) + "%)")
            #                     resultNumbers[2][public][private][relevance][citation]['post_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['post_clicked']) +
            #                         " (" + str(resultNumbers[2][public][private][relevance][citation]['post_clicked'] * 100 / resultNumbers[1][public][private][relevance][citation]['comment']) + "%)")
            #                     resultNumbers[2][public][private][relevance][citation]['tutorial_clicked'] = (str(resultNumbers[2][public][private][relevance][citation]['tutorial_clicked']) +
            #                         " (" + str(resultNumbers[2][public][private][relevance][citation]['tutorial_clicked'] * 100 / resultNumbers[1][public][private][relevance][citation]['comment']) + "%)")
            #                 if resultNumbers[0][public][private][relevance][citation]['positive'] == 0:
            #                     resultNumbers[1][public][private][relevance][citation]['comment'] = (str(resultNumbers[1][public][private][relevance][citation]['comment']) + " (0%)")
            #                 else:
            #                     resultNumbers[1][public][private][relevance][citation]['comment'] = (str(resultNumbers[1][public][private][relevance][citation]['comment']) +
            #                         " (" + str(resultNumbers[1][public][private][relevance][citation]['comment'] * 100 / resultNumbers[0][public][private][relevance][citation]['positive']) + "%)")
            #                 if resultNumbers[0][public][private][relevance][citation]['sent'] == 0:
            #                     resultNumbers[0][public][private][relevance][citation]['positive'] = (str(resultNumbers[0][public][private][relevance][citation]['positive']) + " (0%)")
            #                 else:
            #                     resultNumbers[0][public][private][relevance][citation]['positive'] = (str(resultNumbers[0][public][private][relevance][citation]['positive']) +
            #                         " (" + str(resultNumbers[0][public][private][relevance][citation]['positive'] * 100 / resultNumbers[0][public][private][relevance][citation]['sent']) + "%)")
            #                 resultNumbers[0][public][private][relevance][citation]['sent'] = str(resultNumbers[0][public][private][relevance][citation]['sent'])
            #                 if relevance != 0 or citation != 0:
            #                     if resultNumbers[0][public][private][0][0]['sent'] == 0:
            #                         resultNumbers[0][public][private][0][0]['opened'] = (str(resultNumbers[0][public][private][0][0]['opened']) + " (0%)")
            #                         resultNumbers[0][public][private][0][0]['negative'] = (str(resultNumbers[0][public][private][0][0]['negative']) + " (0%)")
            #                     else:
            #                         resultNumbers[0][public][private][0][0]['opened'] = (str(resultNumbers[0][public][private][0][0]['opened']) +
            #                             " (" + str(resultNumbers[0][public][private][0][0]['opened'] * 100 / resultNumbers[0][public][private][0][0]['sent']) + "%)")
            #                         resultNumbers[0][public][private][0][0]['negative'] = (str(resultNumbers[0][public][private][0][0]['negative']) +
            #                             " (" + str(resultNumbers[0][public][private][0][0]['negative'] * 100 / resultNumbers[0][public][private][0][0]['sent']) + "%)")
            #                     if resultNumbers[0][public][private][0][0]['positive'] == 0:
            #                         resultNumbers[1][public][private][0][0]['sent'] = (str(resultNumbers[1][public][private][0][0]['sent']) + " (0%)")
            #                         resultNumbers[1][public][private][0][0]['opened'] = (str(resultNumbers[1][public][private][0][0]['opened']) + " (0%)")
            #                         resultNumbers[1][public][private][0][0]['linksClicked'] = (str(resultNumbers[1][public][private][0][0]['linksClicked']) + " (0%)")
            #                         resultNumbers[1][public][private][0][0]['negative'] = (str(resultNumbers[1][public][private][0][0]['negative']) + " (0%)")
            #                         resultNumbers[1][public][private][0][0]['rating'] = (str(resultNumbers[1][public][private][0][0]['rating']) + " (0%)")
            #                     else:
            #                         resultNumbers[1][public][private][0][0]['sent'] = (str(resultNumbers[1][public][private][0][0]['sent']) +
            #                             " (" + str(resultNumbers[1][public][private][0][0]['sent'] * 100 / resultNumbers[0][public][private][0][0]['positive']) + "%)")
            #                         resultNumbers[1][public][private][0][0]['opened'] = (str(resultNumbers[1][public][private][0][0]['opened']) +
            #                             " (" + str(resultNumbers[1][public][private][0][0]['opened'] * 100 / resultNumbers[0][public][private][0][0]['positive']) + "%)")
            #                         resultNumbers[1][public][private][0][0]['linksClicked'] = (str(resultNumbers[1][public][private][0][0]['linksClicked']) +
            #                             " (" + str(resultNumbers[1][public][private][0][0]['linksClicked'] * 100 / resultNumbers[0][public][private][0][0]['positive']) + "%)")
            #                         resultNumbers[1][public][private][0][0]['negative'] = (str(resultNumbers[1][public][private][0][0]['negative']) +
            #                             " (" + str(resultNumbers[1][public][private][0][0]['negative'] * 100 / resultNumbers[0][public][private][0][0]['positive']) + "%)")
            #                         resultNumbers[1][public][private][0][0]['rating'] = (str(resultNumbers[1][public][private][0][0]['rating']) +
            #                             " (" + str(resultNumbers[1][public][private][0][0]['rating'] * 100 / resultNumbers[0][public][private][0][0]['positive']) + "%)")
            #                     if resultNumbers[1][public][private][0][0]['comment'] == 0:
            #                         resultNumbers[2][public][private][0][0]['opened'] = (str(resultNumbers[2][public][private][0][0]['opened']) + " (0%)")
            #                         resultNumbers[2][public][private][0][0]['article_clicked'] = (str(resultNumbers[2][public][private][0][0]['article_clicked']) + " (0%)")
            #                         resultNumbers[2][public][private][0][0]['talkpage_clicked'] = (str(resultNumbers[2][public][private][0][0]['talkpage_clicked']) + " (0%)")
            #                         resultNumbers[2][public][private][0][0]['post_clicked'] = (str(resultNumbers[2][public][private][0][0]['post_clicked']) + " (0%)")
            #                         resultNumbers[2][public][private][0][0]['tutorial_clicked'] = (str(resultNumbers[2][public][private][0][0]['tutorial_clicked']) + " (0%)")
            #                     else:
            #                         resultNumbers[2][public][private][0][0]['opened'] = (str(resultNumbers[2][public][private][0][0]['opened']) +
            #                             " (" + str(resultNumbers[2][public][private][0][0]['opened'] * 100 / resultNumbers[1][public][private][0][0]['comment']) + "%)")
            #                         resultNumbers[2][public][private][0][0]['article_clicked'] = (str(resultNumbers[2][public][private][0][0]['article_clicked']) +
            #                             " (" + str(resultNumbers[2][public][private][0][0]['article_clicked'] * 100 / resultNumbers[1][public][private][0][0]['comment']) + "%)")
            #                         resultNumbers[2][public][private][0][0]['talkpage_clicked'] = (str(resultNumbers[2][public][private][0][0]['talkpage_clicked']) +
            #                             " (" + str(resultNumbers[2][public][private][0][0]['talkpage_clicked'] * 100 / resultNumbers[1][public][private][0][0]['comment']) + "%)")
            #                         resultNumbers[2][public][private][0][0]['post_clicked'] = (str(resultNumbers[2][public][private][0][0]['post_clicked']) +
            #                             " (" + str(resultNumbers[2][public][private][0][0]['post_clicked'] * 100 / resultNumbers[1][public][private][0][0]['comment']) + "%)")
            #                         resultNumbers[2][public][private][0][0]['tutorial_clicked'] = (str(resultNumbers[2][public][private][0][0]['tutorial_clicked']) +
            #                             " (" + str(resultNumbers[2][public][private][0][0]['tutorial_clicked'] * 100 / resultNumbers[1][public][private][0][0]['comment']) + "%)")
            #                     if resultNumbers[0][public][private][0][0]['positive'] == 0:
            #                         resultNumbers[1][public][private][0][0]['comment'] = (str(resultNumbers[1][public][private][0][0]['comment']) + " (0%)")
            #                     else:
            #                         resultNumbers[1][public][private][0][0]['comment'] = (str(resultNumbers[1][public][private][0][0]['comment']) +
            #                             " (" + str(resultNumbers[1][public][private][0][0]['comment'] * 100 / resultNumbers[0][public][private][0][0]['positive']) + "%)")
            #                     if resultNumbers[0][public][private][0][0]['sent'] == 0:
            #                         resultNumbers[0][public][private][0][0]['positive'] = (str(resultNumbers[0][public][private][0][0]['positive']) + " (0%)")
            #                     else:
            #                         resultNumbers[0][public][private][0][0]['positive'] = (str(resultNumbers[0][public][private][0][0]['positive']) +
            #                             " (" + str(resultNumbers[0][public][private][0][0]['positive'] * 100 / resultNumbers[0][public][private][0][0]['sent']) + "%)")
            #                     resultNumbers[0][public][private][0][0]['sent'] = str(resultNumbers[0][public][private][0][0]['sent'])
            #                     if relevance != 0 and citation == 0:
            #                         if resultNumbers[0][public][private][4][0]['sent'] == 0:
            #                             resultNumbers[0][public][private][4][0]['opened'] = (str(resultNumbers[0][public][private][4][0]['opened']) + " (0%)")
            #                             resultNumbers[0][public][private][4][0]['negative'] = (str(resultNumbers[0][public][private][4][0]['negative']) + " (0%)")
            #                         else:
            #                             resultNumbers[0][public][private][4][0]['opened'] = (str(resultNumbers[0][public][private][4][0]['opened']) +
            #                                 " (" + str(resultNumbers[0][public][private][4][0]['opened'] * 100 / resultNumbers[0][public][private][4][0]['sent']) + "%)")
            #                             resultNumbers[0][public][private][4][0]['negative'] = (str(resultNumbers[0][public][private][4][0]['negative']) +
            #                                 " (" + str(resultNumbers[0][public][private][4][0]['negative'] * 100 / resultNumbers[0][public][private][4][0]['sent']) + "%)")
            #                         if resultNumbers[0][public][private][4][0]['positive'] == 0:
            #                             resultNumbers[1][public][private][4][0]['sent'] = (str(resultNumbers[1][public][private][4][0]['sent']) + " (0%)")
            #                             resultNumbers[1][public][private][4][0]['opened'] = (str(resultNumbers[1][public][private][4][0]['opened']) + " (0%)")
            #                             resultNumbers[1][public][private][4][0]['linksClicked'] = (str(resultNumbers[1][public][private][4][0]['linksClicked']) + " (0%)")
            #                             resultNumbers[1][public][private][4][0]['negative'] = (str(resultNumbers[1][public][private][4][0]['negative']) + " (0%)")
            #                             resultNumbers[1][public][private][4][0]['rating'] = (str(resultNumbers[1][public][private][4][0]['rating']) + " (0%)")
            #                         else:
            #                             resultNumbers[1][public][private][4][0]['sent'] = (str(resultNumbers[1][public][private][4][0]['sent']) +
            #                                 " (" + str(resultNumbers[1][public][private][4][0]['sent'] * 100 / resultNumbers[0][public][private][4][0]['positive']) + "%)")
            #                             resultNumbers[1][public][private][4][0]['opened'] = (str(resultNumbers[1][public][private][4][0]['opened']) +
            #                                 " (" + str(resultNumbers[1][public][private][4][0]['opened'] * 100 / resultNumbers[0][public][private][4][0]['positive']) + "%)")
            #                             resultNumbers[1][public][private][4][0]['linksClicked'] = (str(resultNumbers[1][public][private][4][0]['linksClicked']) +
            #                                 " (" + str(resultNumbers[1][public][private][4][0]['linksClicked'] * 100 / resultNumbers[0][public][private][4][0]['positive']) + "%)")
            #                             resultNumbers[1][public][private][4][0]['negative'] = (str(resultNumbers[1][public][private][4][0]['negative']) +
            #                                 " (" + str(resultNumbers[1][public][private][4][0]['negative'] * 100 / resultNumbers[0][public][private][4][0]['positive']) + "%)")
            #                             resultNumbers[1][public][private][4][0]['rating'] = (str(resultNumbers[1][public][private][4][0]['rating']) +
            #                                 " (" + str(resultNumbers[1][public][private][4][0]['rating'] * 100 / resultNumbers[0][public][private][4][0]['positive']) + "%)")
            #                         if resultNumbers[1][public][private][4][0]['comment'] == 0:
            #                             resultNumbers[2][public][private][4][0]['opened'] = (str(resultNumbers[2][public][private][4][0]['opened']) + " (0%)")
            #                             resultNumbers[2][public][private][4][0]['article_clicked'] = (str(resultNumbers[2][public][private][4][0]['article_clicked']) + " (0%)")
            #                             resultNumbers[2][public][private][4][0]['talkpage_clicked'] = (str(resultNumbers[2][public][private][4][0]['talkpage_clicked']) + " (0%)")
            #                             resultNumbers[2][public][private][4][0]['post_clicked'] = (str(resultNumbers[2][public][private][4][0]['post_clicked']) + " (0%)")
            #                             resultNumbers[2][public][private][4][0]['tutorial_clicked'] = (str(resultNumbers[2][public][private][4][0]['tutorial_clicked']) + " (0%)")
            #                         else:
            #                             resultNumbers[2][public][private][4][0]['opened'] = (str(resultNumbers[2][public][private][4][0]['opened']) +
            #                                 " (" + str(resultNumbers[2][public][private][4][0]['opened'] * 100 / resultNumbers[1][public][private][4][0]['comment']) + "%)")
            #                             resultNumbers[2][public][private][4][0]['article_clicked'] = (str(resultNumbers[2][public][private][4][0]['article_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][4][0]['article_clicked'] * 100 / resultNumbers[1][public][private][4][0]['comment']) + "%)")
            #                             resultNumbers[2][public][private][4][0]['talkpage_clicked'] = (str(resultNumbers[2][public][private][4][0]['talkpage_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][4][0]['talkpage_clicked'] * 100 / resultNumbers[1][public][private][4][0]['comment']) + "%)")
            #                             resultNumbers[2][public][private][4][0]['post_clicked'] = (str(resultNumbers[2][public][private][4][0]['post_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][4][0]['post_clicked'] * 100 / resultNumbers[1][public][private][4][0]['comment']) + "%)")
            #                             resultNumbers[2][public][private][4][0]['tutorial_clicked'] = (str(resultNumbers[2][public][private][4][0]['tutorial_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][4][0]['tutorial_clicked'] * 100 / resultNumbers[1][public][private][4][0]['comment']) + "%)")
            #                         if resultNumbers[0][public][private][4][0]['positive'] == 0:
            #                             resultNumbers[1][public][private][4][0]['comment'] = (str(resultNumbers[1][public][private][4][0]['comment']) + " (0%)")
            #                         else:
            #                             resultNumbers[1][public][private][4][0]['comment'] = (str(resultNumbers[1][public][private][4][0]['comment']) +
            #                                 " (" + str(resultNumbers[1][public][private][4][0]['comment'] * 100 / resultNumbers[0][public][private][4][0]['positive']) + "%)")
            #                         if resultNumbers[0][public][private][4][0]['sent'] == 0:
            #                             resultNumbers[0][public][private][4][0]['positive'] = (str(resultNumbers[0][public][private][4][0]['positive']) + " (0%)")
            #                         else:
            #                             resultNumbers[0][public][private][4][0]['positive'] = (str(resultNumbers[0][public][private][4][0]['positive']) +
            #                                 " (" + str(resultNumbers[0][public][private][4][0]['positive'] * 100 / resultNumbers[0][public][private][4][0]['sent']) + "%)")
            #                         resultNumbers[0][public][private][4][0]['sent'] = str(resultNumbers[0][public][private][4][0]['sent'])
            #                     elif relevance == 0 and citation != 0:
            #                         if resultNumbers[0][public][private][0][4]['sent'] == 0:
            #                             resultNumbers[0][public][private][0][4]['opened'] = (str(resultNumbers[0][public][private][0][4]['opened']) + " (0%)")
            #                             resultNumbers[0][public][private][0][4]['negative'] = (str(resultNumbers[0][public][private][0][4]['negative']) + " (0%)")
            #                         else:
            #                             resultNumbers[0][public][private][0][4]['opened'] = (str(resultNumbers[0][public][private][0][4]['opened']) +
            #                                 " (" + str(resultNumbers[0][public][private][0][4]['opened'] * 100 / resultNumbers[0][public][private][0][4]['sent']) + "%)")
            #                             resultNumbers[0][public][private][0][4]['negative'] = (str(resultNumbers[0][public][private][0][4]['negative']) +
            #                                 " (" + str(resultNumbers[0][public][private][0][4]['negative'] * 100 / resultNumbers[0][public][private][0][4]['sent']) + "%)")
            #                         if resultNumbers[0][public][private][0][4]['positive'] == 0:
            #                             resultNumbers[1][public][private][0][4]['sent'] = (str(resultNumbers[1][public][private][0][4]['sent']) + " (0%)")
            #                             resultNumbers[1][public][private][0][4]['opened'] = (str(resultNumbers[1][public][private][0][4]['opened']) + " (0%)")
            #                             resultNumbers[1][public][private][0][4]['linksClicked'] = (str(resultNumbers[1][public][private][0][4]['linksClicked']) + " (0%)")
            #                             resultNumbers[1][public][private][0][4]['negative'] = (str(resultNumbers[1][public][private][0][4]['negative']) + " (0%)")
            #                             resultNumbers[1][public][private][0][4]['rating'] = (str(resultNumbers[1][public][private][0][4]['rating']) + " (0%)")
            #                         else:
            #                             resultNumbers[1][public][private][0][4]['sent'] = (str(resultNumbers[1][public][private][0][4]['sent']) +
            #                                 " (" + str(resultNumbers[1][public][private][0][4]['sent'] * 100 / resultNumbers[0][public][private][0][4]['positive']) + "%)")
            #                             resultNumbers[1][public][private][0][4]['opened'] = (str(resultNumbers[1][public][private][0][4]['opened']) +
            #                                 " (" + str(resultNumbers[1][public][private][0][4]['opened'] * 100 / resultNumbers[0][public][private][0][4]['positive']) + "%)")
            #                             resultNumbers[1][public][private][0][4]['linksClicked'] = (str(resultNumbers[1][public][private][0][4]['linksClicked']) +
            #                                 " (" + str(resultNumbers[1][public][private][0][4]['linksClicked'] * 100 / resultNumbers[0][public][private][0][4]['positive']) + "%)")
            #                             resultNumbers[1][public][private][0][4]['negative'] = (str(resultNumbers[1][public][private][0][4]['negative']) +
            #                                 " (" + str(resultNumbers[1][public][private][0][4]['negative'] * 100 / resultNumbers[0][public][private][0][4]['positive']) + "%)")
            #                             resultNumbers[1][public][private][0][4]['rating'] = (str(resultNumbers[1][public][private][0][4]['rating']) +
            #                                 " (" + str(resultNumbers[1][public][private][0][4]['rating'] * 100 / resultNumbers[0][public][private][0][4]['positive']) + "%)")
            #                         if resultNumbers[1][public][private][0][4]['comment'] == 0:
            #                             resultNumbers[2][public][private][0][4]['opened'] = (str(resultNumbers[2][public][private][0][4]['opened']) + " (0%)")
            #                             resultNumbers[2][public][private][0][4]['article_clicked'] = (str(resultNumbers[2][public][private][0][4]['article_clicked']) + " (0%)")
            #                             resultNumbers[2][public][private][0][4]['talkpage_clicked'] = (str(resultNumbers[2][public][private][0][4]['talkpage_clicked']) + " (0%)")
            #                             resultNumbers[2][public][private][0][4]['post_clicked'] = (str(resultNumbers[2][public][private][0][4]['post_clicked']) + " (0%)")
            #                             resultNumbers[2][public][private][0][4]['tutorial_clicked'] = (str(resultNumbers[2][public][private][0][4]['tutorial_clicked']) + " (0%)")
            #                         else:
            #                             resultNumbers[2][public][private][0][4]['opened'] = (str(resultNumbers[2][public][private][0][4]['opened']) +
            #                                 " (" + str(resultNumbers[2][public][private][0][4]['opened'] * 100 / resultNumbers[1][public][private][0][4]['comment']) + "%)")
            #                             resultNumbers[2][public][private][0][4]['article_clicked'] = (str(resultNumbers[2][public][private][0][4]['article_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][0][4]['article_clicked'] * 100 / resultNumbers[1][public][private][0][4]['comment']) + "%)")
            #                             resultNumbers[2][public][private][0][4]['talkpage_clicked'] = (str(resultNumbers[2][public][private][0][4]['talkpage_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][0][4]['talkpage_clicked'] * 100 / resultNumbers[1][public][private][0][4]['comment']) + "%)")
            #                             resultNumbers[2][public][private][0][4]['post_clicked'] = (str(resultNumbers[2][public][private][0][4]['post_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][0][4]['post_clicked'] * 100 / resultNumbers[1][public][private][0][4]['comment']) + "%)")
            #                             resultNumbers[2][public][private][0][4]['tutorial_clicked'] = (str(resultNumbers[2][public][private][0][4]['tutorial_clicked']) +
            #                                 " (" + str(resultNumbers[2][public][private][0][4]['tutorial_clicked'] * 100 / resultNumbers[1][public][private][0][4]['comment']) + "%)")
            #                         if resultNumbers[0][public][private][0][4]['positive'] == 0:
            #                             resultNumbers[1][public][private][0][4]['comment'] = (str(resultNumbers[1][public][private][0][4]['comment']) + " (0%)")
            #                         else:
            #                             resultNumbers[1][public][private][0][4]['comment'] = (str(resultNumbers[1][public][private][0][4]['comment']) +
            #                                 " (" + str(resultNumbers[1][public][private][0][4]['comment'] * 100 / resultNumbers[0][public][private][0][4]['positive']) + "%)")
            #                         if resultNumbers[0][public][private][0][4]['sent'] == 0:
            #                             resultNumbers[0][public][private][0][4]['positive'] = (str(resultNumbers[0][public][private][0][4]['positive']) + " (0%)")
            #                         else:
            #                             resultNumbers[0][public][private][0][4]['positive'] = (str(resultNumbers[0][public][private][0][4]['positive']) +
            #                                 " (" + str(resultNumbers[0][public][private][0][4]['positive'] * 100 / resultNumbers[0][public][private][0][4]['sent']) + "%)")
            #                         resultNumbers[0][public][private][0][4]['sent'] = str(resultNumbers[0][public][private][0][4]['sent'])
            
            return render_to_response("Results.html",
                {"resultNumbers":resultNumbers, "resultHoursNumbers":resultHoursNumbers, "resultWeekdaysNumbers":resultWeekdaysNumbers,
                "range": range(24), "rangeWeek": range(7), "totalEmail1Sent":totalEmail1Sent, "totalEmail1Opened":totalEmail1Opened, 
                "totalPositiveResponses":totalPositiveResponses, "totalNegative1Responses":totalNegative1Responses, 
                "totalEmail2Sent":totalEmail2Sent, "totalEmail2Opened":totalEmail2Opened, "totalLinksClickedNum":totalLinksClickedNum, 
                "totalNegative2Responses":totalNegative2Responses, "totalCommentsNum":totalCommentsNum, 
                "totalRatingsNum":totalRatingsNum, "totalRefereesNum":totalRefereesNum,
                "totalEmailCommunicationNum":totalEmailCommunicationNum, "totalEmail3Opened":totalEmail3Opened,
                "totalArticle_clicked":totalArticle_clicked, "totalTalkpage_clicked":totalTalkpage_clicked,
                "totalPost_clicked":totalPost_clicked, "totalTutorial_clicked":totalTutorial_clicked,
                "mapElements":mapElements, "version":version, },
                context_instance=RequestContext(request))


def csvrecommendations(request):

    if request.method == 'GET':
        response = '"Specialization","Affiliation","location","Phase 1","Phase 2","Phase 3"'
        response += ',"High View","Citation Benefit","Private Comes First","Acknowledgement","Likely to Cite","May Include Reference"'
        response += ',"Might Refer to","Likely to Cite + Acknowledgement","May Include Reference + Acknowledgement","Might Refer to + Acknowledgement"'
        response += ',"Especially popular","Highly visible","Highly popular","Interested","Email 1 Opened"'
        response += ',"Publication 1","Recommended Article URL 1"'
        response += ',"Publication 2","Recommended Article URL 2"'
        response += ',"Publication 3","Recommended Article URL 3"'
        response += ',"Publication 4","Recommended Article URL 4"'
        response += ',"Publication 5","Recommended Article URL 5"'
        response += ',"Publication 6","Recommended Article URL 6"'
        response += ',"Publication 7","Recommended Article URL 7"\n'

        allExperts = Expert.objects.all()

        for expert in allExperts:

            if expert.study_version == 2:
                email = expert.email
                firstname = expert.firstname
                lastname = expert.name
                expertwikipages = expert.expertwikipub_set.all()
                expertPk = expert.pk
                expertSpecialization = expert.specialization
                school = expert.school
                location = expert.location

                phase1 = expert.phase1
                phase2 = expert.phase2
                phase3 = expert.phase3
                inSpecialtyArea = expert.inspecialtyarea
                indiscipline = expert.indiscipline
                highviewspast90days = expert.highviewspast90days
                citedpublication = expert.citedpublication
                private_first = expert.private_first
                relevance_factor = expert.relevance_factor
                likely_to_cite = expert.likely_to_cite
                may_include_reference = expert.may_include_reference
                might_refer_to = expert.might_refer_to
                relevant_to_research = expert.relevant_to_research
                within_area = expert.within_area
                on_expertise_topic = expert.on_expertise_topic
                especially_popular = expert.especially_popular
                highly_visible = expert.highly_visible
                highly_popular = expert.highly_popular

                interested = expert.returned
                withdrawal = expert.withdrawal
                email1_opened = expert.email1_opened
                email2_opened = expert.email2_opened
                email3_opened = expert.email3_opened

                linksClickedNum = 0
                commentsNum = 0
                ratingsNum = 0
                ExpertwikipubrefereesNum = 0

                for expertwikipage in expertwikipages:
                    linksClickedNum += int(expertwikipage.link_clicked)
                    if expertwikipage.comment is not None and expertwikipage.comment != "":
                        commentsNum += 1
                    if expertwikipage.rating is not None and expertwikipage.rating != "":
                        ratingsNum += 1

                    Expertwikipubreferees = expertwikipage.expertwikipubreferee_set.all()
                    ExpertwikipubrefereesNum += len(Expertwikipubreferees)

                article_clicked = expert.article_clicked
                talkpage_clicked = expert.talkpage_clicked
                post_clicked = expert.post_clicked
                tutorial_clicked = expert.tutorial_clicked
                emailCommunication = expert.emailCommunication

                user_agent = expert.user_agent
                updated = expert.updated

                if (email is not None and email != '' and expertSpecialization is not None and expertSpecialization != "" and not indiscipline and
                    int(withdrawal) == 0 and int(email2_opened) == 0 and int(phase3) == 0 and int(email3_opened) == 0 and 
                    int(linksClickedNum) == 0 and int(commentsNum) == 0 and int(ratingsNum) == 0 and int(ExpertwikipubrefereesNum) == 0):
                    # response += '"' + str(expertPk) + '",'
                    # response += '"' + str(firstname) + '",'
                    # response += '"' + str(lastname) + '",'
                    response += '"' + str(expertSpecialization) + '",'
                    response += '"' + str(school) + '",'
                    response += '"' + str(location) + '",'

                    response += '"' + str(int(phase1)) + '",'
                    response += '"' + str(int(phase2)) + '",'
                    if phase3 is not None:
                        response += '"' + str(int(phase3)) + '",'
                    else:
                        response += '"0",'
                    response += '"' + str(int(highviewspast90days)) + '",'
                    response += '"' + str(int(citedpublication)) + '",'
                    response += '"' + str(int(private_first)) + '",'
                    response += '"' + str(int(relevance_factor)) + '",'
                    response += '"' + str(int(likely_to_cite)) + '",'
                    response += '"' + str(int(may_include_reference)) + '",'
                    response += '"' + str(int(might_refer_to)) + '",'
                    response += '"' + str(int(relevant_to_research)) + '",'
                    response += '"' + str(int(within_area)) + '",'
                    response += '"' + str(int(on_expertise_topic)) + '",'
                    response += '"' + str(int(especially_popular)) + '",'
                    response += '"' + str(int(highly_visible)) + '",'
                    response += '"' + str(int(highly_popular)) + '",'

                    response += '"' + str(int(interested)) + '",'
                    response += '"' + str(int(email1_opened)) + '"'

                    for expertwikipage in expertwikipages:
                        response += ',"' + str(expertwikipage.publication.title) + '",'
                        response += '"' + str(expertwikipage.wikipage.url) + '"'

                    response += '\n'

        result = HttpResponse(response, content_type='text/csv')
        result['Content-Disposition'] = 'attachment; filename="Main_Study_Recommendations.csv"'

        return result


def csvcomments(request):

    if request.method == 'GET':
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Main_Study_Comments.csv"'

        writer = csv.writer(response)

        responseRow = []
        responseRow.extend(["Participant ID", "Firstname", "Lastname", "Specialization", "Affiliation", "location", "Phase 1", "Phase 2", "Phase 3"])
        responseRow.extend(["High View", "Citation Benefit", "Private Comes First", "Acknowledgement", "Likely to Cite"])
        responseRow.extend(["May Include Reference", "Might Refer to", "Likely to Cite + Acknowledgement"])
        responseRow.extend(["May Include Reference + Acknowledgement", "Might Refer to + Acknowledgement", "Especially popular"])
        responseRow.extend(["Highly visible", "Highly popular", "Manual Recommendation", "Track changed", "Inappropriate Comment"])
        responseRow.extend(["Interested", "Withdrawal", "Email 1 Opened", "Email 2 Opened", "Email 3 Opened"])
        responseRow.extend(["Econ Wikiproject Clicked", "Email Communication", "User Agent"])
        responseRow.extend(["Publication", "Wikipage URL", "Edit Protection Level", "Quality Class", "Importance Class"])
        responseRow.extend(["Page Length", "Watchers", "Last Edit Time", "Creation Time", "Redirects", "Total Edits"])
        responseRow.extend(["Distinct Authors", "Last Month Total Edits", "# of Views over the past month", "External Hyperlinks"])
        responseRow.extend(["Link Clicked", "Recommendation Order", "Rating", "# of Experts Referred to", "Submitted to the Talk page"])
        responseRow.extend(["Comment Length", "Word Count", "Link to the Post on the Talk page", "Clicked Article", "Clicked Post"])
        responseRow.extend(["Clicked Tutorial", "# of Comments"])
        writer.writerow(responseRow)

        allExperts = Expert.objects.all()

        for expert in allExperts:

            if expert.study_version == 2:
                # expertwikipages = expert.expertwikipub_set.all().order_by('updated')
                expertwikipages = expert.expertwikipub_set.all()
                expertwikipagesOrdered = sorted(expertwikipages, key = lambda x: x.related_publications_number, reverse=True)
                wikipageslist = []

                rowcounter = 0
                for expertwikipage in expertwikipagesOrdered:
                    wikipage = expertwikipage.wikipage

                    if (not wikipage in wikipageslist) and wikipage.edit_protection_level == "None":
                        rowcounter = rowcounter + 1
                        if rowcounter <= 6:
                            wikipageslist.append(wikipage)

                            # if expertwikipage.comment is not None and expertwikipage.comment != "":
                            responseRow = []
                            responseRow.append(str(expert.pk))
                            responseRow.append(str(expert.firstname))
                            responseRow.append(str(expert.name))
                            responseRow.append(str(expert.specialization))
                            responseRow.append(str(expert.school))
                            responseRow.append(str(expert.location))

                            if expert.phase1 is not None:
                                responseRow.append(str(int(expert.phase1)))
                            else:
                                responseRow.append("0")
                            if expert.phase2 is not None:
                                responseRow.append(str(int(expert.phase2)))
                            else:
                                responseRow.append("0")
                            if expert.phase3 is not None:
                                responseRow.append(str(int(expert.phase3)))
                            else:
                                responseRow.append("0")
                            responseRow.append(str(int(expert.highviewspast90days)))
                            responseRow.append(str(int(expert.citedpublication)))
                            responseRow.append(str(int(expert.private_first)))
                            responseRow.append(str(int(expert.relevance_factor)))
                            responseRow.append(str(int(expert.likely_to_cite)))
                            responseRow.append(str(int(expert.may_include_reference)))
                            responseRow.append(str(int(expert.might_refer_to)))
                            responseRow.append(str(int(expert.relevant_to_research)))
                            responseRow.append(str(int(expert.within_area)))
                            responseRow.append(str(int(expert.on_expertise_topic)))
                            responseRow.append(str(int(expert.especially_popular)))
                            responseRow.append(str(int(expert.highly_visible)))
                            responseRow.append(str(int(expert.highly_popular)))
                            manualRecommendation = False
                            if expert.HIndex == 10:
                                manualRecommendation = True
                            responseRow.append(str(int(manualRecommendation)))
                            responseRow.append(str(int(expertwikipage.approvedbywikipedians)))
                            responseRow.append(str(int(expertwikipage.rejectedbywikipedians)))

                            responseRow.append(str(int(expert.returned)))
                            responseRow.append(str(int(expert.withdrawal)))
                            responseRow.append(str(int(expert.email1_opened)))
                            responseRow.append(str(int(expert.email2_opened)))
                            responseRow.append(str(int(expert.email3_opened)))

                            responseRow.append(str(int(expert.econ_wikiproject_clicked)))
                            responseRow.append(str(int(expert.emailCommunication)))
                            responseRow.append(str(expert.user_agent))

                            responseRow.append(str(expertwikipage.publication.title))
                            responseRow.append(str(expertwikipage.wikipage.url))
                            if expertwikipage.wikipage.edit_protection_level is not None and expertwikipage.wikipage.edit_protection_level != "":
                                responseRow.append(str(expertwikipage.wikipage.edit_protection_level))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.quality_class is not None and expertwikipage.wikipage.quality_class != "":
                                responseRow.append(str(expertwikipage.wikipage.quality_class))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.importance_class is not None and expertwikipage.wikipage.importance_class != "":
                                responseRow.append(str(expertwikipage.wikipage.importance_class))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.page_length is not None and expertwikipage.wikipage.page_length != "":
                                responseRow.append(str(expertwikipage.wikipage.page_length))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.watchers is not None and expertwikipage.wikipage.watchers != "":
                                responseRow.append(str(expertwikipage.wikipage.watchers))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.last_edit_time is not None and expertwikipage.wikipage.last_edit_time != "":
                                responseRow.append(str(expertwikipage.wikipage.last_edit_time))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.creation_time is not None and expertwikipage.wikipage.creation_time != "":
                                responseRow.append(str(expertwikipage.wikipage.creation_time))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.redirects is not None and expertwikipage.wikipage.redirects != "":
                                responseRow.append(str(expertwikipage.wikipage.redirects))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.total_edits is not None and expertwikipage.wikipage.total_edits != "":
                                responseRow.append(str(expertwikipage.wikipage.total_edits))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.distinct_authors is not None and expertwikipage.wikipage.distinct_authors != "":
                                responseRow.append(str(expertwikipage.wikipage.distinct_authors))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.last_month_total_edits is not None and expertwikipage.wikipage.last_month_total_edits != "":
                                responseRow.append(str(expertwikipage.wikipage.last_month_total_edits))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.views_last_90_days is not None and expertwikipage.wikipage.views_last_90_days != "":
                                responseRow.append(str(expertwikipage.wikipage.views_last_90_days))
                            else:
                                responseRow.append("")
                            if expertwikipage.wikipage.external_hyperlinks is not None and expertwikipage.wikipage.external_hyperlinks != "":
                                responseRow.append(str(expertwikipage.wikipage.external_hyperlinks))
                            else:
                                responseRow.append("")
                            if expertwikipage.link_clicked is not None and expertwikipage.link_clicked != "":
                                responseRow.append(str(int(expertwikipage.link_clicked)))
                            else:
                                responseRow.append("")
                            responseRow.append(str(rowcounter))
                            if expertwikipage.rating is not None and expertwikipage.rating != "":
                                responseRow.append(str(expertwikipage.rating))
                            else:
                                responseRow.append("")
                            responseRow.append(str(expertwikipage.expertwikipubreferee_set.count()))
                            # responseRow.append(convert_unicode(expertwikipage.comment))
                            responseRow.append(str(int(expertwikipage.submittedtotalkpage)))
                            commentLength = 0
                            commentWordCount = 0
                            if expertwikipage.comment is not None:
                                commentLength = len(expertwikipage.comment)
                                commentWords = re.findall(r"[\w']+", expertwikipage.comment)
                                commentWordCount = len(commentWords)
                            responseRow.append(str(commentLength))
                            responseRow.append(str(commentWordCount))
                            talkPageHyperlink, postHyperlink = findArticleTalkPageAndPost(expert.name,
                                                                                          expertwikipage.wikipage.title,
                                                                                          expertwikipage.wikipage.url)
                            responseRow.append(postHyperlink)
                            responseRow.append(str(int(expert.article_clicked)))
                            responseRow.append(str(int(expert.post_clicked)))
                            responseRow.append(str(int(expert.tutorial_clicked)))
                            commentsNum = Expertwikipub.objects.filter(wikipage__url=expertwikipage.wikipage.url,
                                                                       submittedtotalkpage=True).count()
                            responseRow.append(str(commentsNum))

                            writer.writerow(responseRow)

        return response


def csvresults(request):

    if request.method == 'GET':
        if 'version' in request.GET and request.GET['version'] != '' and 'key' in request.GET and request.GET['key'] != '':
            version = num(request.GET['version'])
            session_key = request.GET['key']

            if session_key != "":
                s = SessionStore(session_key=session_key)
                s['progressPercent'] == 0.0
                s.save()

            if version == 0:
                response = '"User ID","Domain","Specialization","Affiliation","Location","Phase 1","Phase 2","Phase 3"'
                response += ',"Public Benefit","Private Benefit","Interested","Withdrawal","Email 1 Opened","Email 2 Opened"'
                response += ',"Email 3 Opened","# Links Clicked","# Comments","# Ratings","# Expertsrefered","Email Communication"'
                response += ',"# Articles Clicked","# Talkpages Clicked","# Posts Clicked","# Tutorials Clicked"'
                response += ',"Email 1 Sent Hour","Email 2 Sent Hour","Email 3 Sent Hour","Email 1 Opened Hour","Email 2 Opened Hour"'
                response += ',"Email 3 Opened Hour","Comment Hour","Email 1 Sent Weekday","Email 2 Sent Weekday","Email 3 Sent Weekday"'
                response += ',"Email 1 Opened Weekday","Email 2 Opened Weekday","Email 3 Opened Weekday","Comment Weekday"'
                response += ',"Email 1 Sent Year","Email 2 Sent Year","Email 3 Sent Year","Email 1 Opened Year","Email 2 Opened Year"'
                response += ',"Email 3 Opened Year","Comment Year","Email 1 Sent Month","Email 2 Sent Month","Email 3 Sent Month"'
                response += ',"Email 1 Opened Month","Email 2 Opened Month","Email 3 Opened Month","Comment Month","Email 1 Sent Day"'
                response += ',"Email 2 Sent Day","Email 3 Sent Day","Email 1 Opened Day","Email 2 Opened Day","Email 3 Opened Day"'
                response += ',"Comment Day","User Agent"\n'
            elif version == 1:
                response = '"User ID","Domain","Specialization","Affiliation","Location","Phase 1","Phase 2","Phase 3"'
                response += ',"Public Benefit","Private Benefit","Relevance Factor","Likely to Cite","May Include Reference"'
                response += ',"Might Refer to","Relevant to Research","Within Your Area","On Expertise Topic"'
                response += ',"Interested","Withdrawal","Email 1 Opened","Email 2 Opened","Email 3 Opened"'
                response += ',"# Links Clicked","# Comments","# Ratings","# Expertsrefered","Email Communication"'
                response += ',"# Articles Clicked","# Talkpages Clicked","# Posts Clicked","# Tutorials Clicked"'
                response += ',"Email 1 Sent Hour","Email 2 Sent Hour","Email 3 Sent Hour","Email 1 Opened Hour","Email 2 Opened Hour"'
                response += ',"Email 3 Opened Hour","Comment Hour","Email 1 Sent Weekday","Email 2 Sent Weekday","Email 3 Sent Weekday"'
                response += ',"Email 1 Opened Weekday","Email 2 Opened Weekday","Email 3 Opened Weekday","Comment Weekday"'
                response += ',"Email 1 Sent Year","Email 2 Sent Year","Email 3 Sent Year","Email 1 Opened Year","Email 2 Opened Year"'
                response += ',"Email 3 Opened Year","Comment Year","Email 1 Sent Month","Email 2 Sent Month","Email 3 Sent Month"'
                response += ',"Email 1 Opened Month","Email 2 Opened Month","Email 3 Opened Month","Comment Month","Email 1 Sent Day"'
                response += ',"Email 2 Sent Day","Email 3 Sent Day","Email 1 Opened Day","Email 2 Opened Day","Email 3 Opened Day"'
                response += ',"Comment Day","User Agent"\n'
            elif version == 2:
                response = '"User ID","Firstname","Lastname","Domain","Specialization","Affiliation","Location","Phase 1","Phase 2","Phase 3"'
                response += ',"High View","Citation Benefit","Private Comes First","Acknowledgement","Likely to Cite","May Include Reference"'
                response += ',"Might Refer to","Likely to Cite + Acknowledgement","May Include Reference + Acknowledgement","Might Refer to + Acknowledgement"'
                response += ',"Especially popular","Highly visible","Highly popular"'
                response += ',"Interested","Withdrawal","Econ Project Clicked","Email 1 Opened","Email 2 Opened","Email 3 Opened"'
                response += ',"# Links Clicked","# Comments","# Ratings","# Expertsrefered","Email Communication"'
                response += ',"# Articles Clicked","# Talkpages Clicked","# Posts Clicked","# Tutorials Clicked"'
                response += ',"Email 1 Sent Hour","Email 2 Sent Hour","Email 3 Sent Hour","Email 1 Opened Hour","Email 2 Opened Hour"'
                response += ',"Email 3 Opened Hour","Comment Hour","Email 1 Sent Weekday","Email 2 Sent Weekday","Email 3 Sent Weekday"'
                response += ',"Email 1 Opened Weekday","Email 2 Opened Weekday","Email 3 Opened Weekday","Comment Weekday"'
                response += ',"Email 1 Sent Year","Email 2 Sent Year","Email 3 Sent Year","Email 1 Opened Year","Email 2 Opened Year"'
                response += ',"Email 3 Opened Year","Comment Year","Email 1 Sent Month","Email 2 Sent Month","Email 3 Sent Month"'
                response += ',"Email 1 Opened Month","Email 2 Opened Month","Email 3 Opened Month","Comment Month","Email 1 Sent Day"'
                response += ',"Email 2 Sent Day","Email 3 Sent Day","Email 1 Opened Day","Email 2 Opened Day","Email 3 Opened Day"'
                response += ',"Comment Day","User Agent","# of Phase 1 Emails","# of Phase 2 Emails","# of Phase 3 Emails"'
                response += ',"Total length of comments","Total number of words","Total rating","Total length of Wikipedia articles","Total Quality Class"'
                response += ',"Total Importance Class","Total Watchers","Total Redirects","Total Total Edits","Total # of Views over the Past Month"'
                response += ',"Average length of comments","Average number of words","Average rating","Average length of Wikipedia articles","Average Quality Class"'
                response += ',"Average Importance Class","Average Watchers","Average Redirects","Average Total Edits","Average # of Views over the Past Month"'
                response += ',"Max length of comments","Max number of words","Max rating","Max length of Wikipedia articles","Max Quality Class"'
                response += ',"Max Importance Class","Max Watchers","Max Redirects","Max Total Edits","Max # of Views over the Past Month"'
                response += ',"Manual Recommendation","location"'
                response += ',"publication 1","Wikipedia URL 1","length of comment 1","number of words 1","rating 1","length of Wikipedia article 1","Quality Class 1"'
                response += ',"Importance Class 1","Watchers 1","Redirects 1","Total Edits 1","# of Views over the Past Month 1","Track changed 1","Inappropriate Comment 1"'
                response += ',"publication 2","Wikipedia URL 2","length of comment 2","number of words 2","rating 2","length of Wikipedia article 2","Quality Class 2"'
                response += ',"Importance Class 2","Watchers 2","Redirects 2","Total Edits 2","# of Views over the Past Month 2","Track changed 2","Inappropriate Comment 2"'
                response += ',"publication 3","Wikipedia URL 3","length of comment 3","number of words 3","rating 3","length of Wikipedia article 3","Quality Class 3"'
                response += ',"Importance Class 3","Watchers 3","Redirects 3","Total Edits 3","# of Views over the Past Month 3","Track changed 3","Inappropriate Comment 3"'
                response += ',"publication 4","Wikipedia URL 4","length of comment 4","number of words 4","rating 4","length of Wikipedia article 4","Quality Class 4"'
                response += ',"Importance Class 4","Watchers 4","Redirects 4","Total Edits 4","# of Views over the Past Month 4","Track changed 4","Inappropriate Comment 4"'
                response += ',"publication 5","Wikipedia URL 5","length of comment 5","number of words 5","rating 5","length of Wikipedia article 5","Quality Class 5"'
                response += ',"Importance Class 5","Watchers 5","Redirects 5","Total Edits 5","# of Views over the Past Month 5","Track changed 5","Inappropriate Comment 5"'
                response += ',"publication 6","Wikipedia URL 6","length of comment 6","number of words 6","rating 6","length of Wikipedia article 6","Quality Class 6"'
                response += ',"Importance Class 6","Watchers 6","Redirects 6","Total Edits 6","# of Views over the Past Month 6","Track changed 6","Inappropriate Comment 6"'
                response += '\n'

            allExperts = Expert.objects.all()

            expertNum = 0.00

            for expert in allExperts:
                expertNum += 1.00

                study_version = expert.study_version
                if version == study_version:
                    expertwikipages = expert.expertwikipub_set.all()
                    expertPk = expert.pk
                    email = expert.email
                    expertDomain = expert.domain
                    expertSpecialization = expert.specialization
                    school = expert.school
                    location = expert.location

                    latitude, longitude, timeZoneObj = findTimeZoneObj(location)

                    phase1 = expert.phase1
                    phase2 = expert.phase2
                    phase3 = expert.phase3
                    inSpecialtyArea = expert.inspecialtyarea
                    indiscipline = expert.indiscipline
                    highviewspast90days = expert.highviewspast90days
                    citedpublication = expert.citedpublication
                    if version == 1:
                        relevance_factor = expert.relevance_factor
                        likely_to_cite = expert.likely_to_cite
                        may_include_reference = expert.may_include_reference
                        might_refer_to = expert.might_refer_to
                        relevant_to_research = expert.relevant_to_research
                        within_area = expert.within_area
                        on_expertise_topic = expert.on_expertise_topic

                    if version == 2:
                        private_first = expert.private_first
                        relevance_factor = expert.relevance_factor
                        likely_to_cite = expert.likely_to_cite
                        may_include_reference = expert.may_include_reference
                        might_refer_to = expert.might_refer_to
                        relevant_to_research = expert.relevant_to_research
                        within_area = expert.within_area
                        on_expertise_topic = expert.on_expertise_topic
                        especially_popular = expert.especially_popular
                        highly_visible = expert.highly_visible
                        highly_popular = expert.highly_popular

                    (latitude, longitude, timeZoneObj, emailSentH, email1SentH, email2SentH,
                        email3SentH, email1OpenedTimeH, email2OpenedTimeH, email3OpenedTimeH, commentTimeH, emailSentW, email1SentW,
                        email2SentW, email3SentW, email1OpenedTimeW, email2OpenedTimeW, email3OpenedTimeW, commentTimeW,
                        emailSentYear, email1SentYear, email2SentYear, email3SentYear, email1OpenedYear, email2OpenedYear,
                        email3OpenedYear, commentYear, emailSentMonth, email1SentMonth, email2SentMonth, email3SentMonth,
                        email1OpenedMonth, email2OpenedMonth, email3OpenedMonth, commentMonth, emailSentDay, email1SentDay,
                        email2SentDay, email3SentDay, email1OpenedDay, email2OpenedDay, email3OpenedDay,
                        commentDay) = dateTimeStats(expert, location)

                    interested = expert.returned
                    withdrawal = expert.withdrawal
                    email1_opened = expert.email1_opened
                    email2_opened = expert.email2_opened
                    email3_opened = expert.email3_opened
                    # email1OpenedTime = expert.email1OpenedTime
                    # email2OpenedTime = expert.email2OpenedTime

                    linksClickedNum = 0
                    commentsNum = 0
                    ratingsNum = 0
                    ExpertwikipubrefereesNum = 0
                    totalCommentLength = 0
                    totalCommentWordCount = 0
                    totalRating = 0
                    totalArticlesLength = 0
                    totalQualityClass = 0
                    totalImportanceClass = 0
                    totalWatchers = 0
                    totalRedirects = 0
                    totalTotalEdits = 0
                    totalViews = 0
                    numOfRating = 0.0
                    numOfArticlesLength = 0.0
                    numOfQualityClass = 0.0
                    numOfImportanceClass = 0.0
                    numOfWatchers = 0.0
                    numOfRedirects = 0.0
                    numOfTotalEdits = 0.0
                    numOfViews = 0.0
                    averageCommentLength = 0
                    averageCommentWordCount = 0
                    averageRating = 0
                    averageArticlesLength = 0
                    averageQualityClass = 0
                    averageImportanceClass = 0
                    averageWatchers = 0
                    averageRedirects = 0
                    averageTotalEdits = 0
                    averageViews = 0
                    maxCommentLength = 0
                    maxCommentWordCount = 0
                    maxRating = 0
                    maxArticlesLength = 0
                    maxQualityClass = 0
                    maxImportanceClass = 0
                    maxWatchers = 0
                    maxRedirects = 0
                    maxTotalEdits = 0
                    maxViews = 0

                    expertwikipagesOrdered = sorted(expertwikipages, key = lambda x: x.related_publications_number, reverse=True)
                    wikipageslist = []

                    rowcounter = 0
                    for expertwikipage in expertwikipagesOrdered:
                        wikipage = expertwikipage.wikipage

                        if (not wikipage in wikipageslist) and wikipage.edit_protection_level == "None":
                            rowcounter = rowcounter + 1
                            if rowcounter <= 6:
                                wikipageslist.append(wikipage)

                                if expertwikipage.wikipage.page_length != None and expertwikipage.wikipage.page_length != "":
                                    numOfArticlesLength += 1
                                    totalArticlesLength += expertwikipage.wikipage.page_length
                                    if maxArticlesLength < expertwikipage.wikipage.page_length:
                                        maxArticlesLength = expertwikipage.wikipage.page_length

                                qualityClass = 0
                                if expertwikipage.wikipage.quality_class != None and expertwikipage.wikipage.quality_class != "":
                                    numOfQualityClass += 1
                                if expertwikipage.wikipage.quality_class == "FA-Class":
                                    qualityClass = 5
                                elif expertwikipage.wikipage.quality_class == "GA-Class":
                                    qualityClass = 4
                                elif expertwikipage.wikipage.quality_class == "B-Class":
                                    qualityClass = 3
                                elif expertwikipage.wikipage.quality_class == "C-Class":
                                    qualityClass = 2
                                elif expertwikipage.wikipage.quality_class == "Start-Class":
                                    qualityClass = 1
                                totalQualityClass += qualityClass
                                if maxQualityClass < qualityClass:
                                    maxQualityClass = qualityClass

                                importanceClass = 0
                                if expertwikipage.wikipage.importance_class != None and expertwikipage.wikipage.importance_class != "":
                                    numOfImportanceClass += 1
                                if expertwikipage.wikipage.importance_class == "Top-importance":
                                    importanceClass = 7
                                elif expertwikipage.wikipage.importance_class == "High-importance":
                                    importanceClass = 6
                                elif expertwikipage.wikipage.importance_class == "Mid-importancee":
                                    importanceClass = 5
                                elif expertwikipage.wikipage.importance_class == "Low-importance":
                                    importanceClass = 4
                                elif expertwikipage.wikipage.importance_class == "NA-importance":
                                    importanceClass = 3
                                elif expertwikipage.wikipage.importance_class == "Unknown-importance":
                                    importanceClass = 2
                                elif expertwikipage.wikipage.importance_class == "No-Class":
                                    importanceClass = 1
                                totalImportanceClass += importanceClass
                                if maxImportanceClass < importanceClass:
                                    maxImportanceClass = importanceClass

                                if expertwikipage.wikipage.watchers is not None and expertwikipage.wikipage.watchers != "":
                                    numOfWatchers += 1
                                    totalWatchers += expertwikipage.wikipage.watchers
                                    if maxWatchers < expertwikipage.wikipage.watchers:
                                        maxWatchers = expertwikipage.wikipage.watchers
                                if expertwikipage.wikipage.redirects is not None and expertwikipage.wikipage.redirects != "":
                                    numOfRedirects += 1
                                    totalRedirects += expertwikipage.wikipage.redirects
                                    if maxRedirects < expertwikipage.wikipage.redirects:
                                        maxRedirects = expertwikipage.wikipage.redirects
                                if expertwikipage.wikipage.total_edits is not None and expertwikipage.wikipage.total_edits != "":
                                    numOfTotalEdits += 1
                                    totalTotalEdits += expertwikipage.wikipage.total_edits
                                    if maxTotalEdits < expertwikipage.wikipage.total_edits:
                                        maxTotalEdits = expertwikipage.wikipage.total_edits

                                if expertwikipage.wikipage.views_last_90_days is not None and expertwikipage.wikipage.views_last_90_days != "":
                                    numOfViews += 1
                                    totalViews += expertwikipage.wikipage.views_last_90_days
                                    if maxViews < expertwikipage.wikipage.views_last_90_days:
                                        maxViews = expertwikipage.wikipage.views_last_90_days

                                linksClickedNum += int(expertwikipage.link_clicked)
                                if expertwikipage.comment is not None and expertwikipage.comment != "":
                                    commentsNum += 1
                                    totalCommentLength += len(expertwikipage.comment)
                                    commentWords = re.findall(r"[\w']+", expertwikipage.comment)
                                    totalCommentWordCount = len(commentWords)
                                    if maxCommentLength < len(expertwikipage.comment):
                                        maxCommentLength = len(expertwikipage.comment)
                                    if maxCommentWordCount < len(commentWords):
                                        maxCommentWordCount = len(commentWords)

                                if expertwikipage.rating is not None and expertwikipage.rating != "":
                                    totalRating += expertwikipage.rating
                                    if maxRating < expertwikipage.rating:
                                        maxRating = expertwikipage.rating
                                    ratingsNum += 1

                                Expertwikipubreferees = expertwikipage.expertwikipubreferee_set.all()
                                ExpertwikipubrefereesNum += len(Expertwikipubreferees)

                    if commentsNum != 0:
                        averageCommentLength = totalCommentLength / commentsNum
                        averageCommentWordCount = totalCommentWordCount / commentsNum
                    else:
                        averageCommentLength = 0
                    if ratingsNum != 0:
                        averageRating = totalRating / ratingsNum
                    else:
                        averageRating = 0
                    if numOfArticlesLength != 0:
                        averageArticlesLength = totalArticlesLength / numOfArticlesLength
                    else:
                        averageArticlesLength = 0
                    if numOfQualityClass != 0:
                        averageQualityClass = totalQualityClass / numOfQualityClass
                    else:
                        averageQualityClass = 0
                    if numOfImportanceClass != 0:
                        averageImportanceClass = totalImportanceClass / numOfImportanceClass
                    else:
                        averageImportanceClass = 0
                    if numOfWatchers != 0:
                        averageWatchers = totalWatchers / numOfWatchers
                    else:
                        averageWatchers = 0
                    if numOfRedirects != 0:
                        averageRedirects = totalRedirects / numOfRedirects
                    else:
                        averageRedirects = 0
                    if numOfTotalEdits != 0:
                        averageTotalEdits = totalTotalEdits / numOfTotalEdits
                    else:
                        averageTotalEdits = 0
                    if numOfViews != 0:
                        averageViews = totalViews / numOfViews
                    else:
                        averageViews = 0

                    manualRecommendation = False
                    if expert.HIndex == 10:
                        manualRecommendation = True

                    article_clicked = expert.article_clicked
                    talkpage_clicked = expert.talkpage_clicked
                    post_clicked = expert.post_clicked
                    tutorial_clicked = expert.tutorial_clicked
                    emailCommunication = expert.emailCommunication

                    user_agent = expert.user_agent
                    location = expert.location
                    email1Count = expert.email1Count
                    email2Count = expert.email2Count
                    email3Count = expert.email3Count

                    if email is not None and email != '' and expertSpecialization is not None and expertSpecialization != "" and not indiscipline:
                        response += '"' + str(expertPk) + '",'
                        response += '"' + str(expert.firstname) + '",'
                        response += '"' + str(expert.name) + '",'
                        response += '"' + str(expertDomain) + '",'
                        response += '"' + str(expertSpecialization) + '",'
                        response += '"' + str(school) + '",'
                        response += '"' + str(location) + '",'

                        response += '"' + str(int(phase1)) + '",'
                        response += '"' + str(int(phase2)) + '",'
                        if phase3 is not None:
                            response += '"' + str(int(phase3)) + '",'
                        else:
                            response += '"0",'
                        response += '"' + str(int(highviewspast90days)) + '",'
                        response += '"' + str(int(citedpublication)) + '",'
                        if version == 2:
                            response += '"' + str(int(private_first)) + '",'
                        if version == 1 or version == 2:
                            response += '"' + str(int(relevance_factor)) + '",'
                            response += '"' + str(int(likely_to_cite)) + '",'
                            response += '"' + str(int(may_include_reference)) + '",'
                            response += '"' + str(int(might_refer_to)) + '",'
                            response += '"' + str(int(relevant_to_research)) + '",'
                            response += '"' + str(int(within_area)) + '",'
                            response += '"' + str(int(on_expertise_topic)) + '",'
                        if version == 2:
                            response += '"' + str(int(especially_popular)) + '",'
                            response += '"' + str(int(highly_visible)) + '",'
                            response += '"' + str(int(highly_popular)) + '",'

                        response += '"' + str(int(interested)) + '",'
                        response += '"' + str(int(withdrawal)) + '",'
                        response += '"' + str(int(expert.econ_wikiproject_clicked)) + '",'
                        response += '"' + str(int(email1_opened)) + '",'
                        response += '"' + str(int(email2_opened)) + '",'
                        response += '"' + str(int(email3_opened)) + '",'

                        response += '"' + str(int(linksClickedNum)) + '",'
                        response += '"' + str(int(commentsNum)) + '",'
                        response += '"' + str(int(ratingsNum)) + '",'
                        response += '"' + str(int(ExpertwikipubrefereesNum)) + '",'
                        response += '"' + str(int(emailCommunication)) + '",'

                        response += '"' + str(int(article_clicked)) + '",'
                        response += '"' + str(int(talkpage_clicked)) + '",'
                        response += '"' + str(int(post_clicked)) + '",'
                        response += '"' + str(int(tutorial_clicked)) + '",'

                        response += '"' + str(email1SentH) + '",'
                        response += '"' + str(email2SentH) + '",'
                        response += '"' + str(email3SentH) + '",'
                        response += '"' + str(email1OpenedTimeH) + '",'
                        response += '"' + str(email2OpenedTimeH) + '",'
                        response += '"' + str(email3OpenedTimeH) + '",'
                        response += '"' + str(commentTimeH) + '",'
                        response += '"' + str(email1SentW) + '",'
                        response += '"' + str(email2SentW) + '",'
                        response += '"' + str(email3SentW) + '",'
                        response += '"' + str(email1OpenedTimeW) + '",'
                        response += '"' + str(email2OpenedTimeW) + '",'
                        response += '"' + str(email3OpenedTimeW) + '",'
                        response += '"' + str(commentTimeW) + '",'
                        response += '"' + str(email1SentYear) + '",'
                        response += '"' + str(email2SentYear) + '",'
                        response += '"' + str(email3SentYear) + '",'
                        response += '"' + str(email1OpenedYear) + '",'
                        response += '"' + str(email2OpenedYear) + '",'
                        response += '"' + str(email3OpenedYear) + '",'
                        response += '"' + str(commentYear) + '",'
                        response += '"' + str(email1SentMonth) + '",'
                        response += '"' + str(email2SentMonth) + '",'
                        response += '"' + str(email3SentMonth) + '",'
                        response += '"' + str(email1OpenedMonth) + '",'
                        response += '"' + str(email2OpenedMonth) + '",'
                        response += '"' + str(email3OpenedMonth) + '",'
                        response += '"' + str(commentMonth) + '",'
                        response += '"' + str(email1SentDay) + '",'
                        response += '"' + str(email2SentDay) + '",'
                        response += '"' + str(email3SentDay) + '",'
                        response += '"' + str(email1OpenedDay) + '",'
                        response += '"' + str(email2OpenedDay) + '",'
                        response += '"' + str(email3OpenedDay) + '",'
                        response += '"' + str(commentDay) + '",'

                        response += '"' + str(user_agent) + '",'
                        response += '"' + str(email1Count) + '",'
                        response += '"' + str(email2Count) + '",'
                        response += '"' + str(email3Count) + '",'

                        response += '"' + str(totalCommentLength) + '",'
                        response += '"' + str(totalCommentWordCount) + '",'
                        response += '"' + str(totalRating) + '",'
                        response += '"' + str(totalArticlesLength) + '",'
                        response += '"' + str(totalQualityClass) + '",'
                        response += '"' + str(totalImportanceClass) + '",'
                        response += '"' + str(totalWatchers) + '",'
                        response += '"' + str(totalRedirects) + '",'
                        response += '"' + str(totalTotalEdits) + '",'
                        response += '"' + str(totalViews) + '",'

                        response += '"' + str(averageCommentLength) + '",'
                        response += '"' + str(averageCommentWordCount) + '",'
                        response += '"' + str(averageRating) + '",'
                        response += '"' + str(averageArticlesLength) + '",'
                        response += '"' + str(averageQualityClass) + '",'
                        response += '"' + str(averageImportanceClass) + '",'
                        response += '"' + str(averageWatchers) + '",'
                        response += '"' + str(averageRedirects) + '",'
                        response += '"' + str(averageTotalEdits) + '",'
                        response += '"' + str(averageViews) + '",'

                        response += '"' + str(maxCommentLength) + '",'
                        response += '"' + str(maxCommentWordCount) + '",'
                        response += '"' + str(maxRating) + '",'
                        response += '"' + str(maxArticlesLength) + '",'
                        response += '"' + str(maxQualityClass) + '",'
                        response += '"' + str(maxImportanceClass) + '",'
                        response += '"' + str(maxWatchers) + '",'
                        response += '"' + str(maxRedirects) + '",'
                        response += '"' + str(maxTotalEdits) + '",'
                        response += '"' + str(maxViews) + '",'

                        response += '"' + str(int(manualRecommendation)) + '",'
                        response += '"' + str(location) + '",'

                        expertwikipagesOrdered = sorted(expertwikipages, key = lambda x: x.related_publications_number, reverse=True)

                        rowcounter = 0
                        for expertwikipage in expertwikipagesOrdered:
                            wikipage = expertwikipage.wikipage

                            if wikipage.edit_protection_level == "None" and rowcounter < 6:
                                rowcounter = rowcounter + 1
                                response += '"' + str(expertwikipage.publication.title) + '",'
                                response += '"' + str(expertwikipage.wikipage.url) + '",'
                                commentLength = 0
                                commentWordCount = 0
                                if expertwikipage.comment is not None:
                                    commentLength = len(expertwikipage.comment)
                                    commentWords = re.findall(r"[\w']+", expertwikipage.comment)
                                    commentWordCount = len(commentWords)
                                response += '"' + str(commentLength) + '",'
                                response += '"' + str(commentWordCount) + '",'
                                response += '"' + str(expertwikipage.rating) + '",'
                                response += '"' + str(expertwikipage.wikipage.page_length) + '",'
                                response += '"' + str(expertwikipage.wikipage.quality_class) + '",'
                                response += '"' + str(expertwikipage.wikipage.importance_class) + '",'
                                response += '"' + str(expertwikipage.wikipage.watchers) + '",'
                                response += '"' + str(expertwikipage.wikipage.redirects) + '",'
                                response += '"' + str(expertwikipage.wikipage.total_edits) + '",'
                                response += '"' + str(expertwikipage.wikipage.views_last_90_days) + '",'
                                response += '"' + str(expertwikipage.approvedbywikipedians) + '",'
                                response += '"' + str(expertwikipage.rejectedbywikipedians) + '",'

                        response += '\n'

                if session_key != "":
                    s['progressPercent'] = str(expertNum / float(len(allExperts)))
                    s.save()
                
            if session_key != "":
                result = HttpResponse(response, content_type='text/csv')
                if version == 0:
                    result['Content-Disposition'] = 'attachment; filename="Pilot1.csv"'
                elif version == 1:
                    result['Content-Disposition'] = 'attachment; filename="Pilot2.csv"'
                elif version == 2:
                    result['Content-Disposition'] = 'attachment; filename="Main_Study.csv"'

                return result
            
            return render_to_response("Dataset_Features.html", {},
                context_instance=RequestContext(request))

def csvdownload(request):

    if request.method == 'GET':
        if 'version' in request.GET and request.GET['version'] != '' and 'key' in request.GET and request.GET['key'] != '':
            version = num(request.GET['version'])
            session_key = request.GET['key']

            if session_key != "":
                s = SessionStore(session_key=session_key)

                result = HttpResponse(s['csvResponse'], content_type='text/csv')
                if version == 0:
                    result['Content-Disposition'] = 'attachment; filename="Pilot1.csv"'
                elif version == 1:
                    result['Content-Disposition'] = 'attachment; filename="Pilot2.csv"'
                elif version == 2:
                    result['Content-Disposition'] = 'attachment; filename="Main_Study.csv"'

                return result

@xframe_options_exempt
@csrf_exempt
def studypage(request):

    if request.method == 'GET':
        if 'userpage' in request.GET and request.GET['userpage'] != '':
            expertwikipage = Expertwikipub.objects.get(pk=request.GET['userpage'])
            expert = expertwikipage.expert
            if not 'preview' in request.GET:
                expertwikipage.link_clicked = True
                expertwikipage.save()
                expert.returned = True
                expert.phase2 = True
                expert.email1_opened = True
                expert.email2_opened = True
                expert.email2OpenedTime = timezone.now()
                expert.save()

            expertName = expert.name
            title = "Dr."
            # if "professor" in expert.title.lower():
            #   title = "Professor"

            expertEmail = expert.email
            wikipage = expertwikipage.wikipage
            comment = expertwikipage.comment
            wikipageUrl = wikipage.url
            similarexpertswikipages = wikipage.expertwikipub_set.all()
            otherexperts = []
            for similarexpertswikipage in similarexpertswikipages:
                otherexpert = similarexpertswikipage.expert
                if otherexpert.email != expertEmail:
                    otherexperts.append({'name': otherexpert.name, 'email':otherexpert.email})

            # expertswikipage_set = expertwikipage.expert.expertwikipub_set.all()
            # otherwikipages = []
            # for otherwikipage in expertswikipage_set:
            #   if otherwikipage.pk != expertwikipage.pk:
            #       otherexperts.append({'userpage': otherwikipage.pk})

            return render_to_response("JoinWikipedians.html",
                {'expertName': expertName, "title": title, 'wikipageUrl': wikipageUrl, 'otherexperts': otherexperts, 'userpage': expertwikipage.pk, 'comment': comment, },
                # {'expertName': expertName, 'wikipageUrl': wikipageUrl, 'otherexperts': otherexperts, 'userpage': expertwikipage.pk, 'otherwikipages': otherwikipages },
                context_instance=RequestContext(request))

    elif request.method == 'POST':
        requestPost = request.POST
        if 'userpage' in requestPost and requestPost['userpage'] != '':
            userpage = requestPost['userpage']

            expertwikipage = Expertwikipub.objects.get(pk=userpage)

            if 'feedback' in requestPost:
                comment = requestPost['feedback']
                expertwikipage.comment = comment
                expertwikipage.commentTime = timezone.now()
                expertwikipage.save()

            authorCounter = 0
            while 'authorlist[' + str(authorCounter) + '][Name]' in requestPost and requestPost['authorlist[' + str(authorCounter) + '][Name]'] is not None and requestPost['authorlist[' + str(authorCounter) + '][Name]'] != '':
                authorLastName = requestPost['authorlist[' + str(authorCounter) + '][Name]']
                authorFirstName = requestPost['authorlist[' + str(authorCounter) + '][FirstName]']
                school = requestPost['authorlist[' + str(authorCounter) + '][School]']
                specialization = requestPost['authorlist[' + str(authorCounter) + '][Specialization]']
                expert = Expertwikipubreferee(expertwikipub=expertwikipage, name=authorLastName, firstname=authorFirstName, school=school, specialization=specialization)
                expert.save()

                authorCounter = authorCounter + 1

            if 'rating' in requestPost:
                rating = requestPost['rating']

                expertwikipage.rating = rating
                expertwikipage.save()
                
            return HttpResponse(json.dumps({}), content_type="application/json")

@xframe_options_exempt
def wikipediaproxy(request):

    if request.method == 'GET':
        if 'wikipediaurl' in request.GET and request.GET['wikipediaurl'] != '' and 'userpage' in request.GET and request.GET['userpage'] != '':
            wikipageUrl = request.GET['wikipediaurl']
            userpage = request.GET['userpage']
            if wikipageUrl is not None and userpage is not None:
                expertwikipage = Expertwikipub.objects.get(pk=userpage)
                expert = expertwikipage.expert
                expert.user_agent = request.META['HTTP_USER_AGENT']
                expert.ip_address = request.META['REMOTE_ADDR']
                expert.save()
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
                }
                wikipediaResponse = requests.get(wikipageUrl, headers = headers)
                wikipediaContent = wikipediaResponse.text

                soup = BeautifulSoup(wikipediaContent)

                # # Find the printable version link.
                # printableVersionLink = soup.find('li', id="t-print")

                # if printableVersionLink is not None:

                #   printableVersionLink = printableVersionLink.find('a')

                #   if printableVersionLink is not None:

                #       printableVersionLink = printableVersionLink['href']

                #       wikipediaResponse = requests.get('https://en.wikipedia.org' + printableVersionLink, headers = headers)
                #       wikipediaContent = wikipediaResponse.text

                #       soup = BeautifulSoup(wikipediaContent)

                # Find the head tag.
                headtag = soup.title.parent

                # Insert a base tag in the header of the Wikipedia page to use appropriate links in the iframe.
                baseTag = soup.new_tag("base")

                # Add the base hyperlink.
                baseTag['href'] = 'http://en.wikipedia.org/'

                # Direct all hyperlinks and forms inside the iframe to itself.
                baseTag['target'] = '_self'

                # Insert the base tag as the first element in the head tag.
                headtag.insert(0, baseTag)

                # Find all hyperlinks inside the iframe.
                asArray = soup.find_all('a')

                href_tags = soup.find_all(href=True)
                for href_tag in href_tags:
                    href_tag['href'] = urljoin("http://en.wikipedia.org/", href_tag['href'])

                src_tags = soup.find_all(src=True)
                for src_tag in src_tags:
                    src_tag['src'] = urljoin("http://en.wikipedia.org/", src_tag['src'])

                # Disable pointers of all hyperlinks in the iframe.
                for aElement in asArray:
                    aElement['style'] = 'pointer-events: none; cursor: default;';

                    aElement['disabled'] = "disabled"

                    if 'href' in aElement and aElement['href'] is not None:
                        aElement['href'] = "#"

                soupUnicode = unicode(soup)

            else:
                soupUnicode = "Unfortunately the page is not available! Please reload the page."        
            
            return render_to_response("WikipediaProxy.html",
                { 'wikipageContent': soupUnicode, },
                context_instance=RequestContext(request))

def fillEmailSignature(expertDomain, message, html_content):
    if "econ" in expertDomain.lower():
        message = message + "Yan Chen, Daniel Kahneman Collegiate Professor of Information, University of Michigan\n"
        html_content = html_content + "\n<p>Yan Chen, Daniel Kahneman Collegiate Professor of Information, \nUniversity of Michigan</p>\n"
        # message = message + "Rosta Farzan, Assistant Professor of Information, University of Pittsburgh\n"
        # html_content = html_content + "<p>Rosta Farzan, Assistant Professor of Information, University of Pittsburgh</p>\n"
        message = message + "Robert Kraut, Herbert A. Simon Professor of Human-Computer Interaction, Carnegie Mellon University\n\n\n\n\n\n"
        html_content = html_content + "<p>Robert Kraut, Herbert A. Simon Professor of Human-Computer Interaction, \nCarnegie Mellon University</p><br><br><br>\n"
    elif "info" in expertDomain.lower():
        # message = message + "Rosta Farzan, Assistant Professor of Information, University of Pittsburgh\n"
        # html_content = html_content + "<p>Rosta Farzan, Assistant Professor of Information, University of Pittsburgh</p>\n"
        message = message + "Robert Kraut, Herbert A. Simon Professor of Human-Computer Interaction, Carnegie Mellon University\n"
        html_content = html_content + "<p>Robert Kraut, Herbert A. Simon Professor of Human-Computer Interaction, \nCarnegie Mellon University</p>\n"
        message = message + "Yan Chen, Daniel Kahneman Collegiate Professor of Information, University of Michigan\n\n\n\n\n\n"
        html_content = html_content + "<p>Yan Chen, Daniel Kahneman Collegiate Professor of Information, \nUniversity of Michigan</p><br><br><br>\n"
    else:
        message = message + "Robert Kraut, Herbert A. Simon Professor of Human-Computer Interaction, Carnegie Mellon University\n"
        html_content = html_content + "<p>Robert Kraut, Herbert A. Simon Professor of Human-Computer Interaction, \nCarnegie Mellon University</p>\n"
        message = message + "Yan Chen, Daniel Kahneman Collegiate Professor of Information, University of Michigan\n"
        html_content = html_content + "<p>Yan Chen, Daniel Kahneman Collegiate Professor of Information, \nUniversity of Michigan</p>\n"
        # message = message + "Rosta Farzan, Assistant Professor of Information, University of Pittsburgh\n\n\n\n\n\n"
        # html_content = html_content + "<p>Rosta Farzan, Assistant Professor of Information, University of Pittsburgh</p><br><br><br>\n"
    return message, html_content

def fillEmailFactors(expertPK, expertSpecialization, expertDomain, inSpecialtyArea, highviewspast90days,
    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, 
    relevant_to_research, within_area, on_expertise_topic, especially_popular, highly_visible, 
    highly_popular, private_first):
    personalIncentive = ''
    includingPersonalIncentive = ''
    personalIncentiveHTML = ''
    includingPersonalIncentiveHTML = ''
    # if inSpecialtyArea == 'true':
    #     personalIncentive = " related to " + expertSpecialization.lower()
    #     personalIncentiveHTML = "\n related to " + expertSpecialization.lower()
    #     includingPersonalIncentive = ", including " + expertSpecialization.lower()
    #     includingPersonalIncentiveHTML = ",\n including " + expertSpecialization.lower()

    publicIncentive = " We will select only"
    publicIncentiveHTML = " We will select only"

    if especially_popular == 'true':
        publicIncentive += " especially popular "
        publicIncentiveHTML += " especially popular "
    elif highly_visible == 'true':
        publicIncentive += " highly visible "
        publicIncentiveHTML += " highly visible "
    elif highly_popular == 'true':
        publicIncentive += " highly popular "
        publicIncentiveHTML += " highly popular "

    publicIncentive += "articles, with over 1,000 views in the past month, so that your feedback will benefit many Wikipedia readers."
    publicIncentiveHTML += " articles, with over 1,000 views in\n the past month, so that your feedback will benefit many Wikipedia readers."

    if citedpublication == 'true':
        if relevance_factor == 'true':
            if within_area == 'true':
                personalIncentive += " that may include some of your publications in their references."
                personalIncentiveHTML += "\n that may include some of your publications in their references."
            elif on_expertise_topic == 'true':
                personalIncentive += " that might refer to some of your research."
                personalIncentiveHTML += "\n that might refer to some of your research."
            else:
                personalIncentive += " that are likely to cite your research."
                personalIncentiveHTML += "\n that are likely to cite your research."

            personalIncentive += " We will also acknowledge your contribution at the WikiProject Economics Page \n( http://wkpd.research.si.umich.edu/r?userid=" + expertPK + "&p=ew )\n, a forum for discussion of economics articles on Wikipedia."
            personalIncentiveHTML += "\n We will also acknowledge your contribution at the <a href=\n'http://wkpd.research.si.umich.edu/r?userid=" + expertPK + "&p=ew'\n>WikiProject Economics Page</a>,\n a forum for discussion of economics articles on Wikipedia."
        else:
            if may_include_reference == 'true':
                personalIncentive += " that may include some of your publications in their references."
                personalIncentiveHTML += "\n that may include some of your publications in their references."
            elif might_refer_to == 'true':
                personalIncentive += " that might refer to some of your research."
                personalIncentiveHTML += "\n that might refer to some of your research."
            else:
                personalIncentive += " that are likely to cite your research."
                personalIncentiveHTML += "\n that are likely to cite your research."
        if highviewspast90days == 'true':

            if private_first == 'true':
                personalIncentive += "\n\n" + publicIncentive
                personalIncentiveHTML += "</p>\n<p>" + publicIncentiveHTML
            else:
                personalIncentive = ". " + publicIncentive + "\n\n These articles " + personalIncentive[5:]
                personalIncentiveHTML = ".\n " + publicIncentiveHTML + "</p>\n<p> These articles " + personalIncentiveHTML[7:]
    elif highviewspast90days == 'true':
        personalIncentive += ". " + publicIncentive
        personalIncentiveHTML += ".\n " + publicIncentiveHTML
    return personalIncentive, includingPersonalIncentive, personalIncentiveHTML, includingPersonalIncentiveHTML

def phase1EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, 
    especially_popular, highly_visible, highly_popular, private_first, preview=False):

    personalIncentive, includingPersonalIncentive, personalIncentiveHTML, includingPersonalIncentiveHTML = fillEmailFactors(
        expertPK, expertSpecialization, expertDomain, inSpecialtyArea, highviewspast90days,
        citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, 
        relevant_to_research, within_area, on_expertise_topic, especially_popular, highly_visible, 
        highly_popular, private_first)

    title = "Dr."
    # if "professor" in expertTitle.lower():
    #   title = "Professor"
    message = "Dear " + title + " " + expertName + ",\n\n" + "Would you be willing to spend 10 - 20 minutes providing feedback on a few Wikipedia articles related to " + expertSpecialization.lower()
    message = message + "?\nWikipedia is among the most important information sources the general public uses to find out about a wide range of topics."
    message = message + " A Wikipedia article is viewed on average 426 times each month."
    message = message + " While many Wikipedia articles are useful, articles written by enthusiasts instead of experts can be inaccurate, incomplete, or out of date.\n"
    html_content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN"\n "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html>\n'
    html_content = html_content + '<body>\n'
    html_content = html_content + "<p>Dear " + title + " " + expertName + ",</p>\n"
    html_content = html_content + "<p><br>Would you be willing to spend 10 - 20 minutes providing feedback on\n a few Wikipedia articles related to " + expertSpecialization.lower()
    html_content = html_content + "?\n Wikipedia is among the most important information sources the general \npublic uses to find out about a wide range of topics.\n"
    html_content = html_content + " A Wikipedia article is viewed on average 426 times each month.\n"
    html_content = html_content + "While many Wikipedia articles are useful, articles written by enthusiasts\n instead of experts can be inaccurate, incomplete, or out of date.</p>"

    # message = message + "While many Wikipedia articles are useful, articles written by enthusiasts instead of experts can be inaccurate, incomplete, or out of date.\n\n"
    # html_content = html_content + "While many Wikipedia articles are useful, articles written by enthusiasts\n instead of experts can be inaccurate, incomplete, or out of date.</p>\n"
    message = message + "If you are willing to help, we will send you links to a few Wikipedia articles in your area of expertise" + personalIncentive + "\n\n"
    html_content = html_content + "<p>If you are willing to help, we will send you links to a few Wikipedia articles in your area of expertise" + personalIncentiveHTML + "</p>\n"
    message = message + "Please open one of the following webpages in a browser to continue:\n\n"
    html_content = html_content + "<p>Please click one of the following links to continue:</p>\n"
    message = message + "1- To send you some Wikipedia articles in your area of expertise for comment:\n"
    message = message + "http://wkpd.research.si.umich.edu/i?i=" + str(expertPK) + "\n\n"
    html_content = html_content + "<p><a href=\n'http://wkpd.research.si.umich.edu/i?i=" + str(expertPK) + "'\n>Yes, please send me some Wikipedia articles to comment on.</a></p>\n"
    message = message + "2- If you are not interested in this study:\n"
    message = message + "http://wkpd.research.si.umich.edu/o?i=" + str(expertPK) + "\n\n"
    html_content = html_content + "<p><a href=\n'http://wkpd.research.si.umich.edu/o?i=" + str(expertPK) + "'\n>No, I am not interested.</a></p>\n"

    # message = message + "If you would rather comment on articles in another area, please reply to this email and let us know.\n\n"
    # html_content = html_content + "<p>If you would rather comment on articles in another area, please reply to\n this email and let us know.</p>\n"

    message = message + "Thank you for your attention.\n\n"
    html_content = html_content + "<p>Thank you for your attention.</p>\n"

    message = message + "Sincerely,\n\n"
    html_content = html_content + "<p><br>Sincerely,</p>\n"

    message, html_content = fillEmailSignature(expertDomain, message, html_content)

    if not preview:
        randomNumber = random.randint(1, 9999999)
        html_content = html_content + "<img src=\n'http://wikipediastudy-env.us-east-1.elasticbeanstalk.com/images" + str(expertPK) + "B" + str(randomNumber) + ".gif'\n width='1px' height='1px'></body></html>\n"
    else:
        html_content = html_content + "</body></html>\n"

    return message, html_content

def phase2EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, preview=False):

    title = "Dr."
    # if "professor" in expertTitle.lower():
    #   title = "Professor"
    message = "Dear " + title + " " + expertName + ",\n\n" + "Thank you for your willingness to provide feedback on the quality of Wikipedia articles.\n The following articles are suggested by our algorithm as related to " + expertSpecialization.lower() + ".\n"
    message = message + "\n\n Please comment on the articles most relevant to your research.\n Your feedback can significantly improve these articles' accuracy and completeness,\n and the comments and the references that you provide will be incorporated therein.\n"
    if citedpublication == 'true':
        if relevance_factor == 'true':
            if within_area == 'true':
                message += "\nThese articles may include some of your publications in their references."
            elif on_expertise_topic == 'true':
                message += "\nThese articles might refer to some of your research."
            else:
                message += "\nThese articles are likely to cite your research."
            message += " We will also acknowledge your contribution at the WikiProject Economics Page \n( http://wkpd.research.si.umich.edu/r?userid=" + expertPK + "&p=ew )\n, a forum for discussion of economics articles on Wikipedia."
        else:
            if may_include_reference == 'true':
                message += "\nThese articles may include some of your publications in their references."
            elif might_refer_to == 'true':
                message += "\nThese articles might refer to some of your research."
            else:
                message += "\nThese articles are likely to cite your research."
    html_content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN"\n "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html>\n'
    html_content = html_content + '<head>\n<style>table { width:100%; } \ntable, th, td { border: 1px solid d4d4d4; border-collapse: collapse; } \nth, td { padding: 5px; text-align: left; } \ntable#t01 tr:nth-child(even) { background-color: #eee; } \ntable#t01 tr:nth-child(odd) { background-color:#fff; } \ntable#t01 th { background-color: #777777; color: #FFFFFF; }\n'
    html_content = html_content + '</style></head>\n<body>\n'
    html_content = html_content + "<p>Dear " + title + " " + expertName + ",</p>\n"
    html_content = html_content + "<p><br>Thank you for your willingness to provide\n feedback on the quality of Wikipedia articles.\n"
    html_content = html_content + " The following articles are suggested by our algorithm as related to \n" + expertSpecialization.lower() + "."
    html_content = html_content + "</p>\n<p>Please comment on the articles most relevant to your research. Your feedback\n can significantly improve these articles' accuracy and completeness, and the\n comments and the references that you provide will be incorporated therein.\n"
    if citedpublication == 'true':
        if relevance_factor == 'true':
            if within_area == 'true':
                html_content += "\nThese articles may include some of your publications in their references."
            elif on_expertise_topic == 'true':
                html_content += "\nThese articles might refer to some of your research."
            else:
                html_content += "\nThese articles are likely to cite your research."
            html_content += "\n We will also acknowledge your contribution at the <a href=\n'http://wkpd.research.si.umich.edu/r?userid=" + expertPK + "&p=ew'\n>WikiProject Economics Page</a>,\n a forum for discussion of economics articles on Wikipedia."
        else:
            if may_include_reference == 'true':
                html_content += "\nThese articles may include some of your publications in their references."
            elif might_refer_to == 'true':
                html_content += "\nThese articles might refer to some of your research."
            else:
                html_content += "\nThese articles are likely to cite your research."

    nextMonthDate = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%b %d, %Y')

    message = message + "We would appreciate receiving your comments by " + nextMonthDate + ". Thank you very much for your help.\n\n"
    html_content = html_content + "\nWe would appreciate receiving your comments by " + nextMonthDate + ".\n Thank you very much for your help.</p>\n"

    message = message + "\nWikipedia Article Title\t\t"
    html_content = html_content + "\n<table cellspacing='10' cellpadding='10' style='width:100%; border:\n 1px solid #d4d4d4; border-collapse: collapse; '>\n<tr style=' padding: 5px; text-align: left; background-color: #777777;\n color: #FFFFFF; border: 1px solid #d4d4d4; '>\n<th>Wikipedia Article Title</th>\n"

    if highviewspast90days == 'true':
        message = message + "Number of views in the past month\t\t"
        html_content = html_content + "<th>Number of views in the past month</th>\n"

    message = message + "Link to review the article\n\n"
    html_content = html_content + "<th>Link to review the article</th></tr>\n"

    expertwikipagesOrdered = sorted(expertwikipages, key = lambda x: x.related_publications_number, reverse=True)
    wikipageslist = []

    rowcounter = 0
    for expertwikipage in expertwikipagesOrdered:
        wikipage = expertwikipage.wikipage

        if (not wikipage in wikipageslist) and wikipage.edit_protection_level == "None":
            rowcounter = rowcounter + 1
            if rowcounter <= 6:
                html_content = html_content + "<tr style=' padding: 5px; text-align: left; border: 1px solid #d4d4d4; \n"
                if rowcounter % 2 == 0:
                    html_content = html_content + "background-color: #EEEEEE; '>\n"
                else:
                    html_content = html_content + "background-color: #FFFFFF; '>\n"

                wikipageslist.append(wikipage)

                message = message + wikipage.title + "\t\t"
                html_content = html_content + "<td>" + wikipage.title + "</td>\n"

                # Find current date.
                todayDate = (datetime.date.today()).strftime('%Y%m%d')

                # Find date of a month ago.
                pastMonthDate = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y%m%d')

                # Find the encoded title of the article.
                articleEncodedTitle = re.search("wiki/([^?]+)", wikipage.url)

                if articleEncodedTitle is not None:
                    articleEncodedTitle = articleEncodedTitle.group(1)
                else:
                    articleEncodedTitle = wikipage.title

                # Retrieve content of the traffic statistics page in BeautifulSoup structure.
                trafficStatisticsURL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/" + articleEncodedTitle + "/daily/" + pastMonthDate + "/" + todayDate

                while True:
                    try:
                        numberofViewsResponse = requests.get(trafficStatisticsURL)
                        numberofViewsResponse = numberofViewsResponse.json()
                        numberofViewsPerDays = numberofViewsResponse['items']
                        break
                    except:
                        print ("\n\n\nI cannot retrieve the number of views of this article!")
                        time.sleep(1)

                # Print out the number of views in the last month.
                viewsNum = 0
                for numberofViewsPerDay in numberofViewsPerDays:
                    viewsNum += numberofViewsPerDay['views']

                wikipage.views_last_90_days = viewsNum
                wikipage.save()

                if highviewspast90days == 'true':
                    message = message + str("{:,}".format(wikipage.views_last_90_days)) + "\t\t"
                    html_content = html_content + "<td>" + str("{:,}".format(wikipage.views_last_90_days)) + "</td>\n"

                message = message + "http://wkpd.research.si.umich.edu/j?u=" + str(expertwikipage.pk) + "\n\n"
                html_content = html_content + "<td><a href=\n'http://wkpd.research.si.umich.edu/j?u=" + str(expertwikipage.pk) + "'\n>Click here</a></td>\n"
            else:
                break
    html_content = html_content + "</table>\n"

    # message = message + "In case you want to see more recommendations, you can take a look at the table below.\n\n"
    # html_content = html_content + "<p>In case you want to see more recommendations, you can take a look at the table below.</p>"

    # message = message + "If you would rather comment on other articles, please reply to this email and let us know.\n\n"
    # html_content = html_content + "<p>If you would rather comment on other articles, please reply to this email\n and let us know.</p>\n"

    message = message + "Sincerely,\n\n"
    html_content = html_content + "<p><br>Sincerely,</p>\n"

    message, html_content = fillEmailSignature(expertDomain, message, html_content)

    # if rowcounter == 6:
    #   message = message + "\n\nWikipedia Article Title\t"
    #   html_content = html_content + "<br><br><table cellspacing='10' cellpadding='10' style='width:100%; border: 1px solid #d4d4d4; border-collapse: collapse; '><tr style=' padding: 5px; text-align: left; background-color: #777777; color: #FFFFFF; border: 1px solid #d4d4d4; '><th>Wikipedia Article Title</th>"
    #   if highviewspast90days == 'true':
    #       message = message + "Number of views in past 90 days\t"
    #       html_content = html_content + "<th>Number of views in past 90 days</th>"
    #   message = message + "Link to review the article\n\n"
    #   html_content = html_content + "<th>Link to review the article</th></tr>"

    #   rowcounter = 0
    #   for expertwikipage in expertwikipagesOrdered:
    #       wikipage = expertwikipage.wikipage

    #       if (not wikipage in wikipageslist) and wikipage.edit_protection_level == "None":
    #           rowcounter = rowcounter + 1
    #           html_content = html_content + "<tr style=' padding: 5px; text-align: left; border: 1px solid #d4d4d4; "
    #           if rowcounter % 2 == 0:
    #               html_content = html_content + "background-color: #EEEEEE; '>"
    #           else:
    #               html_content = html_content + "background-color: #FFFFFF; '>"

    #           wikipageslist.append(wikipage)

    #           message = message + wikipage.title + "\t"
    #           html_content = html_content + "<td>" + wikipage.title + "</td>"

    #           if highviewspast90days == 'true':
    #               message = message + str(wikipage.views_last_90_days) + "\t"
    #               html_content = html_content + "<td>" + str("{:,}".format(wikipage.views_last_90_days)) + "</td>"

    #           message = message + "http://wkpd.research.si.umich.edu/j?u=" + str(expertwikipage.pk) + "\n\n"
    #           html_content = html_content + "<td><a href='http://wkpd.research.si.umich.edu/j?u=" + str(expertwikipage.pk) + "'>Click here</a></td>"
    #   html_content = html_content + "</table>"

    message = message + "\nIf you would like to stop receiving emails from us, please click the following link:\n\n"
    message = message + "http://wkpd.research.si.umich.edu/o?i=" + expertPK
    html_content = html_content + "\n<p>If you would like to stop receiving emails from us, please <a href=\n'http://wkpd.research.si.umich.edu/o?i=" + expertPK + "'\n>click here</a>.</p>\n"

    if not preview:
        randomNumber = random.randint(1, 9999999)
        html_content = html_content + "<img src=\n'http://wikipediastudy-env.us-east-1.elasticbeanstalk.com/images" + str(expertPK) + "2nB" + str(randomNumber) + ".gif'\n width='1px' height='1px'>\n</body></html>\n"
    else:
        html_content = html_content + "</body></html>\n"

    return message, html_content


def findArticleTalkPageAndPost(expertName, wikipageTitle, articleHyperlink):

    # Find the encoded title of the article.
    articleEncodedTitle = re.search("wiki/([^?]+)", articleHyperlink)

    if articleEncodedTitle is not None:
        articleEncodedTitle = articleEncodedTitle.group(1)
    else:
        articleEncodedTitle = re.search("/[?]title=([^?]+)", articleHyperlink)

        if articleEncodedTitle is not None:
            articleEncodedTitle = articleEncodedTitle.group(1)
        else:
            articleEncodedTitle = wikipageTitle

    articleEncodedTitle = articleEncodedTitle.replace(" ", "_")
    talkPageHyperlink = 'http://en.wikipedia.org/wiki/Talk:' + articleEncodedTitle

    expertName = expertName.replace(" ", "_")
    # urllib.quote_plus(expertName)

    postHyperlink = talkPageHyperlink + "#Dr._" + expertName + ".27s_comment_on_this_article"

    return talkPageHyperlink, postHyperlink


def redirectPage(request):

    if request.method == 'GET':
        if 'userid' in request.GET and 'p' in request.GET and request.GET['userid'] != '' and request.GET['p'] != '':
            userid = request.GET['userid']
            pageType = request.GET['p']

            expert = Expert.objects.get(pk=userid)

            if pageType == "m":

                pageID = request.GET['id']
                wikipage = Wikipage.objects.get(article_id=pageID)
    
                expert.article_clicked = True
                url = wikipage.url

            elif pageType == "t":

                pageID = request.GET['id']
                wikipage = Wikipage.objects.get(article_id=pageID)
                wikipageTitle = wikipage.title
    
                talkPageHyperlink, postHyperlink = findArticleTalkPageAndPost(expert.name, wikipageTitle, wikipage.url)

                expert.talkpage_clicked = True
                url = talkPageHyperlink

            elif pageType == "p":

                pageID = request.GET['id']
                wikipage = Wikipage.objects.get(article_id=pageID)
                wikipageTitle = wikipage.title
    
                talkPageHyperlink, postHyperlink = findArticleTalkPageAndPost(expert.name, wikipageTitle, wikipage.url)

                expert.post_clicked = True
                url = postHyperlink

            elif pageType == "g":

                expert.tutorial_clicked = True
                url = "https://en.wikipedia.org/wiki/Help:Getting_started"

            elif pageType == "ew":

                expert.econ_wikiproject_clicked = True
                url = "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Economics#Edit_Requests"

            expert.save()

            return HttpResponseRedirect(url)

def phase3EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, preview=False):
    title = "Dr."
    # if "professor" in expertTitle.lower():
    #   title = "Professor"

    message = "Dear " + title + " " + expertName + ",\n\n" + "Thank you for providing feedback on Wikipedia articles.\n We have posted your comments to the following article talk page(s),\n which is where Wikipedia editors discuss changes to articles.\n You can see the original article or your comments,\n by clicking on the appropriate links below.\n\n"
    html_content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN"\n "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html>\n'
    html_content = html_content + '<head>\n<style>table { width:100%; } \ntable, th, td { border: 1px solid d4d4d4; border-collapse: collapse; } \nth, td { padding: 5px; text-align: left; } \ntable#t01 tr:nth-child(even) { background-color: #eee; } \ntable#t01 tr:nth-child(odd) { background-color:#fff; } \ntable#t01 th { background-color: #777777; color: #FFFFFF; }\n'
    html_content = html_content + '</style></head>\n<body>\n'
    html_content = html_content + "<p>Dear " + title + " " + expertName + ",</p>\n"
    html_content = html_content + "<p><br>Thank you for providing feedback on Wikipedia articles.\n We have posted your comments to the following article talk page(s),\n which is where Wikipedia editors discuss changes to articles.\n You can see the original article or your comments,\n by clicking on the appropriate links below.</p>\n"

    message = message + "Wikipedia Article\t\t"
    html_content = html_content + "<table cellspacing='10' cellpadding='10' style='width:100%;\n border: 1px solid #d4d4d4; border-collapse: collapse; '>\n<tr style=' padding: 5px; text-align: left; background-color: #777777;\n color: #FFFFFF; border: 1px solid #d4d4d4; '>\n<th>Wikipedia Article</th>\n"
    # message = message + "Article Talk Page\t\t"
    # html_content = html_content + "<th>Article Talk Page</th>\n"
    message = message + "Your Comment\n\n"
    html_content = html_content + "<th>Your Comment</th></tr>\n"

    expertwikipagesOrdered = sorted(expertwikipages, key = lambda x: x.related_publications_number, reverse=True)
    wikipageslist = []

    rowcounter = 0
    for expertwikipage in expertwikipagesOrdered:
        wikipage = expertwikipage.wikipage

        if (not wikipage in wikipageslist) and expertwikipage.submittedtotalkpage == True:
            rowcounter = rowcounter + 1
            if rowcounter <= 6:
                html_content = html_content + "<tr style=' padding: 5px; text-align: left; border: 1px solid #d4d4d4; \n"
                if rowcounter % 2 == 0:
                    html_content = html_content + "background-color: #EEEEEE; '>\n"
                else:
                    html_content = html_content + "background-color: #FFFFFF; '>\n"

                wikipageslist.append(wikipage)

                wikipageTitle = wikipage.title
                talkPageHyperlink, postHyperlink = findArticleTalkPageAndPost(expertName, wikipageTitle, wikipage.url)

                message = message + "http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=m&id=" + str(wikipage.article_id) + "\t\t"
                html_content = html_content + "<td><a href=\n'http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=m&id=" + str(wikipage.article_id) + "'\n>" + wikipage.title + "\n</a></td>\n"

                # message = message + "http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=t&id=" + str(wikipage.article_id) + "\t\t"
                # html_content = html_content + "<td><a href=\n'http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=t&id=" + str(wikipage.article_id) + "'\n>Talk:" + wikipage.title + "\n</a></td>\n"

                message = message + "http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=p&id=" + str(wikipage.article_id) + "\n\n"
                html_content = html_content + "<td><a href=\n'http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=p&id=" + str(wikipage.article_id) + "'\n>Your comment on the Talk Page</a></td>\n"

            else:
                break
    html_content = html_content + "</table>"

    message = message + "If you would like to edit these or other articles yourself, here is a tutorial on how to edit Wikipedia articles:\n\n"
    html_content = html_content + "<p>If you would like to edit these or other articles yourself, \n"

    message = message + "http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=g\n\n"
    html_content = html_content + "<a href=\n'http://wkpd.research.si.umich.edu/r?i=" + str(expertPK) + "&p=g'\n>here is a tutorial</a>\n"

    html_content = html_content + " on how to edit Wikipedia articles:</p>\n"

    message = message + "Thank you again for your contribution to Wikipedia!\n\n"
    html_content = html_content + "<p>Thank you again for your contribution to Wikipedia!</p>\n"

    message = message + "Sincerely,\n\n"
    html_content = html_content + "<p><br>Sincerely,</p>\n"

    message, html_content = fillEmailSignature(expertDomain, message, html_content)

    if not preview:
        randomNumber = random.randint(1, 9999999)
        html_content = html_content + "<img src=\n'http://wikipediastudy-env.us-east-1.elasticbeanstalk.com/images" + str(expertPK) + "3nB" + str(randomNumber) + ".gif'\n width='1px' height='1px'>\n</body></html>\n"
    else:
        html_content = html_content + "</body></html>\n"

    return message, html_content

@xframe_options_exempt
def images(request):

    if request.method == 'GET':
        userid = re.search("images(\d*)B\d*[.]gif", request.path)
        if userid is not None:
            expert = Expert.objects.get(pk=userid.group(1))
            expert.email1_opened = True
            expert.email1OpenedTime = timezone.now()
            expert.user_agent = request.META['HTTP_USER_AGENT']
            expert.ip_address = request.META['REMOTE_ADDR']
            expert.save()
        else:
            userid = re.search("images(\d*)2nB\d*[.]gif", request.path)
            if userid is not None:
                expert = Expert.objects.get(pk=userid.group(1))
                expert.email2_opened = True
                expert.email2OpenedTime = timezone.now()
                expert.user_agent = request.META['HTTP_USER_AGENT']
                expert.ip_address = request.META['REMOTE_ADDR']
                expert.save()
            else:
                userid = re.search("images(\d*)3nB\d*[.]gif", request.path)
                if userid is not None:
                    expert = Expert.objects.get(pk=userid.group(1))
                    expert.email3_opened = True
                    expert.email3OpenedTime = timezone.now()
                    expert.user_agent = request.META['HTTP_USER_AGENT']
                    expert.ip_address = request.META['REMOTE_ADDR']
                    expert.save()
            
        imagePath = "ExpertIdeas/Blank.gif"
        with open(imagePath, "rb") as f:
            return HttpResponse(f.read(), mimetype="image/gif")

def sendemail_method(userid, phase, inSpecialtyArea, highviewspast90days, citedpublication,
    relevance_factor, likely_to_cite, may_include_reference, might_refer_to,
    relevant_to_research, within_area, on_expertise_topic, especially_popular, highly_visible, 
    highly_popular, private_first):

    expert = Expert.objects.get(pk=userid)

    expert.emailSent = timezone.now()
    if phase == 'Phase_1_EmailList':
        expert.email1Sent = timezone.now()
        expert.email1Count = expert.email1Count + 1
    elif phase == 'Phase_2_EmailList':
        expert.email2Sent = timezone.now()
        expert.email2Count = expert.email2Count + 1
    elif phase == 'Phase_3_EmailList':
        expert.email3Sent = timezone.now()
        expert.email3Count = expert.email3Count + 1
    expert.emailCount = expert.emailCount + 1
    if inSpecialtyArea == "true":
        expert.inspecialtyarea = True
    if highviewspast90days == "true":
        expert.highviewspast90days = True
    if citedpublication == "true":
        expert.citedpublication = True
    if relevance_factor == "true":
        expert.relevance_factor = True
    if likely_to_cite == "true":
        expert.likely_to_cite = True
    if may_include_reference == "true":
        expert.may_include_reference = True
    if might_refer_to == "true":
        expert.might_refer_to = True
    if relevant_to_research == "true":
        expert.relevant_to_research = True
    if within_area == "true":
        expert.within_area = True
    if on_expertise_topic == "true":
        expert.on_expertise_topic = True
    if especially_popular == "true":
        expert.especially_popular = True
    if highly_visible == "true":
        expert.highly_visible = True
    if highly_popular == "true":
        expert.highly_popular = True
    if private_first == "true":
        expert.private_first = True
    expert.save()
    expertName = expert.name
    expertTitle = expert.title
    expertEmail = expert.email
    expertPK = str(expert.pk)
    expertDomain = expert.domain
    expertSpecialization = expert.specialization
    
    expertwikipages = expert.expertwikipub_set.all()

    if phase == 'Phase_1_EmailList':
        message, html_content = phase1EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
            citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, especially_popular, 
            highly_visible, highly_popular, private_first, False)
    elif phase == 'Phase_2_EmailList':
        message, html_content = phase2EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
            citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, False)
    elif phase == 'Phase_3_EmailList':
        message, html_content = phase3EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
            citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, False)

    if expertSpecialization is None or expertSpecialization == "":
        expertSpecialization = expertDomain
    subject = expertSpecialization + " Articles in Wikipedia"
    from_email = settings.EMAIL_HOST_USER
    to_list = [expertEmail]

    msg = EmailMultiAlternatives(subject, message, from_email, to_list, headers={'Reply-To': "YourEmailAddressHere", 'format': 'flowed'})
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
    # send_mail(subject, message, from_email, to_list, fail_silently=False)

@login_required
def sendemail(request):

    if request.method == 'POST':
        if 'phase' in request.POST and 'inSpecialtyArea' in request.POST and 'citedpublication' in request.POST and 'highviewspast90days' in request.POST and 'userid' in request.POST and request.POST['userid'] != '' and request.POST['phase'] != '':
            userid = request.POST['userid']
            phase = request.POST['phase']
            inSpecialtyArea = request.POST['inSpecialtyArea']
            highviewspast90days = request.POST['highviewspast90days']
            citedpublication = request.POST['citedpublication']
            relevance_factor = request.POST['relevance_factor']
            likely_to_cite = request.POST['likely_to_cite']
            may_include_reference = request.POST['may_include_reference']
            might_refer_to = request.POST['might_refer_to']
            relevant_to_research = request.POST['relevant_to_research']
            within_area = request.POST['within_area']
            on_expertise_topic = request.POST['on_expertise_topic']
            if 'especially_popular' in request.POST:
                especially_popular = request.POST['especially_popular']
            else:
                especially_popular = 'false'
            if 'highly_visible' in request.POST:
                highly_visible = request.POST['highly_visible']
            else:
                highly_visible = 'false'
            if 'highly_popular' in request.POST:
                highly_popular = request.POST['highly_popular']
            else:
                highly_popular = 'false'
            if 'private_first' in request.POST:
                private_first = request.POST['private_first']
            else:
                private_first = 'false'
            
            sendemail_method(userid, phase, inSpecialtyArea, highviewspast90days, citedpublication,
                relevance_factor, likely_to_cite, may_include_reference, might_refer_to,
                relevant_to_research, within_area, on_expertise_topic, especially_popular, 
                highly_visible, highly_popular, private_first)

            return HttpResponse(json.dumps({}), content_type="application/json")

def emailpreview(request):

    if request.method == 'GET':
        if 'phase' in request.GET and 'userid' in request.GET and 'inSpecialtyArea' in request.GET and request.GET['userid'] != '':
            userid = request.GET['userid']
            phase = request.GET['phase']
            inSpecialtyArea = request.GET['inSpecialtyArea']
            highviewspast90days = request.GET['highviewspast90days']
            citedpublication = request.GET['citedpublication']
            relevance_factor = request.GET['relevance_factor']
            likely_to_cite = request.GET['likely_to_cite']
            may_include_reference = request.GET['may_include_reference']
            might_refer_to = request.GET['might_refer_to']
            relevant_to_research = request.GET['relevant_to_research']
            within_area = request.GET['within_area']
            on_expertise_topic = request.GET['on_expertise_topic']
            if 'especially_popular' in request.POST:
                especially_popular = request.POST['especially_popular']
            else:
                especially_popular = 'false'
            if 'highly_visible' in request.POST:
                highly_visible = request.POST['highly_visible']
            else:
                highly_visible = 'false'
            if 'highly_popular' in request.POST:
                highly_popular = request.POST['highly_popular']
            else:
                highly_popular = 'false'
            if 'private_first' in request.POST:
                private_first = request.POST['private_first']
            else:
                private_first = 'false'

            expert = Expert.objects.get(pk=userid)

            if inSpecialtyArea == "true":
                expert.inspecialtyarea = True
            if highviewspast90days == "true":
                expert.highviewspast90days = True
            if citedpublication == "true":
                expert.citedpublication = True
            if relevance_factor == "true":
                expert.relevance_factor = True
            if likely_to_cite == "true":
                expert.likely_to_cite = True
            if may_include_reference == "true":
                expert.may_include_reference = True
            if might_refer_to == "true":
                expert.might_refer_to = True
            if relevant_to_research == "true":
                expert.relevant_to_research = True
            if within_area == "true":
                expert.within_area = True
            if on_expertise_topic == "true":
                expert.on_expertise_topic = True
            if especially_popular == "true":
                expert.especially_popular = True
            if highly_visible == "true":
                expert.highly_visible = True
            if highly_popular == "true":
                expert.highly_popular = True
            if private_first == "true":
                expert.private_first = True
            expert.save()
            expertName = expert.name
            expertTitle = expert.title
            expertEmail = expert.email
            expertPK = str(expert.pk)
            expertDomain = expert.domain
            expertSpecialization = expert.specialization
            if expertSpecialization is None or expertSpecialization == "":
                expertSpecialization = expertDomain
            
            expertwikipages = expert.expertwikipub_set.all()

            if 'Phase_1' in phase:
                message, html_content = phase1EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
                    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, especially_popular, 
                    highly_visible, highly_popular, private_first, True)
            elif 'Phase_2' in phase:
                message, html_content = phase2EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
                    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, True)
            elif 'Phase_3' in phase:
                message, html_content = phase3EmailContent(expertPK, expertName, expertTitle, expertSpecialization, expertwikipages, expertDomain, inSpecialtyArea, highviewspast90days,
                    citedpublication, relevance_factor, likely_to_cite, may_include_reference, might_refer_to, relevant_to_research, within_area, on_expertise_topic, True)

            return render_to_response("Preview.html",
                {"html_content": html_content, },
                context_instance=RequestContext(request))


@login_required
def posttotalkpage(request):

    if request.method == 'POST':
        if 'userpage' in request.POST and request.POST['userpage'] != '':
            userpage = request.POST['userpage']
            expertwikipage = Expertwikipub.objects.get(pk=userpage)

            expert = expertwikipage.expert
            expertName = expert.name

            comment = expertwikipage.comment
            wikipage = expertwikipage.wikipage
            wikipageTitle = wikipage.title
            wikipageURL = wikipage.url

            publications = []

            expertwikipagePublications = Expertwikipub.objects.filter(wikipage__title__exact=wikipageTitle,
                                                                      expert__name__exact=expertName)
            for index in range(len(expertwikipagePublications)):
                publications.append({})
                publications[index]['title'] = expertwikipagePublications[index].publication.title
                publications[index]['citations'] = expertwikipagePublications[index].publication.citations
                publications[index]['year'] = expertwikipagePublications[index].publication.publication_year
                publications[index]['fullcitation'] = expertwikipagePublications[index].publication.fullcitation

            # publications_Sorted = sorted(publications, key=lambda k: k['citations'])
            # postCommentstoTalkpages(wikipageTitle, wikipageURL, expertName, publications_Sorted, comment)
            postCommentstoTalkpages(wikipageTitle, wikipageURL, expertName, publications, comment)

            expertwikipage.submittedtotalkpage = True
            expertwikipage.save()

            expert.phase3 = True
            expert.emailCount = 0
            expert.save()

            return HttpResponse(json.dumps({}), content_type="application/json")

@xframe_options_exempt
def optout(request):

    if request.method == 'GET':
        if 'userid' in request.GET and request.GET['userid'] != '':
            userid = request.GET['userid']

            expert = Expert.objects.get(pk=userid)
            expert.withdrawal = True
            expert.returned = False
            if expert.phase2:
                expert.email2_opened = True
                expert.email2OpenedTime = timezone.now()
            else:
                expert.email1_opened = True
                expert.email1OpenedTime = timezone.now()
            expert.user_agent = request.META['HTTP_USER_AGENT']
            expert.ip_address = request.META['REMOTE_ADDR']
            expert.save()

            expertName = expert.name
            title = "Dr."
            # if "professor" in expert.title.lower():
            #   title = "Professor"

            # expertEmail = expert.email
            # expertDomain = expert.domain
            # expertSpecialization = expert.specialization
            # if expertSpecialization is None or expertSpecialization == "":
            #   expertSpecialization = expertDomain

            # message = "Dear Dr. " + expertName + ",\n\nWe are so sorry that you don't like to continue helping us to improve human knowledge."
            # html_content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html>'
            # html_content = html_content + '<p>Dear Dr. ' + expertName + ",</p><p><br>We are so sorry that you don't like to continue helping us to improve human knowledge.</p>"
            # message = message + "In case you changed your mind, the following link to return to our community:\n\n"
            # message = message + "http://wikipediastudy-env.us-east-1.elasticbeanstalk.com/interested?userid=" + str(expert.pk)
            # html_content = html_content + "<p>In case you changed your mind, <a href='http://wikipediastudy-env.us-east-1.elasticbeanstalk.com/interested?userid=" + str(expert.pk) + "'>click here</a> to return to our community"
            # message = message + "Sincerely,\n\n"
            # html_content = html_content + "<p><br>Sincerely,</p>"
            
            # message, html_content = fillEmailSignature(expertDomain, message, html_content)

            # subject = expertSpecialization + " Articles in Wikipedia"
            # from_email = settings.EMAIL_HOST_USER
            # to_list = [expertEmail, settings.EMAIL_HOST_USER]

            # msg = EmailMultiAlternatives(subject, message, from_email, to_list)
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()

            return render_to_response("Withdrawal.html",
                {"name": expertName, "title": title},
                context_instance=RequestContext(request))

@xframe_options_exempt
def interested(request):

    if request.method == 'GET':
        if 'userid' in request.GET and request.GET['userid'] != '':
            userid = request.GET['userid']

            expert = Expert.objects.get(pk=userid)
            expert.withdrawal = False
            expert.returned = True
            expert.emailCount = 0
            expert.phase2 = True
            expert.email1_opened = True
            expert.email1OpenedTime = timezone.now()
            expert.user_agent = request.META['HTTP_USER_AGENT']
            expert.ip_address = request.META['REMOTE_ADDR']
            expert.save()

            expertName = expert.name
            title = "Dr."
            # if "professor" in expert.title.lower():
            #   title = "Professor"

            sendemail_method(userid, 'Phase_2_EmailList', str(expert.inspecialtyarea).lower(),
                str(expert.highviewspast90days).lower(), str(expert.citedpublication).lower(),
                str(expert.relevance_factor).lower(), str(expert.likely_to_cite).lower(),
                str(expert.may_include_reference).lower(), str(expert.might_refer_to).lower(),
                str(expert.relevant_to_research).lower(), str(expert.within_area).lower(),
                str(expert.on_expertise_topic).lower(), str(expert.especially_popular).lower(), str(expert.highly_visible).lower(), 
                str(expert.highly_popular).lower(), str(expert.private_first).lower())

            return render_to_response("Interested.html",
                {"name": expertName, "title": title},
                context_instance=RequestContext(request))

@xframe_options_exempt
def notfound(request):

    if request.method == 'GET':
        return render_to_response("404.html",
            {},
            context_instance=RequestContext(request))

@login_required
def loadwikipages(request):

    if request.method == 'GET':
        if 'filename' in request.GET and request.GET['filename'] != '':
            filename = request.GET['filename']

            try:
                f = codecs.open('ExpertIdeas/' + str(filename) + '.html', encoding='utf-8')

                html_doc = ""

                for line in f:
                    html_doc = html_doc + repr(line)

                soup = BeautifulSoup(html_doc)

                WikipediaPages = soup.find_all('tr')

                for index in range(len(WikipediaPages)):
                    if index != 0:
                        WikipediaPage = WikipediaPages[index].find_all('td')

                        article_id = WikipediaPage[0].renderContents()
                        title = WikipediaPage[1].renderContents()
                        processedTitle = title.replace(" ", "_")
                        url = "https://en.wikipedia.org/wiki/" + processedTitle
                        edit_protection_level = WikipediaPage[2].renderContents()
                        quality_class = WikipediaPage[3].renderContents()
                        importance_class = WikipediaPage[4].renderContents()
                        page_length = WikipediaPage[5].renderContents()
                        watchers = WikipediaPage[6].renderContents()
                        views_last_90_days = WikipediaPage[14].renderContents()

                        wikipages = Wikipage.objects.filter(title=title)
                        if len(wikipages) == 0:
                            wikipage = Wikipage(article_id=article_id, title=title, url=url,
                                edit_protection_level=edit_protection_level, quality_class=quality_class,
                                importance_class=importance_class, page_length=page_length, watchers=watchers,
                                views_last_90_days=views_last_90_days)
                            wikipage.save()
                        else:
                            for wikipage in wikipages:
                                wikipage.article_id=article_id
                                wikipage.title=title
                                wikipage.url=url
                                wikipage.edit_protection_level=edit_protection_level
                                wikipage.quality_class=quality_class
                                wikipage.importance_class=importance_class
                                wikipage.page_length=page_length
                                wikipage.watchers=watchers
                                wikipage.views_last_90_days=views_last_90_days
                                wikipage.save()

                return render_to_response("SuccessfullyLoaded.html",
                    {},
                    context_instance=RequestContext(request))
            except Exception, e:
                return render_to_response("ProblemWithLoading.html",
                    {'message': str(e), },
                    context_instance=RequestContext(request))

@login_required
def loadauthorpaperwikipages(request):

    if request.method == 'GET':
        if 'filename' in request.GET and request.GET['filename'] != '' and 'discipline' in request.GET and request.GET['discipline'] != '':
            filename = request.GET['filename']
            discipline = request.GET['discipline']

            # try:
            f = codecs.open('ExpertIdeas/' + str(filename) + '.html', encoding='utf-8')

            html_doc = ""

            for line in f:
                html_doc = html_doc + repr(line)

            soup = BeautifulSoup(html_doc)

            WikipediaPages = soup.find_all('tr')

            for index in range(len(WikipediaPages)):
                if index != 0:
                    WikipediaPage = WikipediaPages[index].find_all('td')
                    if len(WikipediaPage) >= 12:
                        expert_name = WikipediaPage[0].renderContents()
                        expert_title = WikipediaPage[1].renderContents()
                        expert_specialization = WikipediaPage[2].renderContents()
                        expert_citations = WikipediaPage[3].renderContents()
                        expert_h_index = WikipediaPage[4].renderContents()
                        expert_i10_index = WikipediaPage[5].renderContents()
                        paper_title = WikipediaPage[6].find('a').renderContents()
                        paper_url = WikipediaPage[6].find('a')['href']
                        paper_citation = WikipediaPage[7].renderContents()
                        paper_year = WikipediaPage[8].renderContents()
                        # Find the appropriate title of the Wikipedia page from articleTitle.
                        appropriatewikipage_title = re.search("(.+) -", WikipediaPage[9].find('a').renderContents())

                        # IF appropriateArticleTitle is found:
                        if appropriatewikipage_title is not None:

                            # Assign the value of appropriateArticleTitle to articleTitle.
                            wikipage_title = appropriatewikipage_title.group(1)

                        lastname_occurrence = WikipediaPage[10].renderContents()
                        related_paper_number = len(WikipediaPage[11].find_all('a'))

                        wikipage = Wikipage.objects.get(title=wikipage_title)
                        experts = Expert.objects.filter(name=expert_name)
                        if len(experts) == 0:
                            expert = Expert(name=expert_name, domain=discipline,
                            title=expert_title, specialization=expert_specialization,
                            citations=expert_citations, HIndex=expert_h_index,
                            I10Index=expert_i10_index)
                            expert.save()
                        else:
                            for expert in experts:
                                expert.name=expert_name
                                expert.domain=discipline
                                expert.title=expert_title
                                expert.specialization=expert_specialization
                                expert.citations=expert_citations
                                expert.HIndex=expert_h_index
                                expert.I10Index=expert_i10_index
                                expert.save()

                        publications = Publication.objects.filter(title__exact=paper_title)
                        publication = None
                        # publicationhasnorelation = False
                        if len(publications) == 0:
                            publication = Publication(title=paper_title, citations=paper_citation,
                            publication_year=paper_year, url=paper_url)
                            publication.save()
                        else:
                            publication = publications[0]
                            # for publicationTemp in publications:
                            #   if not hasattr(publicationTemp, 'expertwikipub_set'):
                            #       publicationhasnorelation = True
                            #       publication = publicationTemp
                            #       break
                            # if publicationhasnorelation == False:
                            #   publication = Publication(title=paper_title, citations=paper_citation,
                            #       publication_year=paper_year, url=paper_url)
                            #   publication.save()
                        
                        expertwikipages = Expertwikipub.objects.filter(publication__title__exact=paper_title, expert__name__exact=expert_name)
                        if len(expertwikipages) == 0:
                            expertwikipage = Expertwikipub(publication=publication, wikipage=wikipage,
                            expert=expert, last_name_ocurances=lastname_occurrence,
                            related_publications_number=related_paper_number, comment='', timestamp=timezone.now())
                            expertwikipage.save()
                        else:
                            for expertwikipage in expertwikipages:
                                expertwikipage.publication=publication
                                expertwikipage.wikipage=wikipage
                                expertwikipage.expert=expert
                                expertwikipage.last_name_ocurances=lastname_occurrence
                                expertwikipage.related_publications_number=related_paper_number
                                expertwikipage.comment=''
                                expertwikipage.save()

            return render_to_response("SuccessfullyLoaded.html",
                {},
                context_instance=RequestContext(request))
            # except Exception, e:
            #   return render_to_response("ProblemWithLoading.html",
            #       {'message': str(e), },
            #       context_instance=RequestContext(request))

@login_required
def loadauthorpapers(request):

    if request.method == 'GET':
        if 'filename' in request.GET and request.GET['filename'] != '' and 'discipline' in request.GET and request.GET['discipline'] != '':
            filename = request.GET['filename']
            discipline = request.GET['discipline']

            # try:
            f = codecs.open('ExpertIdeas/' + str(filename) + '.html', encoding='utf-8')

            html_doc = ""

            for line in f:
                html_doc = html_doc + repr(line)

            soup = BeautifulSoup(html_doc)

            WikipediaPages = soup.find_all('tr')

            for index in range(len(WikipediaPages)):
                if index != 0:
                    WikipediaPage = WikipediaPages[index].find_all('td')
                    expert_name = WikipediaPage[0].renderContents()
                    expert_title = WikipediaPage[1].renderContents()
                    expert_specialization = WikipediaPage[2].renderContents()
                    expert_citations = WikipediaPage[3].renderContents()
                    expert_h_index = WikipediaPage[4].renderContents()
                    expert_i10_index = WikipediaPage[5].renderContents()
                    paper_title = WikipediaPage[6].find('a').renderContents()
                    paper_url = WikipediaPage[6].find('a')['href']
                    paper_citation = WikipediaPage[7].renderContents()
                    paper_year = WikipediaPage[8].renderContents()

                    experts = Expert.objects.filter(name=expert_name)
                    if len(experts) == 0:
                        expert = Expert(name=expert_name, domain=discipline,
                        title=expert_title, specialization=expert_specialization,
                        citations=expert_citations, HIndex=expert_h_index,
                        I10Index=expert_i10_index)
                        expert.save()
                    else:
                        for expert in experts:
                            expert.name=expert_name
                            expert.domain=discipline
                            expert.title=expert_title
                            expert.specialization=expert_specialization
                            expert.citations=expert_citations
                            expert.HIndex=expert_h_index
                            expert.I10Index=expert_i10_index
                            expert.save()

                    publications = Publication.objects.filter(title__exact=paper_title)
                    publication = None
                    # publicationhasnorelation = False
                    if len(publications) == 0:
                        publication = Publication(title=paper_title, citations=paper_citation,
                        publication_year=paper_year, url=paper_url)
                        publication.save()
                    else:
                        publication = publications[0]
                    expertwikipages = Expertwikipub.objects.filter(publication__title__exact=paper_title, expert__name__exact=expert_name)
                    if len(expertwikipages) == 0:
                        expertwikipage = Expertwikipub(publication=publication, wikipage=wikipage,
                        expert=expert, last_name_ocurances=lastname_occurrence,
                        related_publications_number=related_paper_number, comment='', timestamp=timezone.now())
                        expertwikipage.save()
                    else:
                        for expertwikipage in expertwikipages:
                            expertwikipage.publication=publication
                            expertwikipage.expert=expert
                            expertwikipage.save()

            return render_to_response("SuccessfullyLoaded.html",
                {},
                context_instance=RequestContext(request))

@login_required
def loaduniversityauthors(request):

    if request.method == 'GET':
        if 'filename' in request.GET and request.GET['filename'] != '' and 'discipline' in request.GET and request.GET['discipline'] != '' and 'title' in request.GET and request.GET['title'] != '':
            filename = request.GET['filename']
            discipline = request.GET['discipline']
            title = request.GET['title']

            with open('ExpertIdeas/' + str(filename) + '.csv', 'rb') as fr:
                reader = csv.reader(fr)

                firstRow = True
                for row in reader:
                    if firstRow:
                        firstRow = False
                    else:
                        expert_firstname = row[0]
                        expert_name = row[1]
                        expert_email = row[2]
                        expert_specialization = row[3]

                        randNum = random.randrange(0, 2)

                        if randNum == 1:
                            citedpublication = True

                        randNum = random.randrange(0, 2)

                        if randNum == 1:
                            highviewspast90days = True

                        expert = Expert(firstname=row[0], name=row[1], domain=discipline,
                        specialization=row[3], email=row[2], title=title, phase1=True,
                        citedpublication=citedpublication, highviewspast90days=highviewspast90days)
                        expert.save()

            return render_to_response("SuccessfullyLoaded.html",
                {},
                context_instance=RequestContext(request))

def convert_unicode(s):
    if isinstance(s, unicode):
        return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
    else:
        return s

# import ExpertIdeas.views
# class Request:
#     def __init__(self):
#        self.method = 'GET'
#        self.GET = {'filename1': 'Ideas_Repec_Dataset_Pilot3_Clean', 'filename2': 'Ideas_Repec_Dataset_Pilot3_Clean_Replace_Stub_FA_Recommendations', 'discipline':'Economics', 'title':'Dr.', 'study_version':'2'}

# request = Request()
# request.GET

# ExpertIdeas.views.loadrepecauthors(request)

def loadrepecauthors(request):

    if request.method == 'GET':
        if 'filename1' in request.GET and request.GET['filename1'] != '' and 'discipline' in request.GET and request.GET['discipline'] != '' and 'title' in request.GET and request.GET['title'] != '' and 'study_version' in request.GET and request.GET['study_version'] != '':
            filename1 = request.GET['filename1']
            if 'filename2' in request.GET and request.GET['filename2'] != '':
                filename2 = request.GET['filename2']
            discipline = request.GET['discipline']
            study_version = request.GET['study_version']
            title = 'Dr.'

            resultRowsTest = []

            savedSuccessfully = False

            with open('ExpertIdeas/' + str(filename1) + '.csv', 'rb') as fr1:
                reader1 = csv.reader(fr1)

                if 'filename2' in request.GET and request.GET['filename2'] != '':
                    with open('ExpertIdeas/' + str(filename2) + '.csv', 'rb') as fr2:
                        reader2 = csv.reader(fr2)

                        contactListRecommendations = {}

                        for row in reader2:
                            contactListRecommendations[row[0]] = row

                emailList = []
                contactIndex = 0
                header1 = next(reader1)
                for row in reader1:
                    contactIndex += 1
                    wikipagesID = []
                    wikipagesTitle = []
                    wikipagesURL = []

                    firstname = convert_unicode(row[0])
                    name = convert_unicode(row[1])
                    email = row[2]
                    specialization = row[3]
                    affiliation = convert_unicode(row[5])
                    location = convert_unicode(row[6])

                    affiliationGroup = re.search("(?:([^(].+))|(?:[(]\d\d?%[)][ ](.+))", affiliation)

                    # If affiliationGroup is found:
                    if affiliationGroup is not None:

                        # Assign the value of affiliationGroup to affiliation.
                        affiliation = affiliationGroup.group(1)

                    publications = []
                    years = []
                    citations = []

                    if 'filename2' in request.GET and request.GET['filename2'] != '':
                        recommendationsList = contactListRecommendations[email]
                        recommendationIndex = -2

                    for i in range(8, len(row) - 3, 4):
                        if 'filename2' in request.GET and request.GET['filename2'] != '':
                            recommendationIndex += 4
                        if row[i] != "" and row[i] is not None:
                            publications.append(convert_unicode(row[i]))
                            years.append(row[i+1])
                            citations.append(convert_unicode(row[i+2]))
                            if 'filename2' in request.GET and request.GET['filename2'] != '' and recommendationIndex+1 < len(recommendationsList) and recommendationsList[recommendationIndex] != '':
                                print ("email: " + str(email))
                                print ("recommendationIndex: " + str(recommendationIndex))
                                articleID = long(recommendationsList[recommendationIndex])
                                articleTitle = convert_unicode(recommendationsList[recommendationIndex+1])
                                # # Find the appropriate title of the Wikipedia page from articleTitle.
                                # appropriateArticleTitle = re.search("(.+) -", articleTitle)

                                # # IF appropriateArticleTitle is found:
                                # if appropriateArticleTitle is not None:

                                #     # Assign the value of appropriateArticleTitle to articleTitle.
                                #     articleTitle = appropriateArticleTitle.group(1)

                                wikipagesID.append(articleID)
                                wikipagesTitle.append(articleTitle)
                                wikipagesURL.append(convert_unicode(recommendationsList[recommendationIndex+2]))

                    if name != "" and email != "" and len(publications) > 0 and publications[0] != "" and not " " in email:
                        experts = Expert.objects.filter(email=email)
                        if len(experts) != 0:
                            for expert in experts:
                                if expert.firstname is None or expert.firstname == "":
                                    expert.firstname = convert_unicode(firstname)

                                if expert.name is None or expert.name == "":
                                    expert.name = convert_unicode(name)

                                if expert.domain is None or expert.domain == "":
                                    expert.domain = convert_unicode(discipline)

                                if expert.specialization is None or expert.specialization == "":
                                    expert.specialization = convert_unicode(specialization)

                                if expert.title is None or expert.title == "":
                                    expert.title = convert_unicode(title)

                                if expert.school is None or expert.school == "":
                                    expert.school = convert_unicode(affiliation)

                                if expert.location is None or expert.location == "":
                                    expert.location = convert_unicode(location)

                                if not expert.phase1:
                                    expert.phase1 = True
                                expert.save()

                        else:
                            inspecialtyarea = True
                            
                            if study_version == "0":
                                study_version = 0
                            elif study_version == "1":
                                study_version = 1
                            elif study_version == "2":
                                study_version = 2

                            private_first = False
                            highviewspast90days = False
                            especially_popular = False
                            highly_visible = False
                            highly_popular = False
                            
                            randNum = random.randrange(0, 2)
                            if randNum == 1:
                                private_first = True

                            randNum = random.randrange(0, 2)
                            if randNum == 1:
                                highviewspast90days = True

                                randNum = random.randrange(0, 3)
                                if randNum == 0:
                                    especially_popular = True
                                elif randNum == 1:
                                    highly_visible = True
                                else:
                                    highly_popular = True

                            citedpublication = False
                            relevance_factor = False
                            likely_to_cite = False
                            may_include_reference = False
                            might_refer_to = False
                            relevant_to_research = False
                            within_area = False
                            on_expertise_topic = False

                            if study_version == 0:
                                randNum = random.randrange(0, 2)
                                if randNum == 1:
                                    citedpublication = True

                            else:
                                randNum = random.randrange(0, 3)
                                if randNum == 1:
                                    citedpublication = True

                                    relevance_factor = True

                                    randNum = random.randrange(0, 3)
                                    if randNum == 0:
                                        relevant_to_research = True
                                    elif randNum == 1:
                                        within_area = True
                                    else:
                                        on_expertise_topic = True

                                elif randNum == 2:
                                    citedpublication = True

                                    randNum = random.randrange(0, 3)
                                    if randNum == 0:
                                        likely_to_cite = True
                                    elif randNum == 1:
                                        may_include_reference = True
                                    else:
                                        might_refer_to = True

                            expert = Expert(firstname=firstname, name=name, domain=discipline, 
                            specialization=specialization, email=email, title=title, school=affiliation, 
                            location=location, study_version=study_version, phase1=True, inspecialtyarea=inspecialtyarea, 
                            citedpublication=citedpublication, highviewspast90days=highviewspast90days, 
                            relevance_factor=relevance_factor, likely_to_cite=likely_to_cite, 
                            may_include_reference=may_include_reference, might_refer_to=might_refer_to, 
                            relevant_to_research=relevant_to_research, within_area=within_area, 
                            on_expertise_topic=on_expertise_topic, especially_popular=especially_popular, 
                            highly_visible=highly_visible, highly_popular=highly_popular, 
                            private_first=private_first)
                            expert.save()

                        # resultRowsTest.append("firstname=" + firstname + "name=" + str(name) +
                        #   "discipline=" + discipline + "specialization=" + specialization + 
                        #   "email=" + email + "title=" + str(title) +
                        #   "affiliation=" + str(affiliation) + "location=" + str(location) + "\n")
                        if 'filename2' in request.GET and request.GET['filename2'] != '':
                            for pubIndex in range(len(publications)):
                                if pubIndex < len(wikipagesID) and wikipagesID[pubIndex] != '':
                                    paper_title = publications[pubIndex]
                                    year = years[pubIndex]
                                    citation = citations[pubIndex]
                                    wikipageID = wikipagesID[pubIndex]
                                    wikipageTitle = wikipagesTitle[pubIndex]
                                    wikipageURL = wikipagesURL[pubIndex]

                                    publicationsList = Publication.objects.filter(title=paper_title)
                                    if len(publicationsList) != 0:
                                        for publication in publicationsList:
                                            if publication.publication_year is None or publication.publication_year == "":
                                                publication.publication_year = year

                                            if publication.fullcitation is None or publication.fullcitation == "":
                                                publication.fullcitation = citation

                                            publication.save()
                                            break
                                    else:
                                        publication = Publication(title=paper_title, publication_year=year, fullcitation = citation)
                                        publication.save()

                                    wikipages = Wikipage.objects.filter(article_id=wikipageID)
                                    if len(wikipages) != 0:
                                        for wikipage in wikipages:
                                            if wikipage.url is None or wikipage.url == "":
                                                wikipage.title = wikipageTitle
                                                wikipage.url = wikipageURL
                                                wikipage.save()

                                    else:
                                        wikipage = Wikipage(article_id=wikipageID, title=wikipageTitle, url=wikipageURL)
                                        wikipage.save()

                                    expertwikipub = Expertwikipub.objects.filter(publication__title__exact=paper_title, 
                                        expert__email__exact=email, wikipage__article_id__exact=wikipageID)

                                    if len(expertwikipub) == 0:
                                        expertwikipub = Expertwikipub(publication=publication, expert=expert, wikipage=wikipage)
                                        expertwikipub.save()

                            savedSuccessfully = True

                #       resultRowsTest.append("paper_title=" + paper_title + "year=" + str(year) +
                #           "citation=" + citation + "wikipageTitle=" + wikipageTitle + 
                #           "wikipageURL=" + wikipageURL + "\n")
                # return HttpResponse(resultRowsTest, content_type="text/html")

            # if savedSuccessfully:
            #     return render_to_response("SuccessfullyLoaded.html",
            #         {},
            #         context_instance=RequestContext(request))
            # else:
            #     return render_to_response("ProblemWithLoading.html",
            #         {},
            #         context_instance=RequestContext(request))

# import ExpertIdeas.views
# class Request:
#     def __init__(self):
#        self.method = 'GET'
#        self.GET = {'filename': 'Ideas_Repec_Dataset_Pilot3_Clean_Replace_Stub_FA_Recommendations_Stats'}

# request = Request()
# request.GET

# ExpertIdeas.views.loadwikiarticlesCSV(request)


def loadwikiarticlesCSV(request):

    if request.method == 'GET':
        if 'filename' in request.GET and request.GET['filename'] != '':
            filename = request.GET['filename']

            with open('ExpertIdeas/' + str(filename) + '.csv', 'rb') as fr:
                reader = csv.reader(fr)

                header = next(reader)
                for row in reader:
                    wikipageID = long(row[0])
                    wikipageTitle = row[1]
                    wikipageEditProtection = row[2]
                    wikipageClass = row[3]
                    wikipageImportance = row[4]
                    wikipagePageLength = int(row[5])
                    wikipageWatchersNum = int(row[6])
                    wikipageTimeOfLastEdit = iso8601.parse_date(row[7])
                    try:
                        wikipageRedirectsNum = int(row[8])
                    except:
                        wikipageRedirectsNum = 0
                    if row[9] != 0 and row[9] != "":
                        # 05:08, 25 August 2013
                        wikipagePageCreationDate = datetime.datetime.strptime(row[9], "%H:%M, %d %B %Y")
                        # 9/1/2005 22:03
                        # wikipagePageCreationDate = datetime.datetime.strptime(row[9], "%m/%d/%Y %H:%M")
                    else:
                        wikipagePageCreationDate = datetime.datetime.now()

                    wikipageTotalEdits = num(row[10])
                    wikipageTotalDistinctAuthors = int(row[12])
                    wikipagePast30DaysEdits = int(row[11])
                    wikipageRecentDistinctAuthors = 0
                    wikipagePast90DaysViews = int(row[13])
                    wikipageTotalReferences = int(row[14])
                    wikipageReferencesAfter2010 = int(row[15])
                    wikipageExternalHyperlinks = int(row[16])

                    wikipages = Wikipage.objects.filter(article_id=wikipageID)
                    if len(wikipages) != 0:
                        for wikipage in wikipages:
                            wikipage.title = wikipageTitle
                            wikipage.edit_protection_level = wikipageEditProtection
                            wikipage.quality_class = wikipageClass
                            wikipage.importance_class = wikipageImportance
                            wikipage.page_length = wikipagePageLength
                            wikipage.watchers = wikipageWatchersNum
                            wikipage.last_edit_time = wikipageTimeOfLastEdit
                            wikipage.creation_time = wikipagePageCreationDate

                            if wikipage.redirects == 0 or wikipage.redirects is None or wikipage.redirects == "":
                                wikipage.redirects = wikipageRedirectsNum
                            wikipage.total_edits = wikipageTotalEdits
                            if wikipage.distinct_authors == 0 or wikipage.distinct_authors is None or wikipage.distinct_authors == "":
                                wikipage.distinct_authors = wikipageTotalDistinctAuthors
                            wikipage.last_month_total_edits = wikipagePast30DaysEdits
                            if wikipage.last_month_distinct_authors == 0 or wikipage.last_month_distinct_authors is None or wikipage.last_month_distinct_authors == "":
                                wikipage.last_month_distinct_authors = wikipageRecentDistinctAuthors
                            wikipage.views_last_90_days = wikipagePast90DaysViews
                            wikipage.total_references = wikipageTotalReferences
                            wikipage.external_hyperlinks = wikipageExternalHyperlinks

                            wikipage.save()

                    else:
                        wikipage = Wikipage(title=wikipageTitle, article_id=wikipageID, 
                            edit_protection_level=wikipageEditProtection, quality_class=wikipageClass, 
                            importance_class=wikipageImportance, page_length=wikipagePageLength, 
                            watchers=wikipageWatchersNum, last_edit_time=wikipageTimeOfLastEdit, 
                            creation_time=wikipagePageCreationDate, redirects=wikipageRedirectsNum, 
                            total_edits=wikipageTotalEdits, distinct_authors=wikipageTotalDistinctAuthors, 
                            views_last_90_days=wikipagePast90DaysViews, total_references=wikipageTotalReferences, 
                            external_hyperlinks=wikipageExternalHyperlinks)
                        wikipage.save()

                return render_to_response("SuccessfullyLoaded.html",
                    {},
                    context_instance=RequestContext(request))


def loadVerifiedRecommendations(request):

    if request.method == 'GET':
        if ('filename' in request.GET and request.GET['filename'] != ''):
            filename = request.GET['filename']

            with open('ExpertIdeas/' + str(filename) + '.csv', 'rb') as fr:
                reader = csv.reader(fr)

                header = next(reader)
                for row in reader:
                    email = row[0]
                    print ("email: " + email)

                    for i in range(1, len(row) - 5, 6):
                        if row[i] != "" and row[i] is not None:
                            paper_title = convert_unicode(row[i])
                            articleID = long(row[i + 1])
                            print ("articleID: " + str(row[i + 1]))
                            articleTitle = row[i + 2]
                            articleURL = row[i + 3]
                            print ("articleURL: " + articleURL)
                            newArticleTitle = row[i + 4]
                            newArticleURL = row[i + 5]
                            print ("newArticleURL: " + newArticleURL)

                            if newArticleURL is not None and newArticleURL != "":
                                expertwikipub = Expertwikipub.objects.filter(publication__title__exact=paper_title,
                                                                             expert__email__exact=email,
                                                                             wikipage__article_id__exact=articleID)
                                # try:
                                expert = Expert.objects.get(email=email)
                                if expert.study_version == 2:
                                    expertSpecialization = expert.specialization
                                    expertwikipages = expert.expertwikipub_set.all()
                                    phase3 = expert.phase3
                                    indiscipline = expert.indiscipline

                                    interested = expert.returned
                                    withdrawal = expert.withdrawal
                                    email1_opened = expert.email1_opened
                                    email2_opened = expert.email2_opened
                                    email3_opened = expert.email3_opened

                                    linksClickedNum = 0
                                    commentsNum = 0
                                    ratingsNum = 0
                                    ExpertwikipubrefereesNum = 0

                                    for expertwikipage in expertwikipages:
                                        linksClickedNum += int(expertwikipage.link_clicked)
                                        if expertwikipage.comment is not None and expertwikipage.comment != "":
                                            commentsNum += 1
                                        if expertwikipage.rating is not None and expertwikipage.rating != "":
                                            ratingsNum += 1

                                        Expertwikipubreferees = expertwikipage.expertwikipubreferee_set.all()
                                        ExpertwikipubrefereesNum += len(Expertwikipubreferees)

                                    if (email is not None and email != '' and expertSpecialization is not None and
                                            expertSpecialization != "" and not indiscipline and int(withdrawal) == 0 and
                                            int(email2_opened) == 0 and int(phase3) == 0 and int(email3_opened) == 0 and
                                            int(linksClickedNum) == 0 and int(commentsNum) == 0 and
                                            int(ratingsNum) == 0 and int(ExpertwikipubrefereesNum) == 0):
                                        publication = Publication.objects.get(title=paper_title)
                                        wikipage = Wikipage.objects.filter(title=newArticleTitle)[0]
                                        wikipage.url = newArticleURL
                                        wikipage.save()

                                        if len(expertwikipub) == 0:
                                            expertwikipub = Expertwikipub(publication=publication,
                                                                          expert=expert,
                                                                          wikipage=wikipage)
                                        else:
                                            expertwikipub = expertwikipub[0]
                                            expertwikipub.publication = publication
                                            expertwikipub.expert = expert
                                            expertwikipub.wikipage = wikipage
                                        expertwikipub.save()
                                        expert.HIndex = 10
                                        expert.save()
                                # except:
                                #     pass

                return render_to_response("SuccessfullyLoaded.html",
                    {},
                    context_instance=RequestContext(request))


@login_required
def cleanDatabase(request):

    if request.method == 'GET':
        index = 0

        publicationList = Publication.objects.all()
        wikipageList = Wikipage.objects.all()
        expertList = Expert.objects.all()
        expertwikipubList = Expertwikipub.objects.all()

        for expertwikipub in expertwikipubList:

            similarExpertwikipages = expertwikipubList.exclude(pk=expertwikipub.pk).filter(publication=expertwikipub.publication, wikipage=expertwikipub.wikipage,
                                                          expert=expertwikipub.expert, link_clicked=False, submittedtotalkpage=False,
                                                          comment__isnull=True)

            if len(similarExpertwikipages) != 0:
                similarExpertwikipages.delete()

        # for publication in publicationList:

        #     expertwikipages = publication.expertwikipub_set.all()
        #     publicationkeywords = publication.publicationkeyword_set.all()
            
        #     if len(expertwikipages) == 0 and len(publicationkeywords) == 0:
        #         publication.delete()
        #         return render_to_response("Duplicated publication was: " + publication.title,
        #             {},
        #             context_instance=RequestContext(request))

        # for wikipage in Wikipage.objects.all():

        #   expertwikipages = wikipage.expertwikipub_set.all()
            
        #   if len(expertwikipages) == 0:
        #       wikipage.delete()
        #       if index == 1:
        #           return render_to_response("Duplicated wikipage was: " + wikipage.title,
        #               {},
        #               context_instance=RequestContext(request))
        #       index = 1
        #   else:
        #       return render_to_response("Unique wikipage is: " + wikipage.title,
        #           {},
        #           context_instance=RequestContext(request))

        # for expert in expertList:

        #   expertwikipages = expert.expertwikipub_set.all()
            
        #   if len(expertwikipages) == 0:
        #       return render_to_response("Duplicated expert is: " + expert.email,
        #           {},
        #           context_instance=RequestContext(request))
        #   else:
        #       return render_to_response("Unique expert is: " + expert.email,
        #           {},
        #           context_instance=RequestContext(request))

        return render_to_response("SuccessfullyLoaded.html",
            {},
            context_instance=RequestContext(request))


@login_required
def setInappropriateComments(request):

    if request.method == 'GET':

        expertwikipubList = Expertwikipub.objects.all()

        inappropriateComments = expertwikipubList.filter(submittedtotalkpage=False,
                                                              comment__isnull=False).exclude(comment="")
        if len(inappropriateComments) != 0:
            for inappropriateComment in inappropriateComments:
                inappropriateComment.rejectedbywikipedians = True
                inappropriateComment.save()


        return render_to_response("SuccessfullyLoaded.html",
            {},
            context_instance=RequestContext(request))


@login_required
def removePilot1(request):

    if request.method == 'GET':

        expertList = Expert.objects.all()

        for expert in expertList:

            if expert.study_version == 1:
                expert.delete()

        return render_to_response("SuccessfullyLoaded.html",
            {},
            context_instance=RequestContext(request))


# from django.http import HttpResponseRedirect
# from django.shortcuts import render_to_response
# from .forms import UploadFileForm

# # Imaginary function to handle an uploaded file.
# from somewhere import handle_uploaded_file

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             handle_uploaded_file(request.FILES['file'])
#             return HttpResponseRedirect('/success/url/')
#     else:
#         form = UploadFileForm()
#     return render_to_response('upload.html', {'form': form})