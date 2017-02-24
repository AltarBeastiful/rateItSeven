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
from rateItSeven.legacysenscritique import LegacySensCritique
from rateItSeven.movie import Movie
from rateItSeven.scan.moviestore import MovieStore

class RateItSeven(object):

    # TODO: Lists titles should be configurable by the user
    _LISTS_LIB = {"movies" : "La clef",
                  "episodes" : "zodes"}

    def __init__(self, login, password, search_path, store_file_path):
        self._search_paths = search_path
        self._store_file_path = store_file_path

        self._sc = LegacySensCritique(login, password)
        self._lists = {}
    def start(self):
        self._sc.sign_in()

        for video_type,title in self._LISTS_LIB.items():
            current_list = self._sc.retrieveListByTitle(title)
            if not current_list.isValid():
                self._sc.createList(current_list)
            self._lists[video_type] = current_list

        with MovieStore(self._store_file_path, self._search_paths) as store:
            changes = store.pull_changes()

            for video_type in RateItSeven._LISTS_LIB.keys():
                for guess in changes[video_type].added:
                    self._sc.addMovie(Movie(guess.get("title"), guess.abs_path), self._lists[video_type])

            store.persist_scanned_changes()


if __name__ == '__main__':
    daemon = RateItSeven("legalizme@gmail.com", "12345")
    daemon.start()


