import pywikibot
# from pywikibot import i18n

class ExpertIdeasBot:

    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. ExpertIdeasBot.py in this case)

    def run(self, pageTitle, newContent):
        # Set the edit summary message
        site = pywikibot.Site()
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


def postCommentstoTalkpages(articleTitle, scholarName, scholarPublication, publicationCitation, scholarComment):
    
    text = u"\n== Professor {0}'s comment on this article ==\n".format(scholarName)
    text += u"\nProfessor {0} has recently published the following research publication which is related to this Wikipedia article:\n".format(scholarName)
    text += u"Reference: {title}, Number of Citations: {n_citations}\n".format(title=scholarPublication, n_citations=publicationCitation)
    text += u"\nProfessor {0} has reviewed this Wikipedia page, and provided us with the following comments to improve its quality:\n".format(scholarName)
    text += u"\n{0}\n".format(scholarComment)
    text += u"\nWe hope Wikipedians on this talk page can take advantage of these comments and improve the quality of the article accordingly.\n"
    text += u"\n~~~~\n"

    bot = ExpertIdeasBot()
    # Post the comment to the corresponding Talk page, and add both the Talk page and the main article to the bot's watchlist.
    bot.run(articleTitle, text)
