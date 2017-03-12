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
import pickle

import jsonpickle as jsonpickle
from synthetic import synthesize_constructor
from synthetic import synthesize_property
from tinydb import JSONStorage
from tinydb import TinyDB, Query
from contracts import new_contract, contract

from rateItSeven.scan.piece import Piece
from rateItSeven.scan.polling_observer_with_state import WatchState

new_contract('Piece', Piece)
new_contract('WatchState', WatchState)


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
        self._piece_table().insert(piece.to_dict())

    def piece_list(self):
        """
        :rtype: list(Piece)
        """

        return [Piece.from_dict(piece_dict) for piece_dict in self._piece_table().all()]

    @contract
    def state_list(self):
        """
        :rtype: list(WatchState)
        """
        state_entry_list = self._state_table().all()
        if not state_entry_list:
            return []

        return jsonpickle.loads(state_entry_list[0]['pickle'])

    def set_state_list(self, state_list):
        """
        :type state_list: list(WatchState)
        """
        state_table = self._state_table()
        state_table.purge()
        self._state_table().insert({'pickle': jsonpickle.dumps(state_list)})

    def _piece_table(self):
        return self._db.table("piece")

    def _state_table(self):
        return self._db.table("state")

    def _state_entry(self):
        Entry = Query()
        entry_search_list = self._state_table().search(Entry.name == "state_list")
        if entry_search_list:
            return entry_search_list[0]

