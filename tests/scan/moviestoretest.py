'''
Created on Apr 20, 2015

@author: paolo
'''
import os
import unittest

from rateItSeven.scan.moviestore import MovieStore


class TestMovieStore(unittest.TestCase):

    def setUp(self):
        self.basedir_abspath = os.path.abspath(__file__ + "/../../resources/files_to_scan")
        self.storepath = os.path.abspath(__file__ + "/../../resources/store")

    def tearDown(self):
        if os.path.isfile(self.storepath):
            os.remove(self.storepath)

    def test_persist_shouldCreateFile(self):
        with MovieStore(self.storepath, [self.basedir_abspath]) as store:
            store.persist()
            os.path.isfile(self.storepath)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()