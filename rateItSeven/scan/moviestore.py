#   === This file is part of RateItSeven ===
#
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
import os

from rateItSeven.scan.moviescanner import MovieScanner

class MovieStore(object):
    '''
    Store movies metadata in file
    '''

    def __init__(self, store_file_path : str, movies_dirs : list):
        self.store_file = open(store_file_path, 'a+')
        self.scanner = MovieScanner(movies_dirs)

    def __enter__(self):
        return self

    def __exit__(self, thetype, value, traceback):
        self.store_file.close()

    def persist_scanned_changes(self):
        '''
        Persist all movies found at movies_dirs to the store file
        '''
        scanned_movies = list(self.scanner.list_movies())
        self.store_file.write(json.dumps(scanned_movies, default=lambda o: o.__dict__))
        self.store_file.flush()


