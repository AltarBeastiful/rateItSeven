#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
#
#   RateItSeven is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   RateItSeven is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with RateItSeven. If not, see <http://www.gnu.org/licenses/>.
#

import unittest
from unittest.mock import MagicMock

from selenium.webdriver.support import expected_conditions as EC

from rateItSeven.sclist import SCList
from rateItSeven.senscritiquepages import UserPage, ListCollectionPage, HomePage, \
    ListPage


class Test(unittest.TestCase):


    def testShouldCreateUserPage(self):
        page = UserPage("toto")

        self.assertEqual("toto", page._username)
        self.assertEqual("http://www.senscritique.com/toto", page.url())

    def testShouldCreateListCollectionPage(self):
        page = ListCollectionPage("toto")

        self.assertEqual("http://www.senscritique.com/toto/listes/all/likes", page.url())

    def testShouldCreateHomePage(self):
        page = HomePage()

        self.assertEqual("http://www.senscritique.com/", page.url())

    def testShouldCreateListPage(self):
        # GIVEN
        l = SCList("0042")
        l.setTitle("A title")

        # WHEN
        page = ListPage(l)

        # THEN
        self.assertEqual("http://www.senscritique.com/liste/A_title/0042", page.url())

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
        self.assertIsNone(node)

    def testShouldGetNode(self):
        # GIVEN
        page = HomePage()
        page.waitForNode = MagicMock()

        page.to(MagicMock())

        # WHEN
        node = page.alreadySuscribed()

        # THEN
        self.assertIsNotNone(node)
        page.waitForNode.assert_called_once_with('//button[@data-rel="btn-register" and @data-scmodal-type="login"]',
                                                 EC.visibility_of_element_located, 5, page._driver)

    def testShouldNotCheckAtIfNotSpecified(self):
        # GIVEN
        page = HomePage()
        page.waitForNode = MagicMock()

        # WHEN
        page.to(MagicMock())

        # THEN
        self.assertEqual([], page.waitForNode.mock_calls)

    def testShouldCheckAtIfSpecified(self):
        # GIVEN
        page = ListCollectionPage("toto")
        page.waitForNode = MagicMock()

        # WHEN
        page.to(MagicMock())

        # THEN
        page.waitForNode.assert_called_once_with('//button[@data-rel="sc-list-new"]', EC.element_to_be_clickable)

    def testShouldReturnNoneIfElementNotFound(self):
        #TODO
        self.assertTrue(True)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
