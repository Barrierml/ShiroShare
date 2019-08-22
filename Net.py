from PyQt5.QtCore import QThread,pyqtSignal
import socket,time,select,json,math
from queue import Queue
import mysql
HEAD = b"Shiro"
RecvSocketPort = 6543

# 发送数据格式
# 前5个字节是固定的
# Shiro
# 随后4个字节表明类型
# HALO      FILE     BEAT   CHEN     LIST        ACKN
# 表明身份   文件传输   心跳   更改文件   传输文件列表   确认
#
#
class ShiroNet(QThread):
    """发送信息，接收信息的进程,使用信号驱动"""
    # 初始化完毕的信号
    InitFinsh = pyqtSignal()
    LoadBar = pyqtSignal(str)
    def __init__(self,data,Port=RecvSocketPort):
        super(ShiroNet,self).__init__()
        # 接收广播
        self.RecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.RecvSocket.bind(("",Port))
        # 可读列表
        self.ReadableList = [self.RecvSocket]
        # 自己的数据
        self.data = data
        # 要操作的数据库
        self.sql = mysql.ShiroSQL()
        # 发送
        self.Send = SendMessage(self.data.get("id"))

    def GetJson(self,data:bytes):
        try:
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            print(e)
            return False
    def SayHello(self):
        # 向局域网内广播自己
        self.LoadBar.emit("局域网广播中")
        self.Send.Broadcast("HALO", data=self.data)
        # 发送信号初始化完毕

    def run(self):
        self.SayHello()
        self.InitFinsh.emit()
        _method_map = {b"HALO": self.on_HALO,
                       b"FILE": self.on_FILE,
                       b"BEAT": self.on_BEAT,
                       b"CHEN": self.on_CHEN,
                       b"LIST": self.on_LIST,
                       b"ACKN": self.on_ACKN,
                       b"USER": self.on_USER, }
        while True:
            # 堵塞接收
            try:
                r, w, e = select.select(self.ReadableList, [], self.ReadableList)
                for con in r:
                    data, addr = con.recvfrom(8192)
                    # 前5个字符不是固定就退出
                    if data[0:5] != HEAD:
                        continue
                    type = data[5:9]
                    user = data[9:19]
                    # type不在支持列表内也退出
                    if type not in _method_map:
                        continue
                    data = self.GetJson(data[19:])
                    _method_map[type](data, addr)
            except Exception as e:
                print(e)
                continue
    def on_HALO(self,data,addr):
        # 收到别人的用户信息,返回一个自己的用户信息
        if not self.sql.InUsers(data.get("id")):
            # 新成员加入
            self.sql.AddUser(data.get("id"),data.get("name"),addr[0])
            # 向他发送打招呼信息
            self.Send.SendTo(addr[0],"HALO",self.data)
            # 向他发送本机文件列表
            self.Send.SendTo(addr[0],"LIST",self.data)
        else:
            self.sql.ChangeUser(data.get("id"),name=data.get("name"),ip=addr[0])
    def on_USER(self,data,addr):
        # 修改用户信息
        if self.sql.InUsers(data["id"]):
            self.sql.ChangeUser(data.get("id"),data.get("name"),addr[0])
    def on_LIST(self,data,addr):
        # 收到文件列表,加入数据库
        def g(o):
            # 这只是为了简化查询
            data.get(o)
        # 先判断文件夹是否存在
        if self.sql.InDirs(g("DirId")):
            return
        else:
            self.sql.AddDir(g("DirId"),g())
    def on_FILE(self,data,addr):
        pass
    def on_BEAT(self,data,addr):
        pass
    def on_CHEN(self,data,addr):
        pass
    def on_ACKN(self,data,addr):
        pass
    def Send_LIST(self,dd:dict):
        # 向局域网所有人发送自身的分享列表
        print(dd)
    def close(self):
        self.RecvSocket.close()
class SendMessage():
    """主要是用来发送或者广播消息
        经过查询资料，发现发送udp包不会阻塞,就不需要再开进程了
    """
    def __init__(self,id:str):
        # 设置广播，还有发送信息的嵌套字
        self.SendSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.id = id
    def Broadcast(self,type:str,data:object):
        # 发送广播
        bag = HEAD + self.id.encode("utf-8") + type.encode("utf-8") + json.dumps(data).encode("utf-8")
        return self.SendSocket.sendto(bag,('<broadcast>',RecvSocketPort))
    def SendTo(self,ip,type:str,data:object):
        # 定向传输
        bag = HEAD + self.id.encode("utf-8") +  type.encode("utf-8") + json.dumps(data).encode("utf-8")
        return self.SendSocket.sendto(bag, (ip, RecvSocketPort))

if __name__ == '__main__':
    RecvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    RecvSocket.bind(("", RecvSocketPort))
    r,w,e = select.select([RecvSocket],[],[],5)
    if r == []:
        print("gg")
    else:
        print(r[0].recvfrom(4096))