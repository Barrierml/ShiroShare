import threading,socket,time,select,json
from queue import Queue
HEAD = b"Shiro"
RecvSocketPort = 6543
HHH = {"name":"sadas","sex":"man"}

# 发送数据格式
# 前5个字节是固定的
# Shiro
# 随后4个字节表明类型
# HALO      FILE     BEAT   CHEN     LIST        ACKN
# 表明身份   文件传输   心跳   更改文件   传输文件列表   确认
#
#
class NetMessage(threading.Thread):
    """发送信息，接收信息的进程"""
    def __init__(self,Q,Port=RecvSocketPort):
        super(NetMessage,self).__init__()
        # 接收广播
        self.RecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.RecvSocket.bind(("",Port))
        # 可读列表
        self.ReadableList = [self.RecvSocket]
        # 发给主进程的通信queue
        self.SQueue = Q
        # 发送的端口
        self.Send = SendMessage()
        # 要操作的数据库
        self.sql = None
    def GetJson(self,data:bytes):
        try:
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            print(e)
            return False
    def run(self):
        try:
            _method_map = {"HALO": self.on_HALO,
                           "FILE": self.on_FILE,
                           "BEAT": self.on_BEAT,
                           "CHEN": self.on_CHEN,
                           "LIST": self.on_LIST,
                           "ACKN": self.on_ACKN}
            while True:
            # 堵塞接收
                r,w,e = select.select(self.ReadableList,[],self.ReadableList,1)
                for con in r:
                    data,addr = con.recvfrom(4096)
                    # 前5个字符不是固定就退出
                    if data[0:5] != HEAD:
                        continue
                    type = data[5:9]
                    # type不在支持列表内也退出
                    if type not in _method_map:
                        continue
                    data = self.GetJson(data[9:])
                    _method_map[type](data,addr)
        except Exception as e:
            print(e)
            self.close()
    def on_HALO(self,data,addr):
        pass
    def on_FILE(self,data,addr):
        pass
    def on_BEAT(self,data,addr):
        pass
    def on_CHEN(self,data,addr):
        pass
    def on_LIST(self,data,addr):
        pass
    def on_ACKN(self,data,addr):
        pass
    def close(self):
        self.RecvSocket.close()
class SendMessage():
    """主要是用来发送或者广播消息
        经过查询资料，发现发送udp包不会阻塞,就不需要再开进程了
    """
    def __init__(self):
        # 设置广播，还有发送信息的嵌套字
        self.SendSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    def Broadcast(self,type:str,data:object):
        # 发送广播
        bag = HEAD + type.encode("utf-8") + json.dumps(data).encode("utf-8")
        return self.SendSocket.sendto(bag,('<broadcast>',RecvSocketPort))
    def SendTo(self,ip,type:str,data:object):
        # 定向传输
        bag = HEAD + type.encode("utf-8") + json.dumps(data).encode("utf-8")
        return self.SendSocket.sendto(bag, (ip, RecvSocketPort))

if __name__ == '__main__':
    RecvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    RecvSocket.bind(("", RecvSocketPort))
    r,w,e = select.select([RecvSocket],[],[],5)
    if r == []:
        print("gg")
    else:
        print(r[0].recvfrom(4096))