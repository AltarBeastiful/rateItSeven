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

import logging
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from rateItSeven import sclist
from rateItSeven.senscritiquepages import HomePage, ListCollectionPage, ListPage, \
    ListModule
from rateItSeven.sclist import SCList


LINUX_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"


class SensCritique(object):

    '''
    Interact with SensCritique website
    '''

    def __init__(self, login, password, userAgent=LINUX_USER_AGENT):
        '''
        Constructor

        :param login:
        :param password:
        '''

        self.login = login
        self.password = password

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            userAgent
        )
        self.driver = PhantomJS(desired_capabilities=dcap)
        self.driver.set_window_size(1366, 768)

    def sign_in(self):
        '''
        Sign-in to SensCritique using the given login details

        :rtype: bool
        :Return: true if login succeeded, false otherwise
        '''

        self.to(HomePage())

        self.page.alreadySuscribed().hover()

        self.page.loginField().send_keys(self.login)
        self.page.passwordField().send_keys(self.password)

        self.page.submitLoginButton().click()

        currentUser = self.page.username()

        if currentUser is not None:
            self._currentUsername = currentUser.value()
            logging.warn("Logged in with user " + self._currentUsername)

            return True
        else:
            if self.page.loginError() is not None:
                logging.error("Couldn't login : " + self.page.loginError().value())

            return False

    def retrieveListById(self, listId):
        self.to(ListCollectionPage(self._currentUsername))

        for l in self.page.lists():
            if listId in l.url():
                return self.createSCListFromListModule(l)

        return None

    def retrieveListByTitle(self, title):
        self.to(ListCollectionPage(self._currentUsername))

        for l in self.page.lists():
            if l.title() == title:
                return self.createSCListFromListModule(l)

        return None

    def retrieveMoviesFromList(self, l):
        self.to(ListPage(l))

        for movie in self.page.movies():
            yield movie

    def addMovie(self, movie, l : SCList):
        self.to(ListPage(l))

        self.page.query_input().send_keys(movie)

        add_button = self.page.add_movie_button(0)
        if add_button is None:
            return False

        add_button.click()
        return True

    def to(self, page):
        page.to(self.driver)
        self.page = page

    def createSCListFromListModule(self, module : ListModule):
        list = sclist.SCList(module.id())

        list.setTitle(module.title())
        list.setDescription(module.description())
        list.setType(None)  # TODO: parse the type

        return list
