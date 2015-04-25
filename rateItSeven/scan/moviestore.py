import json

from rateItSeven.scan.moviescan import MovieScanner

class MovieStore(object):
    '''
    Store movies metadata in file
    '''

    def __init__(self, store_file_path : str, movies_dirs : list):
        self.store_file = open(store_file_path, 'a')
        self.scanner = MovieScanner(movies_dirs)

    def __enter__(self):
        return self

    def __exit__(self, thetype, value, traceback):
        self.store_file.close()

    def persist(self):
        self.store_file.write(json.dumps(list(self.scanner.list_movies()), default=lambda o: o.__dict__))

