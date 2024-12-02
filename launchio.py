'''
## launchio
File input/output module for Launcher

ln : file class
lndir : directory class
'''

import os
import sys
from typing import Literal

sep = os.path.sep

pathname = sep.join(__file__.split(sep)[:-1])+sep

class ln:
    def __init__(self, *paths, form = ""):
        if len(form) == 0:
            self.path = pathname + sep.join(paths)
        else:
            self.path = pathname + sep.join(paths) + "." + form

    def __str__(self):
        return self.path

    def isfile(self):
        return os.path.isfile(self.path)
    
    def open(self, mode:Literal['r', 'w', 'a']='r', encoding="utf8"):
        return open(self.path, mode, encoding=encoding)
    
    def read(self):
        readfile = self.open()
        cont = readfile.read()
        readfile.close()
        return cont
    
    def readlines(self):
        readfile = self.open()
        cont = readfile.readlines()
        readfile.close()
        return cont

    def write(self, cont='', mode:Literal['w', 'a']='w'):
        editfile = self.open(mode)
        editfile.write(cont)
        editfile.close()

    def remove(self):
        os.remove(self.path)
    
class lndir:
    def __init__(self, *paths):
        self.path = pathname + sep.join(paths)

    def __str__(self):
        return self.path
    
    def isdir(self):
        return os.path.isdir(self.path)
    
    def makedirs(self):
        os.makedirs(self.path, exist_ok=True)

    def removedirs(self):
        os.removedirs(self.path)

    def pardir(self):
        pard = lndir()
        pard.path = sep.join(self.path.split(sep)[:-1])
        return pard
    
    def chidir(self, name):
        chid = lndir()
        chid.path = self.path+sep+name
        return chid
    
    def chifile(self, *paths, form = ""):
        chfl = ln()
        if len(form) == 0:
            chfl.path = self.path + os.path.sep + os.path.sep.join(paths)
        else:
            chfl.path = self.path + os.path.sep + os.path.sep.join(paths) + "." + form
        print(chfl)
        return chfl
    
    def listdir(self):
        return os.listdir(self.path)

def setpath():
    sys.path.append(pathname[:-1])