'''
## launchio.json
JSON module for Launcher

json : JSON class
'''

from launchio import ln
import json as json_legacy

class JSON:
    def __init__(self, file:ln):
        self.file = file
        self.json_dict:dict = json_legacy.load(file.open())

    def __call__(self): # read
        return self.json_dict

    def dump(self, json_dict):
        with self.file.open('w') as res:
            json_legacy.dump(json_dict, res, indent=2)

    def edit(self, *key:str, value):
        tmp = self.json_dict
        prev = {}

        if key[0] not in self.json_dict.keys():
            tmp[key[0]] = {}

        for i in key[:-1]:
            if i not in tmp.keys():
                prev[i] = {}
            tmp = tmp[i]
            prev = tmp

        tmp[key[-1]] = value

        with self.file.open('w') as res:
            json_legacy.dump(self.json_dict, res, indent=2)

    def append(self, *key:str, value):
        tmp = self.json_dict
        prev = {}

        if key[0] not in self.json_dict.keys():
            tmp[key[0]] = {}

        for i in key[:-1]:
            if i not in tmp.keys():
                prev[i] = {}
            tmp = tmp[i]
            prev = tmp

        if key[-1] not in tmp.keys():
            tmp[key[-1]] = []

        tmp[key[-1]].append(value)

        with self.file.open('w') as res:
            json_legacy.dump(self.json_dict, res, indent=2)

    def remove(self, *key:str, value):
        tmp = self.json_dict

        if key[0] not in self.json_dict.keys():
            return

        for i in key[:-1]:
            if i not in tmp.keys():
                return
            tmp = tmp[i]

        if key[-1] not in tmp.keys():
            return

        tmp[key[-1]].remove(value)

        with self.file.open('w') as res:
            json_legacy.dump(self.json_dict, res, indent=2)