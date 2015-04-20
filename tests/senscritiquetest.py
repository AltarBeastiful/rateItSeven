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

    def corretLogin(self):
        return SensCritique("legalizme@gmail.com", "12345")

    def test_shouldChangeMyUserAgent(self):
        expectedUserAgent = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)"
        sc = SensCritique("", "", expectedUserAgent, "http://gs.statcounter.com/detect")

        userAgent = sc.driver.find_element_by_xpath('//*[@id="content-inner"]/div/p[1]/em').get_attribute("innerHTML")
        self.assertEqual(expectedUserAgent, userAgent, "User agent are not equals")

    def test_shouldFailToLogin(self):
        sc = SensCritique("badlogin", "badpassword")
        self.assertFalse(sc.sign_in())

    def test_shouldSuccessLogin(self):
        sc = self.corretLogin()
        self.assertTrue(sc.sign_in())

    def test_shouldRetrieveListFromId(self):
        sc = self.corretLogin()
        sc.sign_in()

        listId = "857267"
        listTitle = "Une liste"
        myList = sc.retrieveListById(listId)

        self.assertEqual(listId, myList.id())
        self.assertEqual(listTitle, myList.title())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
