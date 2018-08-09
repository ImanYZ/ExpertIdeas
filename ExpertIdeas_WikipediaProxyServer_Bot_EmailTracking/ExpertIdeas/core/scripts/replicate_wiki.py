#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
This bot replicates all pages (from specific namespaces) in a wiki to a second
wiki within one family.

Example:
python replicate_wiki.py [-r] -ns 10 -f wikipedia -o nl li fy

to copy all templates from an nlwiki to liwiki and fywiki. It will show which
pages have to be changed if -r is not present, and will only actually write
pages if -r /is/ present.

You can add replicate_replace to your user_config.py, which has the following
format:

replicate_replace = {
    'wikipedia:li': {'Hoofdpagina': 'Veurblaad'}
}

to replace all occurences of 'Hoofdpagina' with 'Veurblaad' when writing to
liwiki. Note that this does not take the origin wiki into account.
"""
#
# (C) Kasper Souren 2012-2013
# (C) Pywikibot team, 2013-2014
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: a7defbcac90a2c177d9b6d7ecfb44dd187b3207e $'
#

import sys
from pywikibot import *
from itertools import imap


def namespaces(site):
    """dict from namespace number to prefix"""
    ns = dict(map(lambda n: (site.getNamespaceIndex(n), n),
                  site.namespaces()))
    ns[0] = ''
    return ns


def multiple_replace(text, word_dict):
    """Replace all occurrences in text of key value pairs in word_dict"""
    for key in word_dict:
        text = text.replace(key, word_dict[key])
    return text


class SyncSites:
    """Work is done in here."""

    def __init__(self, options):
        self.options = options

        if options.original_wiki:
            original_wiki = options.original_wiki
        else:
            original_wiki = config.mylang

        pywikibot.output("Syncing from " + original_wiki)

        family = options.family or config.family

        sites = options.destination_wiki

        self.original = Site(original_wiki, family)
        self.original.login()

        if options.namespace and 'help' in options.namespace:
            nsd = namespaces(self.original)
            for k in nsd:
                pywikibot.output('%s %s' % (k, nsd[k]))
            sys.exit()

        self.sites = map(lambda s: Site(s, family), sites)

        self.differences = {}
        self.user_diff = {}
        pywikibot.output('Syncing to', newline=False)
        for s in self.sites:
            s.login()
            self.differences[s] = []
            self.user_diff[s] = []
            pywikibot.output(str(s), newline=False)
        pywikibot.output('')

    def check_sysops(self):
        """Check if sysops are the same on all wikis """
        def get_users(site):
            userlist = [ul['name'] for ul in site.allusers(group='sysop')]
            return set(userlist)

        ref_users = get_users(self.original)
        for site in self.sites:
            users = get_users(site)
            diff = list(ref_users.difference(users))
            diff.sort()
            self.user_diff[site] = diff

    def check_namespaces(self):
        """Check all namespaces, to be ditched for clarity"""
        namespaces = [
            0,    # Main
            8,    # MediaWiki
            152,  # DPL
            102,  # Eigenschap
            104,  # Type
            106,  # Formulier
            108,  # Concept
            10,   # Sjabloon
        ]

        if self.options.namespace:
            pywikibot.output(str(options.namespace))
            namespaces = [int(options.namespace)]
        pywikibot.output("Checking these namespaces: %s\n" % (namespaces,))

        for ns in namespaces:
            self.check_namespace(ns)

    def check_namespace(self, namespace):
        """Check an entire namespace"""

        pywikibot.output("\nCHECKING NAMESPACE %s" % namespace)
        pages = imap(lambda p: p.title(),
                     self.original.allpages('!', namespace=namespace))
        for p in pages:
            if p not in ['MediaWiki:Sidebar', 'MediaWiki:Mainpage',
                         'MediaWiki:Sitenotice', 'MediaWiki:MenuSidebar']:
                try:
                    self.check_page(p)
                except pywikibot.exceptions.NoPage:
                    pywikibot.output('Bizarre NoPage exception that we are '
                                     'just going to ignore')
                except pywikibot.exceptions.IsRedirectPage:
                    pywikibot.output(
                        'error: Redirectpage - todo: handle gracefully')
        pywikibot.output('')

    def generate_overviews(self):
        """Create page on wikis with overview of bot results"""
        for site in self.sites:
            sync_overview_page = Page(site,
                                      'User:%s/sync.py overview' % site.user())
            output = "== Pages that differ from original ==\n\n"
            if self.differences[site]:
                output += "".join(map(lambda l: '* [[:%s]]\n' % l,
                                      self.differences[site]))
            else:
                output += "All important pages are the same"

            output += "\n\n== Admins from original that are missing here ==\n\n"
            if self.user_diff[site]:
                output += "".join(map(lambda l: '* %s\n' % l.replace('_', ' '),
                                      self.user_diff[site]))
            else:
                output += "All users from original are also present on this wiki"

            pywikibot.output(output)
            sync_overview_page.text = output
            sync_overview_page.save(self.put_message(site))

    def put_message(self, site):
        return ('%s replicate_wiki.py synchronization from %s'
                % (site.user(), str(self.original)))

    def check_page(self, pagename):
        """Check one page"""

        pywikibot.output("\nChecking %s" % pagename)
        sys.stdout.flush()
        page1 = Page(self.original, pagename)
        txt1 = page1.text

        for site in self.sites:
            if options.dest_namespace:
                prefix = namespaces(site)[int(options.dest_namespace)]
                if prefix:
                    prefix += ':'
                new_pagename = prefix + page1.titleWithoutNamespace()
                pywikibot.output("\nCross namespace, new title: %s"
                                 % new_pagename)
            else:
                new_pagename = pagename

            page2 = Page(site, new_pagename)
            if page2.exists():
                txt2 = page2.text
            else:
                txt2 = ''

            if str(site) in config.replicate_replace:
                txt_new = multiple_replace(txt1,
                                           config.replicate_replace[str(site)])
                if txt1 != txt_new:
                    pywikibot.output(
                        'NOTE: text replaced using config.sync_replace')
                    pywikibot.output('%s %s %s' % (txt1, txt_new, txt2))
                    txt1 = txt_new

            if txt1 != txt2:
                pywikibot.output("\n %s DIFFERS" % site)
                self.differences[site].append(pagename)

        if self.options.replace:
            page2.text = txt1
            page2.save(self.put_message(site))
        else:
            sys.stdout.write('.')
            sys.stdout.flush()


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-f", "--family", dest="family",
                        help="wiki family")

    parser.add_argument("-r", "--replace", action="store_true",
                        help="actually replace pages (without this option you will only get an overview page)")
    parser.add_argument("-o", "--original", dest="original_wiki",
                        help="original wiki")
    parser.add_argument('destination_wiki', metavar='destination', type=str, nargs='+',
                        help='destination wiki(s)')
    parser.add_argument("-ns", "--namespace", dest="namespace",
                        help="specify namespace")
    parser.add_argument("-dns", "--dest-namespace", dest="dest_namespace",
                        help="destination namespace (if different)")

    (options, args) = parser.parse_known_args()

    # sync is global for convenient IPython debugging
    sync = SyncSites(options)
    sync.check_sysops()
    sync.check_namespaces()
    sync.generate_overviews()
