import socket
import ssl
import select
import struct
import time
#导入模块

class MCRconException(Exception):
    pass


class MCRcon(object):	
    """Minecraft服务端远程命令（RCON）模板

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
    """
    socket = None

	#重写init方法
    def __init__(self, host, password, port, tlsmode=0):
        self.host = host
        self.password = password
        self.port = port
        self.tlsmode = tlsmode

    def __exit__(self, type, value, tb):
        self.disconnect()
		
    def __enter__(self):
        self.connect()
        return self

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 打开 TLS
        if self.tlsmode > 0:
            ctx = ssl.create_default_context()

            # 禁用主机名和证书验证
            if self.tlsmode > 1:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.host)

        self.socket.connect((self.host, self.port))
        self._send(3, self.password)



    def _read(self, length):
        data = b""
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return data
		
    def disconnect(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
			
    def _send(self, out_type, out_data):
        if self.socket is None:
            raise MCRconException("发送前必须连接！")

        # 发送请求包
        out_payload = struct.pack('<ii', 0, out_type) + out_data.encode('utf8') + b'\x00\x00'
        out_length = struct.pack('<i', len(out_payload))
        self.socket.send(out_length + out_payload)

        # 读取响应包
        in_data = ""
        while True:
            # 读取数据包
            in_length, = struct.unpack('<i', self._read(4))
            in_payload = self._read(in_length)
            in_id, in_type = struct.unpack('<ii', in_payload[:8])
            in_data_partial, in_padding = in_payload[8:-2], in_payload[-2:]

            # 异常处理
            if in_padding != b'\x00\x00':
                raise MCRconException("Incorrect padding")
            if in_id == -1:
                raise MCRconException("登录rcon协议失败")

            
            in_data += in_data_partial.decode('utf8')


            if len(select.select([self.socket], [], [], 0)[0]) == 0:
                return in_data

    def command(self, command):
        result = self._send(2, command)
        time.sleep(0.003) # MC-72390 （非线程安全的解决办法）
        return result
