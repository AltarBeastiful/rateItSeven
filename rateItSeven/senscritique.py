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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


LINUX_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"
SC_HOME_PAGE = 'http://senscritique.com'


class SensCritique(object):

    '''
    Interact with SensCritique website
    '''

    def __init__(self, login, password, userAgent=LINUX_USER_AGENT, homePage=SC_HOME_PAGE):
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
        self.driver.get(homePage)

    def sign_in(self):
        '''
        Sign-in to SensCritique using the given login details

        :rtype: bool
        :Return: true if login succeeded, false otherwise
        '''

        loginForm = self.getNode('//*[@id="wrap"]/header/div[1]/div/div/div/div')
        hover = ActionChains(self.driver).move_to_element(loginForm)
        hover.perform()

        loginField = self.getNode('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/input[1]')
        passwordField = self.getNode('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/input[2]')

        loginField.send_keys(self.login)
        passwordField.send_keys(self.password)

        submit = self.getNode('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/fieldset/input')
        submit.click()

        try:
            currentUser = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="wrap"]/header/div[1]/div/div/div/a[3]')))
            currentUserChildNodes = currentUser.find_elements_by_xpath(".//*")

            if len(currentUserChildNodes) == 2:
                logging.info("Logged in with user " + currentUserChildNodes[1].get_attribute('innerHTML'))

            return True
        except TimeoutException:
            loginError = self.getNode('//*[@id="wrap"]/header/div[1]/div/div/div/div/form/fieldset/p')

            if loginError is not None:
                logging.error("Couldn't login : " + loginError.get_attribute('innerHTML'))

            return False

    def getNode(self, xpath):
        try:
            node = self.driver.find_element_by_xpath(xpath);
        except NoSuchElementException:
            node = None
        finally:
            return node

