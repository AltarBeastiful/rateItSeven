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
from synthetic import synthesize_constructor
from synthetic import synthesize_equality
from synthetic import synthesize_property

from rateItSeven.lib.dict_object_mixin import DictObjectMixin


@synthesize_constructor()
@synthesize_equality()
@synthesize_property('path', contract='string')
@synthesize_property('guess')
class Piece(DictObjectMixin):

    # For IDE integration
    def __init__(self):
        pass

    def is_movie(self):
        mime_type = self.guess.get('mimetype', "")
        piece_type = self.guess.get('type', "")

        return "video" in mime_type and "movie" in piece_type

    def to_dict(self):
        return {
            'path': self.path,
            'guess': self.guess,
        }

    @staticmethod
    def from_dict(dict_object):
        return Piece(
            path=dict_object['path'],
            guess=dict_object['guess'],
        )
