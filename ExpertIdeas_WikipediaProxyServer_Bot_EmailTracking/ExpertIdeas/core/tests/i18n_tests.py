# -*- coding: utf-8  -*-
#
# (C) Pywikipedia bot team, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 78ddc8966f60cf4282519872ec0f8ddc59adc1cd $'

from pywikibot import i18n

from tests.utils import unittest, PywikibotTestCase


class TestTranslate(PywikibotTestCase):
    def setUp(self):
        self.msg_localized = {'en': u'test-localized EN',
                              'nl': u'test-localized NL',
                              'fy': u'test-localized FY'}
        self.msg_semi_localized = {'en': u'test-semi-localized EN',
                                   'nl': u'test-semi-localized NL'}
        self.msg_non_localized = {'en': u'test-non-localized EN'}
        self.msg_no_english = {'ja': u'test-no-english JA'}
        super(TestTranslate, self).setUp()

    def testLocalized(self):
        self.assertEqual(i18n.translate('en', self.msg_localized,
                                        fallback=True),
                         u'test-localized EN')
        self.assertEqual(i18n.translate('nl', self.msg_localized,
                                        fallback=True),
                         u'test-localized NL')
        self.assertEqual(i18n.translate('fy', self.msg_localized,
                                        fallback=True),
                         u'test-localized FY')

    def testSemiLocalized(self):
        self.assertEqual(i18n.translate('en', self.msg_semi_localized,
                                        fallback=True),
                         u'test-semi-localized EN')
        self.assertEqual(i18n.translate('nl', self.msg_semi_localized,
                                        fallback=True),
                         u'test-semi-localized NL')
        self.assertEqual(i18n.translate('fy', self.msg_semi_localized,
                                        fallback=True),
                         u'test-semi-localized NL')

    def testNonLocalized(self):
        self.assertEqual(i18n.translate('en', self.msg_non_localized,
                                        fallback=True),
                         u'test-non-localized EN')
        self.assertEqual(i18n.translate('fy', self.msg_non_localized,
                                        fallback=True),
                         u'test-non-localized EN')
        self.assertEqual(i18n.translate('nl', self.msg_non_localized,
                                        fallback=True),
                         u'test-non-localized EN')
        self.assertEqual(i18n.translate('ru', self.msg_non_localized,
                                        fallback=True),
                         u'test-non-localized EN')

    def testNoEnglish(self):
        self.assertEqual(i18n.translate('en', self.msg_no_english,
                                        fallback=True),
                         u'test-no-english JA')
        self.assertEqual(i18n.translate('fy', self.msg_no_english,
                                        fallback=True),
                         u'test-no-english JA')
        self.assertEqual(i18n.translate('nl', self.msg_no_english,
                                        fallback=True),
                         u'test-no-english JA')


class TestTWN(PywikibotTestCase):
    def setUp(self):
        self.orig_messages_package_name = i18n.messages_package_name
        i18n.messages_package_name = 'tests.i18n'
        super(TestTWN, self).setUp()

    def tearDown(self):
        super(TestTWN, self).tearDown()
        i18n.messages_package_name = self.orig_messages_package_name


class TestTWTranslate(TestTWN):

    def testLocalized(self):
        self.assertEqual(i18n.twtranslate('en', 'test-localized'),
                         u'test-localized EN')
        self.assertEqual(i18n.twtranslate('nl', 'test-localized'),
                         u'test-localized NL')
        self.assertEqual(i18n.twtranslate('fy', 'test-localized'),
                         u'test-localized FY')

    def testSemiLocalized(self):
        self.assertEqual(i18n.twtranslate('en', 'test-semi-localized'),
                         u'test-semi-localized EN')
        self.assertEqual(i18n.twtranslate('nl', 'test-semi-localized'),
                         u'test-semi-localized NL')
        self.assertEqual(i18n.twtranslate('fy', 'test-semi-localized'),
                         u'test-semi-localized NL')

    def testNonLocalized(self):
        self.assertEqual(i18n.twtranslate('en', 'test-non-localized'),
                         u'test-non-localized EN')
        self.assertEqual(i18n.twtranslate('fy', 'test-non-localized'),
                         u'test-non-localized EN')
        self.assertEqual(i18n.twtranslate('nl', 'test-non-localized'),
                         u'test-non-localized EN')
        self.assertEqual(i18n.twtranslate('ru', 'test-non-localized'),
                         u'test-non-localized EN')

    def testNoEnglish(self):
        self.assertRaises(i18n.TranslationError, i18n.twtranslate, 'en', 'test-no-english')


