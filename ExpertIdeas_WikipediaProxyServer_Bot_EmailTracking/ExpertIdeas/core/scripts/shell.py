#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Spawns an interactive Python shell.

Usage:
    python pwb.py shell

"""
# (C) Pywikibot team, 2014
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 0f7337f27e02e2f053384b9d811b878fbe583c19 $'
#

if __name__ == "__main__":
    import code
    code.interact("""Welcome to the Pywikibot interactive shell!""")
