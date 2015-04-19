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

import guessit

from rateItSeven.scan.containers.movie import MovieGuess
from rateItSeven.scan.filescanner import FileScanner

def list_movies(dir_paths):
    fileScanner = FileScanner(dir_paths)
    for abs_path in fileScanner.absolute_file_paths():
        movie = MovieGuess(guessit.guess_file_info(abs_path, info=['video', 'filename']), abs_path)
        if movie.is_movie():
            yield movie