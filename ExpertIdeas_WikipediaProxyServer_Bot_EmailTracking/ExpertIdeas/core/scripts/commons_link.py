#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Include Commons template in home wiki.

This bot functions mainly in the en.wikipedia, because it
compares the names of articles and category in English
language (standard language in Commons). If the name of
an article in Commons will not be in English but with
redirect, this also functions.

Run:
Syntax: python commons_link.py [action] [pagegenerator]

where action can be one of these:
 * pages      : Run over articles, include {{commons}}
 * categories : Run over categories, include {{commonscat}}

and pagegenerator can be one of these:
&params;

"""
#
# (C) Leonardo Gregianin, 2006
# (C) Pywikibot team, 2007-2014
#
# Distributed under the terms of the MIT license.
#
# Ported by Geoffrey "GEOFBOT" Mon for Google Code-In 2013
# User:Sn1per
#


__version__ = '$Id: fdc09502e2ac9f75bfadb6499185cc9ce36c1c24 $'

import re
import pywikibot
from pywikibot import textlib, pagegenerators, i18n, Bot

docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}


class CommonsLinkBot(Bot):
    def __init__(self, generator, **kwargs):
        self.availableOptions.update({
            'action': None,
        })
        super(CommonsLinkBot, self).__init__(**kwargs)

        self.generator = generator
        self.findTemplate = re.compile(ur'\{\{[Ss]isterlinks')
        self.findTemplate2 = re.compile(ur'\{\{[Cc]ommonscat')
        self.findTemplate3 = re.compile(ur'\{\{[Cc]ommons')

    def run(self):
        if not all((self.getOption('action'), self.generator)):
            return
        catmode = (self.getOption('action') == 'categories')
        for page in self.generator:
            try:
                pywikibot.output(u'\n>>>> %s <<<<' % page.title())
                commons = page.site.image_repository()
                commonspage = getattr(pywikibot,
                                      ('Page', 'Category')[catmode]
                                      )(commons, page.title())
                try:
                    getcommons = commonspage.get(get_redirect=True)
                    pagetitle = commonspage.title(withNamespace=not catmode)
                    if page.title() == pagetitle:
                        oldText = page.get()
                        text = oldText

                        # for Commons/Commonscat template
                        s = self.findTemplate.search(text)
                        s2 = getattr(self, 'findTemplate%d'
                                           % (2, 3)[catmode]).search(text)
                        if s or s2:
                            pywikibot.output(u'** Already done.')
                        else:
                            cats = textlib.getCategoryLinks(text, site=page.site)
                            text = textlib.replaceCategoryLinks(
                                u'%s{{commons%s|%s}}'
                                % (text, ('', 'cat')[catmode], pagetitle),
                                cats)
                            comment = i18n.twtranslate(page.site,
                                                       'commons_link%s-template-added'
                                                       % ('', '-cat')[catmode])
                            try:
                                self.userPut(page, oldText, text, comment=comment)
                            except pywikibot.EditConflict:
                                pywikibot.output(
                                    u'Skipping %s because of edit conflict'
                                    % page.title())

                except pywikibot.NoPage:
                    pywikibot.output(u'%s does not exist in Commons'
                                     % page.__class__.__name__)

            except pywikibot.NoPage:
                pywikibot.output(u'Page %s does not exist' % page.title())
            except pywikibot.IsRedirectPage:
                pywikibot.output(u'Page %s is a redirect; skipping.'
                                 % page.title())
            except pywikibot.LockedPage:
                pywikibot.output(u'Page %s is locked' % page.title())


def main():
    options = {}

    local_args = pywikibot.handleArgs()
    genFactory = pagegenerators.GeneratorFactory()

    for arg in local_args:
        if arg in ('pages', 'categories'):
            options['action'] = arg
        elif arg == '-always':
            options['always'] = True
        else:
            genFactory.handleArg(arg)

    if 'action' in options:
        gen = genFactory.getCombinedGenerator()
        if gen:
            gen = pagegenerators.PreloadingGenerator(gen)
            bot = CommonsLinkBot(gen, **options)
            bot.run()
            return
    pywikibot.showHelp()


if __name__ == "__main__":
    main()
