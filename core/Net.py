from PyQt5.QtCore import QThread,pyqtSignal
import socket,time,select,json
import threading
from tools import mysql, os_cope as oc

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
class ShiroRecv(threading.Thread):
    def __init__(self,queue,Port=RecvSocketPort):
        super(ShiroRecv,self).__init__()
        self.RecvSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.RecvSocket.bind(("",Port))
        self.ReadableList = [self.RecvSocket]
        self.Queue = queue
    def GetJson(self,data:bytes):
        try:
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            print(e)
            return False
    def run(self):
        # 受支持的类型
        _method_map = [b"HALO",b"GEHA",b"FILE",b"LIST",b"GELI",b"ACKN"]
        while True:
            # 堵塞接收
            try:
                r, w, fe = select.select(self.ReadableList, [], self.ReadableList)
                for con in r:
                    data, addr = con.recvfrom(8192)
                    # 前5个字符不是固定就退出
                    if data[0:5] != HEAD:
                        continue
                    type = data[5:9]
                    # type不在支持列表内也退出
                    if type not in _method_map:
                        continue
                    data = self.GetJson(data[9:])
                    self.Queue.put({
                        "type":type.decode("utf-8"),
                        "data":data,
                        "ip":addr[0]
                    })
            except Exception as e:
                print(e)
                continue
    def close(self):
        self.RecvSocket.close()
class SendMessage:
    """主要是用来发送或者广播消息
        经过查询资料，发现发送udp包不会阻塞,就不需要再开进程了
    """
    def __init__(self,port=RecvSocketPort):
        # 设置广播，还有发送信息的嵌套字
        self.port = port
        self.SendSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    def Broadcast(self,type:str,data:object):
        # 发送广播
        bag = HEAD  + type.encode("utf-8") + json.dumps(data).encode("utf-8")
        return self.SendSocket.sendto(bag,('<broadcast>',self.port))
    def SendTo(self,ip,type:str,data:object):
        # 定向传输
        bag = HEAD  +  type.encode("utf-8") + json.dumps(data).encode("utf-8")
        return self.SendSocket.sendto(bag, (ip, self.port))
class FileSend(threading.Thread):
    """使用tcp进行文件传输"""
    def __init__(self,file_url,open_port):
        # file_url 要发送的文件地址
        # ip  发送方的ip
        # open_port 自己开启的端口，等待接受发来请求
        super(FileSend,self).__init__()
        self.port = open_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(open_port)
        self.socket.listen(1)
        self.f = oc.FileSendRaw(file_url)
    def run(self) -> None:
        # 打开文件
        # 只等待5秒钟，5秒后没有连接自动销毁
        r,w,e = select.select([self.socket],[],[],5)
        if r:
            con,addr = r[0].accept()
            # 判断addr是否和ip相同，不相同就关闭
            while True:
                # 预计的ip不一样也退出
                r,w,e = select.select([],[con],[])
                ww = self.f.Get()
                if w and self.f.opened:
                    w[0].send(ww)
                else:
                    break
            con.close()
        # 关闭文件
        if self.f.opened:
            self.f.close()
        self.socket.close()
    def bind(self,port):
        # 开启监控端口，失败+1再试
        try:
            self.socket.bind(("", port))
            self.port = port
        except Exception as e:
            print(e)
            self.bind(port+1)
class FileRecv(threading.Thread):
    """接受文件"""
    def __init__(self,ip,port,file_data):
        super(FileRecv,self).__init__()
        self.file_data = file_data
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.f = oc.FileRecvRaw(self.file_data.get("url"),self.file_data.get("end_time"))
    def run(self):
        # 要是没有打开直接退出
        if not self.f.opened:
            return
        r = self.connect()
        if r:
            while True:
                r,w,e = select.select([self.socket],[],[])
                if r:
                    if not self.f.opened:
                        break
                    data = r[0].recv(1024)
                    self.f.write(data=data)
            self.socket.close()
        self.CallBack()
    def connect(self):
        try:
            self.socket.connect((self.ip,self.port))
        except Exception as e:
            print(e)
            return False
        return True
    def CallBack(self):
        pass
if __name__ == '__main__':
    w = FileSend("D:\\英雄时刻\\hahah.txt",1200)
    w.start()
    w.join()