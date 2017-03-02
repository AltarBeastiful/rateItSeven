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

from synthetic import synthesize_constructor
from synthetic import synthesize_equality
from synthetic import synthesize_property


class ProductType(Enum):
    MOVIE = "film"
    SERIE = "serie"
    ALBUM = "album"
    BOOK = "livre"


@synthesize_constructor()
@synthesize_equality()
@synthesize_property('type', contract=ProductType)
@synthesize_property('title', contract=str)
@synthesize_property('id', contract=str)
class Product(object):

    def __init__(self):
        pass
