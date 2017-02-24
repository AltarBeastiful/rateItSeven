#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
#   Copyright 2015, Paolo de Vathaire <paolo.devathaire@gmail.com>
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
import json

import requests
from synthetic import synthesize_constructor
from synthetic import synthesize_property


_HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'dnt': '1', 'referer': 'https://www.senscritique.com/',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept-encoding': 'gzip, deflate, br',
    'origin': 'https://www.senscritique.com', 'x-requested-with': 'XMLHttpRequest',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en,en-US;q=0.8,ja;q=0.6,fr;q=0.4,de;q=0.2,en-ZA;q=0.2'
}


@synthesize_property('email', contract=str)
@synthesize_property('password', contract=str)
@synthesize_constructor()
class AuthSrv(object):
    _URL = "https://www.senscritique.com/sc2/auth/login.json"

    def dologin(self):
        """
        Send a login request with the given credentials
        :return: The session cookies returned by SC
        :rtype: requests.cookies.RequestsCookieJar
        """
        data = {
            'email': self.email,
            'pass': self.password,
        }
        response = requests.post(self._URL, headers=_HEADERS, data=data)
        if response.status_code != 200:
            raise Exception
        content = json.loads(response.text)
        if not content["json"]["success"]:
            raise UnauthorizedException
        return response.cookies


class UnauthorizedException(Exception):
    pass
