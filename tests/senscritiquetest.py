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
from rateItSeven.senscritique import SensCritique


class TestSensCritique(unittest.TestCase):

    def setupBadLogin(self):
        self.sc.login = self.badLogin

    def setupCorretLogin(self):
        self.sc.login = self.goodLogin

    def test_shouldChangeMyUserAgent(self):
        expectedUserAgent = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)"
        sc = SensCritique("", "", expectedUserAgent, "http://gs.statcounter.com/detect")

    def testSensCritique(self):
        # Setup
        self.badLogin = "badLogin"

        self.goodLogin = "legalizme@gmail.com"
        self.password = "12345"

        self.sc = SensCritique("", self.password)

        # Scenarios

        self.shouldFailToLogin()
        self.shouldSuccessLogin()
        self.shouldRetrieveListFromId()
        self.shouldRetrieveListFromTitle()
        self.shouldRetrieveMoviesFromList()

    def shouldFailToLogin(self):
        # GIVEN
        self.setupBadLogin()

        # WHEN
        result = self.sc.sign_in()

        # THEN
        self.assertFalse(result)

    def shouldSuccessLogin(self):
        # GIVEN
        self.setupCorretLogin()

        # WHEN
        result = self.sc.sign_in()

        # THEN
        self.assertTrue(result)

    def shouldRetrieveListFromId(self):
        # GIVEN
        listId = "857267"
        listTitle = "Une liste"
        listDescription = "une descri"

        # WHEN
        myList = self.sc.retrieveListById(listId)

        # THEN
        self.assertEqual(listId, myList.id())
        self.assertEqual(listTitle, myList.title())
        self.assertEqual(listDescription, myList.description())

    def shouldRetrieveListFromTitle(self):
        # GIVEN
        listId = "857267"
        listTitle = "Une liste"
        listDescription = "une descri"

        # WHEN
        self.myList = self.sc.retrieveListByTitle(listTitle)

        # THEN
        self.assertEqual(listId, self.myList.id())
        self.assertEqual(listTitle, self.myList.title())
        self.assertEqual(listDescription, self.myList.description())

    def shouldRetrieveMoviesFromList(self):
        # GIVEN
        # WHEN
        movies = self.sc.retrieveMoviesFromList(self.myList)

        # THEN
        self.assertEqual("Izo", next(movies).title())
        self.assertEqual("La Maison des 1000 morts", next(movies).title())
        self.assertEqual("Pi", next(movies).title())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
