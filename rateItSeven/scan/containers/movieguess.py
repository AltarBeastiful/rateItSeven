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
from guessit import Guess


class MovieGuess(object):
    '''
    Data struct for guessed data on a movie
    '''

    def __init__(self, guess: Guess, abs_path):
        '''
        :param guess: a Guess object containing movie infos
        :param abs_path: the full path of the movie file
        '''
        self.guess = guess
        self.abs_path = abs_path

    def __key(self):
        return (self.abs_path)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__key())

    def nice_string(self):
        return self.abs_path + '\n' + self.guess.nice_string()

    def get(self, key):
        return self.guess.get(key)

    def is_movie(self):
        mimetype = self.guess.get("mimetype")
        videotype = self.guess.get("type")
        return videotype and videotype  == "movie" and mimetype and "video" in mimetype

