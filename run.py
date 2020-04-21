from rcon import MCRcon as rcon
import os
if not os.isfile("./inf"):
    with open("./inf",'w+') as file:
        print('输入IP')
        ip=input()
        print('输入端口')
        port=int(input())
        print('rcon密码')
        pw=input()
        print('\n\n',"确认你的信息\n",'IP:',ip,'\n端口:',str(port),'\n密码:',pw)
        input('Enter')
        try:
            file.write(ip+' '+str(port)+' '+pw)
        except Exception as err:
            print('\n档案储存出现错误:',err,'\n')
        else:
            print('档案储存成功',os.filepath("./inf")
        finally:
            
