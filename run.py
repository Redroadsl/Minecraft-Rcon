from rcon import MCRcon as rcon
import os
if not os.isfile("./inf"):
    print('输入IP')
    ip=input()
    print('输入端口')
    port=int(input())
    print('rcon密码')
    pw=input()
    print('\n\n',"确认你的信息\n",'IP:',ip,'\n端口:',str(port),'\n密码:',pw)
    input('Enter')
    with open("./inf",'w+') as file:
        file.write(ip)
