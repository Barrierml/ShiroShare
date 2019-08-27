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
        self.sql = sql.ShiroSQL("../222")
        self.FilePort = (20000,30000)
    def run(self) -> None:
        for i in self.watch_list:
            i.start()
        self.Recv.start()
        model_method_map = {
            "All_list": self.on_All_list,
            "ADD_FILE": self.on_ADD_FILE,
            "MODI_FILE": self.on_MODI_FILE,
            "DEL_FILE": self.on_DEL_FILE,
        }
        net_method_map = {
            "HALO":self.on_HALO,
            "GEHA":self.on_GEHA,
            "LIST":self.on_LIST,
            "GELI":self.on_GELI,
            "FILE":self.on_FILE,
            "ACKN":self.on_ACKN,
        }
        while True:
            time.sleep(0.1)
            need_del = []
            for k,v in self.WaitAckFiles.items():
                if time.time() - v.get("time") > 10:
                    need_del.append(k)
            for i in need_del:
                print("删除一个过期的")
                del self.WaitAckFiles[i]
            if not self.Queue.empty():
                bag = self.Queue.get()
                _type = bag.get("type")
                data = bag.get("data")
                if _type in model_method_map:
                    dirid = bag.get("DirId")
                    model_method_map[_type](data,dirid)
                elif _type in net_method_map:
                    ip = bag.get("ip")
                    net_method_map[_type](data,ip)
    def on_All_list(self,data,dirid):
        data["SelfId"] = self.id
        self.watch_dir_list[dirid] = data
        print(self.watch_dir_list)
    def on_ADD_FILE(self,data,dirid):
        if data:
            self.GetDirFiles(dirid).append(data)
    def on_MODI_FILE(self,data,dirid):
        p = -1
        ll = self.GetDirFiles(dirid)
        for i in range(len(ll)):
            if ll[i].get("_id") == data.get("_id"):
                p = i
                break
        if p != -1:
            ll[p] = data
    def on_DEL_FILE(self,data,dirid):
        p = -1
        ll = self.GetDirFiles(dirid)
        for i in range(len(ll)):
            if ll[i].get("_id") == data:
                p = i
                break
        if p != -1:
            del ll[p]
    def on_HALO(self,data,ip):
        id = data.get("id")
        name = data.get("name")
        if not self.sql.InUsers(id):self.sql.AddUser(id,name,ip)
        else:self.sql.ChangeUser(id,{"name":name,"ip":ip})
        print(self.sql.GetAllUser())
    def on_GEHA(self,data,ip):
        self.on_HALO(data,ip)
        self.Send.SendTo(ip,"HALO",self.HALO_data)
    def on_LIST(self,data,ip):
        def g(o):
            return data.get(o)
        print("收到一份列表")
        url = oc.path_join(self.main_dir,g("DirName"))
        print(self.sql.InDirs(g("DirId")))
        if self.sql.InDirs(g("DirId")):
            Old = self.sql.GetInDirFIles(g("DirId"))
            New = g("Files")
            OldDir = {i.get("_id"):i for i in Old}
            NewDir = {i.get("_id"):i for i in New}
            NeedAdd = [y for y in NewDir if y not in OldDir]
            NeedDel = [y for y in OldDir if y not in NewDir]
            for i in NeedAdd:
                print("添加一个")
                w = NewDir[i]
                w["owner"] = g("SelfId")
                self.Request_File(ip, w)
            for i in NeedDel:
                print("删除一个")
                self.sql.DelFile(i)
                oc.remove(OldDir[i].get("abs_url"))
                del OldDir[i]
            for k,v in OldDir.items():
                n = NewDir[k]
                if v.get("md5") != n.get("md5") and int(float(v.get("end_time"))) < int(float(n.get("end_time"))):
                    w = NewDir[k]
                    w["owner"] = g("SelfId")
                    self.Request_File(ip, w)
                else:
                    w = NewDir[k]
                    w["owner"] = g("SelfId")
                    self.sql.ChangeFile(k,w)
        else:
            oc.mkdir(url)
            self.sql.AddDir(g("DirId"),g("SelfId"),g("DirName"),url)
            for i in g("Files"):
                i["owner"] = g("SelfId")
                self.Request_File(ip,i)
    def on_GELI(self,data,ip):
        print("请求列表")
        for i in self.watch_dir_list.values():
            self.Send.SendTo(ip,"LIST",i)
    def on_FILE(self,data,ip):
        print("请求文件")
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
    def Request_File(self,ip,filedata):
        p = self.AckId
        print("发送一个文件请求")
        self.Send.SendTo(ip, "FILE", {"GetId": filedata.get("_id"), "AckId": p})
        self.WaitAckFiles[str(p)] = {
            "File": filedata,
            "time": time.time()
        }
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
                uu = self.sql.GetDirName(filedata.get("belong_dir"))
                print(uu)
                if not uu:
                    return
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
        e = self.sql.AddFile(f("_id"),f("FileName"),f("suffix"),f("md5"),f("belong_dir"),f("owner"),url,f("end_time"))
        if not e:
            filedata["abs_url"] = url
            self.sql.ChangeFile(f("_id"),filedata)
        thread = Net.FileRecv(ip,port,filedata)
        thread.start()
    def watch_dir_search(self,id):
        for i in self.watch_list:
            r = i.search(id)
            if r:
                return r
        return False,False,False
    def GetList(self):
        self.Send.Broadcast("GELI","")
    def GetConfig(self):
        self.share = []
        self.name = "你好"
        self.id = "12312321"
        self.main_dir = "D:\\备份"
        self.watch_list = []
        self.watch_dir_list = {}
        self._ack_id = 0
        self.WaitAckFiles = {}
        Config = oc.GetFileToJson("D:\\ShiroShare\\Config.json")
        if Config:
            self.__dict__.update(Config)
        self.Queue = Queue()
    def GetDirFiles(self,dirid) -> list:
        l = self.watch_dir_list[dirid].get("Files")
        return l
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
