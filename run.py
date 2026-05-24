from rcon import MCRcon as MCR
import configparser
import os

ip = ''
port = 0
pw = ''

config = configparser.ConfigParser()

def ask_for_config():
    '询问用户连接信息并覆盖储存在配置文件'
    with open("./mcrcon.ini",'w') as file:
        config['RCON'] = {}
        config['RCON']['ip']=ip=input('输入IP（无端口）: ')
        config['RCON']['port']=port=input('输入端口: ')
        config['RCON']['password']=pw=input('rcon密码:\n')
        print('确认保存你的信息:\nIP:{}\n端口:{}\n密码:{}'.format(ip, port, pw))
        input('Enter')
        try:
            config.write(file)
        except Exception as err:
            print('档案储存出现错误:',err,'\n')
        else:
            print('档案储存成功: ./mcrcon.ini')


if os.path.exists('./mcrcon.ini'):
    try:
        config.read('./mcrcon.ini')
        ip=config['RCON']['ip']
        port=config['RCON']['port']
        pw=config['RCON']['password']
    except:
        print('配置文件有误，重新创建')
        ask_for_config()
        config.read('./mcrcon.ini')
        ip=config['RCON']['ip']
        port=config['RCON']['port']
        pw=config['RCON']['password']
else:
    ask_for_config()


while True:
    try:
        print('正在连接 {}:{}'.format(ip,port))
        mcr = MCR(ip, pw, int(port))
        mcr.connect()
        while True:
            print(mcr.command(input('{}:{}>'.format(ip,port))))
    except ConnectionRefusedError as err:
        print('连接错误:',err)
    except KeyboardInterrupt:
        print('连接关闭')
        mcr.disconnect()
        break
    




        
