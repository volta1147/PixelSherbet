'''
search
'''

from launchio import lndir

while True:
    asdf = True
    mlst = []
    keyw = input('검색어를 입력하세요. : ')
    if keyw == 'quit':
        break
    fles = lndir('community', 'memo').listdir()
    print(f"\n======{keyw}======")
    for i in fles:
        if keyw in i:
            asdf = False
            mlst.append(i)
    if asdf:
        print("검색 결과가 없습니다!")
    else:
        mlst.sort()
        print("\n".join(mlst))
    print("="*10)
    print()
