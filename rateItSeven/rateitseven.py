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

from rateItSeven.movie import Movie
from rateItSeven.scan.moviestore import MovieStore
from rateItSeven.sclist import SCList
from rateItSeven.senscritique import SensCritique


class RateItSeven(object):

    def __init__(self, login, password, search_path, store_file_path):
        self._search_paths = search_path
        self._store_file_path = store_file_path

        self._sc = SensCritique(login, password)

        self._list = SCList()
        self._list.setTitle("La clef")

    def start(self):
        self._sc.sign_in()

        self._list = self._sc.retrieveListByTitle(self._list.title())
        if not self._list.isValid():
            self._sc.createList(self._list)

        store = MovieStore(self._store_file_path, self._search_paths)
        changes = store.pull_changes()

        for guess in changes.added:
            self._sc.addMovie(Movie(guess.get("title"), guess.abs_path), self._list)

        store.persist_scanned_changes()


if __name__ == '__main__':
    daemon = RateItSeven("legalizme@gmail.com", "12345")
    daemon.start()


