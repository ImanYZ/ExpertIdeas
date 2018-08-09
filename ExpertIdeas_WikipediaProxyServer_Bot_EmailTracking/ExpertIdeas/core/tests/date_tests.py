# -*- coding: utf-8  -*-
#
# (C) Pywikibot team, 2014
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 44b89d913ef0b1ff7fee593dd67bf332287ec26c $'

from tests.utils import unittest, PywikibotTestCase
from pywikibot import date


class TestDateMeta(type):
    """Test meta class"""

    def __new__(cls, name, bases, dct):
        """create the new class"""

        def test_method(formatname):

            def testMapEntry(self):
                """The test ported from date.py"""
                step = 1
                if formatname in date.decadeFormats:
                    step = 10
                try:
                    predicate, start, stop = date.formatLimits[formatname]
                except KeyError:
                    return

                for code, convFunc in date.formats[formatname].items():
                    for value in range(start, stop, step):
                        self.assertTrue(
                            predicate(value),
                            "date.formats['%(formatname)s']['%(code)s']:\n"
                            "invalid value %(value)d" % locals())

                        newValue = convFunc(convFunc(value))
                        self.assertEqual(
                            newValue, value,
                            "date.formats['%(formatname)s']['%(code)s']:\n"
                            "value %(newValue)d does not match %(value)s"
                            % locals())
            return testMapEntry

        for formatname in date.formats:
            test_name = "test_" + formatname
            dct[test_name] = test_method(formatname)
        return type.__new__(cls, name, bases, dct)


class TestDate(PywikibotTestCase):
    """Test cases for date library processed by unittest"""
    __metaclass__ = TestDateMeta


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
