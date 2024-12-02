from launchio import ln, lndir
from typing import Literal
import json

def ismemo(filename: str):
    name = ln("community", "memo", filename, form="txt")
    return name.isfile()

def openfile(cmd: str, filename: str, newfile=False):
    name = ln("community", cmd, filename, form="txt") # cmd+os.path.sep+filename+".txt"
    if name.isfile(): # os.path.isfile(name):
        return name.read() # with open(name, "r", encoding="utf8") as file:
        #     return file.read()
    else:
        if newfile:
            name.write()
        return ''

def editfile(cmd: str, filename: str, memo: str):
    name = ln("community", cmd, filename, form="txt")
    name.write(memo, 'w')   

def appendfile(cmd: str, filename: str, memo: str):
    name = ln("community", cmd, filename, form="txt")
    name.write(memo, 'a')

def delfile(cmd: str, filename: str):
    name = ln("community", cmd, filename, form="txt")
    if name.isfile():
        name.remove()

def listsplit(cmd: str, filename: str):
    name = ln("community", cmd, filename, form="txt")
    return name.readlines()

def userlvl(id:int, guildid:int):
    a = json.load(ln("community", "chats", form="json").open())
    if id not in [i['id'] for i in a[str(guildid)]['users']]:
        return 0
    else:
        for i in a[str(guildid)]['users']:
            if i['id'] == id:
                return i['chats']

def rev(folder: str, filename: str, memo: str, mode:Literal['w', 'a']='w'):
    dr = lndir("community", folder, filename)# folder+os.path.sep+filename
    revf = ln("res", "tmp")
    revv = 0
    if not dr.isdir():
        dr.makedirs()
    else:
        revv = int(dr.chifile("rev.txt").read())
        revf.write(dr.chifile(f"rev{revv}.txt").read())
        revv += 1
    
    revf.write('\n'+memo, mode=mode)

    dr.chifile("rev.txt").write(str(revv))
    dr.chifile(f"rev{revv}.txt").write(revf.read())

def isrev(folder: str, filename: str, ver):
    return ln("community", folder, filename, f"rev{ver}.txt").isfile()

def openrev(folder: str, filename: str, ver):
    return ln("community", folder, filename, f"rev{ver}.txt").read()

def getver(folder: str, filename: str):
    return ln("community", folder, filename, "rev.txt").read()

def memover(tp: str, name: str, rev):
    return tp + " - " + name + f"(rev {rev})"

def edit_json(name:str, key:str, value):
    resf = json.load(ln('res', 'json', name, form='json').open())
    resf[key] = value
    with ln('res', 'json', name, form='json').open('w') as res:
        json.dump(resf, res, indent=2)

def append_json(name:str, key:str, value):
    resf:dict = json.load(ln('res', 'json', name, form='json').open())
    if key not in resf.keys():
        resf[key] = []
    resf[key].append(value)
    with ln('res', 'json', name, form='json').open('w') as res:
        json.dump(resf, res, indent=2)

def dict_json(name:str, key:str, valkey:str, value):
    resf:dict = json.load(ln('res', 'json', name, form='json').open())
    if key not in resf.keys():
        resf[key] = {}
    resf[key][valkey] = value
    with ln('res', 'json', name, form='json').open('w') as res:
        json.dump(resf, res, indent=2)

def read_json(name:str):
    return json.load(ln('res', 'json', name, form='json').open())