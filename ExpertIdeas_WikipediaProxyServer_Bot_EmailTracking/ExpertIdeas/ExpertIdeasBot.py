import sys
import os
import re
import requests
import time

# if not '/opt/python/run/venv/lib/python2.7/site-packages/core' in sys.path:
#     sys.path.append('/opt/python/run/venv/lib/python2.7/site-packages/core')
#
# if not 'PYWIKIBOT2_DIR' in os.environ:
#     os.environ['PYWIKIBOT2_DIR'] = '/opt/python/run/venv/lib/python2.7/site-packages/core'
#
if not 'C:\Users\onewe\Google Drive\DjangoProjects\WikipediaStudy\PyWikiBot_Clone\core' in sys.path:
    sys.path.append('C:\Users\onewe\Google Drive\DjangoProjects\WikipediaStudy\PyWikiBot_Clone\core')

if not 'PYWIKIBOT2_DIR' in os.environ:
    os.environ['PYWIKIBOT2_DIR'] = 'C:\Users\onewe\Google Drive\DjangoProjects\WikipediaStudy\PyWikiBot_Clone\core'

import pywikibot

# from pywikibot import i18n

class ExpertIdeasBot:

    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. ExpertIdeasBot.py in this case)

    def run(self, pageTitle, newContent):
        
        # Set the edit summary message
        site = pywikibot.Site()

        if not site.logged_in():
            site.login()

        # summary = i18n.twtranslate(site, u'ExpertIdeasBot-changing')
        talkTitle = u"{talk}:{title}".format(talk=site.namespaces()[1][0], # fetch Talk ns name through pywikibot
                                             title=pageTitle)
        page = pywikibot.Page(site, talkTitle)
        
        # Note: Can also test if bots can edit the page, e.g:
        # if not page.botMayEdit():
        #    pywikibot.output(u"Page %s is not bot-editable; skipping."
        #                     % page.title(asLink=True))
        #    return
        #
        # botMayEdit() returns false if {{nobots}} template is present, or {{bots}} template blacklists
        # the current bot username.  It returns true if {{nobots}} whitelists the current bot username.
        
        # Loads the given page, does some changes, and saves it.
        text = self.load(page)
        if text is None: # Note: can't use "if not text:", will fail if content is empty
            pywikibot.output(u'Page %s not retrieved appropriately.' % page.title(asLink=True))
            return

        text = text + newContent

        if not self.save(text, page):
            pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))

    def load(self, page):
        # Load the text of the given page.
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            text = u'' # if it doesn't exist, we'll create it
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None

    def save(self, text, page, comment=None, minorEdit=False,
             botflag=True, watchval=True):
        # Update the given page with new text.
        try:
            old_text = page.get()
        except pywikibot.NoPage:
            pass # noop
        except pywikibot.IsRedirectPage():
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
            return False
        
        # only save if something was changed...
        if text != old_text:
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            pywikibot.showDiff(page.get(), text)
            pywikibot.output(u'Comment: %s' % comment)

            try:
                page.text = text
                # Save the page
                page.save(comment=u'ExpertIdeasBot-changing',
                          minor=minorEdit, botflag=botflag, watch=watchval)
            except pywikibot.LockedPage:
                pywikibot.output(u"Page %s is locked; skipping."
                                 % page.title(asLink=True))
            except pywikibot.EditConflict:
                pywikibot.output(
                    u'Skipping %s because of edit conflict'
                    % (page.title()))
            except pywikibot.SpamfilterError as error:
                pywikibot.output(
                    u'Cannot change %s because of spam blacklist entry %s'
                    % (page.title(), error.url))
            else:
                return True
        return False


def postCommentstoTalkpages(articleTitle, articleURL, scholarName, scholarPublications, scholarComment):
    
    # Find the encoded title of the article.
    articleEncodedTitle = re.search("wiki/([^?]+)", articleURL)

    if articleEncodedTitle != None:
        articleEncodedTitle = articleEncodedTitle.group(1)
    else:
        articleEncodedTitle = articleTitle

    revisionID = None
    error_Count = 0
    while error_Count < 10:
        try:
            r = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles=' + articleEncodedTitle)
            r = r.json()
            query = r['query']
            pages = query['pages']
            break
        except Exception, e:
            print ("\n\n\nI cannot retrieve the revision ID of this article! Error Message: " + str(e))
            time.sleep(1)
            error_Count += 1
    try:
        revisions = pages.values()[0]['revisions']
        revisionID = revisions[0]['revid']
    except:
        pass

    text = u"\n== Dr. {0}'s comment on this article ==\n".format(scholarName)
    text += u"\n\nDr. {0} has reviewed ".format(scholarName)
    if revisionID != None:
        text += u"[https://en.wikipedia.org/w/index.php?title=" + articleEncodedTitle + u"&oldid=" + str(revisionID) + u" this Wikipedia page]"
    else:
        text += u" this Wikipedia page"
    text += u", and provided us with the following comments to improve its quality:\n"
    text += u"\n\n{{quote|text=" + scholarComment + u"}}\n\n"
    text += u"\nWe hope Wikipedians on this talk page can take advantage of these comments and improve the quality of the article accordingly.\n"
    text += u"\nWe believe Dr. {0} has expertise on the topic of this article, since he has published relevant scholarly research:\n\n".format(scholarName)
    for index in range(min(len(scholarPublications), 5)):
        text += u"\n\n*'''Reference "
        if len(scholarPublications) > 1:
            text += str(index + 1)
        # text += "''': {fullcitation}, Number of Citations: {n_citations}".format(fullcitation=scholarPublications[index]['fullcitation'], n_citations=scholarPublications[index]['citations'])
        text += "''': {fullcitation}".format(fullcitation=scholarPublications[index]['fullcitation'])
    text += u"\n\n~~~~\n"

    bot = ExpertIdeasBot()
    # Post the comment to the corresponding Talk page, and add both the Talk page and the main article to the bot's watchlist.
    bot.run(articleTitle, text)
