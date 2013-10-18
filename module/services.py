import os
import logging
import random
import pickle

rand_data = []
try:
    f = open('randlist.dat', 'r')
    rand_data = pickle.load(f.read())
    f.close()
except:
    rand_data = range(1000)
    random.shuffle(rand_data)

class OutOfIDException(Exception):
    pass

class RandID(object):
    def __init__(self):
        pass

    def new_id(self):
        global rand_data
        if rand_data:
            newid = rand_data.pop()
            return newid
        else:
            raise OutOfIDException

randId = RandID()