class TestTWNTranslate(TestTWN):
    " Test {{PLURAL:}} support "

    def testNumber(self):
        """ use a number """
        self.assertEqual(
            i18n.twntranslate('de', 'test-plural', 0) % {'num': 0},
            u'Bot: Ändere 0 Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-plural', 1) % {'num': 1},
            u'Bot: Ändere 1 Seite.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-plural', 2) % {'num': 2},
            u'Bot: Ändere 2 Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-plural', 3) % {'num': 3},
            u'Bot: Ändere 3 Seiten.')
        self.assertEqual(
            i18n.twntranslate('en', 'test-plural', 0) % {'num': 'no'},
            u'Bot: Changing no pages.')
        self.assertEqual(
            i18n.twntranslate('en', 'test-plural', 1) % {'num': 'one'},
            u'Bot: Changing one page.')
        self.assertEqual(
            i18n.twntranslate('en', 'test-plural', 2) % {'num': 'two'},
            u'Bot: Changing two pages.')
        self.assertEqual(
            i18n.twntranslate('en', 'test-plural', 3) % {'num': 'three'},
            u'Bot: Changing three pages.')

    def testString(self):
        """ use a string """
        self.assertEqual(
            i18n.twntranslate('en', 'test-plural', '1') % {'num': 'one'},
            u'Bot: Changing one page.')

    def testDict(self):
        """ use a dictionary """
        self.assertEqual(
            i18n.twntranslate('en', 'test-plural', {'num': 2}),
            u'Bot: Changing 2 pages.')

    def testExtended(self):
        """ use additional format strings """
        self.assertEqual(
            i18n.twntranslate('fr', 'test-plural', {'num': 1, 'descr': 'seulement'}),
            u'Robot: Changer seulement une page.')

    def testExtendedOutside(self):
        """ use additional format strings also outside """
        self.assertEqual(
            i18n.twntranslate('fr', 'test-plural', 1) % {'descr': 'seulement'},
            u'Robot: Changer seulement une page.')

    def testMultiple(self):
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', 1)
            % {'action': u'Ändere', 'line': u'eine'},
            u'Bot: Ändere eine Zeile von einer Seite.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', 2)
            % {'action': u'Ändere', 'line': u'zwei'},
            u'Bot: Ändere zwei Zeilen von mehreren Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', 3)
            % {'action': u'Ändere', 'line': u'drei'},
            u'Bot: Ändere drei Zeilen von mehreren Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', (1, 2, 2))
            % {'action': u'Ändere', 'line': u'eine'},
            u'Bot: Ändere eine Zeile von mehreren Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', [3, 1, 1])
            % {'action': u'Ändere', 'line': u'drei'},
            u'Bot: Ändere drei Zeilen von einer Seite.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', ["3", 1, 1])
            % {'action': u'Ändere', 'line': u'drei'},
            u'Bot: Ändere drei Zeilen von einer Seite.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals', "321")
            % {'action': u'Ändere', 'line': u'dreihunderteinundzwanzig'},
            u'Bot: Ändere dreihunderteinundzwanzig Zeilen von mehreren Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals',
                              {'action': u'Ändere', 'line': 1, 'page': 1}),
            u'Bot: Ändere 1 Zeile von einer Seite.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals',
                              {'action': u'Ändere', 'line': 1, 'page': 2}),
            u'Bot: Ändere 1 Zeile von mehreren Seiten.')
        self.assertEqual(
            i18n.twntranslate('de', 'test-multiple-plurals',
                              {'action': u'Ändere', 'line': "11", 'page': 2}),
            u'Bot: Ändere 11 Zeilen von mehreren Seiten.')

    def testMultipleWrongParameterLength(self):
        """ Test wrong parameter lenght"""
        with self.assertRaisesRegexp(ValueError, "Length of parameter does not match PLURAL occurences"):
            self.assertEqual(
                i18n.twntranslate('de', 'test-multiple-plurals', (1, 2))
                % {'action': u'Ändere', 'line': u'drei'},
                u'Bot: Ändere drei Zeilen von mehreren Seiten.')

        with self.assertRaisesRegexp(ValueError, "Length of parameter does not match PLURAL occurences"):
            self.assertEqual(
                i18n.twntranslate('de', 'test-multiple-plurals', ["321"])
                % {'action': u'Ändere', 'line': u'dreihunderteinundzwanzig'},
                u'Bot: Ändere dreihunderteinundzwanzig Zeilen von mehreren Seiten.')

    def testMultipleNonNumbers(self):
        """ Numbers or string numbers are required for tuple or list items """
        with self.assertRaisesRegexp(ValueError, "invalid literal for int\(\) with base 10: 'drei'"):
            self.assertEqual(
                i18n.twntranslate('de', 'test-multiple-plurals', ["drei", "1", 1])
                % {'action': u'Ändere', 'line': u'drei'},
                u'Bot: Ändere drei Zeilen von einer Seite.')
        with self.assertRaisesRegexp(ValueError, "invalid literal for int\(\) with base 10: 'elf'"):
            self.assertEqual(
                i18n.twntranslate('de', 'test-multiple-plurals',
                                  {'action': u'Ändere', 'line': "elf", 'page': 2}),
                u'Bot: Ändere elf Zeilen von mehreren Seiten.')

    def testAllParametersExist(self):
        with self.assertRaisesRegexp(KeyError, "u'line'"):
            # all parameters must be inside twntranslate
            self.assertEqual(
                i18n.twntranslate('de', 'test-multiple-plurals',
                                  {'line': 1, 'page': 1})
                % {'action': u'Ändere'},
                u'Bot: Ändere 1 Zeile von einer Seite.')


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
