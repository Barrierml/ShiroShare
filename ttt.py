import threading,socket,time,select,json
HEAD = b"Shiro"
RecvSocketPort = 6543
HHH = {"name":"sadas","sex":"man"}
class SendMessage(threading.Thread):
    """主要是用来发送或者广播消息"""
    def __init__(self,Queue):
        super(SendMessage,self).__init__()
        # 设置广播，还有发送信息的嵌套字
        self.SendSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # 设置接收信息的Queue
        self.Queue = Queue
        # 消息id
        self.MessageId = 0
    def run(self) -> None:
        pass
    def Broadcast(self,type:str,data:object) -> int:
        # 发送广播
        bag = HEAD + type.encode("utf-8") + json.dumps(data).encode("utf-8")
        self.SendSocket.sendto(bag,('<broadcast>',RecvSocketPort))
        self.MessageId += 1
        return self.MessageId
if __name__ == '__main__':
    w = json.dumps("123")
    print(w)
    print(json.loads(w))