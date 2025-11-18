from launchio import ln, lndir
import json as json_legacy

json_path = lndir('res', 'json')
community_path = lndir('community')

def ismemo(filename: str, cmd='memo'):
    name = ln("community", cmd, filename, form="txt")
    return name.isfile()

def openfile(cmd: str, filename: str, newfile=False):
    name = ln("community", cmd, filename, form="txt") # cmd+os.path.sep+filename+".txt"
    if name.isfile(): # os.path.isfile(name):
        return name.read()
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
    a = json_legacy.load(ln("community", "chats", form="json").open())
    if id not in [i['id'] for i in a[str(guildid)]['users']]:
        return 0
    else:
        for i in a[str(guildid)]['users']:
            if i['id'] == id:
                return i['chats']

def memo_footer(tp: str, name: str):
    return tp + " - " + name