from launchio import ln, lndir, sep
import lib.file as file
import os

class Output:
    def __init__(self):
        self.output = ''

    def __str__(self):
        return self.output

    def append(self, text:str):
        self.output += str(text)

    def addline(self, text:str=''):
        self.output += str(text)
        self.output += '\n'

    def tab(self):
        self.output += '\t'

class FileSetting:
    def __init__(self, file:ln):
        self.file = file
    
    def fileUI(self):
        if self.file.name.count('.') > 0:
            if self.file.name.split('.')[-2:] == 'tar.gz':
                form = 'tar.gz'
            else:
                form = self.file.name.split('.')[-1]
        else:
            form = ''

        output = Output()

        output.append('File name : ')
        output.addline(self.file.name)
        output.addline()

        output.append('Format')
        output.addline('None' if form == '' else form)
        output.addline()

        output.addline('='*20)
        
        output.addline('O | Open file')

        output.addline()

        output.addline('E | Edit file')
        output.addline('R | Rename file')
        output.addline('D | Delete file')
        # output.addline('M | Replace file')
        # output.addline('C | Copy file')
        # output.addline('X | Cut file')

        output.addline()

        output.addline('Q | Quit')

        return str(output)

    def fileSetting(self):
        response = ''

        quit_code = ['q']
        action_code = ['o', 'e', 'r', 'd', 'q']

        while response not in action_code:
            os.system('clear')
            print(self.directory())
            print('='*20)
            response = input('>>>')[0].lower()


class FileExplorer:
    def __init__(self, home:str):
        self.dir = lndir(home)

    def directory(self):
        listdir = self.dir.listdir()
        folders = []
        files = []
        
        for i in listdir:
            if self.dir.chidir(i).isdir():
                folders.append(i)
            else:
                files.append(i)

        output = Output()

        if len(folders) > 0:
            output.addline('Folders')
            output.append('\t'.join(folders))
    
            if len(files) > 0:
                output.addline()
                output.addline()

        if len(files) > 0:
            output.addline('Files')
            output.append('\t'.join(files))

        return str(output)

    def fileExplorer(self):
        response = ''

        quit_code = ['quit', 'exit']

        while response not in quit_code:
            os.system('clear')
            print(self.directory())
            print('='*20)
            response = input('>>>')
            if self.dir.chidir(response).isdir():
                self.dir = self.dir.chidir(response)
            elif self.dir.chifile(response).isfile():
                fileinfo = FileSetting(self.dir.chifile(response))
                fileinfo.fileSetting()

def run(response):
    if response == 'community':
        pass

os.system('clear')

response = ''

aa = FileExplorer('community')
aa.fileExplorer()
# while True:
#     response = input('>>>')
#     
#     run(response)