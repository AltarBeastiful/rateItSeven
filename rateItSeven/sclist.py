#   === This file is part of RateItSeven ===
#
#   Copyright 2015, Rémi Benoit <r3m1.benoit@gmail.com>
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

from enum import Enum

class ArtType(Enum):
    default = 1
    film = 2

class SCList(object):
    '''
    classdocs
    '''


    def __init__(self, listId = None, title = None):
        '''
        Constructor
        '''
        self._id = listId
        self._type = None
        self._title = title
        self._description = ""

    def isValid(self):
        try:
            int(self._id)
            return True
        except:
            return False

    def id(self):
        return self._id

    def title(self):
        return self._title

    def url(self):
        if self.isValid() and self.title() is not None:
            return "http://www.senscritique.com/liste/" + self.title().replace(' ', '_') + "/" + self.id()
        else:
            return None

    def setTitle(self, title):
        self._title = title

    def type(self):
        return self._type

    def setType(self, type : ArtType):
        self._type = type

    def description(self):
        return self._description

    def setDescription(self, descr):
        self._description = descr
