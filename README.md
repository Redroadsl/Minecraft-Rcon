# Minecraft-Rcon
轻量级Minecraft服务端rcon连接器。

Minecraft服务端远程命令（RCON）模板
	老咩友情提醒您：
		道路千万条，
		规范第一条。
		写码不规范，
		维护两行泪。
    
    推荐你使用python的'with'语句！
    这样可以确保及时的关闭连接，而不是被遗漏。
    'with'语句例子:
    In [1]: from mcrcon import MCRcon
    In [2]: with MCRcon("这是一个ip", "这是rcon的密码","这是Rcon的端口" ) as mcr:
       ...:     resp = mcr.command("/发送给服务端的指令")
       ...:     print(resp) #输出
	
	  两行泪方式:
	  你当然也可以不用python的'with'语句，但是一定要在建立连接后，及时的断开连接。
    In [3]: mcr = MCRcon("这是一个ip", "这是rcon的密码","这是Rcon的端口" )
    In [4]: mcr.connect() #连接建立
    In [5]: resp = mcr.command("/发送给服务端的指令")
    In [6]: print(resp) #输出
    In [7]: mcr.disconnect() #断开连接
