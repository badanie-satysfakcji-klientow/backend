import unittest

def suite():
    return unittest.TestLoader().discover("appname.tests", pattern="*.py")