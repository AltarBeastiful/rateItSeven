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
from synthetic import synthesize_property
from tinydb import JSONStorage
from tinydb import TinyDB, Query
from contracts import new_contract

from rateItSeven.scan.piece import Piece

new_contract('Piece', Piece)


@synthesize_constructor()
@synthesize_property('path', contract='string')
class LocalCollectionStore(object):

    def __init__(self):
        if TinyDB.DEFAULT_STORAGE == JSONStorage:
            self._db = TinyDB(path=self.path)
        else:
            self._db = TinyDB()

    def add(self, piece):
        """
        :param Piece piece:
        :return:
        """
        self._db.insert(piece.to_dict())

    def piece_list(self):
        """
        :rtype: list(Piece)
        """

        return [Piece.from_dict(piece_dict) for piece_dict in self._db.all()]

