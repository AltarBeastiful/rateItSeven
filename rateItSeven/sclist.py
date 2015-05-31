'''
Created on Apr 19, 2015

@author: remi
'''
from enum import Enum

class ArtType(Enum):
    default = 1
    film = 2

class SCList(object):
    '''
    classdocs
    '''


    def __init__(self, listId=""):
        '''
        Constructor
        '''
        self._id = listId
        self._type = None
        self._title = None
        self._description = None

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
