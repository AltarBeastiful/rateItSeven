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
from enum import Enum

from contracts import new_contract, contract
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.senscritique.domain.product import Product

new_contract('Product', Product)


class ListType(Enum):
    MOVIE = ("1", "films")
    SERIE = ("4", "series")


@synthesize_constructor()
@synthesize_property('id', contract='string')
@synthesize_property('list_id', contract='string')
@synthesize_property('description', contract='string')
@synthesize_property('product', contract='Product|None')
class ListItem(object):

    def __init__(self):
        pass


@synthesize_constructor()
@synthesize_property('type', contract=ListType)
@synthesize_property('name', contract='string')
@synthesize_property('path', contract='string')
class ScList(object):

    # Defined for integration with IDE
    def __init__(self):
        pass

    def compute_list_id(self):
        #SC list path is of the form "liste/formattedName/id
        splitted_path = self.path.split("/")
        return splitted_path[-1]

    @contract
    def page_url(self, index):
        """
        Return the url of the list page.
        :type index: int
        :rtype: string
        """

        return "/sc2/liste/{list_id}/page-{page_index}.ajax".format(list_id=self.compute_list_id(),
                                                                    page_index=index)
