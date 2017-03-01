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
from synthetic import synthesize_constructor
from synthetic import synthesize_property

from rateItSeven.legacysenscritique import LegacySensCritique
from rateItSeven.movie import Movie
from rateItSeven.scan.moviestore import MovieStore
from rateItSeven.senscritique.domain.sc_list import ListType
from rateItSeven.senscritique.sc_api import AuthService, ListService


@synthesize_property('login', contract=str)
@synthesize_property('password', contract=str)
@synthesize_property('search_paths', contract=list)
@synthesize_property('store_file_path', contract=str)
@synthesize_property('legacy_mode', contract=bool, default=True)
@synthesize_constructor()
class RateItSeven(object):
    # TODO: Lists titles should be configurable by the user
    _LISTS_LIB = {ListType.MOVIE: "La clef",
                  ListType.SERIE: "zodes"}

    def __init__(self):
        self._lists = {}

    def start(self):
        if self._legacy_mode:
            self._start_legacy()
        else:
            self._start()

    def _start_legacy(self):
        sc = LegacySensCritique(self.login, self.password)
        sc.sign_in()
        for video_type, title in self._LISTS_LIB.items():
            current_list = sc.retrieveListByTitle(title)
            if not current_list.isValid():
                sc.createList(current_list)
            self._lists[video_type] = current_list

        with MovieStore(self._store_file_path, self._search_paths) as store:
            changes = store.pull_changes()

            for video_type in RateItSeven._LISTS_LIB.keys():
                for guess in changes[video_type].added:
                    sc.addMovie(Movie(guess.get("title"), guess.abs_path), self._lists[video_type])

            store.persist_scanned_changes()

    def _start(self):
        user = AuthService().do_login(email=self.login, password=self.password)
        listsrv = ListService(user)
        for video_type, title in self._LISTS_LIB.items():
            [current_list] = listsrv.find_list(title=title, list_type=video_type)
            if not current_list:
                current_list = listsrv.create_list(name=title, list_type=video_type)
            self._lists[video_type] = current_list

        with MovieStore(self._store_file_path, self._search_paths) as store:
            changes = store.pull_changes()

            for video_type in RateItSeven._LISTS_LIB.keys():
                list_id = self._lists[video_type].compute_list_id()
                for guess in changes[video_type].added:
                    # TODO find movie/serie product_id then add it to the list (see ListSrv.add_movie)
                    pass

            store.persist_scanned_changes()


if __name__ == '__main__':
    daemon = RateItSeven("legalizme@gmail.com", "12345")
    daemon.start()
