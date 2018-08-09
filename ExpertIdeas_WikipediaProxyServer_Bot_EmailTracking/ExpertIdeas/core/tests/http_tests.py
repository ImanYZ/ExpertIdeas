# -*- coding: utf-8  -*-
"""
Tests for http module.
"""
#
# (C) Pywikibot team, 2014
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 0063774cdf21a89f4022466b5ac9788a19a1bc19 $'


from pywikibot.comms import http, threadedhttp
from tests.utils import unittest


class HttpTestCase(unittest.TestCase):

    def test_get(self):
        r = http.request(site=None, uri='http://www.wikipedia.org/')
        self.assertIsInstance(r, str)
        self.assertTrue('<html lang="mul"' in r)

    def test_request(self):
        o = threadedhttp.Http()
        r = o.request('http://www.wikipedia.org/')
        self.assertIsInstance(r, tuple)
        self.assertIsInstance(r[0], dict)
        self.assertTrue('status' in r[0])
        self.assertIsInstance(r[0]['status'], str)
        self.assertEquals(r[0]['status'], '200')

        self.assertIsInstance(r[1], str)
        self.assertTrue('<html lang="mul"' in r[1])
        self.assertEquals(int(r[0]['content-length']), len(r[1]))

    def test_gzip(self):
        o = threadedhttp.Http()
        r = o.request('http://www.wikipedia.org/')
        self.assertTrue('-content-encoding' in r[0])
        self.assertEquals(r[0]['-content-encoding'], 'gzip')

        url = 'https://test.wikidata.org/w/api.php?action=query&meta=siteinfo'
        r = o.request(url)
        self.assertTrue('-content-encoding' in r[0])
        self.assertEquals(r[0]['-content-encoding'], 'gzip')


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
