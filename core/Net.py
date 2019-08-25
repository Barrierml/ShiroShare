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
class ShiroRecv(QThread):
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
    def SayHello(self):
        # 向局域网内广播自己
        self.LoadBar.emit("局域网广播中")
        self.Send.Broadcast("HALO", data=self.data)
        # 发送信号初始化完毕
    def run(self):
        # 受支持的类型
        _method_map = [b"HALO",b"FILE",b"BEAT",b"CHEN",b"LIST",b"ACKN",b"USER",]
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
    def on_HALO(self,data,addr):
        # 收到别人的用户信息,返回一个自己的用户信息
        print("收到一个新成员")
        if not self.sql.InUsers(data.get("id")):
            # 新成员加入
            self.sql.AddUser(data.get("id"),data.get("name"),addr[0])
            # 向他发送打招呼信息
            self.Send.SendTo(addr[0],"HALO",self.data)
            # 向他发送本机文件列表
            self.Send.SendTo(addr[0],"LIST",self.data)
        else:
            self.sql.ChangeUser(data.get("id"),{"Name":data.get("name"),"ip":addr[0],"end_life_time":time.time()})
    def on_USER(self,data,addr):
        # 修改用户信息
        if self.sql.InUsers(data["id"]):
            self.sql.ChangeUser(data.get("id"),{"Name":data.get("name"),"ip":addr[0],"end_life_time":time.time()})

    def on_FILE(self,data,addr):
        print("收到一个请求文件的东西")
        file_id = data.get("GetId")
        ackid = data.get("AckId")
        ip = addr[0]
        url,md5,ttt = self.model.search(file_id)
        port = oc.RngPort(self.FilePort)
        thread = FileSend(url,port)
        thread.start()
        self.Send.SendTo(ip,"ACKN",{
            "port":thread.port,
            "md5":md5,
            "time":ttt,
            "AckId":ackid,
        })
    def on_ACKN(self,data,addr):
        # 收到确认包，开启接收接收
        port = data.get("port")
        tt = data.get("time")
        md5 = data.get("md5")
        ackid = data.get("AckId")
        filedata = None
        for i in self.WaitAckFiles:
            if i.get("AckId") == ackid:
                filedata = i.get("File")
                self.WaitAckFiles.remove(i)
        if filedata == None:
            return
        url = oc.path_join(self.data.get("dir_url"),filedata.get("FileName")+filedata.get("suffix"))
        filedata["url"] = url
        def f(o):
            return filedata.get(o)
        self.sql.AddFile(f("_id"),f("FileName"),f("suffix"),f("md5"),f("belong_dir"),f("owner"),url,f("end_time"))
        thread = FileRecv(addr[0],port,filedata)
        thread.start()
    def RecvOver(self):
        # 接收完毕,实际上还是在子进程内进行操作文件
        pass
    def on_BEAT(self,data,addr):
        pass
    def on_CHEN(self,data,addr):
        pass
    def Send_LIST(self,dd:dict):
        # 向局域网所有人发送自身的分享列表
        print(dd)
    def close(self):
        self.RecvSocket.close()
    @property
    def AckId(self):
        # 确认包的id
        self.ACKID += 1
        return self.ACKID
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