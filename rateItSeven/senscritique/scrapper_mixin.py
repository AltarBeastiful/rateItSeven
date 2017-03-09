#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   === This file is part of RateItSeven ===
#
#   Copyright 2017, Rémi Benoit <r3m1.benoit@gmail.com>
#   Copyright 2017, Paolo de Vathaire <paolo.devathaire@gmail.com>
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

from contracts import contract, new_contract
from lxml import html
from lxml.etree import XMLSyntaxError
from lxml.html import HtmlElement
from requests import Response

new_contract('HtmlElement', HtmlElement)
new_contract('Response', Response)


class ScrapperMixin(object):

    @contract
    def parse_html(self, response):
        """
        :type response: Response
        :rtype: HtmlElement
        """

        try:
            return html.fromstring(response.text)
        except XMLSyntaxError as e:
            print(e)
            print(response.text)
            raise e
