import socket
import core.Net as e
data = {'DirId': '70dfy4bUKSC9PeRDR4Ys', 'DirName': '英雄时刻', 'Files': [{'_id': 'U618PP6Nk0kLEVDhrXoE', 'FileName': '123', 'suffix': '.xlsx', 'md5': '74921cc130e0d35f7114c5136a1f2000', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.083731, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\U618PP6Nk0kLEVDhrXoE\\0'}, {'_id': '167U1crOwal6H52TK8s0', 'FileName': '1232', 'suffix': '.txt', 'md5': 'd41d8cd98f00b204e9800998ecf8427e', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.0852194, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\167U1crOwal6H52TK8s0\\0'}, {'_id': 'I73vdtjWVrrZSuKp8oF0', 'FileName': '2123', 'suffix': '.txt', 'md5': '6ecc1fc5db11899f8051c2860e51a13d', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.086707, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\I73vdtjWVrrZSuKp8oF0\\0'}, {'_id': 'ezP37X61Gy93uDANnij9', 'FileName': 'hahah', 'suffix': '.txt', 'md5': 'f7fc239ea412bcec46a2c6ca3a58c517', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.088195, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\ezP37X61Gy93uDANnij9\\0'}, {'_id': 'f6nmzK1Yio1UNKzOADWs', 'FileName': 'shiro_backupI', 'suffix': '', 'md5': 'b9b349cbc0f78aa6f1d2213f64cc49ee', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.0891871, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\f6nmzK1Yio1UNKzOADWs\\0'}, {'_id': 's7rvMi3Qmx8Z55810Fp2', 'FileName': '新建 DOCX 文档 - 副本 (2)', 'suffix': '.docx', 'md5': '0986e0e9b4f0748487586f969616e34e', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.090179, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\s7rvMi3Qmx8Z55810Fp2\\0'}, {'_id': 'j9b9bt9YaLuCkJWhZKRf', 'FileName': '新建 DOCX 文档 - 副本 (3)', 'suffix': '.docx', 'md5': '0986e0e9b4f0748487586f969616e34e', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.0926588, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\j9b9bt9YaLuCkJWhZKRf\\0'}, {'_id': '6MXCpv5GLmIGLaHa44EC', 'FileName': '新建 DOCX 文档 - 副本', 'suffix': '.docx', 'md5': '0986e0e9b4f0748487586f969616e34e', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.0946422, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\6MXCpv5GLmIGLaHa44EC\\0'}, {'_id': 'pMjXDhAJjO1a67652r8o', 'FileName': '新建 DOCX 文档', 'suffix': '.docx', 'md5': '4297f44b13955235245b2497399d7a93', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.0956342, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\pMjXDhAJjO1a67652r8o\\0'}, {'_id': 'bgae1Xkgqv77C7zKGsdF', 'FileName': '新建 PPT 演示文稿 - 副本 (2)', 'suffix': '.ppt', 'md5': '9d141af3b1cbb74c0e070ff668c81320', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.097122, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\bgae1Xkgqv77C7zKGsdF\\0'}, {'_id': 'SQe6318c461w7g91BXBK', 'FileName': '新建 PPT 演示文稿 - 副本 (3)', 'suffix': '.ppt', 'md5': '9d141af3b1cbb74c0e070ff668c81320', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.0991073, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\SQe6318c461w7g91BXBK\\0'}, {'_id': 'vv0CWaticKY5E5xsDbFS', 'FileName': '新建 PPT 演示文稿 - 副本 (4)', 'suffix': '.ppt', 'md5': '9d141af3b1cbb74c0e070ff668c81320', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.1005964, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\vv0CWaticKY5E5xsDbFS\\0'}, {'_id': '8QB6F7RxLAjPKZPXcB6u', 'FileName': '新建 PPT 演示文稿 - 副本 (5)', 'suffix': '.ppt', 'md5': '9d141af3b1cbb74c0e070ff668c81320', 'belong_dir': '70dfy4bUKSC9PeRDR4Ys', 'end_time': 1566699885.103075, 'send_url': 'D:\\英雄时刻\\ShiroBackup\\8QB6F7RxLAjPKZPXcB6u\\0'}]}
import tools.os_cope as oc
import tools.mysql as sql
from core import model,Net,watch
import threading,time
from queue import Queue

class BackgroundThread(threading.Thread):

    def __init__(self):
        super(BackgroundThread,self).__init__()
        self.GetConfig()
        self.Recv = Net.ShiroRecv(self.Queue)
        self.Send = Net.SendMessage(port=1300)
        self.sql = sql.ShiroSQL(name="123")
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
        }
        self.Send.Broadcast("HALO",self.HALO_data)
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
    def on_HALO(self,data,ip):
        id = data.get("id")
        name = data.get("name")
        if not self.sql.InUsers(id):
            self.sql.AddUser(id,name,ip)
            self.Send.SendTo(ip,"HALO",self.HALO_data)
        else:
            self.sql.ChangeUser(id,{"name":name,"ip":ip})
            for i in self.watch_dir_list:
                self.Send.SendTo(ip, "LIST", i)
    def on_LIST(self,data,ip):
        def g(o):
            return data.get(o)
        print("收到一份列表")
        url = oc.path_join(self.main_dir,g("DirName"))
        if self.sql.InDirs(g("DirId")):
            Old = self.sql.GetInDirFIles(g("DirId"))
            New = g("Files")
            OldDir = {i.get("_id"):i for i in Old}
            NewDir = {i.get("_id"):i for i in New}
            NeedAdd = [y for y in NewDir if y not in OldDir]
            NeedDel = [y for y in OldDir if y not in NewDir]
            for i in NeedAdd:
                w = NewDir[i]
                self.Request_File(ip, w, g("DirName"))
            for i in NeedDel:
                self.sql.DelFile(i)
                oc.remove(OldDir[i].get("abs_url"))
        else:
            oc.mkdir(url)
            self.sql.AddDir(g("DirId"),g("SelfId"),g("DirName"),url)
            for i in g("Files"):
                self.Request_File(ip,i,g("DirName"))
    def Request_File(self,ip,filedata,dir_name):
        p = self.AckId
        print("发送一个文件请求")
        self.Send.SendTo(ip, "FILE", {"GetId": filedata.get("_id"), "AckId": p})
        self.WaitAckFiles[str(p)] = {
            "File": filedata,
            "dir_name": dir_name,
            "time": time.time()
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

