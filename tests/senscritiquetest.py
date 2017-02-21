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
from rateItSeven.senscritique import SensCritique
from rateItSeven.movie import Movie
from rateItSeven.sclist import SCList, ArtType
import datetime


class TestSensCritique(unittest.TestCase):

    def setupBadLogin(self):
        self.sc.login = self.badLogin

    def setupCorretLogin(self):
        self.sc.login = self.goodLogin

    def test_shouldChangeMyUserAgent(self):
        # GIVEN
        expectedUserAgent = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)"
        sc = SensCritique("", "", expectedUserAgent)

        # WHEN
        sc.driver.get("http://gs.statcounter.com/detect")
        user_agent_node = sc.driver.find_element_by_xpath('//*[@id="section-faq"]/main/div/div[2]/div/p[1]/em')

        # THEN
        self.assertEqual(expectedUserAgent, user_agent_node.get_attribute('innerHTML'))

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
        self.shouldRetrieveMoviesFromList()
        self.shouldRetrieveAllMoviesFromList()
        self.shouldCreateList()
        self.shouldRetrieveListFromTitle()
        self.shouldAddMoviesToList()
        self.shouldDeleteMovies()
        self.shouldDeleteList()

    def shouldFailToLogin(self):
        # GIVEN
        self.setupBadLogin()

        # WHEN
        result = self.sc.sign_in()

        # THEN
        self.assertFalse(result)
        self.assertFalse(self.sc.is_logged_in())

    def shouldSuccessLogin(self):
        # GIVEN
        self.setupCorretLogin()

        # WHEN
        result = self.sc.sign_in()

        # THEN
        self.assertTrue(result)
        self.assertTrue(self.sc.is_logged_in())

    def shouldRetrieveListFromId(self):
        # GIVEN
        listId = "857267"
        listTitle = "Une liste"
        listDescription = "une descri"

        # WHEN
        self.myList = self.sc.retrieveListById(listId)

        # THEN
        self.assertEqual(listId, self.myList.id())
        self.assertEqual(listTitle, self.myList.title())
        self.assertEqual(listDescription, self.myList.description())

    def shouldRetrieveMoviesFromList(self):
        # GIVEN
        expectedMovies = [  {"title" : "Izo", "description" : "Une description d'IZO"}
                          , {"title" : "La Maison des 1000 morts", "description" : ""}
                          , {"title" : "Pi", "description" : ""} ]

        # WHEN
        movies = self.sc.retrieveMoviesFromList(self.myList)

        # THEN
        for expectedMovie in expectedMovies:
            movie = next(movies)

            self.assertEqual(expectedMovie["title"], movie.title())
            self.assertEqual(expectedMovie["description"], movie.description())

    def shouldRetrieveAllMoviesFromList(self):
        # GIVEN
        expectedMoviesCount = 70

        # WHEN
        movies = list(self.sc.retrieveMoviesFromList(self.myList))

        # THEN
        self.assertEqual(expectedMoviesCount, len(movies))

    def shouldCreateList(self):
        # GIVEN
        l = SCList()
        l.setTitle("a test list" + str(datetime.datetime.now()))
        l.setDescription("a description")
        l.setType(ArtType.film)

        self.assertFalse(l.isValid())

        # WHEN
        self.sc.createList(l)

        # THEN
        self.assertTrue(l.isValid())

        self.newList = l  # Save it for later tests

    def shouldRetrieveListFromTitle(self):
        # GIVEN
        title = self.newList.title()

        # WHEN
        myList = self.sc.retrieveListByTitle(title)

        # THEN
        self.assertEqual(self.newList.id(), myList.id())
        self.assertEqual(self.newList.title(), myList.title())
        self.assertEqual(self.newList.description(), myList.description())

    def shouldAddMoviesToList(self):
        # GIVEN
        # An SC list (self.newList)
        # Three movies, one with partial title
        movie1 = Movie("maison 1000 morts", "une descr")
        movie2 = Movie('The Green Mile')
        movie3 = Movie('Kick-Ass')

        expectedMovies = [Movie("La Maison des 1000 morts", "une descr"), Movie("La Ligne verte"), Movie("Kick-Ass")]

        # TODO: check if the movies were not there before

        # TODO: check if the movies were not there before

        # WHEN
        self.sc.addMovie(movie1, self.newList)
        self.sc.addMovie(movie2, self.newList)
        self.sc.addMovie(movie3, self.newList)

        # THEN
        movies = self.sc.retrieveMoviesFromList(self.newList)

        for expected in expectedMovies:
            movie = next(movies, None)

            self.assertIsNotNone(movie, expected.title())
            self.assertEqual(expected.title(), movie.title())
            self.assertEqual(expected.description(), movie.description())

    def shouldDeleteMovies(self):
        # GIVEN
        movies = ["La Maison des 1000 morts", "La Ligne verte", "Kick-Ass"]

        # WHEN
        self.sc.deleteMovies(movies, self.newList)

        # THEN
        movies = self.sc.retrieveMoviesFromList(self.newList)
        self.assertIsNone(next(movies, None))

    def shouldDeleteList(self):
        # GIVEN
        # An SC list (self.newList)
        deleted = self.sc.retrieveListById(self.newList.id())
        self.assertIsNotNone(deleted)

        # WHEN
        self.sc.deleteList(self.newList)

        deleted = self.sc.retrieveListById(self.newList.id())

        # THEN
        self.assertIsNone(deleted)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
