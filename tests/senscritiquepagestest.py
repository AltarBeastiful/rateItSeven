'''
Created on Apr 20, 2015

@author: remi
'''
import unittest
from unittest.mock import MagicMock

from selenium.webdriver.support import expected_conditions as EC

from rateItSeven.senscritiquepages import UserPage, ListCollectionPage, HomePage


class Test(unittest.TestCase):


    def testShouldCreateUserPage(self):
        page = UserPage("toto")

        self.assertEqual("toto", page._username)
        self.assertEqual("http://www.senscritique.com/toto", page.url())

    def testShouldCreateListCollectionPage(self):
        page = ListCollectionPage("toto")

        self.assertEqual("http://www.senscritique.com/toto/listes/likes", page.url())

    def testShouldCreateHomePage(self):
        page = HomePage()

        self.assertEqual("http://www.senscritique.com/", page.url())

    def testShouldGoToURL(self):
        # GIVEN
        page = HomePage()

        # WHEN
        page.to(MagicMock())

        # THEN
        page._driver.get.assert_called_once_with("http://www.senscritique.com/")

    def testNonCurrentPageReturnsNoneElements(self):
        # GIVEN
        page = HomePage()

        # WHEN
        node = page.alreadySuscribed()

        # THEN
        self.assertTrue(node is None)

    def testShouldGetNode(self):
        # GIVEN
        page = HomePage()
        page.waitForNode = MagicMock()

        page.to(MagicMock())

        # WHEN
        node = page.alreadySuscribed()

        # THEN
        self.assertTrue(node is not None)
        page.waitForNode.assert_called_once_with('//*[@id="wrap"]/header/div[1]/div/div/div/div',
                                                 EC.presence_of_element_located, 2)

    def testShouldReturnNoneIfElementNotFound(self):
        #TODO
        self.assertTrue(True)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
