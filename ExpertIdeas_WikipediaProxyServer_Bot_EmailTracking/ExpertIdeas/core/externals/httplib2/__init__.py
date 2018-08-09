import os
import sys

path = os.path.dirname(__file__)+os.path.sep+'python'+str(sys.version_info[0])
sys.path.insert(0, path)
del sys.modules['httplib2']
import httplib2
