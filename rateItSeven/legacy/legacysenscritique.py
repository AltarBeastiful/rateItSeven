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

import logging

from rateItSeven.legacy.movie import Movie
from rateItSeven.legacy.senscritiquepages import HomePage, ListCollectionPage, ListPage, \
    ListModule
from selenium.webdriver import PhantomJS, ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from rateItSeven.legacy import sclist
from rateItSeven.legacy.sclist import SCList

LINUX_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"


class LegacySensCritique(object):

    CHANGEPAGE_TIMEOUT = 20

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

        self.page.alreadySuscribed().click()

        self.page.loginField().send_keys(self.login)
        self.page.passwordField().send_keys(self.password)

        self.page.submitLoginButton().click()

        #TODO changing page so wait or something
        currentUser = self.page.username(self.CHANGEPAGE_TIMEOUT)

        if currentUser is not None:
            self._currentUsername = currentUser.value()
            logging.warn("Logged in with user " + self._currentUsername)

            return True
        else:
            if self.page.loginError() is not None:
                logging.error("Couldn't login : " + self.page.loginError().value())

            return False

    def is_logged_in(self):
        return self.page is not None and self.page.username() is not None

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

    def retrieveMoviesFromList(self, l : SCList):
        self.to(ListPage(l))

        for movie in self.page.movies():
            yield movie

    def createList(self, l : SCList):
        self.to(ListCollectionPage(self._currentUsername))

        self.page.create_list_button().click()

        self.page.new_list_title().send_keys(l.title())
        self.page.film_type_radio().click()
        self.page.classic_list_radio().click()
        self.page.public_list_radio().click()

        self.page.confirm_create_list_button().click()

        # Change the current page as we are now on the list page
        self.page = ListPage(l)
        self.page._driver = self.driver  # TODO: fixme, we don't want to use self.to(page) as it would reload the page

        self.page.set_description(l.description())

        url = self.driver.current_url
        l._id = url[url.rfind("/") + 1:]

        return l

    def deleteList(self, l : sclist):
        self.to(ListCollectionPage(self._currentUsername))

        for module in self.page.lists():
            if l.id() in module.url():

                # Alert box will be auto-accepted. Needed as Phantomjs cannot handle them
                self.driver.execute_script("window.confirm = function(msg) { return true; };")

                delete_button = module.delete_button()

                delete_action = ActionChains(self.driver)
                delete_action.move_to_element(module.title_node())
                delete_action.move_to_element(delete_button)
                delete_action.click(delete_button)

                delete_action.perform()

    def addMovie(self, movie: Movie, l : SCList):
        self.to(ListPage(l))

        self.page.query_input().send_keys(movie.title())

        add_button = self.page.add_movie_button(0)
        if add_button is None:
            return False  # Movie already in list

        if movie.description():
            self.page.movie_description_field(0).send_keys(movie.description())

        add_button.click()
        return True

    def deleteMovies(self, movies_to_delete, l : SCList):
        self.to(ListPage(l))

        for movie in self.page.movies():
            try:
                movies_to_delete.remove(movie.title())

                delete = movie.delete_button()
                delete.click()

                movie.confirm_delete_button().click()
                self.page.wait_loading_finished()
            except Exception as e:
                logging.error("Fail to delete movie " + movie.title() + ". " + format(e))

        return movies_to_delete

    def to(self, page):
        page.to(self.driver)
        self.page = page

    def createSCListFromListModule(self, module : ListModule):
        list = sclist.SCList(module.id())

        list.setTitle(module.title())
        list.setDescription(module.description())
        list.setType(None)  # TODO: parse the type

        return list
