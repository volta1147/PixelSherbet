from lib.file import json_path
from launchio.json import PMjson

users_file = PMjson(json_path.chifile('users.json'))

output_dict = {}

for i in users_file.read().keys():
    output_dict[i] = {'users':[]}
    for j in users_file.read()[i]['users']:
        output_dict[i]['users'].append({})
        for k in ['id', 'nick', 'chats', 'min', 'last']:
            output_dict[i]['users'][-1][k] = j[k]

users_file.dump(output_dict)