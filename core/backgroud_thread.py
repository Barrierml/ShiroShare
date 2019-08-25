import tools.os_cope as oc
import tools.mysql as sql
from core import model,Net,watch
import threading,time
from queue import Queue

class BackgroundThread(threading.Thread):

    def __init__(self):
        super(BackgroundThread,self).__init__()
        self.GetConfig()
        self.Recv = Net.ShiroRecv(self.Queue,Port=1300)
        for i in self.share:
            self.watch_list.append(watch.Watch(i,self.Queue))
        self.Send = Net.SendMessage()
        self.sql = sql.ShiroSQL()
        self.FilePort = (20000,30000)
    def run(self) -> None:
        for i in self.watch_list:
            i.start()
        self.Recv.start()
        model_method_map = {
            "All_list": self.on_All_list
        }
        net_method_map = {
            "HALO":self.on_HALO,
            "LIST":self.on_LIST,
            "FILE":self.on_FILE,
            "ACKN":self.on_ACKN,
            "NAME":self.on_NAME
        }
        while True:
            time.sleep(0.1)
            need_del = []
            for k,v in self.WaitAckFiles.items():
                if time.time() - v.get("time") > 10:
                    need_del.append(k)
            for i in need_del:
                del self.WaitAckFiles[i]
            if not self.Queue.empty():
                bag = self.Queue.get()
                _type = bag.get("type")
                data = bag.get("data")
                if _type in model_method_map:
                    model_method_map[_type](data)
                elif _type in net_method_map:
                    ip = bag.get("ip")
                    net_method_map[_type](data,ip)
    def on_All_list(self,data):
        data["SelfId"] = self.id
        self.watch_dir_list.append(data)
    def on_NAME(self,data,ip):
        self.Send.SendTo(ip,"USER",self.HALO_data)
    def on_USER(self,data,ip):
        pass
    def on_HALO(self,data,ip):
        id = data.get("id")
        name = data.get("name")
        if not self.sql.InUsers(id):
            self.sql.AddUser(id,name,ip)
            self.Send.SendTo(ip,"HALO",self.HALO_data)
        else:
            self.sql.ChangeUser(id,{"Name":name,"ip":ip})
            for i in self.watch_dir_list:
                self.Send.SendTo(ip, "LIST", i)
    def on_LIST(self,data,ip):
        def g(o):
            return data.get(o)
        print("收到一份列表")
        url = oc.path_join(self.main_dir,g("DirName"))
        if self.sql.InDirs(g("DirId")):
            Old = self.sql.GetInDirFIles(g("DirId"))
            OldDir = [i[0] for i in Old]
            NewDir = [i.get("_id") for i in g("Files")]
            NeedAdd = [y for y in NewDir if y not in OldDir]
            NeedDel = [y for y in OldDir if y not in NewDir]
            for i in NeedAdd:
                pass
        else:
            oc.mkdir(url)
            self.sql.AddDir(g("DirId"),g("SelfId"),g("DirName"),url)
            for i in g("Files"):
                p = self.AckId
                self.Send.SendTo(ip,"FILE",{"GetId":i.get("_id"),"AckId":p})
                self.WaitAckFiles[str(p)]={
                    "file":i,
                    "time":time.time()
                }

    def on_FILE(self,data,ip):
        print("收到一个请求文件的东西")
        file_id = data.get("GetId")
        AckId = data.get("AckId")
        url,md5,ttt = self.watch_dir_search(file_id)
        if not url:
            return
        port = oc.RngPort(self.FilePort)
        thread = Net.FileSend(url,port)
        thread.start()
        self.Send.SendTo(ip,"ACKN",{
            "port":thread.port,
            "md5":md5,
            "time":ttt,
            "AckId":AckId,
        })
    def on_ACKN(self,data,ip):
        # 收到确认包，开始链接服务器接收
        print("收到确认包")
        port = data.get("port")
        AckId = data.get("AckId")
        filedata = None
        w = False
        uu = ""
        for k,v in self.WaitAckFiles.items():
            if k == AckId:
                filedata = v.get("File")
                uu = v.get("dir_name")
                w = k
                break
        if w:
            del self.WaitAckFiles[w]
        if filedata == None:
            return
        url = oc.path_join(oc.path_join(self.main_dir,uu),filedata.get("FileName")+filedata.get("suffix"))
        filedata["url"] = url
        print(filedata)
        def f(o):
            return filedata.get(o)
        self.sql.AddFile(f("_id"),f("FileName"),f("suffix"),f("md5"),f("belong_dir"),f("owner"),url,f("end_time"))
        thread = Net.FileRecv(ip,port,filedata)
        thread.start()
    def watch_dir_search(self,id):
        for i in self.watch_list:
            r = i.search(id)
            if r:
                return r
        return False,False,False
    def GetConfig(self):
        self.share = []
        self.name = "你好"
        self.id = "12312321"
        self.main_dir = "D:\\备份"
        self.watch_list = []
        self.watch_dir_list = []
        self._ack_id = 0
        self.WaitAckFiles = {}
        Config = oc.GetFileToJson("D:\\ShiroShare\\Config.json")
        if Config:
            self.__dict__.update(Config)
        self.Queue = Queue()
    @property
    def AckId(self):
        self._ack_id += 1
        return str(self._ack_id)
    @property
    def HALO_data(self):
        return {"name":self.name,"id":self.id}
if __name__ == '__main__':
    w = BackgroundThread()
    w.start()
    w.join()
