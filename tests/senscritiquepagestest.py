'''
Created on Apr 20, 2015

@author: remi
'''
import unittest
from rateItSeven.senscritiquepages import UserPage, ListCollectionPage


class Test(unittest.TestCase):


    def testShouldCreateUserPage(self):
        page = UserPage("toto")

        self.assertEqual("toto", page._username)
        self.assertEqual("http://www.senscritique.com/toto", page.url())

    def testShouldCreateListCollectionPage(self):
        page = ListCollectionPage("toto")

        self.assertEqual("http://www.senscritique.com/toto/listes/likes", page.url())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
