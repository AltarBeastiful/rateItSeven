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

class MovieStoreState(object):
    '''
    Hold the state of the movie store in the form of three sets of MovieGuess
    '''

    def __init__(self, added, existing, deleted):
        '''
        :param added: set of movies added since last check
        :param existing: set of movies still existing since last check
        :param deleted: set of movies that don't exist anymore
        '''
        self.added = added
        self.existing = existing
        self.deleted = deleted

