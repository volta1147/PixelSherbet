from launchio import ln

token   = ""
myid    = ""
prefix  = ""
myname  = ""
version = ""

helpdoc = ln('res', 'help', form='md')

def varset(): # 변수 설정
    global token
    global myid
    global prefix
    global myname
    global version

    token   = ln("res", "security", "token.txt") .read()
    myid    = ln("res", "security", "myid.txt")  .read()
    prefix  = ln("res",             "prefix.txt").read()
    myname  = ln("res",             "myname.txt").read()
    version = ln("res",             "version")   .read()