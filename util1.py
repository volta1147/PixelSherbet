'''
server id setting
'''

import launchio.json
from lib.file import json_path

user_file = launchio.json.JSON(json_path.chifile('users.json'))
server_file = launchio.json.JSON(json_path.chifile('servers.json'))

for i in server_file().keys():
    user_file.edit(i, "users", value=[])